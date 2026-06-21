# ADR 0001 — Extract a shared `seolib` package

- Status: accepted
- Date: 2026-06-21

## Context

The course ships one stdlib-only Python tool per lesson (`tools/*.py`). Each tool's
docstring advertises "Stdlib only" and the tools were written to be **self-contained,
copy-pasteable single files** — a student can grab `render_gap.py` alone and run it.

That property created real duplication across the eight tools (surfaced by an
architecture review):

- three hand-rolled `HTMLParser` subclasses re-solving "pull signals from HTML"
  (`crawl_audit.HeadScan`, `render_gap.Extract`, `eeat_audit.Scan`);
- three copies of `urllib` fetch (UA + timeout + read-cap + charset);
- the registrable-`domain` notion re-derived three times, its public-suffix caveat
  documented in only one;
- a JSON-LD extractor (`eeat_audit.flatten_ld`) and a JSON-LD linter
  (`schema_tool.lint`) that are two halves of one capability but never meet.

The duplication is shallow — interfaces nearly as complex as their implementations.
Deepening it into shared modules improves **locality** (HTML quirks, fetch policy,
the public-suffix caveat fixed once) and **leverage** (one interface, N tools), and
turns the tools' `--demo` self-checks into one real test surface.

## Decision

Extract a shared, **still stdlib-only** package at `tools/seolib/` and migrate the
lesson tools to import from it (`from seolib import domain, fetch, parse, ...`).

We accept that the tools are **no longer standalone single files**. We reconcile this
with the teaching goal by reframing: `MISSION.md` is "build software that does SEO/AEO
automatically." The lesson tools are tool-by-tool *sketches*; `seolib` is the
**capstone** — the actual product the course builds toward. The lessons keep teaching
each mechanism from scratch in prose; the code converges on the library.

Mechanics:

- `tools/seolib/` is a package; intra-package imports are relative (`from .fetch import …`).
- Tools are run as `python3 tools/<tool>.py`, which puts `tools/` on `sys.path[0]`, so
  `from seolib import …` resolves with no path glue.
- `tools/test_seolib.py` is the package's single test surface (run from repo root).
- The network edge gets a real seam: a `urllib` adapter in production, a fixture
  adapter in tests — so a fetch-and-audit path is testable for the first time.

## Consequences

- Lesson tools now depend on `tools/seolib/`; the "one self-contained file" property is
  gone. Each migrated tool's docstring says so and points at `seolib`.
- Still zero third-party dependencies.
- HTML parsing, fetch policy, domain extraction, and JSON-LD handling each have one home.
- New capability falls out free: `schema_tool` can lint a live page's JSON-LD.
- Future architecture reviews should NOT re-suggest "keep everything standalone" — that
  trade was made here, deliberately, in favour of the capstone library.
