// Shared getStaticPaths body for the lesson detail routes. Both the English
// (`/lessons/[slug].html`) and Chinese (`/zh/lessons/[slug].html`) routes are the
// same logic over a different locale, so the path-building lives here once: the
// route file just picks the lang. The Next pager is derived from collection order.
import { lessonsFor, slugFor } from './lessons';
import type { Lang } from '../i18n/ui';

export async function lessonPaths(lang: Lang) {
  const ordered = await lessonsFor(lang);
  return ordered.map((entry, i) => {
    const nextEntry = i + 1 < ordered.length ? ordered[i + 1] : null;
    return {
      // `.html` is in the route filename, so `slug` is the locale-free id.
      params: { slug: entry.id.replace(/^(en|zh)\//, '') },
      props: {
        entry,
        next: nextEntry
          ? { slug: slugFor(nextEntry), title: nextEntry.data.title }
          : null,
      },
    };
  });
}
