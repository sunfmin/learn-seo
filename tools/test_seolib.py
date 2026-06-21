#!/usr/bin/env python3
"""test_seolib.py — the seolib package's single test surface.

The interface is the test surface: every shared module is exercised here,
through the same import the tools use. Run from the repo root:

    python3 tools/test_seolib.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # ensure tools/ importable

from seolib import domain, fetch, fixture, Response, parse


def test_domain():
    assert domain("https://www.Ahrefs.com/seo") == "ahrefs.com"
    assert domain("http://moz.com") == "moz.com"
    assert domain("https://sub.example.co.uk/p?q=1") == "sub.example.co.uk"
    assert domain("not-a-url") == ""


def test_page_signals():
    html = ('<html><head><title>Hi</title>'
            '<meta name="robots" content="noindex"><meta name="author" content="Jane">'
            '<link rel="canonical" href="https://x.com/a">'
            '<script type="application/ld+json">{"@type":"Article"}</script></head>'
            '<body><h1>One</h1><h2>Two</h2><p>three four five</p>'
            '<a href="/a">x</a><a rel="author" href="/me">me</a>'
            '<style>.c{color:red}</style><script>var a=1;</script></body></html>')
    pg = parse(html)
    assert pg.title == "Hi"
    assert pg.meta.get("robots") == "noindex" and pg.meta.get("author") == "Jane"
    assert pg.canonical == "https://x.com/a"
    assert pg.rel_author is True
    assert pg.links == ["/a", "/me"]
    assert pg.headings == {"h1": 1, "h2": 1}
    # One + Two + (three four five) + x + me = 7; title/script/style excluded
    assert pg.words == 7
    assert len(pg.ld_blocks) == 1


def test_fetch_fixture_seam():
    pages = {"https://x.com/a": "<html><body>hi</body></html>"}
    r = fetch("https://x.com/a", transport=fixture(pages))
    assert isinstance(r, Response) and r.status == 200 and "hi" in r.body


def test_fetch_and_audit():
    # crawl_audit.audit driven end-to-end through the fetch seam, no network.
    import crawl_audit
    html = ('<html><head><title>Hi</title>'
            '<meta name="robots" content="noindex">'
            '<link rel="canonical" href="https://x.com/a"></head><body>ok</body></html>')
    pages = {"https://x.com/a": Response(url="https://x.com/a", status=200, body=html)}
    rows = crawl_audit.audit(
        "https://x.com/a",
        fetcher=lambda url, **kw: fetch(url, transport=fixture(pages), **kw),
        robots_ok=lambda u: True,
    )
    d = {label: ok for _, label, ok in rows}
    assert d["page returns success (200)"] is True
    assert d["no noindex directive"] is False     # X-Robots/meta noindex caught
    assert d["has a <title>"] is True
    assert d["declares a canonical URL"] is True


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
    print(f"test_seolib: {len(tests)} group(s) passed.")


if __name__ == "__main__":
    main()
