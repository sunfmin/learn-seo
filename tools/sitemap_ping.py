#!/usr/bin/env python3
"""sitemap_ping.py — the publish-and-notify step.  (Lesson 0007)

Once a page is server-rendered (0006) you still have to TELL engines it exists
or changed. Two mechanisms, wildly asymmetric — same shape as every other
split in this course:

  sitemap.xml   PASSIVE discovery. A list of your URLs the engine pulls on its
                own schedule. EVERY engine uses it, Google included. Slow.
  IndexNow      ACTIVE push. You POST changed URLs and Bing/Yandex/Naver/Seznam
                fetch within minutes — and share the ping with each other.
                GOOGLE DOES NOT PARTICIPATE; it ignores IndexNow and relies on
                its own crawl scheduling + sitemaps.

So a publishing pipeline does BOTH: emit/submit a sitemap (for Google &
everyone), and fire IndexNow on change (instant on the engines that take it,
several of which feed AI search). This tool is the offline, testable core:
build + validate a sitemap, and build + validate an IndexNow payload. It only
touches the network if you pass `indexnow ... --send`.

Stdlib only. No pip install.

Usage:
    python3 sitemap_ping.py gen urls.txt > sitemap.xml
        # urls.txt: one URL per line, optional  <space|tab>  lastmod (W3C date)

    python3 sitemap_ping.py check sitemap.xml

    python3 sitemap_ping.py indexnow https://site.com/a https://site.com/b \\
        --key 8e1f...  [--key-location https://site.com/8e1f.txt] [--send]

    python3 sitemap_ping.py --demo      # offline self-check, no network
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from xml.sax.saxutils import escape

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SITEMAP_MAX_URLS = 50_000
SITEMAP_MAX_BYTES = 52_428_800          # 50 MB, per sitemaps.org
INDEXNOW_MAX_URLS = 10_000              # per POST, per indexnow.org
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_RE = re.compile(r"^[A-Za-z0-9-]{8,128}$")
# W3C Datetime: YYYY-MM-DD, optionally with time + timezone (or Z).
W3C_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}"
    r"([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$")


# ---------- sitemap ----------

def valid_w3c_date(s):
    if not W3C_DATE_RE.match(s):
        return False
    y, m, d = (int(x) for x in s[:10].split("-"))
    return 1 <= m <= 12 and 1 <= d <= 31 and y >= 1


def build_sitemap(entries):
    """entries: list of (loc, lastmod_or_None) -> sitemap XML string."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<urlset xmlns="{SITEMAP_NS}">']
    for loc, lastmod in entries:
        out.append("  <url>")
        out.append(f"    <loc>{escape(loc)}</loc>")
        if lastmod:
            out.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
        out.append("  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def parse_url_file(text):
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        entries.append((parts[0], parts[1].strip() if len(parts) > 1 else None))
    return entries


def _local(tag):
    return tag.split("}", 1)[-1]


def validate_sitemap(data):
    """Return list of (label, ok, detail) checks against the sitemaps.org spec."""
    raw = data.encode("utf-8") if isinstance(data, str) else data
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return [("well-formed XML", False, str(e))]

    rows = [("well-formed XML", True, "")]
    rows.append(("root is <urlset>", _local(root.tag) == "urlset", _local(root.tag)))
    urls = [u for u in root if _local(u.tag) == "url"]

    def child(u, name):
        for c in u:
            if _local(c.tag) == name and (c.text or "").strip():
                return c.text.strip()
        return None

    rows.append(("every <url> has a <loc>",
                 bool(urls) and all(child(u, "loc") for u in urls),
                 f"{len(urls)} urls"))
    rows.append((f"<= {SITEMAP_MAX_URLS:,} URLs",
                 len(urls) <= SITEMAP_MAX_URLS, f"{len(urls)}"))
    rows.append(("<= 50 MB uncompressed",
                 len(raw) <= SITEMAP_MAX_BYTES, f"{len(raw):,} bytes"))

    hosts, bad_dates = set(), []
    for u in urls:
        loc = child(u, "loc")
        if loc:
            hosts.add(urlparse(loc).netloc.lower())
        lm = child(u, "lastmod")
        if lm and not valid_w3c_date(lm):
            bad_dates.append(lm)
    rows.append(("all URLs share one host", len(hosts) <= 1, ", ".join(sorted(hosts)) or "-"))
    rows.append(("lastmod dates valid (W3C)", not bad_dates,
                 f"{len(bad_dates)} bad: {bad_dates[:3]}" if bad_dates else "ok"))
    return rows


# ---------- indexnow ----------

def valid_key(key):
    return bool(KEY_RE.match(key))


def indexnow_payload(urls, key, key_location=None):
    """Build + validate the IndexNow POST body. Raises ValueError on any breach."""
    if not valid_key(key):
        raise ValueError("key must be 8-128 chars of [a-z A-Z 0-9 -]")
    if not urls:
        raise ValueError("no URLs to submit")
    if len(urls) > INDEXNOW_MAX_URLS:
        raise ValueError(f"max {INDEXNOW_MAX_URLS:,} URLs per post, got {len(urls)}")
    hosts = {urlparse(u).netloc.lower() for u in urls}
    if len(hosts) != 1:
        raise ValueError(f"all URLs must share one host; got {sorted(hosts)}")
    host = hosts.pop()
    key_location = key_location or f"https://{host}/{key}.txt"
    if urlparse(key_location).netloc.lower() != host:
        raise ValueError("keyLocation must be on the same host as the URLs")
    return {"host": host, "key": key, "keyLocation": key_location, "urlList": urls}


def indexnow_send(payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return getattr(r, "status", 200)


# ---------- reports ----------

def report_check(data):
    rows = validate_sitemap(data)
    print("\n  Sitemap check\n  " + "-" * 52)
    for label, ok, detail in rows:
        mark = "PASS" if ok else "FAIL"
        tail = f"  ({detail})" if detail else ""
        print(f"  [{mark}] {label}{tail}")
    bad = [r for r in rows if not r[1]]
    print("  " + "-" * 52)
    print("  VERDICT: valid sitemap.\n" if not bad
          else f"  VERDICT: {len(bad)} problem(s) — engines may reject it.\n")
    return rows


def report_indexnow(payload, send=False):
    print("\n  IndexNow submission")
    print("  " + "-" * 52)
    print(f"  host         {payload['host']}")
    print(f"  keyLocation  {payload['keyLocation']}")
    print(f"  urlList      {len(payload['urlList'])} URL(s)")
    print("  " + "-" * 52)
    print(f"  1) put your key in a UTF-8 file at: {payload['keyLocation']}")
    print(f"     (file contents = the key: {payload['key']})")
    print(f"  2) POST this body to {INDEXNOW_ENDPOINT} :")
    print("     " + json.dumps(payload, indent=2).replace("\n", "\n     "))
    print("\n  Reaches Bing/Yandex/Naver/Seznam (shared). Google ignores IndexNow —")
    print("  it discovers this URL via your sitemap + its own crawl schedule.")
    if send:
        try:
            status = indexnow_send(payload)
            print(f"\n  --send: POSTed. HTTP {status} "
                  f"({'accepted' if status in (200, 202) else 'check key/host'}).\n")
        except Exception as e:
            print(f"\n  --send FAILED: {e}\n")
    else:
        print("  (dry run — add --send to actually POST.)\n")


# ---------- demo ----------

def demo():
    sm = build_sitemap([
        ("https://site.com/a", "2026-06-19"),
        ("https://site.com/b", "2026-06-18T10:30:00+09:00"),
    ])
    rows = {label: ok for label, ok, _ in validate_sitemap(sm)}
    assert all(rows.values()), f"clean sitemap should pass all: {rows}"

    bad = build_sitemap([
        ("https://site.com/a", "June 19"),       # bad date
        ("https://OTHER.com/b", None),           # second host
    ])
    brows = {label: ok for label, ok, _ in validate_sitemap(bad)}
    assert not brows["all URLs share one host"], "multi-host not caught"
    assert not brows["lastmod dates valid (W3C)"], "bad date not caught"

    assert validate_sitemap("<urlset><nope")[0] == ("well-formed XML", False,
        validate_sitemap("<urlset><nope")[0][2]), "malformed not caught"

    assert valid_w3c_date("2026-06-19")
    assert valid_w3c_date("2026-06-19T10:30:00Z")
    assert not valid_w3c_date("2026-13-40")
    assert not valid_w3c_date("19/06/2026")

    p = indexnow_payload(["https://site.com/a", "https://site.com/b"], "abcd1234EF-x")
    assert p == {"host": "site.com", "key": "abcd1234EF-x",
                 "keyLocation": "https://site.com/abcd1234EF-x.txt",
                 "urlList": ["https://site.com/a", "https://site.com/b"]}, p

    for bad_call, why in [
        (lambda: indexnow_payload(["https://site.com/a"], "short"), "short key"),
        (lambda: indexnow_payload(["https://a.com/x", "https://b.com/y"], "abcd1234"), "multi-host"),
        (lambda: indexnow_payload(["https://a.com/x"], "abcd1234",
                                  key_location="https://b.com/k.txt"), "wrong keyLocation host"),
    ]:
        try:
            bad_call()
            raise AssertionError(f"should have rejected: {why}")
        except ValueError:
            pass

    print("demo: all sitemap_ping assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif len(args) == 2 and args[0] == "gen":
        with open(args[1], encoding="utf-8") as fh:
            sys.stdout.write(build_sitemap(parse_url_file(fh.read())))
    elif len(args) == 2 and args[0] == "check":
        with open(args[1], encoding="utf-8") as fh:
            report_check(fh.read())
    elif args and args[0] == "indexnow":
        rest = args[1:]
        if "--key" not in rest:
            sys.exit("indexnow: --key is required")
        ki = rest.index("--key")
        key = rest[ki + 1]
        send = "--send" in rest
        key_loc = None
        if "--key-location" in rest:
            key_loc = rest[rest.index("--key-location") + 1]
        skip = {key}
        if key_loc:
            skip.add(key_loc)
        urls = [a for i, a in enumerate(rest)
                if a.startswith(("http://", "https://")) and a not in skip]
        try:
            report_indexnow(indexnow_payload(urls, key, key_loc), send=send)
        except ValueError as e:
            sys.exit(f"indexnow: {e}")
    else:
        sys.exit(__doc__)
