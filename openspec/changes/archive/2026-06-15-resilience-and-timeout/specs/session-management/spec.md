## ADDED Requirements

### Requirement: Resilient transport with retry policy and configurable timeout

The service SHALL apply an explicit, configurable timeout to every request sent to the heatpump web UI, and SHALL retry transient transport failures a bounded number of times with backoff before surfacing an error. This defines the "retry policy" referenced by the login and proxied-request flows.

The timeout SHALL default to a read/overall budget of 15 seconds with a connect budget of 5 seconds, replacing the HTTP client library's short default. The read/overall budget SHALL be configurable (via the `request_timeout` add-on option or `HEATPUMP_TIMEOUT` environment variable). Transient transport errors (connection refused, read timeout, protocol errors) SHALL be retried up to 2 additional times with linear backoff before being raised; the connect budget SHALL remain short so a genuinely unreachable host fails fast.

#### Scenario: Transient transport error is retried and succeeds
- **WHEN** a proxied request to the heatpump fails with a transport error (e.g. read timeout) but a subsequent attempt succeeds
- **THEN** the service retries the request after a short backoff and returns the successful response to the caller without surfacing a 502

#### Scenario: Transport error persists past retry budget
- **WHEN** a proxied request fails with a transport error on the initial attempt and all retries
- **THEN** the service raises the error to the caller as a 502 and logs the underlying exception using its `repr()` so empty-message transport errors remain identifiable

#### Scenario: Request timeout is configurable
- **WHEN** a `request_timeout` value is supplied via the add-on option or the `HEATPUMP_TIMEOUT` environment variable
- **THEN** the HTTP client uses that value as its read/overall timeout, defaulting to 15 seconds when unset, with a fixed 5-second connect timeout

### Requirement: Serialise WEB-RC navigation across circuits

The HPM web server maintains a single per-session, stateful navigation context. The service SHALL serialise all WEB-RC navigation and write operations through a single lock so that navigation for one circuit cannot interleave with navigation for another on the shared session.

#### Scenario: Concurrent HC1 and HC2 navigation does not interleave
- **WHEN** requests that navigate to HC1 and HC2 WEB-RC pages arrive concurrently
- **THEN** the service serialises them through one lock, so each navigation re-establishes its full path from root without the other corrupting the shared session context, and each returns data for the correct circuit
