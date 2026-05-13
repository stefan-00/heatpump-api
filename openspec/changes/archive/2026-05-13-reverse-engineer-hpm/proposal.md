## Why

The foundation change left `TODO` stubs in `session.py` and `client.py` because the heatpump's web UI protocol was unknown at that point. Live probing of the HPM-800B7F (http://192.168.1.11/) has revealed the authentication mechanism; this change fills in those stubs and implements the first working API endpoint.

## What Changes

- Replace the `TODO` login URL/payload in `session.py` with the real HPM login flow: obtain a `sessionid` from the initial redirect, then `POST /getlogin.rsp` with `user`, `code`, and `sessionid` fields
- Update `session.py` to pass `sessionid` as a URL query parameter on every proxied request (HPM uses URL params, not cookies)
- Reverse-engineer the authenticated page structure to identify the status and control endpoints
- Fill in `client.py` `get_status()` and `send_command()` with the real HPM endpoint URLs and payload/response formats
- Implement and verify the first working API endpoint: `GET /api/v1/status`
- Update configuration field name: `password` → `code` to match the HPM web UI field (max 8 chars); keep `password` as an alias for backward compatibility in env-var mode

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `session-management`: HPM login is two-step — first `GET /` to obtain a `sessionid` from the 302 redirect, then `POST /getlogin.rsp` with `user`, `code`, and `sessionid`. The session is maintained via `sessionid` URL query parameter on all subsequent requests, not via cookies.
- `heatpump-control`: Fill in actual endpoint URLs, HTTP methods, request payload format, and response field mapping for both `get_status` and `send_command`. Update confirmed value ranges and enums (temperature, modes, fan speeds) once reverse-engineered from the authenticated UI.

## Impact

- `app/session.py`: login URL, fields, session persistence mechanism
- `app/client.py`: status URL, control URL, payload format, response field mapping
- `app/config.py`: minor — document that `password` config key corresponds to the HPM `code` field
- `openspec/specs/session-management/spec.md`: update session storage requirement from "cookies or token" to URL `sessionid` parameter
- `openspec/specs/heatpump-control/spec.md`: update with confirmed endpoints and value constraints
