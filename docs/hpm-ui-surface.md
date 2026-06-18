# HPM-800B7F Web UI Surface Map

Panasonic HPM-800B7F WEB-RC — complete parameter inventory discovered by
crawling the device's HTML UI. Used to plan the REST API surface.

Last crawled: 2026-05-22

## System layout

```
v0.rsp  ──────────────────────────────  System Survey (navigation hub)
  ├── v21.rsp      Heat Pump Unit 1     (v22, v23 exist but are empty — HP2/HP3 not installed)
  ├── v50000.rsp   Heat Source          (subset of v21 — also v10000/v20000/v30000/v70000 variants)
  ├── v30.rsp      Heating Circuit 1    — floor heating (also v10/v20/v50/v90 variants)
  ├── v3.rsp       Heating Circuit 2    — outdoor pool heating (also v1/v2/v5 variants)
  ├── v107000.rsp  Domestic Hot Water   (also v3000 minimal variant)
  └── v100100.rsp  Buffer Tank          (also v100 alias)
       └── vinfo.rsp  Parameter editor  (write endpoint)
```

**Physical system notes:**
- HC1 = floor heating
- HC2 = outdoor pool heating; active in summer, standby in winter
- Buffer tank is present
- HC2 `delOutT` = outdoor temperature with a smoothing/delay filter applied (not a separate sensor)
- Only HP1 is installed; HP2 (v22.rsp) and HP3 (v23.rsp) return no parameters


## System level — v0.rsp

| Param | Label | Current | Type | Notes |
|-------|-------|---------|------|-------|
| MS0 | Operating mode | `auto` | WRITE | off / auto / summer / vacation / nominalOp / manual |
| MS1 | Secondary mode | `auto` | WRITE | off / auto / force — purpose TBD (possibly force DHW) |


## Heat pump unit — v21.rsp

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 114 | On/Off | `on` | bool | ✓ `heat_pump.on` |
| 115 | Heating active | `on` | bool | ✓ `heat_pump.heating` |
| 111 | Outlet temp | `25 °C` | float | ✓ `heat_pump.outlet_temp` |
| 112 | Return temp | `24 °C` | float | ✓ `heat_pump.return_temp` |
| 126 | Compressor frequency | `0 Hz` | int | ✓ `heat_pump.frequency` |
| 125 | Error code | `---` | str | ✓ `heat_pump.error_code` |
| 117 | Tank heating active | `off` | bool | — |
| 118 | Force mode active | `off` | bool | — |
| 120 | Electric heater active | `off` | bool | — |
| 121 | Booster active | `off` | bool | — |
| 124 | Defrost active | `off` | bool | — |
| 123 | Warning active | `off` | bool | — |
| 128 | Electric heat energy | `9 kW` | int | — (configured capacity) |
| 127 | Service mode | `off` | bool | — |
| 87  | HP state | `Blocked / off` | str | — |
| 88  | Operating state | `no demand` | str | — |
| 89  | Heat demand | `no demand` | str | — |
| 109 | HC setpoint (from HP) | `2 °C` | float | — (internal HP value) |
| 110 | DHW setpoint (from HP) | `2 °C` | float | — (internal HP value) |


## Heating circuit 1 (floor heating) — v30.rsp

Main view. Also available as: v10 (with pump speed), v20 (without pump speed), v50 (minimal),
v90 (3-param: state/mode/timer only).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 9   | Outdoor temperature | `18.0 °C` | float | ✓ `outdoor_temp` (top-level) |
| 12  | Flow setpoint | `20.0 °C` | float | ✓ `hc1.flow_setpoint` |
| 13  | Flow temperature | `21.3 °C` | float | ✓ `hc1.flow_temp` |
| 15  | Pump on | `on` | bool | ✓ `hc1.pump_on` |
| 18  | Room setpoint (nominal) | `20.0 °C` | float | ✓ `hc1.room_setpoint` |
| 16  | Pump speed | `100 %` | int | — (v10 only) |
| 6   | Operating mode | `nom. oper. OT1` | str | — |
| 7   | Operating state | `normal` | str | — |
| 8   | Timer status | `timer-OT1 ----------` | str | — |
| 17  | Room setpoint OT1 | `20.0 °C` | float | ✓ `hc1.room_ot1` |
| 169 | Room setpoint OT2 | `20.0 °C` | float | ✓ `hc1.room_ot2` |


## Heating circuit 2 (pool heating) — v3.rsp

Active in summer. Standby in winter via timer SNOT period (was 30.08.25–20.05.26, now expired).
As of 2026-05-22, HC2 is in **OT2 mode** but pump is off because `delOutT` (20.5 °C) > `roomOT2` (19.0 °C).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 23  | Delayed outdoor temp (delOutT) | `20.5 °C` | float | ✓ `hc2.outdoor_temp` |
| 26  | Flow setpoint | `18.0 °C` | float | ✓ `hc2.flow_setpoint` |
| 27  | Flow temperature | `17.1 °C` | float | ✓ `hc2.flow_temp` |
| 29  | Pump on | `off` | bool | ✓ `hc2.pump_on` |
| 30  | Pump speed | `0 %` | int | — |
| 20  | Operating mode | `nom. oper. OT2` | str | — |
| 21  | Operating state | `normal` | str | — |
| 22  | Timer status | `timer-OT2 ----------` | str | — |
| 31  | Room setpoint OT1 | `45.0 °C` | float | ✓ `hc2.room_ot1` |
| 32  | Room setpoint (nominal, roomNO) | `19.0 °C` | float | ✓ `hc2.room_setpoint` |
| 170 | Room setpoint OT2 | `30.0 °C` | float | ✓ `hc2.room_ot2` |


## Domestic hot water — v107000.rsp

Full view. Also available as v3000 (minimal: state/mode/timer/actual temp only).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 37  | Setpoint | `45.0 °C` | float | ✓ `dhw.setpoint` |
| 38  | Actual temperature | `49.0 °C` | float | ✓ `dhw.actual_temp` |
| 117 | Tank heating active | `off` | bool | — (also in v21) |
| 34  | Operating mode | `nom. oper. OT2` | str | — |
| 35  | Operating state | `normal` | str | — |
| 36  | Timer status | `timer-OT2 -----` | str | — |
| 54  | Setpoint OT1 | `52.0 °C` | float | — |
| 171 | Setpoint OT2 | `45.0 °C` | float | — |
| 55  | Setpoint correction (NO) | `2.0 °C` | float | — |


## Buffer tank — v100100.rsp

Also accessible as v100.rsp (alias, identical content).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 61  | Buffer temperature | `34.3 °C` | float | — |
| 59  | Zone 1 setpoint | `20.0 °C` | float | — |
| 56  | Operating mode | `nom. oper.` | str | — |
| 57  | Operating state | `normal` | str | — |


## Heat source — v50000.rsp

All parameters are duplicates of v21.rsp. Also available as v10000/v20000/v30000 (subsets, 5 params each)
and v70000 (same as v50000). No unique data in any heat source page.


## Complete v*.rsp page inventory

All pages discovered by systematic probe (v0–v200 and common large numbers).
Variant pages show subsets of the main view for the same subsystem.

| Page | Title | Params | Notes |
|------|-------|--------|-------|
| v0 | system survey | 2 | MS0/MS1 write selectors |
| v1 | heatC. 2 | 12 | HC2 full — same content as v3 |
| v2 | heatC. 2 | 10 | HC2 without flow temp + pump speed |
| v3 | heatC. 2 | 12 | HC2 main view |
| v5 | heatC. 2 | 9 | HC2 minimal |
| v10 | heatC. 1 | 12 | HC1 full (includes pump speed) |
| v20 | heatC. 1 | 11 | HC1 without pump speed |
| v21 | hp1 | 20 | HP1 full view |
| v22 | hp2 | 0 | HP2 — empty, not installed |
| v23 | hp3 | 0 | HP3 — empty, not installed |
| v30 | heatC. 1 | 12 | HC1 main view |
| v50 | heatC. 1 | 10 | HC1 without pump speed + flow temp |
| v90 | heatC. 1 | 3 | HC1 minimal (state/mode/timer only) |
| v100 | buffer tank | 5 | Alias for v100100 |
| v3000 | domHotWater | 4 | DHW minimal (state/mode/timer/actual temp) |
| v10000 | heat source | 5 | HS subset of v21 |
| v20000 | heat source | 5 | HS subset of v21 |
| v30000 | heat source | 5 | HS subset of v21 |
| v50000 | heat source | 6 | HS full (incl. DHW setpoint) |
| v70000 | heat source | 6 | HS full — same as v50000 |
| v100100 | buffer tank | 5 | Buffer tank main view |
| v107000 | domHotWater | 10 | DHW full view |


## WEB-RC tab (menue.rsp / webfb.rsp)

A separate section of the UI accessible via the "WEB-RC" nav link. Requires
a two-step access elevation: login with service credentials, then POST to
`/getcode.rsp` to unlock the full menu tree.

### Access elevation protocol

```
POST /getcode.rsp
  code=4444&Set=OK&sessionid=SID&branchnr=1&level=0

→ 302 → menue.rsp?sessionid=SID&branchnr=1&level=0   (must be followed before navigating)
```

**`Set=OK` is required** — the submit button value that tells the server to
accept the code. Without it, the server returns 302 (appears to succeed) but
does not elevate the session. Navigation is stateful and parent pages must be
visited before child pages resolve correctly.

### Access codes (live, from device)

| Level | Username | Code |
|-------|----------|------|
| 1 | user | 9999 |
| 2 | operator | 1111 |
| 3 | service | 4444 |

### Full tree structure (access level 4444)

```
WEB-RC root  (branchnr=1, level=0)
├── global  (bn=1, lv=1)
│   ├── service  (bn=1, lv=2)
│   │   ├── software      Language=English
│   │   ├── cold-warm start   warm start 0, coldStSys 0
│   │   └── access codes  protect=2, level1=9999, level2=1111, level3=4444
│   └── structure  (bn=2, lv=2)
│       └── WEB            contr.name=HPM-800B7F, protect=1
│                          user=service (level3=44444444), operator (level2), user (level1)
├── MCR-BMS  (bn=2, lv=1)
│   ├── timers  (bn=1, lv=2)
│   │   ├── timer curVal      season=summer, day=friday
│   │   ├── timer chan. select.
│   │   │   ├── domHotWat.  → week program / special-non-occup. / special-occup. / priority
│   │   │   ├── heatc.1     → week program / special-non-occup. / special-occup. / priority
│   │   │   ├── heatc.2     → week program / special-non-occup. / special-occup. / priority
│   │   │   └── quiet       → week program / special-non-occup. / special-occup. / priority
│   │   ├── timer status      per-channel curStat / nxtStat / timeDiff
│   │   └── timer service     clock 21:05, date 22.05.26
│   ├── heat source  (bn=2, lv=2)
│   │   └── heat pump 1
│   │       ├── curValue      outdoor=18°C, HPOutletTemp=25°C, HPInletTemp=24°C, HPTankTemp=49°C
│   │       ├── setpoints     setpointHC=2°C, setp.DHW=2°C
│   │       ├── function      setpoint limitation / boost / controller / Bivalence / Aquarea / busStatus / pu/va exercise
│   │       ├── status        opStatus=Blocked/off, source=no demand
│   │       ├── manual oper.  no parameter
│   │       └── service       generalVal / sensor correction / terminal ass.
│   ├── buffer tank  (bn=3, lv=2)
│   │   ├── curValue          buffer1=34.3°C
│   │   ├── setpoints         SP-zone1=20.0°C, boostZ1=0.0
│   │   ├── function          boost / ext. demand / signal / buffer tank config
│   │   ├── status            opStatus=nom.oper., source=dem.HC1
│   │   ├── manual oper.      no parameter
│   │   └── service           sensor correction / terminal ass.
│   ├── domHotWater  (bn=4, lv=2)
│   │   ├── curValue          DHWtank=49.0°C
│   │   ├── setpoints         SP-OT1=52°C / SP-OT2=45°C / SP-OT3=45°C / SP-OT4=45°C / SP-NO=2°C / SP-SNOT=2°C / SP-DHWta=45°C
│   │   ├── function          setpoint limitation / controller / therm. disinfection
│   │   ├── status            opStatus=nom.oper.OT2
│   │   ├── manual oper.      no parameter
│   │   └── service           therm. disinfection / sensor correction / terminal ass.
│   ├── heatCirc.  (bn=5, lv=2)
│   │   ├── heatC. 1
│   │   │   ├── curValue      outdoor=18.0°C, flow=21.3°C, delOutT=20.5°C
│   │   │   ├── setpoints     roomOT1-4=20°C, roomNO=20°C, roomSNOT=14°C, hCu-slope=0.5, hCu-exp=1.10, SP-Flow=20.0°C
│   │   │   ├── function      summer shutdown / setpoint limitation (active=1, minFl=2°C, maxFl=65°C) / controller / screed drying
│   │   │   ├── status        opStatus=nom.oper.OT1, pump=on
│   │   │   ├── manual oper.  valve=3, pump=3
│   │   │   └── service       generalVal / summer shutdown / HCu Adaptation / screed drying / sensor correction / terminal ass.
│   │   └── heatC. 2
│   │       ├── curValue      outdoor=18.0°C, flow=17.1°C, delOutT=20.5°C
│   │       ├── setpoints     roomOT1=45°C, roomOT2=19°C, roomOT3=30°C, roomOT4=27°C, roomNO=22°C, roomSNOT=2°C,
│   │       │                 hCu-slope=0.5, hCu-exp=1.10, SP-Flow=18.0°C
│   │       ├── function      summer shutdown / setpoint limitation (active=0, minFl=2°C, maxFl=2°C ⚠) / controller / screed drying
│   │       ├── status        opStatus=nom.oper.OT2, pump=off, Y-contr=0.0%
│   │       ├── manual oper.  valve=3, pump=3
│   │       └── service       generalVal / summer shutdown / HCu Adaptation / screed drying / sensor correction / terminal ass.
│   ├── trend  (bn=6, lv=2)              all 10 trends inactive (active=0, no data)
│   ├── photovoltaics  (bn=7, lv=2)      PV curtailment setpoints
│   ├── Smart Grid  (bn=8, lv=2)         Smart Grid input states (inp1=0, inp2=0)
│   └── Extended configur.  (bn=9, lv=2)
│       ├── hCu1 room compens.  (room compens.=0)
│       ├── hCu2 room compens.  (room compens.=0)
│       ├── HP Bivalence        (HP-Biv=0)
│       ├── domHotWater solar   (solColl=0)
│       ├── buffer solar        (solColl=0)
│       ├── buffer addHS/fireside (addHS-Fl=0)
│       ├── photovoltaics       (type-Pv=1, dem-DHW=1@50°C, dem-HC=1@50°C, minSwOfTm=10min)
│       └── Smart Grid          (inp1=0, Inp2=0)
├── interfaces  (bn=3, lv=1)
│   ├── Ethernet   IP=192.168.1.11, DHCP=off, MAC=<device-mac>, host=hpm-800B7F
│   └── heatpumps  HP interface status
├── configuration  (bn=4, lv=1)
│   ├── inputs   term.17–28 (Pt1000 sensors + meter/mess + 0-10V)
│   ├── outputs  term01/03/05/07/09/11/13 (relays), term27/28 (0-10V)
│   └── switch   term.151=oMod-Sw, term.152/153/154=MS-W-pump1/2/3
├── diagrams  (bn=5, lv=1)    system diagram config (57133, easySetup=1, HP type MXF12D9E8-1)
└── system survey  (bn=6, lv=1)
    ├── controller    PAW-HPM1, H1.1.26, DIAGRAM 57133
    ├── heatC. 1      flow=21.3°C, SP-Flow=20.0°C, pump=on, opStatus=nom.oper.OT1
    ├── heatC. 2      flow=17.1°C, SP-Flow=18.0°C, pump=off, opStatus=nom.oper.OT2
    ├── domHotWater   DHWtank=49°C, SP-DHWta=45°C, opStatus=nom.oper.OT2
    ├── buffer tank   buffer1=34.3°C, SP-zone1=20.0°C
    ├── heat pump 1   freq=0Hz, StatEHeat=9kW, OP-OFF/ON=off, OP-HEAT=on, Blocked/off
    ├── inputs        term.18=21.3°C (HC1 flow), term.19=17.1°C (HC2 flow), term.22=34.3°C (buffer)
    └── outputs       term03=1, term07=1, term11=1 (others=0)
```

### Timer channel programs (live data)

**DHW** — week program group 3:
- Monday: 2 OT periods: OT1 11:00–14:00, OT2 14:00–11:00
- Special non-occupancy: 22.02.25–28.02.25
- Current status: OT2, next OT1 in 834 min

**HC1 (floor heating)** — week program group 3:
- Monday: OT1 21:00–06:00, OT2 06:00–21:00
- No special periods active
- Current status: OT1, next OT2 in 534 min

**HC2 (pool heating)** — week program group 3:
- Monday: OT1 07:30–17:00, OT2 17:00–07:30
- Special non-occupancy (winter standby): **30.08.25–20.05.26** ← **expired 2 days ago**
- Current status: OT2 (normal operation), next OT1 in 624 min (~10.4 h)

**Quiet mode** — week program group 0, all days OT1 24h (quiet enabled 24/7)

### HC2 heating curve details

HC2 uses the same weather-compensation curve as HC1 (`hCu-slope=0.5, hCu-exp=1.10`).

The **delayed outdoor temperature** (`delOutT`) is the smoothed/filtered outdoor reading used by the heating curve — currently **20.5 °C**, which is higher than `roomOT2=19.0 °C`. Since `delOutT > roomOT2`, the curve computes zero demand and the pump stays off.

**HC2 setpoint limitation** (function → setpoint limitation):
- `active = 0` (currently disabled)
- `minFl = 2.0 °C`, `maxFl = 2.0 °C`
- ⚠ If enabled, this would clamp the flow to 2 °C maximum — effectively locking out heating.

**HC2 HCu Adaptation** (stored curve calibration data — likely stale from winter):

| Outdoor | Measured flow |
|---------|--------------|
| +25 °C | 56.0 °C |
| +20 °C | 58.5 °C |
| +15 °C | 60.9 °C |
| +10 °C | 63.3 °C |
| +5 °C | 65.6 °C |
| 0 °C | 68.0 °C |
| −5 °C | 70.3 °C |

These values are far too high for pool heating and likely accumulated from when HC2 was configured differently. They do not affect normal setpoint operation.

### Aquarea settings (heat pump function → Aquarea → settings)

| Param | Value | Description |
|-------|-------|-------------|
| Thermost | 0 | Thermostat disabled |
| Tank | 1 | DHW tank present |
| BoosterH | 1 | Booster heater enabled |
| AntiFr | 1 | Anti-freeze enabled |
| BoostDel | 60 min | Booster heater delay |
| HeaterC | 9 kW | Backup heater capacity |
| OutTOn | −10 °C | Outdoor temp threshold for backup heater |
| BasePHeat | 0 | Base panel heater off |

### Terminal assignments

**Sensors (inputs)**

| Terminal | Type | Current reading | Assignment |
|----------|------|----------------|------------|
| term.17 | Pt1000 | 0.0 °C | (unused/disconnected) |
| term.18 | Pt1000 | 21.3 °C | HC1 flow sensor |
| term.19 | Pt1000 | 17.1 °C | HC2 flow sensor |
| term.20–21, 23–24 | Pt1000 | 0.0 °C | unused |
| term.22 | Pt1000 | 34.3 °C | buffer tank sensor |
| term.25–26 | meter/mess | 0 | pulse meters (unused) |
| term.27 | 0–10V | 0.1 % | (near zero) |
| term.28 | 0–10V | 0.0 % | (near zero) |

**Relays (outputs)**

| Terminal | Value | Notes |
|----------|-------|-------|
| term01 | 0 (off) | |
| term03 | 1 (on) | |
| term05 | 0 (off) | |
| term07 | 1 (on) | |
| term09 | 0 (off) | |
| term11 | 1 (on) | changed since last crawl |
| term13 | 0 (off) | |

**Switches** (all=auto): oMod-Sw (term.151), MS-W-pump1/2/3 (term.152–154)


## Write controls

| Control | Page | Endpoint | Values |
|---------|------|----------|--------|
| System operating mode | v0.rsp | `POST /ms.rsp` MS0 | off / auto / summer / vacation / nominalOp / manual |
| Secondary mode (purpose TBD) | v0.rsp | `POST /ms.rsp` MS1 | off / auto / force |
| Any individual parameter | vinfo.rsp | `POST /execgrset.rsp` id+val+pv+sessionid | param-specific |

Individual parameter writes via `execgrset.rsp` cover setpoint changes.
Mode switches via `ms.rsp` are higher-level named actions.

The WEB-RC pages render all parameters as read-only table rows — no `<input>`
elements are served. All setpoint edits go through `vinfo.rsp`/`execgrset.rsp`
from the v*.rsp views.
