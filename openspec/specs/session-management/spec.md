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
- **WHEN** a proxied request to the web UI returns a 302 redirect to the entry/login page (`enter.rsp` or `login.rsp`) or an HTTP 401
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

### Requirement: Resilient transport with retry policy and configurable timeout

The service SHALL apply an explicit, configurable timeout to every request sent to the heatpump web UI, and SHALL retry transient transport failures a bounded number of times with backoff before surfacing an error. This defines the "retry policy" referenced by the login and proxied-request flows.

The timeout SHALL default to a read/overall budget of 15 seconds with a connect budget of 5 seconds, replacing the HTTP client library's short default. The read/overall budget SHALL be configurable (via the `request_timeout` add-on option or `HEATPUMP_TIMEOUT` environment variable). Transient transport errors (connection refused, read timeout, protocol errors) SHALL be retried up to 2 additional times with linear backoff before being raised; the connect budget SHALL remain short so a genuinely unreachable host fails fast. A transport failure that the HTTP stack surfaces as a non-`RequestError` exception — specifically an `AttributeError` raised when a connection breaks during establishment — SHALL be treated the same as a transient transport error: retried within the budget and, if unresolved, wrapped so it surfaces to the caller as a 502 rather than an unhandled 500.

#### Scenario: Transient transport error is retried and succeeds
- **WHEN** a proxied request to the heatpump fails with a transport error (e.g. read timeout) but a subsequent attempt succeeds
- **THEN** the service retries the request after a short backoff and returns the successful response to the caller without surfacing a 502

#### Scenario: Transport error persists past retry budget
- **WHEN** a proxied request fails with a transport error on the initial attempt and all retries
- **THEN** the service raises the error to the caller as a 502 and logs the underlying exception using its `repr()` so empty-message transport errors remain identifiable

#### Scenario: Broken-connection AttributeError is treated as a transport error
- **WHEN** the underlying HTTP stack raises a non-`RequestError` exception caused by a connection breaking during establishment (the httpcore/anyio `'NoneType' object has no attribute 'getpeername'` `AttributeError`)
- **THEN** the service retries it within the transport-error budget and, if it persists, wraps it as a transport error so the caller receives a 502 — never an unhandled 500

#### Scenario: Request timeout is configurable
- **WHEN** a `request_timeout` value is supplied via the add-on option or the `HEATPUMP_TIMEOUT` environment variable
- **THEN** the HTTP client uses that value as its read/overall timeout, defaulting to 15 seconds when unset, with a fixed 5-second connect timeout

### Requirement: Serialise WEB-RC navigation across circuits

The HPM web server maintains a single per-session, stateful navigation context. The service SHALL serialise all WEB-RC navigation and write operations through a single lock so that navigation for one circuit cannot interleave with navigation for another on the shared session.

#### Scenario: Concurrent HC1 and HC2 navigation does not interleave
- **WHEN** requests that navigate to HC1 and HC2 WEB-RC pages arrive concurrently
- **THEN** the service serialises them through one lock, so each navigation re-establishes its full path from root without the other corrupting the shared session context, and each returns data for the correct circuit

### Requirement: Release the session on shutdown and before re-authentication

The HPM session pool is small and sessions are long-lived (no idle expiry observed), so an abandoned session lingers and eventually exhausts the pool. The service SHALL release its session by sending `GET /leave.rsp?sessionid=SID` (a) on shutdown and (b) before establishing a new session during re-authentication. Logout SHALL be best-effort: a failed `/leave.rsp` request SHALL be logged and ignored, and SHALL never prevent shutdown or re-authentication from proceeding.

#### Scenario: Session released on shutdown
- **WHEN** the service shuts down while holding an active session
- **THEN** it sends `GET /leave.rsp?sessionid=SID` for that session before closing the HTTP client, and the device frees the corresponding session slot

#### Scenario: Re-authentication releases the prior session
- **WHEN** the service re-authenticates while still holding a (possibly stale) `sessionid`
- **THEN** it first logs that session out via `/leave.rsp`, clears the stored id, and then performs the two-step login, so re-authentication does not strand a slot

#### Scenario: Logout failure does not block shutdown or re-auth
- **WHEN** the `/leave.rsp` request itself fails (e.g. the device is unreachable)
- **THEN** the service logs a warning and proceeds with shutdown or re-authentication regardless

### Requirement: Circuit-break repeated transport failures

When the HPM session pool is exhausted the device accepts TCP connections but drops them mid-read, and retrying only hammers it further — preventing the pool from draining. The service SHALL track consecutive transport failures and, once they reach a bounded threshold, open a circuit breaker that fails subsequent requests fast (HTTP 503) for a cooldown window instead of contacting the device. A successful request SHALL reset the breaker. The threshold SHALL be 5 consecutive failures and the cooldown SHALL be 30 seconds.

#### Scenario: Breaker opens after repeated failures
- **WHEN** consecutive transport failures (including failed re-authentication) reach the threshold
- **THEN** the breaker opens and further requests return HTTP 503 immediately, without contacting the device, until the cooldown elapses

#### Scenario: Breaker resets on success
- **WHEN** a request succeeds (the device responds)
- **THEN** the consecutive-failure count resets to zero and the breaker is closed

#### Scenario: Cooldown elapses
- **WHEN** the cooldown window has passed since the breaker opened
- **THEN** the next request is attempted against the device again rather than failing fast

