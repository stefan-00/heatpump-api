## Context

`HeatpumpClient.get_status` fetches five view pages concurrently under `_device_lock`, then parses them in two tiers:

- **Core fields** (HP unit, HC1, DHW, mode) go through `extract_param` / `parse_*` inside one `try`. A `ValueError` there is a 502.
- **HC2** is parsed afterwards, best-effort. A failure logs a warning and leaves `heating_circuit_2 = None`.

Every new value was confirmed on the live device on 2026-09-25 with `research/probe_view_pages.py`. The live readings are in proposal.md. `Y-contr.` is on the view pages the poll already fetches, so the only new request is the buffer page.

Three quirks of the display strings shape the parsing:

- **The heat-demand texts have several words:** `no demand`, `Blocked / off`.
- **The buffer temperature has no unit** (`42.5`).
- **Some values carry a label prefix** (`setpointHC 2 °C`, `SP-zone1 42.0 °C`, `Stat-Defrost off`).

## Goals / Non-Goals

**Goals:**
- Add the new values without changing how the existing core fields fail. A new value that is missing or malformed must never turn a working status into a 502.
- Keep the status poll at one round of concurrent view-page GETs under the lock, with no WEB-RC traffic.

**Non-Goals:**
- Interpreting the values, for example treating `hc_setpoint = 2 °C` as "no demand" or mapping state texts to enums. The spec requires raw values, and the Grafana panel does the interpretation.
- Pump speed. Neither circuit page has it; see proposal.md.
- Moving the `Heat Source` subset pages (`v50000` etc.), or the `v21` ids already exposed.

## Decisions

### 1. Parse every new field as optional, and absorb parse errors as well as absence

`_optional_float` / `_optional_bool` return `None` only when the parameter is *absent*. If the parameter is present but `parse_float` finds no number, the `ValueError` propagates. `parse_hp1` runs inside the core `try`, so a malformed `setpointHC` would 502 the whole status.

Add a small wrapper that also maps `ValueError` to `None`, and use it for all new fields. The existing fields keep their current strict parsing, so they fail exactly as they do today.

*Alternative:* parse the new HP fields in a separate best-effort block after the core parse, like HC2. That was rejected: it splits one model's construction across two places for no gain, since per-field optionality already gives the isolation the spec asks for.

### 2. State texts keep the whole display string

`operating_state` and `heat_demand` use the whole stripped text with internal whitespace collapsed. They do not use `parse_last_token`, which would turn `no demand` into `demand`. Ids 88/89 have no label prefix on the live page, so nothing needs stripping. If a firmware update ever added a label, the text would carry it, which is visible and harmless.

### 3. The buffer is one more page in the same `gather`

`v100100.rsp` joins the existing `asyncio.gather` under the same lock hold. The device documents `v100.rsp` as an identical alias; `v100100` is used because it is the name the menu links point to.

A network error on the buffer page fails the gather like any other page, which gives a 502 as the spec requires. Parsing follows the HC2 pattern: `parse_buffer` raises `ValueError` if neither id 61 nor id 59 is present. The client catches that, logs a warning and leaves `buffer = None`. If only one of the two ids is present, the other is `null`.

### 4. Where the new fields go in the model

- `HeatPumpUnit`: `hc_setpoint`, `operating_state`, `heat_demand`, `defrost`. All are optional, defaulting to `None`.
- `HeatingCircuit.valve_position` and `HeatingCircuit2.valve_position`: optional.
- `Buffer(temp, setpoint)`: both optional. It hangs off `SystemStatus.buffer: Buffer | None = None`.

The valve position sits on the circuit rather than in a separate "valves" section, because each `Y-contr` belongs to its circuit's mixer and is read from that circuit's page.

### 5. HA entities follow the existing package conventions

The new entities are `rest` sensors in the same `resource` block, so they add no extra polls:

- **Numeric sensors** follow the existing `if … is defined and … is not none else none` guard pattern, so a `null` renders as `unknown`, not `0`.
- **Defrost** is a `rest` binary sensor whose `value_template` evaluates to true/false/none directly. The `rest` binary sensor has no `payload_on`.
- **Naming:** `unique_id`s start with `heatpump_` (`heatpump_hp_hc_setpoint`, `heatpump_buffer_temp`, `heatpump_hc1_valve_position`, …).

### 6. Grafana panel

Add one time-series panel to the Heat Pump dashboard (edited live via `grafana-home`, then exported to `homeassistant/grafana/`). It shows `hc_setpoint`, the outlet temperature, the HC2 flow setpoint and the buffer temperature on a °C axis, with the two valve positions on a right-hand `%` axis. Defrost goes in as a state band, reusing the existing state-timeline approach.

### 7. Parser tests from captured pages

The repo has no tests. The parsing is where the risk sits: the last-number rule, the texts with several words, the value with no unit, and `16:` versus `169:`. So add `pytest` with fixture HTML for `v21`, `v30`, `v3` and `v100100`, captured from the device with the session id scrubbed, and parser-level tests only.

*Alternative:* verify only live through the running API. That was rejected: it can't exercise the missing-value and malformed-value paths the spec requires. The client layer stays covered by a live check after deploy.

## Risks / Trade-offs

- **[`extract_param` matches by id prefix.]** `id=16:` must not match `169:`. The pattern already requires the colon after the id; a fixture test pins this.
- **[`hc_setpoint` reads `2 °C` with no demand, a likely placeholder.]** It could look like a real setpoint on a graph. → It is documented in `docs/hpm-ui-surface.md` and in the sensor's description. It must be read once while the compressor runs before the value is relied on for the analysis in proposal.md.
- **[The buffer page dropped one connection during probing.]** An extra page per poll adds a little exposure to transient 502s. → The existing poll already tolerates this: HA marks the sensors unavailable for one interval. It gets revisited only if the 502 rate visibly rises after deploy.
- **[`Y-contr` semantics.]** "controller contrSign back" is taken to mean mixer opening, where 100 % means fully open to the buffer. Not verified. → The panel labels the value "valve (Y-contr)" and makes no claim about its direction until it has been checked against a known state.

## Migration Plan

- **Deploy:** bump the add-on version (Supervisor won't update without it) and update from HA. Then copy the updated `packages/heatpump.yaml` into HA and restart it.
- **Check before relying on the history:** confirm the new entities are recorded in InfluxDB. The include rules live in HA's config, not in this repo.
- **Rollback:** reinstall the previous add-on version. The new fields are optional, so an older package keeps working against a newer API, and a newer package against an older API shows the new entities as `unknown`.

## Open Questions

- ~~What `hc_setpoint` reads while the compressor is running.~~ Resolved on 2026-09-25 by the fixture capture: during HC2 demand at 41 Hz it read `42 °C`, while `setp.DHW` (no DHW demand) still read `2 °C`. So `2 °C` is the no-demand placeholder.
