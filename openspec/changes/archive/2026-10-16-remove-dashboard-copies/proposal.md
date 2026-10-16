## Why

`homeassistant/grafana/` holds hand-synced copies of two live Grafana dashboards, Heat Pump and Sigenergy, and the `heatpump-dashboard` spec requires the first to match live. Every edit made in Grafana therefore needs a manual re-export here, and a reorganisation of all the home dashboards on 2026-10-16 (folders, Swedish titles, new rows and panels) left both copies out of date at once.

The copy is also redundant. ha-config already snapshots every live dashboard nightly to `config/grafana/<uid>.json`, with full git history and no manual step, so it is the complete record. The Sigenergy dashboard never belonged in this repo, which is about the heat pump, and the repo is public.

## What Changes

- **BREAKING** for importers: delete `homeassistant/grafana/heatpump-dashboard.json` and `homeassistant/grafana/sigenergy-dashboard.json`. The repo no longer ships a dashboard.
- Remove the `heatpump-dashboard` capability. Its query behaviours stay on the live dashboard and are documented in ha-config's `GRAFANA.md`.
- `CLAUDE.md`: say where the live dashboards and their record are, instead of pointing at `homeassistant/grafana/`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `heatpump-dashboard`: removed. Every requirement is retired.

## Impact

- **Files**: `homeassistant/grafana/` removed; `CLAUDE.md`; `openspec/specs/heatpump-dashboard/` removed on archive.
- **Live instance**: none. Grafana keeps its dashboards in its own database; nothing reads these files.
- **API and add-on**: unchanged.
