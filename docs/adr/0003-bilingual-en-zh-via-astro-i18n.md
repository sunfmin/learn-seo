# ADR 0003 — Bilingual (English + 简体中文) via Astro i18n

- Status: accepted (extends ADR 0002)
- Date: 2026-06-22

## Context

The course shipped English-only. The brief: make the **whole site** bilingual —
English and Simplified Chinese — with every piece of content translated, not just
the chrome.

Two structural options:

1. **Inline both languages** on one set of pages (English then Chinese, stacked).
   Simplest routing, no duplication — but a mixed-language page is not SEO-correct,
   and this is a course that teaches SEO. It would dogfood the wrong thing.
2. **Switchable locales** — one URL per language, linked by `hreflang`. More files,
   but each page is monolingual and the implementation *is* the textbook i18n setup
   the course should model.

## Decision

Use **Astro's built-in i18n** with `prefixDefaultLocale: false`: English (the default
locale) stays at `/…`, Chinese lives under `/zh/…`. The two trees are linked with
`rel="alternate" hreflang"` (en / zh-CN / x-default) in every `<head>`, and the
`@astrojs/sitemap` `i18n` option emits the same `hreflang` pairs in `sitemap-0.xml`.
A nav toggle (`中文` ⇄ `English`) links each page to its counterpart, computed by
swapping the locale prefix.

**One home per fact, per language** (the single-source principle, extended across the
language axis):

- **UI chrome** — nav, footer, the lesson tail, the quiz engine — reads from one
  dictionary, `src/i18n/ui.ts`, keyed by `lang`. No chrome string is hand-typed twice.
- **Lessons** — the content collection is organised by locale:
  `src/content/lessons/<lang>/NNNN-*.mdx`. The glob recurses, so an entry id is
  `en/0001-…` / `zh/0001-…`; locale-aware helpers in `src/data/lessons.ts`
  (`lessonsFor`, `slugFor`, `langOf`) split the lang off the id and the lesson routes
  filter by it. URLs stay `/lessons/NNNN-*.html` (en) and `/zh/lessons/NNNN-*.html`.
- **Glossary** — term data moves to `src/i18n/glossary.ts`, each term carrying both
  languages (`t`/`d` as `{ en, zh }`); one component renders the active locale.
- **Tools** — the `tools` catalogue keeps one record per tool; `desc` becomes
  `{ en, zh }`. The lesson↔tool mapping is unchanged.
- **Resources** — `RESOURCES.md` (en) + `RESOURCES.zh.md` (zh), each rendered directly
  (no copy). Source-document **titles stay English** (they are real English docs, as on
  the resources page); the surrounding annotations are translated.

**Page shape** — to avoid cloning page logic per locale, each hub page is a shared
component taking a `lang` prop (`src/components/pages/Home.astro`, `LessonsIndex`,
`ToolsIndex`, `GlossaryPage`); the route files (`src/pages/…` and `src/pages/zh/…`) are
thin wrappers that pass `lang`. Page-specific prose lives inline in those components as
`lang === 'zh' ? … : …` — colocated with its markup; only reusable chrome is in the
dictionary.

**Translation style** — Simplified Chinese prose **keeps SEO/AEO jargon in English**
(crawl, index, canonical, JSON-LD, citation, render gap…), glossed in Chinese on first
use. That matches how Chinese developers read these terms, and keeps the headwords
stable across the glossary, lessons, and tools. **Simulated CLI output** (`Runbox`,
`Scoreboard` props) and **pipeline stage names** (`Crawl`, `Index`, `Rank`…) stay
English — the real tools print English, and the stage names are the canonical model.

## Consequences

- Every page exists in two languages with correct `hreflang`; the sitemap advertises
  the pairs. The course now dogfoods i18n the way it dogfoods SSR, sitemaps, and
  structured data.
- Adding a lesson means two MDX files (`en/` + `zh/`); a new UI string means one entry
  with both languages in `ui.ts`. The build fails loudly if a `zh` lesson is missing
  its `en` twin only in that the pager/links would 404 — keep the two trees in step.
- Lesson MDX component imports moved one directory deeper (`../../../components/…`)
  when the files moved into `en/`.
- `og:locale` and JSON-LD `inLanguage` are set per locale; meta titles/descriptions are
  translated, not just the body.
