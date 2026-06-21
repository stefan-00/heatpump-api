## ADDED Requirements

### Requirement: Read and write the HC2 flow-temperature limitation

The service SHALL read and write the HC2 "setpoint limitation" function on the HPM WEB-RC interface. It SHALL navigate to the limitation page by matching menu link labels from root — `MCR-BMS → heatCirc. → heatC. 2 → function → setpoint limitation` — never by hard-coded `(branchnr, level)` pairs, and SHALL serialise this navigation with all other WEB-RC navigation under a single lock so concurrent operations on the stateful session do not interfere.

For reads, the service SHALL parse the `active`, `minFl`, and `maxFl` values (device params `2.5.2.3.6.1`/`.2`/`.3`) from the limitation page HTML.

For writes, the service SHALL set each target parameter via `POST /execset.rsp` using the limitation page's branch/level (position within the page: `active`, `minFl`, `maxFl`), and SHALL pre-validate each value against the range reported by `info.rsp` for that parameter and against the device constraint `maxFl > minFl` before writing. Because the device returns a 302 redirect for both success and failure, the service SHALL rely on this pre-validation rather than the response status to reject invalid writes.

#### Scenario: Read the current limitation
- **WHEN** the service reads the HC2 flow limitation
- **THEN** it navigates by label to the setpoint-limitation page and returns the parsed `active`, `minFl`, and `maxFl` values

#### Scenario: Write the limitation with set-and-enable
- **WHEN** the service applies a flow-limit change for HC2
- **THEN** it writes `minFl`, a `maxFl` strictly greater than `minFl`, and `active = 1` via `execset` against the limitation page's branch/level, after validating each value against its `info.rsp` range and the `maxFl > minFl` constraint

#### Scenario: Pre-validation rejects an invalid write
- **WHEN** a requested limitation value is outside the device's `info.rsp` range, or would make `maxFl <= minFl`
- **THEN** the service SHALL NOT issue the `execset` request and SHALL surface a validation error
