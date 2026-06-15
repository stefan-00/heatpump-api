## 1. Verify implemented transport resilience (session-management)

- [x] 1.1 Confirm `app/session.py` creates the `AsyncClient` with `httpx.Timeout(settings.request_timeout, connect=5.0)`
- [x] 1.2 Confirm `_make_request` retries `httpx.RequestError` up to 2 additional times with linear backoff and re-raises the last exception
- [x] 1.3 Confirm the single `_webrc_lock` in `app/client.py` serialises all WEB-RC navigation/write operations across circuits

## 2. Verify configurable timeout (config + packaging)

- [x] 2.1 Confirm `app/config.py` exposes `request_timeout` (default 15.0) and reads `HEATPUMP_TIMEOUT` for local/env config
- [x] 2.2 Confirm `heatpump-api/config.yaml` declares `request_timeout` in both `options` and `schema` (`float?`)
- [x] 2.3 Confirm the add-on `version` is bumped so the Supervisor offers the update

## 3. Verify error logging (rest-api / client)

- [x] 3.1 Confirm all three `httpx.RequestError` handlers in `app/client.py` log with `%r` and put `{e!r}` in the 502 detail

## 4. Verify HA sensor resilience (ha-sensor-config)

- [x] 4.1 Confirm every status `value_template` in `packages/heatpump.yaml` is guarded (`... if '<key>' in value_json else none`) with a matching `availability`
- [x] 4.2 Confirm every setpoint `value_template` (roomOT1–4, roomNO, roomSNOT for hc1 and hc2) is guarded against missing keys

## 5. Documentation alignment

- [x] 5.1 Update `heatpump-api/DOCS.md` to describe the `request_timeout` option
- [x] 5.2 Add a `heatpump-api/CHANGELOG.md` entry for the new version (timeout + retry + error-response resilience)
- [x] 5.3 Note in `docs/ha-integration.md` that sensors go `unavailable` (not error) when the API returns an error body

## 6. Archive

- [x] 6.1 Run `/opsx:verify` to confirm implementation matches the spec deltas
- [x] 6.2 Archive the change so the four delta specs are synced into `openspec/specs/`
