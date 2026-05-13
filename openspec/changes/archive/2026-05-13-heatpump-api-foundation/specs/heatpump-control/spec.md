## ADDED Requirements

### Requirement: Read current heatpump state
The service SHALL retrieve the current state of the heatpump from the web UI and return it as a structured data model. State SHALL include at minimum: power status, operating mode, current temperature, target temperature, and fan speed.

#### Scenario: State retrieval succeeds
- **WHEN** a status request is made and the web UI responds successfully
- **THEN** the service returns a structured state object with all available fields populated

#### Scenario: Web UI returns unexpected response structure
- **WHEN** the web UI response does not match the expected structure (e.g., after a firmware update)
- **THEN** the service SHALL return a 502 error with a message indicating the upstream response was unparseable, and log the raw response for diagnostics

### Requirement: Send control commands
The service SHALL translate control commands received via the REST API into the equivalent HTTP requests to the heatpump web UI and confirm the operation.

#### Scenario: Valid control command is issued
- **WHEN** a valid control command is received (e.g., set target temperature, change mode)
- **THEN** the service sends the corresponding request to the web UI and returns success when the web UI acknowledges it

#### Scenario: Invalid command value is rejected before proxying
- **WHEN** a command contains a value outside the allowed range (e.g., temperature below minimum or above maximum)
- **THEN** the service SHALL return a 422 error without sending any request to the web UI

#### Scenario: Web UI rejects the command
- **WHEN** the web UI returns an error response to a control request
- **THEN** the service SHALL return a 502 error and include the upstream error detail in the response

### Requirement: Proxy fidelity
The service SHALL not alter or interpret control command semantics — it proxies what the web UI accepts. Allowed values, ranges, and modes are determined by the web UI and reflected in the API, not hardcoded by the proxy.

#### Scenario: Unsupported command for this heatpump model
- **WHEN** the web UI rejects a command that is valid in the API schema but unsupported by this specific heatpump model
- **THEN** the service returns the upstream error as-is with a 502 status rather than silently succeeding
