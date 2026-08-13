## ADDED Requirements

### Requirement: Verify the landed WEB-RC page identity after navigation

After completing a navigation path, the service SHALL parse the page's self-identifying title row and SHALL confirm it matches the intended target before the page is read from or written to.

Every WEB-RC page renders a self-identifying title as the first row of its `<!-- start_mainpane -->`
block (for example `heatCirc1 setpoints`, `heatCirc2 F-SP.limit`). Because `(branchnr, level)`
coordinates collide across circuits — HC1 and HC2 setpoints pages are both `(bn=2, lv=4)`, and both
setpoint-limitation pages are both `(bn=2, lv=5)` — this title is the only evidence of which page a
navigation actually reached.

Matching SHALL be case-insensitive and SHALL require both a circuit marker (`heatcirc1` or `heatcirc2`) and a page
marker (`setpoints` or `f-sp.limit`) to be present, rather than exact equality with a full string, so
that cosmetic firmware differences do not reject valid pages.

When the title does not match, the service SHALL NOT read values from or write values to the page. It
SHALL log the observed title at WARNING level and SHALL surface a 502 error.

#### Scenario: Navigation reaches the intended page
- **WHEN** the service navigates the HC2 setpoint-limitation path and the landed page's title row is `heatCirc2 F-SP.limit`
- **THEN** verification passes and the operation proceeds

#### Scenario: Navigation drifts to the wrong circuit
- **WHEN** the service navigates intending HC2 setpoints but the landed page's title row is `heatCirc1 setpoints`
- **THEN** the service SHALL NOT write to or return values from that page, SHALL log the observed title at WARNING level, and SHALL return 502

#### Scenario: Navigation drifts to the wrong page within the correct circuit
- **WHEN** the service navigates intending the HC2 setpoint-limitation page but the landed page's title row is `heatCirc2 setpoints`
- **THEN** verification fails and the service returns 502 without issuing any write

#### Scenario: Title row is absent or unparseable
- **WHEN** the landed page contains no parseable mainpane title row
- **THEN** verification fails, and the service returns 502 rather than assuming the page is correct

### Requirement: Guard the window between navigation and write with the session generation

Each WEB-RC operation SHALL capture the session generation after its navigation completes and SHALL confirm the generation is unchanged immediately before **each** `execset` request it issues.

A re-authentication resets the device's navigation position to root without restoring the previous
path, so any `(branchnr, level)` write issued afterwards is misaddressed. The service SHALL maintain a
monotonically increasing session generation counter that increments on every successful login.

Where an operation writes several parameters in sequence, the check SHALL be repeated before every
individual write, not only before the first.

If the generation has changed, the service SHALL abandon the write and SHALL NOT issue the `execset`
request against the stale navigation context.

#### Scenario: Generation unchanged across a multi-parameter write
- **WHEN** the service writes `maxFl`, then `minFl`, then `active` and no re-authentication occurs
- **THEN** every generation check passes and all three writes are issued

#### Scenario: Re-authentication occurs partway through a multi-parameter write
- **WHEN** the session is re-authenticated after `maxFl` is written but before `minFl` is written
- **THEN** the service SHALL NOT issue the `minFl` or `active` writes against the stale context, and SHALL restart the operation from navigation or surface an error

## MODIFIED Requirements

### Requirement: Pass session on every request
The service SHALL append `sessionid=<value>` as a URL query parameter to every HTTP request sent to the heatpump web UI. The session token SHALL NOT be sent as a cookie or HTTP header.

Requests SHALL declare whether they may be transparently retried after a re-authentication. Requests whose correctness depends on the device's current WEB-RC navigation position — all `menue.rsp` navigation steps, `info.rsp` range reads, and `execset.rsp` writes — SHALL opt out of transparent retry, because a re-authentication resets that position and the resent request would then address a different parameter. Retry-eligible requests (the stateless `v*.rsp` status pages) retain the existing retry-once behaviour.

#### Scenario: Authenticated request is made
- **WHEN** the client sends any request to the heatpump (status read, parameter set, etc.)
- **THEN** the request URL includes `?sessionid=<stored_value>` or `&sessionid=<stored_value>` appended to whatever other parameters are present

#### Scenario: Session expires mid-operation on a retry-eligible request
- **WHEN** a retry-eligible proxied request to the web UI returns a 302 redirect to the entry/login page (`enter.rsp` or `login.rsp`) or an HTTP 401
- **THEN** the service re-authenticates using the two-step flow, stores the new `sessionid`, retries the original request exactly once, and returns the result to the caller

#### Scenario: Session expires mid-operation on a navigation-dependent request
- **WHEN** a request that has opted out of transparent retry returns a 302 redirect to the entry/login page or an HTTP 401
- **THEN** the service re-authenticates and stores the new `sessionid` so the session is usable again, but SHALL NOT resend the original request; it SHALL raise so the caller can re-run the whole navigate-and-act operation against the fresh session

#### Scenario: Re-authentication fails after session expiry
- **WHEN** the retry after re-authentication also fails
- **THEN** the service SHALL return a 502 error to the caller and log the failure; it SHALL NOT retry further

### Requirement: Re-establish WEB-RC navigation context before each operation
The WEB-RC server maintains a per-session navigation stack. Before any WEB-RC read or write, the service SHALL navigate the full path from the WEB-RC root to the target page by GETting each ancestor `menue.rsp` step in order. The root SHALL always be reset to `branchnr=1&level=0` before traversing the path.

Because HC1 and HC2 expose identical child menu labels (`setpoints`, `function`, `setpoint limitation`), label matching alone cannot detect a walk that has drifted into the wrong circuit's subtree. Navigation SHALL therefore confirm the identity of the page it landed on before the caller uses it, for reads as well as writes.

An operation whose navigation or subsequent device interaction fails because the session expired SHALL be retried once in full — re-running the navigation from root before acting — rather than resending any individual request. Retry SHALL apply only to session-expiry failures and SHALL NOT apply to page-identity verification failures.

#### Scenario: Read HC2 setpoints after navigating to HC1
- **WHEN** a request for HC2 setpoints follows a request that left the server in HC1 context
- **THEN** the service resets to level=0 and re-navigates the full HC2 path before fetching the setpoints page, returning correct HC2 data

#### Scenario: Write setpoint requires full path traversal
- **WHEN** `execset.rsp` is called to update a setpoint
- **THEN** the service has already traversed the full navigation path to the setpoints page in the current request, so the server-side context matches the `branchnr` and `level` values in the write POST

#### Scenario: Session expires during navigation
- **WHEN** the session expires part-way through a navigation walk
- **THEN** the service SHALL NOT continue the walk on the re-authenticated session, and SHALL restart the whole operation from root exactly once

#### Scenario: Verification failure is not retried
- **WHEN** navigation completes but the landed page's identity does not match the intended target
- **THEN** the service SHALL surface a 502 without retrying, since a retry would repeat the same deterministic mismatch
