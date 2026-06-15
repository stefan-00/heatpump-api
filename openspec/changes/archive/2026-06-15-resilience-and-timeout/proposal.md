## Why

The service intermittently returns 502s on `/status` and setpoint reads because the underlying `httpx` client uses a 5-second default timeout and does not retry transient transport failures against the slow embedded HPM device. Several behaviours that were added to address this (a transport-error retry policy, a configurable request timeout, and HA sensors that degrade gracefully when the API returns an error body) are now implemented in code but absent from — or contradicted by — the canonical specs. This change brings the specs back in line with the implemented behaviour.

## What Changes

- Define a **transport-error retry policy**: `httpx.RequestError` is retried a bounded number of times with backoff before surfacing as a 502. This replaces the undefined "retry policy" the session spec already references.
- Specify an **explicit, configurable request timeout** (`request_timeout`, default 15s, connect 5s) replacing the silent 5s `httpx` default, settable via the `HEATPUMP_TIMEOUT` env var and the add-on `request_timeout` option.
- Add the **`request_timeout` add-on option** to the packaging contract (`config.yaml` options + `float?` schema).
- Document that error responses log the upstream exception via `repr()` so empty-message transport errors are identifiable.
- Add an **HA sensor error-response resilience** requirement: sensors use `availability` plus guarded `value_template`s so they go `unavailable` (without logging template errors) when the API returns an error body lacking the expected keys.
- Capture the **single WEB-RC navigation lock** that serialises all WEB-RC navigation across circuits on the shared session.
- **BREAKING (spec correction):** Replace the stale `rest-api` "Control endpoints" requirement — which describes the removed air-conditioner model (`POST /api/v1/control/` for power/mode/target_temp/fan) — with the actual setpoint control surface (`PATCH /api/v1/circuits/{id}/setpoints`).

## Capabilities

### New Capabilities

_None — all changes modify existing capabilities._

### Modified Capabilities

- `session-management`: define the transport-error retry policy and the configurable request timeout; capture the single WEB-RC navigation lock serialising navigation across circuits.
- `haos-addon-packaging`: add the `request_timeout` option to the required/validated config contract.
- `ha-sensor-config`: add a requirement that status/setpoint sensors degrade to `unavailable` without template errors when the API returns an error body.
- `rest-api`: replace the stale "Control endpoints" requirement with the PATCH setpoints control surface.

## Impact

- **Specs:** `session-management`, `haos-addon-packaging`, `ha-sensor-config`, `rest-api` (delta files).
- **Code (already implemented):** `app/config.py` (`request_timeout` setting + env var), `app/session.py` (`httpx.Timeout`, retry loop in `_make_request`), `app/client.py` (`%r`/`{e!r}` error logging), `heatpump-api/config.yaml` (`request_timeout` option + schema, version bump), `packages/heatpump.yaml` (availability + guarded value_templates).
- **No new dependencies.** No runtime API contract change beyond the spec correction (the `POST /control/` endpoints never existed in the shipped service).
