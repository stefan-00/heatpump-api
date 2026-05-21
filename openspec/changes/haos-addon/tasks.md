## 1. Repository metadata

- [x] 1.1 Create `repository.json` at repo root with `name: "Heatpump API"`, `url` (GitHub repo URL), and `maintainer` fields

## 2. config.yaml

- [x] 2.1 Set `url` in `config.yaml` to the GitHub repository URL (currently empty string)
- [x] 2.2 Add `homeassistant: "2024.1.0"` minimum version field to `config.yaml`
- [x] 2.3 Read `app/config.py` — confirm `host` setting exists; remove it from `config.py` and hardcode `host="0.0.0.0"` in `app/main.py` so it is no longer a user-facing option

## 3. DOCS.md

- [x] 3.1 Create `heatpump-api/DOCS.md` with: prerequisites (device URL and access code required), description of each config option (`heatpump_url`, `username`, `password`, `port`), a note that first install takes ~60–90 s to build on Raspberry Pi 4, and a pointer to `docs/ha-integration.md` for setting up HA entities

## 4. CHANGELOG.md

- [x] 4.1 Create `heatpump-api/CHANGELOG.md` with a `## 0.1.0` entry listing: system status endpoint (`GET /api/v1/status`), HC1/HC2 setpoint read endpoint (`GET /api/v1/circuits/{id}/setpoints`), HC1/HC2 setpoint write endpoint (`PATCH /api/v1/circuits/{id}/setpoints`)

## 5. Image assets

- [x] 5.1 Add `heatpump-api/icon.png` — 256×256 px PNG (heatpump/radiator icon or simple placeholder)
- [x] 5.2 Add `heatpump-api/logo.png` — 250×100 px PNG

## 6. HA integration guide

- [x] 6.1 Create `docs/ha-integration.md` with introduction, base URL guidance (`http://localhost:8765` for HAOS, substitute IP for standalone), and minimum `scan_interval: 30` recommendation
- [x] 6.2 Add `rest` sensor platform config to `docs/ha-integration.md` for all 14 fields from `GET /api/v1/status`: `operating_mode`, `outdoor_temp`, `heat_pump.*` (6 fields), `heating_circuit_1.*` (4 fields), `domestic_hot_water.*` (2 fields) — include `unit_of_measurement` and `device_class` where applicable
- [x] 6.3 Add `rest` sensor platform config for reading HC1 and HC2 setpoints from `GET /api/v1/circuits/{circuit_id}/setpoints` (one `rest` resource per circuit returning all 6 values, individual sensors via `value_template`)
- [x] 6.4 Add `rest_command` entries to `docs/ha-integration.md` for writing each of the 12 setpoints (one command per field, using `PATCH /api/v1/circuits/{circuit_id}/setpoints` with a JSON payload containing the single field)
- [x] 6.5 Add `template` `number` entity config for all 6 HC1 setpoints: each reads state from the corresponding REST sensor, calls the appropriate `rest_command` on `set_value`, and sets `min: 2`, `max: 50`, `step: 0.5`, `unit_of_measurement: "°C"`
- [x] 6.6 Add `template` `number` entity config for all 6 HC2 setpoints (same pattern as HC1)

## 7. Verification

- [x] 7.1 Add the GitHub repository URL in the HA Supervisor → confirm `Heatpump API` appears as an available add-on
- [x] 7.2 Install and start the add-on via Supervisor → confirm `GET /health` returns `{"status": "ok"}` and `GET /api/v1/status` returns valid data
- [x] 7.3 Apply the status sensor config from `docs/ha-integration.md` in HA and reload → confirm all 14 sensor entities appear with correct values
- [ ] 7.4 Apply the HC1 and HC2 number entity config and reload → confirm all 12 setpoint number entities show correct current values
- [ ] 7.5 Change one number entity value in HA UI → confirm API returns 200, device reflects the change, entity updates; restore original value
