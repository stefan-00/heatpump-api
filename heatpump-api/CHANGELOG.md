# Changelog

## 0.1.15 — 2026-10-11

### Added

- `heat_pump.tank_heating`, `electric_heater`, `booster_heater` and `dhw_setpoint` in
  `GET /api/v1/status`, parsed best-effort from `v21.rsp` (ids 117, 120, 121, 110), so a
  stalled legionella disinfection run can be diagnosed. `dhw_setpoint` is the DHW target
  the HPM sends to the heat pump, reported as-is including its 2 °C no-demand placeholder;
  it is not `domestic_hot_water.setpoint`. The heater states are unverified against the
  real relays.

## 0.1.4 — 2026-06-15

### Changed

- Dropped the deprecated `armv7` architecture from the add-on manifest; the add-on
  targets `aarch64` and `amd64` only. Silences the Supervisor's deprecated-arch warning.

## 0.1.3 — 2026-06-15

### Added

- `request_timeout` add-on option (default `15`s, env var `HEATPUMP_TIMEOUT`) — the
  read/overall HTTP timeout for requests to the heatpump, replacing the silent 5s
  default that was too short for the slow embedded device. Connect timeout stays at 5s.

### Fixed

- Intermittent 502s on `/status` and setpoint reads: transient transport errors are now
  retried up to 2× with backoff before surfacing, riding out brief device stalls.
- Transport errors were logged with an empty message; they are now logged with `repr()`
  (e.g. `ReadTimeout('')`) so the failure mode is identifiable.
- Extended the `availability` + guarded `value_template` resilience to **all** HA status
  and setpoint sensors, so any error body makes sensors `unavailable` without template-error
  log spam (previously only HC1/DHW were guarded).

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
