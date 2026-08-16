#!/usr/bin/env python3
"""
Try exact browser sequence: cmcookie with level=0, check menue.rsp Set-Cookie,
try different cookie values.
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

async def get_with_cm(client, sid, path, cm):
    sep = "&" if "?" in path else "?"
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}",
                         headers={"Cookie": f"cmcookie={cm}"}, follow_redirects=False)
    set_cookie = r.headers.get("set-cookie","")
    return r.content.decode("latin-1"), set_cookie

def mainpane_text(raw):
    m = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    p = m.group(1) if m else raw
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', p)).strip()

async def try_code(client, sid, code, level, branchnr, cm):
    r = await client.post(f"{URL}/getcode.rsp",
        data={"code": code, "sessionid": sid, "branchnr": str(branchnr), "level": str(level)},
        headers={"Cookie": f"cmcookie={cm}"},
        follow_redirects=False)
    redirect = r.headers.get("location","")
    set_cookie = r.headers.get("set-cookie","")
    return redirect, set_cookie

async def mcr_children(client, sid, cm):
    """Navigate root → MCR-BMS and return children labels."""
    raw0, sc0 = await get_with_cm(client, sid, "menue.rsp?branchnr=1&level=0", cm)
    if sc0: print(f"  Set-Cookie from level=0: {sc0}")
    raw_mcr, sc_mcr = await get_with_cm(client, sid, "menue.rsp?branchnr=2&level=1", cm)
    if sc_mcr: print(f"  Set-Cookie from MCR-BMS: {sc_mcr}")
    mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw_mcr, re.DOTALL|re.IGNORECASE)
    children = re.findall(r'<td[^>]*>.*?<a[^>]*>([^<]+)</a>', mp.group(1) if mp else "", re.DOTALL|re.IGNORECASE)
    return children

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC (use branchnr=0)
        await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)

        # Test 1: exact browser sequence (level=0, cmcookie=0,0,0,0)
        print("\n=== Test 1: code=4444, level=0, cmcookie=0,0,0,0 ===")
        cm = "0%2C0%2C0%2C0"
        redirect, sc = await try_code(client, sid, "4444", level=0, branchnr=1, cm=cm)
        print(f"redirect: {redirect!r}  set-cookie: {sc!r}")
        # Follow redirect and check its Set-Cookie
        redirect_path = re.sub(r'[?&]sessionid=[^&]+', '', redirect.split("//")[-1].split("/",1)[-1]).lstrip("?&")
        raw_r, sc_r = await get_with_cm(client, sid, redirect_path, cm)
        print(f"redirect page set-cookie: {sc_r!r}")
        print(f"redirect page mainpane: {mainpane_text(raw_r)[:300]}")

        # Test 2: try various cmcookie values to find what reveals timers
        print("\n=== Test 2: try different cmcookie values ===")
        for cm_try in ["3%2C0%2C0%2C0", "4%2C0%2C0%2C0", "4444%2C0%2C0%2C0",
                        "0%2C3%2C0%2C0", "3%2C3%2C3%2C3",
                        "1%2C0%2C0%2C0", "2%2C0%2C0%2C0"]:
            children = await mcr_children(client, sid, cm_try)
            print(f"  cmcookie={cm_try}: MCR-BMS children = {children}")

        # Test 3: check what Set-Cookie the server sends on INITIAL visit
        print("\n=== Test 3: check initial Set-Cookie from HPM pages ===")
        paths = ["", "v0.rsp", "menue.rsp?branchnr=0&level=0", "webfb.rsp"]
        for path in paths:
            r = await client.get(f"{URL}/{path}?sessionid={sid}" if path else f"{URL}/?sessionid={sid}",
                                  follow_redirects=False)
            sc = r.headers.get("set-cookie","(none)")
            print(f"  GET {path or '/'}: Set-Cookie: {sc}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
