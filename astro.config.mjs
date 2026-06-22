// @ts-check
import { existsSync, readdirSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import { lessons } from './src/data/lessons.ts';

// Dogfooding Lesson 0007: the SEO course ships a sitemap.xml covering EVERY URL.
// Change `site` to your real production origin before deploying; canonical +
// sitemap URLs derive from it.
const SITE = 'https://learn-seo.example';

// Lessons mid-migration (ADR 0002): a lesson is EITHER an MDX collection entry
// (a real Astro page, auto-discovered by @astrojs/sitemap) OR a self-contained
// file still synced into public/ (invisible to Astro, so hand-listed below).
// The collection route carries `.html` in its slug param so it keeps the existing
// `/lessons/<slug>.html` URLs without flipping the hub pages to file format.
const migratedSlugs = new Set(
  existsSync('src/content/lessons')
    ? readdirSync('src/content/lessons')
        .filter((f) => f.endsWith('.mdx'))
        .map((f) => f.replace(/\.mdx$/, '.html'))
    : [],
);

export default defineConfig({
  site: SITE,
  integrations: [
    mdx(),
    sitemap({
      // Directory format gives a migrated lesson page the URL `/lessons/<x>.html/`
      // (trailing slash); the served file, every internal link, and the canonical
      // all use `/lessons/<x>.html`. Normalise so the sitemap agrees — a course
      // that teaches canonicals shouldn't ship a sitemap that disagrees with them.
      serialize(item) {
        item.url = item.url.replace(/\.html\/$/, '.html');
        return item;
      },
      customPages: [
        ...lessons
          .filter((l) => !migratedSlugs.has(l.slug))
          .map((l) => `${SITE}/lessons/${l.slug}`),
        `${SITE}/reference/glossary.html`,
      ],
    }),
  ],
});
