## 1. Session — elevation

- [x] 1.1 In `session.py` `login()`, after storing `_session_id`, POST `getcode.rsp` with `code=4444&Set=OK&branchnr=1&level=0&sessionid=SID` then GET the 302 redirect target (`menue.rsp?branchnr=1&level=0`) to complete elevation
- [x] 1.2 Verify elevation is included in the re-auth path: the existing `login()` call inside the `_lock` block in `request()` already covers this since elevation is now part of `login()`

## 2. Models

- [x] 2.1 Add `HcSetpoints` Pydantic model to `models.py` with six optional float fields: `roomOT1`, `roomOT2`, `roomOT3`, `roomOT4`, `roomNO`, `roomSNOT`
- [x] 2.2 Add `HcSetpointsPatch` Pydantic model (all fields `float | None = None`) for the PATCH request body — or reuse `HcSetpoints` with all fields optional

## 3. Parser

- [x] 3.1 Add `parse_hc_setpoints(html: str) -> dict[str, float]` to `parsers.py` that extracts the six temperature setpoint values from the WEB-RC setpoints table rows (match by label name in each `<a id="N">` row)

## 4. Client — navigation and read

- [x] 4.1 Define the WEB-RC navigation path constants in `client.py`:
  - `_HC1_SETPOINTS_PATH = [(2,1),(5,2),(1,3),(2,4)]`
  - `_HC2_SETPOINTS_PATH = [(2,1),(5,2),(2,3),(2,4)]`
- [x] 4.2 Add `_webrc_navigate(path)` helper on `HeatpumpClient` that GETs `menue.rsp?branchnr=1&level=0` then steps through each `(bn, lv)` in `path`
- [x] 4.3 Add `get_hc_setpoints(circuit_id: str) -> HcSetpoints` on `HeatpumpClient` that navigates the correct path, GETs the setpoints page, and returns the parsed model
- [x] 4.4 Add a per-circuit `asyncio.Lock` to `HeatpumpClient` to serialise concurrent requests to the same circuit

## 5. Client — write

- [x] 5.1 Add `_setpoint_position` mapping in `client.py`: `{"roomOT1": 1, "roomOT2": 2, "roomOT3": 3, "roomOT4": 4, "roomNO": 5, "roomSNOT": 6}`
- [x] 5.2 Add `set_hc_setpoint(circuit_id: str, field: str, value: float)` on `HeatpumpClient` that navigates the path then POSTs `execset.rsp` with `val`, `Set=OK`, `branchnr=<position>`, `level=4`, `id=<position>`
- [x] 5.3 Handle write failure: if `execset.rsp` does not return a 302 redirect to the setpoints page, fetch `info.rsp?branchnr=<position>&level=4` to read the device limits and raise an appropriate error

## 6. Router

- [x] 6.1 Create `app/routers/setpoints.py` with `APIRouter(prefix="/api/v1/circuits/{circuit_id}")`
- [x] 6.2 Implement `GET /setpoints` handler: validate `circuit_id` in `{"hc1","hc2"}` (404 otherwise), call `client.get_hc_setpoints()`, return `HcSetpoints`
- [x] 6.3 Implement `PATCH /setpoints` handler: validate `circuit_id`, validate body fields are all within the allowed set (422 otherwise), skip write if body is empty, call `client.set_hc_setpoint()` for each non-None field, return final `get_hc_setpoints()` result
- [x] 6.4 Register the new router in `app/main.py`

## 7. Verification

- [x] 7.1 Run `GET /api/v1/circuits/hc1/setpoints` and `GET /api/v1/circuits/hc2/setpoints` against the live device and confirm all six fields are returned with correct values matching the WEB-RC UI
- [x] 7.2 Run `PATCH /api/v1/circuits/hc2/setpoints` with `{"roomOT1": 36.0}`, confirm the response shows the updated value, then restore with `{"roomOT1": 35.0}`
- [x] 7.3 Confirm `PATCH` with an out-of-range value returns 422
- [x] 7.4 Confirm `PATCH` with an unknown field returns 422
- [x] 7.5 Confirm `GET /api/v1/circuits/hc3/setpoints` returns 404
