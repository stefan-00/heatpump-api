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

Requests SHALL declare whether they may be transparently retried after a re-authentication. Requests whose correctness depends on the device's current WEB-RC navigation position — all `menue.rsp` navigation steps, `info.rsp` range reads, and `execset.rsp` writes — SHALL opt out of transparent retry, because a re-authentication resets that position and the resent request would then address a different parameter. Retry-eligible requests (the stateless `v*.rsp` status pages) retain the existing retry-once behaviour.

#### Scenario: Authenticated request is made
- **WHEN** the client sends any request to the heatpump (status read, parameter set, etc.)
- **THEN** the request URL includes `?sessionid=<stored_value>` or `&sessionid=<stored_value>` appended to whatever other parameters are present

#### Scenario: Session expires mid-operation on a retry-eligible request
- **WHEN** a retry-eligible proxied request to the web UI returns a 302 redirect to the entry/login page (`enter.rsp` or `login.rsp`) or an HTTP 401
- **THEN** the service re-authenticates using the two-step flow, stores the new `sessionid`, retries the original request exactly once, and returns the result to the caller

#### Scenario: Session expires mid-operation on a navigation-dependent request
- **WHEN** a request that has opted out of transparent retry returns a 302 redirect to the entry/login page or an HTTP 401
- **THEN** the service re-authenticates and stores the new `sessionid` so the session is usable again, but SHALL NOT resend the original request; it SHALL raise so the caller can re-run the whole navigate-and-act operation against the fresh session

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

Because HC1 and HC2 expose identical child menu labels (`setpoints`, `function`, `setpoint limitation`), label matching alone cannot detect a walk that has drifted into the wrong circuit's subtree. Navigation SHALL therefore confirm the identity of the page it landed on before the caller uses it, for reads as well as writes.

An operation whose navigation or subsequent device interaction fails because the session expired SHALL be retried once in full — re-running the navigation from root before acting — rather than resending any individual request. Retry SHALL apply only to session-expiry failures and SHALL NOT apply to page-identity verification failures.

#### Scenario: Read HC2 setpoints after navigating to HC1
- **WHEN** a request for HC2 setpoints follows a request that left the server in HC1 context
- **THEN** the service resets to level=0 and re-navigates the full HC2 path before fetching the setpoints page, returning correct HC2 data

#### Scenario: Write setpoint requires full path traversal
- **WHEN** `execset.rsp` is called to update a setpoint
- **THEN** the service has already traversed the full navigation path to the setpoints page in the current request, so the server-side context matches the `branchnr` and `level` values in the write POST

#### Scenario: Session expires during navigation
- **WHEN** the session expires part-way through a navigation walk
- **THEN** the service SHALL NOT continue the walk on the re-authenticated session, and SHALL restart the whole operation from root exactly once

#### Scenario: Verification failure is not retried
- **WHEN** navigation completes but the landed page's identity does not match the intended target
- **THEN** the service SHALL surface a 502 without retrying, since a retry would repeat the same deterministic mismatch

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

The HPM web server maintains a single per-session, stateful navigation context. The service SHALL serialise **all** requests to the device through a single lock — WEB-RC navigation, `info.rsp` range reads, `execset.rsp` writes, and the `v*.rsp` status view pages alike — so that no request can interleave with another operation on the shared session.

Serialisation SHALL be determined by the fact that a request shares the session, not by whether it is a WEB-RC request. In particular, status reads SHALL hold the lock for the whole set of view-page fetches they perform, because a status read that interleaves between a verified navigation and its dependent writes causes those writes to land on the wrong parameter.

Within a single status read, the individual view-page fetches MAY proceed concurrently with each other, since they perform no navigation.

#### Scenario: Concurrent HC1 and HC2 navigation does not interleave
- **WHEN** requests that navigate to HC1 and HC2 WEB-RC pages arrive concurrently
- **THEN** the service serialises them through one lock, so each navigation re-establishes its full path from root without the other corrupting the shared session context, and each returns data for the correct circuit

#### Scenario: Status read does not interleave with a write operation
- **WHEN** a status read is requested while a WEB-RC write operation is between its navigation and its `execset` writes
- **THEN** the status read SHALL wait for the write operation to complete, and SHALL NOT issue any request to the device in the interim

#### Scenario: Write operation does not interleave with a status read
- **WHEN** a WEB-RC write is requested while a status read is in progress
- **THEN** the write SHALL wait for the status read to finish before beginning its navigation

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

### Requirement: Verify the landed WEB-RC page identity after navigation

After completing a navigation path, the service SHALL parse the page's self-identifying title row and SHALL confirm it matches the intended target before the page is read from or written to.

Every WEB-RC page renders a self-identifying title as the first row of its `<!-- start_mainpane -->`
block (for example `heatCirc1 setpoints`, `heatCirc2 F-SP.limit`). Because `(branchnr, level)`
coordinates collide across circuits — HC1 and HC2 setpoints pages are both `(bn=2, lv=4)`, and both
setpoint-limitation pages are both `(bn=2, lv=5)` — this title is the only evidence of which page a
navigation actually reached.

Matching SHALL be case-insensitive and SHALL require both a circuit marker (`heatcirc1` or `heatcirc2`) and a page
marker (`setpoints` or `f-sp.limit`) to be present, rather than exact equality with a full string, so
that cosmetic firmware differences do not reject valid pages.

When the title does not match, the service SHALL NOT read values from or write values to the page. It
SHALL log the observed title at WARNING level and SHALL surface a 502 error.

#### Scenario: Navigation reaches the intended page
- **WHEN** the service navigates the HC2 setpoint-limitation path and the landed page's title row is `heatCirc2 F-SP.limit`
- **THEN** verification passes and the operation proceeds

#### Scenario: Navigation drifts to the wrong circuit
- **WHEN** the service navigates intending HC2 setpoints but the landed page's title row is `heatCirc1 setpoints`
- **THEN** the service SHALL NOT write to or return values from that page, SHALL log the observed title at WARNING level, and SHALL return 502

#### Scenario: Navigation drifts to the wrong page within the correct circuit
- **WHEN** the service navigates intending the HC2 setpoint-limitation page but the landed page's title row is `heatCirc2 setpoints`
- **THEN** verification fails and the service returns 502 without issuing any write

#### Scenario: Title row is absent or unparseable
- **WHEN** the landed page contains no parseable mainpane title row
- **THEN** verification fails, and the service returns 502 rather than assuming the page is correct

### Requirement: Guard the window between navigation and write with the session generation

Each WEB-RC operation SHALL capture the session generation after its navigation completes and SHALL confirm the generation is unchanged immediately before **each** `execset` request it issues.

A re-authentication resets the device's navigation position to root without restoring the previous
path, so any `(branchnr, level)` write issued afterwards is misaddressed. The service SHALL maintain a
monotonically increasing session generation counter that increments on every successful login.

Where an operation writes several parameters in sequence, the check SHALL be repeated before every
individual write, not only before the first.

If the generation has changed, the service SHALL abandon the write and SHALL NOT issue the `execset`
request against the stale navigation context.

#### Scenario: Generation unchanged across a multi-parameter write
- **WHEN** the service writes `maxFl`, then `minFl`, then `active` and no re-authentication occurs
- **THEN** every generation check passes and all three writes are issued

#### Scenario: Re-authentication occurs partway through a multi-parameter write
- **WHEN** the session is re-authenticated after `maxFl` is written but before `minFl` is written
- **THEN** the service SHALL NOT issue the `minFl` or `active` writes against the stale context, and SHALL restart the operation from navigation or surface an error

### Requirement: Re-confirm page identity immediately before writing

Before issuing the first `execset` of an operation, the service SHALL re-select the target page at its own `(branchnr, level)` coordinates and SHALL re-confirm the page title identifies the intended circuit and page.

Verifying navigation only at the point it completes cannot protect against anything that disturbs the
session afterwards — which is how the 2026-08-13 leak happened, with a status poll landing between the
range reads and the writes.

If the re-confirmation fails, the service SHALL NOT issue any write and SHALL surface a 502.

#### Scenario: Position intact between navigation and write
- **WHEN** nothing has disturbed the session since navigation completed
- **THEN** re-selecting the target coordinates returns the same page, the title matches, and the write proceeds

#### Scenario: Position disturbed between navigation and write
- **WHEN** the device's navigation position has moved since navigation completed
- **THEN** re-selecting the target coordinates returns a page whose title does not match, and the service SHALL abort without issuing any `execset`

