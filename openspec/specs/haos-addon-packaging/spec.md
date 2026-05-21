# HAOS Add-on Packaging

## Purpose

Define the repository structure and metadata required for the HA Supervisor to discover, validate, and install the heatpump-api as an add-on.

## Requirements

### Requirement: Repository is a valid HA add-on repository
The repository root SHALL contain a `repository.json` file with `name`, `url`, and `maintainer` fields so the HA Supervisor can register it as an add-on source.

#### Scenario: User adds repository in Supervisor
- **WHEN** a user adds the GitHub repository URL in the HA Supervisor add-on store
- **THEN** the Supervisor reads `repository.json`, displays the repository name, and lists the `heatpump-api` add-on as available to install

### Requirement: config.yaml passes Supervisor validation
The `heatpump-api/config.yaml` SHALL contain all fields required by the Supervisor: `name`, `version`, `slug`, `description`, `arch`, `startup`, `boot`, `url` (non-empty GitHub URL), `homeassistant` (minimum HA version), `options`, and `schema`. The `host` option SHALL be removed (internal concern; hardcoded to `0.0.0.0` in the app).

#### Scenario: Supervisor installs the add-on
- **WHEN** a user installs the add-on via the Supervisor UI
- **THEN** the Supervisor validates `config.yaml` without errors and starts the container with the user-supplied options injected into `/data/options.json`

#### Scenario: User omits the optional port option
- **WHEN** a user installs the add-on without setting the `port` option
- **THEN** the add-on starts on the default port 8765

### Requirement: Add-on documentation is displayed in the Supervisor UI
The `heatpump-api/` directory SHALL contain a `DOCS.md` file. The Supervisor displays this file on the add-on's documentation tab.

#### Scenario: User opens the add-on documentation tab
- **WHEN** a user navigates to the add-on page in the Supervisor and clicks the Documentation tab
- **THEN** the content of `DOCS.md` is rendered, including: prerequisites, configuration option descriptions, a note about build time on first install, and a pointer to the HA sensor configuration guide

### Requirement: A version changelog exists
The `heatpump-api/` directory SHALL contain a `CHANGELOG.md` with an entry for the initial version (0.1.0) describing the capabilities present at that release.

#### Scenario: User checks the add-on changelog
- **WHEN** a user views `CHANGELOG.md`
- **THEN** they see at minimum one version entry with a date and a summary of features

### Requirement: Add-on image assets are present
The `heatpump-api/` directory SHALL contain `icon.png` (256×256 px) and `logo.png` (250×100 px). The Supervisor uses these in the add-on store listing.

#### Scenario: Add-on appears in the Supervisor store
- **WHEN** the add-on is listed in the Supervisor
- **THEN** it displays its icon and logo rather than the generic placeholder
