#!/usr/bin/env python3
"""Try browser User-Agent and check if protect level changes after entering 4444."""
import asyncio, os, re
import httpx

URL  = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]

BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
BROWSER_COOKIE = "cmcookie=0%2C0%2C0%2C0"

async def login(client, ua=None):
    hdrs = {"User-Agent": ua} if ua else {}
    for _ in range(5):
        r = await client.get(f"{URL}/", headers=hdrs, follow_redirects=False)
        m = re.search(r"sessionid=([^&]+)", r.headers.get("location",""))
        if not m: await asyncio.sleep(20); continue
        sid = m.group(1)
        r2 = await client.post(f"{URL}/getlogin.rsp",
            data={"user": USER, "code": PASS[:8], "sessionid": sid},
            headers=hdrs, follow_redirects=False)
        if "sorry" in r2.headers.get("location","").lower():
            await asyncio.sleep(20); continue
        print(f"session: {sid}"); return sid
    raise RuntimeError("login failed")

async def get(client, sid, path, ua=None, cm=None):
    hdrs = {}
    if ua:  hdrs["User-Agent"] = ua
    if cm:  hdrs["Cookie"] = cm
    sep = "&" if "?" in path else "?"
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}",
                         headers=hdrs, follow_redirects=False)
    return r.content.decode("latin-1")

def mainpane_text(raw):
    m = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    p = m.group(1) if m else raw
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', p)).strip()[:400]

async def get_mcr_children(client, sid, ua=None, cm=None):
    await get(client, sid, "menue.rsp?branchnr=1&level=0", ua, cm)
    raw = await get(client, sid, "menue.rsp?branchnr=2&level=1", ua, cm)
    mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    return re.findall(r'<td[^>]*>.*?<a[^>]*>([^<]+)</a>', mp.group(1) if mp else "", re.DOTALL|re.IGNORECASE)

async def get_protect_level(client, sid, ua=None, cm=None):
    """Navigate global > service > access codes and read protect value."""
    await get(client, sid, "menue.rsp?branchnr=1&level=0", ua, cm)
    await get(client, sid, "menue.rsp?branchnr=1&level=1", ua, cm)  # global
    await get(client, sid, "menue.rsp?branchnr=1&level=2", ua, cm)  # service
    raw = await get(client, sid, "menue.rsp?branchnr=1&level=3", ua, cm)  # access codes
    protect = re.search(r'protect\s+(\d+)', raw)
    all_codes = re.findall(r'level\s+(\d+)\s+(\d+)', raw)
    return protect.group(1) if protect else "?", all_codes

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client, ua=BROWSER_UA)
        await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)

        # Check protect level BEFORE code entry
        protect_before, codes_before = await get_protect_level(client, sid, ua=BROWSER_UA, cm=BROWSER_COOKIE)
        print(f"Protect level BEFORE code: {protect_before}, codes visible: {codes_before}")

        # Enter 4444 with full browser headers
        r = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid, "branchnr": "1", "level": "0"},
            headers={"User-Agent": BROWSER_UA, "Cookie": BROWSER_COOKIE,
                     "Referer": f"http://192.168.1.11/password.rsp?sessionid={sid}&level=0&branchnr=1",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                     "Content-Type": "application/x-www-form-urlencoded"},
            follow_redirects=False)
        print(f"\ngetcode(4444) with full browser headers → {r.status_code} {r.headers.get('location','')!r}")

        # Check protect level AFTER code entry
        protect_after, codes_after = await get_protect_level(client, sid, ua=BROWSER_UA, cm=BROWSER_COOKIE)
        print(f"Protect level AFTER code: {protect_after}, codes visible: {codes_after}")

        # Check MCR-BMS with browser UA + cookie
        print(f"\nMCR-BMS children with browser UA+cookie: {await get_mcr_children(client, sid, ua=BROWSER_UA, cm=BROWSER_COOKIE)}")

        # Without UA or cookie
        print(f"MCR-BMS children without headers: {await get_mcr_children(client, sid)}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
