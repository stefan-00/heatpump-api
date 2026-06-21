## Why

The proxy never released its HPM session. Because the HPM-800B7F's session pool is tiny and sessions are long-lived (no idle expiry observed), every add-on restart/redeploy stranded a still-live session in the device until the pool was exhausted — at which point the device accepts TCP connections but drops them mid-read, surfacing to users as "Temporarily no sessions available" and to the proxy as `ReadError` storms. Two further defects amplified the failure: the retry path hammered the wedged device (each `/status` poll fans out to 5×3 requests), and a broken-connection `AttributeError` from the HTTP stack escaped the `httpx.RequestError` handlers as an unhandled 500. Separately, expired sessions are bounced to `enter.rsp`, but expiry detection only matched `login.rsp`, so genuine re-authentication would never fire.

These behaviours are now implemented and verified live against the device; this change brings the `session-management` spec in line.

## What Changes

- Add a **session-release (logout)** requirement: the service logs out via `GET /leave.rsp?sessionid=SID` on shutdown and before re-authentication, best-effort, so restarts/redeploys stop leaking session slots.
- Add a **circuit-breaker** requirement: after a bounded number of consecutive transport failures the service fails fast with 503 for a cooldown window instead of hammering a wedged device; a success resets it.
- **MODIFY** the session-expiry detection to treat a redirect to the entry page (`enter.rsp`, not only `login.rsp`) as expiry, so re-authentication actually fires.
- **MODIFY** the transport-resilience requirement so a non-`RequestError` exception caused by a broken connection (the httpcore/anyio `getpeername` `AttributeError`) is treated as a transient transport error and surfaced as a 502, never an unhandled 500.

## Capabilities

### New Capabilities

_None — all changes modify the existing `session-management` capability._

### Modified Capabilities

- `session-management`: add session-release (logout) on shutdown/re-auth; add a transport-failure circuit breaker; broaden expiry detection to `enter.rsp`; treat broken-connection `AttributeError` as a transport error surfaced as 502.

## Impact

- **Specs:** `session-management` (delta file).
- **Code (already implemented & verified):** `app/session.py` (logout via `/leave.rsp` in `close()` and at the start of `login()`; circuit-breaker state + `_raise_if_breaker_open`/`_record_success`/`_record_failure`; `_is_session_expired` matches `enter.rsp`; `_make_request` catches `AttributeError`, wraps as `httpx.ConnectError`; `login()` except clauses widened), `heatpump-api/config.yaml` (version bump 0.1.6 → 0.1.7).
- **No new dependencies.** No REST API contract change; a new 503 response is added when the breaker is open.
