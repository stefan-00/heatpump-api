## Why

`webrc-write-target-verification` (0.1.11) closed the navigation-relative addressing hole, but a
leak recurred on 2026-08-13: HC2 `roomOT2` was set to 34.0, the pool flow floor. The add-on log
shows the mechanism, and it is a different one.

`get_status` fetches five `v*.rsp` view pages and is **not** serialised with WEB-RC operations —
`client.py` gathers them with no lock. On the shared, stateful device session they interleaved
*inside* a flow-limit write's critical section, between the `info.rsp` range reads and the
`execset` writes:

```
09:31:14,495  GET menue.rsp?branchnr=2&level=5   ← lands on F-SP.limit, verified OK
09:31:14,604  GET info.rsp?branchnr=2&level=5
09:31:14,696  GET info.rsp?branchnr=3&level=5
09:31:14,761  GET v30.rsp        ← status poll, same session, mid-write
09:31:15,028  GET v21.rsp
09:31:15,279  GET v107000.rsp
09:31:15,514  GET v0.rsp
09:31:15,692  GET v3.rsp
09:31:15,934  POST execset.rsp  302   ← writes fire against a disturbed context
09:31:15,956  POST execset.rsp  302
09:31:15,970  POST execset.rsp  302
```

Navigation was verified, then the session was disturbed, then the writes landed. On a setpoints
page the flow-limit positions alias onto `roomOT1`/`roomOT2`/`roomOT3`, so `minFl` becomes
`roomOT2` — the same aliasing as before, reached by a new route.

All three 0.1.11 guards were blind to it:

| Guard | Why it did not fire |
|---|---|
| Page verification | Runs at the end of navigation; the disturbance happens after it |
| Generation guard | Only detects re-login. Session `E0186AA3` throughout — no re-auth occurred |
| Read-back confirmation | The requested value already equalled the stored value, so the comparison passed regardless of where the write went |

That last row is the deeper problem. The caller writes `minFl = 34.0` when `minFl` is already
`34.0`, roughly every 10-25 seconds. Such a write is **unverifiable by construction**: the page
reads back correct whether or not the write landed there. Every PATCH returned 200 OK.

## What Changes

- **Serialise every request to the device, not just WEB-RC ones.** The lock is renamed from
  `_webrc_lock` to `_device_lock` and `get_status` acquires it. The session is stateful, so request
  ordering — not request kind — is what matters.
- **Re-verify page identity immediately before the first `execset`**, in addition to after
  navigation. Verification that happens only before a gap cannot protect what happens inside it,
  and this class of bug has now bitten twice.
- **Skip writes that would be no-ops.** When the device already holds the requested value, issue no
  `execset` at all. This removes the unverifiable-write class entirely: every write that remains
  changes something, so read-back confirmation becomes meaningful again. It also eliminates the
  large majority of device traffic, since the caller re-asserts an unchanged value continuously.

## Capabilities

### New Capabilities
<!-- None. Hardens existing behaviour. -->

### Modified Capabilities
- `session-management`: "Serialise WEB-RC navigation across circuits" broadens to cover all device
  requests including status reads; page identity must be re-confirmed immediately before writing.
- `heatpump-control`: the HC2 flow-limitation write must skip no-op writes and re-verify the page
  before writing.
- `heating-circuit-setpoints`: setpoint writes must skip no-op writes and re-verify before writing.

## Impact

- `heatpump-api/app/client.py` — lock rename and broadened scope; `get_status` acquires it;
  `_webrc_navigate` reports its final `(branchnr, level)` so the page can be re-confirmed;
  `set_flow_limit` and `set_hc_setpoint` gain no-op skipping and pre-write re-verification.
- Status reads now queue behind WEB-RC operations. A WEB-RC operation is ~1 s, and status is polled
  every 30 s, so added latency is small and bounded.
- No REST API surface change. A skipped no-op write still returns 200 with the confirmed state, so
  callers see no behavioural difference.
- Out of scope: the caller-side write frequency. Reducing it is worthwhile but is Node-RED
  configuration, and no-op skipping already removes the load and the risk at this end.
