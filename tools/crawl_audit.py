#!/usr/bin/env python3
"""crawl_audit.py — Is a URL crawlable AND indexable?  (Lesson 0002)

Two gates a page must pass before it can ever rank:
  CRAWL  — a bot is allowed to fetch it (robots.txt) and it returns success
  INDEX  — nothing tells the engine to drop it (noindex) and it has the
           minimum signals an index entry needs (title, canonical)

Usage:
    python3 crawl_audit.py https://example.com/some/page
    python3 crawl_audit.py --demo      # offline self-check, no network

Stdlib only (no pip); imports the shared seolib core — see CONTEXT.md / ADR 0001.
"""
import sys
import urllib.robotparser
from urllib.parse import urlparse

from seolib import checklist, fetch, parse

# ponytail: robots.txt matching is prefix-based, so the bare token "Googlebot"
# matches Google's rules fine. Swap to your own UA to test as a different bot.
UA = "Googlebot"


def robots_allows(url):
    p = urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return True  # ponytail: unreachable robots.txt => allowed, same as Google
    return rp.can_fetch(UA, url)


def audit(url, *, fetcher=fetch, robots_ok=robots_allows):
    """Return list of (gate, label, passed) checks.

    fetcher/robots_ok are the seams — inject a seolib.fixture and a stub to
    exercise this end-to-end offline (see tools/test_seolib.py).
    """
    rows = [("CRAWL", "robots.txt allows the bot", robots_ok(url))]
    try:
        resp = fetcher(url, ua=UA)
    except Exception as e:
        rows.append(("CRAWL", f"page fetches OK ({e})", False))
        return rows
    rows.append(("CRAWL", f"page returns success ({resp.status})", 200 <= resp.status < 400))

    pg = parse(resp.body)
    meta_robots = (pg.meta.get("robots") or "").lower()
    noindex = "noindex" in resp.header("x-robots-tag").lower() or "noindex" in meta_robots
    rows.append(("INDEX", "no noindex directive", not noindex))
    rows.append(("INDEX", "has a <title>", bool(pg.title)))
    rows.append(("INDEX", "declares a canonical URL", bool(pg.canonical)))
    if resp.url != url:
        rows.append(("CRAWL", f"note: redirected to {resp.url}", True))
    return rows


def report(url):
    rows = audit(url)
    body = [f"[{checklist.mark(ok)}] {gate:5} · {label}" for gate, label, ok in rows]
    blocking = [r for r in rows if not r[2]]
    verdict = (f"VERDICT: cannot be indexed yet — {len(blocking)} gate(s) failing."
               if blocking
               else "VERDICT: crawlable + indexable. (Ranking is a separate fight.)")
    print(checklist.render(f"Audit: {url}", body, verdict, width=48))
    return rows


def demo():
    """Offline self-check: parsing (via seolib.page) must surface index signals."""
    good = parse('<html><head><title>Hi</title>'
                 '<link rel="canonical" href="https://x.com/a"></head><body>ok</body></html>')
    assert good.title == "Hi", good.title
    assert good.canonical == "https://x.com/a", good.canonical
    assert good.meta.get("robots") is None

    bad = parse('<html><head><meta name="robots" content="NOINDEX, nofollow">'
                '</head><body>x</body></html>')
    assert "noindex" in (bad.meta.get("robots") or "").lower(), bad.meta
    assert bad.title is None and bad.canonical is None
    print("demo: all parser assertions passed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--demo":
        demo()
    else:
        report(sys.argv[1])
