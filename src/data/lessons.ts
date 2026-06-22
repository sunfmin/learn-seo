// Lesson metadata now lives in each lesson's MDX frontmatter (the `lessons`
// content collection — see src/content.config.ts and ADR 0002). What remains here
// is the tool catalogue and the lesson↔tool mapping the tools/lessons hub pages use.
import { getCollection } from 'astro:content';

export interface Tool {
  name: string;
  lesson: string; // lesson num it belongs to
  desc: string;
  run: string;
}

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

/**
 * The /lessons/ slug (`NNNN-*.html`) for a lesson number, read from the content
 * collection. Async because the collection is the single source of truth now.
 */
export async function slugForLesson(num: string): Promise<string> {
  const entry = (await getCollection('lessons')).find((l) => l.data.num === num);
  return entry ? `${entry.id}.html` : '';
}
