// Single source of truth for lesson + tool metadata. The lesson bodies live as
// self-contained HTML in public/lessons/ (their quizzes + scoped CSS are
// pristine — served verbatim). The tools live in tools/ (see CONTEXT.md / ADR 0001).
export interface Lesson {
  num: string;
  slug: string; // file in public/lessons/
  title: string;
  blurb: string;
}

export interface Tool {
  name: string;
  lesson: string; // lesson num it belongs to
  desc: string;
  run: string;
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
  },
  {
    num: '0003',
    slug: '0003-structured-data.html',
    title: 'Structured Data',
    blurb:
      'JSON-LD that earns rich results and feeds machines your facts. Required vs recommended properties, validated.',
  },
  {
    num: '0004',
    slug: '0004-writing-for-retrieval.html',
    title: 'Writing for Retrieval',
    blurb:
      'Answer-first, self-contained chunks an engine can lift verbatim — the inverted pyramid as an AEO tactic.',
  },
  {
    num: '0005',
    slug: '0005-measuring-it.html',
    title: 'Measuring It',
    blurb:
      'Two scoreboards: Search Console gives ground truth via API; AI citations have none, so you build the proxy everyone builds.',
  },
  {
    num: '0006',
    slug: '0006-the-js-rendering-gap.html',
    title: 'The JS-Rendering Gap',
    blurb:
      "Google's deferred two-wave render, and why your urllib crawler — and most AI crawlers — only ever see the raw, pre-JS HTML.",
  },
  {
    num: '0007',
    slug: '0007-sitemaps-and-indexnow.html',
    title: 'Sitemaps + IndexNow',
    blurb:
      'Passive discovery (a sitemap every engine pulls) vs active push (IndexNow — instant, shared, and ignored by Google).',
  },
  {
    num: '0008',
    slug: '0008-eeat.html',
    title: 'E-E-A-T',
    blurb:
      'Experience, Expertise, Authoritativeness, Trust. Not a score, not a ranking factor — so audit the machine-detectable mix instead.',
  },
];

export const tools: Tool[] = [
  { name: 'crawl_audit.py', lesson: '0002',
    desc: 'Is a URL crawlable AND indexable? Checks robots.txt, status, noindex, title, canonical — the two gates before ranking.',
    run: 'python3 tools/crawl_audit.py https://example.com/page' },
  { name: 'schema_tool.py', lesson: '0003',
    desc: 'JSON-LD structured-data linter. Validates required vs recommended schema.org properties, and lints the JSON-LD on a live page.',
    run: 'python3 tools/schema_tool.py --demo' },
  { name: 'geo_lint.py', lesson: '0004',
    desc: 'GEO / writing-for-retrieval linter. Flags buried answers and non-self-contained chunks; rewards answer-first prose.',
    run: 'python3 tools/geo_lint.py --demo' },
  { name: 'citation_share.py', lesson: '0005',
    desc: 'Measures AI-citation coverage and share of voice from a set of answer-engine responses — the proxy every AEO tracker builds.',
    run: 'python3 tools/citation_share.py --demo' },
  { name: 'build_prompts.py', lesson: '0005',
    desc: 'Assembles a buyer-question prompt library (from an LLM fan-out or Search Console rows) in the shape citation_share.py consumes.',
    run: 'python3 tools/build_prompts.py --demo' },
  { name: 'render_gap.py', lesson: '0006',
    desc: 'Diffs raw HTML vs the rendered DOM and flags content/links/JSON-LD that exist only after JavaScript — what no-JS bots miss.',
    run: 'python3 tools/render_gap.py --demo' },
  { name: 'sitemap_ping.py', lesson: '0007',
    desc: 'Generates + validates a spec-compliant sitemap.xml, and builds a verified IndexNow push payload. The publish-and-notify step.',
    run: 'python3 tools/sitemap_ping.py --demo' },
  { name: 'eeat_audit.py', lesson: '0008',
    desc: 'Audits a page for the machine-detectable E-E-A-T proxy signals (author, sameAs, dates, publisher, sourcing). Not a score — a gap-finder.',
    run: 'python3 tools/eeat_audit.py --demo' },
];

/** Tools belonging to a lesson (e.g. the lesson card's "▸ tool" label). */
export function toolsForLesson(num: string): Tool[] {
  return tools.filter((t) => t.lesson === num);
}

/** The public/lessons slug for a lesson number (so a tool can link to its lesson). */
export function slugForLesson(num: string): string {
  return lessons.find((l) => l.num === num)?.slug ?? '';
}
