#!/usr/bin/env python3
"""test_seolib.py — the seolib package's single test surface.

The interface is the test surface: every shared module is exercised here,
through the same import the tools use. Run from the repo root:

    python3 tools/test_seolib.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # ensure tools/ importable

from seolib import domain


def test_domain():
    assert domain("https://www.Ahrefs.com/seo") == "ahrefs.com"
    assert domain("http://moz.com") == "moz.com"
    assert domain("https://sub.example.co.uk/p?q=1") == "sub.example.co.uk"
    assert domain("not-a-url") == ""


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
    print(f"test_seolib: {len(tests)} group(s) passed.")


if __name__ == "__main__":
    main()
