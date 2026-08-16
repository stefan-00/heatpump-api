#!/usr/bin/env python3
"""
Fetch password.rsp from both root WEB-RC context and MCR-BMS context.
Compare form fields to see if branchnr/level differ.
Also dump the raw HTML of menue.rsp root to see what cmcookie the server expects.
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

async def get(client, sid, path, cm=None):
    sep = "&" if "?" in path else "?"
    hdrs = {"Cookie": f"cmcookie={cm}"} if cm else {}
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}",
                         headers=hdrs, follow_redirects=False)
    return r.content.decode("latin-1")

def extract_forms(html):
    """Find all <form> tags and their hidden inputs."""
    forms = []
    for fm in re.finditer(r'<form[^>]*>(.*?)</form>', html, re.DOTALL|re.IGNORECASE):
        action_m = re.search(r'action=["\']([^"\']+)["\']', fm.group(0), re.IGNORECASE)
        inputs = re.findall(r'<input[^>]+>', fm.group(1), re.IGNORECASE)
        fields = {}
        for inp in inputs:
            name_m  = re.search(r'name=["\']([^"\']+)["\']', inp, re.IGNORECASE)
            value_m = re.search(r'value=["\']([^"\']*)["\']', inp, re.IGNORECASE)
            type_m  = re.search(r'type=["\']([^"\']+)["\']', inp, re.IGNORECASE)
            if name_m:
                fields[name_m.group(1)] = {
                    "value": value_m.group(1) if value_m else "",
                    "type": type_m.group(1) if type_m else "text",
                }
        forms.append({"action": action_m.group(1) if action_m else "?", "fields": fields})
    return forms

def find_links(html, keyword=""):
    """Find all <a href> links, optionally filtered by keyword."""
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', html, re.IGNORECASE)
    if keyword:
        return [(h,t) for h,t in links if keyword.lower() in t.lower() or keyword.lower() in h.lower()]
    return links

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC
        await client.get(f"{URL}/webfb.rsp?sessionid={sid}", follow_redirects=False)

        cm = "0%2C0%2C0%2C0"

        # ── Step 1: root WEB-RC page ──────────────────────────────────────────
        print("\n=== Root WEB-RC (branchnr=0, level=0) ===")
        root = await get(client, sid, "menue.rsp?branchnr=0&level=0", cm)
        pwd_links = find_links(root, "password")
        code_links = find_links(root, "code")
        print(f"password.rsp links: {pwd_links}")
        print(f"code links: {code_links}")
        all_links = find_links(root)
        print(f"all hrefs: {all_links[:20]}")

        # ── Step 2: navigate to level 1 (WEB-RC children) ────────────────────
        print("\n=== Level 1 items ===")
        lv1 = await get(client, sid, "menue.rsp?branchnr=1&level=1", cm)
        pwd_links2 = find_links(lv1, "password")
        print(f"password.rsp links at level=1: {pwd_links2}")
        all_links2 = find_links(lv1)
        print(f"all hrefs: {all_links2[:20]}")

        # ── Step 3: fetch password.rsp from root context ──────────────────────
        print("\n=== password.rsp from root context (level=0, branchnr=1) ===")
        pwd0 = await get(client, sid, "password.rsp?level=0&branchnr=1", cm)
        forms0 = extract_forms(pwd0)
        for f in forms0:
            print(f"  action={f['action']}  fields={f['fields']}")
        # Also print raw for inspection
        print(f"  raw (first 800): {re.sub(chr(10)+r'+', ' ', pwd0)[:800]}")

        # ── Step 4: navigate to MCR-BMS, then fetch password.rsp ──────────────
        print("\n=== Navigate to MCR-BMS ===")
        await get(client, sid, "menue.rsp?branchnr=1&level=0", cm)  # reset to root
        mcr = await get(client, sid, "menue.rsp?branchnr=2&level=1", cm)  # MCR-BMS
        pwd_links_mcr = find_links(mcr, "password")
        print(f"password.rsp links in MCR-BMS: {pwd_links_mcr}")
        all_links_mcr = find_links(mcr)
        print(f"MCR-BMS all hrefs: {all_links_mcr[:20]}")

        # ── Step 5: fetch password.rsp from MCR-BMS context ───────────────────
        print("\n=== password.rsp from MCR-BMS context ===")
        # Try common levels
        for level in ["0", "1", "2"]:
            pwd_mcr = await get(client, sid, f"password.rsp?level={level}&branchnr=1", cm)
            forms_mcr = extract_forms(pwd_mcr)
            print(f"  level={level}: action forms: {forms_mcr}")

        # ── Step 6: directly fetch the protect page to see its raw content ────
        print("\n=== Access codes page (raw) ===")
        await get(client, sid, "menue.rsp?branchnr=1&level=0", cm)
        await get(client, sid, "menue.rsp?branchnr=1&level=1", cm)
        await get(client, sid, "menue.rsp?branchnr=1&level=2", cm)
        raw3 = await get(client, sid, "menue.rsp?branchnr=1&level=3", cm)
        print(raw3[:2000])

        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

asyncio.run(main())
