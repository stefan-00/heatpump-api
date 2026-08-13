## ADDED Requirements

### Requirement: Skip device writes that would not change a value

Before issuing any `execset`, the service SHALL compare the requested value with the value currently shown on the verified page, and SHALL skip the write when they are equal within the same tolerance used for read-back confirmation. Skipping SHALL be logged.

A write whose requested value already equals the value the device reports **cannot be verified**: the
read-back afterwards passes whether the write landed on the intended parameter, on a different
parameter, or nowhere at all. Such writes therefore carry risk with no benefit.

An operation in which every requested value is already satisfied SHALL issue no `execset` at all and
SHALL still return success with the current confirmed state, so callers cannot distinguish a skipped
no-op from an applied write.

Consequently every `execset` the service does issue changes the page, which is what makes read-back
confirmation a real check rather than a tautology.

#### Scenario: Flow floor already at the requested value
- **WHEN** a flow-limit write requests `minFl = 34.0` and the verified limitation page already shows `minFl = 34.0`, with the limitation already enabled
- **THEN** the service SHALL issue no `execset` requests and SHALL return 200 with the current state

#### Scenario: Floor matches but the limitation is disabled
- **WHEN** a flow-limit write requests a floor that already matches, but `active` is currently `0` and the request implies enabling
- **THEN** the service SHALL skip the `minFl` and `maxFl` writes and SHALL still write `active`

#### Scenario: Value differs, so the write is issued and verifiable
- **WHEN** a flow-limit write requests a floor different from the current value
- **THEN** the service SHALL issue the write, and the read-back afterwards SHALL prove it landed by showing the new value

## MODIFIED Requirements

### Requirement: Read and write the HC2 flow-temperature limitation

The service SHALL read and write the HC2 "setpoint limitation" function on the HPM WEB-RC interface. It SHALL navigate to the limitation page by matching menu link labels from root — `MCR-BMS → heatCirc. → heatC. 2 → function → setpoint limitation` — never by hard-coded `(branchnr, level)` pairs, and SHALL serialise this navigation with all other device requests under a single lock so concurrent operations on the stateful session do not interfere.

Label matching alone is insufficient to establish the target, because HC1 exposes an identically labelled `function → setpoint limitation` path and both circuits' limitation pages occupy the same `(bn=2, lv=5)` coordinates. Before reading values from or writing values to the limitation page, the service SHALL confirm the page identifies as the HC2 limitation page, and SHALL re-confirm that identity immediately before the first write. A write SHALL NOT be issued against an unverified page. Detecting the page by the presence of `active`/`minFl`/`maxFl` fields alone SHALL NOT be treated as verification, because HC1's limitation page carries the same fields.

For reads, the service SHALL parse the `active`, `minFl`, and `maxFl` values (device params `2.5.2.3.6.1`/`.2`/`.3`) from the verified limitation page HTML. If the page's expected values cannot be parsed, the service SHALL surface an error and SHALL NOT substitute defaults for the missing values in any subsequent write decision.

For writes, the service SHALL set each target parameter via `POST /execset.rsp` using the limitation page's branch/level (position within the page: `active`, `minFl`, `maxFl`). It SHALL support writing `active` (enable or disable) independently, without requiring a `minFl`/`maxFl` write. Writes whose requested value already matches the device's current value SHALL be skipped. When a flow floor is being written, the service SHALL pre-validate it against the range reported by `info.rsp` for that parameter and against the device constraint `maxFl > minFl` before writing, and SHALL write `maxFl` before `minFl` so the floor never transiently exceeds the cap. Every parameter written — `active` and `maxFl` as well as `minFl` — SHALL be range-validated before it is written. Because the device returns a 302 redirect for both success and failure, the service SHALL rely on this pre-validation rather than the response status to reject invalid writes, and SHALL additionally read the page back after writing to confirm all written parameters hold their requested values.

#### Scenario: Read the current limitation
- **WHEN** the service reads the HC2 flow limitation
- **THEN** it navigates by label to the setpoint-limitation page, confirms the page identifies as the HC2 limitation page, and returns the parsed `active`, `minFl`, and `maxFl` values

#### Scenario: Write the limitation with set-and-enable
- **WHEN** the service applies a flow-floor change for HC2 without an explicit enabled state
- **THEN** it confirms the page identity, re-confirms it immediately before writing, then writes `maxFl` (strictly greater than the floor), then `minFl`, then `active = 1` via `execset`, skipping any of those whose value already matches, after validating each value against its `info.rsp` range and the `maxFl > minFl` constraint, and finally reads back to confirm

#### Scenario: Toggle the enabled state only
- **WHEN** the service is asked to enable or disable the limitation without a new floor
- **THEN** it confirms the page identity and writes only the `active` parameter (`1` or `0`) via `execset`, does not write `minFl`/`maxFl`, and reads back to confirm `active`

#### Scenario: Write target cannot be verified
- **WHEN** the page reached for a limitation write does not identify as the HC2 limitation page, either after navigation or on re-confirmation immediately before writing
- **THEN** the service SHALL NOT issue any `execset` request and SHALL surface a 502

#### Scenario: Current values cannot be parsed before a write
- **WHEN** the limitation page's `active`/`minFl`/`maxFl` values cannot be parsed
- **THEN** the service SHALL surface an error and SHALL NOT proceed to write using default or assumed current values

#### Scenario: Pre-validation rejects an invalid write
- **WHEN** a requested limitation value is outside the device's `info.rsp` range, or would make `maxFl <= minFl`
- **THEN** the service SHALL NOT issue the `execset` request and SHALL surface a validation error

#### Scenario: Write does not take effect
- **WHEN** the read-back after a limitation write shows a value other than the one requested
- **THEN** the service SHALL surface a 502 rather than reporting success
