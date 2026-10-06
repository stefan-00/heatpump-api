## Context

See proposal.md for the motivation. Current state:

- The repo file is an importable export: `__inputs` / `__requires`, with `${DS_INFLUXDB}` in place of the datasource uid. The live dashboard uses uid `efpfpxt9z6t4wc` and schemaVersion 42 (the repo has 39). Its panels carry the defaults Grafana fills in on save (`pluginVersion` 12.3.0, `hideFrom`, `stacking`, thresholds, …). Compared against ha-config's snapshot of 2026-09-26, the only substantive drift is `hc2_setpoint_roomot1` → `roomot2` in the HC2 panel.
- Every affected panel uses `palette-classic` with no colour overrides, so colours are assigned by series order. Within one query the series come out sorted by `entity_id`.
- The DHW and HC2 queries use `mean("value")`. The heat-source panel uses `last("value")`. All of them use `GROUP BY time($__interval), "entity_id" fill(previous)` and the alias `$tag_entity_id`.
- The `grafana-home` MCP failed to connect in the session that wrote this change. Apply needs it, or the Grafana UI as a fallback.

## Goals / Non-Goals

**Goals:**
- Make the repo file equal to live, apart from the export wrapper.
- Make the sparse setpoint lines span short ranges, with no visual change otherwise.

**Non-Goals:**
- Restyling the dashboard or changing any panel layout.
- Changing how HA records to InfluxDB, for example forcing periodic writes.
- The sigenergy dashboard and the ha-config-owned dashboards.

## Decisions

**1. Re-sync from the live API, not the snapshot.** The ha-config snapshot is from 2026-09-26, and the live dashboard may have changed since. Pull live through `grafana-home` (`get_dashboard_by_uid heatpump-overview`) and use the snapshot only as a cross-check. Build the repo file from the live panels taken verbatim, with every datasource uid replaced by `${DS_INFLUXDB}`. Keep `__inputs` / `__requires`, and drop `id` / `version`. Copying Grafana's filled-in defaults is not semantic, but it makes later diffs against live show only real changes. *Alternative:* port only the `roomot2` query. That keeps the file smaller, but every future comparison would again show the same default noise.

**2. Lookback query per sparse setpoint, using the ha-config pattern verbatim:**

```sql
SELECT last("value") FROM "°C" WHERE "entity_id" = '<id>' AND time >= ${__from}ms - 90d AND time <= ${__to}ms GROUP BY time(15m), "entity_id" fill(previous) tz('Europe/Stockholm')
```

The split series is then removed from the shared regex. The query uses `last` rather than `mean`, because a setpoint is a step function and `mean` would blur a change inside a bucket. The 15m grouping stays fixed so the cost is flat, about 8.6k buckets per series, whatever the range. Grafana clips the x-axis to the range. *Alternative:* raise the `$__interval` minimum or use `fill(linear)`. Neither reaches points before the range. *Alternative:* a `$__timeFilter`-shifted query with `timeShift`. Grafana applies that to the whole query and shifts the x-axis too, so it does not work here.

**3. Keep the alias `$tag_entity_id`** on the new query, so legend names are unchanged.

**4. Pin colours explicitly in affected panels.** Moving a series into a later query changes its position in the frame order, and with it the palette-classic colour of every series behind it. Before the split, record the colour each series renders with in the UI. Then add a `byName` → `color: fixed` override for every series in each affected panel, set to that colour. *Alternative:* order the targets so the frame order is preserved. In the HC2 panel the setpoint sorts 3rd of 5, so no placement of the targets keeps it there.

**5. `hc1_active_room_setpoint` in Temperatures** uses the same lookback query. It gets the same dashed override as `hc1_flow_setpoint`: `lineStyle` dash [10, 10] and `fillOpacity` 0. It also gets a pinned colour that differs from the existing five.

**6. Buffer setpoint only on evidence.** Before touching it, view the panel on 6h and 12h ranges and query the write cadence with literal epoch-ms bounds. Split it only if the line is missing or starts partway across. Record the finding in tasks.md either way.

**7. Testing the variable form.** `${__from}` and `${__to}` are interpolated by the frontend, so a raw `/api/ds/query` rejects them with "empty bound parameter". Validate each lookback query through the datasource proxy with literal epoch-ms bounds, then confirm the real query in the panel UI on a 6h range.

## Risks / Trade-offs

- [The legend's min/mean/max for a lookback series include the 90 days before the range] → Accepted for setpoints. The lookback is never used for measured values (spec requirement).
- [A setpoint with no write and no HA restart for 90 days drops out again] → Accepted. An HA restart rewrites every state.
- [Pinned colours drift from the palette-classic look if series are added later] → New series still get palette colours. Only the pinned ones are fixed.
- [The live dashboard is edited in the UI between the pull and the write] → Pull immediately before editing, and re-read after `update_dashboard` to write the repo file from the result.

## Migration Plan

Apply live with `update_dashboard`, then export the result to the repo file. To roll back, re-apply the previous live JSON, which ha-config's snapshot also holds.
