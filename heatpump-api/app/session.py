import asyncio
import logging
import re

import httpx
from fastapi import HTTPException

from .config import settings

logger = logging.getLogger(__name__)

_SESSION_ID_RE = re.compile(r"sessionid=([A-F0-9]+)", re.IGNORECASE)

# Transient transport errors are retried before surfacing as a 502; the HPM is a
# slow embedded device that occasionally drops or stalls connections.
_REQUEST_RETRIES = 2
_RETRY_BACKOFF_S = 0.5


class StartupError(Exception):
    pass


class SessionManager:
    def __init__(self) -> None:
        # Explicit timeout: the HPM default httpx 5s read timeout is too short for
        # this slow embedded device. Connect stays short; read/overall is configurable.
        self._client = httpx.AsyncClient(
            follow_redirects=False,
            timeout=httpx.Timeout(settings.request_timeout, connect=5.0),
        )
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

        # Elevate to WEB-RC access level 3 (code 4444).
        # GET /webfb.rsp first (loads the code-entry form), then POST the code.
        # Set=OK is mandatory — without it the server returns 302 but does not elevate.
        # The redirect URL already contains sessionid; do not append it again.
        try:
            await self._client.get(f"{base}/webfb.rsp?sessionid={session_id}")
            r = await self._client.post(
                base + "/getcode.rsp",
                data={"code": "4444", "Set": "OK", "sessionid": session_id,
                      "branchnr": "1", "level": "0"},
            )
            if r.status_code == 302:
                redirect = r.headers.get("location", "menue.rsp?branchnr=1&level=0")
                await self._client.get(f"{base}/{redirect.lstrip('/')}")
        except httpx.RequestError as e:
            raise StartupError(f"WEB-RC elevation failed: {e}") from e

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
        last_exc: httpx.RequestError | None = None
        for attempt in range(_REQUEST_RETRIES + 1):
            try:
                return await self._client.request(method, url, params=params, **kwargs)
            except httpx.RequestError as e:
                last_exc = e
                if attempt < _REQUEST_RETRIES:
                    logger.warning(
                        "Transient transport error (attempt %d/%d) for %s %s: %r",
                        attempt + 1, _REQUEST_RETRIES + 1, method, url, e,
                    )
                    await asyncio.sleep(_RETRY_BACKOFF_S * (attempt + 1))
        assert last_exc is not None  # only reached after the loop exhausts retries
        raise last_exc

    async def close(self) -> None:
        await self._client.aclose()


session_manager = SessionManager()
