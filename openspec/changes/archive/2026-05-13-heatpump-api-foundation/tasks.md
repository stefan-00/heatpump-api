## 1. Project Scaffolding

- [x] 1.1 Create top-level `heatpump-api/` directory with subdirectories `app/` and `app/routers/`
- [x] 1.2 Create `requirements.txt` with pinned versions: `fastapi`, `uvicorn[standard]`, `httpx`, `pydantic`
- [x] 1.3 Create `Dockerfile` using `python:3.11-slim`, installing requirements, copying app, and exposing port 8765
- [x] 1.4 Create `run.sh` entrypoint that launches `uvicorn app.main:app` with host/port from environment
- [x] 1.5 Create empty `app/__init__.py` and `app/routers/__init__.py`

## 2. Configuration

- [x] 2.1 Create `app/config.py` with a Pydantic `Settings` model covering: `heatpump_url`, `username`, `password`, `port` (default 8765), `host` (default `0.0.0.0`)
- [x] 2.2 Implement config loading: read `/data/options.json` if it exists, otherwise fall back to environment variables
- [x] 2.3 Verify that a missing required field (e.g. no `heatpump_url`) raises a clear validation error at startup

## 3. Data Models

- [x] 3.1 Create `app/models.py` with a `HeatpumpState` Pydantic model (fields: `power`, `mode`, `current_temp`, `target_temp`, `fan_speed`)
- [x] 3.2 Add a `ControlCommand` model for inbound control requests (command name + value)
- [x] 3.3 Add a standard `ErrorResponse` model (`detail: str`) used by all non-2xx responses

## 4. Session Management

- [x] 4.1 Create `app/session.py` with a `SessionManager` class that holds an `httpx.AsyncClient` and an `asyncio.Lock`
- [x] 4.2 Implement `login()` method that posts credentials to the web UI and stores the resulting cookies/token (leave the actual URL and payload as `TODO` placeholders until the UI is reverse-engineered)
- [x] 4.3 Implement `request()` method that executes a proxied call; on 401/session-expired response, acquires the lock, re-authenticates once, and retries
- [x] 4.4 Ensure concurrent callers wait on the lock during re-authentication rather than each sending a separate login request
- [x] 4.5 Raise a descriptive `StartupError` if the initial login fails due to bad credentials

## 5. Heatpump Client

- [x] 5.1 Create `app/client.py` with a `HeatpumpClient` class that accepts a `SessionManager`
- [x] 5.2 Implement `get_status() -> HeatpumpState` (leave URL and response-parsing as `TODO` placeholder)
- [x] 5.3 Implement `send_command(command: str, value: Any) -> dict` (leave URL and payload as `TODO` placeholder)
- [x] 5.4 Wrap upstream network errors in a `502` `HTTPException` with a `detail` message
- [x] 5.5 Wrap unparseable upstream responses in a `502` `HTTPException` and log the raw response body

## 6. REST API

- [x] 6.1 Create `app/main.py` with the FastAPI app instance; wire up lifespan to call `session_manager.login()` on startup
- [x] 6.2 Create `app/routers/status.py` with `GET /api/v1/status` calling `client.get_status()`
- [x] 6.3 Create `app/routers/control.py` with `POST /api/v1/control/power`, `/mode`, `/temperature`, `/fan-speed` — each validates its input and calls `client.send_command()`
- [x] 6.4 Add `GET /health` directly in `main.py` returning `{"status": "ok"}`
- [x] 6.5 Register a global exception handler that ensures all unhandled errors return `{"detail": "..."}` JSON (not HTML)
- [x] 6.6 Include both routers in the app and verify `/docs` and `/openapi.json` are reachable

## 7. HA Add-on Packaging

- [x] 7.1 Create `config.yaml` HA add-on manifest with `name`, `version`, `slug`, `description`, `arch` list, `startup: application`, and `boot: auto`
- [x] 7.2 Define the `options` and `schema` sections in `config.yaml` for all config fields: `heatpump_url` (str), `username` (str), `password` (str), `port` (int, optional)
- [x] 7.3 Verify `run.sh` maps `/data/options.json` fields to the env vars expected by `config.py`

## 8. Documentation

- [x] 8.1 Update `CLAUDE.md` with the project overview, directory layout, and local dev commands (`docker build`, `docker run`, `uvicorn` with env vars)
