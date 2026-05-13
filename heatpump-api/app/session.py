import asyncio
import logging

import httpx
from fastapi import HTTPException

from .config import settings

logger = logging.getLogger(__name__)


class StartupError(Exception):
    pass


class SessionManager:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient()
        self._lock = asyncio.Lock()
        self._generation = 0

    async def login(self) -> None:
        # TODO: replace URL path and payload structure after reverse-engineering the web UI
        login_url = f"{settings.heatpump_url}/TODO/login"
        payload = {"username": settings.username, "password": settings.password}

        try:
            response = await self._client.post(login_url, json=payload)
        except httpx.RequestError as e:
            raise StartupError(
                f"Cannot reach heatpump at {settings.heatpump_url}: {e}"
            ) from e

        if response.status_code in (401, 403):
            raise StartupError("Login failed: invalid credentials")

        if not response.is_success:
            raise StartupError(f"Login failed with HTTP {response.status_code}")

        # TODO: persist cookies/token from response once auth mechanism is known
        self._generation += 1
        logger.info("Authenticated with heatpump web UI (session generation %d)", self._generation)

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        gen_at_call = self._generation
        response = await self._client.request(method, url, **kwargs)

        if response.status_code != 401:
            return response

        # Session expired — re-authenticate, but only once per generation to
        # prevent N concurrent 401s from each sending a separate login request.
        async with self._lock:
            if self._generation == gen_at_call:
                await self.login()

        response = await self._client.request(method, url, **kwargs)
        if response.status_code == 401:
            raise HTTPException(status_code=502, detail="Re-authentication failed")
        return response

    async def close(self) -> None:
        await self._client.aclose()


session_manager = SessionManager()
