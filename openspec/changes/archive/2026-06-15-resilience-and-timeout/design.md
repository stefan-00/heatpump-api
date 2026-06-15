## Context

The HPM-800B7F is a slow embedded web server reached over the LAN. The service polls it every 30s for `/status` (4 concurrent view-page GETs) plus two WEB-RC setpoint resources. Production logs showed intermittent 502s on all three endpoints, traced to `httpx.RequestError` (transport-level) — not parse failures. Two root causes: the `httpx.AsyncClient` was created with the silent 5s default timeout (too short for a sluggish device), and no transient transport failure was retried before surfacing as a 502. The exception detail was also logged with `%s`, which is empty for several `httpx` transport errors, making diagnosis impossible.

The session spec already *references* "the retry policy" without defining it, and the `rest-api` spec still documents a `POST /api/v1/control/` air-conditioner surface that was removed in favour of `PATCH /api/v1/circuits/{id}/setpoints`. The HA package was hardened (availability + guarded `value_template`s) but `ha-sensor-config` never specified that behaviour. This change documents the implemented reality.

## Goals / Non-Goals

**Goals:**
- Define a bounded transport-error retry policy with backoff at the session layer.
- Specify a configurable request timeout (env var + add-on option) replacing the 5s default.
- Specify that HA sensors degrade to `unavailable` without template-error log spam on error bodies.
- Capture the single WEB-RC navigation lock and correct the stale control-endpoint requirement.

**Non-Goals:**
- Changing the polling cadence or staggering scan intervals (HA-side tuning, out of scope here).
- Adding retries to the login/elevation flow itself (only proxied `_make_request` calls retry).
- Introducing any new runtime API endpoint or dependency.

## Decisions

- **Retry at `_make_request`, not per-caller.** Retrying inside the session layer means all proxied requests (status reads, setpoint reads/writes, WEB-RC navigation) inherit resilience uniformly, and retries happen *before* the session-expiry check so a transient blip never masquerades as expiry. Alternative — per-router retry — was rejected as duplicative and easy to forget.
- **Bounded retries (2) with linear backoff (0.5s × attempt).** Small enough to stay well within HA's `scan_interval`, large enough to ride out a brief device stall. Exponential backoff was unnecessary at this scale.
- **Explicit `httpx.Timeout(request_timeout, connect=5.0)`.** Connect stays short (a dead device should fail fast); the read/overall budget is the tunable knob, defaulting to 15s. Exposed via `HEATPUMP_TIMEOUT` env var and the `request_timeout` add-on option so users on slower hardware can raise it without rebuilding.
- **Log exceptions with `repr()`.** `%r` / `{e!r}` renders `ReadTimeout('')` vs `ConnectError('')` even when the message is empty, so the failure mode is identifiable from logs.
- **HA resilience via guarded `value_template`s, not just `availability`.** HA's `rest` platform still renders `value_template` when `availability` is false, so the template itself must short-circuit (`... if 'key' in value_json else none`) to avoid `Template variable error` log spam. `availability` alone is insufficient.

## Risks / Trade-offs

- [Retries add latency to genuinely-down devices] → bounded at 2 retries × ≤1s backoff, far under the 30s poll interval; connect timeout stays short so a truly dead host fails fast.
- [Longer default timeout could delay surfacing a real outage] → 15s is still well within the poll window and only applies after connect succeeds; configurable down if undesired.
- [Spec correction to `rest-api` looks breaking] → the `POST /control/` endpoints were never shipped, so correcting the spec aligns it with reality rather than removing a live capability.

## Migration Plan

Specs only — the code already ships these behaviours (config `request_timeout`, session retry/timeout, client logging, HA package guards). Archiving this change updates `openspec/specs/` to match. No deployment or rollback steps; reverting is a spec-file revert.
