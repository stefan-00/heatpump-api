## Context

WEB-RC parameter writes go to `POST /execset.rsp` with `val`, `Set=OK`, `sessionid`, `branchnr`,
`level`, `id`. The `(branchnr, level)` pair is **relative to the page the session last navigated
to** — it does not identify a circuit. Evidence from `webrc_deep_dump.md`:

| Page | Address | Title row |
|---|---|---|
| HC1 setpoints (:1026) | `bn=2, lv=4` | `heatCirc1 setpoints` |
| HC2 setpoints (:1264) | `bn=2, lv=4` | `heatCirc2 setpoints` |
| HC1 setpoint limitation (:1066) | `bn=2, lv=5` | `heatCirc1 F-SP.limit` |
| HC2 setpoint limitation (:1304) | `bn=2, lv=5` | `heatCirc2 F-SP.limit` |

Coordinates collide across circuits; the **title row disambiguates them**. It is the first row of
the `<!-- start_mainpane -->` block that `parsers._mainpane()` already isolates, so extracting it
needs no new page fetch.

Two existing behaviours defeat the current code's assumption that navigation state is stable:

1. `SessionManager.request()` (session.py:127-131) re-authenticates on session expiry and re-sends
   the identical request. `login()` builds a fresh device session positioned at root and restores no
   navigation, so the resent request resolves its `(branchnr, level)` against the wrong page.
2. `_webrc_navigate` matches menu entries by label text, and HC1/HC2 expose identical child labels
   (`setpoints`, `function`, `setpoint limitation`). A re-login part-way through the walk can land
   the remainder of the walk in the wrong subtree and still match every label, so it raises nothing.

The device returns 302 for both accepted and rejected writes, so neither failure is observable
without an explicit read-back.

## Goals / Non-Goals

**Goals:**
- No `execset` is ever sent to a page whose identity has not been positively confirmed.
- A session re-authentication can never convert a write into a misaddressed write.
- Reads also confirm page identity, so HC1 values are never reported as HC2 (a wrong read would
  feed the Node-RED flow bad input and cause it to write wrong values).
- A write that the device rejects, or that does not take effect, surfaces as an error.
- A legitimate session expiry still completes the caller's request, by restarting the whole
  navigate+write operation rather than resending one leg of it.

**Non-Goals:**
- Switching WEB-RC writes to absolute parameter addressing (see Decisions — deferred).
- Changing the REST API surface, request/response models, or the Home Assistant package.
- Reducing the Node-RED write frequency. That lowers exposure but is not a fix, and is the user's
  own configuration.
- Recovering or auditing historical corruption; only prevention is in scope.

## Decisions

### 1. Verify identity via the page title row, not via `(branchnr, level)`

Add `parse_page_title(html) -> str` returning the first mainpane row's text, whitespace-normalised.
Compare case-insensitively against an expected token pair — the circuit marker (`heatcirc1` /
`heatcirc2`) and the page marker (`setpoints` / `f-sp.limit`).

*Why token matching over exact string equality:* firmware revisions may pad or re-word the row.
Requiring both tokens is specific enough to separate every page we address (no other page under a
circuit contains `setpoints` or `f-sp.limit` in its title) while tolerating cosmetic drift.

*Alternative rejected:* deriving identity from the presence of expected field labels (e.g. "does
this page have `minFl`?"). That cannot distinguish HC1's limitation page from HC2's — both have
`minFl` — which is precisely one of the two observed failures.

### 2. Verify at the end of navigation, for reads and writes alike

`_webrc_navigate` takes an `expect` argument and raises if the landed page's title does not match.
This catches mid-walk drift at the point it happens, and covers reads at no extra cost.

### 3. Guard the navigate→write window with the session generation counter

`SessionManager` already increments `_generation` on every successful `login()`. Expose it as a
public property. Each WEB-RC operation captures the generation after navigating and asserts it is
unchanged immediately before **each** `execset`. `set_flow_limit` issues three sequential writes, so
the check belongs before every one, not just the first.

*Why a counter rather than re-verifying the page before each write:* re-verification costs an extra
HTTP round-trip per parameter against a slow embedded device. The counter is free and detects the
only event that can invalidate navigation.

### 4. WEB-RC requests opt out of retry-after-re-auth

Add `retry_on_expiry: bool = True` to `SessionManager.request()`. WEB-RC navigation and write calls
pass `False`: on detecting expiry the method re-authenticates (so the session is usable again) but
raises instead of resending the misaddressed request.

*Why keep re-auth but drop the resend:* the session genuinely needs renewing, and dropping that
would make the next operation fail too. Only the blind resend is unsafe.

*Alternative rejected:* holding `_webrc_lock` across `login()` to make re-auth atomic with the
operation. `login()` is already serialised by its own lock and the ordering between the two locks
would invite deadlock; it also would not help when expiry is detected mid-write.

### 5. Retry the whole operation once, at the operation level

Writes and reads wrap navigate+act in a single retry: if the first attempt fails because the session
expired, re-run it from scratch on the fresh session. This keeps a routine expiry invisible to the
caller while guaranteeing every write is preceded by a verified navigation.

### 6. Read back and confirm after writing

After a setpoint write, re-parse the page and confirm the field holds the requested value; after a
flow-limit write, confirm all three parameters. Mismatch raises 502. This turns the device's
indistinguishable 302 into an observable outcome and would have caught both incidents even if every
guard above had been bypassed.

### 7. Range-check all three flow-limit parameters

`_execset_flowlimit` currently range-checks only `minFl`. Extend to `active` and `maxFl`. Note this
is defence in depth, not the primary fix: the `info.rsp` range read is itself context-relative, so
on an unverified page it validates against the wrong parameter's limits. It only becomes meaningful
once decision 2 guarantees the page.

### 8. Deferred: absolute parameter addressing

The proper long-term fix is to address parameters absolutely (`2.5.2.3.6.x`) rather than by relative
`(branchnr, level)`, which would make navigation state irrelevant. `execgrset.rsp` accepts
`id`/`val`/`pv` and is used for standard params, but it is unproven for WEB-RC params and would need
a fresh reverse-engineering pass against a live device. Deferred to keep this change small and
shippable while heating is actively being mis-set.

## Risks / Trade-offs

- **Title format differs from the dump on the live device → every write fails closed, losing all
  setpoint control.** → Match on two lowercase tokens rather than an exact string; log the actual
  observed title at WARNING on mismatch so a format change is immediately diagnosable from the
  add-on log. Verify against the live device before considering the change done.
- **Fail-closed is a deliberate trade-off.** A rejected write leaves the pool un-heated and surfaces
  an error in HA; a misaddressed write overheats the house for days undetected. The former is
  strictly preferable, and this is accepted rather than mitigated.
- **Read-back adds one page fetch per write** against a slow device. → Writes already navigate
  (4-5 requests); one more is marginal, and `set_flow_limit` needs only a single read-back for all
  three parameters.
- **Operation-level retry could double a write.** → Retry only on session-expiry failure, never on a
  verification failure, and writes are idempotent (setting the same value twice is a no-op).
- **The generation guard cannot detect a re-login that happens and is followed by a re-login back to
  the same count.** → Not reachable: the counter is monotonically increasing, never reset.

## Migration Plan

1. Implement and unit-test parsing/verification against the captured HTML in `webrc_deep_dump.md`.
2. Bump the add-on version in `config.yaml` — HA Supervisor only offers an update on a version
   change.
3. After deploying, confirm in the add-on log that reads pass verification (no WARNING about
   unexpected titles) before trusting writes.
4. Rollback: revert to the prior add-on version. No persisted state or schema changes, so rollback
   is clean.

## Open Questions

- Do the live device's title rows match the `webrc_deep_dump.md` capture exactly? Resolved by step 3
  of the migration plan; the loose token match is chosen so that the answer does not have to be
  "yes, byte for byte".
