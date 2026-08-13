## 1. Page-identity parsing

- [x] 1.1 Add `parse_page_title(html) -> str | None` to `parsers.py`, returning the first `<tr>` row text inside the `<!-- start_mainpane -->` block, whitespace-normalised, reusing the existing `_mainpane()` helper
- [x] 1.2 Add a `PageIdentity` description of the expected target (circuit marker + page marker) and a `page_matches(title, circuit, page) -> bool` check that is case-insensitive and requires both markers, per design decision 1
- [x] 1.3 Define the marker constants: circuits `heatcirc1`/`heatcirc2`, pages `setpoints`/`f-sp.limit`

## 2. Session layer: stop unsafe retries

- [x] 2.1 Expose the session generation counter as a public read-only `generation` property on `SessionManager`
- [x] 2.2 Add `retry_on_expiry: bool = True` to `SessionManager.request()`; when `False`, re-authenticate on expiry but raise a distinguishable `SessionExpiredError` instead of resending the request
- [x] 2.3 Ensure `SessionExpiredError` is converted to a 502 if it ever reaches a caller that does not handle it, so it never surfaces as an unhandled 500

## 3. Navigation verification

- [x] 3.1 Change `_webrc_navigate` to take the expected page identity and pass `retry_on_expiry=False` on every `menue.rsp` step
- [x] 3.2 After the walk completes, parse the landed page title and verify it against the expected identity; on mismatch log the observed title at WARNING and raise 502 without retrying
- [x] 3.3 Add an operation-level helper that runs navigate+act and retries the whole thing exactly once on `SessionExpiredError`, but never on a verification failure

## 4. Setpoint read/write hardening

- [x] 4.1 Route `get_hc_setpoints` through the verifying navigation with the circuit's setpoints identity, so a wrong-circuit read returns 502 instead of the other circuit's values
- [x] 4.2 Route `set_hc_setpoint` through the same verification; pass `retry_on_expiry=False` on the `info.rsp` read and the `execset` POST
- [x] 4.3 Capture the session generation after navigation and assert it is unchanged immediately before the `execset` POST
- [x] 4.4 After writing, re-read the setpoints page and confirm the written field holds the requested value; raise 502 on mismatch
- [x] 4.5 Wrap the whole navigate+write in the single-retry helper from 3.3

## 5. Flow-limit read/write hardening

- [x] 5.1 Route `get_flow_limit` and `set_flow_limit` through the verifying navigation with the HC2 `f-sp.limit` identity
- [x] 5.2 In `set_flow_limit`, fail with 502 when `parse_flow_limit` cannot return all of `active`/`minFl`/`maxFl`, instead of falling through to `current.get("maxFl", 0.0)`
- [x] 5.3 Range-validate `maxFl` and `active` before writing, not just `minFl`
- [x] 5.4 Assert the captured session generation is unchanged before **each** of the three `execset` writes, per design decision 3
- [x] 5.5 Pass `retry_on_expiry=False` on the `info.rsp` read and all `_execset_flowlimit` POSTs
- [x] 5.6 After writing, re-read the limitation page once and confirm all written parameters hold their requested values; raise 502 on mismatch
- [x] 5.7 Wrap the whole navigate+write in the single-retry helper from 3.3

## 6. Verification

- [x] 6.1 Write a standalone verification script (scratch, not committed) with synthetic HTML fixtures reproducing the four page structures from `webrc_deep_dump.md`, asserting `parse_page_title` extracts each title and `page_matches` accepts only the correct circuit+page pair
- [x] 6.2 Assert the regression directly: a flow-limit write attempted while positioned on an HC1 setpoints page raises rather than writing, and no `execset` is issued
- [x] 6.3 Confirm the app imports and starts cleanly (`python -m app.main` fails only on device connectivity, not on an import or syntax error)

## 7. Ship

- [x] 7.1 Bump `heatpump-api/config.yaml` version from `0.1.10` to `0.1.11` so HA Supervisor offers the update
- [x] 7.2 Update `CLAUDE.md` to document that `execset` addressing is navigation-relative and that page identity must be verified before every write
- [x] 7.3 Commit and push directly to `main`
- [x] 7.4 After deploying, check the add-on log to confirm reads pass verification with no unexpected-title WARNINGs before trusting writes
