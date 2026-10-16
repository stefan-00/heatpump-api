## REMOVED Requirements

### Requirement: The repo dashboard file matches the live dashboard
**Reason**: The repo no longer keeps a copy of the dashboard. ha-config's nightly snapshot records every live dashboard automatically.
**Migration**: Read the live dashboard through the Grafana API, or its snapshot at ha-config `config/grafana/heatpump-overview.json`.

### Requirement: Sparse setpoint lines span the whole selected time range
**Reason**: The dashboard is no longer specified here.
**Migration**: The behaviour stays on the live dashboard; the 90-day lookback is documented in ha-config `GRAFANA.md`.

### Requirement: Splitting a series out does not change how it looks
**Reason**: The dashboard is no longer specified here.
**Migration**: None needed; it described how the sparse-setpoint queries were introduced.

### Requirement: The active HC1 room setpoint is shown with the HC1 temperatures
**Reason**: The dashboard is no longer specified here.
**Migration**: The panel stays on the live dashboard; ha-config `GRAFANA.md` explains why the active setpoint is the right series.

### Requirement: Measured values are not carried in from before the range
**Reason**: The dashboard is no longer specified here.
**Migration**: The rule stays on the live dashboard and is documented in ha-config `GRAFANA.md`: the lookback is for setpoints only.
