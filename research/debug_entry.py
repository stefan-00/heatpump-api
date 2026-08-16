#!/usr/bin/env python3
"""Check webfb.rsp content and follow its redirect chain."""
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

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Check webfb.rsp raw content
        r = await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        print(f"webfb.rsp → status={r.status_code}")
        print(f"  headers: {dict(r.headers)}")
        print(f"  body: {r.content.decode('latin-1')!r}")

        # Check if it meta-refreshes or has a JS redirect
        body = r.content.decode("latin-1")
        refresh = re.search(r'content=["\']0;\s*url=([^"\']+)["\']', body, re.IGNORECASE)
        js_loc  = re.search(r'location\.(?:href|replace)\s*=\s*["\']([^"\']+)["\']', body, re.IGNORECASE)
        loc_hdr = r.headers.get("location","")
        print(f"  meta-refresh URL: {refresh.group(1) if refresh else None}")
        print(f"  JS redirect URL:  {js_loc.group(1) if js_loc else None}")
        print(f"  Location header:  {loc_hdr or None}")

        # Now try webfb.rsp WITH follow_redirects=True (as a browser would)
        print("\n--- webfb.rsp with follow_redirects=True ---")
        r2 = await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=True)
        print(f"Final URL after redirects: {r2.url}")
        print(f"Final status: {r2.status_code}")
        final_body = r2.content.decode("latin-1")
        mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', final_body, re.DOTALL|re.IGNORECASE)
        if mp:
            print(f"Mainpane: {re.sub(chr(10)+r'+', chr(10), re.sub(r'<[^>]+>', ' ', mp.group(1))).strip()}")

        # What does branchnr=1&level=1 look like RIGHT AFTER following webfb redirect?
        print("\n--- menue.rsp?branchnr=1&level=1 immediately after webfb ---")
        r3 = await client.get(f"{URL}/menue.rsp?branchnr=1&level=1&sessionid={sid}", follow_redirects=False)
        body3 = r3.content.decode("latin-1")
        mp3 = re.search(r'id="mainpane"[^>]*>(.*?)</div>', body3, re.DOTALL|re.IGNORECASE)
        if mp3:
            print(re.sub(r'<[^>]+>', ' ', mp3.group(1)).strip())

        # Now enter 4444 and check branchnr=1&level=1 WITHOUT going to level=0 first
        print("\n--- Enter 4444 (level=1 ctx), check branchnr=1&level=1 ---")
        await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "1"},
            follow_redirects=False)
        r4 = await client.get(f"{URL}/menue.rsp?branchnr=1&level=1&sessionid={sid}", follow_redirects=False)
        body4 = r4.content.decode("latin-1")
        mp4 = re.search(r'id="mainpane"[^>]*>(.*?)</div>', body4, re.DOTALL|re.IGNORECASE)
        if mp4:
            print(re.sub(r'<[^>]+>', ' ', mp4.group(1)).strip())

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
