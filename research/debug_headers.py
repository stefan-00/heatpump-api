#!/usr/bin/env python3
"""Check all response headers from key WEB-RC requests."""
import asyncio, os, re
import httpx

URL  = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # Login
        r = await client.get(f"{URL}/", follow_redirects=False)
        sid = re.search(r"sessionid=([^&]+)", r.headers.get("location","")).group(1)
        print(f"Login GET / headers: {dict(r.headers)}")

        r2 = await client.post(f"{URL}/getlogin.rsp",
            data={"user": USER, "code": PASS[:8], "sessionid": sid},
            follow_redirects=False)
        print(f"\nLogin POST headers: {dict(r2.headers)}")
        print(f"Cookies after login: {dict(client.cookies)}")

        # webfb.rsp
        r3 = await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        print(f"\nwebfb.rsp headers: {dict(r3.headers)}")
        print(f"Cookies after webfb: {dict(client.cookies)}")

        # getcode.rsp POST with 4444
        r4 = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "0"},
            follow_redirects=False)
        print(f"\ngetcode.rsp (4444) headers: {dict(r4.headers)}")
        print(f"Body: {r4.content.decode('latin-1')[:500]}")
        print(f"Cookies after getcode: {dict(client.cookies)}")

        # Check global page — how many children?
        await client.get(f"{URL}/menue.rsp?branchnr=1&level=0&sessionid={sid}", follow_redirects=False)
        r5 = await client.get(f"{URL}/menue.rsp?branchnr=1&level=1&sessionid={sid}", follow_redirects=False)
        raw_global = r5.content.decode("latin-1")
        mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw_global, re.DOTALL|re.IGNORECASE)
        print(f"\nGlobal mainpane:\n{mp.group(1) if mp else 'not found'}")

        # Logout
        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
