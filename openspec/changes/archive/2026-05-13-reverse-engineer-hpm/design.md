## Context

The HPM-800B7F is a **whole-house heating system controller**, not an air conditioner. The foundation change built an API skeleton assuming an AC-style device (heat/cool/dry/fan modes, single temperature setpoint). Live reverse-engineering revealed the actual system manages multiple zones over a session-based HTML web UI.

**Actual system structure:**
- Heat pump 1 — compressor, outlet/inlet water temps, frequency, error codes
- Heating circuit 1 (HC1) — underfloor/radiator circuit, room setpoints, flow temp
- Heating circuit 2 (HC2) — second zone, same structure as HC1
- Domestic hot water (DHW) — tank temperature and setpoints
- Buffer tank — intermediate storage, actual and setpoint temps

**Discovered protocol (HPM WEB-RC):**
- Session: `GET /` → extract `sessionid` from 302 → `POST /getlogin.rsp` (fields: `user`, `code`, `sessionid`)
- All requests pass `sessionid` as a URL query parameter — no cookies used
- Read: `GET /v21.rsp`, `/v30.rsp`, `/v3.rsp`, `/v107000.rsp`, `/v100100.rsp` return HTML with embedded values
- Individual param read: `GET /vinfo.rsp?sessionid=X&id=N:P` returns value, limits, read/write flag
- Write: `POST /execgrset.rsp` (fields: `sessionid`, `id`, `val`, `pv`, `Set=OK`)
- Mode switch: `POST /ms.rsp` (fields: `sessionid`, `MS0=0..5`)

## Goals / Non-Goals

**Goals:**
- Replace the TODO stubs in `session.py` with the real HPM login flow
- Replace `HeatpumpState` with a model that matches the actual HPM system structure
- Implement `GET /api/v1/status` returning live data parsed from the HPM view pages
- Identify and document the write path (`execgrset.rsp`) ready for a future control change
- Update `session.py` to pass `sessionid` as a URL param on every proxied request

**Non-Goals:**
- Control endpoints (writes via `execgrset.rsp` or `ms.rsp`) — deferred to the next change
- Exposing all HPM parameters — status covers the operationally useful subset
- Heating circuit 2 in the first version — HC1 + HP1 + DHW is sufficient to start

## Decisions

### 1. Parse view page HTML, not individual `vinfo.rsp` calls

**Decision:** Fetch a small set of view pages (`v21.rsp`, `v30.rsp`, `v107000.rsp`) and extract values via regex on the parameter anchor `href` ID.

**Pattern:** Each data point appears in the HTML as:
```html
<a class="infolink" href="vinfo.rsp?sessionid=X&id=111:6.6.6"> 23 °C</a>
```
Parse with: `id=111:[^"]+">([^<]+)<` — match by numeric ID prefix.

**Alternative considered:** Call `vinfo.rsp` per parameter. Cleaner per-value response, but requires N round-trips (one per field). The view pages batch all subsystem values in one request.

**Why view pages:** Three HTTP requests replace fifteen-plus individual calls. The embedded format is consistent and parseable without a full HTML parser.

### 2. Replace `HeatpumpState` with a multi-subsystem model

**Decision:** Replace the single flat `HeatpumpState` model with nested Pydantic models:

```python
class HeatPumpUnit(BaseModel):
    on: bool                     # OP-OFF/ON (id 114)
    heating: bool                # OP-HEAT (id 115)
    outlet_temp: float           # HP outlet water °C (id 111)
    return_temp: float           # HP return water °C (id 112)
    frequency: int               # Compressor Hz (id 126)
    error_code: str              # Error code string (id 125)

class HeatingCircuit(BaseModel):
    flow_setpoint: float         # SP-Flow °C (id 12/26)
    flow_temp: float             # Actual flow °C (id 13/27)
    room_setpoint: float         # Room setpoint Normal °C (id 18/32)
    pump_on: bool                # Pump status (id 15/29)

class DomesticHotWater(BaseModel):
    setpoint: float              # SP-DHWta °C (id 37)
    actual_temp: float           # Actual tank °C (id 38)

class SystemStatus(BaseModel):
    operating_mode: str          # off/auto/summer/vacation/nominalOp/manual
    outdoor_temp: float          # Outdoor °C (id 9 from HC1)
    heat_pump: HeatPumpUnit
    heating_circuit_1: HeatingCircuit
    domestic_hot_water: DomesticHotWater
```

**Why:** The original `HeatpumpState` modelled an air conditioner. The HPM manages independent subsystems — any flat model would either omit information or misrepresent the structure.

### 3. Session passed as URL query parameter

**Decision:** In `session.py`, store the `sessionid` string and append `?sessionid=XXX` (or `&sessionid=XXX`) to every request URL before passing to `httpx`.

**Alternative considered:** Use cookies via httpx cookie jar. Not applicable — the HPM does not set any `Set-Cookie` headers; the session token is only in the URL.

**Implementation:** `SessionManager` stores `self._session_id: str`. The `request()` method appends it as a query param using `httpx`'s `params=` argument. On re-auth, `login()` extracts the new sessionid from the 302 Location header.

### 4. Operating mode parsed from `v0.rsp` `<select>` element

**Decision:** Fetch `v0.rsp` and find the `<option ... selected>LABEL</option>` inside the `MS0Select` form to get the current operating mode string.

**Why `v0.rsp`:** It is the only page that renders the mode selector with a `selected` attribute on the active option. Other pages do not show the mode switch.

### 5. Value parsing strategy for HPM HTML

Values in the HTML are formatted strings like `" 23 °C"`, `"on "`, `"nom. oper.         "`. Strip whitespace, then either:
- Extract the numeric part with regex `[-\d.]+` for temperature/numeric fields
- Use the stripped string directly for enum/status fields

The `°C` character uses ISO-8859-1 encoding (`\xb0`). The httpx client must request with `Accept-Charset: ISO-8859-1` or decode the bytes with `latin-1` before parsing.

## Risks / Trade-offs

**[HTML parsing fragility]** → The HPM firmware may render slightly different HTML on different firmware versions or with different session states. Mitigation: match by numeric parameter ID in the href (e.g. `id=111:`), not by position or CSS class. Log raw HTML on parse failure so mismatches are diagnosable.

**[Session lifetime unknown]** → It is unknown how long a session stays valid without activity. The existing re-auth on 401 logic handles this generically. The HPM may also invalidate a session when another client logs in. Mitigation: the generation-counter pattern in `session.py` already handles concurrent re-auth correctly.

**[Single-user session model]** → The HPM supports only one active session. If a human is using the web UI while the API service is running, sessions will conflict. Mitigation: document this limitation; the existing re-login logic will recover automatically.

**[Encoding]** → HPM serves ISO-8859-1. Python's `httpx` will default to UTF-8 for response text. Mitigation: always decode response bytes with `latin-1` (`response.content.decode("latin-1")`).

## Migration Plan

1. Update `session.py`: implement the two-step login (GET / → extract sessionid, POST /getlogin.rsp), store sessionid, inject as URL param on all requests
2. Replace `models.py`: swap `HeatpumpState`/`ControlCommand` for the new multi-subsystem models
3. Implement HTML parsers in `client.py`: one function per view page
4. Wire `get_status()` to fetch the three view pages and return a `SystemStatus`
5. Update `GET /api/v1/status` router to use `SystemStatus` response model
6. Remove the provisional AC-style control endpoints (power/mode/temperature/fan-speed) — they are wrong for this device; control endpoints will be re-added in the next change

## Open Questions

- **HC2 inclusion:** Heating circuit 2 exists (v3.rsp) but is not included in the first status model. Add it once HC1 is validated.
- **Buffer tank:** Not included in initial status. Add if useful for HA automations.
- **Write value confirmation:** Does `execgrset.rsp` return the new value in the response, or does it redirect back to the view page? This needs to be verified before implementing control endpoints (next change).
