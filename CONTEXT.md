# Context — domain & architecture language

Vocabulary for this codebase. Use these terms exactly in code, commits, and issues.

## Domain (SEO / AEO)

See the glossary at `/reference/glossary.html` (authored in
`src/pages/reference/glossary.html.astro`) for the full, lesson-grounded glossary.
The load-bearing terms:

- **Classic pipeline** — crawl → index → rank → serve. Measured by the Search Console API (ground truth).
- **Answer-engine pipeline** — retrieve → generate → cite. No first-party measurement API; trackers use proxy sampling.
- **Crawlable / Indexable** — the two gates a page passes before it can rank.
- **Citation** — the AEO win: being the source an answer engine links. The equivalent of a #1 rank.
- **Render gap** — content that exists only in the rendered DOM, invisible to no-JS bots and delayed for Google's deferred render wave.

## Architecture (`tools/seolib/`)

`seolib` is the course **capstone** — the product the lesson tools sketch toward (see ADR 0001).
Stdlib-only. Modules, named as concepts (not "utils"):

- **`domain`** — `domain(url) → host`. Registrable-ish host (netloc, lowercased, `www.` dropped). Carries the no-public-suffix-list caveat in one place.
- **`fetch`** — the network seam. `fetch(url) → Response`. A `urllib` adapter in prod; a fixture adapter in tests. Owns UA, timeout, read-cap, charset.
- **`Page`** — the parse-once HTML module. `parse(html) → Page` exposing `title`, `meta`, `canonical`, `robots`, `links`, `headings`, `words`, and JSON-LD nodes. The one HTML scanner.
- **`ld`** — JSON-LD handling. `extract(html) → nodes` (flattens `@graph`/nesting); pairs with `schema_tool`'s linter so a live page can be validated.
- **`checklist`** — the report renderer. Rows of `(status, label, detail)` → the formatted runbox + verdict every tool prints.

### Test surface

`tools/test_seolib.py` is the package's single test surface — run from the repo root.
Each lesson tool keeps its own `--demo` offline self-check for its lesson-specific logic.

## Architecture (`src/` — the course site)

An Astro site (see ADR 0002). As `seolib` is the capstone the tools converge on, the
lesson **presentation** converges on shared components. Named as concepts:

- **lesson** — an MDX entry in the `lessons` content collection (`src/content/lessons/*.mdx`).
  Its **frontmatter is the single source** for metadata, the quiz (answer key + feedback in
  one array), the primary source, and footnotes; the MDX body is teaching prose only. URLs
  stay `/lessons/NNNN-*.html`.
- **`LessonLayout`** — wraps `BaseLayout` (the site shell). Renders the structured tail from
  frontmatter — quiz, primary-source box, ask box, footnotes — and computes the Next pager
  from collection order. Nothing in the tail is hand-authored per lesson.
- **lesson components** (`src/components/lesson/`) — the shared vocabulary the bodies are
  built from: **`Callout`** (one box, `variant` = win/insight/gotcha/note/do), **`Quiz`**,
  **`Runbox`** (the HTML twin of `seolib.checklist`'s output), **`Pipeline`** (stage-flow
  diagram), **`TwoCol`** (compare cards), **`Scoreboard`**, **`Letters`**, **`Gates`**, **`Pill`**.
- **`global.css`** — the one design system; lesson chrome lives here, component-specific
  styles are Astro-scoped in each component.
