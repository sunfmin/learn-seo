#!/usr/bin/env python3
"""ai_bots.py — what's your site's posture toward AI crawlers?  (Lesson 0010)

Classic SEO has one bot to think about (Googlebot). The AI era added a zoo of
them, and a new decision per vendor: do you let them fetch your pages — to train
a model, to ground a live answer, or on a user's behalf? That choice lives in
the same place as always: robots.txt. This reads it the way each AI bot would.

There is no PASS/FAIL here — allow vs block is a policy choice, not a bug. The
tool reports your current ALLOW/BLOCK posture per crawler, plus whether you ship
the (non-standard, unenforced) llms.txt. Three caveats it makes loud:
  - robots.txt is VOLUNTARY — only bots that choose to obey it do.
  - Google-Extended governs *Gemini/Vertex training*, NOT Google Search or AI
    Overviews — blocking it does not remove you from search.
  - llms.txt is a proposal, not a standard; Google has called it unnecessary.

Usage:
    python3 ai_bots.py https://example.com/
    python3 ai_bots.py --demo      # offline self-check, no network

Stdlib only (no pip); imports the shared seolib core — see CONTEXT.md / ADR 0001.
"""
import sys
import urllib.robotparser
from urllib.parse import urlparse

from seolib import checklist, fetch

# The crawlers worth a posture, with vendor and what fetching you feeds:
#   train      — corpus for model training
#   search     — live retrieval to ground/cite an answer (the AEO-relevant ones)
#   user-fetch — a fetch triggered by a specific user action, not bulk crawling
AI_BOTS = [
    ("GPTBot", "OpenAI", "train"),
    ("OAI-SearchBot", "OpenAI", "search"),
    ("ChatGPT-User", "OpenAI", "user-fetch"),
    ("ClaudeBot", "Anthropic", "train"),
    ("Claude-Web", "Anthropic", "user-fetch"),
    ("Google-Extended", "Google", "train"),
    ("PerplexityBot", "Perplexity", "search"),
    ("CCBot", "Common Crawl", "train"),
    ("Bytespider", "ByteDance", "train"),
    ("Applebot-Extended", "Apple", "train"),
    ("Amazonbot", "Amazon", "search"),
    ("Meta-ExternalAgent", "Meta", "train"),
]


def audit(robots_text, llms_present, *, path="/"):
    """Given robots.txt text + whether llms.txt exists, return per-bot posture.

    Returns ([(ua, vendor, kind, allowed)], llms_present). Pure — no network, so
    the parsing is exercisable offline (see demo() and tools/test_seolib.py)."""
    rp = urllib.robotparser.RobotFileParser()
    rp.parse((robots_text or "").splitlines())
    rows = [(ua, vendor, kind, rp.can_fetch(ua, path)) for ua, vendor, kind in AI_BOTS]
    return rows, llms_present


def _origin(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def report(url, *, fetcher=fetch):
    """Fetch robots.txt + probe llms.txt for `url`'s origin, then report posture.
    fetcher is the seam — inject a seolib.fixture to run offline (see tests)."""
    origin = _origin(url)

    def _get(path):
        try:
            r = fetcher(origin + path)
            return r if 200 <= r.status < 400 else None
        except Exception:
            return None

    robots = _get("/robots.txt")
    robots_text = robots.body if robots else ""   # no robots.txt => everything allowed
    llms_present = _get("/llms.txt") is not None
    rows, _ = audit(robots_text, llms_present)

    body = []
    allowed = 0
    for ua, vendor, kind, ok in rows:
        allowed += 1 if ok else 0
        body.append(f"[{checklist.mark(ok, yes='ALLOW', no='BLOCK')}] {vendor:12} · {ua:18} {kind}")
    body.append(f"[{checklist.mark(llms_present, yes='FOUND', no='none ')}] "
                f"{'(extra)':12} · llms.txt           non-standard, unenforced")

    verdict = (f"VERDICT: {allowed}/{len(rows)} AI crawlers allowed. "
               "robots.txt is voluntary — only honored by bots that choose to.")
    print(checklist.render(f"AI-crawler posture: {origin}", body, verdict, width=58))
    return rows, llms_present


def demo():
    """Offline self-check: a robots.txt blocking two AI bots must parse as such,
    and unlisted bots fall through to the wildcard group (allowed)."""
    robots = ("User-agent: GPTBot\nDisallow: /\n\n"
              "User-agent: CCBot\nDisallow: /\n\n"
              "User-agent: *\nAllow: /\n")
    rows, llms = audit(robots, llms_present=False)
    d = {ua: ok for ua, _, _, ok in rows}
    assert d["GPTBot"] is False, d           # explicitly blocked
    assert d["CCBot"] is False, d            # explicitly blocked
    assert d["ClaudeBot"] is True, d         # unlisted → wildcard → allowed
    assert d["Google-Extended"] is True, d   # unlisted → allowed (search unaffected anyway)
    assert llms is False
    print("demo: AI-bot robots parsing assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--demo":
        demo()
    else:
        report(args[0])
