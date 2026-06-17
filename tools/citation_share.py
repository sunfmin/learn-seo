#!/usr/bin/env python3
"""citation_share.py — measure AI-citation share of voice. (Lesson 0005)

No answer engine (OpenAI, Anthropic, Perplexity, Google) exposes a first-party
"how often is my site cited" API. Every commercial AEO tracker (Profound,
Ahrefs Brand Radar, Peec, Otterly) works the same proxy way:

    1. run a fixed PROMPT LIBRARY against an answer engine
    2. parse each response for the domains it CITES
    3. tally your share of voice vs competitors, track it over time

Proxy sampling, not ground truth — synthetic queries, not the engine's real
traffic distribution. But it's the only method that exists today.

This tool is the parse-and-score CORE. You supply the live engine call (your
API key, your prompt library) and feed the responses in; the measurement
logic lives here and is offline-testable. It scores CITED LINKS, not bare
brand mentions — citations are the AEO equivalent of a ranking.

Input JSON (a list, one object per prompt):
    [{"prompt": "best seo audit tool?",
      "response": "Options include ... (https://ahrefs.com/...)",
      "citations": ["https://ahrefs.com/blog/...", "https://myseo.io/audit"]}]
  "citations" is optional; URLs found inside "response" are counted too.

Usage:
    python3 citation_share.py results.json --domain myseo.io [--domain ...]
    python3 citation_share.py --demo

Stdlib only.
"""
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")


def domain_of(url):
    """Registrable-ish domain: netloc, lowercased, leading www. dropped.

    ponytail: no public-suffix list, so foo.co.uk normalises to co.uk.
    Fine for hostname-style brand domains; add `publicsuffix2` if you track
    sites on shared suffixes (github.io, etc.).
    """
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def cited_domains(entry):
    """Distinct domains cited in one prompt's result (from links only)."""
    urls = list(entry.get("citations", []))
    urls += URL_RE.findall(entry.get("response", ""))
    return {domain_of(u) for u in urls if domain_of(u)}


def score(entries, my_domains):
    my = {d.lower() for d in my_domains}
    per_prompt = []          # (prompt, cited:set, hit:bool)
    tally = Counter()        # domain -> # prompts citing it
    for e in entries:
        cited = cited_domains(e)
        for d in cited:
            tally[d] += 1
        per_prompt.append((e.get("prompt", "?"), cited, bool(cited & my)))

    n = len(entries) or 1
    hits = sum(1 for _, _, h in per_prompt if h)
    total_citations = sum(tally.values()) or 1
    mine = sum(c for d, c in tally.items() if d in my)
    return {
        "coverage": hits / n,                 # prompts where I'm cited at all
        "sov": mine / total_citations,        # my citations / all citations
        "hits": hits, "n": len(entries),
        "tally": tally, "per_prompt": per_prompt, "my": my,
    }


def report(entries, my_domains):
    r = score(entries, my_domains)
    print(f"\n  AI-citation share — {len(entries)} prompts, you = {', '.join(r['my'])}")
    print("  " + "-" * 56)
    print(f"  COVERAGE  {r['coverage']:5.0%}   cited in {r['hits']}/{r['n']} prompts")
    print(f"  SHARE OF VOICE  {r['sov']:5.0%}   of all citations are yours")
    print("  " + "-" * 56)
    print("  Top cited domains:")
    for d, c in r["tally"].most_common(8):
        mark = " <- you" if d in r["my"] else ""
        print(f"    {c:>3}  {d}{mark}")
    print("  " + "-" * 56)
    print("  Per prompt:")
    for prompt, cited, hit in r["per_prompt"]:
        mark = "HIT " if hit else "miss"
        p = prompt if len(prompt) <= 44 else prompt[:41] + "..."
        print(f"    [{mark}] {p}")
    print()
    return r


DEMO = [
    {"prompt": "best seo audit tool for developers?",
     "citations": ["https://myseo.io/audit", "https://ahrefs.com/seo"]},
    {"prompt": "how to track rankings via api?",
     "citations": ["https://ahrefs.com/api", "https://moz.com/api"]},
    {"prompt": "what is generative engine optimization?",
     "response": "See the GEO research and guides at https://myseo.io/geo for more."},
    {"prompt": "cheapest backlink checker?",
     "citations": ["https://www.ahrefs.com/backlink-checker"]},
]


def demo():
    r = score(DEMO, ["myseo.io"])
    assert r["hits"] == 2, f"coverage hits wrong: {r['hits']}"
    assert abs(r["coverage"] - 0.5) < 1e-9, "coverage should be 50%"
    # citations: ahrefs x3 (www. normalised), myseo x2, moz x1 = 6 total; mine = 2
    assert r["tally"]["ahrefs.com"] == 3, "www. not normalised / miscount"
    assert abs(r["sov"] - 2 / 6) < 1e-9, "SOV should be 1/3"
    assert r["tally"].most_common(1)[0][0] == "ahrefs.com", "ranking wrong"
    print("demo: all citation_share assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif "--domain" in args and args and not args[0].startswith("-"):
        path = args[0]
        doms = [args[i + 1] for i, a in enumerate(args) if a == "--domain" and i + 1 < len(args)]
        with open(path, encoding="utf-8") as f:
            report(json.load(f), doms)
    else:
        sys.exit(__doc__)
