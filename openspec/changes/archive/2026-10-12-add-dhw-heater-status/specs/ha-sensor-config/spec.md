## ADDED Requirements

### Requirement: Tank-heating, heater and DHW-setpoint values are available as HA entities
`packages/heatpump.yaml` SHALL expose the tank-heating, heater and DHW-setpoint status values from the same `rest` poll of `GET /api/v1/status`. These entities are:

- binary sensors: `heat_pump.tank_heating`, `heat_pump.electric_heater` and `heat_pump.booster_heater`;
- a sensor with `°C` and device class `temperature`: `heat_pump.dhw_setpoint`, named `Heatpump DHW Setpoint` so that its entity id is `sensor.heatpump_dhw_setpoint`.

`Heatpump DHW Setpoint` SHALL NOT reuse the name or `unique_id` of the existing `DHW Setpoint` sensor (`sensor.dhw_setpoint`, the controller's own tank setpoint), so the two can't be mixed up and neither replaces the other's history.

The entities SHALL follow the naming of the existing package entities: names start with `Heatpump`, and `unique_id`s start with `heatpump_`. A value the API returns as `null` SHALL make its entity `unavailable` or `unknown`, and SHALL NOT make it `0` or `off`.

#### Scenario: New values reach HA
- **WHEN** HA polls `GET /api/v1/status` and the response contains `heat_pump.tank_heating`, `heat_pump.electric_heater`, `heat_pump.booster_heater` and `heat_pump.dhw_setpoint`
- **THEN** each of the four entities updates to the value from the response, and the existing `sensor.dhw_setpoint` keeps showing `domestic_hot_water.setpoint`

#### Scenario: A new value is null
- **WHEN** the status response contains `"booster_heater": null`
- **THEN** the booster heater entity shows `unavailable` or `unknown` rather than `off`, and the other entities keep updating
