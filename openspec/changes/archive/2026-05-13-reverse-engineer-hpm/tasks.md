## 1. Session management

- [x] 1.1 Update `SessionManager.login()` to perform the two-step HPM login: send `GET /` to extract `sessionid` from the `Location` header of the 302 redirect, then send `POST /getlogin.rsp` with form-encoded fields `user`, `code`, and `sessionid`; store the returned `sessionid` in `self._session_id`
- [x] 1.2 Update `SessionManager.request()` to inject `sessionid` as a URL query parameter (via `httpx`'s `params=` argument) on every outgoing request instead of relying on cookies
- [x] 1.3 Update `SessionManager.request()` to detect session expiry by checking if the response is a 302 redirect whose `Location` contains `login.rsp` (in addition to the existing 401 check), and trigger re-authentication in that case
- [x] 1.4 Update `StartupError` message for login failure to mention that the HPM credential field is called `code` (max 8 chars) but maps to the `password` config key

## 2. Data models

- [x] 2.1 Remove `HeatpumpState` and `ControlCommand` from `app/models.py`
- [x] 2.2 Add `HeatPumpUnit` Pydantic model with fields: `on: bool`, `heating: bool`, `outlet_temp: float`, `return_temp: float`, `frequency: int`, `error_code: str`
- [x] 2.3 Add `HeatingCircuit` Pydantic model with fields: `flow_setpoint: float`, `flow_temp: float`, `room_setpoint: float`, `pump_on: bool`
- [x] 2.4 Add `DomesticHotWater` Pydantic model with fields: `setpoint: float`, `actual_temp: float`
- [x] 2.5 Add `SystemStatus` Pydantic model with fields: `operating_mode: str`, `outdoor_temp: float`, `heat_pump: HeatPumpUnit`, `heating_circuit_1: HeatingCircuit`, `domestic_hot_water: DomesticHotWater`

## 3. HTML parser

- [x] 3.1 Create `app/parsers.py` with a helper `extract_param(html: str, param_id: str) -> str` that finds `<a ... href="vinfo.rsp?...&id=<param_id>:[^"]+">([^<]+)<` and returns the stripped inner text; raise `ValueError` if the parameter is not found
- [x] 3.2 Add `parse_float(text: str) -> float` helper that strips whitespace and unit suffixes (e.g. `" 23 °C"` → `23.0`, `" 22.6 °C"` → `22.6`)
- [x] 3.3 Add `parse_bool(text: str) -> bool` helper that returns `True` if the stripped text starts with `"on"` (case-insensitive)
- [x] 3.4 Implement `parse_hp1(html: str) -> HeatPumpUnit` using param IDs: `114` (on/off), `115` (heating), `111` (outlet temp), `112` (return temp), `126` (frequency), `125` (error code)
- [x] 3.5 Implement `parse_hc1(html: str) -> HeatingCircuit` using param IDs: `12` (flow setpoint), `13` (actual flow temp), `18` (room setpoint Normal), `15` (pump on/off)
- [x] 3.6 Implement `parse_dhw(html: str) -> DomesticHotWater` using param IDs: `37` (setpoint), `38` (actual tank temp)
- [x] 3.7 Implement `parse_system_mode(html: str) -> tuple[str, float]` that finds the `selected` option in the `MS0` select element for operating mode, and extracts outdoor temperature using param ID `9` from the same page (v0.rsp contains it via the heat source view)

## 4. Client

- [x] 4.1 Remove `send_command()` from `HeatpumpClient` in `app/client.py`
- [x] 4.2 Rewrite `get_status()` to fetch `v21.rsp` (HP unit), `v30.rsp` (HC1), `v107000.rsp` (DHW), and `v0.rsp` (system mode + outdoor temp) concurrently using `asyncio.gather`; decode all responses as `latin-1`
- [x] 4.3 Wire the four parser functions into `get_status()` and return a `SystemStatus`; raise `HTTPException(502)` with the raw HTML logged if any parser raises `ValueError`

## 5. Routing

- [x] 5.1 Update `app/routers/status.py` response model from `HeatpumpState` to `SystemStatus`
- [x] 5.2 Delete `app/routers/control.py` (AC-style endpoints are wrong for this device; control will be re-added in the next change)
- [x] 5.3 Remove `from .routers import control` from `app/main.py` and remove `app.include_router(control.router)`

## 6. Configuration

- [x] 6.1 Add a comment to `app/config.py` clarifying that the `password` field is sent to the HPM as the `code` form field (HPM login page label: "access code", max 8 chars)
- [x] 6.2 Update `heatpump-api/config.yaml` description for the `password` option to say "HPM access code (max 8 characters)"
