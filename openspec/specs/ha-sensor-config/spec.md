# HA Sensor Configuration

## Purpose

Define the documented HA configuration that exposes the heatpump API as native HA entities using only HA's built-in `rest` and `number` integrations. No custom component is required.

## Requirements

### Requirement: Heatpump status is available as HA sensor entities
A `packages/heatpump.yaml` package file SHALL provide ready-to-use HA configuration using HA's `rest` sensor platform to poll `GET /api/v1/status` and expose the following as individual sensor entities: `operating_mode`, `outdoor_temp`, `heat_pump.on`, `heat_pump.heating`, `heat_pump.outlet_temp`, `heat_pump.return_temp`, `heat_pump.frequency`, `heat_pump.error_code`, `heating_circuit_1.flow_setpoint`, `heating_circuit_1.flow_temp`, `heating_circuit_1.room_setpoint`, `heating_circuit_1.pump_on`, `domestic_hot_water.setpoint`, `domestic_hot_water.actual_temp`. Each sensor SHALL include a `unit_of_measurement` and `device_class` where applicable. `docs/ha-integration.md` SHALL document how to install the package.

#### Scenario: HA polls the status endpoint
- **WHEN** HA's `rest` sensor platform polls `GET http://<ha-host-ip>:8765/api/v1/status` on its `scan_interval`
- **THEN** each configured sensor entity updates to reflect the current value from the JSON response

#### Scenario: Add-on is not running
- **WHEN** the add-on is stopped and HA polls the status endpoint
- **THEN** the sensor entities become `unavailable` (standard HA `rest` sensor behavior on connection failure)

### Requirement: HC1 setpoints are available as HA number entities
`packages/heatpump.yaml` SHALL expose all six HC1 setpoints (`roomOT1`, `roomOT2`, `roomOT3`, `roomOT4`, `roomNO`, `roomSNOT`) as writable number entities using HA's `template` number platform backed by `rest_command`. Each entity SHALL read from `GET /api/v1/circuits/hc1/setpoints` and write via `PATCH /api/v1/circuits/hc1/setpoints` with the appropriate JSON body.

#### Scenario: User reads an HC1 setpoint in HA
- **WHEN** HA polls `GET /api/v1/circuits/hc1/setpoints`
- **THEN** each of the six HC1 number entities shows the current setpoint value in °C

#### Scenario: User changes an HC1 setpoint from HA
- **WHEN** a user sets a new value on an HC1 number entity in the HA UI or via automation
- **THEN** HA issues `PATCH /api/v1/circuits/hc1/setpoints` with a JSON body containing the field and new value (e.g. `{"roomOT1": 21.0}`), and the entity state updates to the confirmed value returned by the API

#### Scenario: User sets an out-of-range HC1 value
- **WHEN** a user attempts to set a value outside the device's accepted range via the number entity
- **THEN** the API returns 422 and the entity state remains at the previous value

### Requirement: HC2 setpoints are available as HA number entities
`packages/heatpump.yaml` SHALL expose all six HC2 setpoints (`roomOT1`, `roomOT2`, `roomOT3`, `roomOT4`, `roomNO`, `roomSNOT`) as writable number entities using HA's `template` number platform backed by `rest_command`. Each entity SHALL read from `GET /api/v1/circuits/hc2/setpoints` and write via `PATCH /api/v1/circuits/hc2/setpoints`.

#### Scenario: User reads an HC2 setpoint in HA
- **WHEN** HA polls `GET /api/v1/circuits/hc2/setpoints`
- **THEN** each of the six HC2 number entities shows the current setpoint value in °C

#### Scenario: User changes an HC2 setpoint from HA
- **WHEN** a user sets a new value on an HC2 number entity in the HA UI or via automation
- **THEN** HA issues `PATCH /api/v1/circuits/hc2/setpoints` with a JSON body containing the field and new value, and the entity state updates to the confirmed value returned by the API

### Requirement: Integration guide documents the base URL and polling interval
`docs/ha-integration.md` SHALL document that the HA host's LAN IP (e.g. `http://192.168.1.x:8765`) is required as the base URL when the API runs as an HAOS add-on — `localhost` does NOT work because HA Core and add-ons run in separate Docker containers. The guide SHALL recommend a minimum `scan_interval` of 30 seconds to avoid saturating the single HPM device session.

#### Scenario: User follows the guide on a non-HAOS installation
- **WHEN** a user runs the API as a standalone Docker container on a separate host
- **THEN** the guide instructs them to use that host's IP address or hostname as the base URL
