// The shared glossary, bilingual (ADR 0003). One term = one record carrying both
// languages; the page renders the active locale. Simplified Chinese keeps the
// SEO/AEO jargon in English (glossed on first use) — the terms ARE the headwords.
import type { Lang } from './ui';

export type Tag = 'seo' | 'aeo' | 'both';
export interface Term {
  t: Record<Lang, string>; // headword
  tag: Tag;
  d: Record<Lang, string>; // definition (inline HTML allowed)
}
export interface Group {
  h: Record<Lang, string>;
  terms: Term[];
}

export const groups: Group[] = [
  {
    h: { en: 'The fields', zh: '领域' },
    terms: [
      {
        t: { en: 'SEO — Search Engine Optimization', zh: 'SEO — 搜索引擎优化' },
        tag: 'seo',
        d: {
          en: 'Making a site rank higher in classic search results pages (the "ten blue links"). Optimizes for the <em>crawl → index → rank → serve</em> pipeline.',
          zh: '让网站在经典搜索结果页（那“十条蓝色链接”）里排得更高。优化的是 <em>crawl → index → rank → serve</em> 这条管线。',
        },
      },
      {
        t: { en: 'AEO — Answer Engine Optimization', zh: 'AEO — 答案引擎优化' },
        tag: 'aeo',
        d: {
          en: 'Making your content the source an AI answer engine <em>cites</em> when it generates a reply (ChatGPT, Claude, Perplexity, Google AI Overviews). Sometimes called GEO.',
          zh: '让你的内容成为 AI 答案引擎（ChatGPT、Claude、Perplexity、Google AI Overviews）生成回复时所<em>引用（cite）</em>的来源。有时也叫 GEO。',
        },
      },
      {
        t: { en: 'GEO — Generative Engine Optimization', zh: 'GEO — 生成式引擎优化' },
        tag: 'aeo',
        d: {
          en: 'Academic name for AEO, from the GEO research paper. Same goal: visibility inside generated answers, not just ranked links.',
          zh: 'AEO 的学术叫法，出自 GEO 研究论文。目标相同：在生成的答案里获得可见度，而不只是排名链接。',
        },
      },
    ],
  },
  {
    h: { en: 'The classic pipeline', zh: '经典管线' },
    terms: [
      {
        t: { en: 'Crawling', zh: 'Crawling（抓取）' },
        tag: 'seo',
        d: {
          en: 'A bot (e.g. Googlebot) fetches your pages by following links and reading your <code>sitemap.xml</code>. Gated by <code>robots.txt</code>.',
          zh: 'bot（如 Googlebot）通过跟随链接、读取你的 <code>sitemap.xml</code> 来抓取页面。受 <code>robots.txt</code> 把关。',
        },
      },
      {
        t: { en: 'Indexing', zh: 'Indexing（索引）' },
        tag: 'seo',
        d: {
          en: "The engine parses a crawled page, renders it, and stores it in a giant searchable database. A page that isn't indexed can never rank.",
          zh: '引擎解析抓取到的页面、渲染它，并存入一个巨大的可搜索数据库。没被 index 的页面永远无法排名。',
        },
      },
      {
        t: { en: 'Rendering (two-wave / deferred)', zh: 'Rendering 渲染（两波 / 延迟）' },
        tag: 'both',
        d: {
          en: 'Google processes JS pages in phases: it crawls the <em>raw HTML</em> first, then — in a <em>separate, deferred queue</em>, once resources allow — a headless Chrome runs the JavaScript and re-indexes what it produced. Content that only exists after JS is indexed late, or never by bots that don\'t render.',
          zh: 'Google 分阶段处理 JS 页面：先抓取<em>原始 HTML</em>，然后——在一个<em>独立、延迟的队列</em>里，等资源允许时——用 headless Chrome 跑 JavaScript，并对产物重新 index。只在 JS 执行后才存在的内容，会被晚很久才 index，或被不渲染的 bot 永远漏掉。',
        },
      },
      {
        t: { en: 'CSR vs SSR / SSG', zh: 'CSR 对比 SSR / SSG' },
        tag: 'both',
        d: {
          en: '<b>Client-side rendering (CSR):</b> the server sends an empty shell (<code>&lt;div id="root"&gt;</code>) and JS builds the page in the browser — invisible to no-JS bots. <b>Server-side rendering (SSR)</b> / <b>static site generation (SSG):</b> the content is in the first HTML response, seen by every bot immediately. For SEO/AEO, get facts into the server\'s HTML.',
          zh: '<b>客户端渲染（CSR）：</b>服务器只发一个空壳（<code>&lt;div id="root"&gt;</code>），由 JS 在浏览器里搭出页面——对不跑 JS 的 bot 不可见。<b>服务端渲染（SSR）</b> / <b>静态站点生成（SSG）：</b>内容就在第一个 HTML 响应里，每个 bot 立刻看得到。做 SEO/AEO，请把事实放进服务器发出的 HTML 里。',
        },
      },
      {
        t: { en: 'Ranking', zh: 'Ranking（排名）' },
        tag: 'seo',
        d: {
          en: 'For a given query, the engine orders indexed pages by hundreds of signals (relevance, links, quality, freshness). Decides position.',
          zh: '对某个 query，引擎按数百个信号（相关性、链接、质量、新鲜度）给已 index 的页面排序。决定位置。',
        },
      },
      {
        t: { en: 'Serving / SERP', zh: 'Serving / SERP（结果页）' },
        tag: 'seo',
        d: {
          en: 'The Search Engine Results Page actually shown to the user — links, plus features like snippets, knowledge panels, and AI Overviews.',
          zh: '真正展示给用户的搜索结果页（SERP）——链接，加上 snippet、知识面板、AI Overviews 等功能。',
        },
      },
    ],
  },
  {
    h: { en: 'The answer-engine pipeline', zh: '答案引擎管线' },
    terms: [
      {
        t: { en: 'Retrieval', zh: 'Retrieval（检索）' },
        tag: 'aeo',
        d: {
          en: 'The answer engine pulls candidate passages — usually from the <em>same crawled/indexed web</em> (often via a live search) — to ground its answer. This is why indexing still matters for AEO.',
          zh: '答案引擎拉取候选段落——通常来自<em>同一个被 crawl/index 的网络</em>（常通过一次实时搜索）——来为答案提供依据。这就是为什么 index 对 AEO 仍然重要。',
        },
      },
      {
        t: { en: 'Synthesis / Generation', zh: 'Synthesis / Generation（合成 / 生成）' },
        tag: 'aeo',
        d: {
          en: 'The LLM writes a single composed answer from the retrieved passages plus its training knowledge.',
          zh: 'LLM 综合检索到的段落加上它的训练知识，写出一个统一的答案。',
        },
      },
      {
        t: { en: 'Citation', zh: 'Citation（引用）' },
        tag: 'aeo',
        d: {
          en: 'The link/attribution the engine shows next to (or behind) its answer. Being the cited source is the AEO win — the equivalent of a #1 rank.',
          zh: '引擎在答案旁（或背后）展示的链接/出处。成为被引用的来源就是 AEO 的赢点——相当于经典搜索里的第 1 名。',
        },
      },
      {
        t: { en: 'Passage / chunk', zh: 'Passage / chunk（段落 / 块）' },
        tag: 'aeo',
        d: {
          en: 'The retrieval unit. Engines split pages into smaller passages, embed them, and pull the few most relevant — so the thing that gets cited is a <em>self-contained chunk</em>, not the whole page. Write each section to stand alone.',
          zh: 'retrieval 的基本单位。引擎把页面切成更小的段落，做 embedding，再拉出最相关的几个——所以被引用的是一个<em>自足的 chunk</em>，而不是整页。把每一节都写成能独立成立。',
        },
      },
      {
        t: { en: 'Answer-first (inverted pyramid)', zh: 'Answer-first 答案先行（倒金字塔）' },
        tag: 'aeo',
        d: {
          en: "Lead with the direct answer in 1–2 sentences, then expand with detail. Makes the opening a quotable, self-contained chunk an engine can lift verbatim. Borrowed from journalism's inverted pyramid.",
          zh: '用 1–2 句先给出直接答案，再展开细节。这让开头成为一个可引用、自足的 chunk，引擎能原样摘走。借自新闻业的倒金字塔写法。',
        },
      },
    ],
  },
  {
    h: { en: 'Quality & trust', zh: '质量与信任' },
    terms: [
      {
        t: { en: 'E-E-A-T', zh: 'E-E-A-T' },
        tag: 'both',
        d: {
          en: '<b>Experience, Expertise, Authoritativeness, Trust</b> — Google\'s framework for "is this content trustworthy?", used by quality raters. <em>Trust is the centre</em>; the others feed it. <b>Not a direct ranking factor and not a score</b> — Google approximates it with "a mix of factors." For builders: audit the machine-detectable proxies (author + <code>sameAs</code>, dates, publisher, outbound sourcing, about/contact).',
          zh: '<b>Experience（经验）、Expertise（专业）、Authoritativeness（权威）、Trust（信任）</b>——Google 用来判断“这内容可信吗？”的框架，供质量评估员使用。<em>Trust 是中心</em>，其余三者为它供能。<b>它不是直接的排名因子，也不是一个分数</b>——Google 用“一组混合因子”来近似它。对开发者：审查机器可检测的 proxy（author + <code>sameAs</code>、日期、publisher、对外引用、about/contact）。',
        },
      },
      {
        t: { en: 'YMYL — Your Money or Your Life', zh: 'YMYL — 钱财或生命' },
        tag: 'seo',
        d: {
          en: 'Topics that could significantly affect health, financial stability, safety, or societal well-being. Held to a far higher E-E-A-T bar — trust signals matter most here, and faking them is risky.',
          zh: '可能显著影响健康、财务稳定、安全或社会福祉的主题。E-E-A-T 的门槛要高得多——这里信任信号最关键，伪造它们很危险。',
        },
      },
      {
        t: { en: 'sameAs', zh: 'sameAs' },
        tag: 'both',
        d: {
          en: 'A schema.org property linking an entity (a <code>Person</code> author, an <code>Organization</code>) to its authoritative profiles elsewhere (LinkedIn, Wikipedia, ORCID). The machine-readable way to assert <em>who</em> an author is — an Authoritativeness signal.',
          zh: 'schema.org 的一个属性，把一个实体（<code>Person</code> 作者、<code>Organization</code>）链接到它在别处的权威资料页（LinkedIn、Wikipedia、ORCID）。这是机器可读地声明作者<em>是谁</em>的方式——一个 Authoritativeness 信号。',
        },
      },
    ],
  },
  {
    h: { en: 'Builder-facing artifacts', zh: '面向开发者的产物' },
    terms: [
      {
        t: { en: 'Structured data', zh: 'Structured data（结构化数据）' },
        tag: 'both',
        d: {
          en: 'Machine-readable markup (usually <code>schema.org</code> JSON-LD) embedded in a page that tells engines exactly what an entity is. Powers rich results and helps machines extract facts.',
          zh: '嵌入页面的机器可读标记（通常是 <code>schema.org</code> 的 JSON-LD），明确告诉引擎某个实体是什么。它驱动 rich result，并帮机器提取事实。',
        },
      },
      {
        t: { en: 'JSON-LD', zh: 'JSON-LD' },
        tag: 'both',
        d: {
          en: 'Google\'s recommended structured-data format: a <code>&lt;script type="application/ld+json"&gt;</code> block of JSON, kept separate from visible HTML. Each type has <em>required</em> properties (miss one → no rich result) and <em>recommended</em> ones.',
          zh: 'Google 推荐的结构化数据格式：一个 <code>&lt;script type="application/ld+json"&gt;</code> 的 JSON 块，与可见 HTML 分离。每种类型都有 <em>required（必填）</em>属性（缺一个 → 没有 rich result）和 <em>recommended（推荐）</em>属性。',
        },
      },
      {
        t: { en: 'Rich result', zh: 'Rich result（富结果）' },
        tag: 'seo',
        d: {
          en: 'An enhanced SERP listing — star ratings, prices, FAQ accordions — earned by valid structured data. Takes more space, draws more clicks than a plain blue link.',
          zh: '一种增强的 SERP 条目——星级评分、价格、FAQ 折叠——靠有效的 structured data 赢得。它占更多空间，比普通蓝色链接吸引更多点击。',
        },
      },
      {
        t: { en: 'robots.txt', zh: 'robots.txt' },
        tag: 'both',
        d: {
          en: 'A file at your site root that tells crawlers which paths they may or may not fetch. First thing a crawler reads.',
          zh: '位于站点根目录的文件，告诉 crawler 哪些路径可以、哪些不可以抓取。是 crawler 读的第一样东西。',
        },
      },
      {
        t: { en: 'sitemap.xml', zh: 'sitemap.xml' },
        tag: 'both',
        d: {
          en: 'A machine-readable list of your URLs (with metadata) that helps crawlers discover pages efficiently. <em>Passive</em>: engines pull it on their own schedule. Spec limits: ≤50,000 URLs and ≤50 MB per file; <code>&lt;loc&gt;</code> required, <code>&lt;lastmod&gt;</code> optional (W3C date); all URLs on one host. Past 50k URLs, use a <b>sitemap index</b> (a sitemap of sitemaps).',
          zh: '一份机器可读的 URL 清单（含元数据），帮 crawler 高效发现页面。它是<em>被动的</em>：引擎按自己的节奏来拉取。规范限制：每个文件 ≤50,000 个 URL 且 ≤50 MB；<code>&lt;loc&gt;</code> 必填，<code>&lt;lastmod&gt;</code> 可选（W3C 日期）；所有 URL 同一 host。超过 5 万个 URL，就用 <b>sitemap index</b>（sitemap 的 sitemap）。',
        },
      },
      {
        t: { en: 'IndexNow', zh: 'IndexNow' },
        tag: 'both',
        d: {
          en: 'An open protocol to <em>actively push</em> changed URLs to engines: <code>POST {host, key, keyLocation, urlList}</code> (≤10,000 URLs/post), and the ping is shared across all participants. Supported by Bing, Yandex, Naver, Seznam — <b>not Google</b>, which sticks to sitemaps + its own crawl scheduling. The key (8–128 chars) lives in a file at your root to prove host ownership.',
          zh: '一个开放协议，用来把改动过的 URL <em>主动推送</em>给引擎：<code>POST {host, key, keyLocation, urlList}</code>（每次 ≤10,000 个 URL），且这次 ping 会在所有参与方之间共享。Bing、Yandex、Naver、Seznam 支持——<b>Google 不支持</b>，它坚持用 sitemap + 自己的抓取调度。key（8–128 字符）放在根目录的一个文件里，用来证明 host 所有权。',
        },
      },
      {
        t: { en: 'noindex', zh: 'noindex' },
        tag: 'seo',
        d: {
          en: 'A directive telling the engine to drop a page from the index. Lives in <code>&lt;meta name="robots"&gt;</code> or the <code>X-Robots-Tag</code> header. Only works if the page is <em>crawlable</em> — a blocked page\'s noindex is never read.',
          zh: '一个指令，告诉引擎把某页面从 index 里剔除。写在 <code>&lt;meta name="robots"&gt;</code> 或 <code>X-Robots-Tag</code> 响应头里。只有当页面<em>可被 crawl</em> 时才生效——被 robots 屏蔽的页面，它的 noindex 永远读不到。',
        },
      },
      {
        t: { en: 'X-Robots-Tag', zh: 'X-Robots-Tag' },
        tag: 'seo',
        d: {
          en: 'An HTTP response header that carries indexing directives (like <code>noindex</code>) — the header-level equivalent of the robots meta tag. Useful for non-HTML files (PDFs, images).',
          zh: '一个携带索引指令（如 <code>noindex</code>）的 HTTP 响应头——robots meta 标签的响应头版本。对非 HTML 文件（PDF、图片）很有用。',
        },
      },
      {
        t: { en: 'Canonical', zh: 'Canonical（规范链接）' },
        tag: 'both',
        d: {
          en: 'Via <code>&lt;link rel="canonical"&gt;</code>: declares which URL is the "real" one when several show near-identical content, so the engine consolidates signals onto one.',
          zh: '通过 <code>&lt;link rel="canonical"&gt;</code>：当多个 URL 展示几乎相同的内容时，声明哪个才是“真身”，让引擎把信号归并到一个上。',
        },
      },
      {
        t: { en: 'Search Console (API)', zh: 'Search Console（API）' },
        tag: 'seo',
        d: {
          en: "Google's first-party feed for your site: impressions, clicks, average position, and the queries that surfaced you — from Google's own logs. The <code>searchanalytics.query</code> endpoint makes it pollable. The <code>Web</code> search type now includes AI-feature traffic.",
          zh: 'Google 给你站点的第一方数据源：曝光、点击、平均排名，以及让你出现的那些 query——全部来自 Google 自己的日志。<code>searchanalytics.query</code> 端点让它可被轮询。<code>Web</code> 这个搜索类型现在已包含 AI 功能带来的流量。',
        },
      },
      {
        t: { en: 'Share of voice', zh: 'Share of voice（声量占比）' },
        tag: 'aeo',
        d: {
          en: "Your slice of all citations across a prompt set: <em>your citations ÷ everyone's citations</em>. The headline AEO metric — but a <em>proxy</em>, since the prompt set is sampled, not the engine's real traffic. Pair with <em>coverage</em> (% of prompts that cite you at all).",
          zh: '在一组 prompt 里，你占全部 citation 的比例：<em>你的 citation ÷ 所有人的 citation</em>。AEO 的头号指标——但它是个 <em>proxy</em>，因为 prompt 集是抽样的，不是引擎的真实流量。要和 <em>coverage</em>（有多少比例的 prompt 至少引用了你一次）一起看。',
        },
      },
    ],
  },
];
