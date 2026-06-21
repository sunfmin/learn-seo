"""ld — JSON-LD extraction from a page.  (seolib)

The course had two halves that never met: eeat_audit could pull JSON-LD nodes
out of live HTML, and schema_tool could lint a JSON-LD object — but only from a
.json file. This is the shared extractor that joins them, so a linter can reach
a live page.

    extract(html) -> [node, ...]   # every dict node, @graph + nesting flattened
    flatten(blocks) -> [...]       # same, from already-parsed page.ld_blocks
    types(node) -> [lowercased @type, ...]
"""
import json

from .page import parse

ARTICLE_TYPES = {"article", "blogposting", "newsarticle", "techarticle", "scholarlyarticle"}


def flatten(blocks):
    """Every dict node across raw application/ld+json block strings."""
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


def extract(html):
    """All JSON-LD dict nodes embedded in an HTML page."""
    return flatten(parse(html).ld_blocks)


def types(node):
    t = node.get("@type")
    return [t.lower()] if isinstance(t, str) else [str(x).lower() for x in (t or [])]
