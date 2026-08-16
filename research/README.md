# Protocol research scripts

One-off probes written while reverse-engineering the Panasonic HPM-800B7F
WEB-RC HTTP interface. They are the empirical basis for the protocol notes in
`CLAUDE.md` — kept because the device is undocumented and the next question
about it is usually answered faster by re-running a probe than by re-deriving
the behaviour.

They are **not** part of the application. Nothing in `heatpump-api/` imports
them, they have no tests, and they were written to answer a single question
each. Expect duplicated setup and abandoned dead ends.

All of them read `HEATPUMP_URL`, `HEATPUMP_USERNAME` and `HEATPUMP_PASSWORD`
from the environment, same as the application — there are no credentials in
these files. Two exceptions assume the device address `192.168.1.11` regardless
of `HEATPUMP_URL`: `debug_redirect.py` (splitting a redirect `Location`) and
`debug_ua.py` (a hardcoded `Referer`).

| Area | Scripts |
|---|---|
| Login and session handling | `debug_entry.py`, `debug_pwdform.py`, `debug_redirect.py`, `debug_sequence.py` |
| Cookies vs `sessionid` query param | `debug_cookies.py`, `debug_cookie2.py`, `debug_cookie_fix.py` |
| Request headers / user agent sensitivity | `debug_headers.py`, `debug_ua.py` |
| WEB-RC navigation and access elevation | `debug_webrc.py`, `debug_webrc2.py`, `debug_bn0.py`, `debug_codes.py`, `explore_webrc_deep.py` |
| MCR context and BMS pages | `debug_mcrctx.py`, `debug_mcrbms.py` |

`webrc_deep_dump.md` is the captured output of `explore_webrc_deep.py` — a walk
of the WEB-RC menu tree.

New probes belong in the project root while you are iterating (the root
`debug_*.py` / `explore_*.py` / `*_dump.md` patterns are gitignored). Move one
here once it is worth keeping.
