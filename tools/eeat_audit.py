#!/usr/bin/env python3
"""eeat_audit.py — audit the machine-detectable signals behind E-E-A-T.  (Lesson 0008)

E-E-A-T = Experience, Expertise, Authoritativeness, Trust. Google is explicit:
"Of these aspects, trust is most important," and — crucially — "While E-E-A-T
itself isn't a specific ranking factor, using a mix of factors that can
identify content with good E-E-A-T is useful."

So there is NO E-E-A-T score to compute, and this tool does not pretend to.
What it DOES: check a page for the concrete, machine-readable proxy signals
that align with E-E-A-T — the byline, the author's linked identity, dates,
publisher, outbound sourcing, transparency links. Present = the page gives
engines (and AI answer engines) something to trust; missing = it's anonymous.

Grouped by the letter each signal supports. Trust signals are weighted heaviest
because Google says trust is the centre of the family.

Stdlib only (imports the shared seolib core — see CONTEXT.md / ADR 0001).
Reads a URL (fetches) or a local .html file.

Usage:
    python3 eeat_audit.py https://site.com/blog/post
    python3 eeat_audit.py page.html --base https://site.com/blog/post
    python3 eeat_audit.py --demo      # offline self-check, no network
"""
import json
import sys

from seolib import domain, fetch, parse

ARTICLE = {"article", "blogposting", "newsarticle", "techarticle", "scholarlyarticle"}


def flatten_ld(blocks):
    """Every dict node across all JSON-LD blocks (handles @graph + nesting)."""
    out = []

    def walk(o):
        if isinstance(o, dict):
            out.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for b in blocks:
        try:
            walk(json.loads(b))
        except Exception:
            pass
    return out


def _types(node):
    t = node.get("@type")
    return [t.lower()] if isinstance(t, str) else [str(x).lower() for x in (t or [])]


def analyze(html, base_url=None):
    """Return (facts dict, list of (letter, label, ok, detail) rows)."""
    pg = parse(html)
    nodes = flatten_ld(pg.ld_blocks)
    arts = [n for n in nodes if ARTICLE & set(_types(n))]
    persons = [n for n in nodes if "person" in _types(n)]

    def art_has(key):
        return any(a.get(key) for a in arts)

    author_val = next((a.get("author") for a in arts if a.get("author")), None)
    author_in_schema = bool(author_val)
    author_named = bool(pg.meta.get("author") or pg.rel_author or author_in_schema)
    author_linked = (isinstance(author_val, dict) and bool(author_val.get("sameAs"))) \
        or any(p.get("sameAs") for p in persons)

    base_host = domain(base_url) if base_url else None
    outbound, about = 0, False
    for h in pg.links:
        hl = h.lower()
        if "about" in hl or "contact" in hl:
            about = True
        if hl.startswith(("http://", "https://")):
            host = domain(h)
            if base_host is None or host != base_host:
                outbound += 1
    https = base_url.startswith("https://") if base_url else None

    rows = [
        ("E·E", "named author (byline / meta / schema)", author_named,
         "the author's meta tag, rel=author, or Article.author"),
        ("E·E", "author detailed in Article schema", author_in_schema,
         "add author to your Article/BlogPosting JSON-LD"),
        ("A", "author identity linked off-site (sameAs)", author_linked,
         "link the author to an authoritative profile via Person.sameAs"),
        ("A", "publisher declared in schema", art_has("publisher"),
         "add publisher to the Article JSON-LD"),
        ("T", "publish date present (datePublished)", art_has("datePublished"),
         "stamp datePublished in schema"),
        ("T", "updated date present (dateModified)", art_has("dateModified"),
         "stamp dateModified when you revise"),
        ("T", "cites outbound sources", outbound >= 1, f"{outbound} external link(s)"),
        ("T", "transparency link (about / contact)", about,
         "link to an about or contact page"),
    ]
    if https is not None:
        rows.insert(4, ("T", "served over HTTPS", https, base_url.split("://")[0]))

    facts = {"arts": len(arts), "persons": len(persons), "outbound": outbound,
             "meta_author": pg.meta.get("author")}
    return facts, rows


def report(html, base_url=None):
    facts, rows = analyze(html, base_url)
    groups = {"E·E": "Experience / Expertise", "A": "Authoritativeness", "T": "Trust (most important)"}
    present = sum(1 for *_, ok, _ in [(r[0], r[1], r[2], r[3]) for r in rows] if ok)
    total = len(rows)
    print("\n  E-E-A-T proxy-signal audit")
    print("  NOTE: not an 'E-E-A-T score' (no such thing) — these are the")
    print("        machine-detectable factors that align with E-E-A-T.")
    print("  " + "-" * 56)
    for letter, title in groups.items():
        grp = [r for r in rows if r[0] == letter]
        if not grp:
            continue
        print(f"  [{letter}] {title}")
        for _, label, ok, detail in grp:
            mark = "ok " if ok else "MISS"
            print(f"      [{mark}] {label}  ({detail})")
    print("  " + "-" * 56)
    print(f"  {present}/{total} trust signals present.", end=" ")
    print("Strong, trustworthy page." if present >= total - 1
          else ("Anonymous / thin — engines have little to trust."
                if present <= 2 else "Some signals missing — fill the gaps above."))
    print()
    return rows


GOOD = """<html><head>
<meta name="author" content="Dr. Jane Roe">
<script type="application/ld+json">{"@context":"https://schema.org",
 "@type":"BlogPosting","headline":"GEO explained",
 "datePublished":"2026-06-01","dateModified":"2026-06-18",
 "publisher":{"@type":"Organization","name":"MySEO"},
 "author":{"@type":"Person","name":"Dr. Jane Roe",
   "sameAs":["https://www.linkedin.com/in/janeroe"]}}</script>
</head><body><article>...
<a href="https://arxiv.org/abs/2311.09735">the GEO paper</a>
<a href="/about">About us</a></article></body></html>"""

BAD = """<html><head><title>Untitled</title></head>
<body><p>Some text with no author, no dates, no sources.</p></body></html>"""


def demo():
    _, rows = analyze(GOOD, base_url="https://myseo.io/blog/geo")
    g = {label: ok for _, label, ok, _ in rows}
    assert g["named author (byline / meta / schema)"], "named author missed"
    assert g["author identity linked off-site (sameAs)"], "sameAs missed"
    assert g["publisher declared in schema"], "publisher missed"
    assert g["updated date present (dateModified)"], "dateModified missed"
    assert g["cites outbound sources"], "outbound link missed"
    assert g["transparency link (about / contact)"], "about link missed"
    assert g["served over HTTPS"], "https missed"

    _, brows = analyze(BAD, base_url="http://example.com/x")
    b = {label: ok for _, label, ok, _ in brows}
    assert not b["named author (byline / meta / schema)"], "false author on bad page"
    assert not b["publisher declared in schema"], "false publisher"
    assert not b["cites outbound sources"], "false outbound"
    assert not b["served over HTTPS"], "http flagged as https"

    # outbound must EXCLUDE same-host links
    _, srows = analyze('<a href="https://myseo.io/other">x</a>',
                       base_url="https://myseo.io/blog/geo")
    s = {label: (ok, det) for _, label, ok, det in srows}
    assert s["cites outbound sources"][0] is False, "same-host counted as outbound"

    print("demo: all eeat_audit assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif args and args[0].startswith(("http://", "https://")) and len(args) == 1:
        resp = fetch(args[0])
        report(resp.body, base_url=resp.url)
    elif args and not args[0].startswith("-"):
        base = args[args.index("--base") + 1] if "--base" in args else None
        with open(args[0], encoding="utf-8") as f:
            report(f.read(), base_url=base)
    else:
        sys.exit(__doc__)
