# Heatpump Control

## Purpose

Retrieves the current heatpump state by parsing HTML view pages from the HPM web UI and returns it as a structured multi-subsystem data model.
## Requirements
### Requirement: Read current heatpump state
The service SHALL retrieve the current state of the HPM heating system by fetching the HTML view pages for the heat pump unit, heating circuit 1, and domestic hot water subsystem, and return it as a structured `SystemStatus` model. The model SHALL include the system operating mode, outdoor temperature, heat pump unit status, heating circuit 1 status, and domestic hot water status.

#### Scenario: State retrieval succeeds
- **WHEN** a status request is made and all three view pages respond successfully
- **THEN** the service returns a `SystemStatus` object with all fields populated, including: operating mode (one of off/auto/summer/vacation/nominalOp/manual), heat pump on/off state, outlet and return water temperatures, compressor frequency, heating circuit flow setpoint and actual temperature, room setpoint, DHW target and actual tank temperature, and outdoor temperature

#### Scenario: Web UI returns unexpected response structure
- **WHEN** a view page response does not contain the expected parameter anchors (e.g. after a firmware update)
- **THEN** the service SHALL return a 502 error with a message indicating the upstream response was unparseable, and log the raw HTML for diagnostics

#### Scenario: One subsystem page is unreachable
- **WHEN** one of the view page requests fails with a network error while others succeed
- **THEN** the service SHALL return a 502 error and SHALL NOT return a partial status object

### Requirement: System data model reflects HPM structure
The service SHALL model the heatpump state as a multi-subsystem structure, not as a flat air-conditioner model. The `SystemStatus` type SHALL contain nested models for the heat pump unit, heating circuit, and domestic hot water.

#### Scenario: Status response matches HPM subsystem structure
- **WHEN** `GET /api/v1/status` is called
- **THEN** the JSON response contains top-level fields `operating_mode`, `outdoor_temp`, `heat_pump`, `heating_circuit_1`, and `domestic_hot_water`, each with the sub-fields defined in the data model

#### Scenario: Old AC-style fields are absent
- **WHEN** `GET /api/v1/status` is called
- **THEN** the response SHALL NOT contain fields named `mode`, `fan_speed`, `current_temp`, or `target_temp` (the prior air-conditioner model fields)

### Requirement: Read and write the HC2 flow-temperature limitation

The service SHALL read and write the HC2 "setpoint limitation" function on the HPM WEB-RC interface. It SHALL navigate to the limitation page by matching menu link labels from root — `MCR-BMS → heatCirc. → heatC. 2 → function → setpoint limitation` — never by hard-coded `(branchnr, level)` pairs, and SHALL serialise this navigation with all other WEB-RC navigation under a single lock so concurrent operations on the stateful session do not interfere.

For reads, the service SHALL parse the `active`, `minFl`, and `maxFl` values (device params `2.5.2.3.6.1`/`.2`/`.3`) from the limitation page HTML.

For writes, the service SHALL set each target parameter via `POST /execset.rsp` using the limitation page's branch/level (position within the page: `active`, `minFl`, `maxFl`), and SHALL pre-validate each value against the range reported by `info.rsp` for that parameter and against the device constraint `maxFl > minFl` before writing. Because the device returns a 302 redirect for both success and failure, the service SHALL rely on this pre-validation rather than the response status to reject invalid writes.

#### Scenario: Read the current limitation
- **WHEN** the service reads the HC2 flow limitation
- **THEN** it navigates by label to the setpoint-limitation page and returns the parsed `active`, `minFl`, and `maxFl` values

#### Scenario: Write the limitation with set-and-enable
- **WHEN** the service applies a flow-limit change for HC2
- **THEN** it writes `minFl`, a `maxFl` strictly greater than `minFl`, and `active = 1` via `execset` against the limitation page's branch/level, after validating each value against its `info.rsp` range and the `maxFl > minFl` constraint

#### Scenario: Pre-validation rejects an invalid write
- **WHEN** a requested limitation value is outside the device's `info.rsp` range, or would make `maxFl <= minFl`
- **THEN** the service SHALL NOT issue the `execset` request and SHALL surface a validation error

