import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// One home per lesson (ADR 0002): the MDX body is pure teaching prose; everything
// structured — metadata, the quiz answer key + feedback, the primary source, and
// footnotes — lives here in typed frontmatter. The layout renders them and computes
// the Next-lesson pager from collection order, so nothing is hand-typed twice.
// Lessons are organised by locale: `src/content/lessons/<lang>/NNNN-*.mdx`
// (ADR 0003). The glob recurses, so an entry id is `en/0001-…` / `zh/0001-…`;
// the locale-aware helpers in src/data/lessons.ts split the lang off the id.
const lessons = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: 'src/content/lessons' }),
  schema: z.object({
    num: z.string(), // '0001'
    title: z.string(),
    kicker: z.string(), // e.g. 'Lesson 0001 · Foundations'
    sub: z.string(), // the italic subtitle
    blurb: z.string(), // index-card blurb + meta description
    quizHeading: z.string().optional(), // lesson-specific quiz title
    quiz: z.array(
      z.object({
        q: z.string(),
        options: z.array(z.string()),
        correct: z.number().int(), // index into options
        ok: z.string(), // feedback when right
        no: z.string(), // feedback when wrong
      }),
    ),
    primarySource: z.object({
      url: z.string().url(),
      label: z.string(),
      minutes: z.number().int().optional(),
      note: z.string(),
    }),
    footnotes: z.array(z.string()).default([]),
  }),
});

export const collections = { lessons };
