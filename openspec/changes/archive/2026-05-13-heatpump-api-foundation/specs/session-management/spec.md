## ADDED Requirements

### Requirement: Authenticate with heatpump web UI
The service SHALL authenticate with the heatpump web UI using credentials supplied in configuration and store the resulting session (cookies or token) in memory for reuse by subsequent requests.

#### Scenario: Successful login on startup
- **WHEN** the service starts and no session exists
- **THEN** it performs a login request to the web UI using configured credentials and stores the resulting session material

#### Scenario: Login fails due to wrong credentials
- **WHEN** the login request returns an authentication failure response
- **THEN** the service SHALL raise a startup error with a clear message indicating invalid credentials and refuse to serve requests

#### Scenario: Login fails due to network error
- **WHEN** the heatpump web UI is unreachable during login
- **THEN** the service SHALL log the error and retry according to the retry policy before failing

### Requirement: Transparent session refresh
The service SHALL detect when a session has expired during a proxied request and automatically re-authenticate and retry the original request once without exposing the re-auth to the caller.

#### Scenario: Session expires mid-operation
- **WHEN** a proxied request to the web UI returns a session-expired or 401 response
- **THEN** the service re-authenticates, replaces the stored session, retries the original request exactly once, and returns the result to the caller

#### Scenario: Re-authentication fails after session expiry
- **WHEN** the retry after re-authentication also fails
- **THEN** the service SHALL return a 502 error to the caller and log the failure; it SHALL NOT retry further

### Requirement: Single active session
The service SHALL maintain at most one active session at a time. Concurrent requests that trigger simultaneous re-authentication attempts MUST be serialised so that only one login request is sent to the web UI.

#### Scenario: Concurrent requests during re-authentication
- **WHEN** multiple requests arrive while a re-authentication is already in progress
- **THEN** all waiting requests use the new session once re-authentication completes rather than each initiating their own login
