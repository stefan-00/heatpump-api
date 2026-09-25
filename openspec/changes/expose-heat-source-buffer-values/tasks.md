## 1. Test fixtures and harness

- [x] 1.1 Add a raw-save mode to `research/probe_view_pages.py`. It writes each fetched page's HTML with the `sessionid` values scrubbed. Verify by running it for `v21.rsp v30.rsp v3.rsp v100100.rsp`: the saved files contain `id=16:6.2.15` and no real session id.
- [x] 1.2 Save those four pages as `heatpump-api/tests/fixtures/*.html`, add `pytest` as a dev dependency (`requirements-dev.txt`) and add a `tests/conftest.py` fixture loader. Verify `.venv/bin/python -m pytest` runs and collects zero failing tests.

## 2. Models and parsers

- [x] 2.1 Add a parser helper that returns `None` both when a parameter is absent and when it is present but unparseable, plus a whole-text helper that collapses whitespace. Verify with unit tests: `no demand` stays `no demand`, a garbage value gives `None`, and `16` doesn't match `169`.
- [x] 2.2 Extend `HeatPumpUnit` with `hc_setpoint`, `operating_state`, `heat_demand` and `defrost` (all optional), and parse them in `parse_hp1` from ids 109/88/89/124. Verify with a test against the `v21` fixture (captured during HC2 demand): 42.0, `normal`, `dem. HC2`, False.
- [x] 2.3 Add `valve_position` to `HeatingCircuit` and `HeatingCircuit2`, parsed from `v30` id 16 and `v3` id 30. Verify with fixture tests: 0.0 and 100.0.
- [x] 2.4 Add a `Buffer` model and `parse_buffer`, which raises `ValueError` only when both ids 61 and 59 are absent. Add `SystemStatus.buffer`. Verify with fixture tests: `temp` 35.7 (no unit), `setpoint` 42.0, a page with one id gives the other as `None`, and a page with neither raises.
- [x] 2.5 Verify the existing fields are unchanged: a test parses the fixtures and checks every pre-existing field is still populated with its old type, and a page with a malformed new value still parses the core fields.

## 3. Client

- [x] 3.1 Add `v100100.rsp` to the `gather` in `get_status` under the same lock hold. Parse it best-effort like HC2: on `ValueError`, log a warning and leave `buffer = None`. Verify with a client test that serves all six captured pages through a stubbed session: the status carries all eight new fields populated. The live API is checked in 6.1; running it locally would need the device password in its environment.
- [x] 3.2 Verify the failure paths. A network error on the buffer page still gives a 502; check with a test that stubs the session request to raise `httpx.RequestError` for `v100100.rsp`. An unparseable buffer page gives 200 with `buffer: null`; check with a test using a stripped fixture.

## 4. Home Assistant package

- [x] 4.1 Add the numeric sensors to `homeassistant/packages/heatpump.yaml` using the existing guard pattern: `hc_setpoint`, `buffer.temp` and `buffer.setpoint` as °C / `temperature`, and the HC1/HC2 valve position as `%`. All `unique_id`s start with `heatpump_`. Verify that HA's config check passes after copying the file in, and that the entities show values.
- [x] 4.2 Add the text sensors for `operating_state` / `heat_demand`, and a `rest` binary sensor for `defrost` with no `payload_on`. Verify in HA that the entities show `normal`, `no demand` and `off`. With the add-on stopped they go `unavailable`, and a `null` field shows `unknown`, not `0`. (Values confirmed live via InfluxDB. The null path was checked by rendering the templates against a nulled status. The stopped-add-on case was not exercised; it uses the same `value_json is defined` guard as the existing sensors.)
- [x] 4.3 Confirm the new entities are recorded in InfluxDB. Query the datasource proxy through `grafana-home` for the new `entity_id`s, and fix HA's Influx include rules if any are missing. (Done 2026-09-25: `binary_sensor.heatpump_*` was missing, which had also silently stopped `heatpump_on`/`heatpump_heating` since mid-August. The glob was added, and the dead `*heat_pump_*` globs were removed.)

## 5. Dashboard and docs

- [x] 5.1 Add the heat-source panel to the Heat Pump dashboard through `grafana-home`:
  - `hc_setpoint`, the outlet temperature, the HC2 flow setpoint and the buffer temperature on °C;
  - the valve positions on a right-hand % axis, labelled `valve (Y-contr)`;
  - defrost as a row in the existing `Pump / Compressor activity` state timeline (it already draws the on/off rows).

  Export the dashboard to `homeassistant/grafana/`. Verify the panel renders with data.
- [x] 5.2 Update `docs/hpm-ui-surface.md`:
  - relabel `v30` id 16 and `v3` id 30 as `Y-contr.`, and drop the "v10 only" / pump-speed notes;
  - add the `v21` id 109 no-demand `2 °C` observation;
  - mark the new API fields.

  Also update `docs/ha-integration.md` if it lists the sensors. Verify by grepping for `Pump speed`: no hits remain for ids 16/30.
- [x] 5.3 Remove item 1 from `TODO.md`, and renumber item 2 while keeping its `Y-contr` reference accurate. Verify by reading the file.

## 6. Release

- [x] 6.1 Bump `version` in `heatpump-api/config.yaml`, then update the add-on from HA and check `GET /api/v1/status` on the live instance returns the new fields.
- [x] 6.2 While the compressor is running, record `hc_setpoint` against the outlet temperature. This answers design.md's open question: is `2 °C` a no-demand placeholder? Note the result in `docs/hpm-ui-surface.md`. (Done from the 2026-09-25 fixture capture: 42 °C asked, 37 °C outlet, at 41 Hz.)
