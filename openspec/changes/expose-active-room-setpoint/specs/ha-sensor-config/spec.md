## ADDED Requirements

### Requirement: Operating period and active room setpoint are available as HA entities
`packages/heatpump.yaml` SHALL expose, for HC1 and HC2, the circuit's operating period and the room setpoint in force.

- A text sensor per circuit, "HC1 Operating Period" / "HC2 Operating Period", from the `period` field of the existing `GET /api/v1/status` poll. It SHALL carry the raw `operating_status` and `timer_status` strings as attributes.
- A temperature sensor per circuit, "HC1 Active Room Setpoint" / "HC2 Active Room Setpoint", with entity_ids `sensor.hc1_active_room_setpoint` and `sensor.hc2_active_room_setpoint`, unit `°C` and device class `temperature`. Its value SHALL be the API's `active_room_setpoint` when that is not `null`; otherwise, when the period is known, the value of that circuit's existing setpoint sensor for the period (`sensor.hcN_setpoint_room<period>`, from the `/setpoints` poll).

The active-setpoint entity SHALL be `unavailable` or `unknown`, never `0`, when the period is unknown or no source has a value. The entity_ids SHALL match the existing `sensor.hc1_*` / `sensor.hc2_*` patterns so InfluxDB records them without a configuration change.

#### Scenario: Period's setpoint is on the status page
- **WHEN** the status poll reports HC1 `period = OT2` and `active_room_setpoint = 18.0`
- **THEN** `sensor.hc1_operating_period` is `OT2` and `sensor.hc1_active_room_setpoint` is `18.0`

#### Scenario: Period's setpoint is only on the setpoints page
- **WHEN** the status poll reports HC2 `period = SNOT` with `active_room_setpoint = null`, and `sensor.hc2_setpoint_roomsnot` is `2.0`
- **THEN** `sensor.hc2_active_room_setpoint` is `2.0`

#### Scenario: Period unknown
- **WHEN** the status poll reports `period = null` for a circuit
- **THEN** that circuit's active-setpoint sensor is `unavailable` or `unknown`, and the operating-period sensor shows no period while its attributes still carry the raw strings

### Requirement: roomNO-backed entities are named for what they hold
The entities backed by the `roomNO` setpoint SHALL be named for the non-occupation-time setpoint: the status sensors "HC1 Room Setpoint" and "HC2 Room Setpoint" SHALL be renamed to "HC1 Room Setpoint NO" and "HC2 Room Setpoint NO". The writable number entities for `roomNO` and `roomSNOT` SHALL be named for non-occupation and special non-occupation (holiday) time rather than "Normal" and "Standby". Renaming SHALL change only friendly names: `unique_id`s and entity_ids SHALL stay as they are, because InfluxDB history and dashboards are keyed on the entity_id.

#### Scenario: Renamed sensor keeps its history
- **WHEN** the updated package is loaded in HA
- **THEN** `sensor.hc1_room_setpoint` still exists under that entity_id, shows the friendly name "HC1 Room Setpoint NO", and its InfluxDB series continues without a break
