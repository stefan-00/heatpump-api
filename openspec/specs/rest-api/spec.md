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

### Requirement: Control endpoints
The service SHALL expose control endpoints under `POST /api/v1/control/` that allow callers to change heatpump settings. Initial endpoints SHALL cover: power on/off, operating mode, target temperature, and fan speed.

#### Scenario: Valid control request
- **WHEN** a `POST /api/v1/control/<command>` is made with a valid JSON body
- **THEN** the service returns HTTP 200 with a confirmation JSON body

#### Scenario: Malformed request body
- **WHEN** the request body is missing required fields or contains invalid types
- **THEN** the service returns HTTP 422 with a JSON body listing the validation errors

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
