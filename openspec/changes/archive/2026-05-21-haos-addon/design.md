## Context

The FastAPI service is fully functional and already structured as an HAOS add-on (`config.yaml`, `Dockerfile`, `run.sh` are all present). What's missing is the surrounding packaging that lets the HA Supervisor discover, install, and display the add-on: a `repository.json` at the repo root, several required `config.yaml` fields, user-facing documentation (`DOCS.md`), and a version changelog. Additionally, nothing maps the API's JSON responses to actual HA entities — that link is provided by `configuration.yaml` snippets using HA's built-in `rest`, `number`, and `template` integrations.

## Goals / Non-Goals

**Goals:**
- Make the add-on installable via the HA Supervisor add-on store by adding the GitHub repo URL
- Fix `config.yaml` to pass Supervisor validation
- Give users copy-paste HA configuration to expose all API data as HA entities
- Preserve standalone operation (env-var Docker run, local Python)

**Non-Goals:**
- Publishing a pre-built Docker image to a container registry (local build is sufficient for a personal add-on)
- HAOS ingress support (ingress is for embedded web UIs; this is a backend API called over `localhost`)
- A native HA custom component (`custom_components/`) — out of scope for this change
- HA long-lived access token auth on the API (no API key currently; the API is trusted on the local network)

## Decisions

### 1. Repository layout: subdirectory add-on, not root-level

**Decision:** Keep the current `heatpump-api/` subdirectory layout. Add `repository.json` at the repo root.

A valid HAOS add-on repository has `repository.json` at the root and one subdirectory per add-on, each containing its own `config.yaml`. The current layout already matches this. No restructuring needed.

**Alternative considered:** Flatten so `config.yaml` lives at repo root (single-add-on root layout). Rejected — it would force moving all app code to root level, mixing application files with repo metadata.

### 2. Local Docker build, no pre-built image

**Decision:** Omit the `image:` field in `config.yaml`. The Supervisor will build from the local `Dockerfile` on install.

Pre-built images require a CI/CD pipeline publishing to `ghcr.io` on every release. For a personal add-on with infrequent releases, the build-on-install approach is simpler and has no external dependency.

**Trade-off:** First install takes ~60–90 seconds to build on a Raspberry Pi 4 instead of pulling a pre-built image (~10 seconds). Acceptable for a personal add-on.

### 3. Direct port access, no ingress

**Decision:** Keep `ports: {8765/tcp: 8765}` and do not add `ingress: true`.

Ingress is designed for add-ons that serve a web UI embedded in the HA sidebar. The heatpump API is a JSON REST endpoint called programmatically by HA's `rest` integration. Ingress would add a path-prefix proxy layer with no benefit and would require HA long-lived access token authentication to call the API from outside HA, complicating the `rest` sensor config.

On HAOS the add-on container's published port is reachable from HA's own config at `http://localhost:8765` (both share the host network stack).

### 4. HA entity config via built-in REST integrations, documented in `docs/ha-integration.md`

**Decision:** Document `configuration.yaml` snippets using HA's built-in `rest`, `number`, and `template` platforms. No custom component.

HA's `rest` sensor platform can poll `GET /api/v1/status` and extract fields via `value_template`. The `number` platform's `rest` variant can read and write individual HC1/HC2 setpoints against `GET/PATCH /api/v1/circuits/{circuit_id}/setpoints`. This covers all current API endpoints without any new code.

**Alternative considered:** A `custom_components/heatpump/` integration providing proper `climate` and `sensor` entities. Rejected for this change — it requires significantly more code, a separate release/installation step, and adds a maintenance surface. Can be a follow-up change.

**URL for HA config:** `http://localhost:8765` — works reliably on HAOS where both HA and the add-on share the host network. Document as the default with a note to substitute the host IP for non-HAOS setups.

### 5. `config.yaml` required fields to add

The following fields are missing or need correction:
- `url`: GitHub repo URL (shown in Supervisor UI; currently `""`)
- `homeassistant`: minimum HA version (set to `"2024.1.0"` — conservative lower bound)
- `image`: intentionally omitted (local build)
- `map`: add `config:r` so the add-on can read `/data/options.json` (already works in practice but should be explicit)
- Remove `host` from `options`/`schema` — the bind host is an internal concern, not a user-facing option; hardcode `0.0.0.0` in the app

## Risks / Trade-offs

**Build time on Raspberry Pi** → First install is slow (~60–90s). Mitigated by clear DOCS.md note so users don't think it's hanging.

**`rest` sensor polling interval** → HA polls on a fixed `scan_interval`. If set too short, it could saturate the single HPM session. Recommend 30s minimum in the docs.

**No authentication on the API** → Port 8765 is accessible to any host on the local network. Acceptable for a home network; documented as a known limitation. Future change could add token auth.

**HA `number` platform REST write** → The `number` platform's `set_value` action issues a `PATCH` but requires the payload to be constructed as a JSON body. This works with HA's `payload` template but the configuration is verbose. Document clearly with working examples.

## Migration Plan

1. Add `repository.json` and update `config.yaml` — no effect on existing running instances
2. Add `DOCS.md`, `CHANGELOG.md`, assets — documentation only
3. Add `docs/ha-integration.md` — additive
4. Users who want HA entities: manually add the REST sensor/number snippets to their `configuration.yaml` and restart HA

No breaking changes. Existing Docker/env-var deployments are unaffected.

## Open Questions

- Icon and logo: use a generic heatpump/radiator icon (e.g. from MDI) or create a custom one? Placeholder acceptable for first release.

**Resolved:**
- HA `number` config covers all 12 setpoints (HC1 + HC2 × roomOT1–4, roomNO, roomSNOT).
