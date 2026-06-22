// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// Dogfooding Lesson 0007: the SEO course ships a sitemap.xml covering EVERY URL.
// Every page — lessons (MDX collection), the glossary, and the hub pages — is now
// a real Astro page, so @astrojs/sitemap discovers them all; no customPages hack
// (ADR 0002). Change `site` to your real production origin before deploying.
const SITE = 'https://learn-seo.sunfmin.com';

export default defineConfig({
  site: SITE,
  // Bilingual (ADR 0003): English is the default locale at `/`; Chinese lives
  // under `/zh/`. prefixDefaultLocale:false keeps the English URLs unprefixed.
  i18n: {
    locales: ['en', 'zh'],
    defaultLocale: 'en',
    routing: { prefixDefaultLocale: false },
  },
  integrations: [
    mdx(),
    sitemap({
      // Dogfooding hreflang: the sitemap groups each page with its other-language
      // twin and emits <xhtml:link rel="alternate" hreflang> — the same hreflang
      // the pages carry in <head>. A course that teaches i18n shouldn't ship a
      // sitemap that hides its translations.
      i18n: {
        defaultLocale: 'en',
        locales: { en: 'en', zh: 'zh-CN' },
      },
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
