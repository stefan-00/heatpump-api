## Context

The heatpump exposes only a browser-based web UI — no official API. Home Assistant OS (HAOS) on Raspberry Pi is the target runtime. HAOS is a locked-down OS where extensions run as Docker-based add-ons managed by HA Supervisor; there is no accessible host Python environment.

The proxy service must reverse-engineer the web UI's HTTP traffic, maintain an authenticated session, and expose a clean REST API for HA (or any local client) to consume.

## Goals / Non-Goals

**Goals:**
- Package the proxy as an installable HA add-on (HAOS-native deployment)
- Authenticate with the heatpump web UI and maintain the session transparently
- Expose heatpump state and controls via a RESTful HTTP API
- Support local development without a running HA instance (plain Docker)

**Non-Goals:**
- HA custom component / HACS integration (deferred — REST API is the foundation)
- Multi-heatpump support (single device for now)
- Authentication on the proxy API itself (assumed local network; HA controls access)
- Persisting state across proxy restarts beyond what the heatpump UI provides

## Decisions

### 1. Deployment: HA Add-on

**Decision:** Package as a Home Assistant add-on (`config.yaml` manifest + `Dockerfile`).

**Rationale:** HAOS does not expose a usable host Python environment. Add-ons are the only supported way to run custom long-lived services on HAOS. They integrate with HA Supervisor (start/stop/restart, log viewer, options UI) and run in isolated Docker containers.

**Alternative considered:** Running on a separate machine on the same network — rejected because it requires additional hardware and adds a network dependency outside the RPi.

---

### 2. Framework: FastAPI + httpx

**Decision:** FastAPI for the REST server; httpx (async) as the HTTP client for proxying.

**Rationale:** FastAPI is async-native, which means the proxy can hold a connection from HA while awaiting a response from the heatpump web UI without blocking. httpx has an async API that pairs directly with FastAPI's async handlers. Pydantic (already a FastAPI dependency) handles config validation and response models.

**Alternative considered:** Flask + requests — synchronous stack is simpler but would block the event loop on every proxied call, limiting throughput unnecessarily.

---

### 3. Session management: in-memory, re-auth on expiry

**Decision:** Store the heatpump web UI session (cookies/token) in memory. On any proxied request that receives a 401 or session-expired response, automatically re-authenticate and retry once.

**Rationale:** Persisting session state to disk adds complexity with little benefit — the credentials are already in the add-on config and re-login is cheap. An in-memory session is simpler and survives normal operation; only a container restart requires a fresh login, which is handled automatically.

**Alternative considered:** Proactive session refresh on a timer — requires knowing the session TTL, which is unknown until the UI is reverse-engineered; reactive re-auth is safer as a default.

---

### 4. Configuration: HA add-on options → environment variables

**Decision:** Define all user-facing config (heatpump URL, username, password, listen port) in the add-on `config.yaml` schema. HA Supervisor writes chosen values to `/data/options.json` at startup; the app reads that file (standard HA add-on convention).

**Rationale:** This gives users a UI form in HA to configure the add-on without editing files. `/data/options.json` is the HA-standard config delivery mechanism for add-ons.

---

### 5. Project layout

```
heatpump-api/
  config.yaml          # HA add-on manifest
  Dockerfile
  run.sh               # container entrypoint
  app/
    main.py            # FastAPI app + startup
    config.py          # reads /data/options.json
    session.py         # web UI auth + session management
    client.py          # httpx client, proxies calls to web UI
    routers/
      status.py        # GET /api/v1/status
      control.py       # POST /api/v1/control/...
    models.py          # Pydantic request/response models
```

**Rationale:** Flat enough to be navigable at this stage; routers split by read (status) vs write (control) to make the API surface clear. `session.py` and `client.py` are separated so session logic can be tested independently of routing.

## Risks / Trade-offs

- **Web UI changes break the proxy** → The heatpump vendor can update the UI at any time with no notice, silently breaking the proxy. Mitigation: structured error responses that make breakage obvious; integration tests against a recorded fixture of the UI traffic.
- **Unknown auth mechanism** → The web UI's session/cookie behavior is not yet known. Mitigation: design `session.py` behind an interface so the implementation can be swapped without touching routers or models.
- **HA add-on complexity for local dev** → Developing inside an add-on requires either a full HAOS VM or workarounds. Mitigation: the app reads `/data/options.json` but falls back to environment variables, so `uvicorn app.main:app` works locally with `ENV` vars set.

## Open Questions

- What HTTP mechanism does the heatpump web UI use for auth? (cookie session, Bearer token, basic auth?) — answered once the UI is inspected.
- Does the web UI use WebSockets or long-polling for live state updates, or plain polling? — determines whether the `status` endpoint needs to proxy a stream or just snapshot.
- What port should the add-on listen on by default? (suggestion: `8765` to avoid clashing with HA's 8123)
