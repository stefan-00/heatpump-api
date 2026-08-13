## Context

The HPM maintains one stateful navigation position per session. `execset.rsp` addresses a parameter
relative to that position, so any request that moves it between navigation and write makes the write
land somewhere else.

0.1.11 treated this as a *WEB-RC* concurrency problem and serialised WEB-RC operations under
`_webrc_lock`. But `get_status` was left outside the lock on the assumption that `v*.rsp` view-page
fetches do not affect navigation state. The 2026-08-13 log disproves that assumption: five `v*.rsp`
fetches interleaved between `info.rsp` and `execset`, and `roomOT2` took the `minFl` value.

The precise device-side effect of a `v*.rsp` fetch on the menu pointer is not directly observable —
what the log proves is that non-WEB-RC traffic entered the critical section and the write
mis-landed. The fix does not depend on knowing the exact internal mechanism; it removes the
interleaving.

## Goals / Non-Goals

**Goals:**
- No request of any kind reaches the device between a verified navigation and the writes that depend
  on it.
- Page identity is confirmed immediately before writing, so a disturbance from any future source is
  caught rather than assumed away.
- Every `execset` that is issued changes a value, so read-back confirmation actually proves the
  write landed on the intended parameter.

**Non-Goals:**
- Reducing caller write frequency (Node-RED configuration).
- Absolute parameter addressing, still the proper long-term fix and still deferred.
- Any REST API or Home Assistant package change.

## Decisions

### 1. One lock for all device access, not just WEB-RC access

Rename `_webrc_lock` to `_device_lock` and acquire it in `get_status`. The name change is
load-bearing: the previous name is what made "status reads aren't WEB-RC, so they don't need the
lock" sound reasonable.

*Why not a second lock for status:* two locks would have to be ordered against each other to mean
anything, and the requirement is simply that device requests do not interleave. One lock expresses
that directly.

*Cost:* status polls serialise behind WEB-RC operations. A WEB-RC operation is roughly 1 s; status
is polled every 30 s. Worst case a poll waits one operation. Accepted.

*Note:* the five `v*.rsp` fetches inside `get_status` remain gathered concurrently **with each
other**. They perform no navigation, and the log shows the device already serialises them (~250 ms
apart). Holding the lock for the whole gather is what matters.

### 2. Re-verify page identity immediately before the first `execset`

`_webrc_navigate` returns the final `(branchnr, level)` alongside the response. Before the first
write, re-fetch `menue.rsp?branchnr=<final_bn>&level=<final_lv>` and re-check the title.

If the position is intact, this re-selects the same node and returns the same page, so the title
matches. If something moved the position, the request resolves elsewhere and the title does not
match — abort without writing.

*Why this and not only the lock:* the lock should make it unreachable, which is exactly what was
believed about `_webrc_lock` before this incident. One extra request per write is cheap insurance
against the third variant of this bug.

*Why not verify before every write in a multi-parameter sequence:* the three flow-limit writes are
consecutive with no intervening requests, and the generation check already covers re-login between
them. Verifying once before the first is proportionate.

### 3. Skip no-op writes

Before writing, compare the requested value with what the page already shows. If equal (within the
same 0.05 tolerance used for read-back confirmation), skip the `execset` and log at INFO.

This is the highest-value change here, for a reason worth stating plainly: **a write whose requested
value already matches the stored value cannot be verified.** Read-back passes whether the write
landed on the right parameter, the wrong parameter, or nowhere. Skipping such writes means every
write that is issued must change the page, so read-back confirmation becomes a real check.

It also removes most of the device traffic — the caller re-asserts `minFl = 34.0` every 10-25 s —
which shrinks the window for any remaining concurrency bug.

*Behaviour:* a fully no-op request still returns 200 with the current confirmed state, so callers
cannot tell the difference. `active` is compared too, so "set the floor and enable" still writes
`active` when the limitation is currently off even if the floor already matches.

*Alternative rejected:* writing anyway and logging a warning that the result is unverifiable. That
keeps the risk while only documenting it.

## Risks / Trade-offs

- **Status latency increases.** → Bounded by one WEB-RC operation (~1 s) against a 30 s poll
  interval. If it ever matters, the fix is fewer writes, not a second lock.
- **A no-op skip could mask a genuine need to rewrite** — e.g. the device silently lost a value but
  still reports it. → Not possible: the comparison is against what the device currently reports, so
  if it reports the target value, the target is met by definition.
- **Pre-write re-verification adds a request per write.** → Offset many times over by no-op
  skipping, which removes most writes entirely.
- **Re-selecting the final node could itself have side effects** on a device this quirky. → It is
  the same `menue.rsp` GET the navigation walk already performs as its last step, so it is a repeat
  of a known-safe request, not a new kind of interaction.

## Migration Plan

1. Implement, then verify with synthetic fixtures that reproduce the interleaving.
2. Bump the add-on version so Supervisor offers the update.
3. After deploying, confirm in the log that `PATCH hc2/flow-limit` calls now complete without
   `execset` POSTs when the value is unchanged — that is the visible signature of the fix working.
4. Rollback: revert to the previous add-on version. No persisted state.

## Open Questions

- Does a `v*.rsp` fetch actually reset the menu pointer, or does it disturb the session some other
  way? Unresolved and deliberately not blocking: the fix prevents the interleaving regardless. If
  it ever matters, the way to find out is a controlled experiment against the device — navigate,
  fetch `v3.rsp`, then read back `menue.rsp` at the same coordinates and compare titles.
