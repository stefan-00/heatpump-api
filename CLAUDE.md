# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A reverse-engineering proxy for a **Panasonic HPM-800B7F WEB-RC** whole-house heating controller. Exposes the device's browser-based web UI as a REST API, packaged as a Home Assistant add-on (HAOS). Built with Python 3.11 + FastAPI + httpx.

```
heatpump-api/          # application code
  config.yaml          # HA add-on manifest
  Dockerfile
  run.sh               # container entrypoint
  requirements.txt
  app/
    main.py            # FastAPI app, lifespan, health endpoint
    config.py          # reads /data/options.json or env vars
    session.py         # HPM auth + session management (SessionManager)
    client.py          # fetches HPM view pages, returns SystemStatus (HeatpumpClient)
    parsers.py         # parses HPM HTML view pages into Pydantic models
    models.py          # Pydantic models: SystemStatus, HeatPumpUnit, HeatingCircuit,
                       #   DomesticHotWater, ErrorResponse
    routers/
      status.py        # GET /api/v1/status
openspec/              # spec-driven change workflow
```

## Local development

```bash
cd heatpump-api

# First time: create venv and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Run (activate venv first, or prefix with .venv/bin/python3)
source .venv/bin/activate
HEATPUMP_URL=http://192.168.1.x HEATPUMP_USERNAME=admin HEATPUMP_PASSWORD=secret \
  python -m app.main

# Or with Docker (no venv needed)
docker build -t heatpump-api .
docker run -p 8765:8765 \
  -e HEATPUMP_URL=http://192.168.1.x \
  -e HEATPUMP_USERNAME=admin \
  -e HEATPUMP_PASSWORD=secret \
  heatpump-api
```

API docs available at `http://localhost:8765/docs` once running.

## Configuration

| Source | When used |
|---|---|
| `/data/options.json` | Running as HA add-on (written by HA Supervisor) |
| Env vars | Local dev: `HEATPUMP_URL`, `HEATPUMP_USERNAME`, `HEATPUMP_PASSWORD`, `PORT`, `HOST` |

## HPM web UI protocol

The HPM-800B7F serves classic HTML pages. There is no JSON API.

- **Login**: `GET /` → extract `sessionid` from 302 `Location` header → `POST /getlogin.rsp` with form fields `user`, `code` (the HPM name for the password, max 8 chars), `sessionid`
- **Session**: `sessionid` is appended as a URL query parameter on every request — no cookies
- **Session expiry**: detected by a 302 redirect whose `Location` contains `login.rsp`; triggers automatic re-authentication
- **Status read**: fetch `GET /v21.rsp` (HP unit), `/v30.rsp` (HC1), `/v107000.rsp` (DHW), `/v0.rsp` (system mode); decode responses as `latin-1`
- **Value parsing**: values are embedded in anchor tags — `<a href="vinfo.rsp?...&id=111:6.6.6"> 23 °C</a>`; `parsers.py` extracts by numeric param ID
- **Write** (not yet implemented): `POST /execgrset.rsp` with `id`, `val`, `pv`, `sessionid`; mode switch via `POST /ms.rsp`

## Architecture notes

- `session.py` uses a generation counter + `asyncio.Lock` so concurrent session-expiry responses trigger only one re-login
- `parsers.py` functions (`parse_hp1`, `parse_hc1`, `parse_dhw`, `parse_operating_mode`) each take raw latin-1 HTML and return typed Pydantic models; `extract_param(html, id)` matches by numeric param ID prefix
- HPM value strings use a `"LABEL   value"` format for some fields — `parse_bool` and `parse_last_token` use the **last** whitespace-separated token, not the first
- The app reads `/data/options.json` directly — `run.sh` needs no mapping logic
- `password` config key maps to the HPM `code` form field

## OpenSpec Workflow

This project uses the `spec-driven` schema for structured change management:

```
openspec/
  config.yaml       # project config
  specs/            # canonical specs (updated after changes are archived)
  changes/          # active and archived change work
```

### Key commands

```bash
openspec new change "<name>"
openspec status --change "<name>"
openspec instructions <artifact-id> --change "<name>"
```

### Slash commands

- `/opsx:new` — start a new change
- `/opsx:continue` — create the next artifact
- `/opsx:apply` — implement tasks
- `/opsx:verify` — verify implementation
- `/opsx:archive` — finalize and archive
- `/opsx:ff` — fast-forward all artifacts
- `/opsx:explore` — think through ideas first
- `/opsx:sync` — sync delta specs without archiving
