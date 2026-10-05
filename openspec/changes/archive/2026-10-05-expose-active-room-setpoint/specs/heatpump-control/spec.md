## ADDED Requirements

### Requirement: Status includes each heating circuit's operating period and active room setpoint
The status returned by `GET /api/v1/status` SHALL include, for each heating circuit, the operating period in force and the room setpoint for that period, read from the view pages the status already fetches and without WEB-RC navigation.

For `heating_circuit_1` (`v30.rsp`) and `heating_circuit_2` (`v3.rsp`):

- `operating_status`: the operating-mode string as the device shows it, whitespace-collapsed (HC1 id 6, HC2 id 20), e.g. `nom. oper. OT1`;
- `timer_status`: the timer string as the device shows it, whitespace-collapsed (HC1 id 8, HC2 id 22), e.g. `timer-OT1 ----------`;
- `period`: the period in force, derived from `operating_status`, as one of `OT1`, `OT2`, `OT3`, `OT4`, `NO`, `SNOT`;
- `active_room_setpoint`: the room setpoint for `period`, in °C, taken from the same view page: `OT1` → `room_ot1`, `OT2` → `room_ot2`, `NO` → `room_setpoint` (roomNO).

`period` SHALL be derived from the operating status rather than the timer status, because the operating status also reflects the system mode switch (e.g. holiday forces the NO setpoints regardless of the timer). An operating status whose final token is not one of the listed periods SHALL give `period = null`; the service SHALL NOT infer a period from partial matches.

`active_room_setpoint` SHALL be `null` when `period` is `null`, when `period` is `OT3`, `OT4` or `SNOT` (whose setpoints are not on the view page), or when the matching view-page value is missing. The service SHALL NOT perform WEB-RC navigation to resolve it.

All four fields are additive and best-effort. A missing or unrecognised value SHALL be `null` and SHALL NOT fail the status request or change any other field.

`room_setpoint` keeps its value and meaning: it is the non-occupation-time setpoint `roomNO`, not a nominal or default setpoint.

#### Scenario: Circuit in occupation time 1
- **WHEN** HC1's operating status reads `nom. oper. OT1` and its view page shows `roomOT1 18.0 °C`
- **THEN** `heating_circuit_1.period` is `OT1`, `active_room_setpoint` is `18.0`, and `operating_status` / `timer_status` carry the device strings

#### Scenario: Circuit in occupation time 2
- **WHEN** HC2's operating status reads `nom. oper. OT2` and its view page shows `roomOT2 27.0 °C`
- **THEN** `heating_circuit_2.period` is `OT2` and `active_room_setpoint` is `27.0`

#### Scenario: Circuit in special non-occupation time
- **WHEN** HC2's operating status reads `red. oper. SNOT` and its timer status reads `timer-SNOT ----`
- **THEN** `heating_circuit_2.period` is `SNOT`, `active_room_setpoint` is `null`, and the raw strings are returned as shown

#### Scenario: Unrecognised operating status
- **WHEN** a circuit's operating status is a string whose final token is not a known period (e.g. a frost-protection or off state)
- **THEN** `period` and `active_room_setpoint` are `null`, `operating_status` carries the raw string, and the response is HTTP 200 with every other field populated as before

#### Scenario: Operating status absent
- **WHEN** a circuit's view page lacks the operating-status or timer parameter
- **THEN** the corresponding fields are `null` and the rest of the status is unaffected

#### Scenario: No extra device traffic
- **WHEN** `GET /api/v1/status` is called
- **THEN** the service fetches the same view pages as before this change and issues no `menue.rsp`, `info.rsp` or `execset.rsp` request
