## 1. Models (app/models.py)

- [x] 1.1 `FlowLimitPatch`: make `flow_setpoint` optional, add `active: bool | None = None`
- [x] 1.2 Require at least one of `flow_setpoint`/`active` (model or router validation)

## 2. Client (app/client.py)

- [x] 2.1 `set_flow_limit(flow_setpoint: float | None, active: bool | None)` — navigate once; write floor only when `flow_setpoint` given; decide effective active (`active` if given, else True when a floor was written, else no active write); write `active` 1/0 when determined
- [x] 2.2 Keep maxFl-before-minFl ordering and range + `maxFl > minFl` validation for floor writes

## 3. Router (app/routers/setpoints.py)

- [x] 3.1 `patch_flow_limit` passes `flow_setpoint` + `active`; return 422 when both are None

## 4. HA package (packages/heatpump.yaml)

- [x] 4.1 Add `heatpump_enable_hc2_flow_limit` / `heatpump_disable_hc2_flow_limit` rest_commands (`{"active": true/false}`)
- [x] 4.2 Add a template `switch` "HC2 Flow Limit" backed by `binary_sensor.hc2_flow_limit_active`
- [x] 4.3 Change the flow-limit REST resource `scan_interval` 60 → 300

## 5. Verify (live device)

- [x] 5.1 `PATCH {"active": false}` disables (read-back active false), floor unchanged
- [x] 5.2 `PATCH {"active": true}` re-enables; `PATCH {"flow_setpoint": N}` still sets+enables
- [x] 5.3 `PATCH {}` → 422

## 6. Packaging, docs & archive

- [x] 6.1 Update `docs/ha-integration.md` (switch entity, disable now supported, 300 s poll)
- [x] 6.2 Bump `heatpump-api/config.yaml` version
- [x] 6.3 `openspec validate hc2-flow-limit-enable-disable --strict`
- [x] 6.4 Archive the change
