# TODO

Open ideas not yet turned into openspec changes. Each entry says why it matters and
where to start; move it into `openspec/changes/` once it is picked up.

## 1. Use the HPM's built-in PV function for solar-surplus heating

**Why.** Surplus solar should go into the pool and the hot water instead of being exported.
**This is about convenience, not money.** Measured 2026-10-14: midday export is worth only
~0.65 SEK/kWh, not the 1.2–1.5 once assumed here. Surplus and the house's heat demand
barely overlap — large surplus in summer, when only the pool and hot water need heat, none
from November to February. As space heating that is under 100 SEK a year. What the relay
does buy is the pool heated on surplus without hand-tuning, and hot water charged on
surplus without moving the DHW timer by hand twice a year. Figures and reasoning:
`kolarbacken35/docs/energy.md`, "The battery already moves the heat pump's load".

The HPM already has this: `MCR-BMS → photovoltaics` raises the heating demand to a fixed
temperature while a PV signal is active. It is configured but not wired:

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
  it should, since HC1 regulates its own flow, but verify with the `HC1 Valve Position`
  sensor (`Y-contr`).

## 2. Find out what caps the compressor frequency

**Why.** With a 50 °C demand that was never reached, the compressor held a flat
43–44 Hz for 3+ hours (outdoor ~11–13 °C). On colder nights earlier that week it ran at
50–53 Hz (outdoor 3–4 °C), and across the week frequency tracked outdoor temperature
almost exactly (3.6 °C → 50 Hz, 11 °C → 37–38 Hz, 15–21 °C → 31–32 Hz). So the maximum
appears to be set from outdoor temperature rather than from unmet demand. At 50 °C the
pool heat exchanger is no longer the bottleneck (≈5 kW into the pool vs ≈2 kW at 42 °C),
so this cap is now what limits pool heating.

**Where to start.** Nothing in `research/webrc_deep_dump.md` looks like a frequency
limit — the HPM seems to pass only a setpoint to the Aquarea. Look in the Aquarea
service manual (`import/monobloc-service-manual.pdf`) for outdoor-temperature-dependent
maximum frequency, a capacity/"eco" setting, or demand-control input. Note that quiet
mode is **not** it: it only lowers fan speed by 80 rpm, and the unit reports
`Quiet 0` / `Quiet off`.
