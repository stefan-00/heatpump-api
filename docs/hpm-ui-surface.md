# HPM-800B7F Web UI Surface Map

Panasonic HPM-800B7F WEB-RC — complete parameter inventory discovered by
crawling the device's HTML UI. Used to plan the REST API surface.

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
- HC2 = outdoor pool heating; active in summer, standby in winter (simulated via
  low flow setpoint + outdoor temp delta offset of +10°C)
- Buffer tank is present
- HC2 param 23 ("outdoor") shows outdoor_temp + delta, not a separate sensor
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
| 111 | Outlet temp | `21 °C` | float | ✓ `heat_pump.outlet_temp` |
| 112 | Return temp | `21 °C` | float | ✓ `heat_pump.return_temp` |
| 126 | Compressor frequency | `0 Hz` | int | ✓ `heat_pump.frequency` |
| 125 | Error code | `---` | str | ✓ `heat_pump.error_code` |
| 117 | Tank heating active | `off` | bool | — |
| 118 | Force mode active | `off` | bool | — |
| 120 | Electric heater active | `off` | bool | — |
| 121 | Booster active | `off` | bool | — |
| 124 | Defrost active | `off` | bool | — |
| 123 | Warning active | `off` | bool | — |
| 128 | Electric heat energy | `9` | int | — (unit unclear) |
| 127 | Service mode | `off` | bool | — |
| 87  | HP state | `nom. oper.` | str | — |
| 88  | Operating state | `normal` | str | — |
| 89  | Heat demand | `dem. HC1` | str | — |
| 109 | HC setpoint (from HP) | `28 °C` | float | — (internal HP value) |
| 110 | DHW setpoint (from HP) | `2 °C` | float | — (internal HP value) |


## Heating circuit 1 (floor heating) — v30.rsp

Main view. Also available as: v10 (with pump speed), v20 (without pump speed), v50 (minimal),
v90 (3-param: state/mode/timer only).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 9   | Outdoor temperature | `7.0 °C` | float | ✓ `outdoor_temp` (top-level) |
| 12  | Flow setpoint | `28.2 °C` | float | ✓ `hc1.flow_setpoint` |
| 13  | Flow temperature | `26.1 °C` | float | ✓ `hc1.flow_temp` |
| 15  | Pump on | `on` | bool | ✓ `hc1.pump_on` |
| 18  | Room setpoint (nominal) | `20.0 °C` | float | ✓ `hc1.room_setpoint` |
| 16  | Pump speed | `100 %` | int | — (v10 only) |
| 6   | Operating mode | `nom. oper. OT1` | str | — |
| 7   | Operating state | `normal` | str | — |
| 8   | Timer status | `timer-OT1 ----` | str | — |
| 17  | Room setpoint OT1 | `20.0 °C` | float | — |
| 169 | Room setpoint OT2 | `20.0 °C` | float | — |


## Heating circuit 2 (pool heating) — v3.rsp

Standby in winter (flow setpoint ≈ 2°C, pump off). Active in summer.
Param 23 shows outdoor_temp + delta (+10°C offset), not a separate sensor.
Also available as: v1 (same as v3), v2 (without flow temp/pump speed), v5 (minimal).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 23  | Outdoor + delta (reference temp) | `17.0 °C` | float | — |
| 26  | Flow setpoint | `2.0 °C` | float | — |
| 27  | Flow temperature | `19.9 °C` | float | — |
| 29  | Pump on | `off` | bool | — |
| 30  | Pump speed | `0 %` | int | — |
| 20  | Operating mode | `red. oper. SNOT` | str | — |
| 21  | Operating state | `normal` | str | — |
| 22  | Timer status | `timer-SNOT ----` | str | — |
| 31  | Room setpoint OT1 | `35.0 °C` | float | — |
| 32  | Room setpoint NO | `22.0 °C` | float | — |
| 170 | Room setpoint OT2 | `27.0 °C` | float | — |


## Domestic hot water — v107000.rsp

Full view. Also available as v3000 (minimal: state/mode/timer/actual temp only).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 37  | Setpoint | `45.0 °C` | float | ✓ `dhw.setpoint` |
| 38  | Actual temperature | `48.0 °C` | float | ✓ `dhw.actual_temp` |
| 117 | Tank heating active | `off` | bool | — (also in v21) |
| 34  | Operating mode | `nom. oper. OT2` | str | — |
| 35  | Operating state | `normal` | str | — |
| 36  | Timer status | `timer-OT2 ----` | str | — |
| 54  | Setpoint OT1 | `52.0 °C` | float | — |
| 171 | Setpoint OT2 | `45.0 °C` | float | — |
| 55  | Setpoint correction (NO) | `2.0 °C` | float | — |


## Buffer tank — v100100.rsp

Also accessible as v100.rsp (alias, identical content).

| ID  | Label | Current | Type | API |
|-----|-------|---------|------|-----|
| 61  | Buffer temperature | `22.8 °C` | float | — |
| 59  | Zone 1 setpoint | `28.2 °C` | float | — |
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

→ 302 → menue.rsp?branchnr=1&level=0   (must be followed before navigating)
```

**`Set=OK` is required** — the submit button value that tells the server to
accept the code. Without it, the server returns 302 (appears to succeed) but
does not elevate the session. Navigation is stateful and parent pages must be
visited before child pages resolve correctly.

### Full tree structure (access level 4444)

```
WEB-RC root  (branchnr=1, level=0)
├── global  (bn=1, lv=1)
│   ├── service  (bn=1, lv=2)
│   │   ├── software      language, version info
│   │   ├── cold-warm start   warm start 0, coldStSys 0
│   │   └── access codes  protect=3 (elevated), level 1/2/3 code hashes
│   └── structure  (bn=2, lv=2)
│       └── WEB            web interface settings
├── MCR-BMS  (bn=2, lv=1)
│   ├── timers  (bn=1, lv=2)               ← NEW at access level 3
│   │   ├── timer curVal      season/day readout
│   │   ├── timer chan. select.
│   │   │   ├── domHotWat.  → week program / special-non-occup. / special-occup. / priority
│   │   │   ├── heatc.1     → week program / special-non-occup. / special-occup. / priority
│   │   │   ├── heatc.2     → week program / special-non-occup. / special-occup. / priority
│   │   │   └── quiet       → week program / special-non-occup. / special-occup. / priority
│   │   ├── timer status      per-channel curStat / nxtStat / timeDiff
│   │   └── timer service     clock time + date
│   ├── heat source  (bn=2, lv=2)
│   │   └── heat pump 1
│   │       ├── curValue      HP1 live readings (outdoor, outlet/inlet, freq…)
│   │       ├── setpoints     setpointHC=26°C, setp.DHW=2°C
│   │       ├── function      setpoint limitation / boost / controller / Bivalence / Aquarea / busStatus
│   │       ├── status        operating status
│   │       ├── manual oper.
│   │       └── service       generalVal / sensor correction / terminal ass.
│   ├── buffer tank  (bn=3, lv=2)
│   │   ├── curValue          SP-zone1, buffer temp, boostZ1
│   │   ├── setpoints         SP-zone1=26.3°C, boostZ1=0.0
│   │   ├── function          boost / ext. demand / signal / buffer tank config
│   │   ├── status
│   │   ├── manual oper.
│   │   └── service           sensor correction / terminal ass.
│   ├── domHotWater  (bn=4, lv=2)
│   │   ├── curValue          SP-OTx, SP-NO, SP-DHWta, DHWtank
│   │   ├── setpoints         SP-OT1=52°C / SP-OT2=45°C / SP-OT3/4=45°C / SP-NO=2°C / SP-SNOT=2°C / SP-DHWta=45°C
│   │   ├── function          setpoint limitation / controller / therm. disinfection
│   │   ├── status
│   │   ├── manual oper.
│   │   └── service           therm. disinfection / sensor correction / terminal ass.
│   ├── heatCirc.  (bn=5, lv=2)
│   │   ├── heatC. 1
│   │   │   ├── curValue      outdoor, flow SP/actual, pump, Y-control
│   │   │   ├── setpoints     roomOT1-4=20°C, roomNO=20°C, roomSNOT=14°C, hCu-slope/exp, SP-Flow=26.3°C
│   │   │   ├── function      summer shutdown / setpoint limitation / controller / screed drying
│   │   │   ├── status
│   │   │   ├── manual oper.
│   │   │   └── service       generalVal / summer shutdown / HCu Adaptation / screed drying / sensor correction / terminal ass.
│   │   └── heatC. 2
│   │       ├── curValue      outdoor, flow SP/actual, pump, Y-control
│   │       ├── setpoints     roomOT1=35°C, roomOT2=27°C, roomNO=22°C, roomSNOT=2°C, SP-Flow=2°C
│   │       ├── function      summer shutdown / setpoint limitation / controller / screed drying
│   │       ├── status
│   │       ├── manual oper.
│   │       └── service
│   ├── trend  (bn=6, lv=2)              ← NEW at access level 3
│   │   └── trend 1–10  each with curValue / function (record config, controller) / status / service
│   ├── photovoltaics  (bn=7, lv=2)      PV curtailment setpoints
│   ├── Smart Grid  (bn=8, lv=2)         Smart Grid input states
│   └── Extended configur.  (bn=9, lv=2) ← NEW at access level 3
│       ├── hCu1 room compens.  (room compens.=0)
│       ├── hCu2 room compens.  (room compens.=0)
│       ├── HP Bivalence        (HP-Biv=0)
│       ├── domHotWater solar   (solColl=0)
│       ├── buffer solar        (solColl=0)
│       ├── buffer addHS/fireside (addHS-Fl=0)
│       ├── photovoltaics       (type-Pv=1, dem-DHW=1@50°C, dem-HC=1@50°C, minSwOfTm=10min)
│       └── Smart Grid          (inp1=0, Inp2=0)
├── interfaces  (bn=3, lv=1)
│   ├── Ethernet   IP=192.168.1.11, DHCP=off, MAC=00:1F:FC:80:0B:7F, host=hpm-800B7F
│   └── heatpumps  HP interface status
├── configuration  (bn=4, lv=1)
│   ├── inputs   term.17–28 (Pt1000 sensors + meter/mess + 0-10V)
│   ├── outputs  term01/03/05/07/09/11/13 (relays), term27/28 (0-10V)
│   └── switch   term.151=oMod-Sw, term.152/153/154=MS-W-pump1/2/3
├── diagrams  (bn=5, lv=1)    system diagram config (57133, easySetup=1, HP type MXF12D9E8-1)
└── system survey  (bn=6, lv=1)
    ├── controller    PAW-HPM1, H1.1.26, DIAGRAM 57133
    ├── heatC. 1      flow 22.8°C, SP-Flow 26.3°C, pump on, opStatus nom.oper.OT1
    ├── heatC. 2      flow 20.8°C, SP-Flow 2°C, pump off, opStatus red.oper.SNOT
    ├── domHotWater   DHWtank 49°C, SP-DHWta 45°C, opStatus nom.oper.OT2
    ├── buffer tank   buffer1 23°C, SP-zone1 26.3°C
    ├── heat pump 1   freq=0Hz, StatEHeat=9kW, OP-OFF/ON=on, OP-HEAT=on
    ├── inputs        term.18=22.8°C (HC1 flow), term.19=20.8°C (HC2 flow), term.22=23.0°C (buffer)
    └── outputs       term03=1, term07=1, term09=1 (others=0)
```

### Timer channel programs (live data)

The timers section controls occupancy periods (OT1/OT2 = occupied, NO = normal,
SNOT = special non-occupancy, SO = special occupancy) for each channel.

**DHW** — week program group 3:
- Monday: 2 OT periods: OT1 11:00–14:00, OT2 14:00–11:00
- Special non-occupancy: 22.02.25–28.02.25
- Current status: OT2, next OT1 in 700 min

**HC1 (floor heating)** — week program group 3:
- Monday: OT1 21:00–06:00, OT2 06:00–21:00
- No special periods active
- Current status: OT1, next OT2 in 400 min

**HC2 (pool heating)** — week program group 3:
- Monday: 4 OT periods (10:00–16:30, 16:30–01:00, 01:00–05:00, 05:00–10:00)
- Special non-occupancy (winter standby): **30.08.25–25.05.26** ← pool off season
- Current status: SNOT (in winter standby — pool season ends 25 May 2026)

**Quiet mode** — week program group 0, all days OT1 24h (quiet enabled 24/7)

### Terminal assignments

**Sensors (inputs)**

| Terminal | Type | Current reading | Assignment |
|----------|------|----------------|------------|
| term.17 | Pt1000 | 0.0°C | (unused/disconnected) |
| term.18 | Pt1000 | 22.8°C | HC1 flow sensor |
| term.19 | Pt1000 | 20.8°C | HC2 flow sensor |
| term.20–21, 23–24 | Pt1000 | 0.0°C | unused |
| term.22 | Pt1000 | 23.0°C | buffer tank sensor |
| term.25–26 | meter/mess | 0 | pulse meters (unused) |
| term.27 | 0–10V | 0.2% | (near zero) |
| term.28 | 0–10V | 0.1% | (near zero) |

**Relays (outputs)**

| Terminal | srcVal | termVal |
|----------|--------|---------|
| term01 | 0 | 0 (off) |
| term03 | 1 | 1 (on) |
| term05 | 0 | 0 (off) |
| term07 | 1 | 1 (on) |
| term09 | 1 | 1 (on) |
| term11 | 0 | 0 (off) |
| term13 | 0 | 0 (off) |

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
