# SEO / AEO for builders

A hands-on, developer-first course on the two pipelines that decide who finds your
content — **classic search** (crawl → index → rank) and **AI answer engines**
(retrieve → generate → cite) — published as an [Astro](https://astro.build) site.

Every lesson ends in a runnable, stdlib-only Python tool. The site practices what
the course preaches: server-rendered (Lesson 0006), sitemap-emitting (0007), with
canonical / Open Graph / JSON-LD on every hub page (0003, 0008).

## Run it

```bash
pnpm install
pnpm dev        # local dev server (auto-syncs lesson pages first)
pnpm build      # static build to dist/ (+ sitemap.xml)
pnpm preview    # serve the built site
```

Set your real origin in `astro.config.mjs` (`site`) before deploying — canonical
URLs and the sitemap derive from it.

## Layout

| Path | What |
|------|------|
| `src/pages/` | Astro hub pages: home, lessons index, `tools/`, `resources/` |
| `src/layouts/`, `src/styles/` | shared layout + the design system the lessons use |
| `src/data/lessons.ts` | single source of truth for lesson metadata |
| `lessons/*.html` | the authored lesson pages (self-contained: scoped CSS + quiz) |
| `reference/glossary.html` | the glossary |
| `RESOURCES.md` | every primary source the lessons cite — rendered at `/resources/` |
| `MISSION.md` | why this course exists |
| `tools/*.py` | one audit/automation script per lesson (each has `--demo`) |
| `scripts/sync-lessons.mjs` | prebuild step: copies lessons → `public/`, rewrites links |

`public/lessons/` and `public/reference/` are **generated** by the sync step
(gitignored). Edit the originals in `lessons/` and `reference/`, never the copies.

## The tools

```bash
python3 tools/crawl_audit.py    --demo   # 0002 crawlable + indexable
python3 tools/schema_tool.py    --demo   # 0003 JSON-LD linter
python3 tools/geo_lint.py       --demo   # 0004 writing-for-retrieval linter
python3 tools/citation_share.py --demo   # 0005 AI-citation share of voice
python3 tools/build_prompts.py  --demo   # 0005 prompt-library builder
python3 tools/render_gap.py     --demo   # 0006 raw-vs-rendered DOM diff
python3 tools/sitemap_ping.py   --demo   # 0007 sitemap + IndexNow
python3 tools/eeat_audit.py     --demo   # 0008 E-E-A-T proxy-signal audit
```
