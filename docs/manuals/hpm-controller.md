# HPM Controller — PAW-HPM 800B7F

Source: `import/HPM_HBInstIB_en.pdf` (Part 1) and `import/Aquarea-part2-modules.pdf` (Part 2)

---

## Access levels

The HPM menu is structured into five access levels. Higher levels expose more
parameters *and* make more of them writable.

The manual's generic defaults are not what this device uses — the codes are per
controller, stored under `global → service → access codes` (`1.3.5.n`). Codes
verified on our unit:

| Level | Code | Scope |
|---|---|---|
| 0 | *(none)* | End-user read-only |
| 1 | 9999 | Operator |
| 2 | 1111 | Service technician |
| 3 | 4444 | Advanced service — heating-circuit setpoints, setpoint limitation |
| 4 | 5555 | Full configuration — `interfaces`, network parameters |

Enter a code via the **WEB-RC** menu path: `webfb.rsp` → `getcode.rsp` with `code=<CODE>&Set=OK&branchnr=1&level=0`.

**Level 3 is not enough for everything it displays.** At 4444 the `interfaces →
Ethernet` page (`3.3.n`) renders but every field is read-only; entering 5555
makes them editable. Expect the same pattern elsewhere — visibility and
writability are separate gates, so a read-only field usually means "one level
up", not "not settable over the web".

The access-codes page itself only lists the codes at or below the session's
current level, which is why our level-3 dump shows rows for levels 1–3 and no
level 4, even though the manual documents `1.3.5.4 level 4`.

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

## Network interface (`interfaces → Ethernet`, `3.3.n`)

Source: `import/Aquarea-part2-modules.pdf` §9.3. **Requires access code 5555
(level 4) to edit** — at level 3 the page is visible but read-only.

| Param | Name | Notes | Live value |
|---|---|---|---|
| 3.3.1 | active | 0 = interface off, 1 = on | 1 |
| 3.3.2 | host name | own host name | hpm-800B7F |
| 3.3.3 | MAC-adr | read-only | 00:1F:FC:80:0B:7F |
| 3.3.4 | DHCPC | 0 = fixed IP, 1 = from DHCP server | 0 |
| 3.3.5 | IP-no | fixed address, used when DHCPC=0 | 192.168.1.11 |
| 3.3.6 | netMask | network mask | 255.255.255.0 |
| 3.3.8 | defaultGW | default gateway | 192.168.178.1 ⚠ |
| 3.3.9 | nameserver | DNS server | 192.168.178.1 ⚠ |
| 3.3.10 | Link | link status, read-only | LF |
| 3.3.11 | lowSpeed | 1 = force 10 Mbit/s | 0 |

⚠ Gateway and nameserver are still the German factory defaults and are not on
the device's own `192.168.1.0/24` subnet. Harmless for LAN-local access, which
is all the add-on needs.

Changes take effect after a **warm start** (`global → service → cold- warm
start → warm start = 1`, `1.3.4.1`) or a power cycle. Never set `coldStSys`
(`1.3.4.6`) — it resets every parameter to defaults.

Keep `DHCPC = 0`. The add-on's `heatpump_url` needs a stable LAN IP (a hostname
does not work), so use a router-side DHCP reservation if you want the router to
own the addressing. Changing the address means updating `heatpump_url` in the
add-on options and restarting it.

In a cascade install, loading a system diagram **overwrites** the slave
controllers' IP addresses (HPM Part 1, table 2.1: .11 / .12 / .13).

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
