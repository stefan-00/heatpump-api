## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Send control commands
**Reason**: The original `send_command` API assumed AC-style commands (power on/off, heat/cool/dry/fan modes, single temperature setpoint, fan speed). The HPM-800B7F is a multi-zone heating system with no such commands. Control is via `POST /execgrset.rsp` with a parameter ID and value, and mode switching via `POST /ms.rsp`.
**Migration**: Control endpoints will be re-introduced in the next change as zone-specific setpoint commands (e.g. `POST /api/v1/heating-circuit/1/setpoints`) and a system mode command (`POST /api/v1/system/mode`), using the discovered HPM write protocol.

### Requirement: Proxy fidelity
**Reason**: The original proxy-fidelity requirement was framed around AC command semantics. The HPM uses a parameter-ID-based write protocol (`execgrset.rsp`) that is being deferred to the control change.
**Migration**: Will be re-introduced in the control change with HPM-specific semantics: allowed value ranges are those returned by `vinfo.rsp` for each parameter ID, not hardcoded enums.
