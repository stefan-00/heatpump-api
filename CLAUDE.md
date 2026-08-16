# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git workflow

Solo project — commit and push directly to `main`. Do not create a feature branch or open a PR unless explicitly asked.

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
    client.py          # HPM requests: SystemStatus reads, WEB-RC setpoint reads/writes (HeatpumpClient)
    parsers.py         # parses HPM HTML view pages into Pydantic models
    models.py          # Pydantic models: SystemStatus, HeatPumpUnit, HeatingCircuit,
                       #   DomesticHotWater, ErrorResponse, HcSetpoints, HcSetpointsPatch,
                       #   FlowLimit, FlowLimitPatch
    routers/
      status.py        # GET /api/v1/status
      setpoints.py     # GET/PATCH /api/v1/circuits/{circuit_id}/setpoints
                       #   GET/PATCH /api/v1/circuits/hc2/flow-limit (HC2 only)
repository.json        # HA add-on repository manifest — must stay at the root,
                       #   alongside heatpump-api/, for Supervisor to find the add-on
homeassistant/         # artefacts deployed into the HA box (copied in by hand)
  packages/            # heatpump.yaml (sensors, numbers), influx_health.yaml (ingestion alert)
  automations/         # nightly-config-export.yaml
  node-red/            # pool-heating-flow.json
  grafana/             # dashboards
research/              # WEB-RC protocol probes — see research/README.md
docs/                  # written docs; import/ holds the source PDFs they derive from
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
- **Write (standard params)**: `POST /execgrset.rsp` with `id`, `val`, `pv`, `sessionid`; mode switch via `POST /ms.rsp` — not yet used by the API
- **Write (WEB-RC setpoints)**: after navigating to the target page, `POST /execset.rsp` with `val`, `Set=OK`, `sessionid` (in POST body), `branchnr=N`, `level=4`, `id=N`; the device returns 302 for both success and failure (same redirect URL), so range is pre-validated against `info.rsp?branchnr=N&level=4` before writing
- **Write (WEB-RC HC2 flow limitation)**: the `heatC. 2 → function → setpoint limitation` page (params `2.5.2.3.6.x`) sits one level deeper than the setpoints page, so its params use `level=5` (positions 1=`active`, 2=`minFl`, 3=`maxFl`) for both `info.rsp` range reads and `execset` writes. The device **rejects `maxFl <= minFl`**, so writes raise `maxFl` first, then `minFl`, then `active`. Backs the `flow-limit` endpoint; `minFl` floors the effective flow setpoint to `max(curve, minFl)` so HC2 (pool) heats regardless of outdoor temp
- **WEB-RC access elevation**: `GET /webfb.rsp?sessionid=SID` → `POST /getcode.rsp` with `code=4444&Set=OK&branchnr=1&level=0&sessionid=SID` (body) → follow 302 redirect as-is (do NOT append sessionid again — the redirect URL already contains it); **both `GET /webfb.rsp` and `Set=OK` are mandatory** — omitting either causes the server to return 302 but leaves the session unelevated (setpoints page shows only SP-Flow instead of all six setpoints)
- **WEB-RC navigation**: `branchnr` values in `menue.rsp` links are not stable across sessions; always navigate by matching the link label text (`heatC. 1` has a space before the digit), never by hard-coded `(branchnr, level)` pairs
- **WEB-RC write addressing is navigation-relative — verify the page before every write**: `execset.rsp` carries only `val`/`branchnr`/`level`/`id`; the device resolves that address against **whatever page the session last navigated to**, and nothing in the write identifies the circuit. HC1 and HC2 setpoints pages are BOTH `(bn=2, lv=4)`; both setpoint-limitation pages are BOTH `(bn=2, lv=5)`. A mis-navigation therefore writes silently to the wrong circuit, and the device returns 302 for both accepted and rejected writes so nothing surfaces. This corrupted live heating twice (HC1 `roomOT2` = 34.0 on 2026-08-06, HC2 `roomOT2` = 35.0 on 2026-08-02) because the flow-limit sequence `maxFl`@bn3 / `minFl`@bn2 / `active`@bn1 aliases onto `roomOT3`/`roomOT2`/`roomOT1` on a setpoints page — only `roomOT2` lands, the other two being range-rejected. Guards now in place:
  - every page's first mainpane row is a self-identifying title (`heatCirc1 setpoints`, `heatCirc2 F-SP.limit`, …); `parse_page_title` + `page_matches` verify it at the end of `_webrc_navigate`, for reads as well as writes. Field presence is NOT sufficient — HC1's limitation page has `minFl`/`maxFl` too
  - navigation-dependent requests (`menue.rsp`, `info.rsp`, `execset.rsp`) pass `retry_on_expiry=False` to `session.request`, because `login()` resets the device to root and restores no navigation, so a blind resend is misaddressed. They raise `SessionExpiredError`; `_webrc_operation` re-runs the whole navigate+act once
  - `HeatpumpClient._check_generation` re-checks `session.generation` before **each** `execset`, so a re-login mid-sequence cannot retarget the remaining writes
  - writes are read back and confirmed in the routers; label-matching navigation alone can silently land on the wrong circuit since HC1/HC2 share identical child labels
  - `_device_lock` (formerly `_webrc_lock`) serialises **every** request to the device, including the `v*.rsp` status fetches. It originally covered only WEB-RC calls, on the assumption that view pages don't touch navigation state — on 2026-08-13 a status poll interleaved between `info.rsp` and `execset` and HC2 `roomOT2` took the `minFl` value. What matters is that a request shares the session, not what kind it is
  - `_reconfirm_page` re-selects the target page at its own `(branchnr, level)` and re-checks the title immediately **before** the first `execset`. Verifying only at the end of navigation cannot protect against something disturbing the session inside the gap that follows
  - **no-op writes are skipped**: a write whose requested value already equals the stored value *cannot be verified*, because read-back passes wherever it landed. Skipping them is what makes read-back a real check for the writes that remain — and it removes almost all device traffic, since the pool controller re-asserts an unchanged floor every 10–25 s

## Architecture notes

- `session.py` uses a generation counter + `asyncio.Lock` so concurrent session-expiry responses trigger only one re-login
- `parsers.py` functions (`parse_hp1`, `parse_hc1`, `parse_dhw`, `parse_operating_mode`) each take raw latin-1 HTML and return typed Pydantic models; `extract_param(html, id)` matches by numeric param ID prefix; `parse_hc_setpoints(html)` extracts six setpoint values from the WEB-RC setpoints page using `<!-- start_mainpane -->` / `<!-- end_mainpane -->` comment markers to bound the search; `parse_flow_limit(html)` extracts `active`/`minFl`/`maxFl` from the HC2 setpoint-limitation page the same way
- `HeatpumpClient._webrc_lock` — single `asyncio.Lock` serialises ALL WEB-RC navigation/write requests across circuits; navigation re-establishes the full path from root on every call (device context is stateful — concurrent hc1/hc2 navigations on the same session interfere with each other)
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
