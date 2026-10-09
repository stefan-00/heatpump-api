# Operating Modes — WH-MXF09/12 Mono-bloc

Source: `import/monobloc-service-manual.pdf` — Operation & Control section (pp. 44–63)

---

## Heating Mode

- 3-way valve directs HP output to the heating circuit (not tank).
- Compressor runs to meet flow temperature setpoint.
- Compressor shuts OFF when `(water outlet temp − setpoint) > 2 °C` for 3 minutes continuously.
- Compressor restarts only after a 3-minute wait **and** once the water outlet temperature
  has dropped more than 3 °C below the water *inlet* temperature recorded at the moment
  it shut off (§12.1.2.1). The restart point is relative to the inlet at thermo-off, not
  to the setpoint.
- Water pump runs continuously while heating mode is active.

### How this interacts with the HPM buffer control

The HPM passes the Aquarea the buffer setpoint (`SP-zone1`, in HA `Heatpump HC Setpoint`)
with no margin on top. But charging the buffer *to* that setpoint needs outlet water
*above* it — a charge run typically sends 26–27 °C against a 24 °C setpoint. So any charge
run longer than about 3 minutes trips the Aquarea's own +2 K thermo-off above while the
HPM is still demanding heat. The compressor then waits for its water to fall ~3 K, which
can take hours, while the buffer sags 4–5 K below setpoint. Status and error code stay
normal throughout.

The signature in the data: `Heatpump On` = on, `Heatpump HC Setpoint` = the buffer
setpoint, frequency 0, and each stall ending when outlet ≈ (inlet at stop − 3).
Observed 2026-10-06 → 10-09, after HC1's roomOT1/roomOT2 went 18 → 20 °C: runs lengthened
from ~2 min to 8–12 min and stalls of 1.5–13 h took up about half the time. Before that,
2-minute runs ended (HPM demand off at buffer ≥ setpoint) before the 3-minute timer could
expire, so this never showed.

A fix needs a margin between the setpoint sent to the Aquarea and the buffer setpoint.
Candidate HPM parameters, neither confirmed — the manuals do not match this firmware's
labels:

- `heatp.1 → function → boost → boost.hCu` (live 0.0 °C). Not in either manual; the
  documented heat-pump boost (2.2.x.3.3) is a set of percentages per consumer, while this
  firmware shows `boost DHW1` plus this absolute °C value.
- `buffer tank → setpoints → boostZ1` (live 0.0). Part 2 §4.2 calls it "boost demand
  buffer zone 1", range 1.0–25.0, default 5.0; part 1's menu tree says "boost until
  switch-off limit". The live value is below the documented minimum.

Change one at a time and watch whether `Heatpump HC Setpoint` moves away from
`Heatpump Buffer Setpoint`; if it does not, revert.

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
