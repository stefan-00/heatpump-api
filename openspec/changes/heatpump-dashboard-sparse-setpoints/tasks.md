## 1. Re-sync the repo file with live

- [x] 1.1 Confirm the `grafana-home` MCP is connected (restart Claude Code if it is not), pull the live dashboard `heatpump-overview`, and cross-check it against ha-config's `config/grafana/heatpump-overview.json`. Verify by listing any substantive differences beyond the known `roomot2` query
- [x] 1.2 Rebuild `homeassistant/grafana/heatpump-dashboard.json` from the live panels verbatim, with datasource uids → `${DS_INFLUXDB}`, `__inputs`/`__requires` kept and `id`/`version` dropped. Verify that a panel-by-panel diff against live (uid mapped) shows no differences
- [x] 1.3 Commit the re-sync on its own, so the behaviour change in later commits diffs cleanly

## 2. Establish the baseline

- [ ] 2.1 In the Grafana UI, view the dashboard on a 6h range and record the colour each series renders with in DHW, HC2, Temperatures and Heat-source demand. Verify that the recorded list covers every series in those panels
- [ ] 2.2 Check `heatpump_buffer_setpoint` on 6h and 12h ranges, and its write count per day over 30 days (literal epoch-ms query via the datasource proxy). Record here whether it is missing or starts late. That decides task 3.3

## 3. Split sparse setpoints into lookback queries

- [ ] 3.1 Domestic Hot Water: remove `dhw_setpoint` from the regex, add a lookback query (design decision 2) with alias `$tag_entity_id`, and pin colours for both series. Verify the literal-epoch version through the datasource proxy, and on a 6h range in the UI that the line spans the full width in its old colour
- [ ] 3.2 HC2 (pool) & Heat Pump Temperatures: the same for `hc2_setpoint_roomot2`, pinning all five series' colours. Verify the same way, and that the other four series keep their colours
- [ ] 3.3 Heat-source demand, buffer & mixing valves: if 2.2 found it missing, the same for `heatpump_buffer_setpoint`, pinning the °C series' colours. Otherwise mark this task skipped with the reason
- [ ] 3.4 Temperatures: add `hc1_active_room_setpoint` with the lookback query, dashed like `hc1_flow_setpoint`, in a distinct pinned colour, and pin the existing five series' colours. Verify on a 6h range that it is dashed and spans the range
- [ ] 3.5 Confirm that no measured series (temperatures, valves, frequency, activity) has been given a lookback. Verify by grepping the final JSON: `90d` appears only in setpoint targets

## 4. Apply live and write back

- [ ] 4.1 Apply the edits to `heatpump-overview` via `update_dashboard`, then re-read it. Verify the dashboard loads without query errors on the 6h, 12h and 7d ranges
- [ ] 4.2 Write the re-read live JSON back to `homeassistant/grafana/heatpump-dashboard.json` in the export form from 1.2. Verify the panel-by-panel diff against live is empty
- [ ] 4.3 Commit and push to `main`
