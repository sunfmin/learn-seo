// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { lessons } from './src/data/lessons.ts';

// Dogfooding Lesson 0007: the SEO course ships a sitemap.xml covering EVERY
// URL — including the self-contained lesson pages served from public/, which
// @astrojs/sitemap can't discover on its own. Change `site` to your real
// production origin before deploying; canonical + sitemap URLs derive from it.
const SITE = 'https://learn-seo.example';

export default defineConfig({
  site: SITE,
  integrations: [
    sitemap({
      customPages: [
        ...lessons.map((l) => `${SITE}/lessons/${l.slug}`),
        `${SITE}/reference/glossary.html`,
      ],
    }),
  ],
});
