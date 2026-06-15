## REMOVED Requirements

### Requirement: Control endpoints
**Reason**: Describes the removed air-conditioner model (`POST /api/v1/control/` for power on/off, operating mode, target temperature, fan speed). The service never shipped these endpoints; control was implemented as writable heating-circuit setpoints. The requirement contradicts the `heatpump-control` capability, which explicitly states the AC-style fields are absent.
**Migration**: Use `PATCH /api/v1/circuits/{circuit_id}/setpoints` (see the new "Setpoint control endpoints" requirement below and the `heating-circuit-setpoints` capability). No client migration is required because the `POST /control/` endpoints were never available.

## ADDED Requirements

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
