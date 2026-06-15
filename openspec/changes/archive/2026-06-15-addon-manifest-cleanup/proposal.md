## Why

The Supervisor logs two warnings when reading the add-on repository: the `config.yaml` `arch` list uses the deprecated value `armv7`, and the Supervisor's recursive `config.yaml` scan finds `openspec/config.yaml` and rejects it as an invalid app config. Neither breaks the add-on (0.1.3 installs correctly), but the `armv7` deprecation is a real cleanup and the scan collision should be documented as expected behaviour so it isn't mistaken for a fault.

## What Changes

- Remove the deprecated `armv7` value from the add-on `config.yaml` `arch` list (keeping `aarch64` and `amd64`, which match the target hardware).
- Bump the add-on version so the Supervisor offers the manifest update.
- Document that the Supervisor recursively scans the repository for `config.yaml` and will log a benign "Invalid app config" warning for `openspec/config.yaml` (OpenSpec's required config path) — this is expected while the add-on and OpenSpec tooling share one repository, and has no functional impact.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `haos-addon-packaging`: tighten the `arch` field to currently-supported values only (drop deprecated `armv7`), and add a requirement documenting that non-add-on `config.yaml` files in the repository are expected and do not affect add-on discovery.

## Impact

- **Code:** `heatpump-api/config.yaml` (`arch` list, version bump), `heatpump-api/CHANGELOG.md`.
- **No behaviour change** for the running add-on; `armv7` was not a deployment target. No new dependencies.
