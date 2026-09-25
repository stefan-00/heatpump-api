# TODO

Open ideas not yet turned into openspec changes. Each entry says why it matters and
where to start; move it into `openspec/changes/` once it is picked up.

## 1. Use the HPM's built-in PV function for solar-surplus heating

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
  it should, since HC1 regulates its own flow, but verify with the `HC1 Valve Position`
  sensor (`Y-contr`).
