## MODIFIED Requirements

### Requirement: config.yaml passes Supervisor validation
The `heatpump-api/config.yaml` SHALL contain all fields required by the Supervisor: `name`, `version`, `slug`, `description`, `arch`, `startup`, `boot`, `url` (non-empty GitHub URL), `homeassistant` (minimum HA version), `options`, and `schema`. The `host` option SHALL be removed (internal concern; hardcoded to `0.0.0.0` in the app). The `options` and `schema` blocks SHALL include an optional `request_timeout` (typed `float?`) that sets the read/overall HTTP timeout in seconds for requests to the heatpump, defaulting to 15 when unset. The `arch` list SHALL contain only currently-supported architectures (`aarch64`, `amd64`) and SHALL NOT include values the Supervisor has deprecated, such as `armv7`.

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

#### Scenario: Supervisor reads the manifest without deprecated-arch warnings
- **WHEN** the Supervisor reads `heatpump-api/config.yaml`
- **THEN** it does not log a deprecated-architecture warning because `arch` lists only `aarch64` and `amd64`

## ADDED Requirements

### Requirement: Repository may contain non-add-on config.yaml files
The HA Supervisor recursively searches the registered repository for `config.yaml` files and attempts to parse each as an add-on configuration. Because the add-on shares its repository with project tooling (OpenSpec, whose configuration lives at the fixed path `openspec/config.yaml`), the Supervisor SHALL be expected to log a benign "Invalid app config" warning for such non-add-on `config.yaml` files. This warning has no functional impact: add-on discovery, version detection, and installation SHALL continue to work correctly.

#### Scenario: Supervisor encounters a non-add-on config.yaml
- **WHEN** the Supervisor scans the repository and reads `openspec/config.yaml` (which is not an add-on config)
- **THEN** it logs an "Invalid app config" warning for that file and still discovers the `heatpump-api` add-on and its latest version correctly
