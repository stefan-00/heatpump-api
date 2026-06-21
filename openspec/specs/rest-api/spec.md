# REST API

## Purpose

Defines the HTTP API surface exposed by the service, including status, control, health, and documentation endpoints, as well as consistent error response formatting and runtime configuration of the listen address.
## Requirements
### Requirement: Status endpoint
The service SHALL expose a `GET /api/v1/status` endpoint that returns the current heatpump state as JSON.

#### Scenario: Successful status request
- **WHEN** `GET /api/v1/status` is called and the heatpump is reachable
- **THEN** the service returns HTTP 200 with a JSON body containing the current heatpump state

#### Scenario: Heatpump unreachable
- **WHEN** `GET /api/v1/status` is called but the heatpump web UI cannot be reached
- **THEN** the service returns HTTP 502 with a JSON error body describing the upstream failure

### Requirement: Setpoint control endpoints
The service SHALL expose writable heating-circuit setpoints under `GET` and `PATCH /api/v1/circuits/{circuit_id}/setpoints`, where `circuit_id` is `hc1` or `hc2`. A `PATCH` SHALL accept a JSON body containing one or more setpoint fields and SHALL validate each value against the device's accepted range before writing.

#### Scenario: Read current setpoints
- **WHEN** `GET /api/v1/circuits/hc1/setpoints` is called and the heatpump is reachable
- **THEN** the service returns HTTP 200 with a JSON body of the current setpoint values

#### Scenario: Write a valid setpoint
- **WHEN** `PATCH /api/v1/circuits/hc1/setpoints` is called with a valid JSON body (e.g. `{"roomOT1": 21.0}`)
- **THEN** the service writes the value to the device and returns HTTP 200 with the confirmed setpoints

#### Scenario: Write an out-of-range setpoint
- **WHEN** `PATCH /api/v1/circuits/{circuit_id}/setpoints` is called with a value outside the device's accepted range
- **THEN** the service returns HTTP 422 with a JSON error body and does not write the value

#### Scenario: Unknown circuit identifier
- **WHEN** a request targets a `circuit_id` other than `hc1` or `hc2`
- **THEN** the service returns an error response and does not attempt a device write

### Requirement: Structured error responses
All error responses SHALL use a consistent JSON envelope with at minimum a `detail` field describing the error.

#### Scenario: Any error condition
- **WHEN** the service returns any non-2xx HTTP status
- **THEN** the response body is JSON with at least `{"detail": "<human-readable message>"}`

### Requirement: OpenAPI documentation
The service SHALL serve an OpenAPI schema at `GET /openapi.json` and an interactive UI at `GET /docs`, auto-generated from the FastAPI route definitions.

#### Scenario: Docs endpoint is reachable
- **WHEN** `GET /docs` is requested
- **THEN** the service returns HTTP 200 with the Swagger UI

### Requirement: Health check endpoint
The service SHALL expose `GET /health` that returns HTTP 200 when the service is running, regardless of whether the heatpump is currently reachable.

#### Scenario: Service is running
- **WHEN** `GET /health` is called
- **THEN** the service returns HTTP 200 with `{"status": "ok"}`

### Requirement: Configurable listen address and port
The service SHALL read its bind address and port from configuration and default to `0.0.0.0:8765` if not specified.

#### Scenario: Custom port configured
- **WHEN** the configuration specifies a port value
- **THEN** the service binds to that port on startup

#### Scenario: Default port used when not configured
- **WHEN** no port is specified in configuration
- **THEN** the service binds to port 8765

### Requirement: HC2 flow-limit control endpoint

The service SHALL expose the HC2 heating-circuit flow-temperature limitation under `GET` and `PATCH /api/v1/circuits/hc2/flow-limit`. This controls the device "setpoint limitation" function, whose `minFl` floor forces the effective flow setpoint to `max(curve, minFl)` so HC2 (pool heating) can demand heat independently of the outdoor temperature.

The `GET` SHALL return the current limitation state as JSON with at least `active` (boolean), `min_flow` (°C), and `max_flow` (°C).

The `PATCH` SHALL accept a JSON body containing a `flow_setpoint` value (°C) and SHALL, in a single request, enable the limitation and set it: it SHALL write `minFl = flow_setpoint`, SHALL ensure `maxFl > minFl` (raising `maxFl` to the device default cap of 65 °C when the current `maxFl` is not strictly greater than the requested `flow_setpoint`), and SHALL set `active = 1`. This makes the feature controllable from a single Home Assistant `number` entity without a separate enable toggle.

Every written value SHALL be validated against the device's accepted range (read from `info.rsp`, currently 2.0–160 °C) and against the device constraint that `maxFl` MUST be strictly greater than `minFl`, before any write is attempted.

The endpoint SHALL be HC2-only; a request for any other circuit SHALL return an error response without attempting a device write.

#### Scenario: Read current flow limit
- **WHEN** `GET /api/v1/circuits/hc2/flow-limit` is called and the heatpump is reachable
- **THEN** the service returns HTTP 200 with a JSON body containing `active`, `min_flow`, and `max_flow`

#### Scenario: Set and enable the flow limit in one request
- **WHEN** `PATCH /api/v1/circuits/hc2/flow-limit` is called with `{"flow_setpoint": 30.0}`
- **THEN** the service writes `minFl = 30.0`, raises `maxFl` to a value strictly greater than 30.0 (the 65 °C default cap when needed), sets `active = 1`, and returns HTTP 200 with the resulting `active`/`min_flow`/`max_flow`

#### Scenario: Requested value out of device range
- **WHEN** `PATCH /api/v1/circuits/hc2/flow-limit` is called with a `flow_setpoint` outside the device's accepted range (e.g. below 2.0 °C or above 160 °C)
- **THEN** the service returns HTTP 422 with a JSON error body and does not write any value

#### Scenario: Requested value would violate maxFl > minFl
- **WHEN** a `PATCH` would result in `maxFl <= minFl` and `maxFl` cannot be raised within range to satisfy the constraint
- **THEN** the service returns HTTP 422 with a JSON error body and does not write any value

#### Scenario: Flow limit requested for an unsupported circuit
- **WHEN** the flow-limit endpoint is targeted at any circuit other than `hc2`
- **THEN** the service returns an error response and does not attempt a device write

