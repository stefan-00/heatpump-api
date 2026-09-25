## ADDED Requirements

### Requirement: Heat-source, buffer and mixing-valve values are available as HA entities
`packages/heatpump.yaml` SHALL expose the new status values from the same `rest` poll of `GET /api/v1/status`. These entities are:

- sensors, with `°C` and device class `temperature`:
  - `heat_pump.hc_setpoint`;
  - `buffer.temp` and `buffer.setpoint`;
- sensors, with unit `%`:
  - `heating_circuit_1.valve_position`;
  - `heating_circuit_2.valve_position`;
- text sensors: `heat_pump.operating_state` and `heat_pump.heat_demand`;
- a binary sensor: `heat_pump.defrost`.

The entities SHALL follow the naming of the existing package entities: names start with `Heatpump`, `HC1` or `HC2`, and `unique_id`s start with `heatpump_`. That way they are recorded in InfluxDB the same way as the existing heatpump sensors. A value the API returns as `null` SHALL make its entity `unavailable` or `unknown`, and SHALL NOT make it `0`.

#### Scenario: New values reach HA and InfluxDB
- **WHEN** HA polls `GET /api/v1/status` and the response contains the new fields
- **THEN** each new entity updates to the value from the response, and its history appears in InfluxDB alongside the existing heatpump sensors

#### Scenario: A new value is null
- **WHEN** the status response contains `null` for one of the new values, such as `"buffer": null`
- **THEN** the corresponding entities show `unavailable` or `unknown` rather than `0`, and the other entities keep updating
