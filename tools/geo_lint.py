#!/usr/bin/env python3
"""geo_lint.py — score a draft for retrieval & citation readiness. (Lesson 0004)

Classic SEO asks "will this rank?". AEO/GEO asks a blunter question: if an
answer engine RETRIEVES this page, is there a clean, self-contained fact here
it can lift and CITE? The GEO paper (Aggarwal et al., KDD 2024, arXiv:2311.09735)
measured which content edits actually raise visibility in generative engines.
The three that moved the needle most — up to ~40% relative lift:

    CITE SOURCES     — back claims with references
    ADD QUOTATIONS   — quote authorities verbatim
    ADD STATISTICS   — concrete numbers, not vague adjectives

Keyword stuffing did NOT help in that study (it hurt). This linter scores a
plain-text / markdown draft against those evidence-backed signals plus
extractability (answer-first, chunked) and flags the stuffing anti-pattern.

It is a SHAPE checker, not a style grader and not a ranker. A high score means
"easy to retrieve and quote," not "good writing" or "will rank #1."

Usage:
    python3 geo_lint.py draft.md
    python3 geo_lint.py --demo

Stdlib only.
"""
import re
import sys
from collections import Counter

# words too common to count as a "stuffed" keyword
STOP = set("""the a an and or but for nor so yet of to in on at by with from as
is are was were be been being this that these those it its their your you we
they he she them his her our not no can will would should could may might must
have has had do does did then than into over under about more most very just
""".split())


def blocks(text):
    """Split into paragraph-ish blocks on blank lines."""
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


def is_heading(block):
    return block.lstrip().startswith("#")


def words(s):
    return re.findall(r"[A-Za-z][A-Za-z'-]+", s)


def check(text):
    """Return list of (signal, status, note). status in PASS/WARN."""
    out = []
    bl = blocks(text)

    # --- GEO signal 1: statistics (numbers, especially percentages) ---
    pcts = re.findall(r"\b\d[\d,.]*\s?%", text)
    nums = re.findall(r"(?<![\w/])\d[\d,.]*\b", text)
    if pcts or len(nums) >= 3:
        out.append(("STATISTICS", "PASS",
                    f"{len(pcts)} percentage(s), {len(nums)} number(s) — concrete facts to lift"))
    else:
        out.append(("STATISTICS", "WARN",
                    "few/no numbers — add concrete stats; vague adjectives don't get cited"))

    # --- GEO signal 2: citations / sources ---
    links = re.findall(r"https?://\S+", text)
    md_links = re.findall(r"\[[^\]]+\]\(https?://[^)]+\)", text)
    attrib = re.findall(r"(?i)\b(according to|source:|per |reports?|study|research)\b", text)
    cites = len(links) + len(attrib)
    if cites >= 2:
        out.append(("CITE SOURCES", "PASS",
                    f"{len(links)} link(s) ({len(md_links)} inline), {len(attrib)} attribution phrase(s)"))
    else:
        out.append(("CITE SOURCES", "WARN",
                    "thin sourcing — back claims with references; engines favour sourced text"))

    # --- GEO signal 3: quotations ---
    quoted = re.findall(r"[\"“][^\"”]{15,}[\"”]", text)
    bq = [b for b in bl if b.lstrip().startswith(">")]
    if quoted or bq:
        out.append(("QUOTATIONS", "PASS",
                    f"{len(quoted)} inline quote(s), {len(bq)} blockquote(s)"))
    else:
        out.append(("QUOTATIONS", "WARN",
                    "no quotations — a verbatim quote from an authority is highly liftable"))

    # --- extractability: answer-first (lead block is a short, direct answer) ---
    body = [b for b in bl if not is_heading(b)]
    if body and len(words(body[0])) <= 60:
        out.append(("ANSWER-FIRST", "PASS",
                    f"opens with a {len(words(body[0]))}-word answer block — quotable as-is"))
    else:
        n = len(words(body[0])) if body else 0
        out.append(("ANSWER-FIRST", "WARN",
                    f"opening block is {n} words — lead with the answer, then expand (inverted pyramid)"))

    # --- extractability: chunked (headings + no wall-of-text) ---
    heads = [b for b in bl if is_heading(b)]
    longest = max((len(words(b)) for b in body), default=0)
    if len(heads) >= 2 and longest <= 150:
        out.append(("CHUNKED", "PASS",
                    f"{len(heads)} headings, longest block {longest} words — self-contained sections"))
    else:
        out.append(("CHUNKED", "WARN",
                    f"{len(heads)} headings, longest block {longest} words — break into headed, "
                    "self-contained chunks engines can retrieve in isolation"))

    # --- anti-pattern: keyword stuffing (GEO paper: did not help / hurt) ---
    toks = [w.lower() for w in words(text) if len(w) >= 3 and w.lower() not in STOP]
    if toks:
        word, freq = Counter(toks).most_common(1)[0]
        density = freq / len(toks)
        # ponytail: crude single-token density. Good enough to catch obvious
        # stuffing; swap in a TF-IDF check if false positives show up.
        if freq >= 8 and density > 0.06:
            out.append(("NO STUFFING", "WARN",
                        f"'{word}' is {density:.0%} of content words ({freq}x) — reads as stuffing, "
                        "which the GEO study found unhelpful"))
        else:
            out.append(("NO STUFFING", "PASS",
                        f"top word '{word}' at {density:.0%} density — no stuffing"))
    return out


def report(text):
    rows = check(text)
    passes = sum(1 for _, s, _ in rows if s == "PASS")
    print("\n  GEO / retrieval-readiness lint")
    print("  " + "-" * 56)
    for sig, status, note in rows:
        mark = "PASS" if status == "PASS" else "WARN"
        print(f"  [{mark}] {sig:13} {note}")
    print("  " + "-" * 56)
    print(f"  SCORE: {passes}/{len(rows)} signals — "
          + ("strong retrieval shape." if passes >= len(rows) - 1
             else "fixable; each WARN is a concrete edit." if passes >= 3
             else "weak — restructure before publishing.") + "\n")
    return rows


STRONG = """# Is crawlable the same as indexable?

No. Crawlable means a bot may fetch the page; indexable means the engine will
keep it. They are two separate gates.

## Why it matters

A 2026 Google study notes that according to Search Central, roughly 40% of
"why isn't my page ranking" reports fail at one of these two gates, not at
ranking. As Google puts it, "blocking a page in robots.txt does not remove it
from the index."

## The fix

Allow the crawl, then serve a noindex directive — 1 change, in the page head.
"""

WEAK = """SEO is important for SEO because good SEO helps your SEO rankings and
SEO traffic grows when you do SEO well so invest in SEO today for better SEO
results and more SEO success with SEO."""


def demo():
    s = {sig: st for sig, st, _ in check(STRONG)}
    assert s["STATISTICS"] == "PASS", "strong draft: stats missed"
    assert s["CITE SOURCES"] == "PASS", "strong draft: cites missed"
    assert s["QUOTATIONS"] == "PASS", "strong draft: quote missed"
    assert s["ANSWER-FIRST"] == "PASS", "strong draft: answer-first missed"

    w = {sig: st for sig, st, _ in check(WEAK)}
    assert w["CITE SOURCES"] == "WARN", "weak draft: thin sourcing not caught"
    assert w["STATISTICS"] == "WARN", "weak draft: missing stats not caught"
    assert w["NO STUFFING"] == "WARN", "weak draft: keyword stuffing not caught"
    print("demo: all geo_lint assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif len(args) == 1 and not args[0].startswith("-"):
        with open(args[0], encoding="utf-8") as f:
            report(f.read())
    else:
        sys.exit(__doc__)
