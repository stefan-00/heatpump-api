## ADDED Requirements

### Requirement: Status includes heat-source demand, buffer and mixing-valve values
The status returned by `GET /api/v1/status` SHALL also include the following values, all read from the HPM view pages without WEB-RC navigation.

- **Heat pump unit (`v21.rsp`):**
  - `hc_setpoint` (id 109): the heating setpoint the controller sends to the heat pump, in °C;
  - `operating_state` (id 88) and `heat_demand` (id 89): as the text the device shows;
  - `defrost` (id 124): a boolean.
- **A new `buffer` subsystem (`v100100.rsp`):**
  - `temp` (id 61): the buffer tank temperature, in °C;
  - `setpoint` (id 59): the zone-1 buffer setpoint, in °C.
- **Mixing-valve position (`Y-contr.`), in percent:**
  - HC1: `heating_circuit_1.valve_position` (id 16 on `v30.rsp`);
  - HC2: `heating_circuit_2.valve_position` (id 30 on `v3.rsp`).

Each value SHALL be reported as the device shows it, without substitution. A setpoint the controller reports while there is no demand is returned as-is, not replaced or suppressed.

These values are additive: existing status fields SHALL keep their names, types and meaning.

A value that is missing or can't be parsed SHALL be returned as `null`, and SHALL NOT fail the status request. If the buffer page can't be parsed, `buffer` SHALL be `null`. Failing to reach the buffer page SHALL be handled like failing to reach any other view page.

#### Scenario: All new values present
- **WHEN** `GET /api/v1/status` is called and every view page, including the buffer page, responds with the expected parameters
- **THEN** the response contains `heat_pump.hc_setpoint`, `heat_pump.operating_state`, `heat_pump.heat_demand`, `heat_pump.defrost`, `buffer.temp`, `buffer.setpoint`, `heating_circuit_1.valve_position` and `heating_circuit_2.valve_position`, each populated from the device

#### Scenario: Buffer temperature shown without a unit
- **WHEN** the buffer page shows the buffer temperature as a bare number with no `°C` suffix (e.g. `42.5`)
- **THEN** `buffer.temp` is that number, parsed as a float

#### Scenario: One new value is missing
- **WHEN** a view page lacks one of the new parameters, e.g. after a firmware update, while all existing parameters are present
- **THEN** the response is HTTP 200, the missing value is `null`, and every other field is populated as before

#### Scenario: Buffer page unparseable
- **WHEN** the buffer page responds but contains none of the expected buffer parameters
- **THEN** the response is HTTP 200 with `buffer` set to `null`, and the service logs a warning

#### Scenario: Buffer page unreachable
- **WHEN** the buffer page request fails with a network error
- **THEN** the service returns a 502 error and does not return a partial status object, as for any other view page

#### Scenario: Existing fields unchanged
- **WHEN** `GET /api/v1/status` is called after this change
- **THEN** every field present before the change is still present, with the same name, type and value semantics
