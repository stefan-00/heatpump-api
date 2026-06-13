# Changelog

## 0.1.2 — 2026-06-13

### Fixed

- HA template errors logged on every 502 response: added `availability` guards to
  HC1 and DHW sensors so they go unavailable instead of failing template rendering
  when the API returns an error body.
- Network errors (unreachable heatpump) were silently swallowed; the add-on now
  logs a `WARNING` with the actual error reason before returning 502.

## 0.1.1

### Fixed

- HC2 setpoint sensors in Home Assistant showing HC1 values: concurrent HC1 and HC2
  polls from HA fired simultaneously and interfered on the HPM's stateful session.
  Replaced per-circuit locks with a single global WEB-RC navigation lock.

## 0.1.0

Initial release.

### Added

- `GET /api/v1/status` — full system status including operating mode, outdoor temperature,
  heat pump unit state (on/off, heating, outlet/return temps, compressor frequency, error code),
  heating circuit 1 (flow setpoint, flow temp, room setpoint, pump state), and
  domestic hot water (setpoint, actual temperature)
- `GET /api/v1/circuits/{circuit_id}/setpoints` — read all six temperature setpoints
  for HC1 or HC2 via the WEB-RC interface: `roomOT1`, `roomOT2`, `roomOT3`, `roomOT4`,
  `roomNO`, `roomSNOT`
- `PATCH /api/v1/circuits/{circuit_id}/setpoints` — write one or more setpoints for HC1 or HC2;
  values are validated against device-reported limits before writing
- Persistent authenticated session with automatic re-authentication on expiry
- WEB-RC session elevation (access level 3) baked into login
