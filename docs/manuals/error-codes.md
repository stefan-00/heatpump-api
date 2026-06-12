# Error Codes Reference

Sources:
- HP unit error codes: `import/monobloc-service-manual.pdf` — Troubleshooting section (pp. 74–75)
- HPM controller error messages: `import/HPM_HBInstIB_en.pdf` — Error message appendix

---

## HP Unit Error Codes (WH-MXF09/12)

Error codes are displayed on the HPM status screen and in the `v21.rsp` page.

### H-series — Sensor and communication faults

| Code | Detection delay | Description |
|---|---|---|
| H00 | — | No abnormality (normal status) |
| H12 | 90 s after power-on | Indoor/outdoor unit capacity mismatch |
| H15 | 5 s | Compressor discharge temperature sensor fault |
| H23 | 5 s | Indoor refrigerant liquid temperature sensor fault |
| H42 | — | Compressor low pressure fault |
| H62 | 1 min | Water flow switch fault |
| H63 | 4× in 20 min | Refrigerant low pressure protection |
| H64 | 5 s | Refrigerant high pressure protection |
| H70 | 60 s | Backup heater overload protector (OLP) trip |
| H72 | 5 s | Tank temperature sensor fault |
| H76 | — | Indoor unit – remote control communication fault |
| H90 | > 1 min after start | Indoor/outdoor unit abnormal communication |
| H91 | 60 s | Tank heater overload protector (OLP) trip |
| H95 | — | Indoor/outdoor unit wrong connection |
| H98 | — | Outdoor unit high pressure overload |
| H99 | — | Indoor heat exchanger freeze prevention activated |

### F-series — Protection and trip events

| Code | Detection trigger | Description |
|---|---|---|
| F12 | 4× in 20 min | Pressure switch trip |
| F14 | 4× in 20 min | Outdoor compressor abnormal revolution |
| F15 | 4× in 30 min | Outdoor fan motor lock |
| F16 | 3× in 20 min | Total running current exceeded |
| F20 | 4× in 30 min | Compressor overheating |
| F22 | 3× in 30 min | IPM (inverter power module) overheating |
| F23 | 7× continuously | Outdoor DC peak protection |
| F24 | 2× in 20 min | Refrigeration cycle abnormality |
| F25 | 4× in 30 min | Cooling/heating cycle changeover fault |
| F27 | 1 min | Pressure switch protection (secondary) |
| F36 | 5 s | Outdoor air temperature sensor fault |
| F37 | 5 s | Indoor water inlet temperature sensor fault |
| F40 | 5 s | Outdoor discharge pipe temperature sensor fault |
| F41 | 4× in 10 min | PFC (power factor correction) control fault |
| F42 | 5 s | Outdoor heat exchanger temperature sensor fault |
| F43 | 5 s | Outdoor defrost sensor fault |
| F45 | 5 s | Indoor water outlet temperature sensor fault |
| F46 | — | Outdoor current transformer open circuit |
| F48 | 5 s | Outdoor EVA outlet temperature sensor fault |
| F49 | 5 s | Outdoor bypass outlet temperature sensor fault |
| F95 | — | Cooling high pressure overload |

---

## HPM Controller Error Messages (PAW-HPM)

These messages appear in the HPM status/alarm display, separate from the HP unit codes above.

### FP — Frost protection alarms

| Message | Description |
|---|---|
| FP-system | Frost protection triggered on system/hydraulic circuit |
| FP-stor | Frost protection triggered on storage/buffer |

### BP — Boiler protection alarms

| Message | Description |
|---|---|
| BP-frRoom | Boiler protection — frost in room sensor circuit |
| BP-heRoom | Boiler protection — overheating in room sensor circuit |

### Xw — External signal / demand errors

| Message | Description |
|---|---|
| Xw-HP | External demand signal fault on heat producer |
| Xw-HC | External demand signal fault on heating circuit |
| Xw-DHW | External demand signal fault on DHW circuit |

### TI — Temperature/input sensor errors

| Message | Description |
|---|---|
| TI-out | Outdoor temperature sensor fault |
| TI-buff | Buffer tank sensor fault |
| TI-dhw | DHW tank sensor fault |
| TI-room | Room temperature sensor fault |
| TI-solar | Solar collector sensor fault |

---

## Notes

- HP unit error codes (H/F series) are read from the `v21.rsp` page — they reflect the state reported by the mono-bloc outdoor unit to the HPM.
- HPM controller error messages are separate and originate from the HPM's own logic (sensor reads, protection thresholds, external signal monitoring).
- "Detection trigger" for F-series codes means the fault must occur the stated number of times within the stated window before the error is latched.
