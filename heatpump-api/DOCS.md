# Heatpump API

REST API proxy for the Panasonic HPM-800B7F WEB-RC whole-house heating controller.
Exposes the device's browser-based web UI as a JSON REST API so Home Assistant automations
and dashboards can read and control the system.

## Prerequisites

- The HPM-800B7F controller must be reachable on your local network
- You need the device's IP address or hostname
- You need the HPM access code (up to 8 characters; the "service" code, not the user PIN)

## Configuration

| Option | Required | Description |
|---|---|---|
| `heatpump_url` | Yes | Full URL of the HPM web UI, e.g. `http://192.168.1.x` |
| `username` | Yes | HPM login username (typically `service`) |
| `password` | Yes | HPM access code (up to 8 characters) |
| `port` | No | Port the API listens on inside the add-on (default: `8765`) |

> **Note:** The HPM access code is entered on the device's web UI login page as "access code".
> It is not the same as a Wi-Fi or router password.

## First install

The add-on is built from source on your device on first install.
On a **Raspberry Pi 4** this takes approximately **60–90 seconds** — the progress bar may appear
stuck during this time. This is normal; the add-on will start once the build completes.
Subsequent restarts use the cached image and are fast.

## API endpoints

Once running, the API is available at `http://<your-ha-ip>:8765` from any device
on your local network, including from HA's own `configuration.yaml`.

> **Note:** Use your HA host's LAN IP address — `localhost` does not work from within
> HA's configuration on HAOS because HA and add-ons run in separate containers.

| Endpoint | Description |
|---|---|
| `GET /health` | Health check — returns `{"status": "ok"}` |
| `GET /api/v1/status` | Full system status (temperatures, modes, pump state) |
| `GET /api/v1/circuits/{hc1\|hc2}/setpoints` | Read all 6 temperature setpoints for a circuit |
| `PATCH /api/v1/circuits/{hc1\|hc2}/setpoints` | Update one or more setpoints for a circuit |

Interactive API docs (Swagger UI) are available at `http://<your-ha-ip>:8765/docs`.

## Setting up Home Assistant entities

To expose heatpump data as HA sensors and controls, see the integration guide:
[`docs/ha-integration.md`](https://github.com/stefan-00/heatpump-api/blob/main/docs/ha-integration.md)

This covers:
- Temperature sensors for all status fields
- Writable number entities for HC1 and HC2 setpoints
