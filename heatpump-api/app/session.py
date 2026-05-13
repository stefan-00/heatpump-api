import asyncio
import logging
import re

import httpx
from fastapi import HTTPException

from .config import settings

logger = logging.getLogger(__name__)

_SESSION_ID_RE = re.compile(r"sessionid=([A-F0-9]+)", re.IGNORECASE)


class StartupError(Exception):
    pass


class SessionManager:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(follow_redirects=False)
        self._lock = asyncio.Lock()
        self._generation = 0
        self._session_id: str = ""

    async def login(self) -> None:
        base = settings.heatpump_url.rstrip("/")

        # Step 1: GET / to obtain sessionid from the 302 Location header
        try:
            response = await self._client.get(base + "/")
        except httpx.RequestError as e:
            raise StartupError(f"Cannot reach heatpump at {base}: {e}") from e

        location = response.headers.get("location", "")
        match = _SESSION_ID_RE.search(location)
        if not match:
            raise StartupError(
                f"Heatpump did not issue a session (unexpected response "
                f"HTTP {response.status_code}, Location: {location!r})"
            )
        session_id = match.group(1)

        # Step 2: POST credentials using the HPM form field name 'code'
        # (HPM login page labels this field "access code", max 8 chars;
        # it is supplied via the 'password' config key)
        try:
            response = await self._client.post(
                base + "/getlogin.rsp",
                data={"user": settings.username, "code": settings.password, "sessionid": session_id},
            )
        except httpx.RequestError as e:
            raise StartupError(f"Cannot reach heatpump at {base}: {e}") from e

        location = response.headers.get("location", "").lower()
        if response.status_code in (401, 403) or any(
            word in location for word in ("login", "enter")
        ):
            raise StartupError(
                "Login failed: invalid credentials "
                "(HPM access code is max 8 chars, configured as 'password' key)"
            )

        self._session_id = session_id
        self._generation += 1
        logger.info("Authenticated with heatpump web UI (session generation %d)", self._generation)

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        gen_at_call = self._generation
        response = await self._make_request(method, url, **kwargs)

        if not self._is_session_expired(response):
            return response

        # Session expired — re-authenticate, but only once per generation to
        # prevent N concurrent 302s from each sending a separate login request.
        async with self._lock:
            if self._generation == gen_at_call:
                await self.login()

        response = await self._make_request(method, url, **kwargs)
        if self._is_session_expired(response):
            raise HTTPException(status_code=502, detail="Re-authentication failed")
        return response

    def _is_session_expired(self, response: httpx.Response) -> bool:
        if response.status_code == 401:
            return True
        if response.status_code == 302:
            return "login.rsp" in response.headers.get("location", "").lower()
        return False

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        params = dict(kwargs.pop("params", {}))
        params["sessionid"] = self._session_id
        return await self._client.request(method, url, params=params, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()


session_manager = SessionManager()
