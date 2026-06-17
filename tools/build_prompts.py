#!/usr/bin/env python3
"""build_prompts.py — assemble a buyer-question prompt library. (Lesson 0005 helper)

A citation tracker is only as good as its prompt library — the fixed set of
buyer questions you re-run over time. This builds that library two ways and
emits it in the exact shape citation_share.py eats (a results.json skeleton
with empty response/citations for you to fill from a real engine run):

  fanout  — parse an LLM's brainstormed list of questions into clean prompts
            (you ask the engine; this cleans + filters the answer)
  gsc     — filter Google Search Console query rows down to the
            question-shaped, buyer-intent ones (real demand, not guesses)

Stdlib only. It does NOT call any API — you supply the engine/Search Console
output; the filtering and emitting logic is here and offline-testable.

  # mode 1: ask an engine, save its answer, then clean it
  #   prompt used: "List 25 questions someone asks when choosing a <product>."
  python3 build_prompts.py fanout llm_answer.txt > results.json

  # mode 2: feed Search Console rows (the API's searchanalytics.query output)
  python3 build_prompts.py gsc gsc_rows.json > results.json

  python3 build_prompts.py --demo
"""
import json
import re
import sys

# buyer-intent / question signals (lowercased match)
STARTERS = ("how ", "what ", "why ", "which ", "who ", "where ", "when ",
            "can ", "should ", "is ", "are ", "do ", "does ", "will ")
KEYWORDS = (" vs ", "best ", "top ", "cheapest ", "alternative",
            "compare", "review", "recommend")


def is_buyer_question(q):
    s = q.strip().lower()
    if len(s.split()) < 3:
        return False
    return s.endswith("?") or s.startswith(STARTERS) or any(k in s for k in KEYWORDS)


def clean_line(line):
    """Strip list markers and surrounding quotes from one brainstormed line."""
    s = line.strip()
    s = re.sub(r"^\s*(?:[-*•·]|\d+[.)])\s*", "", s)   # 1. / 2) / - / *
    s = s.strip().strip('"“”\'')
    return s.strip()


def dedupe(prompts):
    seen, out = set(), []
    for p in prompts:
        k = p.lower()
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


def from_fanout(text):
    """LLM brainstorm answer -> clean buyer-question list (drops the preamble)."""
    lines = [clean_line(l) for l in text.splitlines()]
    return dedupe([l for l in lines if l and is_buyer_question(l)])


def from_gsc(data):
    """Search Console rows -> buyer-question queries.

    Accepts the raw API response ({"rows":[{"keys":["q"],...}]}), a bare list
    of those row objects, or a plain list of query strings.
    """
    rows = data.get("rows", data) if isinstance(data, dict) else data
    queries = []
    for r in rows:
        if isinstance(r, str):
            queries.append(r)
        elif isinstance(r, dict) and r.get("keys"):
            queries.append(r["keys"][0])
    return dedupe([q for q in queries if is_buyer_question(q)])


def to_results(prompts):
    """Emit the results.json skeleton citation_share.py consumes."""
    skel = [{"prompt": p, "response": "", "citations": []} for p in prompts]
    return json.dumps(skel, indent=2, ensure_ascii=False)


FANOUT_SAMPLE = """Here are some questions buyers ask:
1. What is the best SEO audit tool for developers?
2. Ahrefs vs Semrush for a small team?
- How do I track rankings via an API?
3. "Cheapest backlink checker that's accurate?"
Thanks for reading!
"""

GSC_SAMPLE = {"rows": [
    {"keys": ["best seo audit tool for developers"], "clicks": 12},
    {"keys": ["acme corp login"], "clicks": 40},          # branded, not a question
    {"keys": ["how to get cited by chatgpt"], "clicks": 8},
    {"keys": ["seo"], "clicks": 3},                        # too short
]}


def demo():
    f = from_fanout(FANOUT_SAMPLE)
    assert "Thanks for reading!" not in f, "preamble/closing not dropped"
    assert "Ahrefs vs Semrush for a small team?" in f, "vs question dropped"
    assert all(not p[0].isdigit() and not p.startswith("-") for p in f), "list markers left in"
    assert len(f) == 4, f"expected 4 cleaned questions, got {len(f)}: {f}"

    g = from_gsc(GSC_SAMPLE)
    assert "acme corp login" not in g, "branded non-question kept"
    assert "seo" not in g, "too-short query kept"
    assert "how to get cited by chatgpt" in g, "real question dropped"
    assert len(g) == 2, f"expected 2 GSC questions, got {g}"

    obj = json.loads(to_results(f))
    assert obj[0] == {"prompt": f[0], "response": "", "citations": []}, "bad results shape"
    print("demo: all build_prompts assertions passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--demo"]:
        demo()
    elif args and args[0] == "fanout":
        text = open(args[1], encoding="utf-8").read() if len(args) > 1 else sys.stdin.read()
        print(to_results(from_fanout(text)))
    elif len(args) == 2 and args[0] == "gsc":
        with open(args[1], encoding="utf-8") as fh:
            print(to_results(from_gsc(json.load(fh))))
    else:
        sys.exit(__doc__)
