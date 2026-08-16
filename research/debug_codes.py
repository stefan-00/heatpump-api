#!/usr/bin/env python3
"""
Try entering 4444 from within MCR-BMS context (level=1).
Check access codes page before/after each code.
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

def mcr_children(raw):
    """Extract child labels from MCR-BMS mainpane."""
    mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    pane = mp.group(1) if mp else raw
    return re.findall(r'<td[^>]*>.*?<a[^>]*>([^<]+)</a>.*?</td>', pane, re.DOTALL|re.IGNORECASE)

async def enter_code(client, sid, code, level, branchnr):
    r = await client.post(f"{URL}/getcode.rsp",
        data={"code": code, "sessionid": sid, "branchnr": str(branchnr), "level": str(level)},
        follow_redirects=False)
    return r.status_code, r.headers.get("location","")

async def check_mcr(client, sid, label=""):
    await get(client, sid, "menue.rsp?branchnr=1&level=0")
    raw = await get(client, sid, "menue.rsp?branchnr=2&level=1")
    children = mcr_children(raw)
    print(f"  MCR-BMS children ({label}): {children}")
    return children

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)
        await get(client, sid, "webfb.rsp")

        # Baseline: no code entered
        print("\n[1] Baseline — no code")
        await check_mcr(client, sid, "no code")

        # Approach A: enter 4444 from root (level=0, branchnr=1)
        print("\n[2] Enter code=4444 from root context (level=0, branchnr=1)")
        sc, loc = await enter_code(client, sid, "4444", level=0, branchnr=1)
        print(f"    → {sc} {loc!r}")
        await asyncio.sleep(1)
        await check_mcr(client, sid, "4444 from root")

        # Approach B: enter 4444 from MCR-BMS context (level=1, branchnr=1)
        print("\n[3] Navigate to MCR-BMS, then enter code=4444 from there (level=1, branchnr=1)")
        await get(client, sid, "menue.rsp?branchnr=1&level=0")
        await get(client, sid, "menue.rsp?branchnr=2&level=1")  # navigate into MCR-BMS
        sc, loc = await enter_code(client, sid, "4444", level=1, branchnr=1)
        print(f"    → {sc} {loc!r}")
        await asyncio.sleep(1)
        await check_mcr(client, sid, "4444 from MCR-BMS ctx")

        # Try code 0000 (user says this = no timers)
        print("\n[4] Enter code=0000 from root")
        sc, loc = await enter_code(client, sid, "0000", level=0, branchnr=1)
        print(f"    → {sc} {loc!r}")
        await asyncio.sleep(1)
        await check_mcr(client, sid, "0000")

        # Try code 9999 (level 1 from the access codes page)
        print("\n[5] Enter code=9999 from root")
        sc, loc = await enter_code(client, sid, "9999", level=0, branchnr=1)
        print(f"    → {sc} {loc!r}")
        await asyncio.sleep(1)
        await check_mcr(client, sid, "9999")

        # Try code 1111 (level 2)
        print("\n[6] Enter code=1111 from root")
        sc, loc = await enter_code(client, sid, "1111", level=0, branchnr=1)
        print(f"    → {sc} {loc!r}")
        await asyncio.sleep(1)
        await check_mcr(client, sid, "1111")

        # Check the access codes page to see current protect level
        print("\n[7] Global > service > access codes page")
        await get(client, sid, "menue.rsp?branchnr=1&level=0")
        await get(client, sid, "menue.rsp?branchnr=1&level=1")  # global
        await get(client, sid, "menue.rsp?branchnr=1&level=2")  # service
        raw_codes = await get(client, sid, "menue.rsp?branchnr=1&level=3")  # access codes
        mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw_codes, re.DOTALL|re.IGNORECASE)
        print(re.sub(r"<[^>]+>", " ", (mp.group(1) if mp else raw_codes)).strip())

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
