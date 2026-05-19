## Why

The FastAPI service exists and works but cannot be installed through the Home Assistant Supervisor — the repository lacks the metadata and documentation required by the add-on store, and `config.yaml` is missing fields the Supervisor enforces. Once the add-on is installable, users also need a way to surface its data as native HA entities so automations and dashboards can consume heatpump state.

## What Changes

- Add `repository.json` at repo root to register this as a valid HA add-on repository
- Fix and complete `config.yaml`: add `url`, `homeassistant` min version, `ingress` support, and a `host` network description
- Add `DOCS.md` to the add-on directory (displayed in the Supervisor UI)
- Add `CHANGELOG.md` with initial version entry
- Add `icon.png` and `logo.png` (Supervisor UI assets)
- Document HA REST sensor / template sensor configuration to expose heatpump data as HA entities (sensors, number inputs for setpoints)

## Capabilities

### New Capabilities

- `haos-addon-packaging`: Complete the add-on repository structure so users can add the GitHub URL in the Supervisor and install the add-on like any other. Covers `repository.json`, corrected `config.yaml`, `DOCS.md`, `CHANGELOG.md`, and image assets.
- `ha-sensor-config`: A documented, copy-paste HA configuration that exposes all API endpoints as native HA entities — `sensor` platform entries for status fields, `number` platform entries for the writable setpoints (HC1 and HC2). No custom component code; uses only HA's built-in `rest` and `template` integrations.

### Modified Capabilities

<!-- none — no existing spec requirements change -->

## Impact

- **`repository.json`** (new, repo root): add-on repository manifest
- **`heatpump-api/config.yaml`**: add missing Supervisor fields
- **`heatpump-api/DOCS.md`** (new): installation and configuration guide
- **`heatpump-api/CHANGELOG.md`** (new): version history
- **`heatpump-api/icon.png`** and **`heatpump-api/logo.png`** (new): Supervisor UI assets
- **`docs/ha-integration.md`** (new): HA `configuration.yaml` snippets for REST sensors and number entities
- No changes to application code or existing API endpoints
