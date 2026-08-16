#!/usr/bin/env python3
"""
Try entering codes in sequence and check protect level after each.
Also try combinations and the install code if accessible.
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

async def enter_code(client, sid, code, from_level=1):
    r = await client.post(f"{URL}/getcode.rsp",
        data={"code": code, "sessionid": sid, "branchnr": "1", "level": str(from_level)},
        headers={"Cookie": "cmcookie=0%2C0%2C0%2C0"},
        follow_redirects=False)
    return r.status_code, r.headers.get("location","")

async def get_protect(client, sid):
    await get(client, sid, "menue.rsp?branchnr=1&level=0")
    await get(client, sid, "menue.rsp?branchnr=1&level=1")  # global
    await get(client, sid, "menue.rsp?branchnr=1&level=2")  # service
    raw = await get(client, sid, "menue.rsp?branchnr=1&level=3")  # access codes
    protect = re.search(r'protect\s+(\d+)', raw)
    # Extract all level N XXXX pairs
    codes = re.findall(r'level\s+(\S+)\s+(\d+)', raw)
    mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', mp.group(1) if mp else raw)).strip()
    return protect.group(1) if protect else "?", codes, plain

async def get_mcr(client, sid):
    await get(client, sid, "menue.rsp?branchnr=1&level=0")
    raw = await get(client, sid, "menue.rsp?branchnr=2&level=1")
    mp = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL|re.IGNORECASE)
    return re.findall(r'<td[^>]*>.*?<a[^>]*>([^<]+)</a>', mp.group(1) if mp else "", re.DOTALL|re.IGNORECASE)

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)
        await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)
        await get(client, sid, "menue.rsp?branchnr=2&level=1")  # enter MCR-BMS ctx

        print("=== Baseline ===")
        p, c, txt = await get_protect(client, sid)
        print(f"protect={p}  codes={c}")
        print(f"access codes page: {txt}")
        print(f"MCR-BMS: {await get_mcr(client, sid)}")

        # Try code sequence: 9999 first
        for code in ["9999", "1111", "4444"]:
            sc, loc = await enter_code(client, sid, code, from_level=1)
            print(f"\n=== After entering {code} (sc={sc}) ===")
            p, c, txt = await get_protect(client, sid)
            print(f"protect={p}  codes={c}")
            print(f"access codes page: {txt}")
            print(f"MCR-BMS: {await get_mcr(client, sid)}")

        # Try higher codes that might exist
        for code in ["8888", "5555", "3333", "2222", "1234", "0001"]:
            sc, loc = await enter_code(client, sid, code, from_level=1)
            print(f"\n=== Code {code} → sc={sc} redirect={loc!r} ===")
            p, _, _ = await get_protect(client, sid)
            mcr = await get_mcr(client, sid)
            print(f"protect={p}  MCR-BMS={mcr}")

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
