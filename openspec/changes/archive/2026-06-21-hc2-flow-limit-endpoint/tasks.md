## 1. Models (app/models.py)

- [x] 1.1 Add `FlowLimit` response model: `active: bool`, `min_flow: float`, `max_flow: float`
- [x] 1.2 Add `FlowLimitPatch` request model: `flow_setpoint: float` (required); optional `max_flow`/`active` overrides if useful

## 2. Parser (app/parsers.py)

- [x] 2.1 Add `parse_flow_limit(html)` that extracts `active`, `minFl`, `maxFl` from the setpoint-limitation page (params `2.5.2.3.6.1/.2/.3`), bounded by the `start_mainpane`/`end_mainpane` markers
- [x] 2.2 Reuse `parse_float`/`parse_last_token` conventions; return a dict or raise `ValueError` on unparseable input

## 3. Client (app/client.py)

- [x] 3.1 Add HC2 limitation nav labels: `["MCR-BMS", "heatCirc.", "heatC. 2", "function", "setpoint limitation"]`
- [x] 3.2 Add `get_flow_limit()` — navigate (under `_webrc_lock`), parse, return `FlowLimit`
- [x] 3.3 Add `set_flow_limit(flow_setpoint)` — navigate, read `info.rsp` ranges, compute target `maxFl` (raise to 65 °C cap when not `> flow_setpoint`), validate range + `maxFl > minFl`, then `execset` `minFl`, `maxFl`, `active=1`
- [x] 3.4 Confirm the correct `execset` branchnr/level for the limitation page via a live read-back (probe showed `info.rsp` responds at `level=5`, positions 1=active/2=minFl/3=maxFl)

## 4. Router (app/routers/setpoints.py)

- [x] 4.1 Add `GET /api/v1/circuits/hc2/flow-limit` → `FlowLimit`
- [x] 4.2 Add `PATCH /api/v1/circuits/hc2/flow-limit` accepting `FlowLimitPatch` → set-and-enable, return resulting `FlowLimit`
- [x] 4.3 Reject any circuit other than `hc2` with an error response (no device write)

## 5. Verify (live device)

- [x] 5.1 `GET` returns current `active`/`min_flow`/`max_flow` matching the HPM web UI
- [x] 5.2 `PATCH {"flow_setpoint": N}` sets `minFl=N`, `maxFl>N`, `active=1`; confirm via read-back and that `SP-Flow` rises
- [x] 5.3 Out-of-range and `maxFl <= minFl` requests return 422 with no write

## 6. Packaging & archive

- [x] 6.1 Bump `heatpump-api/config.yaml` version so the Supervisor offers the update
- [x] 6.2 `openspec validate hc2-flow-limit-endpoint`
- [x] 6.3 Archive the change so the `rest-api` and `heatpump-control` deltas sync into `openspec/specs/`
