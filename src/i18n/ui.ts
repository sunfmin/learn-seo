// The one home for every UI string the site chrome needs in both languages
// (single source of truth — see CONTEXT.md). Page-specific prose lives inline in
// the shared page components; reusable chrome — nav, footer, the lesson tail, the
// quiz engine — reads from here, keyed by `lang`.
//
// Language model (ADR 0003): English is the default locale and lives at `/`;
// Chinese lives under `/zh/`. Every page links its counterpart with hreflang.
// Simplified Chinese prose keeps SEO/AEO jargon (crawl, index, canonical,
// JSON-LD, citation…) in English, glossing it in Chinese on first use.

export const languages = { en: 'English', zh: '中文' } as const;
export type Lang = keyof typeof languages;
export const defaultLang: Lang = 'en';
/** BCP-47 codes for <html lang> and hreflang. */
export const htmlLang: Record<Lang, string> = { en: 'en', zh: 'zh-CN' };

export const ui = {
  en: {
    'brand.tag': 'for builders',
    'nav.home': 'Home',
    'nav.lessons': 'Lessons',
    'nav.glossary': 'Glossary',
    'nav.resources': 'Resources',
    'nav.tools': 'Tools',
    'lang.switch': '中文', // label on the toggle that switches TO the other language
    'footer.html':
      'A hands-on SEO / AEO course for developers — and itself a server-rendered, ' +
      'sitemap-emitting Astro site (dogfooding ' +
      '<a href="/lessons/0006-the-js-rendering-gap.html">0006</a> &amp; ' +
      '<a href="/lessons/0007-sitemaps-and-indexnow.html">0007</a>). ' +
      'Knowledge grounded in <a href="/resources/">primary sources</a>.',
    // Lesson tail (LessonLayout)
    'lesson.kicker.prefix': 'Lesson',
    'lesson.primary.title': 'Primary source — read this next',
    'lesson.primary.min': 'min',
    'lesson.ask.html':
      '<b>Stuck or curious?</b> This agent is your teacher. Ask it anything — “show ' +
      'me a real robots.txt”, “do Claude and Perplexity retrieve differently?” — ' +
      'followups are the fastest way to learn.',
    'lesson.nav.all': '← All lessons',
    'lesson.nav.next': 'Next:',
    'lesson.footer.tail': 'SEO/AEO for builders.',
    // Quiz engine
    'quiz.kicker': 'Retrieval practice · no peeking',
    'quiz.heading': 'Check what stuck',
    'quiz.intro':
      'Answer from memory — that effort is what makes it stick. One try each; pick ' +
      'before you read the others.',
    'quiz.question': 'Question',
    'quiz.of': '/',
    'quiz.score': 'Score:',
    'quiz.perfect': 'perfect — on to the next lesson.',
    'quiz.review':
      'review the section above, then ask your teacher about any miss.',
  },
  zh: {
    'brand.tag': '给开发者',
    'nav.home': '首页',
    'nav.lessons': '课程',
    'nav.glossary': '术语表',
    'nav.resources': '资料',
    'nav.tools': '工具',
    'lang.switch': 'English',
    'footer.html':
      '一门面向开发者、动手实践的 SEO / AEO 课程——本站本身就是一个服务端渲染（SSR）、' +
      '在构建时生成 sitemap 的 Astro 站点（实战演示 ' +
      '<a href="/zh/lessons/0006-the-js-rendering-gap.html">0006</a> 与 ' +
      '<a href="/zh/lessons/0007-sitemaps-and-indexnow.html">0007</a>）。' +
      '每条结论都基于<a href="/zh/resources/">一手来源（primary source）</a>。',
    'lesson.kicker.prefix': '第',
    'lesson.primary.title': '一手来源 — 接下来读这个',
    'lesson.primary.min': '分钟',
    'lesson.ask.html':
      '<b>卡住了，或者好奇？</b> 这个 agent 就是你的老师。尽管问——“给我看一个真实的 ' +
      'robots.txt”、“Claude 和 Perplexity 的 retrieve 方式不一样吗？”——' +
      '追问是学得最快的方式。',
    'lesson.nav.all': '← 所有课程',
    'lesson.nav.next': '下一课：',
    'lesson.footer.tail': 'SEO/AEO for builders（给开发者的 SEO/AEO）。',
    'quiz.kicker': '提取练习 · 不许偷看',
    'quiz.heading': '检验掌握程度',
    'quiz.intro':
      '凭记忆作答——正是这份努力让知识留得住。每题只有一次机会；在看其他选项前先选。',
    'quiz.question': '第',
    'quiz.of': '/',
    'quiz.score': '得分：',
    'quiz.perfect': '满分——进入下一课吧。',
    'quiz.review': '回顾上面那一节，然后就任何错题问你的老师。',
  },
} as const;

export type UIKey = keyof (typeof ui)['en'];

/** Translator bound to a language, falling back to the default locale. */
export function useTranslations(lang: Lang) {
  return function t(key: UIKey): string {
    return ui[lang][key] ?? ui[defaultLang][key];
  };
}

/** The locale of a request path: `/zh/...` → 'zh', everything else → 'en'. */
export function getLangFromUrl(url: URL): Lang {
  return url.pathname === '/zh' || url.pathname.startsWith('/zh/') ? 'zh' : 'en';
}

/** Strip the locale prefix, returning the canonical (English-form) path. */
export function unlocalizePath(pathname: string): string {
  if (pathname === '/zh') return '/';
  if (pathname.startsWith('/zh/')) return pathname.slice(3);
  return pathname;
}

/** Re-apply a locale prefix to a canonical (unprefixed) path. */
export function localizePath(path: string, lang: Lang): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  if (lang === 'en') return clean;
  return clean === '/' ? '/zh/' : `/zh${clean}`;
}

/** The same page in the other language — used by the nav toggle. */
export function alternatePath(pathname: string, target: Lang): string {
  return localizePath(unlocalizePath(pathname), target);
}
