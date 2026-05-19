# Session Management (delta)

## ADDED Requirements

### Requirement: Elevate session to WEB-RC access level 3 after login
After every successful login, the service SHALL:
1. Send `GET /webfb.rsp?sessionid=SID` to initialise the server-side code-entry form state (mandatory — omitting this step causes the subsequent POST to return 302 but leaves the session unelevated)
2. Immediately POST to `/getcode.rsp` with `code=4444`, `Set=OK`, `branchnr=1`, `level=0`, and `sessionid` in the **POST body**
3. Follow the 302 redirect by GETting the URL from the `Location` header as-is — do NOT append `sessionid` again, as the redirect URL already contains it

Elevation SHALL be considered complete only when the redirect is followed. Elevation SHALL be retried as part of every re-authentication cycle.

#### Scenario: Elevation succeeds on startup
- **WHEN** the service logs in successfully
- **THEN** it immediately POSTs the elevation code and GETs the redirect target; the session is then ready for both standard and WEB-RC operations

#### Scenario: Session re-authentication includes re-elevation
- **WHEN** a WEB-RC request triggers session re-authentication due to an expired session
- **THEN** the service re-logs in and re-elevates before retrying the original request

### Requirement: Re-establish WEB-RC navigation context before each operation
The WEB-RC server maintains a per-session navigation stack. Before any WEB-RC read or write, the service SHALL navigate the full path from the WEB-RC root to the target page by GETting each ancestor `menue.rsp` step in order. The root SHALL always be reset to `branchnr=1&level=0` before traversing the path.

#### Scenario: Read HC2 setpoints after navigating to HC1
- **WHEN** a request for HC2 setpoints follows a request that left the server in HC1 context
- **THEN** the service resets to level=0 and re-navigates the full HC2 path before fetching the setpoints page, returning correct HC2 data

#### Scenario: Write setpoint requires full path traversal
- **WHEN** `execset.rsp` is called to update a setpoint
- **THEN** the service has already traversed the full navigation path to the setpoints page in the current request, so the server-side context matches the `branchnr` and `level` values in the write POST
