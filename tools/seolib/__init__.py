"""seolib — the SEO/AEO course capstone (see ADR 0001 + CONTEXT.md).

Stdlib-only shared modules the lesson tools converge on. Tools run as
`python3 tools/<tool>.py`, which puts tools/ on sys.path, so `from seolib
import ...` resolves with no path glue. The package's test surface is
tools/test_seolib.py (run from the repo root).
"""
from .domain import domain
from .fetch import fetch, fixture, Response

__all__ = ["domain", "fetch", "fixture", "Response"]
