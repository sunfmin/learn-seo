// Single source of truth for lesson metadata. The lesson bodies themselves
// live as self-contained HTML in public/lessons/ (their quizzes + scoped CSS
// are pristine — served verbatim, zero regression).
export interface Lesson {
  num: string;
  slug: string; // file in public/lessons/
  title: string;
  blurb: string;
  tool?: string;
}

export const lessons: Lesson[] = [
  {
    num: '0001',
    slug: '0001-the-two-pipelines.html',
    title: 'The Two Pipelines',
    blurb:
      'Classic search (crawl → index → rank) vs AI answer engines (retrieve → generate → cite). The mental model the whole course hangs on.',
  },
  {
    num: '0002',
    slug: '0002-crawlable-vs-indexable.html',
    title: 'Crawlable vs Indexable',
    blurb:
      'The two gates a page passes before it can ever rank — and why one is robots.txt and the other is noindex/title/canonical.',
    tool: 'crawl_audit.py',
  },
  {
    num: '0003',
    slug: '0003-structured-data.html',
    title: 'Structured Data',
    blurb:
      'JSON-LD that earns rich results and feeds machines your facts. Required vs recommended properties, validated.',
    tool: 'schema_tool.py',
  },
  {
    num: '0004',
    slug: '0004-writing-for-retrieval.html',
    title: 'Writing for Retrieval',
    blurb:
      'Answer-first, self-contained chunks an engine can lift verbatim — the inverted pyramid as an AEO tactic.',
    tool: 'geo_lint.py',
  },
  {
    num: '0005',
    slug: '0005-measuring-it.html',
    title: 'Measuring It',
    blurb:
      'Two scoreboards: Search Console gives ground truth via API; AI citations have none, so you build the proxy everyone builds.',
    tool: 'citation_share.py · build_prompts.py',
  },
  {
    num: '0006',
    slug: '0006-the-js-rendering-gap.html',
    title: 'The JS-Rendering Gap',
    blurb:
      "Google's deferred two-wave render, and why your urllib crawler — and most AI crawlers — only ever see the raw, pre-JS HTML.",
    tool: 'render_gap.py',
  },
  {
    num: '0007',
    slug: '0007-sitemaps-and-indexnow.html',
    title: 'Sitemaps + IndexNow',
    blurb:
      'Passive discovery (a sitemap every engine pulls) vs active push (IndexNow — instant, shared, and ignored by Google).',
    tool: 'sitemap_ping.py',
  },
  {
    num: '0008',
    slug: '0008-eeat.html',
    title: 'E-E-A-T',
    blurb:
      "Experience, Expertise, Authoritativeness, Trust. Not a score, not a ranking factor — so audit the machine-detectable mix instead.",
    tool: 'eeat_audit.py',
  },
];
