## Why

HC2 drives pool heating. The circuit is weather-compensated (heating curve), so when the outdoor temperature is high — which is exactly pool season — the computed flow setpoint collapses toward the room setpoint and the pool gets no heat. The outdoor sensor is shared with the heat pump and HC1, so it cannot simply be unassigned (doing so drops HC2 to its 2 °C frost setpoint and deactivates it), and `hCu-slope` cannot be flattened to 0 (device minimum is 0.2).

The device's **setpoint limitation** function (`heatC. 2 → function → setpoint limitation`, params `2.5.2.3.6.x`) solves this: a `minFl` floor forces the effective flow setpoint to `max(curve, minFl)` regardless of outdoor temperature. This was verified manually against the live device — setting `active=1`, `minFl=30`, `maxFl>minFl` makes HC2 heat the pool at high outdoor temperatures. The device **rejects `maxFl <= minFl`**, so a true constant (min == max) is not allowed.

Today this can only be set by hand-navigating the HPM web UI. To control it from Home Assistant it needs to be a single REST call.

## What Changes

- Add a **flow-limit control endpoint** for HC2 under `GET` and `PATCH /api/v1/circuits/hc2/flow-limit`.
- `GET` returns the current `active`, `min_flow`, `max_flow`.
- `PATCH` accepts a `flow_setpoint` value and, in one request, **enables the limit and sets it**: writes `minFl = flow_setpoint`, ensures `maxFl > minFl` (raising `maxFl` to the device default cap of 65 °C when needed), and sets `active = 1`. This makes the feature a single-write HA `number` entity — no separate enable toggle.
- Values are validated against the device range (read from `info.rsp`: 2.0–160 °C) and the `maxFl > minFl` device constraint before any write.
- Scope is **HC2 only** (the only circuit that needs it); the existing `setpoints` endpoint remains unchanged.

## Capabilities

### New Capabilities

_None — extends the existing `rest-api` capability with a new endpoint, backed by the `heatpump-control` capability for the device write._

### Modified Capabilities

- `rest-api`: add the HC2 flow-limit `GET`/`PATCH` endpoint (read current limitation; set-and-enable in one PATCH; range + `maxFl > minFl` validation).
- `heatpump-control`: add the WEB-RC flow-limitation read/write operation (navigate `heatC. 2 → function → setpoint limitation`; parse `active`/`minFl`/`maxFl`; write via `execset` with the limitation page's branch/level).

## Impact

- **Specs:** `rest-api`, `heatpump-control` (delta files).
- **Code:** `app/parsers.py` (parse flow-limitation page), `app/client.py` (navigate to limitation page, read + set-and-enable write, serialised under `_webrc_lock`), `app/models.py` (`FlowLimit`, `FlowLimitPatch`), `app/routers/setpoints.py` or a sibling router (`GET`/`PATCH .../flow-limit`).
- **Config:** `heatpump-api/config.yaml` version bump so the Supervisor offers the update.
- **No new dependencies.** Additive REST surface; existing endpoints unchanged.

## Non-goals

- HC1 flow-limit control.
- Exposing `posLim`/`negLim`/`maxDemFl-T` (left at device defaults).
- Allowing `min_flow == max_flow` (device rejects it).
