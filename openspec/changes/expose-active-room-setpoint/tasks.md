## 1. Fixtures

- [x] 1.1 Build the HC2 SNOT state in-test by substituting id 20 = `red. oper. SNOT`, id 22 = `timer-SNOT ----` into the `v3.html` capture with `_replace_value` (the suite's existing convention; `fixtures/` holds live captures only), with a comment naming the source (commit 4f8a383)
- [x] 1.2 Build the HC1 NO state (id 6 = `red. oper. NO`) and an unrecognised state (id 6 = `frost prot.`) the same way from `v30.html`, commented as constructed

## 2. Parsing and model

- [x] 2.1 Add `operating_status`, `timer_status`, `period`, `active_room_setpoint` as optional fields to `HeatingCircuit` and `HeatingCircuit2`, and correct the `room_setpoint` comments/docstrings from "nominal" to non-occupation time (roomNO); verify the existing tests still pass
- [x] 2.2 Add a period parser in `parsers.py`: whitespace-collapsed last token, accepted only if in {`OT1`..`OT4`, `NO`, `SNOT`}, else `None`; verify with unit tests for each observed string, the NO string, an unknown string, an extra trailing word, and an empty string
- [x] 2.3 Wire the four fields into `parse_hc1` (ids 6/8) and `parse_hc2` (ids 20/22) via the lenient helpers, resolving `active_room_setpoint` from `room_ot1`/`room_ot2`/`room_setpoint` for OT1/OT2/NO and `None` otherwise; correct the "nominal" wording in both docstrings; verify fixture tests: HC1 `v30.html` → OT2/18.0, HC2 `v3.html` → OT1/27.0, SNOT → SNOT/None, NO → NO/20.0, unknown → None/None with raw string kept
- [x] 2.4 Add a test that removing ids 6/8 (or 20/22) from a fixture yields `None` for the new fields and leaves every pre-existing field unchanged
- [x] 2.5 Confirm in `tests/test_client_status.py` that the status call still requests exactly the same set of pages and no `menue.rsp`/`info.rsp`/`execset.rsp`, and that the new fields appear in the `SystemStatus` JSON; run the full suite green

## 3. Home Assistant package

- [x] 3.1 Add REST sensors "HC1 Operating Period" / "HC2 Operating Period" (`unique_id` `heatpump_hc1_operating_period` / `heatpump_hc2_operating_period`) on the status resource, with `operating_status` and `timer_status` as attributes and the existing availability/value_template guard pattern
- [x] 3.2 Add a `template: - sensor:` block with "HC1 Active Room Setpoint" / "HC2 Active Room Setpoint" (unit `°C`, device class `temperature`, `unique_id` `heatpump_hc1_active_room_setpoint` / `heatpump_hc2_active_room_setpoint`): API value if present, else `sensor.hcN_setpoint_room<period|lower>`, else unavailable; never `0`
- [x] 3.3 Rename friendly names only: "HC1/HC2 Room Setpoint" → "… Room Setpoint NO"; "Room Normal" → "Room NO (non-occupied)"; "Room Standby" → "Room SNOT (holiday)"; fix the "normal/standby" header comments. Verify by diff that no `unique_id` changed
- [x] 3.4 Validate the package YAML parses (e.g. `python -c 'import yaml'` with a loader that tolerates `!secret`), and render the active-setpoint template by hand for OT2, SNOT and unknown inputs

## 4. Docs and version

- [x] 4.1 Update `docs/hpm-ui-surface.md`: ids 6/8/20/22 ✓ with their API field names, id 18/32 relabelled "Room setpoint NO (non-occupation time)", a short note on the period meanings citing manual §3.3.4/§3.3.7 and Table 1.4, and the observed `red. oper. SNOT` string
- [x] 4.2 Document the new entities in `docs/ha-integration.md` if it lists package entities; verify by grep that no "nominal" gloss of roomNO remains outside `docs/manuals/` (flag `docs/manuals/hpm-controller.md` in the hand-off, don't edit it)
- [x] 4.3 Bump the add-on version in `heatpump-api/config.yaml`; commit and push to `main`

## 5. Deploy and hand-off (each step needs approval first)

- [x] 5.1 Ask for approval, then update the add-on on the live instance and verify `GET /api/v1/status` returns `period`, `active_room_setpoint` and the raw strings for both circuits
- [ ] 5.2 Ask for approval, then copy the package to `/config/packages/heatpump.yaml`, check config, reload; verify `sensor.hc1_active_room_setpoint` shows 18.0 and `sensor.hc1_room_setpoint` kept its entity_id
- [ ] 5.3 Hand back to ha-config: once the new sensor has data in InfluxDB, swap the Indoor Temperatures dashboard's dashed line to `hc1_active_room_setpoint` and update `ha-config/GRAFANA.md`
