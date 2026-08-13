## Why

WEB-RC writes (`execset.rsp`) address a parameter only by `branchnr`/`level`, which the device
resolves **relative to the page the session last navigated to** — nothing in the write identifies
the circuit. HC1 and HC2 setpoints pages are both `(bn=2, lv=4)`, and both setpoint-limitation
pages are both `(bn=2, lv=5)`. When navigation lands somewhere unintended, the write silently
targets the wrong parameter, and the device returns 302 either way so nothing surfaces.

This has already corrupted live heating twice, confirmed from Home Assistant recorder history:

| When | Symptom |
|---|---|
| 2026-08-06 11:42 | HC1 `roomOT2` = 34.0 — the HC2 pool flow floor. Overheated floor heating for 3 days until corrected manually on 2026-08-09 17:42. |
| 2026-08-02 06:58 | HC2 `roomOT2` = 35.0 — the pool floor in force at that time. Reverted 2026-08-02 21:07. |

The HC2 flow-limit write sequence is `maxFl`@bn3=65.0, `minFl`@bn2=`<floor>`, `active`@bn1=1.
Landing that on a *setpoints* page maps bn1/2/3 onto `roomOT1`/`roomOT2`/`roomOT3`. The device
range-rejects `roomOT1`←1.0 and `roomOT3`←65.0, so only the middle write lands — which is why
`roomOT2` alone visibly moves. A Node-RED flow drives the pool floor many times a day, giving
the race dozens of daily chances to fire.

## What Changes

- **Verify the write target before every `execset`.** Every WEB-RC page carries a self-identifying
  title row (`heatCirc1 setpoints`, `heatCirc2 F-SP.limit`, …). Parse it and require an exact match
  for the intended circuit *and* page. Abort with an error rather than writing to an unverified page.
- **Stop auto-retrying WEB-RC requests across a re-login.** `SessionManager.request()` currently
  re-authenticates on session expiry and blindly re-sends the same request; `login()` resets the
  device to root and restores no navigation, so the resent request is misaddressed. WEB-RC callers
  opt out of that retry and re-run navigate+write from scratch instead. **BREAKING** for internal
  callers of `SessionManager.request()` that relied on transparent retry.
- **Detect navigation that drifts to the wrong circuit.** `_webrc_navigate` matches menu items by
  label, and HC1/HC2 have identical child labels (`setpoints`, `function`, `setpoint limitation`),
  so a mid-walk re-login can land on the wrong circuit without raising. Confirm the final page
  identity at the end of navigation, for reads as well as writes.
- **Read back and verify after writing**, so a rejected or misdirected write surfaces as an error
  instead of a silent success.
- **Range-check all flow-limit writes.** `_execset_flowlimit` validates only `minFl` today, and that
  check is itself context-relative, so it offers no protection on a wrong page.

## Capabilities

### New Capabilities
<!-- None. This hardens existing behaviour; no new user-facing capability. -->

### Modified Capabilities
- `session-management`: the "Session expires mid-operation" behaviour changes — WEB-RC requests must
  no longer be transparently retried after re-authentication; and navigation must confirm it landed
  on the intended page, strengthening "Re-establish WEB-RC navigation context before each operation".
- `heating-circuit-setpoints`: setpoint writes must verify page identity before writing and verify
  the value after writing; a write to an unverified page is rejected.
- `heatpump-control`: the HC2 flow-temperature limitation read/write must verify page identity, and
  all three parameters (`active`, `minFl`, `maxFl`) must be range-checked, not just `minFl`.

## Impact

- `heatpump-api/app/session.py` — `request()` gains an opt-out of retry-after-re-auth; expiry during
  a no-retry request raises so the caller can restart the whole operation.
- `heatpump-api/app/client.py` — `_webrc_navigate` verifies the landed page; `set_hc_setpoint`,
  `get_hc_setpoints`, `set_flow_limit`, `get_flow_limit` and `_execset_flowlimit` verify target
  identity before writing and read back after.
- `heatpump-api/app/parsers.py` — new parser for the page title/identity row.
- No REST API surface change; new failure modes surface as existing 502 responses.
- No Home Assistant package change. Reducing the Node-RED write frequency remains a useful
  mitigation but is not a fix and is out of scope here.
