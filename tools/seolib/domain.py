"""domain — registrable-ish host extraction.  (seolib)

The AEO/SEO tools repeatedly need "what site is this URL on?" to compare a
cited/linked host against a brand. This is that one notion.

ponytail: no public-suffix list, so foo.co.uk normalises to co.uk. Fine for
hostname-style brand domains; add `publicsuffix2` if you track sites on shared
suffixes (github.io, etc.). The caveat lives HERE so every caller inherits it
instead of re-deriving it (and silently forgetting it).
"""
from urllib.parse import urlparse


def domain(url):
    """netloc, lowercased, leading www. dropped. '' if there's no host."""
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host
