"""checklist — the shared runbox skeleton the audit tools print.  (seolib)

The leading title, the two horizontal rules, the verdict line, and the 2-space
indent are identical across the flat status-row tools (crawl_audit, schema_tool,
geo_lint, sitemap_ping). Only the row text and the rule width vary. This owns the
skeleton; callers format their own rows and pass a verdict.

Deliberately NOT used by the tools whose output isn't a flat status checklist:
render_gap (a numeric table), citation_share (coverage / share-of-voice), and
eeat_audit (rows grouped under E-E-A-T letters). Bending those through one
renderer would cost more than it saves — one shape per consumer, not forced.
"""


def mark(ok, yes="PASS", no="FAIL"):
    """Bracket label for a boolean row."""
    return yes if ok else no


def render(title, body_lines, verdict, *, width=56):
    """Title + rule + indented body rows + rule + verdict, as one string.

    body_lines are pre-formatted (each tool keeps its own row layout); they get
    the 2-space indent here. Returns the block with a trailing blank line.
    """
    parts = [f"\n  {title}", "  " + "-" * width]
    parts += ["  " + line for line in body_lines]
    parts += ["  " + "-" * width, "  " + verdict, ""]
    return "\n".join(parts)
