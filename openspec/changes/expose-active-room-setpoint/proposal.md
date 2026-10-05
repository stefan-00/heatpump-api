## Why

The Indoor Temperatures Grafana dashboard draws `sensor.hc1_room_setpoint` as the heat pump's target, but that sensor is `roomNO` (`v30.rsp` id 18), which sat flat at 20 °C over 2026-09-28..10-05. HC1's week program covers the whole day with OT1 (21:00–06:00) and OT2 (06:00–21:00), so the 18 °C of `roomOT1`/`roomOT2` is what is actually in force. The API doesn't say which period a circuit is in, so nothing downstream can pick the right setpoint.

"NO" is also mislabelled. The installation manual (`import/HPM_HBInstIB_en.pdf`, §3.3.4 and Table 1.4) defines it as the **non-occupation time** setpoint — what applies outside any occupation time, or in the "holiday" switch position ("Reduced operation: setpoints of non-operating time NO apply"). `nom. oper.` in the status strings means *nominal operation*, i.e. an occupation time is running. The repo calls `roomNO` "nominal" in `models.py`, `parsers.py` and `docs/hpm-ui-surface.md`, which conflates the two.

## What Changes

- Each heating circuit in `GET /api/v1/status` gains optional fields, read from the view pages the status poll already fetches (no new fetch, no WEB-RC navigation):
  - `operating_status` — the raw operating-mode string (HC1 `v30.rsp` id 6, HC2 `v3.rsp` id 20), e.g. `nom. oper. OT1`;
  - `timer_status` — the raw timer string (id 8 / id 22), e.g. `timer-OT1 ----------`;
  - `period` — the period in force as a token, `OT1`..`OT4`, `NO` or `SNOT`, taken from the operating status; `null` for any string not recognised;
  - `active_room_setpoint` — the room setpoint for that period, when that setpoint is on the same view page (`roomOT1`, `roomOT2`, `roomNO`); `null` otherwise.
- The format is taken from observed strings only: `nom. oper. OT1` / `OT2` from the current fixtures, `red. oper. SNOT` / `timer-SNOT ----` from HC2's winter standby capture (2026-05 crawl, git history of `docs/hpm-ui-surface.md`).
- `homeassistant/packages/heatpump.yaml` gains, per circuit, an operating-period sensor and an active-room-setpoint template sensor (`sensor.hc1_active_room_setpoint`, `sensor.hc2_active_room_setpoint`). The template falls back to the existing `/setpoints` sensors for periods whose value is not on the view page (OT3, OT4, SNOT).
- The friendly names "HC1/HC2 Room Setpoint" become "… Room Setpoint NO"; entity_ids stay, because InfluxDB history is keyed on them. The writable numbers "Room Normal" / "Room Standby" get friendly names that match the manual ("Room NO (non-occupied)", "Room SNOT (holiday)"), entity_ids unchanged.
- "nominal" wording for `roomNO` is corrected in `models.py`, `parsers.py` and `docs/hpm-ui-surface.md`; ids 6/8/20/22 are marked ✓ in the doc's API column.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `heatpump-control`: the status read reports each circuit's operating period, raw mode/timer strings and the room setpoint in force.
- `ha-sensor-config`: the package exposes the operating period and active room setpoint per circuit, and relabels the roomNO-backed entities without changing their entity_ids.

## Impact

- **Code**: `app/models.py` (new optional fields on `HeatingCircuit` / `HeatingCircuit2`, docstring fixes), `app/parsers.py` (period parsing and resolution), tests and fixtures.
- **API**: additive fields on the status endpoint; existing fields unchanged.
- **Device traffic**: none added. The status poll fetches the same pages; no WEB-RC navigation joins it.
- **HA**: package changes to copy into `/config` by hand, after approval. `sensor.hc*_active_room_setpoint` matches the existing `sensor.hc1_*` / `sensor.hc2_*` InfluxDB globs, so ha-config needs no whitelist change.
- **Hand back to ha-config** (out of scope here): swap the Indoor Temperatures dashboard's dashed `hc1_room_setpoint` line for `hc1_active_room_setpoint` once it has data, and update the matching section of `ha-config/GRAFANA.md`.
- **Not touched**: `docs/manuals/hpm-controller.md` also glosses NO as "normal (unoccupied)" and SNOT as "setback / night"; that file is a verbatim manual extract with its own correction process, so it is flagged rather than edited. DHW (`v107000.rsp` ids 34/36) is left out.
