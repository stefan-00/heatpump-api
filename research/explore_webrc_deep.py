#!/usr/bin/env python3
"""
Deep WEB-RC explorer.

Key insight: branchnr is position-indexed WITHIN the parent, not global.
The server does NOT cleanly reset context when jumping between siblings at
the same level — you MUST return to level=0 (root) before navigating to a
different top-level branch. This was validated by the debug script.

Navigation rule: before visiting ANY level=1 branch, always re-navigate to
level=0 first to give the server a clean root context.
"""

import asyncio
import html as html_module
import os
import re
from dataclasses import dataclass, field
from urllib.parse import parse_qs

import httpx

URL  = os.environ["HEATPUMP_URL"].rstrip("/")
USER = os.environ["HEATPUMP_USERNAME"]
PASS = os.environ["HEATPUMP_PASSWORD"]

MAX_DEPTH = 8


# ── HTTP ──────────────────────────────────────────────────────────────────────

async def login(client: httpx.AsyncClient) -> str:
    for attempt in range(5):
        r = await client.get(f"{URL}/", follow_redirects=False)
        loc = r.headers.get("location", "")
        m = re.search(r"sessionid=([^&]+)", loc)
        if not m:
            print(f"  [login] no sessionid, waiting...")
            await asyncio.sleep(20)
            continue
        sid = m.group(1)
        r2 = await client.post(
            f"{URL}/getlogin.rsp",
            data={"user": USER, "code": PASS[:8], "sessionid": sid},
            follow_redirects=False,
        )
        if "sorry" in r2.headers.get("location", "").lower():
            print(f"  [login] session full, retrying ({attempt+1}/5)...")
            await asyncio.sleep(20)
            continue
        print(f"  [login] sid={sid}")
        return sid
    raise RuntimeError("login failed")


async def get(client: httpx.AsyncClient, sid: str, path: str) -> str:
    sep = "&" if "?" in path else "?"
    r = await client.get(f"{URL}/{path}{sep}sessionid={sid}", follow_redirects=False)
    if "login.rsp" in r.headers.get("location", ""):
        raise RuntimeError("session expired")
    return r.content.decode("latin-1")


# ── Parsing ───────────────────────────────────────────────────────────────────

def mainpane(raw: str) -> str:
    m = re.search(r'id="mainpane"[^>]*>(.*?)</div>', raw, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else raw


def child_links(raw: str) -> list[tuple[str, str, str]]:
    """Extract (label, bn, lv) from <td> elements of the mainpane only."""
    pane = mainpane(raw)
    results = []
    for td in re.findall(r"<td[^>]*>(.*?)</td>", pane, re.DOTALL | re.IGNORECASE):
        for m in re.finditer(
            r'href=["\']menue\.rsp\?([^"\']+)["\'][^>]*>\s*([^<]+)',
            html_module.unescape(td), re.IGNORECASE,
        ):
            qs = parse_qs(m.group(1))
            bn = qs.get("branchnr", ["?"])[0]
            lv = qs.get("level",    ["?"])[0]
            label = m.group(2).strip()
            results.append((label, bn, lv))
    return results


def params(raw: str) -> list[dict]:
    out = []
    # vinfo read-only anchors
    for m in re.finditer(
        r'href=["\']vinfo\.rsp\?[^"\']*?id=([^:&"\'\s]+)[^"\']*["\'][^>]*>\s*([^<]+)',
        raw, re.IGNORECASE,
    ):
        pid, val = m.group(1).strip(), m.group(2).strip()
        if pid and val:
            out.append({"id": pid, "value": val, "writable": False, "type": "anchor"})

    # input elements
    for m in re.finditer(r'<input([^>]+)>', raw, re.IGNORECASE):
        attrs = m.group(1)
        name = re.search(r'name=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        val  = re.search(r'value=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        typ  = re.search(r'type=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        if not name:
            continue
        n = name.group(1)
        t = (typ.group(1) if typ else "text").lower()
        if n.lower() == "sessionid" or t in ("submit", "hidden", "button", "image"):
            continue
        if any(p["id"] == n for p in out):
            continue
        out.append({"id": n, "value": val.group(1) if val else "", "writable": True, "type": f"input[{t}]"})

    # select dropdowns
    for m in re.finditer(
        r'<select[^>]+name=["\']([^"\']+)["\'][^>]*>(.*?)</select>',
        raw, re.DOTALL | re.IGNORECASE,
    ):
        n = m.group(1)
        if n.lower() == "sessionid":
            continue
        body = m.group(2)
        sel  = re.search(r'<option[^>]+selected[^>]*>\s*([^<]+)', body, re.IGNORECASE)
        opts = re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>\s*([^<]+)', body, re.IGNORECASE)
        value = sel.group(1).strip() if sel else "?"
        opts_str = " | ".join(f"{v}={t.strip()}" for v, t in opts)
        out.append({"id": n, "value": value, "writable": True, "type": "select", "options": opts_str})

    return out


def rows(raw: str) -> list[list[str]]:
    result = []
    pane = mainpane(raw)
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", pane, re.DOTALL | re.IGNORECASE):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.DOTALL | re.IGNORECASE)
        row = []
        for cell in cells:
            inp  = re.search(r'<input[^>]+value=["\']([^"\']*)["\']', cell, re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", cell).strip()
            text = re.sub(r"\s+", " ", text)
            if inp:
                text = f"{text} [v={inp.group(1)}]"
            row.append(text)
        if any(c.strip() for c in row):
            result.append(row)
    return result


# ── Tree node ─────────────────────────────────────────────────────────────────

@dataclass
class Node:
    label:    str
    bn:       str
    lv:       str
    children: list = field(default_factory=list)
    params:   list = field(default_factory=list)
    rows:     list = field(default_factory=list)
    error:    bool = False


# ── Crawler ───────────────────────────────────────────────────────────────────

async def crawl(
    client: httpx.AsyncClient,
    sid: str,
    node: Node,
    parent_path: tuple,          # nav path from root to parent (for re-entry)
    get_root: "callable",        # coroutine that returns the root page
    depth: int = 0,
) -> None:
    if depth > MAX_DEPTH:
        return

    indent = "  " * depth
    nav = f"menue.rsp?branchnr={node.bn}&level={node.lv}"
    print(f"{indent}GET {nav}  [{node.label}]")

    raw = await get(client, sid, nav)

    if "Cannot find sub menu" in raw:
        node.error = True
        print(f"{indent}  → error")
        return

    node.params = params(raw)
    node.rows   = rows(raw)

    links = child_links(raw)
    for (label, bn, lv) in links:
        child = Node(label=label, bn=bn, lv=lv)
        node.children.append(child)

    # Navigate to each child — parent context is already set (we just fetched this node).
    # For siblings after the first, we need to reset to this node's context again.
    for i, child in enumerate(node.children):
        if i > 0:
            # Re-fetch this node to re-establish parent context on server
            print(f"{indent}  [re-enter parent to set context for sibling #{i+1}]")
            await _re_enter_path(client, sid, parent_path + ((node.bn, node.lv),))
        await crawl(client, sid, child, parent_path + ((node.bn, node.lv),), get_root, depth + 1)


async def _re_enter_path(client: httpx.AsyncClient, sid: str, path: tuple) -> None:
    """Re-navigate from level=0 through each ancestor to restore server context."""
    # Always start from level=0 (clean root state)
    await get(client, sid, "menue.rsp?branchnr=1&level=0")
    for (bn, lv) in path:
        await get(client, sid, f"menue.rsp?branchnr={bn}&level={lv}")


# ── Output ────────────────────────────────────────────────────────────────────

def print_tree(node: Node, depth: int = 0) -> None:
    indent = "  " * depth
    has = node.params or node.rows
    flag = " ✎" if any(p["writable"] for p in node.params) else (" *" if has else "")
    err  = " [ERROR]" if node.error else ""
    print(f"\n{indent}{'─'*50}")
    print(f"{indent}[{node.label}]{flag}{err}  (bn={node.bn}, lv={node.lv})")
    if node.rows:
        for row in node.rows:
            clean = [c for c in row if c.strip() and c not in ("-", "---")]
            if clean:
                print(f"{indent}  | {' | '.join(clean)}")
    if node.params:
        for p in node.params:
            w    = "WRITE" if p["writable"] else "read "
            opts = f"  [{p.get('options','')}]" if p.get("options") else ""
            print(f"{indent}  {w}  {p['id']:28s}  {p['value']!r}{opts}")
    for child in node.children:
        print_tree(child, depth + 1)


def to_md(node: Node, depth: int = 0) -> list[str]:
    lines = []
    hdr   = "#" * min(depth + 2, 6)
    flag  = " ✏️" if any(p["writable"] for p in node.params) else ""
    lines.append(f"\n{hdr} {node.label}{flag}  _(bn={node.bn}, lv={node.lv})_\n\n")
    if node.error:
        lines.append("_Error page_\n\n")
        return lines
    if node.rows:
        max_c = max((len(r) for r in node.rows), default=1)
        lines.append("| " + " | ".join([""] * max_c) + " |\n")
        lines.append("|" + "---|" * max_c + "\n")
        for row in node.rows[:60]:
            cols = [(c or "").replace("|", "\\|") for c in row]
            while len(cols) < max_c:
                cols.append("")
            lines.append("| " + " | ".join(cols) + " |\n")
        lines.append("\n")
    if node.params:
        lines.append("| ID | Value | Access | Options |\n")
        lines.append("|-----|-------|--------|--------|\n")
        for p in node.params:
            w    = "**WRITE**" if p["writable"] else "read"
            opts = (p.get("options") or "")
            lines.append(f"| `{p['id']}` | `{p['value']}` | {w} | {opts} |\n")
        lines.append("\n")
    for child in node.children:
        lines.extend(to_md(child, depth + 1))
    return lines


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    print(f"Target: {URL}\n")
    async with httpx.AsyncClient(timeout=30) as client:
        sid = await login(client)

        # Enter WEB-RC
        await get(client, sid, "webfb.rsp")

        # Elevate to level 3 (4444).
        # Browser sends: code + Set=OK + sessionid + branchnr=1 + level=0
        # Set=OK (submit button value) is required — server ignores the code without it.
        # Must also follow the 302 redirect before navigating further.
        r = await client.post(
            f"{URL}/getcode.rsp",
            data={"code": "4444", "Set": "OK", "sessionid": sid, "branchnr": "1", "level": "0"},
            follow_redirects=False,
        )
        elev_loc = r.headers.get("location", "")
        if r.status_code == 302 and "menue.rsp" in elev_loc:
            print(f"[elevate] SUCCESS (302 → {elev_loc})")
        else:
            print(f"[elevate] FAILED status={r.status_code} loc={elev_loc!r}")

        # Root level — follow the redirect target to let the server commit session state
        raw_root = await get(client, sid, "menue.rsp?branchnr=1&level=0")
        print(f"[root] {len(raw_root)} bytes")

        top = child_links(raw_root)
        print(f"[top-level sections] {[(l,bn,lv) for l,bn,lv in top]}\n")

        root = Node(label="WEB-RC root", bn="1", lv="0")
        root.rows = rows(raw_root)
        for (label, bn, lv) in top:
            root.children.append(Node(label=label, bn=bn, lv=lv))

        # Crawl each top-level section.
        # Before each top-level visit, always reset to level=0 first.
        for i, child in enumerate(root.children):
            print(f"\n{'='*60}")
            print(f"SECTION: {child.label}  (bn={child.bn}, lv={child.lv})")
            print(f"{'='*60}")

            # Reset to root before each top-level section
            await get(client, sid, "menue.rsp?branchnr=1&level=0")

            await crawl(
                client, sid, child,
                parent_path=(),           # root has no ancestors
                get_root=None,
                depth=1,
            )

        # Logout
        await client.get(f"{URL}/leave.rsp?sessionid={sid}", follow_redirects=False)
        print("\n[logout]")

    print("\n" + "="*70)
    print("FULL WEB-RC TREE")
    print("="*70)
    print_tree(root)

    out = "/Users/steake/devel/projects/stefan/heatpump/webrc_deep_dump.md"
    lines = ["# WEB-RC Full Tree (access level 4444)\n\n"]
    lines.extend(to_md(root))
    with open(out, "w") as f:
        f.writelines(lines)
    print(f"\n\nSaved → {out}")


if __name__ == "__main__":
    asyncio.run(main())
