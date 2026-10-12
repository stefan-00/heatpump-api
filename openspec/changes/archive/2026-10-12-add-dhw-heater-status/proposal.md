## Why

The weekly legionella disinfection (the HPM's therm. disinfection, target 60 °C) stalls at about 52 °C. The heat pump alone tops out there, so the last degrees depend on the tank's 3 kW booster heater, which the Aquarea switches itself (HPM settings `BoosterH 1`, `BoostDel 60`). Per the monobloc service manual §12.10 the booster only turns on when the tank is more than 7 °C below the Aquarea's tank setpoint, the booster delay has expired since tank heating started, and at least 20 minutes have passed since it last switched off.

None of that is visible in Home Assistant today, so a run can't be diagnosed after the fact: we can't tell whether the booster came on, whether the Aquarea was in tank mode, or what tank target it was given. The values are already on `v21.rsp`, which the add-on polls every 30 s; they just aren't parsed.

## What Changes

- Add four best-effort fields to the status response's `heat_pump` object, all parsed from `v21.rsp`, so no new requests reach the HPM:
  - `tank_heating` (id 117, `OP-TANK`): the Aquarea is in tank mode;
  - `electric_heater` (id 120, `Stat-Heater`): the 9 kW backup heater;
  - `booster_heater` (id 121, `Stat-Booster`): the tank's 3 kW immersion heater;
  - `dhw_setpoint` (id 110, `setp.DHW`): the DHW setpoint the HPM sends to the heat pump, reported as-is including its low no-demand placeholder (seen: 2 °C).
- A missing or unparseable value is `null` and never fails the status response.
- `homeassistant/packages/heatpump.yaml`: three binary sensors (tank heating, electric heater, booster heater) and one temperature sensor, `sensor.heatpump_dhw_setpoint` ("Heatpump DHW Setpoint"), named so it can't be mixed up with the existing `sensor.dhw_setpoint` (the HPM's own tank setpoint from the DHW page).
- `docs/hpm-ui-surface.md`: ids 110, 117, 120 and 121 now map to API fields.
- Changelog entry and add-on version bump.

Out of scope: writing any of these values, changing the disinfection settings, and deploying to the live instance (`ha-config`), which happens separately.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `heatpump-control`: the status response's heat pump unit also reports tank heating, electric heater, booster heater and the DHW setpoint sent to the heat pump.
- `ha-sensor-config`: the HA package exposes those four values as entities.

## Impact

- **API**: additive fields on `GET /api/v1/status` → `heat_pump`; existing fields unchanged.
- **Code**: `heatpump-api/app/models.py` (`HeatPumpUnit`), `heatpump-api/app/parsers.py` (`parse_hp1`), parser and status tests.
- **HA**: four new entities in `homeassistant/packages/heatpump.yaml`, recorded in InfluxDB like the existing heatpump sensors once deployed.
- **Device**: no additional requests; `v21.rsp` is already fetched on every status poll.
- **Open question**: nobody has yet seen ids 120 or 121 read `on`. They come from the Aquarea over its bus, so whether they track the real relays is unverified; the first disinfection run with these sensors will show it.
