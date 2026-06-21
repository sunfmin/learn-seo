#!/usr/bin/env python3
"""schema_tool.py — generate & lint schema.org JSON-LD.  (Lesson 0003)

Structured data is how you hand machines a clean, labelled fact instead of
making them guess from prose. It feeds two stages at once:
  SERVE    — earns rich results in classic search
  RETRIEVE — gives an answer engine an unambiguous fact to extract & cite

This tool encodes GOOGLE'S rich-result requirements (required vs recommended
properties) for three high-value types — NOT the full schema.org vocabulary.

Usage:
    python3 schema_tool.py sample FAQPage        # print copy-paste JSON-LD
    python3 schema_tool.py sample Product
    python3 schema_tool.py lint mypage.json      # validate a JSON-LD file
    python3 schema_tool.py page https://site/x   # lint the JSON-LD on a LIVE page
    python3 schema_tool.py --demo                # offline self-check

Stdlib only; imports the shared seolib core — see CONTEXT.md / ADR 0001.
"""
import json
import sys

from seolib import fetch, ld

CONTEXT = "https://schema.org"

# Top-level property requirements, per Google's rich-result docs.
# ponytail: covers the 3 types that actually earn rich results / AI citations.
# Add a type here when you need it; don't reach for the full schema.org graph.
SPEC = {
    "Article": {"required": [],
                "recommended": ["headline", "image", "datePublished", "dateModified", "author"]},
    "Product": {"required": ["name"],
                "recommended": ["image", "description", "brand", "offers", "aggregateRating", "review"]},
    "FAQPage": {"required": ["mainEntity"],
                "recommended": []},
}

SAMPLES = {
    "Article": {
        "@context": CONTEXT, "@type": "Article",
        "headline": "How crawling differs from indexing",
        "image": ["https://example.com/cover.jpg"],
        "datePublished": "2026-06-17T09:00:00+09:00",
        "dateModified": "2026-06-17T09:00:00+09:00",
        "author": {"@type": "Person", "name": "Felix",
                   "url": "https://example.com/about"},
    },
    "Product": {
        "@context": CONTEXT, "@type": "Product",
        "name": "Acme Widget Pro",
        "image": ["https://example.com/widget.jpg"],
        "description": "A widget that widgets.",
        "brand": {"@type": "Brand", "name": "Acme"},
        "offers": {"@type": "Offer", "price": "29.00",
                   "priceCurrency": "USD", "availability": "https://schema.org/InStock"},
    },
    "FAQPage": {
        "@context": CONTEXT, "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": "Is crawlable the same as indexable?",
             "acceptedAnswer": {"@type": "Answer",
                                "text": "No. Crawlable means a bot may fetch the page; "
                                        "indexable means the engine will keep it. Two gates."}},
        ],
    },
}


def lint(obj):
    """Return list of (severity, message). ERROR = blocks rich result; WARN = recommended."""
    issues = []
    if obj.get("@context") not in ("https://schema.org", "http://schema.org"):
        issues.append(("WARN", "@context should be https://schema.org"))
    t = obj.get("@type")
    if t not in SPEC:
        issues.append(("ERROR", f"@type {t!r} not recognised by this linter ({', '.join(SPEC)})"))
        return issues
    spec = SPEC[t]
    for p in spec["required"]:
        if not obj.get(p):
            issues.append(("ERROR", f"{t} missing required property: {p}"))
    for p in spec["recommended"]:
        if not obj.get(p):
            issues.append(("WARN", f"{t} missing recommended property: {p}"))

    # nested checks for the structures that earn the rich result
    if t == "FAQPage" and isinstance(obj.get("mainEntity"), list):
        for i, q in enumerate(obj["mainEntity"]):
            if q.get("@type") != "Question" or not q.get("name"):
                issues.append(("ERROR", f"mainEntity[{i}] must be a Question with a name"))
            ans = q.get("acceptedAnswer") or {}
            if not ans.get("text"):
                issues.append(("ERROR", f"mainEntity[{i}].acceptedAnswer needs text"))
    if t == "Product" and isinstance(obj.get("offers"), dict):
        o = obj["offers"]
        for p in ("price", "priceCurrency"):
            if not o.get(p):
                issues.append(("ERROR", f"offers missing required property: {p}"))
    return issues


def report(obj):
    issues = lint(obj)
    errors = [m for s, m in issues if s == "ERROR"]
    print("\n  Linting JSON-LD: @type =", obj.get("@type"))
    print("  " + "-" * 50)
    if not issues:
        print("  clean — no issues.")
    for sev, msg in issues:
        print(f"  [{sev:5}] {msg}")
    print("  " + "-" * 50)
    print(f"  VERDICT: {'INVALID — ' + str(len(errors)) + ' error(s) block the rich result.' if errors else 'valid (warnings are optional polish).'}\n")
    return issues


def lint_page(html):
    """Offline core: extract JSON-LD from a page, split into all nodes and the
    ones this linter recognises. The half that used to be missing."""
    nodes = ld.extract(html)
    known = [n for n in nodes if n.get("@type") in SPEC]
    return nodes, known


def report_page(url, *, fetcher=fetch):
    html = fetcher(url).body
    nodes, known = lint_page(html)
    print(f"\n  JSON-LD on {url}: {len(nodes)} node(s), {len(known)} lintable.")
    if not known:
        print(f"  (no {'/'.join(SPEC)} JSON-LD found to lint.)\n")
        return []
    issues = []
    for n in known:
        issues += report(n)
    return issues


def emit(type_name):
    obj = SAMPLES[type_name]
    blob = json.dumps(obj, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{blob}\n</script>'


def demo():
    # complete Product → no errors
    assert not [m for s, m in lint(SAMPLES["Product"]) if s == "ERROR"], "good Product flagged"
    # Product without a name → required error
    assert any(s == "ERROR" for s, _ in lint({"@context": CONTEXT, "@type": "Product"})), "missing name not caught"
    # FAQ answer with no text → error
    bad_faq = {"@context": CONTEXT, "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": "Q?", "acceptedAnswer": {"@type": "Answer"}}]}
    assert any("acceptedAnswer needs text" in m for s, m in lint(bad_faq)), "empty answer not caught"
    # Product offer missing currency → error
    bad_prod = {"@context": CONTEXT, "@type": "Product", "name": "X",
                "offers": {"@type": "Offer", "price": "9.00"}}
    assert any("priceCurrency" in m for s, m in lint(bad_prod)), "missing currency not caught"
    print("demo: all linter assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif len(args) == 2 and args[0] == "sample" and args[1] in SAMPLES:
        print(emit(args[1]))
    elif len(args) == 2 and args[0] == "lint":
        with open(args[1], encoding="utf-8") as f:
            report(json.load(f))
    elif len(args) == 2 and args[0] == "page":
        report_page(args[1])
    else:
        sys.exit(__doc__)
