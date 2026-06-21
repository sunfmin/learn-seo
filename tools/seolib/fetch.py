"""fetch — the network seam.  (seolib)

Every tool that reads a live page repeated the same urllib + UA + timeout +
read-cap + charset dance. This is that, once. The `transport` argument is the
seam: production uses the urllib adapter; a test passes a fixture adapter so the
fetch-and-audit path is exercisable offline (two adapters = a real seam).
"""
import urllib.request
from dataclasses import dataclass, field

UA = "Mozilla/5.0 (compatible; seolib/1.0; +https://learn-seo.example)"
TIMEOUT = 15
READ_CAP = 800_000


@dataclass
class Response:
    url: str                              # final URL (after redirects)
    status: int
    body: str                             # decoded HTML, capped at READ_CAP
    headers: dict = field(default_factory=dict)  # lowercased name -> value

    def header(self, name):
        return self.headers.get(name.lower(), "")


def _urllib_transport(url, ua, timeout, read_cap):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        body = r.read(read_cap).decode(charset, "replace")
        return Response(
            url=r.geturl(),
            status=getattr(r, "status", 200),
            body=body,
            headers={"x-robots-tag": r.headers.get("X-Robots-Tag", "")},
        )


def fetch(url, *, ua=UA, timeout=TIMEOUT, read_cap=READ_CAP, transport=_urllib_transport):
    """GET `url` -> Response. Swap `transport` to fetch differently (or in tests)."""
    return transport(url, ua, timeout, read_cap)


def fixture(pages):
    """Build a transport that serves canned pages from a dict.

    pages: {url: html} or {url: Response}. Use as fetch(url, transport=fixture({...}))
    to test fetch-and-audit without a network.
    """
    def _transport(url, ua, timeout, read_cap):
        v = pages[url]
        if isinstance(v, Response):
            return v
        return Response(url=url, status=200, body=v)
    return _transport
