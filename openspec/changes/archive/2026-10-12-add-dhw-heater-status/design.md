## Context

See proposal.md — Why. `parse_hp1` already parses four best-effort fields from `v21.rsp` (`hc_setpoint`, `operating_state`, `heat_demand`, `defrost`) through `_lenient`, which turns an absent or unparseable value into `None`. The four new ids sit on the same page, in the same `LABEL   value` format. In the captured fixture they read:

| id | raw text |
|---|---|
| 110 | `setp.DHW                       2 °C` |
| 117 | `OP-TANK                         off` |
| 120 | `Stat-Heater                     off` |
| 121 | `Stat-Booster                    off` |

The HA package already has a `DHW Setpoint` sensor with `unique_id: heatpump_dhw_setpoint` (entity `sensor.dhw_setpoint`), fed from `domestic_hot_water.setpoint`.

## Goals / Non-Goals

**Goals:**
- Reuse the existing best-effort pattern exactly, so the new fields can never turn a working status into a 502.
- Make the two DHW setpoints impossible to confuse, in the API model and in HA.

**Non-Goals:**
- Any interpretation of the values: no filtering of the `dhw_setpoint` placeholder, no inference of booster state from temperatures.
- Grafana panels for the new entities; they can follow once the sensors have data.

## Decisions

- **Parse with `_lenient(html, id, parse_on_off)` / `_lenient(html, "110", parse_float)`**, as `defrost` and `hc_setpoint` do. `parse_on_off` is strict (last token must be `on`/`off`), so an unexpected string becomes `null` rather than a guessed `false` — which matters here because 120/121 have never been seen `on`. `parse_bool` was rejected for that reason.
- **Field names as suggested**: `tank_heating`, `electric_heater`, `booster_heater`, `dhw_setpoint` on `HeatPumpUnit`. `dhw_setpoint` lives under `heat_pump`, next to `hc_setpoint`, while the controller's own tank setpoint stays at `domestic_hot_water.setpoint`; the object it sits in says which one it is. Extend the existing model comment so it covers both `hc_setpoint` and `dhw_setpoint` (what the HPM asks the unit for; 2 °C placeholder with no demand; reported as-is).
- **HA `unique_id: heatpump_hp_dhw_setpoint`**, following `heatpump_hp_hc_setpoint`. `heatpump_dhw_setpoint` is already taken by the existing `DHW Setpoint` sensor; reusing it would collide and re-point that entity's history. The name `Heatpump DHW Setpoint` gives entity id `sensor.heatpump_dhw_setpoint`. Binary sensors: `heatpump_hp_tank_heating`, `heatpump_hp_electric_heater`, `heatpump_hp_booster_heater`, named `Heatpump Tank Heating`, `Heatpump Electric Heater`, `Heatpump Booster Heater`.
- **Binary sensors without a device class**, like `Heatpump Defrost`, so HA shows plain on/off rather than implying a verified heat state. Availability/value templates copy the guarded `defrost` form, so `null` reads as unavailable, never `off`.
- **Tests**: the fixture only has `off` values, so the `on` case is covered by rewriting the value with the existing `_replace_value` helper. The missing-ids case extends the `_drop_param` pattern and checks the core fields still parse. The status-level test in `test_client_status.py` gets the four fields asserted alongside `hc_setpoint`.
- **Version / changelog**: bump `config.yaml` from `0.1.14` to `0.1.15` and add a `0.1.15` entry at the top of `heatpump-api/CHANGELOG.md`. The changelog currently stops at `0.1.4`; backfilling 0.1.5–0.1.14 is not part of this change.

## Risks / Trade-offs

- [Ids 120/121 may not track the real relays] → The parser reports exactly what the page shows and assumes neither value; the first disinfection run with the sensors confirms or refutes it.
- [`dhw_setpoint` placeholder (2 °C) looks like a real target on a graph] → Documented in the model, the HA package comment and `docs/hpm-ui-surface.md`; consumers read it together with `tank_heating`.

## Migration Plan

Additive only. Install the new add-on version through the Supervisor, then copy the updated `packages/heatpump.yaml` into HA (done separately, outside this change). Rollback: reinstall the previous add-on version; the new HA entities go unavailable and can be removed from the package.

## Open Questions

- Do ids 120 (`Stat-Heater`) and 121 (`Stat-Booster`) reflect the Aquarea's actual relay state? Nobody has seen either read `on` yet; the first disinfection run with these sensors will show it. The answer doesn't change the implementation.
