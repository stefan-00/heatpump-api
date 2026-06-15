## Context

The Supervisor emitted two warnings while reading the `stefan-00/heatpump-api` repository: `arch` uses deprecated `armv7`, and `openspec/config.yaml` fails add-on validation (`Got {'schema': 'spec-driven'}`). The add-on still resolves correctly (`version_latest` read `0.1.3`), so both are non-blocking. Per the HA developer docs, the Supervisor **recursively** searches the repository for `config.yaml` and parses each as an add-on config, which is why OpenSpec's config file is picked up.

## Goals / Non-Goals

**Goals:**
- Remove the deprecated `armv7` arch value and ship the cleaned manifest via a version bump.
- Capture the recursive-scan behaviour in the spec so the `openspec/config.yaml` warning is recognised as expected, not a defect.

**Non-Goals:**
- Splitting the add-on into a dedicated repository or relocating OpenSpec's config — the warning is benign and a repo split would change the store URL users have already added.
- Any change to add-on runtime behaviour.

## Decisions

- **Drop `armv7`, keep `aarch64` + `amd64`.** The target hardware is 64-bit; `armv7` was never a real deployment target and is deprecated by the Supervisor. Keeping it only produces a warning.
- **Document, don't suppress, the `openspec/config.yaml` scan.** The supported way to avoid the warning is to not have a non-add-on `config.yaml` in the repo, which conflicts with OpenSpec's fixed `openspec/config.yaml` path. Since the collision has no functional impact, the spec records it as expected behaviour rather than forcing a structural change.
- **Bump the version.** A manifest-only change still needs a version bump for the Supervisor to offer the update.

## Risks / Trade-offs

- [The `openspec/config.yaml` warning persists in logs] → accepted and documented; it does not affect add-on discovery or installation (verified: `version_latest` resolved correctly to 0.1.3).
- [Dropping `armv7` removes 32-bit ARM support] → no such target is in use; the add-on is built for `aarch64`/`amd64` only.
