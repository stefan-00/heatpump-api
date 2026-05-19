# Home Assistant Integration Guide

This guide shows how to expose the Heatpump API as native Home Assistant entities using
only HA's built-in integrations — no custom component required.

## Prerequisites

The Heatpump API add-on must be installed and running. Verify it with:

```
GET http://localhost:8765/health
→ {"status": "ok"}
```

## Base URL

| Setup | Base URL |
|---|---|
| HAOS add-on | `http://<ha-host-ip>:8765` (e.g. `http://192.168.1.x:8765`) |
| Standalone Docker on a separate host | `http://<host-ip>:8765` |

> **Note:** `localhost` does **not** work from within HA's `configuration.yaml` on HAOS.
> HA Core and add-ons run in separate Docker containers; the add-on's published port is
> only reachable via the host's LAN IP address.

## Polling interval

The HPM device supports only one active session at a time. Use a minimum `scan_interval`
of **30 seconds** to avoid saturating the session. Lower values risk interfering with
the API's own session management.

---

## Status sensors

Add the following to your `configuration.yaml`. A single HTTP request to `/api/v1/status`
populates all 14 sensors.

```yaml
rest:
  - resource: http://localhost:8765/api/v1/status
    scan_interval: 30
    sensor:
      - name: "Heatpump Operating Mode"
        unique_id: heatpump_operating_mode
        value_template: "{{ value_json.operating_mode }}"

      - name: "Heatpump Outdoor Temperature"
        unique_id: heatpump_outdoor_temp
        value_template: "{{ value_json.outdoor_temp }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "Heat Pump On"
        unique_id: heatpump_hp_on
        value_template: "{{ value_json.heat_pump.on }}"

      - name: "Heat Pump Heating"
        unique_id: heatpump_hp_heating
        value_template: "{{ value_json.heat_pump.heating }}"

      - name: "Heat Pump Outlet Temperature"
        unique_id: heatpump_hp_outlet_temp
        value_template: "{{ value_json.heat_pump.outlet_temp }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "Heat Pump Return Temperature"
        unique_id: heatpump_hp_return_temp
        value_template: "{{ value_json.heat_pump.return_temp }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "Heat Pump Frequency"
        unique_id: heatpump_hp_frequency
        value_template: "{{ value_json.heat_pump.frequency }}"
        unit_of_measurement: "Hz"
        state_class: measurement

      - name: "Heat Pump Error Code"
        unique_id: heatpump_hp_error_code
        value_template: "{{ value_json.heat_pump.error_code }}"

      - name: "HC1 Flow Setpoint"
        unique_id: heatpump_hc1_flow_setpoint
        value_template: "{{ value_json.heating_circuit_1.flow_setpoint }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Flow Temperature"
        unique_id: heatpump_hc1_flow_temp
        value_template: "{{ value_json.heating_circuit_1.flow_temp }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Room Setpoint"
        unique_id: heatpump_hc1_room_setpoint
        value_template: "{{ value_json.heating_circuit_1.room_setpoint }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Pump On"
        unique_id: heatpump_hc1_pump_on
        value_template: "{{ value_json.heating_circuit_1.pump_on }}"

      - name: "DHW Setpoint"
        unique_id: heatpump_dhw_setpoint
        value_template: "{{ value_json.domestic_hot_water.setpoint }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "DHW Actual Temperature"
        unique_id: heatpump_dhw_actual_temp
        value_template: "{{ value_json.domestic_hot_water.actual_temp }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
```

---

## Setpoint sensors

These sensors read the current setpoint values. They are also used as the state source
for the writable number entities below.

```yaml
rest:
  - resource: http://localhost:8765/api/v1/circuits/hc1/setpoints
    scan_interval: 30
    sensor:
      - name: "HC1 Setpoint roomOT1"
        unique_id: heatpump_hc1_sp_roomot1
        value_template: "{{ value_json.roomOT1 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Setpoint roomOT2"
        unique_id: heatpump_hc1_sp_roomot2
        value_template: "{{ value_json.roomOT2 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Setpoint roomOT3"
        unique_id: heatpump_hc1_sp_roomot3
        value_template: "{{ value_json.roomOT3 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Setpoint roomOT4"
        unique_id: heatpump_hc1_sp_roomot4
        value_template: "{{ value_json.roomOT4 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Setpoint roomNO"
        unique_id: heatpump_hc1_sp_roomno
        value_template: "{{ value_json.roomNO }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC1 Setpoint roomSNOT"
        unique_id: heatpump_hc1_sp_roomsnot
        value_template: "{{ value_json.roomSNOT }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

  - resource: http://localhost:8765/api/v1/circuits/hc2/setpoints
    scan_interval: 30
    sensor:
      - name: "HC2 Setpoint roomOT1"
        unique_id: heatpump_hc2_sp_roomot1
        value_template: "{{ value_json.roomOT1 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC2 Setpoint roomOT2"
        unique_id: heatpump_hc2_sp_roomot2
        value_template: "{{ value_json.roomOT2 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC2 Setpoint roomOT3"
        unique_id: heatpump_hc2_sp_roomot3
        value_template: "{{ value_json.roomOT3 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC2 Setpoint roomOT4"
        unique_id: heatpump_hc2_sp_roomot4
        value_template: "{{ value_json.roomOT4 }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC2 Setpoint roomNO"
        unique_id: heatpump_hc2_sp_roomno
        value_template: "{{ value_json.roomNO }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement

      - name: "HC2 Setpoint roomSNOT"
        unique_id: heatpump_hc2_sp_roomsnot
        value_template: "{{ value_json.roomSNOT }}"
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
```

---

## Writable setpoint controls

These create number entities in HA that both display the current setpoint and allow
you to change it from the UI or via automations.

Each control is wired to a `rest_command` that sends a PATCH to the API.

### Step 1 — REST commands

```yaml
rest_command:
  # HC1
  heatpump_set_hc1_roomot1:
    url: http://localhost:8765/api/v1/circuits/hc1/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT1": {{ value }}}'

  heatpump_set_hc1_roomot2:
    url: http://localhost:8765/api/v1/circuits/hc1/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT2": {{ value }}}'

  heatpump_set_hc1_roomot3:
    url: http://localhost:8765/api/v1/circuits/hc1/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT3": {{ value }}}'

  heatpump_set_hc1_roomot4:
    url: http://localhost:8765/api/v1/circuits/hc1/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT4": {{ value }}}'

  heatpump_set_hc1_roomno:
    url: http://localhost:8765/api/v1/circuits/hc1/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomNO": {{ value }}}'

  heatpump_set_hc1_roomsnot:
    url: http://localhost:8765/api/v1/circuits/hc1/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomSNOT": {{ value }}}'

  # HC2
  heatpump_set_hc2_roomot1:
    url: http://localhost:8765/api/v1/circuits/hc2/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT1": {{ value }}}'

  heatpump_set_hc2_roomot2:
    url: http://localhost:8765/api/v1/circuits/hc2/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT2": {{ value }}}'

  heatpump_set_hc2_roomot3:
    url: http://localhost:8765/api/v1/circuits/hc2/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT3": {{ value }}}'

  heatpump_set_hc2_roomot4:
    url: http://localhost:8765/api/v1/circuits/hc2/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomOT4": {{ value }}}'

  heatpump_set_hc2_roomno:
    url: http://localhost:8765/api/v1/circuits/hc2/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomNO": {{ value }}}'

  heatpump_set_hc2_roomsnot:
    url: http://localhost:8765/api/v1/circuits/hc2/setpoints
    method: PATCH
    content_type: application/json
    payload: '{"roomSNOT": {{ value }}}'
```

### Step 2 — Template number entities

```yaml
template:
  - number:
      # ── HC1 ──────────────────────────────────────────────────────────
      - name: "HC1 Room OT1"
        unique_id: heatpump_hc1_num_roomot1
        state: "{{ states('sensor.hc1_setpoint_roomot1') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc1_roomot1
          data:
            value: "{{ value }}"

      - name: "HC1 Room OT2"
        unique_id: heatpump_hc1_num_roomot2
        state: "{{ states('sensor.hc1_setpoint_roomot2') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc1_roomot2
          data:
            value: "{{ value }}"

      - name: "HC1 Room OT3"
        unique_id: heatpump_hc1_num_roomot3
        state: "{{ states('sensor.hc1_setpoint_roomot3') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc1_roomot3
          data:
            value: "{{ value }}"

      - name: "HC1 Room OT4"
        unique_id: heatpump_hc1_num_roomot4
        state: "{{ states('sensor.hc1_setpoint_roomot4') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc1_roomot4
          data:
            value: "{{ value }}"

      - name: "HC1 Room Normal"
        unique_id: heatpump_hc1_num_roomno
        state: "{{ states('sensor.hc1_setpoint_roomno') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc1_roomno
          data:
            value: "{{ value }}"

      - name: "HC1 Room Standby"
        unique_id: heatpump_hc1_num_roomsnot
        state: "{{ states('sensor.hc1_setpoint_roomsnot') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc1_roomsnot
          data:
            value: "{{ value }}"

      # ── HC2 ──────────────────────────────────────────────────────────
      - name: "HC2 Room OT1"
        unique_id: heatpump_hc2_num_roomot1
        state: "{{ states('sensor.hc2_setpoint_roomot1') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc2_roomot1
          data:
            value: "{{ value }}"

      - name: "HC2 Room OT2"
        unique_id: heatpump_hc2_num_roomot2
        state: "{{ states('sensor.hc2_setpoint_roomot2') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc2_roomot2
          data:
            value: "{{ value }}"

      - name: "HC2 Room OT3"
        unique_id: heatpump_hc2_num_roomot3
        state: "{{ states('sensor.hc2_setpoint_roomot3') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc2_roomot3
          data:
            value: "{{ value }}"

      - name: "HC2 Room OT4"
        unique_id: heatpump_hc2_num_roomot4
        state: "{{ states('sensor.hc2_setpoint_roomot4') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc2_roomot4
          data:
            value: "{{ value }}"

      - name: "HC2 Room Normal"
        unique_id: heatpump_hc2_num_roomno
        state: "{{ states('sensor.hc2_setpoint_roomno') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc2_roomno
          data:
            value: "{{ value }}"

      - name: "HC2 Room Standby"
        unique_id: heatpump_hc2_num_roomsnot
        state: "{{ states('sensor.hc2_setpoint_roomsnot') }}"
        min: 2
        max: 50
        step: 0.5
        unit_of_measurement: "°C"
        set_value:
          action: rest_command.heatpump_set_hc2_roomsnot
          data:
            value: "{{ value }}"
```

### How it works

When you drag a slider or enter a value on a number entity:
1. HA calls the corresponding `rest_command` with the new value
2. The command sends `PATCH /api/v1/circuits/{circuit_id}/setpoints` with a JSON body (e.g. `{"roomOT1": 21.0}`)
3. The API validates the value against device limits and writes it to the HPM
4. On the next `scan_interval` poll, the sensor updates and the number entity reflects the confirmed value

If the value is outside the device's accepted range, the API returns 422 and the entity
state remains at the previous value.

---

## Reloading configuration

After adding any of the above to `configuration.yaml`, reload the affected integrations
in **Settings → System → YAML configuration reloading**, or restart HA.
