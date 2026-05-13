import logging
from typing import Any

import httpx
from fastapi import HTTPException

from .config import settings
from .models import HeatpumpState
from .session import SessionManager, session_manager

logger = logging.getLogger(__name__)


class HeatpumpClient:
    def __init__(self, session: SessionManager) -> None:
        self._session = session

    async def get_status(self) -> HeatpumpState:
        # TODO: replace with actual status URL after reverse-engineering the web UI
        url = f"{settings.heatpump_url}/TODO/status"
        try:
            response = await self._session.request("GET", url)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e}") from e

        try:
            # TODO: map actual response fields to HeatpumpState
            return HeatpumpState(**response.json())
        except Exception as e:
            logger.error("Unparseable status response: %s", response.text)
            raise HTTPException(
                status_code=502, detail="Unexpected response structure from heatpump"
            ) from e

    async def send_command(self, command: str, value: Any) -> dict:
        # TODO: replace with actual control URL and payload mapping after reverse-engineering the web UI
        url = f"{settings.heatpump_url}/TODO/control/{command}"
        payload = {"value": value}  # TODO: map to actual web UI payload format

        try:
            response = await self._session.request("POST", url, json=payload)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e}") from e

        if not response.is_success:
            raise HTTPException(
                status_code=502,
                detail=f"Heatpump rejected command '{command}': {response.text}",
            )

        try:
            return response.json()
        except Exception:
            return {"status": "ok"}


client = HeatpumpClient(session_manager)
