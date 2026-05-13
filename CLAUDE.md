# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A reverse-engineering proxy that exposes the heatpump's browser-based web UI as a REST API, packaged as a Home Assistant add-on (HAOS). Built with Python 3.11 + FastAPI + httpx.

```
heatpump-api/          # application code
  config.yaml          # HA add-on manifest
  Dockerfile
  run.sh               # container entrypoint
  requirements.txt
  app/
    main.py            # FastAPI app, lifespan, health endpoint
    config.py          # reads /data/options.json or env vars
    session.py         # web UI auth + session management (SessionManager)
    client.py          # proxies calls to the heatpump web UI (HeatpumpClient)
    models.py          # Pydantic models: HeatpumpState, ControlCommand, ErrorResponse
    routers/
      status.py        # GET /api/v1/status
      control.py       # POST /api/v1/control/{power,mode,temperature,fan-speed}
openspec/              # spec-driven change workflow
```

## Local development

```bash
# Run with env vars (no HA required)
cd heatpump-api
HEATPUMP_URL=http://192.168.1.x HEATPUMP_USERNAME=admin HEATPUMP_PASSWORD=secret \
  python -m app.main

# Or with Docker
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

## Architecture notes

- `session.py` uses a generation counter + `asyncio.Lock` so concurrent 401s trigger only one re-login
- `client.py` stubs (`get_status`, `send_command`) contain `TODO` markers for URLs/payloads — these are filled in after reverse-engineering the web UI
- Control endpoint value ranges (e.g. temperature 16–30°C) are provisional; confirm from the web UI
- The app reads `/data/options.json` directly — `run.sh` needs no mapping logic

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
