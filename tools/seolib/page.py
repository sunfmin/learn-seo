"""page — parse an HTML string once into the signals every tool needs.  (seolib)

Three tools each grew their own HTMLParser subclass (crawl_audit.HeadScan,
render_gap.Extract, eeat_audit.Scan) re-solving the same script/style skip,
ld+json capture, link/title/heading scraping. This is the one scanner.

    parse(html) -> Page

Page deliberately stays domain-neutral: raw signals (title, meta, canonical,
links, headings, words, ld_blocks). Interpreting them (is this noindex? is the
JSON-LD valid? is the page client-rendered?) stays in the tools / seolib.ld.
"""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser

_HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


@dataclass
class Page:
    title: str | None
    meta: dict            # lowercased <meta name> -> content (raw)
    canonical: str | None
    rel_author: bool      # any <a|link rel="author">
    links: list           # every <a href> value
    headings: dict         # {"h1": n, ...} only for levels present
    words: int            # visible words (excludes title, script, style, ld+json)
    ld_blocks: list       # raw application/ld+json script bodies


class _Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.meta = {}
        self.canonical = None
        self.rel_author = False
        self.links = []
        self.headings = {}
        self.words = 0
        self.ld_blocks = []
        self._skip = 0        # depth inside non-ld script/style
        self._in_title = False
        self._in_ld = False
        self._ld = ""

    def _start(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        rel = a.get("rel", "").lower().split()
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name and a.get("content"):
                self.meta[name] = a["content"]
        elif tag == "link":
            if "canonical" in rel and a.get("href"):
                self.canonical = a["href"]
            if "author" in rel:
                self.rel_author = True
        elif tag == "a":
            if "author" in rel:
                self.rel_author = True
            if a.get("href"):
                self.links.append(a["href"])
        elif tag in _HEADINGS:
            self.headings[tag] = self.headings.get(tag, 0) + 1
        elif tag == "script":
            if "ld+json" in a.get("type", "").lower():
                self._in_ld, self._ld = True, ""
            else:
                self._skip += 1
        elif tag == "style":
            self._skip += 1

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            if self._in_ld:
                self.ld_blocks.append(self._ld)
                self._in_ld = False
            elif self._skip:
                self._skip -= 1
        elif tag == "style" and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_ld:
            self._ld += data
        elif self._skip:
            return
        elif self._in_title:
            t = data.strip()
            if t:
                self.title = (self.title or "") + t
        else:
            self.words += len(data.split())


def parse(html):
    s = _Scan()
    s.feed(html)
    return Page(s.title, s.meta, s.canonical, s.rel_author, s.links,
                s.headings, s.words, s.ld_blocks)
