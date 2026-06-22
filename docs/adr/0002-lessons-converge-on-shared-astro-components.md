# ADR 0002 — Lessons converge on shared Astro components

- Status: accepted (extends ADR 0001)
- Date: 2026-06-22

## Context

The eight lessons — and `reference/glossary.html` — were authored as **self-contained
HTML files**: a scoped `<style>` block, an inline quiz `<script>`, hand-written nav and
footer, synced verbatim into `public/` by `scripts/sync-lessons.mjs`.

An architecture review found the same kind of duplication ADR 0001 found in the tools:

- a shared **chrome** (the design-system `:root` vars, `.kicker/.sub/.wrap`, the quiz
  engine, the universal "ask your teacher" box) cloned into all 8 lesson files —
  re-implementing the design system that already lives in `src/styles/global.css`;
- the quiz **answer key split three ways** — a `data-correct` attribute, two JS feedback
  arrays (`fbOk`/`fbNo`), and inline score strings;
- per-lesson **metadata** in `src/data/lessons.ts`, a separate home from the body it
  describes — and a hand-typed "Next: Lesson NNNN…" string in each file that can drift;
- the sitemap forced to hand-list every page via `customPages`, because `public/` files
  are invisible to Astro's page discovery.

## Decision

Migrate the lessons into an **Astro content collection of MDX entries**
(`src/content/lessons/*.mdx`), rendered through a shared **`LessonLayout`** (which wraps
`BaseLayout`, so lessons gain the site shell while keeping the narrow reading column),
plus a small **lesson-component library** named as concepts — `Quiz`, `Callout`
(one component, `variant=win|insight|gotcha|note`), `Runbox`, `TwoCol`, `Recap`.

Structured-but-hand-written content moves into **typed frontmatter** (one home,
schema-checked by Zod in `src/content.config.ts`): metadata, the quiz array
(`q`/`options`/`correct`/`ok`/`no`), the primary source, and footnotes. The layout
renders the quiz, primary-source box, footnotes, and ask box, and **computes** the
Next-lesson pager from collection order. The MDX body is left as pure teaching prose +
diagrams. Code samples render through Astro's built-in **Shiki** (the hand-rolled
`.cm/.k/.s` highlight spans go away), themed to preserve the current look.

The glossary becomes a `BaseLayout` Astro page (`src/pages/reference/glossary.astro`).
With nothing left in `public/lessons/` or `public/reference/`, **`sync-lessons.mjs`, the
`public/` copies, the `predev`/`prebuild` sync hooks, and the sitemap `customPages` hack
are all deleted** — Astro discovers every page. Lesson URLs keep their existing
`/lessons/NNNN-*.html` shape, so no internal link, external bookmark, or canonical
changes.

We accept that lessons are **no longer self-contained HTML files** — the same trade
ADR 0001 made for the tools. ADR 0001 framed it as "the code converges on the library"
while "the lessons keep teaching each mechanism from scratch in prose." This ADR extends
convergence to the lesson **presentation** (chrome + quiz engine); the
teach-each-mechanism-from-scratch **prose** principle is untouched.

## Consequences

- One design system (`global.css` + Astro-scoped component styles); the quiz engine and
  ask box have one home; the quiz answer key is single-sourced.
- Per-lesson metadata is co-located in MDX frontmatter; the `lessons` array in
  `src/data/lessons.ts` dissolves into the collection. The `tools` array and its
  `toolsForLesson`/`slugForLesson` helpers stay (the lessons index + tools page consume
  them) — re-pointed at the collection.
- New site-side dependency `@astrojs/mdx`. The tools' stdlib-only / zero-dependency rule
  is unaffected — it governs `tools/`, not the Astro site.
- Editing a lesson now means editing MDX + shared components, not one file. The
  "open one `.html`" property is gone (judged incidental — no student-download or
  agent-regeneration requirement depends on it).
- The MDX `{` footgun on JSON-LD samples is handled by fenced code blocks (Shiki), not
  raw `<pre>`.
