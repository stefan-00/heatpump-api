#!/usr/bin/env python3
"""Check all Set-Cookie headers throughout the WEB-RC flow."""
import asyncio, os, re
import httpx

URL  = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # Login
        r0 = await client.get(f"{URL}/", follow_redirects=False)
        m = re.search(r"sessionid=([^&]+)", r0.headers.get("location",""))
        sid = m.group(1)
        print(f"GET /  cookies: {r0.headers.get('set-cookie','(none)')}")

        r1 = await client.post(f"{URL}/getlogin.rsp",
            data={"user": USER, "code": PASS[:8], "sessionid": sid},
            follow_redirects=False)
        print(f"POST /getlogin.rsp  set-cookie: {r1.headers.get('set-cookie','(none)')}")
        print(f"  cookie jar: {dict(client.cookies)}")
        print(f"  session: {sid}")

        # webfb
        r2 = await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        print(f"\nGET webfb.rsp  set-cookie: {r2.headers.get('set-cookie','(none)')}")
        print(f"  cookie jar: {dict(client.cookies)}")

        # getcode
        r3 = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "1"},
            follow_redirects=False)
        print(f"\nPOST getcode.rsp(4444)  set-cookie: {r3.headers.get('set-cookie','(none)')}")
        print(f"  redirect: {r3.headers.get('location','')}")
        print(f"  cookie jar: {dict(client.cookies)}")
        print(f"  all response headers: {dict(r3.headers)}")

        # Fetch the redirect destination WITH cookies being sent
        r4 = await client.get(f"{URL}/menue.rsp?branchnr=1&level=1&sessionid={sid}",
                               follow_redirects=False)
        print(f"\nGET menue.rsp branchnr=1 level=1:")
        print(f"  request cookies sent: {dict(client.cookies)}")
        mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', r4.content.decode("latin-1"),
                       re.DOTALL|re.IGNORECASE)
        if mp:
            print(f"  mainpane: {re.sub(chr(10)+r'+', ' ', re.sub(r'<[^>]+>',' ', mp.group(1))).strip()[:300]}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
