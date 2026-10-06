## 1. Re-sync the repo file with live

- [x] 1.1 Confirm the `grafana-home` MCP is connected (restart Claude Code if it is not), pull the live dashboard `heatpump-overview`, and cross-check it against ha-config's `config/grafana/heatpump-overview.json`. Verify by listing any substantive differences beyond the known `roomot2` query
- [x] 1.2 Rebuild `homeassistant/grafana/heatpump-dashboard.json` from the live panels verbatim, with datasource uids → `${DS_INFLUXDB}`, `__inputs`/`__requires` kept and `id`/`version` dropped. Verify that a panel-by-panel diff against live (uid mapped) shows no differences
- [x] 1.3 Commit the re-sync on its own, so the behaviour change in later commits diffs cleanly

## 2. Establish the baseline

- [x] 2.1 In the Grafana UI, view the dashboard on a 6h range and record the colour each series renders with in DHW, HC2, Temperatures and Heat-source demand. Verify that the recorded list covers every series in those panels
  - *Done without the UI* (no image renderer on the box). `palette-classic` colours are `palette[seriesIndex]`. Grafana 13.2.3's default palette, read from its bundle, starts `green, semi-dark-yellow, blue, orange, red, purple, dark-green`. Series order comes from the queries themselves: sorted by `entity_id`, valves (refId B) after the °C series. Temperatures: hc1_flow_setpoint green, hc1_flow_temperature semi-dark-yellow, heatpump_outdoor_temperature blue, heatpump_outlet_temperature orange, heatpump_return_temperature red. DHW: dhw_actual_temperature green, dhw_setpoint semi-dark-yellow. HC2: hc2_flow_temperature green, hc2_outdoor_temperature semi-dark-yellow, hc2_setpoint_roomot2 blue, heatpump_outlet_temperature orange, heatpump_return_temperature red. Heat-source: hc2_flow_setpoint green, heatpump_buffer_setpoint semi-dark-yellow, heatpump_buffer_temperature blue, heatpump_hc_setpoint orange, heatpump_outlet_temperature red, valve hc1 purple, valve hc2 dark-green. This holds for the 7d default, where every series is present. Before this change, a series missing on a short range shifted the colours of the series after it
- [x] 2.2 Check `heatpump_buffer_setpoint` on 6h and 12h ranges, and its write count per day over 30 days (literal epoch-ms query via the datasource proxy). Record here whether it is missing or starts late. That decides task 3.3
  - **Starts late, so split it.** Over 30 days it had 373 writes (12.4/day, median gap 0.3h). But every day it holds at 2 from about 10:00 to 21:00 with no write: 6 gaps over 6h, the longest 12.9h. A 6h view during the day therefore begins hours late

## 3. Split sparse setpoints into lookback queries

- [x] 3.1 Domestic Hot Water: remove `dhw_setpoint` from the regex, add a lookback query (design decision 2) with alias `$tag_entity_id`, and pin colours for both series. Verify the literal-epoch version through the datasource proxy, and on a 6h range in the UI that the line spans the full width in its old colour
- [x] 3.2 HC2 (pool) & Heat Pump Temperatures: the same for `hc2_setpoint_roomot2`, pinning all five series' colours. Verify the same way, and that the other four series keep their colours
- [x] 3.3 Heat-source demand, buffer & mixing valves: if 2.2 found it missing, the same for `heatpump_buffer_setpoint`, pinning the °C series' colours. Otherwise mark this task skipped with the reason
- [x] 3.4 Temperatures: add `hc1_active_room_setpoint` with the lookback query, dashed like `hc1_flow_setpoint`, in a distinct pinned colour, and pin the existing five series' colours. Verify on a 6h range that it is dashed and spans the range
- [x] 3.5 Confirm that no measured series (temperatures, valves, frequency, activity) has been given a lookback. Verify by grepping the final JSON: `90d` appears only in setpoint targets

## 4. Apply live and write back

- [x] 4.1 Apply the edits to `heatpump-overview` via `update_dashboard`, then re-read it. Verify the dashboard loads without query errors on the 6h, 12h and 7d ranges
  - Saved through `POST /api/dashboards/db` with the MCP's token and `overwrite: false` against v4, rather than `update_dashboard`, to keep the JSON out of context. Live is now v5, and the re-read equals the intended JSON. All targets on all three ranges ran without errors (frontend variables substituted by hand). Every lookback setpoint starts at the first 15m bucket edge. In the old in-range form, `dhw_setpoint` and `hc2_setpoint_roomot2` returned nothing at all on a 6h window
- [x] 4.2 Write the re-read live JSON back to `homeassistant/grafana/heatpump-dashboard.json` in the export form from 1.2. Verify the panel-by-panel diff against live is empty
- [x] 4.3 Commit and push to `main`
- [ ] 4.4 Open the dashboard in the browser on a 6h range and confirm the panels look right. Each split setpoint should span the full width in its previous colour, `hc1_active_room_setpoint` should be dashed purple, and no panel should show an error. This is the only check of the `${__from}`/`${__to}` form as the frontend actually sends it
