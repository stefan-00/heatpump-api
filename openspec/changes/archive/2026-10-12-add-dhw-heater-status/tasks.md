## 1. API model and parser

- [x] 1.1 Add `tank_heating`, `electric_heater`, `booster_heater` (`bool | None`) and `dhw_setpoint` (`float | None`) to `HeatPumpUnit`, extending the existing comment to cover `dhw_setpoint` (setpoint the HPM sends to the unit; 2 °C placeholder with no demand; reported as-is; not `domestic_hot_water.setpoint`); verify the model imports and existing tests pass
- [x] 1.2 Parse ids 117, 120, 121 with `_lenient(..., parse_on_off)` and id 110 with `_lenient(..., parse_float)` in `parse_hp1`; verify with the tests in 2.x

## 2. Tests

- [x] 2.1 Parser test against the `v21` fixture: `tank_heating`, `electric_heater`, `booster_heater` are `False` and `dhw_setpoint == 2.0`; verify with `pytest tests/test_parsers.py`
- [x] 2.2 Parser test using `_replace_value` to set ids 117/120/121 to `on`, asserting each reads `True`; verify it passes
- [x] 2.3 Parser test with unparseable values (e.g. `Stat-Booster ???`, `setp.DHW --- °C`) giving `None`; verify it passes
- [x] 2.4 Extend the missing-values case (or add one) dropping ids 110/117/120/121: all four are `None` and core fields such as `outlet_temp` still parse; verify it passes
- [x] 2.5 Assert the four fields in the status-level test in `tests/test_client_status.py`; verify the full suite passes with `pytest`

## 3. Home Assistant package

- [x] 3.1 Add sensor `Heatpump DHW Setpoint` (`unique_id: heatpump_hp_dhw_setpoint`, `°C`, `temperature`, `measurement`) to the status resource in `homeassistant/packages/heatpump.yaml`, with the guarded availability/value templates and a comment distinguishing it from `DHW Setpoint`; verify the existing `heatpump_dhw_setpoint` entry is untouched
- [x] 3.2 Add binary sensors `Heatpump Tank Heating`, `Heatpump Electric Heater`, `Heatpump Booster Heater` (`unique_id`s `heatpump_hp_tank_heating` / `_electric_heater` / `_booster_heater`), no device class, guarded like `Heatpump Defrost`; verify the file parses as YAML (e.g. `python3 -c` with a loader that tolerates `!secret`) and no `unique_id` is duplicated

## 4. Docs and release

- [x] 4.1 In `docs/hpm-ui-surface.md`, map ids 110, 117, 120, 121 to their `heat_pump.*` fields, note that 120/121 have not yet been seen `on` and are unverified against the real relays, and that 110 shares 109's placeholder behaviour; verify no target row still shows `—`
- [x] 4.2 Bump `heatpump-api/config.yaml` version `0.1.14` → `0.1.15` and add a `0.1.15` entry at the top of `heatpump-api/CHANGELOG.md`; verify the two versions match
- [x] 4.3 Run `openspec validate add-dhw-heater-status --strict` and verify it passes
