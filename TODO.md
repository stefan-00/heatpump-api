# TODO

Open ideas not yet turned into openspec changes. Each entry says why it matters and
where to start; move it into `openspec/changes/` once it is picked up.

## 1. Expose the heat-source and buffer values the pool analysis was missing

**Why.** During the 2026-09 end-of-season pool boost (HC2 flow floor raised 34 → 42 °C)
the compressor stayed at ~38 Hz with the outlet at 36–38 °C, i.e. never reached the
42 °C the pool was asking for. Across a week the compressor frequency tracked outdoor
temperature almost exactly (3.6 °C → 50 Hz, 11 °C → 37–38 Hz, 15–21 °C → 31–32 Hz)
regardless of the HC2 floor. Two explanations fit, and the API cannot currently tell
them apart:

- the HPM asks the heat pump for ~37 °C (buffer demand logic caps it) — limit is in the
  controller, fixable by configuration;
- the HPM asks for more (~46 °C with the buffer's `boost HC2 10 %`) and the heat pump
  cannot deliver — limit is the unit.

The pool only got ~2 kW at 42 °C. Also wanted: the mixing-valve position, to graph how
HC1 and HC2 compete for buffer heat.

**What to add** (IDs from `docs/hpm-ui-surface.md` and `research/webrc_deep_dump.md`):

| Value | Source | Notes |
|---|---|---|
| HC setpoint sent to the heat pump | `v21.rsp` id 109 | the decisive one for the question above |
| HP operating state / heat demand | `v21.rsp` id 88 / 89 | text |
| Defrost active | `v21.rsp` id 124 | explains short frequency dips |
| Buffer temperature | `v100100.rsp` id 61 | |
| Buffer setpoint (zone 1) | `v100100.rsp` id 59 | compare with HC2 flow setpoint |
| HC2 pump speed | `v3.rsp` id 30 | |
| HC1 / HC2 mixing valve `Y-contr.` | WEB-RC `heatCirc. → heatC. N → status` | WEB-RC only, not on the v*.rsp pages — must go through the navigation lock and page verification like the setpoint reads |

The v*.rsp values are plain status reads and belong in `GET /api/v1/status`. `Y-contr`
needs WEB-RC navigation, so consider a separate, slower-polled endpoint rather than
putting WEB-RC traffic on the 30 s status poll. Then add the sensors to
`homeassistant/packages/heatpump.yaml` (they flow to InfluxDB via the existing
`sensor.heatpump_*` / `sensor.hc*` globs) and a panel to the Heat Pump dashboard.

## 2. Use the HPM's built-in PV function for solar-surplus heating

**Why.** The pool (and the house) should be heated with surplus solar rather than
exported at ~1.2–1.5 SEK/kWh. The HPM already has this: `MCR-BMS → photovoltaics`
raises the heating demand to a fixed temperature while a PV signal is active. It is
configured but not wired:

- `type photovoltaics`: `type-Pv 1`, `dem-HC 1`, `dem-DHW 1`
- `temperatures`: `dem-HC 50 °C`, `dem-DHW 50 °C`
- `sequence timing`: `minSwOfTm 10 min`
- `service → terminal ass.`: **`rel-pv 0`** — no input assigned, so it never triggers

`Smart Grid` is an alternative route with two inputs (`inp1`/`inp2`, currently 0):
operating state 3 = boost 10 %, operating state 4 = demand 50 °C.

**Where to start.**
- Find in `import/HPM_HBInstIB_en.pdf` which terminal types can be assigned to
  `rel-pv` / the SG inputs, and whether a potential-free contact is expected.
- Hardware: a relay (e.g. a Shelly) on that input, switched by HA from Sigen surplus
  (exporting, battery full). That is installer-level wiring, not software.
- Decide the demand temperature: 50 °C buffer lowers COP noticeably. Probably keep
  `dem-DHW` enabled (hot water is a good heat store) but lower `dem-HC`.
- Whether HC1 floor heating tolerates a hotter buffer depends on its mixing valve —
  it should, since HC1 regulates its own flow, but verify with the `Y-contr` data from
  item 1.
