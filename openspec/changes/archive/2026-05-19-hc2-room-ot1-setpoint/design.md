## Context

The existing API reads status via `v*.rsp` pages and manages a single authenticated session through `SessionManager`. The WEB-RC interface exposes a richer setpoint tree (6 temperature setpoints per circuit vs. 2 in `v3.rsp`) but requires:

1. A session elevation step (POST to `getcode.rsp` with `Set=OK` after every login)
2. Stateful server-side navigation: the HPM server keeps a level stack per session, so the full path to a page must be traversed in order before that page's data or write endpoint is valid

The HPM also uses a different write endpoint for WEB-RC parameters: `execset.rsp` (positional branchnr/level addressing) rather than `execgrset.rsp` (absolute parameter ID addressing).

## Goals / Non-Goals

**Goals:**
- Read all six HC1/HC2 temperature setpoints via the WEB-RC path
- Write individual setpoints via `execset.rsp` within the established WEB-RC context
- Keep re-elevation transparent: callers never deal with session elevation state

**Non-Goals:**
- Exposing hCu-slope, hCu-exp, or SP-Flow
- Writing setpoints via `execgrset.rsp` (only two are available there anyway)
- Supporting DHW or buffer setpoints in this change

## Decisions

### 1. Elevation is baked into `login()`, not a separate call; requires `GET /webfb.rsp` first

**Decision:** `SessionManager.login()` performs elevation immediately after the credential POST, before returning. Every session is always elevated. The elevation sequence is: `GET /webfb.rsp?sessionid=SID` → `POST /getcode.rsp` with `code=4444&Set=OK` → follow 302 redirect.

**Finding during implementation:** Omitting the `GET /webfb.rsp` step causes the elevation POST to return 302 (appearing to succeed) but the session is not actually elevated — the setpoints page returns only SP-Flow instead of the full six-setpoint list. The `webfb.rsp` GET initialises the server-side code-entry form state required for the POST to take effect. Additionally, the redirect URL returned by `getcode.rsp` already contains `sessionid`; appending it again as a query parameter corrupts the URL and breaks subsequent WEB-RC navigation.

**Alternative considered:** Elevate lazily on the first WEB-RC request. Rejected because it adds conditional state ("is this session elevated yet?") that complicates the re-auth path: if a standard-session request expires and re-auth triggers, the new session would be unelevated until the next WEB-RC call. Eager elevation keeps the invariant simple — after `login()` completes, the session is always ready for both paths.

### 2. Navigation context is re-established per request, not cached

**Decision:** Before each read or write, `HeatpumpClient` will navigate the full WEB-RC path from `branchnr=1&level=0` to the target page by GETting each ancestor step in sequence.

**Alternative considered:** Cache the current server-side context and skip re-navigation if the last operation was in the same path. Rejected because the HPM's context is session-scoped state on the device — it can be invalidated by any concurrent request (e.g., the `meta http-equiv="refresh"` on every WEB-RC page makes the browser refresh the page). The safe default is always re-navigate.

### 3. One `HcSetpoints` Pydantic model, both circuits share it

**Decision:** A single `HcSetpoints` model with six optional float fields (`roomOT1`–`roomOT4`, `roomNO`, `roomSNOT`) is used for both read responses and PATCH request bodies. For reads all fields are present; for writes only the supplied fields are acted on.

**Alternative considered:** Separate read/write models. Rejected — the six fields are identical for both circuits and both operations; separate models add friction for no gain.

### 4. PATCH writes fields sequentially, returns final read

**Decision:** For each field present in the PATCH body, navigate to the setpoints page and POST `execset.rsp` for that field's positional branchnr. After all writes, re-fetch the setpoints page and return the live values.

**Alternative considered:** Parallel writes. Rejected — `execset.rsp` operates on server-side context that is mutated by navigation. Writing in parallel with concurrent navigation calls would produce undefined device behaviour.

### 5. WEB-RC navigation uses label matching, not hard-coded branchnr values

**Decision:** Navigation to each circuit's setpoints page is done by matching menu link text at each level rather than following a pre-recorded `(branchnr, level)` sequence.

**Finding during implementation:** WEB-RC pages wrap the relevant content in `<!-- start_mainpane -->` / `<!-- end_mainpane -->` HTML comments. The initial parser used `id="mainpane"[^>]*>(.*?)</div>` which stopped at the first inner `</div>` and missed most rows. Switching to comment-based extraction (`re.search(r'<!--\s*start_mainpane\s*-->(.*?)<!--\s*end_mainpane\s*-->', html, re.DOTALL)`) correctly captures the full table.

**Finding during implementation:** The `branchnr` values for sub-menu items (e.g. `heatCirc.` within MCR-BMS) vary across sessions on the same device and do not match the values recorded during exploration. Hard-coded paths produced "Cannot find sub menu" errors. Switching to label-based lookup resolved this.

The label sequences used:
```
HC1: ["MCR-BMS", "heatCirc.", "heatC. 1", "setpoints"]
HC2: ["MCR-BMS", "heatCirc.", "heatC. 2", "setpoints"]
```

Note the space in `"heatC. 1"` / `"heatC. 2"` — the device renders these with a space before the digit.

The write for setpoint at position `n` (1-indexed, per the setpoints page order) uses:
`POST /execset.rsp  val=X&Set=OK&sessionid=SID&branchnr=n&level=4&id=n`

### 6. Device limit violations surface as 422 via pre-validation

**Finding during implementation:** `execset.rsp` returns HTTP 302 for both success and failure (the redirect URL is identical in both cases). There is no post-write signal to distinguish a rejected write from an accepted one.

**Decision:** Validate the requested value against device-reported limits *before* calling `execset.rsp`. The limits are read from `info.rsp?branchnr=N&level=4` immediately after navigation (while the WEB-RC context is on the target parameter). The response contains `Lower limit:` and `Upper limit:` rows; these are matched with `r'Lower limit:.*?(-?\d+\.\d+)\s*°'` (re.DOTALL) to extract the decimal value. If the requested value is outside `[lo, hi]`, a 422 is raised before any write is attempted.

Confirmed limit range for roomOT1: 2.0–50.0 °C.

## Risks / Trade-offs

**WEB-RC session is single-threaded by navigation** → Navigation path must be sequential per request. Concurrent setpoint writes to the same circuit will be serialised by a per-circuit asyncio lock in `HeatpumpClient`.

**HPM auto-refresh (10s)** → The `<meta http-equiv="refresh" content="10">` on WEB-RC pages means the browser would re-GET pages in the background. Our session only does reads/writes when explicitly called, so this is irrelevant — but it explains why the server's context can drift if sessions are shared between a browser and the API at the same time. Documented as a known limitation: don't browse WEB-RC in a browser while the API is active on the same session.

**Single shared session** → The existing `session_manager` is a process-wide singleton with one session. If the HPM allows only one active session at a time (which appears to be the case from the login retry logic), the API and a browser cannot be logged in simultaneously. This is an existing constraint, unchanged by this feature.

## Migration Plan

No breaking changes to existing endpoints. New router is additive. Deploy by restarting the container.

## Open Questions

All questions resolved. See Decision 6 for the execset.rsp success/failure signal finding and the pre-validation approach adopted.
