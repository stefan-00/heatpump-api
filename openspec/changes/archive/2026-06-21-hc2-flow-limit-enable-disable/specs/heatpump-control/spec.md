## MODIFIED Requirements

### Requirement: Read and write the HC2 flow-temperature limitation

The service SHALL read and write the HC2 "setpoint limitation" function on the HPM WEB-RC interface. It SHALL navigate to the limitation page by matching menu link labels from root — `MCR-BMS → heatCirc. → heatC. 2 → function → setpoint limitation` — never by hard-coded `(branchnr, level)` pairs, and SHALL serialise this navigation with all other WEB-RC navigation under a single lock so concurrent operations on the stateful session do not interfere.

For reads, the service SHALL parse the `active`, `minFl`, and `maxFl` values (device params `2.5.2.3.6.1`/`.2`/`.3`) from the limitation page HTML.

For writes, the service SHALL set each target parameter via `POST /execset.rsp` using the limitation page's branch/level (position within the page: `active`, `minFl`, `maxFl`). It SHALL support writing `active` (enable or disable) independently, without requiring a `minFl`/`maxFl` write. When a flow floor is being written, the service SHALL pre-validate it against the range reported by `info.rsp` for that parameter and against the device constraint `maxFl > minFl` before writing, and SHALL write `maxFl` before `minFl` so the floor never transiently exceeds the cap. Because the device returns a 302 redirect for both success and failure, the service SHALL rely on this pre-validation rather than the response status to reject invalid writes.

#### Scenario: Read the current limitation
- **WHEN** the service reads the HC2 flow limitation
- **THEN** it navigates by label to the setpoint-limitation page and returns the parsed `active`, `minFl`, and `maxFl` values

#### Scenario: Write the limitation with set-and-enable
- **WHEN** the service applies a flow-floor change for HC2 without an explicit enabled state
- **THEN** it writes `maxFl` (strictly greater than the floor), then `minFl`, then `active = 1` via `execset`, after validating each value against its `info.rsp` range and the `maxFl > minFl` constraint

#### Scenario: Toggle the enabled state only
- **WHEN** the service is asked to enable or disable the limitation without a new floor
- **THEN** it writes only the `active` parameter (`1` or `0`) via `execset` and does not write `minFl`/`maxFl`

#### Scenario: Pre-validation rejects an invalid write
- **WHEN** a requested limitation value is outside the device's `info.rsp` range, or would make `maxFl <= minFl`
- **THEN** the service SHALL NOT issue the `execset` request and SHALL surface a validation error
