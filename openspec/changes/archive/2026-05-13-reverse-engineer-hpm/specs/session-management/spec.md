## MODIFIED Requirements

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
