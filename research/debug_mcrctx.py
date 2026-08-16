#!/usr/bin/env python3
"""
Enter 4444 from within MCR-BMS context, then immediately check branchnr=1&level=1
WITHOUT any reset navigation.
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

def mainpane_text(raw):
    m = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    p = m.group(1) if m else raw
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', p)).strip()

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC via webfb (sets branchnr=0 context)
        await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        # Land at root
        await get(client, sid, "menue.rsp?branchnr=0&level=0")

        # Navigate to MCR-BMS
        raw_mcr = await get(client, sid, "menue.rsp?branchnr=2&level=1")
        print(f"MCR-BMS mainpane before code: {mainpane_text(raw_mcr)[:300]}")

        # Capture the "Enter access code" link from MCR-BMS page
        pw_link = re.search(r'password\.rsp\?[^"\']+', raw_mcr)
        print(f"Enter access code link from MCR-BMS: {pw_link.group(0) if pw_link else 'NOT FOUND'}")

        # Enter code 4444 from MCR-BMS context (level=1, branchnr=1)
        r = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "1"},
            follow_redirects=False)
        redirect = r.headers.get("location","")
        print(f"\ngetcode(4444, bn=1, lv=1) → {r.status_code} {redirect!r}")

        # IMMEDIATELY fetch branchnr=1&level=1 (NO reset navigation)
        raw_immediate = await get(client, sid, "menue.rsp?branchnr=1&level=1")
        print(f"\nbranchnr=1&level=1 IMMEDIATELY after code (no reset):")
        print(mainpane_text(raw_immediate))

        # Also try fetching via the redirect path directly
        if redirect:
            m = re.search(r'(menue\.rsp\?[^"\']+)', redirect)
            if m:
                path = m.group(1).replace(f"sessionid={sid}&", "").replace(f"&sessionid={sid}", "")
                raw_redir = await get(client, sid, path)
                print(f"\nRedirect path ({m.group(1)}):")
                print(mainpane_text(raw_redir))

        # Now try navigating to what MCR-BMS children look like
        # DON'T go to level=0 first — stay in MCR-BMS context
        print("\nNow checking what children MCR-BMS shows (no reset):")
        for bn in range(0, 10):
            raw = await get(client, sid, f"menue.rsp?branchnr={bn}&level=2")
            mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
            if mp:
                labels = re.findall(r'<td[^>]*>.*?<a[^>]*>([^<]+)</a>.*?</td>', mp.group(1), re.DOTALL|re.IGNORECASE)
                menu_title = re.search(r'<p>([^<]+)</p>', mp.group(1))
                title = menu_title.group(1).strip() if menu_title else "?"
                if "Cannot find" not in raw:
                    print(f"  bn={bn} lv=2: {title!r}  children={labels}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
