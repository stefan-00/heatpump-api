## Why

The HC2 flow-limit `PATCH` currently only ever *enables* the limitation (`active=1`). There is no way to turn it back off from the API, so disabling pool heating still requires the HPM web UI. To control enable/disable from Home Assistant the endpoint must accept an explicit `active` flag.

## What Changes

- **MODIFY** the flow-limit `PATCH` to accept an optional `active` (boolean) field alongside an optional `flow_setpoint`:
  - `{"flow_setpoint": N}` — set the floor and enable (unchanged default: implies `active=1`).
  - `{"active": false}` — disable the limitation without changing the floor.
  - `{"active": true}` — enable with the current floor.
  - `{"flow_setpoint": N, "active": false}` — set the floor but leave it disabled (explicit `active` wins).
  - A `PATCH` with neither field SHALL return 422.
- Add HA wiring to toggle the limitation: a `switch` (`HC2 Flow Limit`) backed by `binary_sensor.hc2_flow_limit_active`, with enable/disable `rest_command`s.
- Reduce the flow-limit poll `scan_interval` from 60 s to **300 s** (the limit changes rarely; this lightens WEB-RC session load, where it competes with the two setpoint polls under the single device lock).

## Capabilities

### Modified Capabilities

- `rest-api`: the flow-limit `PATCH` accepts an optional `active` flag and supports disabling; `flow_setpoint` becomes optional; at least one of the two is required.
- `heatpump-control`: the limitation write can set `active` independently (enable or disable) without requiring a `minFl`/`maxFl` write.

## Impact

- **Specs:** `rest-api`, `heatpump-control` (delta files).
- **Code:** `app/models.py` (`FlowLimitPatch`: `flow_setpoint` optional, add `active`), `app/client.py` (`set_flow_limit` handles optional floor + explicit active), `app/routers/setpoints.py` (require at least one field).
- **HA:** `packages/heatpump.yaml` (enable/disable `rest_command`s, `switch`, flow-limit `scan_interval` 60 → 300), `docs/ha-integration.md`.
- **Config:** `heatpump-api/config.yaml` version bump.
- **No new dependencies.** Backward compatible: existing `{"flow_setpoint": N}` callers are unchanged.

## Non-goals

- HC1 flow-limit control.
- Exposing `posLim`/`negLim`/`maxDemFl-T`.
