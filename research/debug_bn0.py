#!/usr/bin/env python3
"""Enter 4444 with branchnr=0 (the actual webfb redirect destination)."""
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
    p = m.group(1) if m else raw
    return re.sub(r'<[^>]+>', ' ', p).strip()

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Follow webfb redirect: branchnr=0&level=0
        r_webfb = await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        print(f"webfb → {r_webfb.headers.get('location')}")

        # Land at branchnr=0&level=0 (as browser does)
        raw0 = await get(client, sid, "menue.rsp?branchnr=0&level=0")
        print(f"branchnr=0&level=0 mainpane: {mainpane(raw0)[:200]}")

        # Check what "Enter access code" link looks like from branchnr=0&level=0
        pw_link = re.search(r'password\.rsp\?[^"\']+', raw0)
        print(f"Enter access code link: {pw_link.group(0) if pw_link else 'NOT FOUND'}")

        # Enter 4444 with branchnr=0&level=0 (as browser does from this context)
        r_code = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "0", "level": "0"},
            follow_redirects=False)
        redirect_loc = r_code.headers.get("location","")
        print(f"\ngetcode(4444, bn=0, lv=0) → {r_code.status_code} {redirect_loc!r}")

        # Follow the redirect exactly
        if redirect_loc:
            # parse the path+query from the redirect URL
            m = re.match(r'(?:https?://[^/]+/)?(.*)', redirect_loc)
            path = m.group(1) if m else redirect_loc
            raw_redir = await get(client, sid, path)
            print(f"Redirect destination mainpane:\n{mainpane(raw_redir)}")

            # Also check what branchnr=1&level=1 shows now
            raw_l1 = await get(client, sid, "menue.rsp?branchnr=1&level=1")
            print(f"\nbranchnr=1&level=1 after this elevation:\n{mainpane(raw_l1)}")

            # And MCR-BMS without reset
            raw_mcr = await get(client, sid, "menue.rsp?branchnr=2&level=1")
            print(f"\nbranchnr=2&level=1 (MCR-BMS, no reset):\n{mainpane(raw_mcr)}")

            # Try branchnr=0&level=1
            raw_l1b0 = await get(client, sid, "menue.rsp?branchnr=0&level=1")
            print(f"\nbranchnr=0&level=1:\n{mainpane(raw_l1b0)}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
