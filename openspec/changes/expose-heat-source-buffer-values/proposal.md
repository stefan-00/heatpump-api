## Why

The heat pump stays at around 38 Hz even when the HC2 flow floor asks for 42 °C, and the API can't show why: either the controller asks the heat pump for too little, or the unit can't deliver more. The setpoint the controller sends to the heat pump answers that question, and the mixing-valve positions show how HC1 and HC2 share the buffer's heat.

## What Changes

- `GET /api/v1/status` gains the heat-source values from `v21.rsp`:
  - the setpoint sent to the heat pump (id 109);
  - the operating state and heat demand (id 88 / 89), as text;
  - whether defrost is active (id 124).
- A new `buffer` section in the status comes from `v100100.rsp`, which the status poll doesn't fetch today. It holds the buffer temperature (id 61) and the zone-1 buffer setpoint (id 59).
- Each heating circuit gains its mixing-valve position (`Y-contr.`). It is on the view pages the status poll already fetches, so no WEB-RC navigation is needed:
  - HC1 is `v30.rsp` id 16 (`6.2.15`).
  - HC2 is `v3.rsp` id 30 (`6.3.15`).

  `vinfo.rsp` names both "controller contrSign back". `docs/hpm-ui-surface.md` and the TODO labelled them pump speed. Neither page carries a real pump-speed value, so pump speed is dropped from this change.
- New fields are optional. Existing fields keep their names and meaning, so nothing breaks.
- `homeassistant/packages/heatpump.yaml` gains sensors for the new values. They follow the existing naming, so the InfluxDB globs pick them up with no config change.
- The Heat Pump Grafana dashboard gains a panel that compares the setpoint sent to the heat pump with the outlet temperature and the HC2 flow setpoint, next to the valve positions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `heatpump-control`: reading the heatpump state also covers the heat-source demand values, the buffer page, and each circuit's valve position. The `SystemStatus` model gains a `buffer` subsystem.
- `ha-sensor-config`: the status sensors listed in the package include the new values.

## Impact

- **Code**:
  - `app/client.py`: one more status fetch (`v100100.rsp`), still under `_device_lock`.
  - `app/parsers.py`: new parsing for the new values.
  - `app/models.py`: new fields and a `Buffer` model.
  - Tests.
- **API**: new fields in `GET /api/v1/status`. The endpoint itself doesn't change.
- **Device traffic**: one more view-page GET per status poll. There is no WEB-RC traffic.
- **HA / Grafana**: new sensors to copy into HA by hand, and one dashboard panel.
- **Docs**: `docs/hpm-ui-surface.md` gets id 16 / id 30 relabelled as `Y-contr.`, and the "v10 only" note removed. TODO item 1 is removed once this change is picked up.
