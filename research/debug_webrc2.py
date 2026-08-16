#!/usr/bin/env python3
"""
Debug: inspect password.rsp form + check if setpoints pages have writable inputs.
"""
import asyncio, os, re
import httpx

URL  = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]


async def login(client):
    for _ in range(5):
        r = await client.get(f"{URL}/", follow_redirects=False)
        m = re.search(r"sessionid=([^&]+)", r.headers.get("location", ""))
        if not m:
            await asyncio.sleep(20); continue
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


async def post(client, sid, path, data):
    data["sessionid"] = sid
    r = await client.post(f"{URL}/{path}", data=data, follow_redirects=False)
    return r.status_code, r.headers.get("location",""), r.content.decode("latin-1")


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC
        await get(client, sid, "webfb.rsp")

        # 1. Look at password.rsp BEFORE elevation (at level=0)
        print("\n=== password.rsp (before elevation, level=0) ===")
        pw = await get(client, sid, "password.rsp?level=0&branchnr=1")
        print(pw[:3000])

        # 2. Submit 4444 via the form as-is
        print("\n=== POST getcode.rsp code=4444 level=0 ===")
        sc, loc, body = await post(client, sid, "getcode.rsp",
            {"code": "4444", "level": "0", "branchnr": "1"})
        print(f"status={sc} loc={loc!r}")
        print(body[:1000])

        # 3. Check password.rsp again to see if level changed
        print("\n=== password.rsp AFTER elevation ===")
        pw2 = await get(client, sid, "password.rsp?level=1&branchnr=1")
        print(pw2[:2000])

        # 4. Navigate MCR-BMS and check children count
        print("\n=== root level=0 ===")
        await get(client, sid, "menue.rsp?branchnr=1&level=0")
        print("\n=== MCR-BMS (bn=2&lv=1) after level=0 reset ===")
        raw = await get(client, sid, "menue.rsp?branchnr=2&level=1")
        print(raw)

        # 5. Check a setpoints page for actual input fields
        print("\n=== heatC.1 setpoints raw HTML ===")
        # Need to navigate: level=0 → MCR-BMS → heatCirc. → heatC.1 → setpoints
        await get(client, sid, "menue.rsp?branchnr=1&level=0")
        await get(client, sid, "menue.rsp?branchnr=2&level=1")  # MCR-BMS
        await get(client, sid, "menue.rsp?branchnr=4&level=2")  # heatCirc.
        await get(client, sid, "menue.rsp?branchnr=1&level=3")  # heatC.1
        sp = await get(client, sid, "menue.rsp?branchnr=2&level=4")  # setpoints
        print(sp)

        # Logout
        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")


asyncio.run(main())
