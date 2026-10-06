# heatpump-dashboard Specification

## Purpose
Define how the Heat Pump Grafana dashboard behaves, and keep its repo copy faithful to the live dashboard so that edits land on what is actually deployed.

## Requirements

### Requirement: The repo dashboard file matches the live dashboard
`homeassistant/grafana/heatpump-dashboard.json` SHALL contain the same panels, queries, aliases and field overrides as the live dashboard (uid `heatpump-overview`). It differs only in the export wrapper: the datasource is referenced as `${DS_INFLUXDB}` and declared under `__inputs`, so the file stays importable.

#### Scenario: Repo file compared with live
- **WHEN** the live dashboard JSON is compared panel by panel with the repo file, after mapping the datasource uid to `${DS_INFLUXDB}`
- **THEN** no panel, target, alias or override differs

#### Scenario: Importing the repo file
- **WHEN** the repo file is imported into a Grafana instance with an InfluxDB 1.x datasource
- **THEN** Grafana prompts for the datasource and every panel renders against it

### Requirement: Sparse setpoint lines span the whole selected time range
A setpoint series that HA writes rarely SHALL render from the left edge to the right edge of any selected range. Its value SHALL be the last one stored up to 90 days before the range start. This SHALL apply to `dhw_setpoint` in Domestic Hot Water, `hc2_setpoint_roomot2` in HC2 (pool) & Heat Pump Temperatures, `hc1_active_room_setpoint` in Temperatures, and `heatpump_buffer_setpoint` in Heat-source demand, buffer & mixing valves if a short range shows that series missing without it.

#### Scenario: Short range with no write inside it
- **WHEN** the dashboard shows a 6-hour range in which `dhw_setpoint` was not written, but it was written within the preceding 90 days
- **THEN** the Domestic Hot Water panel draws `dhw_setpoint` as a line across the full 6 hours at the last stored value

#### Scenario: Write inside the range
- **WHEN** `hc2_setpoint_roomot2` changes partway through the selected range
- **THEN** the line holds the earlier value up to the change and the new value after it

#### Scenario: No write for over 90 days
- **WHEN** a sparse setpoint has had no write in the 90 days before the range end
- **THEN** the series is absent from the panel (accepted limitation)

#### Scenario: Past range
- **WHEN** the selected range lies entirely in the past
- **THEN** the lookback is measured from that range's start, not from now

### Requirement: Splitting a series out does not change how it looks
A setpoint moved to its own query SHALL keep the legend name and line style it had before. Every series in an affected panel SHALL keep its colour.

#### Scenario: Legend after the split
- **WHEN** the Domestic Hot Water panel renders after `dhw_setpoint` moves to its own query
- **THEN** the legend still lists `dhw_actual_temperature` and `dhw_setpoint` with the same names and colours as before

### Requirement: The active HC1 room setpoint is shown with the HC1 temperatures
The Temperatures panel SHALL plot `hc1_active_room_setpoint` as a dashed line, styled like `hc1_flow_setpoint`.

#### Scenario: Temperatures panel
- **WHEN** the Temperatures panel renders any range
- **THEN** `hc1_active_room_setpoint` appears as a dashed line spanning the range

### Requirement: Measured values are not carried in from before the range
Measured temperatures, valve positions, frequency and binary activity series SHALL be queried only within the selected range. An outage then shows as a gap or flat stretch inside the range, and is not filled from older data.

#### Scenario: Measured temperature on a short range
- **WHEN** a 6-hour range is selected
- **THEN** `dhw_actual_temperature`, `hc2_flow_temperature` and the other measured series draw only points stored within those 6 hours
