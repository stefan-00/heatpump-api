## Context

See proposal.md for motivation. The facts that shape the approach:

- The status poll already fetches `v30.rsp` (HC1) and `v3.rsp` (HC2) every 30 s under `_device_lock`. Both pages carry the operating status, the timer status, and three of the six room setpoints:

  | | HC1 `v30.rsp` | HC2 `v3.rsp` |
  |---|---|---|
  | operating status | id 6 `nom. oper. OT2` | id 20 `nom. oper. OT1` |
  | timer status | id 8 `timer-OT2 ----------` | id 22 `timer-OT1 ------B---` |
  | roomOT1 / roomOT2 / roomNO | ids 17 / 169 / 18 | ids 31 / 170 / 32 |

  `roomOT3`, `roomOT4` and `roomSNOT` exist only on the WEB-RC setpoints page, which needs label navigation under the device lock.
- HA already polls `GET /api/v1/circuits/hc{1,2}/setpoints` every 60 s, so all six setpoints per circuit are in HA as `sensor.hcN_setpoint_room*`.
- Observed operating/timer strings: `nom. oper. OT1`, `nom. oper. OT2` (current fixtures, all three circuits), and `red. oper. SNOT` / `timer-SNOT ----` (HC2 during its 2025-08-30..2026-05-20 special non-occupation period, from the history of `docs/hpm-ui-surface.md`, commit 4f8a383). The whitespace padding of the SNOT capture was not preserved.
- The manual defines the periods: OT1..OT4 are occupation times, NO the non-occupation time, SNOT the special non-occupation time (holiday). Table 1.4 says the "holiday" switch position applies the NO setpoints and "continuous" applies OT1, so the operating status — not the timer — is what tells which setpoint is in force.
- All three timers (DHW, HC1, HC2) currently have OT1 + OT2 covering 24 h, so the `NO` period cannot be observed without changing a timer or the mode switch on the live system.

## Goals / Non-Goals

**Goals:**
- Report the period in force and its setpoint per circuit with zero added device traffic.
- Fail closed on strings we have not seen: `null`, never a guess, never a broken status.

**Non-Goals:**
- Provoking the NO or other states on the live device just to capture their strings.
- Interpreting the timer-status flag characters (`------B---`).
- DHW (`v107000.rsp` ids 34/36). The same parser would fit, but there is no consumer, and DHW's setpoint semantics (`SP-NO` is id 55, a correction) differ enough to need their own look.

## Decisions

### Resolve in the API from the view page; fall back in HA for the rest

The API resolves `active_room_setpoint` only when the value is on the page it already fetched (OT1, OT2, NO). For OT3, OT4 and SNOT it returns `null`, and the HA template sensor falls back to `sensor.hcN_setpoint_room<period>` from the existing `/setpoints` poll.

- *Alternative: resolve everything in the API.* Needs the WEB-RC setpoints page on every status poll — two label navigations per 30 s, held under `_device_lock`, in the same session as the pool controller's writes. That is the traffic pattern behind every past corruption incident, for a value that changes a few times a year. Rejected.
- *Alternative: cache `/setpoints` results in the API and resolve from the cache.* Couples the status endpoint to whether anyone has called `/setpoints` recently, and makes staleness invisible. Rejected.
- *Alternative: resolve entirely in HA.* Works, but then the API's `active_room_setpoint` doesn't exist, and every consumer re-derives the period→setpoint mapping. Resolving in the API where it's free keeps the period and value from the same page fetch, so they can't skew; the HA fallback only covers periods HC1 never uses (it has two OTs) and HC2's winter standby.

### Period comes from the operating status's final token, matched against a closed set

Collapse whitespace, take the last token, and accept it only if it is exactly one of `OT1`–`OT4`, `NO`, `SNOT`. The prefix (`nom. oper.` / `red. oper.`) is not checked, so a firmware wording change in the prefix doesn't lose the period, but anything else — `off`, `frost prot.`, an extra word after the token — gives `null`.

`NO` is in the set though no `… NO` string has been observed. The shape is confirmed by two prefixes and three tokens, and the manual names the period `NO`. Accepting it costs nothing if the device spells it differently (the result is `null`, as now); leaving it out would guarantee `null` in the one state the feature exists for. Its test uses a fixture labelled as constructed, not captured.

### Raw strings are passed through

`operating_status` and `timer_status` are whitespace-collapsed (as `parse_text` already does) and returned verbatim, so an unrecognised state is still visible in HA and InfluxDB and can be turned into a fixture later.

### Parsing uses the lenient helpers

All four fields go through `_lenient` / `_optional_param`, the pattern from the heat-source change: absent or unparseable means `null`, never a 502. HC2's parse is already wrapped as best-effort; HC1's core fields stay strict, the new ones do not.

### Fixtures

The existing `v30.html` (OT2) and `v3.html` (OT1) are real captures and already cover the two observed `nom. oper.` states. SNOT and NO fixtures are derived by substituting the strings into a copy of `v3.html` / `v30.html`, with a comment at the top of each saying what was substituted and where the string came from. They are not presented as captures.

### HA naming

`sensor.hc1_operating_period` / `sensor.hc2_operating_period` are REST sensors on the status resource, with the raw strings as attributes. The active-setpoint sensors are `template` sensors, because they combine the REST value with the fallback. Both match the `sensor.hc1_*` / `sensor.hc2_*` InfluxDB globs.

Renames change `name:` only. These entities have a `unique_id`, so HA keeps the registered entity_id and updates the friendly name.

## Risks / Trade-offs

- [The device writes NO differently from `… NO`] → `period` is `null` during NO and the HA sensor shows unknown; the raw string is in the attributes and the next session adds it to the set with a real fixture. No wrong value is ever shown.
- [Fallback setpoint is up to 60 s older than the period] → Only for OT3/OT4/SNOT, whose values change by hand and rarely. Acceptable for a dashboard line.
- [Grafana line during the HC2 SNOT season depends on the `/setpoints` poll] → That poll already runs; if it is unavailable the active sensor goes unavailable rather than wrong.
- [Renamed friendly names confuse a reader of old screenshots] → entity_ids and history are unchanged, which is what dashboards and automations use.

## Migration Plan

1. Implement, test locally, bump the add-on version (Supervisor won't update otherwise), push.
2. **With approval:** update the add-on on the live instance; check `GET /api/v1/status` shows `period` for both circuits.
3. **With approval:** copy `homeassistant/packages/heatpump.yaml` into `/config/packages/`, check config, reload; verify the new entities and that `sensor.hc1_room_setpoint` kept its entity_id.
4. Hand back to ha-config: swap the Indoor Temperatures dashed line to `sensor.hc1_active_room_setpoint` once it has data, update `ha-config/GRAFANA.md`.

Rollback: the fields are additive. Reverting the add-on version and the package restores the previous state; the new InfluxDB series simply stop.

## Open Questions

- What the operating status reads in NO, holiday, summer and off states. Answerable from a future capture without changing the specs; the parser already handles unknown strings.
- What the flag characters in the timer status mean (HC2 shows a `B`). Not needed for this change.
