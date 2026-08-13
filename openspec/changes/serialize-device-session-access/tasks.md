## 1. Serialise all device access

- [x] 1.1 Rename `HeatpumpClient._webrc_lock` to `_device_lock` and update its comment to say the lock covers every request to the shared stateful session, not only WEB-RC ones
- [x] 1.2 Acquire `_device_lock` in `get_status` around the whole `asyncio.gather` of `v*.rsp` fetches, leaving those five concurrent with each other
- [x] 1.3 Confirm no other method issues a device request outside the lock

## 2. Pre-write page re-confirmation

- [x] 2.1 Change `_webrc_navigate` to return the landed page's response together with its final `(branchnr, level)`, and update all callers
- [x] 2.2 Add `_reconfirm_page(base, branchnr, level, circuit, page)` that re-selects the page at those coordinates and re-checks the title, raising 502 on mismatch
- [x] 2.3 Call it immediately before the first `execset` in `set_hc_setpoint` and in `set_flow_limit`

## 3. Skip no-op writes

- [x] 3.1 Add a shared tolerance constant for "already at this value" matching the routers' read-back tolerance (0.05)
- [x] 3.2 In `set_hc_setpoint`, read the current value from the verified page and skip the `execset` when it already matches, logging the skip
- [x] 3.3 In `set_flow_limit`, skip `minFl`/`maxFl` when they already match, and skip `active` when it already matches; ensure a floor that matches while the limitation is off still writes `active`
- [x] 3.4 Ensure a fully skipped operation still returns the confirmed current state so callers see no behavioural difference
- [x] 3.5 Ensure the routers' read-back confirmation still passes for skipped writes (the value is already correct)

## 4. Verification

- [x] 4.1 Extend the scratch verification script with a session that interleaves a `v*.rsp` fetch between `info.rsp` and `execset`, asserting the pre-write re-confirmation aborts the write
- [x] 4.2 Assert no-op skipping: a flow-limit write matching the current state issues zero `execset` POSTs and still returns the state
- [x] 4.3 Assert a differing value still writes, in the correct `maxFl`/`minFl`/`active` order
- [x] 4.4 Assert `get_status` cannot interleave: with the lock held by a WEB-RC operation, a concurrent `get_status` issues no device request until the operation completes
- [x] 4.5 Re-run the 0.1.11 verification script to confirm no regression in page-identity and generation guards
- [x] 4.6 Confirm the app imports and starts cleanly

## 5. Ship

- [x] 5.1 Bump `heatpump-api/config.yaml` version from `0.1.11` to `0.1.12`
- [x] 5.2 Update `CLAUDE.md`: the lock covers all device requests, page identity is re-confirmed before writing, and no-op writes are skipped because they are unverifiable
- [ ] 5.3 Commit and push directly to `main`
- [ ] 5.4 After deploying, confirm in the log that repeated `PATCH hc2/flow-limit` calls with an unchanged value complete with no `execset` POSTs
