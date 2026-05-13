import asyncio
import logging

import httpx
from fastapi import HTTPException

from .config import settings
from .models import SystemStatus
from .parsers import extract_param, parse_dhw, parse_float, parse_hc1, parse_hp1, parse_operating_mode
from .session import SessionManager, session_manager

logger = logging.getLogger(__name__)


class HeatpumpClient:
    def __init__(self, session: SessionManager) -> None:
        self._session = session

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
            raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e}") from e

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


client = HeatpumpClient(session_manager)
