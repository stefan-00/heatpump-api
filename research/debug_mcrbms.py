#!/usr/bin/env python3
"""Print raw HTML of MCR-BMS page after code 4444 elevation, for debugging."""
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

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)
        await get(client, sid, "webfb.rsp")

        # Elevate with correct form fields
        r = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "0"},
            follow_redirects=False)
        print(f"elevation: {r.status_code} → {r.headers.get('location','')!r}")
        await asyncio.sleep(1)

        # Follow the redirect destination from elevation
        elev_redirect = r.headers.get("location","").replace(f"?sessionid={sid}&","?")
        if elev_redirect:
            raw_redir = await get(client, sid, elev_redirect.split("?")[0] + "?" + elev_redirect.split("?")[1].replace(f"sessionid={sid}&",""))
            print(f"post-elevation redirect page: {len(raw_redir)} bytes")

        # Navigate fresh to root then MCR-BMS
        print("\n[navigating: level=0 root]")
        raw0 = await get(client, sid, "menue.rsp?branchnr=1&level=0")
        print(f"root: {len(raw0)} bytes")

        print("\n[navigating: MCR-BMS bn=2 lv=1]")
        raw_mcr = await get(client, sid, "menue.rsp?branchnr=2&level=1")
        print(f"MCR-BMS: {len(raw_mcr)} bytes")
        print("\n=== FULL MCR-BMS HTML ===")
        print(raw_mcr)

        # Also check what the mainpane contains specifically
        import re as re2
        mp = re2.search(r'id="mainpane"[^>]*>(.*?)</div>', raw_mcr, re2.DOTALL|re2.IGNORECASE)
        if mp:
            print("\n=== MAINPANE ONLY ===")
            print(mp.group(1))

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
