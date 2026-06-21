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
the API's own session management. The status resource polls every **30 s**; the two
setpoint resources poll every **60 s**, since setpoints are writable configuration values
that change rarely and their reads traverse the slower WEB-RC navigation path.

## Fetch timeouts

Setpoint reads and writes navigate the device's stateful WEB-RC pages, serialized on a
single session, so they can take longer than HA's **default 10-second** fetch timeout.
The package sets an explicit `timeout: 30` on every `rest` resource and every
`rest_command` so slow-but-successful operations complete within one call instead of
raising *"Timeout when calling resource"*. This is comfortably above the API's own
per-request budget (default 15 s, the `request_timeout` add-on option). Note that the
`timeout` on a `rest` resource covers reads only — write commands need their own
`timeout` under `rest_command`.

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
heatpump_status_url:        "http://<ha-host-ip>:8765/api/v1/status"
heatpump_hc1_sp_url:        "http://<ha-host-ip>:8765/api/v1/circuits/hc1/setpoints"
heatpump_hc2_sp_url:        "http://<ha-host-ip>:8765/api/v1/circuits/hc2/setpoints"
heatpump_hc2_flowlimit_url: "http://<ha-host-ip>:8765/api/v1/circuits/hc2/flow-limit"
```

Replace `<ha-host-ip>` with your HA host's LAN IP.

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

> **Resilience to API errors:** if the API returns an error body (e.g. a `502` with
> `{"detail": ...}` when the heatpump is briefly unreachable), an empty/non-JSON body, or
> nothing at all (a fetch timeout), every sensor goes **unavailable** rather than logging
> template errors. Each `availability` template first guards `value_json is defined`
> before testing its key — otherwise, when a poll times out and `value_json` is undefined,
> rendering the availability template itself raises *"UndefinedError: 'value_json' is
> undefined"*. Each `value_template` additionally short-circuits when its key is missing.
> A transient upstream error therefore produces no log spam and the entities recover on
> the next successful poll.

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

> **Availability:** each number entity guards its state with
> `availability: "{{ has_value('sensor.<backing_sensor>') }}"`, so when the backing
> setpoint sensor is `unavailable` (e.g. its poll timed out) the slider goes
> **unavailable** instead of logging *"invalid number state: unavailable"*.

### Pool flow-limit control (HC2)

HC2 (pool heating) is weather-compensated, so at high outdoor temperatures the heating
curve collapses the flow setpoint and the pool stops heating. The device's *setpoint
limitation* function fixes this: a `minFl` floor forces the effective flow setpoint to
`max(curve, minFl)`, independent of the outdoor temperature.

The API exposes this as a **single knob**:

- `GET /api/v1/circuits/hc2/flow-limit` → `{ "active": bool, "min_flow": float, "max_flow": float }`
- `PATCH /api/v1/circuits/hc2/flow-limit` accepts an optional `flow_setpoint` and/or an
  optional `active` (at least one required):
  - `{ "flow_setpoint": 30 }` → sets `minFl = 30`, ensures `maxFl > minFl` (the device rejects
    `maxFl <= minFl`; `maxFl` is raised to the 65 °C cap when needed), and enables the limit
    (`active = 1`) — one call sets the floor *and* turns it on, no separate toggle.
  - `{ "active": false }` → disables the limitation without changing the floor.
  - `{ "active": true }` → enables it with the current floor.

Values are validated against the device range (2–160 °C) and the `maxFl > minFl` constraint;
an invalid or empty body returns 422 and writes nothing. The endpoint is **HC2-only** (HC1 → 400).

This is wired into `packages/heatpump.yaml` (requires the `heatpump_hc2_flowlimit_url` secret).
It polls `/api/v1/circuits/hc2/flow-limit` every 300 s (the limit changes rarely) and provides:

- **`number.hc2_pool_flow_setpoint`** — the slider for the pool flow floor. Its state reflects
  the confirmed `min_flow`; setting it sends `PATCH {"flow_setpoint": <value>}`, which writes
  `min_flow` and enables the limit in one call.
- **`switch.hc2_flow_limit`** — enable/disable the limitation (`PATCH {"active": …}`), state
  backed by `binary_sensor.hc2_flow_limit_active`.
- **`sensor.hc2_flow_limit_min`** / **`sensor.hc2_flow_limit_max`** — current `min_flow`/`max_flow`.
- **`binary_sensor.hc2_flow_limit_active`** — whether the device limitation is currently enabled.

Like the other writable controls, the slider is a template `number` backed by the GET sensor
(so it shows the device-confirmed value) rather than a standalone `input_number` helper.

---

## Package structure (abbreviated)

```yaml
# packages/heatpump.yaml

rest:
  - resource: !secret heatpump_status_url   # 14 status sensors
    scan_interval: 30
    timeout: 30
    sensor:
      # operating mode, outdoor temp, heat pump stats, HC1, DHW ...
      # each: availability: "{{ value_json is defined and 'heat_pump' in value_json }}"

  - resource: !secret heatpump_hc1_sp_url   # 6 HC1 setpoint sensors
    scan_interval: 60
    timeout: 30
    sensor:
      # roomOT1, roomOT2, roomOT3, roomOT4, roomNO, roomSNOT ...

  - resource: !secret heatpump_hc2_sp_url   # 6 HC2 setpoint sensors
    scan_interval: 60
    timeout: 30
    sensor:
      # roomOT1, roomOT2, roomOT3, roomOT4, roomNO, roomSNOT ...

rest_command:                                # 12 commands total (6 × HC1, 6 × HC2)
  heatpump_set_hc1_roomot1:
    url: !secret heatpump_hc1_sp_url
    method: PATCH
    content_type: application/json
    timeout: 30
    payload: '{"roomOT1": {{ value }}}'
  # heatpump_set_hc1_roomot2 ... heatpump_set_hc2_roomsnot ...

template:
  - number:                                  # 12 slider entities (6 × HC1, 6 × HC2)
      - name: "HC1 Room OT1"
        availability: "{{ has_value('sensor.hc1_setpoint_roomot1') }}"
        state: "{{ states('sensor.hc1_setpoint_roomot1') }}"
        set_value:
          action: rest_command.heatpump_set_hc1_roomot1
          data:
            value: "{{ value }}"
      # HC1 Room OT2 ... HC2 Room Standby ...
```
