## ADDED Requirements

### Requirement: Sensors degrade gracefully when the API returns an error body

When the API returns an error response (e.g. HTTP 502 with a JSON body such as `{"detail": "..."}`) instead of the expected payload, the configured HA sensor entities SHALL become `unavailable` rather than logging template errors or showing stale/invalid values. Each sensor in `packages/heatpump.yaml` SHALL use an `availability` template that checks for the presence of its expected key, AND a `value_template` that itself short-circuits to `none` when the expected key is absent — because HA's `rest` platform still renders `value_template` even when `availability` is false.

#### Scenario: API returns an error body during a poll
- **WHEN** HA polls `GET /api/v1/status` (or a setpoints endpoint) and the response body lacks the expected keys (e.g. an error envelope)
- **THEN** the affected sensor entities become `unavailable` and no `Template variable error` is logged for the missing keys

#### Scenario: API returns a valid payload
- **WHEN** HA polls an endpoint and the response contains the expected keys
- **THEN** each sensor's `availability` template evaluates true and its `value_template` renders the value as normal
