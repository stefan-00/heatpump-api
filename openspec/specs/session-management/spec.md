# Session Management

## Purpose

Manages authentication with the heatpump web UI, maintaining a single active session in memory and handling transparent re-authentication when sessions expire.

## Requirements

### Requirement: Authenticate with heatpump web UI
The service SHALL authenticate with the HPM-800B7F web UI using a two-step login flow: first obtain a `sessionid` from the initial HTTP redirect, then POST credentials to `/getlogin.rsp`. The `sessionid` string SHALL be stored in memory and appended as a URL query parameter on all subsequent requests. No cookie jar is used.

#### Scenario: Successful login on startup
- **WHEN** the service starts and no session exists
- **THEN** it sends `GET /` to the heatpump, extracts the `sessionid` from the `Location` header of the 302 redirect, then sends `POST /getlogin.rsp` with form fields `user`, `code`, and `sessionid`, and stores the returned `sessionid` for reuse

#### Scenario: Login fails due to wrong credentials
- **WHEN** `POST /getlogin.rsp` returns a 401 or 403 response, or redirects back to the login page instead of the main view
- **THEN** the service SHALL raise a startup error with a clear message indicating invalid credentials and refuse to serve requests

#### Scenario: Login fails due to network error
- **WHEN** the heatpump web UI is unreachable during login
- **THEN** the service SHALL log the error and retry according to the retry policy before failing

### Requirement: Pass session on every request
The service SHALL append `sessionid=<value>` as a URL query parameter to every HTTP request sent to the heatpump web UI. The session token SHALL NOT be sent as a cookie or HTTP header.

#### Scenario: Authenticated request is made
- **WHEN** the client sends any request to the heatpump (status read, parameter set, etc.)
- **THEN** the request URL includes `?sessionid=<stored_value>` or `&sessionid=<stored_value>` appended to whatever other parameters are present

#### Scenario: Session expires mid-operation
- **WHEN** a proxied request to the web UI returns a 302 redirect to `login.rsp` (session expired) or an HTTP 401
- **THEN** the service re-authenticates using the two-step flow, stores the new `sessionid`, retries the original request exactly once, and returns the result to the caller

#### Scenario: Re-authentication fails after session expiry
- **WHEN** the retry after re-authentication also fails
- **THEN** the service SHALL return a 502 error to the caller and log the failure; it SHALL NOT retry further

### Requirement: Single active session
The service SHALL maintain at most one active session at a time. Concurrent requests that trigger simultaneous re-authentication attempts MUST be serialised so that only one login request is sent to the web UI.

#### Scenario: Concurrent requests during re-authentication
- **WHEN** multiple requests arrive while a re-authentication is already in progress
- **THEN** all waiting requests use the new session once re-authentication completes rather than each initiating their own login

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
