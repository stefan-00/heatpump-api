## ADDED Requirements

### Requirement: Status includes tank-heating, heater and DHW-setpoint values
The status returned by `GET /api/v1/status` SHALL also include the following values in `heat_pump`, read from the heat pump unit view page (`v21.rsp`) without WEB-RC navigation and without any additional request to the device:

- `tank_heating` (id 117, `OP-TANK`): a boolean, whether the heat pump is in tank (DHW) mode;
- `electric_heater` (id 120, `Stat-Heater`): a boolean, the backup electric heater's status;
- `booster_heater` (id 121, `Stat-Booster`): a boolean, the tank booster heater's status;
- `dhw_setpoint` (id 110, `setp.DHW`): the DHW setpoint the controller sends to the heat pump, in °C.

The booleans SHALL be `true` when the device shows `on` and `false` when it shows `off`; any other text is unparseable.

`dhw_setpoint` SHALL be reported as the device shows it. A setpoint the controller reports while there is no demand (a low placeholder such as `2 °C`) is returned as-is, not replaced or suppressed. It is distinct from `domestic_hot_water.setpoint`, which is the controller's own tank setpoint, and neither SHALL be derived from the other.

These values are additive: existing status fields SHALL keep their names, types and meaning.

A value that is missing or can't be parsed SHALL be returned as `null`, and SHALL NOT fail the status request.

#### Scenario: All four values present
- **WHEN** `GET /api/v1/status` is called and `v21.rsp` shows `OP-TANK off`, `Stat-Heater off`, `Stat-Booster off` and `setp.DHW 2 °C`
- **THEN** the response contains `heat_pump.tank_heating = false`, `heat_pump.electric_heater = false`, `heat_pump.booster_heater = false` and `heat_pump.dhw_setpoint = 2.0`

#### Scenario: A heater reads on
- **WHEN** `v21.rsp` shows `Stat-Booster on`
- **THEN** `heat_pump.booster_heater` is `true`

#### Scenario: Values missing from the page
- **WHEN** `v21.rsp` lacks ids 110, 117, 120 and 121
- **THEN** all four fields are `null`, the request succeeds, and the existing `heat_pump` fields are populated as before

#### Scenario: Unparseable value
- **WHEN** `v21.rsp` shows a value for one of the four ids that is neither `on`/`off` (for the booleans) nor a number (for `dhw_setpoint`)
- **THEN** that field is `null` and the request still succeeds
