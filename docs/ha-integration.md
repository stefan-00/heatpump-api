# Home Assistant Integration Guide

This guide shows how to expose the Heatpump API as native Home Assistant entities using
only HA's built-in integrations — no custom component required.

## Prerequisites

The Heatpump API add-on must be installed and running. Verify it with:

```
GET http://<ha-host-ip>:8765/health
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

## Setup

### Step 1 — Copy the package file

Copy [`packages/heatpump.yaml`](../packages/heatpump.yaml) from this repo into your HA
config directory as `packages/heatpump.yaml`. It contains all sensors, REST commands,
and number entities.

### Step 2 — Register the package

Add to `configuration.yaml`:

```yaml
homeassistant:
  packages:
    heatpump: !include packages/heatpump.yaml
```

### Step 3 — Add secrets

Add to `secrets.yaml` (one place to update if the IP ever changes):

```yaml
heatpump_status_url:  "http://192.168.1.x:8765/api/v1/status"
heatpump_hc1_sp_url:  "http://192.168.1.x:8765/api/v1/circuits/hc1/setpoints"
heatpump_hc2_sp_url:  "http://192.168.1.x:8765/api/v1/circuits/hc2/setpoints"
```

Replace `192.168.1.x` with your HA host's LAN IP.

### Step 4 — Restart HA

A full restart is required the first time the `packages:` key is added to
`configuration.yaml`. After that, changes to `packages/heatpump.yaml` can be applied
via **Settings → System → YAML configuration reloading**.

---

## What the package provides

### Status sensors (14 entities)

A single poll of `/api/v1/status` every 30 seconds populates:

- Operating mode, outdoor temperature
- Heat pump: on/off, heating, outlet temp, return temp, frequency, error code
- HC1: flow setpoint, flow temp, room setpoint, pump on/off
- DHW: setpoint, actual temperature

### Setpoint sensors (12 entities)

Polls `/api/v1/circuits/hc1/setpoints` and `.../hc2/setpoints` for the six writable
heating curve breakpoints per circuit. These feed the writable number entities below.

> **Note on `roomOT1`–`roomOT4`:** These are optional heating curve breakpoints. When a
> breakpoint is not configured the API returns `null`, and the sensor is marked
> **unavailable** to avoid *"state is non-numeric"* log errors. The entities reappear
> automatically when the breakpoint is re-added. `roomNO` and `roomSNOT` are always
> present.

### Writable setpoint controls (12 entities)

Number entities (sliders) for each setpoint on HC1 and HC2. When you set a value:

1. HA calls the corresponding `rest_command` with the new value
2. The command sends `PATCH /api/v1/circuits/{circuit_id}/setpoints` with a JSON body (e.g. `{"roomOT1": 21.0}`)
3. The API validates the value against device limits and writes it to the HPM
4. On the next `scan_interval` poll the sensor updates and the slider reflects the confirmed value

If the value is outside the device's accepted range, the API returns 422 and the entity
state remains at the previous value.

---

## Package structure (abbreviated)

```yaml
# packages/heatpump.yaml

rest:
  - resource: !secret heatpump_status_url   # 14 status sensors
    scan_interval: 30
    sensor:
      # operating mode, outdoor temp, heat pump stats, HC1, DHW ...

  - resource: !secret heatpump_hc1_sp_url   # 6 HC1 setpoint sensors
    scan_interval: 30
    sensor:
      # roomOT1, roomOT2, roomOT3, roomOT4, roomNO, roomSNOT ...

  - resource: !secret heatpump_hc2_sp_url   # 6 HC2 setpoint sensors
    scan_interval: 30
    sensor:
      # roomOT1, roomOT2, roomOT3, roomOT4, roomNO, roomSNOT ...

rest_command:                                # 12 commands total (6 × HC1, 6 × HC2)
  heatpump_set_hc1_roomot1:
    url: !secret heatpump_hc1_sp_url
    method: PATCH
    content_type: application/json
    payload: '{"roomOT1": {{ value }}}'
  # heatpump_set_hc1_roomot2 ... heatpump_set_hc2_roomsnot ...

template:
  - number:                                  # 12 slider entities (6 × HC1, 6 × HC2)
      - name: "HC1 Room OT1"
        state: "{{ states('sensor.hc1_setpoint_roomot1') }}"
        set_value:
          action: rest_command.heatpump_set_hc1_roomot1
          data:
            value: "{{ value }}"
      # HC1 Room OT2 ... HC2 Room Standby ...
```
