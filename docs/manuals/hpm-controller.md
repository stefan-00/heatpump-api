# HPM Controller — PAW-HPM 800B7F

Source: `import/HPM_HBInstIB_en.pdf` (Part 1) and `import/Aquarea-part2-modules.pdf` (Part 2)

---

## Access levels

The HPM menu is structured into five access levels. Higher levels expose more parameters.

| Level | Code | Scope |
|---|---|---|
| 0 | *(none)* | End-user read-only |
| 1 | 1111 | Operator |
| 2 | 2222 | Service technician |
| 3 | 3333 | Advanced service |
| 4 | 4444 | WEB-RC / full configuration |

Enter a code via the **WEB-RC** menu path: `webfb.rsp` → `getcode.rsp` with `code=<CODE>&Set=OK&branchnr=1&level=0`.

---

## Menu structure (MCR-BMS)

Top-level navigation after login:

```
MCR-BMS
├── Timer
├── Heat producer
│   ├── HP1 / HP2 / HP3
│   └── Strategy circuit
├── Buffer tank
├── DHW (Domestic Hot Water)
├── Heating circuits
│   ├── HC1
│   └── HC2
└── Trend
```

Additional items at higher access levels:

```
├── Interfaces
├── Configuration
├── System Diagram
└── System Overview
```

---

## Aquarea basic configuration parameters

Located under **Heat producer → HP1** (or the active HP slot).

| Param | Range | Default | Description |
|---|---|---|---|
| Thermos | 0 / 1 | — | Thermostat enable (0=no, 1=yes) |
| Tank | 0 / 1 | — | DHW tank present (0=no, 1=yes) |
| SolarPrio | 0 / 1 | — | Solar priority |
| HeatPrio | 0 / 1 | — | Heating priority over tank |
| Steril | 0 / 1 | — | Sterilization enable |
| basPanH | 0 / 1 | — | Backup/panel heater |
| CoolPrio | 0 / 1 | — | Cooling priority |
| AntiFr | 0 / 1 | — | Anti-freeze enable |
| OpInt | 30–600 min | 180 | Operating interval (alternating mode) |
| TankInt | 5–95 min | 30 | Tank interval (alternating mode) |
| BoostDel | 20–95 min | 60 | Booster heater delay |
| SterTemp | 40–75 °C | 70 | Sterilization target temperature |
| SterTime | 5–60 min | 10 | Sterilization hold duration |
| HeaterC | 0 / 3 / 6 / 9 kW | 0 | Backup heater capacity |
| OutTOn | −15 – +20 °C | 0 | Outdoor temp threshold for backup heater |

---

## Heating circuit setpoints (HC1 / HC2)

### Flow temperature setpoints

| Param | Description |
|---|---|
| SP-Flow | Fixed flow temperature setpoint (used when no heating curve is active) |
| SP-room | Room temperature setpoint |

### Heating curve

The flow temperature is calculated from outdoor temperature using:

```
T_flow = T_base + slope × (T_room_setpoint − T_outdoor) ^ exponent
```

| Param | Description |
|---|---|
| hCu-slope | Heating curve slope |
| hCU-exp | Radiator exponent |

**Recommended slopes by emitter type:**

| Emitter | Slope range |
|---|---|
| Underfloor heating | 0.2 – 0.4 |
| Low-temperature radiators | 0.5 – 0.7 |
| Radiators | 0.8 – 1.0 |
| Convectors | 1.1 – 1.3 |

**Radiator exponents by emitter type:**

| Emitter | Exponent |
|---|---|
| Underfloor heating | 1.10 |
| Radiators | 1.20 |
| DIN standard radiators | 1.33 |
| Plate radiators | 1.25 – 1.40 |
| Convectors | 1.40 – 1.66 |

### Room temperature occupation setpoints

| Param | Description |
|---|---|
| roomOT1 | Room setpoint — occupation time 1 |
| roomOT2 | Room setpoint — occupation time 2 |
| roomOT3 | Room setpoint — occupation time 3 |
| roomOT4 | Room setpoint — occupation time 4 |
| roomNO | Room setpoint — normal (unoccupied) |
| roomSNOT | Room setpoint — setback / night |

### Flow temperature limits

| Param | Description |
|---|---|
| minFl | Minimum flow temperature limit |
| maxFl | Maximum flow temperature limit |
| maxDemFl-T | Maximum demanded flow temperature |

### Frost protection / reduced operation setpoints

| Param | Description |
|---|---|
| floReNO | Flow temperature setpoint in reduced (night) mode |
| flowReSNOT | Flow temperature setpoint in setback mode |

---

## DHW setpoints

| Param | Range | Default | Description |
|---|---|---|---|
| SP-tank | — | — | DHW storage target temperature |
| TankMax | ≤ 50 °C | — | Maximum tank temperature (HP only; booster heater can exceed) |

---

## Sensor reference table (HPM Part 1)

| Sensor label | Location |
|---|---|
| T-out | Outdoor air temperature |
| T-inl | Water inlet temperature (HP evaporator inlet) |
| T-outl | Water outlet temperature (HP condenser outlet) |
| T-buff | Buffer tank temperature |
| T-dhw | DHW tank temperature |
| T-room | Room thermostat / ambient sensor |
| T-solar | Solar collector temperature |
