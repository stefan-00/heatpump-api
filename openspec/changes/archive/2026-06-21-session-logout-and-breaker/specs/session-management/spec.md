## ADDED Requirements

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

## MODIFIED Requirements

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
