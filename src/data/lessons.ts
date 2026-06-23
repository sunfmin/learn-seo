// Lesson metadata lives in each lesson's MDX frontmatter (the `lessons` content
// collection — see src/content.config.ts and ADR 0002), now one file per locale
// (ADR 0003). What lives here is the tool catalogue (bilingual descriptions) and
// the locale-aware lesson↔tool helpers the hub pages use.
import { getCollection, type CollectionEntry } from 'astro:content';
import type { Lang } from '../i18n/ui';

export interface Tool {
  name: string;
  lesson: string; // lesson num it belongs to
  desc: Record<Lang, string>;
  run: string;
}

export const tools: Tool[] = [
  { name: 'crawl_audit.py', lesson: '0002',
    desc: {
      en: 'Is a URL crawlable AND indexable? Checks robots.txt, status, noindex, title, canonical — the two gates before ranking.',
      zh: '一个 URL 既可被 crawl（抓取）又可被 index（索引）吗？检查 robots.txt、状态码、noindex、title、canonical——排名前的两道门。',
    },
    run: 'python3 tools/crawl_audit.py https://example.com/page' },
  { name: 'schema_tool.py', lesson: '0003',
    desc: {
      en: 'JSON-LD structured-data linter. Validates required vs recommended schema.org properties, and lints the JSON-LD on a live page.',
      zh: 'JSON-LD 结构化数据（structured data）linter。校验 schema.org 的 required 与 recommended 属性，并对线上页面的 JSON-LD 做检查。',
    },
    run: 'python3 tools/schema_tool.py --demo' },
  { name: 'geo_lint.py', lesson: '0004',
    desc: {
      en: 'GEO / writing-for-retrieval linter. Flags buried answers and non-self-contained chunks; rewards answer-first prose.',
      zh: 'GEO / 为 retrieval 而写的 linter。标记被埋没的答案和不自足的 chunk（段落块）；奖励“答案先行”的写法。',
    },
    run: 'python3 tools/geo_lint.py --demo' },
  { name: 'citation_share.py', lesson: '0005',
    desc: {
      en: 'Measures AI-citation coverage and share of voice from a set of answer-engine responses — the proxy every AEO tracker builds.',
      zh: '从一组 answer-engine（答案引擎）回复中测量 AI citation（引用）的 coverage 与 share of voice（声量占比）——每个 AEO 追踪工具都在搭的那个 proxy（代理指标）。',
    },
    run: 'python3 tools/citation_share.py --demo' },
  { name: 'build_prompts.py', lesson: '0005',
    desc: {
      en: 'Assembles a buyer-question prompt library (from an LLM fan-out or Search Console rows) in the shape citation_share.py consumes.',
      zh: '把买家问题组装成一个 prompt 库（来自 LLM 扇出或 Search Console 行数据），格式正好是 citation_share.py 所需的。',
    },
    run: 'python3 tools/build_prompts.py --demo' },
  { name: 'render_gap.py', lesson: '0006',
    desc: {
      en: 'Diffs raw HTML vs the rendered DOM and flags content/links/JSON-LD that exist only after JavaScript — what no-JS bots miss.',
      zh: '对比原始 HTML 与渲染后 DOM，标记只在 JavaScript 执行后才出现的内容/链接/JSON-LD——也就是不跑 JS 的 bot 会漏掉的东西。',
    },
    run: 'python3 tools/render_gap.py --demo' },
  { name: 'sitemap_ping.py', lesson: '0007',
    desc: {
      en: 'Generates + validates a spec-compliant sitemap.xml, and builds a verified IndexNow push payload. The publish-and-notify step.',
      zh: '生成并校验符合规范的 sitemap.xml，并构造一个经验证的 IndexNow 推送 payload。即“发布并通知”这一步。',
    },
    run: 'python3 tools/sitemap_ping.py --demo' },
  { name: 'eeat_audit.py', lesson: '0008',
    desc: {
      en: 'Audits a page for the machine-detectable E-E-A-T proxy signals (author, sameAs, dates, publisher, sourcing). Not a score — a gap-finder.',
      zh: '审查一个页面上机器可检测的 E-E-A-T proxy 信号（author、sameAs、日期、publisher、引用来源）。它不是打分——而是找差距。',
    },
    run: 'python3 tools/eeat_audit.py --demo' },
  { name: 'site_audit.py', lesson: '0009',
    desc: {
      en: 'The capstone: crawls a whole site BFS from a seed and runs every gate from 0002–0008 on each page, then rolls findings into one prioritized report (a check failing site-wide = a template bug).',
      zh: '集大成之作：从一个种子 URL 起按 BFS（广度优先）crawl（抓取）整个站点，对每个页面跑 0002–0008 的所有 gate（关卡），再把结果汇总成一份带优先级的报告（某项检查在全站失败 = 模板 bug）。',
    },
    run: 'python3 tools/site_audit.py --demo' },
  { name: 'ai_bots.py', lesson: '0010',
    desc: {
      en: "Reports your site's ALLOW/BLOCK posture toward AI crawlers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot, CCBot…) from robots.txt, and whether you ship the non-standard llms.txt. Posture, not pass/fail.",
      zh: '从 robots.txt 读出你的站点对 AI crawler（GPTBot、ClaudeBot、Google-Extended、PerplexityBot、CCBot……）的 ALLOW/BLOCK 姿态，以及你是否提供了非标准的 llms.txt。报告的是姿态，而非对错。',
    },
    run: 'python3 tools/ai_bots.py --demo' },
];

/** Tools belonging to a lesson (e.g. the lesson card's "▸ tool" label). */
export function toolsForLesson(num: string): Tool[] {
  return tools.filter((t) => t.lesson === num);
}

type LessonEntry = CollectionEntry<'lessons'>;

/** The locale segment of an entry id (`en/0001-…` → 'en'). */
export function langOf(entry: LessonEntry): Lang {
  return entry.id.split('/')[0] as Lang;
}

/** The locale-free slug + `.html` (`en/0001-foo` → `0001-foo.html`). */
export function slugFor(entry: LessonEntry): string {
  return `${entry.id.replace(/^(en|zh)\//, '')}.html`;
}

/** Lessons for one locale, ordered by lesson number (the single source of order). */
export async function lessonsFor(lang: Lang): Promise<LessonEntry[]> {
  return (await getCollection('lessons'))
    .filter((l) => langOf(l) === lang)
    .sort((a, b) => a.data.num.localeCompare(b.data.num));
}

/** The /lessons/ slug (`NNNN-*.html`) for a lesson number, in a given locale. */
export async function slugForLesson(num: string, lang: Lang = 'en'): Promise<string> {
  const entry = (await getCollection('lessons')).find(
    (l) => langOf(l) === lang && l.data.num === num,
  );
  return entry ? slugFor(entry) : '';
}
