# SEO / AEO for Builders — Resources

All URLs verified resolving as of 2026-06-17. Knowledge for lessons is drawn from here, not from memory.

## Knowledge

### Official / primary docs (start here)

- [SEO Starter Guide: The Basics — Google Search Central](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
  Google's own beginner doc on crawling, indexing, and what actually moves rankings. The canonical "first read" before any opinionated blog.
- [In-depth guide to how Google Search works — Google Search Central](https://developers.google.com/search/docs/fundamentals/how-search-works)
  The crawl → index → serve pipeline from the engine itself. Use for: Lesson 0001 (the two pipelines), anything about the classic pipeline mechanics.
- [SEO for developers (Get started) — Google Search Central](https://developers.google.com/search/docs/fundamentals/get-started-developers)
  Developer-angled entry point: rendering, JS SEO, technical requirements. Reach for it when building tooling, not writing content.
- [Understand the JavaScript SEO basics — Google Search Central](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
  The crawl → render → index phases and why rendering is a *deferred queue* ("Once Google's resources allow, a headless Chrome renders the page and executes the JavaScript"). Use for: Lesson 0006 (the JS-rendering gap), anything about client-side rendering, SSR/SSG, or why a no-JS crawler misses content.
- [Introduction to structured data markup — Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
  How JSON-LD/Microdata/RDFa drive rich results. Read before automating any schema generation.
- [Getting Started — schema.org](https://schema.org/docs/gs.html)
  The authoritative vocabulary spec (types, properties, formats). The source of truth your structured-data tooling should validate against.
- [About the Search Console API + API Reference — Google](https://developers.google.com/webmaster-tools/about) ([reference](https://developers.google.com/webmaster-tools/v1/api_reference_index))
  REST API for Search Analytics, Sitemaps, Sites, URL Inspection. Backbone for any SEO monitoring/automation you build. The "Web" search-type now includes AI-feature traffic.
- [Search Quality Rater Guidelines (PDF) — Google](https://services.google.com/fh/files/misc/hsw-sqrg.pdf)
  Google's full evaluator manual defining E-E-A-T and "quality." Use to understand *what Google considers good content* at the policy level.
- [IndexNow — getting started (Bing)](https://www.bing.com/indexnow/getstarted) · [protocol docs](https://www.indexnow.org/documentation)
  Open protocol for instantly pushing URL changes to Bing/Yandex/others. Use when building a crawl-notification step into a publishing pipeline.

### Recognized authorities (evidence-based)

- [Beginner's Guide to SEO — Ahrefs](https://ahrefs.com/seo)
  Clean 10-chapter primer, now with chapters on AI search. Best free structured curriculum for zero → competent.
- [The Beginner's Guide to SEO — Moz](https://moz.com/beginners-guide-to-seo)
  Long-standing, vendor-neutral conceptual foundation. Pair with Ahrefs for a second framing of the fundamentals.

### AI Overviews / AEO / GEO

- [AI features and your website — Google Search Central](https://developers.google.com/search/docs/appearance/ai-features)
  Google on-record: how AI Overviews / AI Mode pick content and how to control inclusion (`nosnippet`, `noindex`). Primary source that debunks most AEO myths.
- [Optimizing your website for generative AI features on Google Search — Google Search Central](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
  Google's explicit "AEO/GEO is still SEO" guidance (May 2026). Reach for it whenever a vendor claims you need `llms.txt` or special AI markup. ([announcement](https://developers.google.com/search/blog/2026/05/a-new-resource-for-optimizing))
- [Introducing Search Generative AI performance reports in Search Console — Google (June 2026)](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
  Newest primary source: Google's *own* reporting on how your content performs in AI experiences. Closest thing to a first-party AEO measurement feed (UI report — see Gaps re: API).
- [GEO: Generative Engine Optimization — Aggarwal, Murahari, Rajpurohit, Kalyan, Narasimhan, Deshpande (arXiv:2311.09735, KDD 2024)](https://arxiv.org/abs/2311.09735)
  THE canonical academic paper. Coined "GEO," introduced GEO-bench, measured tactics (up to ~40% visibility lift). The rigorous baseline beneath the marketing-blog noise. ([ACM venue](https://dl.acm.org/doi/10.1145/3637528.3671900))
- [7 Steps for Tracking Your ChatGPT Visibility With Ahrefs — Louise Linehan (Ahrefs)](https://ahrefs.com/blog/chatgpt-visibility-tracking/)
  Concrete, builder-friendly walkthrough of AI share-of-voice, citation analysis, fan-out queries. Use when designing what metrics your own AEO tracker should compute.

## Wisdom (Communities)

- [r/TechSEO](https://www.reddit.com/r/TechSEO/) (~41k)
  Technical/engineering side: rendering, log analysis, headers, indexing, API quirks. Best fit for a builder debugging tooling.
- [r/bigseo](https://www.reddit.com/r/bigseo/) (~127k)
  Higher-signal practitioner discussion bridging technical and strategy. Ask here once past beginner level.
- [r/SEO](https://www.reddit.com/r/SEO/)
  Largest general SEO town square. Good for algorithm-update tracking and quick sanity checks (expect noise with the signal).
- AEO/GEO niche subs + vendor Discords (Profound, Ahrefs)
  Newer AEO discussion is fragmented. Treat as trend-radar, NOT authority — validate every claim against the Google primary docs above.

> Community preference: not yet stated. Propose joining r/TechSEO once the user is doing hands-on technical work.

## Gaps

- **No first-party AEO measurement API.** No public API from OpenAI, Anthropic, Perplexity, or Google to query "how often / where is my brand cited in AI answers." Google's June 2026 gen-AI performance reports are a Search Console *UI report, not (yet) in the API*. **Biggest tooling gap — and directly on the build mission.** A self-built tracker must scrape the UI or wait.
- **AEO trackers rely on proxy methods, not ground truth.** Every commercial tool (Profound, Ahrefs Brand Radar, Peec, Otterly) runs a prompt library against the engines and parses responses — synthetic sampling, not the engines' real query distribution. No audited "AI share of voice" standard exists; cross-tool numbers aren't comparable. Building your own = reinventing the same proxy.
- **AEO/GEO writing is overwhelmingly vendor content marketing.** Outside the one GEO paper and Google's docs, almost all 2024–2026 "AEO guide" material is vendor-incentivized. The paper + Google primary docs are the only fully neutral anchors.
- **No stable spec for AI-crawler controls.** `llms.txt` and AI-specific markup proposals exist but aren't standardized and are called unnecessary by Google. No settled, engine-backed equivalent to robots.txt/sitemaps for governing generative-AI inclusion.
