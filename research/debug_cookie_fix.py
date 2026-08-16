#!/usr/bin/env python3
"""
Send cmcookie=0,0,0,0 with getcode.rsp POST and follow the Set-Cookie response.
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

async def get(client, sid, path, cookies=None):
    sep = "&" if "?" in path else "?"
    hdrs = {"Cookie": f"cmcookie={cookies}"} if cookies else {}
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}",
                         headers=hdrs, follow_redirects=False)
    return r

def mainpane_text(raw):
    m = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    p = m.group(1) if m else raw
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', p)).strip()

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC
        await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        await client.get(f"{URL}/menue.rsp?branchnr=0&level=0&sessionid={sid}", follow_redirects=False)

        # Navigate to MCR-BMS to establish context
        await client.get(f"{URL}/menue.rsp?branchnr=2&level=1&sessionid={sid}", follow_redirects=False)

        # POST getcode.rsp WITH cmcookie=0,0,0,0 (as browser sends)
        cm = "0%2C0%2C0%2C0"
        print(f"Sending getcode.rsp with Cookie: cmcookie={cm}")
        r = await client.post(
            f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "1"},
            headers={"Cookie": f"cmcookie={cm}"},
            follow_redirects=False,
        )
        redirect = r.headers.get("location","")
        new_cookie = r.headers.get("set-cookie","")
        print(f"  → {r.status_code} {redirect!r}")
        print(f"  Set-Cookie: {new_cookie!r}")
        print(f"  All response headers: {dict(r.headers)}")

        # Extract updated cmcookie from Set-Cookie
        cm_new_match = re.search(r'cmcookie=([^;,\s]+)', new_cookie)
        cm_new = cm_new_match.group(1) if cm_new_match else cm
        print(f"  Updated cmcookie: {cm_new}")

        # Now fetch branchnr=1&level=1 WITH the updated cookie
        print(f"\nFetching branchnr=1&level=1 with cmcookie={cm_new}")
        r2 = await client.get(
            f"{URL}/menue.rsp?branchnr=1&level=1&sessionid={sid}",
            headers={"Cookie": f"cmcookie={cm_new}"},
            follow_redirects=False,
        )
        print(f"  mainpane: {mainpane_text(r2.content.decode('latin-1'))[:400]}")

        # Also try MCR-BMS with the updated cookie
        print(f"\nFetching MCR-BMS (branchnr=2&level=1) with cmcookie={cm_new}")
        await client.get(f"{URL}/menue.rsp?branchnr=1&level=0&sessionid={sid}",
                         headers={"Cookie": f"cmcookie={cm_new}"}, follow_redirects=False)
        r3 = await client.get(
            f"{URL}/menue.rsp?branchnr=2&level=1&sessionid={sid}",
            headers={"Cookie": f"cmcookie={cm_new}"},
            follow_redirects=False,
        )
        print(f"  mainpane: {mainpane_text(r3.content.decode('latin-1'))[:400]}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
