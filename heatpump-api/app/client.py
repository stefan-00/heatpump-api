import asyncio
import logging
import re

import httpx
from fastapi import HTTPException

from .config import settings
from .models import FlowLimit, HcSetpoints, SystemStatus
from .parsers import extract_param, parse_dhw, parse_float, parse_flow_limit, parse_hc1, parse_hc2, parse_hc_setpoints, parse_hp1, parse_operating_mode
from .session import SessionManager, session_manager

logger = logging.getLogger(__name__)

# WEB-RC navigation label sequences from root to the setpoints page for each circuit.
# Label-based so the path is resilient to branchnr numbering differences across firmwares.
_HC1_SETPOINTS_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 1", "setpoints"]
_HC2_SETPOINTS_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 2", "setpoints"]

_CIRCUIT_LABELS = {"hc1": _HC1_SETPOINTS_LABELS, "hc2": _HC2_SETPOINTS_LABELS}

# HC2 flow-temperature limitation ("setpoint limitation" function, params
# 2.5.2.3.6.x). The page sits one level below the setpoints page (under
# "function"), so its params are addressed at level 5 (vs 4 for setpoints).
_HC2_FLOWLIMIT_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 2", "function", "setpoint limitation"]
_FLOWLIMIT_LEVEL = "5"
_FLOWLIMIT_POSITION = {"active": 1, "minFl": 2, "maxFl": 3}
# Device default upper cap; max_flow must be strictly greater than min_flow.
_FLOWLIMIT_MAX_CAP = 65.0

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
            hp1_resp, hc1_resp, hc2_resp, dhw_resp, sys_resp = await asyncio.gather(
                self._session.request("GET", f"{base}/v21.rsp"),
                self._session.request("GET", f"{base}/v30.rsp"),
                self._session.request("GET", f"{base}/v3.rsp"),
                self._session.request("GET", f"{base}/v107000.rsp"),
                self._session.request("GET", f"{base}/v0.rsp"),
            )
        except httpx.RequestError as e:
            logger.warning("Heatpump unreachable during status fetch: %r", e)
            raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e

        hp1_html, hc1_html, hc2_html, dhw_html, sys_html = (
            r.content.decode("latin-1")
            for r in (hp1_resp, hc1_resp, hc2_resp, dhw_resp, sys_resp)
        )

        try:
            status = SystemStatus(
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

        # HC2 (pool heating) is best-effort: a parse failure here must not break
        # the core status response, since HC2 param IDs are less certain.
        try:
            status.heating_circuit_2 = parse_hc2(hc2_html)
        except ValueError as e:
            logger.warning("Failed to parse HC2 status (v3.rsp) — %.200s", str(e))

        return status


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


    async def get_flow_limit(self) -> FlowLimit:
        base = settings.heatpump_url.rstrip("/")
        async with self._webrc_lock:
            try:
                resp = await self._webrc_navigate(base, _HC2_FLOWLIMIT_LABELS)
            except httpx.RequestError as e:
                logger.warning("Heatpump unreachable during flow-limit read: %r", e)
                raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e

        values = parse_flow_limit(resp.content.decode("latin-1"))
        if not all(k in values for k in ("active", "minFl", "maxFl")):
            raise HTTPException(status_code=502, detail="Could not parse flow limit from heatpump response")
        return FlowLimit(
            active=bool(values["active"]),
            min_flow=values["minFl"],
            max_flow=values["maxFl"],
        )

    async def set_flow_limit(
        self, flow_setpoint: float | None = None, active: bool | None = None
    ) -> None:
        """Write the HC2 flow limitation.

        When flow_setpoint is given, writes minFl = flow_setpoint and ensures
        maxFl > minFl (the device rejects maxFl <= minFl; maxFl is kept if
        already above the floor, otherwise raised to the default cap). The
        limitation is enabled/disabled per `active`; when `active` is None it
        defaults to enabled iff a floor was written, so a lone flow_setpoint
        both sets the floor and enables. At least one argument must be set.
        """
        if flow_setpoint is None and active is None:
            raise HTTPException(status_code=422, detail="Nothing to set: provide flow_setpoint and/or active")

        base = settings.heatpump_url.rstrip("/")
        async with self._webrc_lock:
            try:
                resp = await self._webrc_navigate(base, _HC2_FLOWLIMIT_LABELS)
                current = parse_flow_limit(resp.content.decode("latin-1"))

                if flow_setpoint is not None:
                    # Range-check the floor against the device's accepted minFl range.
                    info_resp = await self._session.request(
                        "GET", f"{base}/info.rsp",
                        params={"branchnr": str(_FLOWLIMIT_POSITION["minFl"]), "level": _FLOWLIMIT_LEVEL},
                    )
                    info_html = info_resp.content.decode("latin-1")
                    lo_match = re.search(r"Lower limit:.*?(-?\d+\.\d+)\s*°", info_html, re.DOTALL | re.I)
                    hi_match = re.search(r"Upper limit:.*?(-?\d+\.\d+)\s*°", info_html, re.DOTALL | re.I)
                    lo = float(lo_match.group(1)) if lo_match else 2.0
                    hi = float(hi_match.group(1)) if hi_match else 160.0
                    if not lo <= flow_setpoint <= hi:
                        raise HTTPException(
                            status_code=422,
                            detail=f"flow_setpoint {flow_setpoint} out of device range [{lo}, {hi}]",
                        )

                    # Pick a max_flow strictly greater than the floor (device constraint).
                    cur_max = current.get("maxFl", 0.0)
                    target_max = cur_max if cur_max > flow_setpoint else _FLOWLIMIT_MAX_CAP
                    if target_max <= flow_setpoint:
                        target_max = min(hi, flow_setpoint + 5.0)
                    if not flow_setpoint < target_max <= hi:
                        raise HTTPException(
                            status_code=422,
                            detail=(
                                f"Cannot satisfy max_flow > min_flow within device range "
                                f"[{lo}, {hi}] for flow_setpoint {flow_setpoint}"
                            ),
                        )

                    # Order matters: raise maxFl first (so minFl never transiently
                    # exceeds maxFl), then set the floor.
                    await self._execset_flowlimit(base, "maxFl", f"{target_max:.1f}")
                    await self._execset_flowlimit(base, "minFl", f"{flow_setpoint:.1f}")

                # Explicit `active` wins; otherwise enable (a lone floor write
                # both sets and enables). At least one arg is always set here.
                effective_active = active if active is not None else (flow_setpoint is not None)
                await self._execset_flowlimit(base, "active", "1" if effective_active else "0")
            except HTTPException:
                raise
            except httpx.RequestError as e:
                logger.warning("Heatpump unreachable during flow-limit write: %r", e)
                raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e

    async def _execset_flowlimit(self, base: str, field: str, val: str) -> None:
        position = _FLOWLIMIT_POSITION[field]
        await self._session.request(
            "POST",
            f"{base}/execset.rsp",
            data={
                "val": val,
                "Set": "OK",
                "sessionid": self._session._session_id,
                "branchnr": str(position),
                "level": _FLOWLIMIT_LEVEL,
                "id": str(position),
            },
        )


client = HeatpumpClient(session_manager)
