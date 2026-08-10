## MODIFIED Requirements

### Requirement: Read all setpoints for a heating circuit
The service SHALL expose `GET /api/v1/circuits/{circuit_id}/setpoints` returning the six temperature setpoints for the specified circuit as a JSON object with float values in °C. `circuit_id` SHALL be either `hc1` or `hc2`.

Before parsing values, the service SHALL confirm that the page it navigated to is the setpoints page for the requested circuit. Returning another circuit's values is a correctness failure in its own right, because a consumer acting on those values may then write incorrect setpoints back.

#### Scenario: Successful read of HC2 setpoints
- **WHEN** `GET /api/v1/circuits/hc2/setpoints` is called
- **THEN** the service navigates to the WEB-RC setpoints page for HC2, confirms the page identifies as HC2 setpoints, parses the table, and returns 200 with a JSON body containing `roomOT1`, `roomOT2`, `roomOT3`, `roomOT4`, `roomNO`, `roomSNOT` as float fields (e.g. `{"roomOT1": 35.0, ...}`)

#### Scenario: Successful read of HC1 setpoints
- **WHEN** `GET /api/v1/circuits/hc1/setpoints` is called
- **THEN** the service navigates to the WEB-RC setpoints page for HC1, confirms the page identifies as HC1 setpoints, and returns 200 with the same JSON structure

#### Scenario: Read lands on the wrong circuit
- **WHEN** a read for one circuit navigates to a page identifying as the other circuit
- **THEN** the service SHALL NOT return the parsed values and SHALL return 502

#### Scenario: Unknown circuit ID
- **WHEN** `GET /api/v1/circuits/hc3/setpoints` or any unrecognised circuit_id is called
- **THEN** the service returns 404

### Requirement: Write one or more setpoints for a heating circuit
The service SHALL expose `PATCH /api/v1/circuits/{circuit_id}/setpoints` accepting a JSON body with a subset of setpoint fields to update. Each field present in the body SHALL be written to the device via `execset.rsp` in the WEB-RC context. Fields absent from the body SHALL NOT be modified.

Because `execset.rsp` addresses parameters by a `(branchnr, level)` pair that the device resolves relative to the current navigation position, and because the setpoints pages of HC1 and HC2 share the same coordinates, the service SHALL confirm the target page identifies as the setpoints page of the intended circuit immediately before issuing any write. A write SHALL NOT be issued against an unverified page.

After writing, the service SHALL read the page back and confirm the field holds the requested value. The device returns a 302 redirect for both accepted and rejected writes, so the response status alone SHALL NOT be treated as evidence that a write took effect.

#### Scenario: Patch a single setpoint
- **WHEN** `PATCH /api/v1/circuits/hc2/setpoints` is called with body `{"roomOT1": 38.0}`
- **THEN** the service navigates to the HC2 setpoints WEB-RC page, confirms the page identifies as HC2 setpoints, posts the new value to `execset.rsp` for the roomOT1 position, reads the page back to confirm `roomOT1` is 38.0, and returns 200 with the full updated setpoints object

#### Scenario: Patch multiple setpoints
- **WHEN** `PATCH /api/v1/circuits/hc2/setpoints` is called with body `{"roomOT1": 38.0, "roomNO": 18.0}`
- **THEN** the service writes each field in sequence, confirming page identity before each write, and returns 200 with the full updated setpoints object

#### Scenario: Write target cannot be verified
- **WHEN** the page reached for a setpoint write does not identify as the setpoints page of the requested circuit
- **THEN** the service SHALL NOT issue the `execset` request and SHALL return 502

#### Scenario: Write does not take effect
- **WHEN** the read-back after a write shows a value other than the one requested
- **THEN** the service SHALL return 502 rather than reporting success

#### Scenario: Value out of device range
- **WHEN** the device rejects a value because it falls outside its accepted range
- **THEN** the service returns 422 with an error body identifying the field and the device-reported limits

#### Scenario: Unknown setpoint field in body
- **WHEN** the request body contains a key that is not one of the six defined setpoints (e.g. `{"hCu_slope": 0.7}`)
- **THEN** the service returns 422 before contacting the device

#### Scenario: Empty patch body
- **WHEN** `PATCH /api/v1/circuits/{circuit_id}/setpoints` is called with an empty JSON object `{}`
- **THEN** the service returns 200 with the current setpoints unchanged (no device writes are made)
