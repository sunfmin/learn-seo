// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// Dogfooding Lesson 0007: the SEO course ships a sitemap.xml covering EVERY URL.
// Every page — lessons (MDX collection), the glossary, and the hub pages — is now
// a real Astro page, so @astrojs/sitemap discovers them all; no customPages hack
// (ADR 0002). Change `site` to your real production origin before deploying.
const SITE = 'https://learn-seo.example';

export default defineConfig({
  site: SITE,
  integrations: [
    mdx(),
    sitemap({
      // Lessons + the glossary are routed at `…/<name>.html`; directory build
      // format gives those pages a trailing slash in the sitemap, while the served
      // file, the internal links, and the canonical all use no slash. Normalise so
      // the sitemap agrees — a course that teaches canonicals shouldn't disagree.
      serialize(item) {
        item.url = item.url.replace(/\.html\/$/, '.html');
        return item;
      },
    }),
  ],
});
