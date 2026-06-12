# Operating Modes — WH-MXF09/12 Mono-bloc

Source: `import/monobloc-service-manual.pdf` — Operation & Control section (pp. 44–63)

---

## Heating Mode

- 3-way valve directs HP output to the heating circuit (not tank).
- Compressor runs to meet flow temperature setpoint.
- Compressor shuts OFF when `(water outlet temp − setpoint) > 2 °C` for 3 minutes continuously.
- Compressor restarts when outlet drops back below setpoint.
- Water pump runs continuously while heating mode is active.

---

## Tank (DHW) Mode

- 3-way valve switches to direct flow into the tank.
- HP outlet temperature is limited to **53 °C** maximum (HP-only heating; backup heater can go higher).
- Tank set temperature maximum is **50 °C** when HP is the sole heat source.
- **Booster heater delay timer**: the backup heater does not engage until after the delay configured by `BoostDel` (default 60 min) has elapsed without reaching set temperature.
- Tank mode ends when the DHW sensor reaches the set temperature.

---

## Heat + Tank Mode

Two sub-modes depending on `HeatPrio` setting:

### Heating priority enabled (`HeatPrio = 1`)

- Room thermostat controls 3-way valve switching.
- When room thermostat calls for heat: 3-way valve → heating circuit.
- When room thermostat is satisfied: 3-way valve → tank (if tank needs heating).

### Heating priority disabled (`HeatPrio = 0`) — alternating mode

- HP alternates between heating circuit and DHW tank on fixed interval timers.
- `OpInt` (default 180 min) — duration of each heating circuit interval.
- `TankInt` (default 30 min) — duration of each tank heating interval.
- The cycle continues regardless of room thermostat state.

---

## Anti-freeze Mode

Protects the hydraulic circuit from freezing when the system is in standby.

| Condition | Action |
|---|---|
| Outdoor temp < 3 °C **and** water temp < 6 °C | Water pump turns ON |
| Water temp < 6 °C (pump already running) | Backup heater turns ON |

Anti-freeze operates independently of the main operating mode.

---

## Sterilization Mode

Raises the DHW tank to a high temperature to kill legionella.

- Target temperature: `SterTemp` (range 40–75 °C, default **70 °C**).
- Hold duration: `SterTime` (range 5–60 min, default **10 min**).
- Maximum sterilization cycle duration: **4 hours**.
- If set temperature is not reached within 4 hours, the cycle aborts.
- Backup/booster heater is used to reach temperatures above the HP limit.

---

## Quiet Operation Mode

Reduces acoustic output by throttling the outdoor fan.

- Fan speed is reduced by **80 rpm** from the normal operating speed.
- Minimum fan speed: **200 rpm** (fan does not stop).
- Quiet mode can be scheduled via the HPM timer or activated manually.

---

## Solar Mode

Used when a solar thermal collector is connected.

- 3-way valve position is controlled by the solar pump station signal.
- When solar energy is available and tank needs heat: solar circuit takes priority.
- HPM monitors solar collector temperature (`T-solar`) and tank temperature (`T-dhw`).

---

## Force Heater Mode

Backup operating mode for HP malfunction.

- Bypasses the heat pump compressor circuit entirely.
- All heating demand is met by the electric backup heater only.
- Intended as a temporary fallback — not for continuous operation.

---

## Water Pump Safety Control

The water pump has an independent safety shutdown:

| Condition | Action |
|---|---|
| Water inlet temp > 80 °C for 10 seconds | Pump shuts off |
| 10 minutes after shutdown | Pump automatically restarts |

This applies regardless of the active operating mode.

---

## Protection Controls Summary

| Protection | Trigger | Response |
|---|---|---|
| Compressor overheating | Discharge pipe temp exceeds limit | Compressor stops (F20) |
| High pressure | Refrigerant high pressure switch trips | Compressor stops (H64 / F12 / F27) |
| Low pressure | Refrigerant low pressure too low | Compressor stops (H63) |
| Freeze prevention | Heat exchanger temp too low | Compressor stops (H99) |
| Water pump thermal | Water inlet > 80 °C / 10 s | Pump stops, auto-restarts after 10 min |
| Backup heater OLP | Backup heater overload protector | Heater stops (H70) |
| Tank heater OLP | Tank heater overload protector | Heater stops (H91) |
