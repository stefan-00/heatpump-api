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

### Requirement: Sensors degrade gracefully when the API returns an error body

When the API returns an error response (e.g. HTTP 502 with a JSON body such as `{"detail": "..."}`), an empty/non-JSON body, or no response at all (a fetch timeout), the configured HA sensor entities SHALL become `unavailable` rather than logging template errors or showing stale/invalid values. Each sensor in `packages/heatpump.yaml` SHALL use an `availability` template that FIRST guards `value_json is defined` and THEN checks for the presence of its expected key, AND a `value_template` that itself short-circuits to `none` when the expected key is absent — because HA's `rest` platform still renders `value_template` even when `availability` is false. The leading `value_json is defined` guard is required because when a poll times out or returns a non-JSON/empty body `value_json` is undefined entirely, and dereferencing it (`value_json.key`) or testing membership (`'key' in value_json`) raises `UndefinedError` while rendering the `availability` template itself.

#### Scenario: API returns an error body during a poll
- **WHEN** HA polls `GET /api/v1/status` (or a setpoints endpoint) and the response body lacks the expected keys (e.g. an error envelope)
- **THEN** the affected sensor entities become `unavailable` and no `Template variable error` is logged for the missing keys

#### Scenario: A poll times out or returns no parseable body
- **WHEN** HA polls an endpoint and the fetch times out or the body is empty/non-JSON, so `value_json` is undefined
- **THEN** the affected sensor entities become `unavailable` and no `UndefinedError` is logged for the `availability` template

#### Scenario: API returns a valid payload
- **WHEN** HA polls an endpoint and the response contains the expected keys
- **THEN** each sensor's `availability` template evaluates true and its `value_template` renders the value as normal

### Requirement: Writable number entities degrade gracefully when their source sensor is unavailable

Each writable `template` number entity in `packages/heatpump.yaml` SHALL guard its state with an `availability` template that checks `has_value(...)` on the backing setpoint sensor, so that when the sensor is `unavailable` (e.g. its poll timed out) the number entity becomes `unavailable` rather than attempting to coerce the literal string `unavailable` into a number. This applies to all twelve number entities, including `roomNO`/`roomSNOT` (`Room Normal`/`Room Standby`), not only the optional `roomOT1`–`roomOT4` breakpoints.

#### Scenario: Source setpoint sensor is unavailable
- **WHEN** a number entity's backing sensor (e.g. `sensor.hc1_setpoint_roomno`) is `unavailable`
- **THEN** the number entity becomes `unavailable` and no `invalid number state: unavailable` validation error is logged

### Requirement: HA fetch timeouts accommodate slow setpoint reads and writes

The HPM setpoint endpoints traverse stateful WEB-RC navigation serialized on a single device session, so a read or write can take substantially longer than the default HA fetch timeout of 10 seconds. `packages/heatpump.yaml` SHALL therefore set an explicit `timeout` on every `rest` resource and on every `rest_command`, sized comfortably above the API's per-request budget (default 15 seconds), so that slow-but-successful setpoint operations complete within a single HA call instead of being aborted. The setpoint `rest` resources MAY poll on a longer `scan_interval` than the status resource, because setpoints are writable configuration values that change rarely, which also reduces contention on the device session.

#### Scenario: A setpoint write takes longer than the HA default timeout
- **WHEN** a user sets a number entity and the `rest_command` PATCH to the setpoint endpoint takes longer than 10 seconds but completes within the configured `timeout`
- **THEN** HA completes the call successfully and no `Timeout when calling resource` error is logged

#### Scenario: A setpoint read takes longer than the HA default timeout
- **WHEN** HA polls a setpoint resource and the response takes longer than 10 seconds but completes within the configured `timeout`
- **THEN** the fetch succeeds and the setpoint sensors update normally
