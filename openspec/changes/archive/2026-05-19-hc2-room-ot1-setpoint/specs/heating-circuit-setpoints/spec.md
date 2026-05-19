# Heating Circuit Setpoints

## Purpose

Expose the temperature setpoints for each heating circuit (HC1, HC2) as a readable and writable REST resource. Setpoints are sourced from the WEB-RC menu (access level 3) which provides the full set of six temperature setpoints unavailable in the standard v*.rsp pages.

## ADDED Requirements

### Requirement: Read all setpoints for a heating circuit
The service SHALL expose `GET /api/v1/circuits/{circuit_id}/setpoints` returning the six temperature setpoints for the specified circuit as a JSON object with float values in °C. `circuit_id` SHALL be either `hc1` or `hc2`.

#### Scenario: Successful read of HC2 setpoints
- **WHEN** `GET /api/v1/circuits/hc2/setpoints` is called
- **THEN** the service navigates to the WEB-RC setpoints page for HC2, parses the table, and returns 200 with a JSON body containing `roomOT1`, `roomOT2`, `roomOT3`, `roomOT4`, `roomNO`, `roomSNOT` as float fields (e.g. `{"roomOT1": 35.0, ...}`)

#### Scenario: Successful read of HC1 setpoints
- **WHEN** `GET /api/v1/circuits/hc1/setpoints` is called
- **THEN** the service navigates to the WEB-RC setpoints page for HC1 and returns 200 with the same JSON structure

#### Scenario: Unknown circuit ID
- **WHEN** `GET /api/v1/circuits/hc3/setpoints` or any unrecognised circuit_id is called
- **THEN** the service returns 404

### Requirement: Write one or more setpoints for a heating circuit
The service SHALL expose `PATCH /api/v1/circuits/{circuit_id}/setpoints` accepting a JSON body with a subset of setpoint fields to update. Each field present in the body SHALL be written to the device via `execset.rsp` in the WEB-RC context. Fields absent from the body SHALL NOT be modified.

#### Scenario: Patch a single setpoint
- **WHEN** `PATCH /api/v1/circuits/hc2/setpoints` is called with body `{"roomOT1": 38.0}`
- **THEN** the service navigates to the HC2 setpoints WEB-RC page, posts the new value to `execset.rsp` for the roomOT1 position, and returns 200 with the full updated setpoints object

#### Scenario: Patch multiple setpoints
- **WHEN** `PATCH /api/v1/circuits/hc2/setpoints` is called with body `{"roomOT1": 38.0, "roomNO": 18.0}`
- **THEN** the service writes each field in sequence and returns 200 with the full updated setpoints object

#### Scenario: Value out of device range
- **WHEN** the device rejects a value because it falls outside its accepted range
- **THEN** the service returns 422 with an error body identifying the field and the device-reported limits

#### Scenario: Unknown setpoint field in body
- **WHEN** the request body contains a key that is not one of the six defined setpoints (e.g. `{"hCu_slope": 0.7}`)
- **THEN** the service returns 422 before contacting the device

#### Scenario: Empty patch body
- **WHEN** `PATCH /api/v1/circuits/{circuit_id}/setpoints` is called with an empty JSON object `{}`
- **THEN** the service returns 200 with the current setpoints unchanged (no device writes are made)
