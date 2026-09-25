"""Read-only HPM probe: dump the parameter anchors on view pages, or the vinfo.rsp page for one id.

Credentials come from research/.env.local (gitignored), falling back to the environment:
HEATPUMP_URL, HEATPUMP_USERNAME, HEATPUMP_PASSWORD.

Usage: python research/probe_view_pages.py v30.rsp v3.rsp vinfo:16:6.2.15
       python research/probe_view_pages.py --save heatpump-api/tests/fixtures v21.rsp v30.rsp

--save DIR writes each page's raw HTML to DIR/<page>.html (e.g. v30.html) with the
session id replaced by SESSIONID, for use as parser test fixtures.

Logs out via leave.rsp on exit — the device's session pool is tiny and long-lived.
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

ENV_FILE = Path(__file__).with_name(".env.local")
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and not key.strip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip())

args = sys.argv[1:]
save_dir = None
if args[:1] == ["--save"]:
    save_dir = Path(args[1])
    save_dir.mkdir(parents=True, exist_ok=True)
    args = args[2:]

URL = os.environ["HEATPUMP_URL"].rstrip("/")
client = httpx.Client(follow_redirects=False, timeout=20)

r = client.get(URL + "/")
sid = parse_qs(urlparse(r.headers["location"]).query)["sessionid"][0]
r = client.post(
    URL + "/getlogin.rsp",
    data={
        "user": os.environ["HEATPUMP_USERNAME"],
        "code": os.environ["HEATPUMP_PASSWORD"][:8],
        "sessionid": sid,
    },
)
print("login", r.status_code)


def get(path: str, **params: str) -> str:
    params["sessionid"] = sid
    return client.get(f"{URL}/{path}", params=params).content.decode("latin-1")


def mainpane_text(html: str) -> str:
    m = re.search(r"<!-- start_mainpane -->(.*?)<!-- end_mainpane -->", html, re.S)
    text = re.sub(r"<[^>]+>", " ", m.group(1) if m else html)
    return re.sub(r"\s+", " ", text).strip()


try:
    for arg in args:
        if arg.startswith("vinfo:"):
            print(f"== vinfo {arg[6:]}: {mainpane_text(get('vinfo.rsp', id=arg[6:]))[:400]}")
            continue
        print(f"== {arg}")
        html = get(arg)
        if save_dir is not None:
            out = save_dir / (arg.removesuffix(".rsp") + ".html")
            out.write_text(html.replace(sid, "SESSIONID"), encoding="latin-1")
            print(f"  saved {out}")
        prev_end = 0
        for m in re.finditer(r'<a[^>]*vinfo\.rsp[^"]*?id=([\d:.]+)"[^>]*>([^<]*)</a>', html):
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html[prev_end:m.start()])).strip()
            prev_end = m.end()
            print(f"  {m.group(1):14} {label[-40:]:40} | {m.group(2).strip()}")
finally:
    client.get(URL + "/leave.rsp", params={"sessionid": sid})
    print("logged out")
