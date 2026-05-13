## Why

The heatpump has no official API — only a browser-based web UI. Automating it from Home Assistant requires a proxy service that reverse-engineers the web UI's HTTP traffic and exposes the controls as a clean REST API.

## What Changes

- Introduce a new Python service (`heatpump-api`) packaged as a Home Assistant add-on (Docker container managed by HA Supervisor)
- The service authenticates with the heatpump web UI and maintains a session
- Incoming REST API requests are translated into the equivalent web UI HTTP calls and results returned as JSON
- The service handles session expiry and re-authentication transparently
- Configuration (heatpump URL, credentials, service port) is managed via the HA add-on options UI

## Capabilities

### New Capabilities

- `session-management`: Authenticates with the heatpump web UI, manages cookies/session tokens, and transparently re-authenticates when sessions expire
- `heatpump-control`: Core domain model — reading current state (temperature, mode, fan speed, etc.) and issuing control commands by proxying the web UI's HTTP calls
- `rest-api`: Public-facing HTTP API that exposes heatpump state and controls as RESTful endpoints, suitable for consumption by Home Assistant or other clients

### Modified Capabilities

*(none — this is a greenfield project)*

## Impact

- **Language/runtime:** Python 3.11+ (pinned in Dockerfile; independent of host OS Python)
- **Target platform:** Home Assistant OS (HAOS) on Raspberry Pi; also runnable locally via Docker for development
- **Dependencies:** FastAPI (REST framework), httpx (async HTTP client for proxying), Pydantic (config and models)
- **Deployment:** HA add-on — includes `config.yaml` (add-on manifest), `Dockerfile`, and `run.sh` entrypoint; installable and configurable from the HA Supervisor UI
- **Home Assistant integration:** To be decided — REST API is designed to be consumed by HA's built-in RESTful integration, a custom integration, or MQTT bridge; the API surface should not assume a specific HA integration style
