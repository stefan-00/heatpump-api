## Why

The v*.rsp read pages only expose 2 of 8 heating circuit setpoints (roomOT1 and roomOT2). All 8 setpoints — including roomNO, roomSNOT, hCu-slope, hCu-exp, and the 4 OT time slots — are only accessible via the WEB-RC menu at access level 3 (code 4444). This gap makes it impossible to read or change key scheduling values (e.g., the night/standby setpoint roomSNOT) through the API.

## What Changes

- Add `GET /api/v1/circuits/{circuit_id}/setpoints` — returns all writable setpoints for a heating circuit (HC1 or HC2)
- Add `PATCH /api/v1/circuits/{circuit_id}/setpoints` — updates one or more setpoints for a heating circuit
- Extend `SessionManager` to maintain a WEB-RC elevated session (access code 4444) alongside the existing standard session
- Add a WEB-RC navigation helper that re-establishes server-side context before each read/write

## Capabilities

### New Capabilities

- `heating-circuit-setpoints`: Read and write temperature setpoints for HC1 and HC2 via the WEB-RC menu path. Covers roomOT1–4, roomNO, roomSNOT. Excludes hCu-slope and hCu-exp (controller tuning, not temperature setpoints) and SP-Flow (read-only on the device).

### Modified Capabilities

- `session-management`: The session layer must support a second, persistently-elevated WEB-RC session (code 4444 entered on login) and re-establish WEB-RC navigation context before each request. Re-login and re-elevation must be atomic when the session expires.

## Impact

- **`app/session.py`**: extend to support WEB-RC elevation; add re-elevation on session expiry
- **`app/client.py`**: add `get_hc_setpoints(circuit: int)` and `set_hc_setpoint(circuit: int, name: str, value: float)` using WEB-RC path navigation + `execset.rsp` writes
- **`app/parsers.py`**: add `parse_hc_setpoints(html)` that reads the WEB-RC setpoints table
- **`app/models.py`**: add `HeatingCircuitSetpoints` Pydantic model
- **`app/routers/`**: add `setpoints.py` with the two new endpoints
- **`app/main.py`**: register the new router
- No breaking changes to existing endpoints
