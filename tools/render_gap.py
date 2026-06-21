#!/usr/bin/env python3
"""render_gap.py — what does a bot see BEFORE JavaScript runs?  (Lesson 0006)

Google indexes in two passes: it crawls the raw HTML first, then later — once
its resources allow — a headless Chrome renders the page and runs the JS, and
only THEN re-indexes what the JavaScript produced. That render is a separate,
deferred queue. Meanwhile your own crawl_audit.py (Lesson 0002) and most
standalone AI crawlers fetch only the RAW HTML and never run any JS at all.

So the question that decides whether your content is seen, when, and by whom is:
how much of the page exists in the first server response, before a line of JS?

This tool answers that. It extracts the same signals from two HTML strings —
the RAW response (no JS) and the RENDERED DOM (after JS) — and diffs them:

    visible words · <a> links · JSON-LD blocks · <h1> / <h2> headings

A signal that jumps from ~0 in raw to a lot in rendered is JS-DEPENDENT:
invisible to no-JS bots, and delayed for Google until the render wave.

Stdlib only (imports the shared seolib core — see CONTEXT.md / ADR 0001). It
does NOT run a browser. You capture the rendered DOM yourself
(DevTools -> Elements -> right-click <html> -> Copy -> Copy outerHTML, paste
into rendered.html) and supply it; the raw side this tool can fetch for you.

Usage:
    # diff two captured files
    python3 render_gap.py raw.html rendered.html

    # fetch the raw HTML from a URL, diff against your captured rendered DOM
    python3 render_gap.py https://example.com/page rendered.html

    python3 render_gap.py --demo      # offline self-check, no network
"""
import sys

from seolib import fetch, parse

UA = "Googlebot"

# (key, human label, min absolute delta to bother flagging)
SIGNALS = [
    ("words", "visible words", 20),
    ("links", "<a> links", 2),
    ("jsonld", "JSON-LD blocks", 1),
    ("h1", "<h1> headings", 1),
    ("h2", "<h2> headings", 1),
]


def extract(html):
    """The signals that decide indexability — read off the shared seolib.Page.

    A no-JS bot sees only what's here in the raw HTML; ld+json blocks count
    because JS-injected structured data is a classic thing such a bot misses.
    """
    pg = parse(html)
    return {"words": pg.words, "links": len(pg.links),
            "jsonld": sum(1 for b in pg.ld_blocks if b.strip()),
            "title": pg.title,
            "h1": pg.headings.get("h1", 0), "h2": pg.headings.get("h2", 0)}


def analyze(raw_html, rendered_html):
    """Return (raw dict, rendered dict, list of per-signal gap rows)."""
    raw, rend = extract(raw_html), extract(rendered_html)
    rows = []
    for key, label, floor in SIGNALS:
        r, d = raw[key], rend[key]
        visible = (r / d) if d else 1.0          # share present without JS
        js_dep = d > 0 and (d - r) >= floor and visible < 0.5
        rows.append({"key": key, "label": label, "raw": r, "rendered": d,
                     "visible": visible, "js_dep": js_dep})
    return raw, rend, rows


def verdict(rows):
    """Headline call, keyed on how much visible TEXT survives without JS."""
    words = next(r for r in rows if r["key"] == "words")
    flagged = [r["label"] for r in rows if r["js_dep"]]
    if words["visible"] >= 0.9:
        head = ("SERVER-RENDERED — your content is in the first byte. "
                "Every bot (Googlebot wave 1, no-JS AI crawlers) sees it now.")
    elif words["rendered"] > 0 and words["visible"] <= 0.1:
        head = ("CLIENT-SIDE RENDERED — the raw HTML is an empty shell. "
                "No-JS AI crawlers see ~nothing; Googlebot indexes it only on "
                "the deferred render wave.")
    else:
        head = ("HYDRATION / PARTIAL GAP — some content needs JS. "
                "That part is invisible to no-JS bots and delayed for Google.")
    return head, flagged


def report(raw_html, rendered_html):
    raw, rend, rows = analyze(raw_html, rendered_html)
    print("\n  Render gap — raw HTML (no JS)  vs  rendered DOM (after JS)")
    print("  " + "-" * 60)
    print(f"  {'signal':<16}{'no JS':>8}{'with JS':>9}{'visible':>9}   flag")
    for r in rows:
        flag = "JS-DEP" if r["js_dep"] else ""
        print(f"  {r['label']:<16}{r['raw']:>8}{r['rendered']:>9}"
              f"{r['visible']:>8.0%}   {flag}")
    print("  " + "-" * 60)
    head, flagged = verdict(rows)
    print(f"  VERDICT: {head}")
    if flagged:
        print(f"  JS-only signals (a no-JS bot misses these): {', '.join(flagged)}")
    print()
    return rows


# raw shell: the SPA pattern — empty <div id=root>, JS bundle, nothing else.
RAW_SHELL = (
    '<html><head><title>App</title></head>'
    '<body><div id="root"></div><script src="/bundle.js"></script></body></html>'
)
# rendered DOM: JS has filled in the content, links, headings, and JSON-LD.
RENDERED_FULL = (
    '<html><head><title>Best SEO Audit Tools (2026)</title>'
    '<script type="application/ld+json">{"@type":"Article"}</script></head>'
    '<body><div id="root"><h1>Best SEO audit tools</h1>'
    '<h2>For developers</h2><p>' + ("word " * 200) + '</p>'
    '<a href="/a">one</a><a href="/b">two</a><a href="/c">three</a>'
    '</div></body></html>'
)


def demo():
    raw, rend, rows = analyze(RAW_SHELL, RENDERED_FULL)
    by = {r["key"]: r for r in rows}

    assert raw["words"] <= 2, f"raw shell should be near-empty: {raw['words']}"
    assert rend["words"] >= 200, f"rendered should be full: {rend['words']}"
    assert by["words"]["js_dep"], "client-side text must flag JS-DEP"
    assert by["links"]["js_dep"], "JS-injected links must flag"
    assert by["jsonld"]["raw"] == 0 and by["jsonld"]["rendered"] == 1, "ld+json count"
    assert by["jsonld"]["js_dep"], "JS-injected JSON-LD must flag (AEO trap)"

    head, flagged = verdict(rows)
    assert "CLIENT-SIDE RENDERED" in head, head
    assert "JSON-LD blocks" in flagged, flagged

    # the inverse: a server-rendered page must NOT flag.
    raw2, rend2, rows2 = analyze(RENDERED_FULL, RENDERED_FULL)
    h2, f2 = verdict(rows2)
    assert "SERVER-RENDERED" in h2, h2
    assert f2 == [], f"server-rendered page flagged nothing-wrongly: {f2}"

    # script/style text must not be counted as visible words.
    noisy = extract('<body><style>.x{color:red}</style>'
                    '<script>var a=1;</script><p>two words</p></body>')
    assert noisy["words"] == 2, f"script/style leaked into words: {noisy['words']}"

    print("demo: all render_gap assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif len(args) == 2:
        src, rendered_path = args
        raw_html = fetch(src, ua=UA).body if src.startswith(("http://", "https://")) \
            else open(src, encoding="utf-8").read()
        rendered_html = open(rendered_path, encoding="utf-8").read()
        report(raw_html, rendered_html)
    else:
        sys.exit(__doc__)
