import asyncio
import logging
import re

import httpx
from fastapi import HTTPException

from .config import settings
from .models import HcSetpoints, SystemStatus
from .parsers import extract_param, parse_dhw, parse_float, parse_hc1, parse_hc_setpoints, parse_hp1, parse_operating_mode
from .session import SessionManager, session_manager

logger = logging.getLogger(__name__)

# WEB-RC navigation label sequences from root to the setpoints page for each circuit.
# Label-based so the path is resilient to branchnr numbering differences across firmwares.
_HC1_SETPOINTS_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 1", "setpoints"]
_HC2_SETPOINTS_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 2", "setpoints"]

_CIRCUIT_LABELS = {"hc1": _HC1_SETPOINTS_LABELS, "hc2": _HC2_SETPOINTS_LABELS}

_SETPOINT_POSITION = {
    "roomOT1": 1,
    "roomOT2": 2,
    "roomOT3": 3,
    "roomOT4": 4,
    "roomNO": 5,
    "roomSNOT": 6,
}


class HeatpumpClient:
    def __init__(self, session: SessionManager) -> None:
        self._session = session
        # Single lock for all WEB-RC navigation — the HPM session is stateful and
        # concurrent navigations to different circuits interfere with each other.
        self._webrc_lock: asyncio.Lock = asyncio.Lock()

    async def get_status(self) -> SystemStatus:
        base = settings.heatpump_url.rstrip("/")
        try:
            hp1_resp, hc1_resp, dhw_resp, sys_resp = await asyncio.gather(
                self._session.request("GET", f"{base}/v21.rsp"),
                self._session.request("GET", f"{base}/v30.rsp"),
                self._session.request("GET", f"{base}/v107000.rsp"),
                self._session.request("GET", f"{base}/v0.rsp"),
            )
        except httpx.RequestError as e:
            logger.warning("Heatpump unreachable during status fetch: %r", e)
            raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e

        hp1_html, hc1_html, dhw_html, sys_html = (
            r.content.decode("latin-1") for r in (hp1_resp, hc1_resp, dhw_resp, sys_resp)
        )

        try:
            return SystemStatus(
                operating_mode=parse_operating_mode(sys_html),
                outdoor_temp=parse_float(extract_param(hc1_html, "9")),
                heat_pump=parse_hp1(hp1_html),
                heating_circuit_1=parse_hc1(hc1_html),
                domestic_hot_water=parse_dhw(dhw_html),
            )
        except ValueError as e:
            logger.error(
                "Failed to parse heatpump status — %.300s",
                str(e),
            )
            raise HTTPException(
                status_code=502,
                detail=f"Unexpected response structure from heatpump: {e}",
            ) from e


    async def _webrc_navigate(self, base: str, labels: list[str]) -> httpx.Response:
        resp = await self._session.request(
            "GET", f"{base}/menue.rsp", params={"branchnr": "1", "level": "0"}
        )
        for label in labels:
            html = resp.content.decode("latin-1")
            links = re.findall(
                r'href=["\']menue\.rsp\?([^"\']+)["\'][^>]*>\s*([^<]+)',
                html, re.IGNORECASE
            )
            matched_params = None
            for qs_str, link_text in links:
                if link_text.strip() == label:
                    qs = dict(p.split("=", 1) for p in qs_str.split("&") if "=" in p)
                    if "branchnr" in qs and "level" in qs:
                        matched_params = {"branchnr": qs["branchnr"], "level": qs["level"]}
                        break
            if matched_params is None:
                available = [t.strip() for _, t in links]
                raise HTTPException(
                    status_code=502,
                    detail=f"WEB-RC menu item {label!r} not found; available: {available}",
                )
            resp = await self._session.request(
                "GET", f"{base}/menue.rsp", params=matched_params
            )
        return resp

    async def get_hc_setpoints(self, circuit_id: str) -> HcSetpoints:
        base = settings.heatpump_url.rstrip("/")
        labels = _CIRCUIT_LABELS[circuit_id]
        async with self._webrc_lock:
            try:
                resp = await self._webrc_navigate(base, labels)
            except httpx.RequestError as e:
                logger.warning("Heatpump unreachable during setpoint read: %r", e)
                raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e

        html = resp.content.decode("latin-1")
        values = parse_hc_setpoints(html)
        if not values:
            raise HTTPException(status_code=502, detail="Could not parse setpoints from heatpump response")
        return HcSetpoints(**values)

    async def set_hc_setpoint(self, circuit_id: str, field: str, value: float) -> None:
        base = settings.heatpump_url.rstrip("/")
        labels = _CIRCUIT_LABELS[circuit_id]
        position = _SETPOINT_POSITION[field]
        async with self._webrc_lock:
            try:
                await self._webrc_navigate(base, labels)
                # Validate against device limits before writing
                info_resp = await self._session.request(
                    "GET", f"{base}/info.rsp",
                    params={"branchnr": str(position), "level": "4"},
                )
                info_html = info_resp.content.decode("latin-1")
                lo_match = re.search(
                    r'Lower limit:.*?(-?\d+\.\d+)\s*°', info_html, re.DOTALL | re.I
                )
                hi_match = re.search(
                    r'Upper limit:.*?(-?\d+\.\d+)\s*°', info_html, re.DOTALL | re.I
                )
                if lo_match and hi_match:
                    lo, hi = float(lo_match.group(1)), float(hi_match.group(1))
                    if not lo <= value <= hi:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Value {value} out of device range [{lo}, {hi}] for {field!r}",
                        )
                await self._session.request(
                    "POST",
                    f"{base}/execset.rsp",
                    data={
                        "val": f"{value:.1f}",
                        "Set": "OK",
                        "sessionid": self._session._session_id,
                        "branchnr": str(position),
                        "level": "4",
                        "id": str(position),
                    },
                )
            except HTTPException:
                raise
            except httpx.RequestError as e:
                logger.warning("Heatpump unreachable during setpoint write: %r", e)
                raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e


client = HeatpumpClient(session_manager)
