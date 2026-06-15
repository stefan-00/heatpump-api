## MODIFIED Requirements

### Requirement: config.yaml passes Supervisor validation
The `heatpump-api/config.yaml` SHALL contain all fields required by the Supervisor: `name`, `version`, `slug`, `description`, `arch`, `startup`, `boot`, `url` (non-empty GitHub URL), `homeassistant` (minimum HA version), `options`, and `schema`. The `host` option SHALL be removed (internal concern; hardcoded to `0.0.0.0` in the app). The `options` and `schema` blocks SHALL include an optional `request_timeout` (typed `float?`) that sets the read/overall HTTP timeout in seconds for requests to the heatpump, defaulting to 15 when unset.

#### Scenario: Supervisor installs the add-on
- **WHEN** a user installs the add-on via the Supervisor UI
- **THEN** the Supervisor validates `config.yaml` without errors and starts the container with the user-supplied options injected into `/data/options.json`

#### Scenario: User omits the optional port option
- **WHEN** a user installs the add-on without setting the `port` option
- **THEN** the add-on starts on the default port 8765

#### Scenario: User omits the optional request_timeout option
- **WHEN** a user installs the add-on without setting the `request_timeout` option
- **THEN** the add-on uses a default read/overall timeout of 15 seconds for heatpump requests

#### Scenario: User raises the request timeout for a slow device
- **WHEN** a user sets `request_timeout` to a larger value because their device is slow to respond
- **THEN** the Supervisor accepts the value and the service uses it as the read/overall timeout for heatpump requests
