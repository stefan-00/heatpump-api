## 1. Session release / logout (session-management)

- [x] 1.1 Confirm `app/session.py` has `_logout_quietly(session_id)` that sends `GET /leave.rsp?sessionid=SID` and never raises
- [x] 1.2 Confirm `close()` logs out the active session before `aclose()` (shutdown path is wired via the FastAPI lifespan)
- [x] 1.3 Confirm `login()` logs out any prior `_session_id` before establishing a new session
- [x] 1.4 Verify live: after `close()`, a request with the old `sessionid` is bounced to `enter.rsp` (session released)

## 2. Circuit breaker (session-management)

- [x] 2.1 Confirm `SessionManager` tracks `_consecutive_failures` and `_breaker_open_until`
- [x] 2.2 Confirm `request()` calls `_raise_if_breaker_open()` (503 while open), `_record_failure()` on `RequestError`/`StartupError`, and `_record_success()` on a device response
- [x] 2.3 Confirm the threshold (5) and cooldown (30s) constants exist and the breaker opens/resets accordingly

## 3. Robust error handling (session-management)

- [x] 3.1 Confirm `_make_request` catches `AttributeError` alongside `httpx.RequestError`, retries it, and wraps a persisting non-`RequestError` as `httpx.ConnectError` so it surfaces as 502
- [x] 3.2 Confirm `login()` except clauses catch `(httpx.RequestError, AttributeError)`
- [x] 3.3 Confirm `_is_session_expired` treats a 302 to `enter.rsp` OR `login.rsp` as expired

## 4. Packaging

- [x] 4.1 Bump `heatpump-api/config.yaml` version so the Supervisor offers the update

## 5. Archive

- [x] 5.1 Validate the change with `openspec validate`
- [x] 5.2 Archive the change so the `session-management` delta is synced into `openspec/specs/`
