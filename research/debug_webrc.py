#!/usr/bin/env python3
"""Debug script — dumps raw HTML for specific WEB-RC pages."""

import asyncio
import os
import re

import httpx

URL = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]


async def login(client):
    for attempt in range(5):
        r = await client.get(f"{URL}/", follow_redirects=False)
        loc = r.headers.get("location", "")
        m = re.search(r"sessionid=([^&]+)", loc)
        if not m:
            print(f"no sessionid, waiting...")
            await asyncio.sleep(20)
            continue
        sid = m.group(1)
        r2 = await client.post(
            f"{URL}/getlogin.rsp",
            data={"user": USER, "code": PASS[:8], "sessionid": sid},
            follow_redirects=False,
        )
        if "sorry" in r2.headers.get("location", "").lower():
            print(f"session full, waiting...")
            await asyncio.sleep(20)
            continue
        print(f"session: {sid}")
        return sid
    raise RuntimeError("login failed")


async def get(client, sid, path):
    sep = "&" if "?" in path else "?"
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}", follow_redirects=False)
    return r.content.decode("latin-1")


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC
        raw = await get(client, sid, "webfb.rsp")
        print(f"webfb: {len(raw)} bytes")

        # Elevate
        r = await client.post(f"{URL}/getcode.rsp",
            data={"code": "4444", "sessionid": sid}, follow_redirects=False)
        print(f"elevate: {r.status_code}")

        # Try visiting MCR-BMS FIRST (before global), starting at root
        raw0 = await get(client, sid, "menue.rsp?branchnr=1&level=0")
        print(f"\n=== level=0 ===\n{raw0}\n")

        # Now go directly to MCR-BMS (bn=2) WITHOUT visiting global (bn=1, lv=1)
        raw_mcr = await get(client, sid, "menue.rsp?branchnr=2&level=1")
        print(f"\n=== MCR-BMS bn=2 lv=1 ===\n{raw_mcr}\n")

        # Then try MCR-BMS children at level=2
        raw_mcr2 = await get(client, sid, "menue.rsp?branchnr=2&level=2")
        print(f"\n=== MCR-BMS bn=2 lv=2 ===\n{raw_mcr2}\n")

        raw_mcr3 = await get(client, sid, "menue.rsp?branchnr=2&level=3")
        print(f"\n=== MCR-BMS bn=2 lv=3 ===\n{raw_mcr3}\n")

        # Logout
        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("logout done")


asyncio.run(main())
