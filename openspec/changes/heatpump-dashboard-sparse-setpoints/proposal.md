## Why

HA writes to InfluxDB only on a state change, so setpoints that rarely change have few points. Over 30 days `dhw_setpoint` was written ~4 times a day, `hc2_setpoint_roomot*` ~2 and `heatpump_buffer_setpoint` ~6. The Heat Pump dashboard's panels fill gaps with `fill(previous)` over `$timeFilter`, which can only carry forward a point that lies inside the range. On a 6h or 12h view these lines are therefore missing or start partway across, and the 7-day default hides it. Separately, the repo copy of the dashboard has drifted from what is live, so editing it as-is would overwrite a live fix.

## What Changes

- Re-sync `homeassistant/grafana/heatpump-dashboard.json` with the live dashboard (uid `heatpump-overview`) before anything else. The only substantive drift known today is that live "HC2 (pool) & Heat Pump Temperatures" plots `hc2_setpoint_roomot2` where the repo file has `roomot1`. The rest is defaults Grafana fills in on save. The file keeps its importable export form (`__inputs`, `${DS_INFLUXDB}`).
- Give each sparse setpoint its own query that reaches back 90 days before the range at a fixed 15-minute grouping. This is the pattern the Indoor Temperatures dashboard adopted on 2026-10-06. It applies to:
  - Domestic Hot Water: `dhw_setpoint`
  - HC2 (pool) & Heat Pump Temperatures: `hc2_setpoint_roomot2`
  - Heat-source demand, buffer & mixing valves: `heatpump_buffer_setpoint`, only if a short range shows it missing
- Split series keep their legend name and their colour, so the only visible change is that the line now spans the whole range.
- Add `hc1_active_room_setpoint` to the Temperatures panel (HC1), dashed like `hc1_flow_setpoint`, using the same lookback query.
- Dense series and measured temperatures stay on `$timeFilter` / `$__interval`.
- Apply live through the `grafana-home` MCP, then write the final live JSON back to the repo file.

## Capabilities

### New Capabilities
- `heatpump-dashboard`: the Heat Pump Grafana dashboard. Covers keeping the repo copy faithful to live, and making every setpoint line visible across any time range.

### Modified Capabilities

(none)

## Impact

- `homeassistant/grafana/heatpump-dashboard.json`, and the live Grafana dashboard `heatpump-overview` on the HA box.
- No add-on code, API or HA package changes.
- ha-config: its nightly Git Exporter snapshot (`config/grafana/heatpump-overview.json`) picks up the live change by itself. Nothing to do there.
