import asyncio
import logging
import re
import time

import httpx
from fastapi import HTTPException

from .config import settings

logger = logging.getLogger(__name__)

_SESSION_ID_RE = re.compile(r"sessionid=([A-F0-9]+)", re.IGNORECASE)

# Transient transport errors are retried before surfacing as a 502; the HPM is a
# slow embedded device that occasionally drops or stalls connections.
_REQUEST_RETRIES = 2
_RETRY_BACKOFF_S = 0.5

# Circuit breaker: when the HPM's session pool is exhausted it accepts TCP
# connections but drops them mid-read (httpx ReadError) — and retrying only
# hammers it harder, preventing the pool from ever draining. After this many
# consecutive failures we stop touching the device for a cooldown window and
# fail fast with 503 so callers (and HA's poller) back off.
_BREAKER_FAILURE_THRESHOLD = 5
_BREAKER_COOLDOWN_S = 30.0


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
        # Circuit breaker state
        self._consecutive_failures = 0
        self._breaker_open_until = 0.0

    async def login(self) -> None:
        base = settings.heatpump_url.rstrip("/")

        # Release any prior session first so re-auth doesn't leak a slot. The HPM
        # session pool is tiny and sessions are long-lived, so an abandoned
        # session lingers until idle-timeout and exhausts the pool.
        if self._session_id:
            await self._logout_quietly(self._session_id)
            self._session_id = ""

        # Step 1: GET / to obtain sessionid from the 302 Location header
        try:
            response = await self._client.get(base + "/")
        except (httpx.RequestError, AttributeError) as e:
            raise StartupError(f"Cannot reach heatpump at {base}: {e!r}") from e

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
        except (httpx.RequestError, AttributeError) as e:
            raise StartupError(f"Cannot reach heatpump at {base}: {e!r}") from e

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
        except (httpx.RequestError, AttributeError) as e:
            raise StartupError(f"WEB-RC elevation failed: {e!r}") from e

        self._generation += 1
        logger.info("Authenticated with heatpump web UI (session generation %d)", self._generation)

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        self._raise_if_breaker_open()
        gen_at_call = self._generation
        try:
            response = await self._make_request(method, url, **kwargs)

            if not self._is_session_expired(response):
                self._record_success()
                return response

            # Session expired — re-authenticate, but only once per generation to
            # prevent N concurrent 302s from each sending a separate login request.
            async with self._lock:
                if self._generation == gen_at_call:
                    await self.login()

            response = await self._make_request(method, url, **kwargs)
        except httpx.RequestError:
            self._record_failure()
            raise
        except StartupError as e:
            # Re-auth couldn't reach the device — count toward the breaker and
            # surface as a clean 502 rather than letting StartupError become a 500.
            self._record_failure()
            raise HTTPException(status_code=502, detail=f"Re-authentication failed: {e}") from e

        # Device responded (even if only with a login redirect) — it isn't wedged,
        # so reset the breaker before reporting the re-auth failure.
        self._record_success()
        if self._is_session_expired(response):
            raise HTTPException(status_code=502, detail="Re-authentication failed")
        return response

    def _raise_if_breaker_open(self) -> None:
        if self._breaker_open_until and time.monotonic() < self._breaker_open_until:
            remaining = self._breaker_open_until - time.monotonic()
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Heatpump backing off after repeated failures; "
                    f"retry in {remaining:.0f}s"
                ),
            )

    def _record_success(self) -> None:
        self._consecutive_failures = 0
        self._breaker_open_until = 0.0

    def _record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= _BREAKER_FAILURE_THRESHOLD:
            self._breaker_open_until = time.monotonic() + _BREAKER_COOLDOWN_S
            logger.warning(
                "Circuit breaker opened after %d consecutive failures; "
                "pausing heatpump requests for %.0fs",
                self._consecutive_failures, _BREAKER_COOLDOWN_S,
            )

    def _is_session_expired(self, response: httpx.Response) -> bool:
        if response.status_code == 401:
            return True
        if response.status_code == 302:
            # An invalid/expired session is bounced to the entry page. The device
            # uses 'enter.rsp' for this (and may use 'login.rsp'); a valid request
            # never redirects there, so either marker means re-auth is needed.
            loc = response.headers.get("location", "").lower()
            return "login.rsp" in loc or "enter.rsp" in loc
        return False

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        params = dict(kwargs.pop("params", {}))
        params["sessionid"] = self._session_id
        last_exc: Exception | None = None
        for attempt in range(_REQUEST_RETRIES + 1):
            try:
                return await self._client.request(method, url, params=params, **kwargs)
            except (httpx.RequestError, AttributeError) as e:
                # AttributeError: httpcore/anyio raises "'NoneType' object has no
                # attribute 'getpeername'" when a connection breaks during
                # establishment (observed when the HPM drops connections under
                # session-pool exhaustion). Treat it as a transient transport error
                # so it retries and then surfaces as a clean 502, never a raw 500.
                last_exc = e
                if attempt < _REQUEST_RETRIES:
                    logger.warning(
                        "Transient transport error (attempt %d/%d) for %s %s: %r",
                        attempt + 1, _REQUEST_RETRIES + 1, method, url, e,
                    )
                    await asyncio.sleep(_RETRY_BACKOFF_S * (attempt + 1))
        assert last_exc is not None  # only reached after the loop exhausts retries
        if isinstance(last_exc, httpx.RequestError):
            raise last_exc
        # Wrap the non-RequestError (the getpeername AttributeError) so upstream
        # `except httpx.RequestError` handlers catch it and return 502.
        raise httpx.ConnectError(f"Connection failed: {last_exc!r}") from last_exc

    async def _logout_quietly(self, session_id: str) -> None:
        """Best-effort logout — releases the HPM session slot. Never raises."""
        if not session_id:
            return
        base = settings.heatpump_url.rstrip("/")
        try:
            await self._client.get(f"{base}/leave.rsp", params={"sessionid": session_id})
            logger.info("Logged out heatpump session")
        except Exception as e:  # logout is best-effort; don't let it break shutdown/re-auth
            logger.warning("Logout request failed (ignored): %r", e)

    async def close(self) -> None:
        # Log out on shutdown so add-on restarts/redeploys don't strand a live
        # session in the device's tiny pool.
        await self._logout_quietly(self._session_id)
        self._session_id = ""
        await self._client.aclose()


session_manager = SessionManager()
