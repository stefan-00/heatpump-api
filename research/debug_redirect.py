#!/usr/bin/env python3
"""
Follow getcode.rsp redirect exactly as the browser does.
The redirect goes to branchnr=1&level=1 — stay there and explore.
"""
import asyncio, os, re
import httpx

URL  = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]

async def login(client):
    for _ in range(5):
        r = await client.get(f"{URL}/", follow_redirects=False)
        m = re.search(r"sessionid=([^&]+)", r.headers.get("location",""))
        if not m: await asyncio.sleep(20); continue
        sid = m.group(1)
        r2 = await client.post(f"{URL}/getlogin.rsp",
            data={"user": USER, "code": PASS[:8], "sessionid": sid},
            follow_redirects=False)
        if "sorry" in r2.headers.get("location","").lower():
            await asyncio.sleep(20); continue
        print(f"session: {sid}"); return sid
    raise RuntimeError("login failed")

async def get(client, sid, path):
    sep = "&" if "?" in path else "?"
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}", follow_redirects=False)
    return r.content.decode("latin-1")

def mainpane(raw):
    m = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    return m.group(1) if m else raw

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)
        await get(client, sid, "webfb.rsp")

        # Enter code 4444 with level=1 (as user does from level=1 context)
        r = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "1"},
            follow_redirects=False)
        redirect_loc = r.headers.get("location","")
        print(f"getcode.rsp → {r.status_code} {redirect_loc!r}")

        # Follow the redirect exactly as browser does
        if "menue.rsp" in redirect_loc:
            # Extract the path portion (strip the full domain if present)
            path_part = redirect_loc.split("192.168.1.11/")[-1] if "192.168.1.11" in redirect_loc else redirect_loc.lstrip("/")
            # Remove sessionid from path (our get() adds it back)
            path_part = re.sub(r'[?&]sessionid=[^&]+', '', path_part).lstrip('?&')
            print(f"Following redirect to: {path_part}")
            raw_redir = await get(client, sid, path_part)
            print(f"\n=== REDIRECT DESTINATION ({path_part}) ===")
            print(f"Size: {len(raw_redir)} bytes")
            print(mainpane(raw_redir))

        # Now also check branchnr=1&level=1 directly (the redirect destination)
        print("\n=== menue.rsp?branchnr=1&level=1 (direct, after elevation) ===")
        raw_l1 = await get(client, sid, "menue.rsp?branchnr=1&level=1")
        print(mainpane(raw_l1))

        # And branchnr=2&level=1 (MCR-BMS) without going to level=0 first
        print("\n=== menue.rsp?branchnr=2&level=1 (MCR-BMS, no level=0 reset) ===")
        raw_mcr = await get(client, sid, "menue.rsp?branchnr=2&level=1")
        print(mainpane(raw_mcr))

        # Go to level=0 then MCR-BMS
        print("\n=== level=0 then MCR-BMS (with level=0 reset) ===")
        await get(client, sid, "menue.rsp?branchnr=1&level=0")
        raw_mcr2 = await get(client, sid, "menue.rsp?branchnr=2&level=1")
        print(mainpane(raw_mcr2))

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
