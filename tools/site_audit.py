#!/usr/bin/env python3
"""site_audit.py — crawl a whole site and run every gate at once.  (Lesson 0009)

The course capstone. Lessons 0002–0008 each checked one signal on one URL;
this walks a site the way a bot does — BFS over internal links from a seed —
and runs the whole checklist on every page it finds, then rolls the findings
up into one prioritized report. Same seolib core (`fetch` + `parse`), same
`checklist` renderer; the new thing is the crawl loop and the aggregation.

The gates, per page:
  CRAWL     page returns success (2xx/3xx)
  INDEX     no noindex · has a <title> · declares a canonical
  RETRIEVE  exactly one <h1> · has JSON-LD · enough body text  (AEO extractability)

Usage:
    python3 site_audit.py https://example.com/         # crawl + audit (≤25 pages)
    python3 site_audit.py https://example.com/ 50      # raise the page cap
    python3 site_audit.py --demo                       # offline self-check, no network

Stdlib only (no pip); imports the shared seolib core — see CONTEXT.md / ADR 0001.
"""
import sys
import urllib.robotparser
from collections import Counter
from urllib.parse import urldefrag, urljoin, urlparse

from seolib import checklist, domain, fetch, parse

UA = "Googlebot"
MAX_PAGES = 25
MIN_WORDS = 100  # below this, a page is too thin to retrieve a self-contained chunk from


def _noindex(resp, pg):
    meta_robots = (pg.meta.get("robots") or "").lower()
    return "noindex" in resp.header("x-robots-tag").lower() or "noindex" in meta_robots


# The capstone checklist: one row per signal the per-lesson tools each owned.
# (gate, label, predicate over (resp, page)). Order is the report order.
CHECKS = [
    ("CRAWL", "page returns success", lambda resp, pg: 200 <= resp.status < 400),
    ("INDEX", "no noindex directive", lambda resp, pg: not _noindex(resp, pg)),
    ("INDEX", "has a <title>", lambda resp, pg: bool(pg.title)),
    ("INDEX", "declares a canonical", lambda resp, pg: bool(pg.canonical)),
    ("RETRIEVE", "exactly one <h1>", lambda resp, pg: pg.headings.get("h1", 0) == 1),
    ("RETRIEVE", "has JSON-LD structured data", lambda resp, pg: len(pg.ld_blocks) > 0),
    ("RETRIEVE", "enough body text", lambda resp, pg: pg.words >= MIN_WORDS),
]


def robots_checker():
    """A can_fetch(url) closure that reads each origin's robots.txt once."""
    cache = {}

    def allows(url):
        p = urlparse(url)
        origin = f"{p.scheme}://{p.netloc}"
        rp = cache.get(origin)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(origin + "/robots.txt")
            try:
                rp.read()
            except Exception:
                rp = True  # ponytail: unreachable robots.txt => allowed, same as Google
            cache[origin] = rp
        return True if rp is True else rp.can_fetch(UA, url)

    return allows


def crawl(seed, *, fetcher=fetch, robots_ok=None, max_pages=MAX_PAGES):
    """BFS from `seed`, following internal links only. Returns [(url, resp, page)]
    in discovery order. fetcher/robots_ok are the seams — inject a seolib.fixture
    and a stub to exercise the whole crawl offline (see tools/test_seolib.py)."""
    if robots_ok is None:
        robots_ok = robots_checker()
    host = domain(seed)
    seen, out, queue = set(), [], [urldefrag(seed)[0]]
    while queue and len(out) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not robots_ok(url):
            continue
        try:
            resp = fetcher(url, ua=UA)
        except Exception:
            continue
        pg = parse(resp.body)
        out.append((url, resp, pg))
        for href in pg.links:
            nxt = urldefrag(urljoin(url, href))[0]
            if nxt.startswith("http") and domain(nxt) == host and nxt not in seen:
                queue.append(nxt)
    return out


def audit_site(seed, *, fetcher=fetch, robots_ok=None, max_pages=MAX_PAGES):
    """Crawl, then run CHECKS on every page. Returns [(url, [(gate, label, ok)])]."""
    pages = crawl(seed, fetcher=fetcher, robots_ok=robots_ok, max_pages=max_pages)
    return [
        (url, [(gate, label, pred(resp, pg)) for gate, label, pred in CHECKS])
        for url, resp, pg in pages
    ]


def report(seed, max_pages=MAX_PAGES):
    results = audit_site(seed, max_pages=max_pages)
    if not results:
        print(f"\n  Site audit: {seed}\n  (no pages crawled — check the seed URL / robots.txt)\n")
        return results

    fails = Counter()
    dirty = 0
    page_lines = []
    for url, rows in results:
        bad = [f"{g}·{l}" for g, l, ok in rows if not ok]
        for b in bad:
            fails[b] += 1
        dirty += 1 if bad else 0
        tag = "clean" if not bad else f"{len(bad)} issue(s)"
        page_lines.append(f"[{checklist.mark(not bad, no='WARN')}] {tag:11} {url}")

    total = len(results)
    # Summary rows: every check, worst offenders first; PASS only if no page failed it.
    summary = []
    for gate, label, _ in CHECKS:
        n = fails[f"{gate}·{label}"]
        mark = checklist.mark(n == 0, no="WARN")
        suffix = "all pages OK" if n == 0 else f"{n}/{total} pages failing"
        summary.append(f"[{mark}] {gate:8} · {label:28} {suffix}")

    verdict = (f"VERDICT: {total} pages, all clean. Ship it."
               if dirty == 0
               else f"VERDICT: {dirty}/{total} pages have at least one gate failing — fix worst first.")
    print(checklist.render(f"Site audit: {seed} ({total} pages)", page_lines, "", width=64).rstrip())
    print(checklist.render("Findings rolled up across the site", summary, verdict, width=64))
    return results


def demo():
    """Offline self-check: drive the whole crawl+audit over a canned 3-page site,
    no network. Home links to two pages; one is noindexed, one is missing a title
    and canonical and has a thin body — the rollup must catch each."""
    from seolib import Response, fixture

    home = ('<html><head><title>Home</title><link rel="canonical" href="https://demo.test/">'
            '<script type="application/ld+json">{"@type":"WebSite"}</script></head>'
            '<body><h1>Home</h1><p>' + "word " * 120 + '</p>'
            '<a href="/good">good</a> <a href="/bad">bad</a> '
            '<a href="https://other.test/x">external</a></body></html>')
    good = ('<html><head><title>Good</title><link rel="canonical" href="https://demo.test/good">'
            '<script type="application/ld+json">{"@type":"Article"}</script></head>'
            '<body><h1>Good</h1><p>' + "word " * 120 + '</p></body></html>')
    bad = ('<html><head><meta name="robots" content="noindex"></head>'
           '<body><h1>One</h1><h1>Two</h1><p>thin</p></body></html>')  # no title/canonical/ld, 2 h1s, thin
    site = {
        "https://demo.test/": Response(url="https://demo.test/", status=200, body=home),
        "https://demo.test/good": Response(url="https://demo.test/good", status=200, body=good),
        "https://demo.test/bad": Response(url="https://demo.test/bad", status=200, body=bad),
    }
    results = audit_site(
        "https://demo.test/",
        fetcher=lambda url, **kw: fetch(url, transport=fixture(site), **kw),
        robots_ok=lambda u: True,
    )
    urls = [u for u, _ in results]
    assert urls == ["https://demo.test/", "https://demo.test/good", "https://demo.test/bad"], urls  # BFS, internal only

    d = {u: {l: ok for _, l, ok in rows} for u, rows in results}
    assert all(d["https://demo.test/good"].values()), d["https://demo.test/good"]   # clean page passes every gate
    bd = d["https://demo.test/bad"]
    assert bd["no noindex directive"] is False
    assert bd["has a <title>"] is False
    assert bd["declares a canonical"] is False
    assert bd["exactly one <h1>"] is False          # two h1s
    assert bd["has JSON-LD structured data"] is False
    assert bd["enough body text"] is False          # thin
    print("demo: crawl + full-site rollup assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--demo":
        demo()
    else:
        cap = int(args[1]) if len(args) > 1 else MAX_PAGES
        report(args[0], cap)
