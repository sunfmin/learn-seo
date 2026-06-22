---
title: 资料 — 面向开发者的 SEO / AEO
description: 课程引用的每一个一手来源：Google Search Central 文档、sitemaps.org 规范、IndexNow 协议、GEO 论文，以及那些尚无定论的空白。
---

# 面向开发者的 SEO / AEO — 资料

所有 URL 截至 2026-06-17 均验证可访问。课程的知识取自这里，而非记忆。

## 知识（Knowledge）

### 官方 / 一手文档（从这里开始）

- [SEO Starter Guide: The Basics — Google Search Central](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
  Google 自家关于 crawling、indexing 以及“到底什么真正影响排名”的入门文档。在任何带观点的博客之前，这是当之无愧的“第一读物”。
- [In-depth guide to how Google Search works — Google Search Central](https://developers.google.com/search/docs/fundamentals/how-search-works)
  来自引擎本身的 crawl → index → serve 管线。用于：第 0001 课（两条管线），以及任何关于经典管线机制的内容。
- [SEO for developers (Get started) — Google Search Central](https://developers.google.com/search/docs/fundamentals/get-started-developers)
  从开发者视角切入：rendering、JS SEO、技术要求。在构建工具（而非写内容）时取用。
- [Understand the JavaScript SEO basics — Google Search Central](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
  crawl → render → index 各阶段，以及为什么 rendering 是一个*延迟队列*（“等 Google 资源允许时，一个 headless Chrome 渲染页面并执行 JavaScript”）。用于：第 0006 课（JS 渲染缺口），以及任何关于客户端渲染、SSR/SSG、或为什么不跑 JS 的 crawler 会漏内容的话题。
- [Introduction to structured data markup — Google Search Central](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
  JSON-LD/Microdata/RDFa 如何驱动 rich result。在自动生成任何 schema 之前先读。
- [Getting Started — schema.org](https://schema.org/docs/gs.html)
  权威的词汇规范（类型、属性、格式）。你的 structured-data 工具应当对照它来校验，它就是真相之源。
- [About the Search Console API + API Reference — Google](https://developers.google.com/webmaster-tools/about) （[参考](https://developers.google.com/webmaster-tools/v1/api_reference_index)）
  Search Analytics、Sitemaps、Sites、URL Inspection 的 REST API。是你构建的任何 SEO 监控/自动化的主干。“Web”搜索类型现已包含 AI 功能带来的流量。
- [Search Quality Rater Guidelines (PDF) — Google](https://services.google.com/fh/files/misc/hsw-sqrg.pdf)
  Google 完整的评估员手册，定义了 E-E-A-T 和“质量”。用来在政策层面理解 *Google 认为什么是好内容*。它是一套评估员框架，**而非**算法分数。
- [Creating Helpful, Reliable, People-First Content — Google Search Central](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
  Google 关于页面内 E-E-A-T 的说明：定义、“trust 最重要”，以及那条关键澄清——“虽然 E-E-A-T 本身不是某个具体的排名因子，但用一组能识别出具有良好 E-E-A-T 内容的混合因子是有用的。”用于：第 0008 课（E-E-A-T），以及任何有厂商兜售“E-E-A-T 分数”的时候。
- [IndexNow — getting started (Bing)](https://www.bing.com/indexnow/getstarted) · [协议文档](https://www.indexnow.org/documentation)
  一个开放协议，用于把 URL 改动即时推送给 Bing/Yandex/Naver/Seznam。`POST {host, key, keyLocation, urlList}`（每次 ≤10,000 个 URL）；这次 ping 会在所有参与方之间共享。**Google 不参与**（2026 年 6 月已验证）——它坚持用 sitemap + 自己的抓取调度，Indexing API 仅限 JobPosting/直播。在为发布管线加入“抓取通知”这一步时取用。
- [The Sitemap protocol — sitemaps.org](https://www.sitemaps.org/protocol.html) · [Build and submit a sitemap — Google](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
  权威的 sitemap 规范：每个文件 ≤50,000 个 URL 且 ≤50 MB，`<loc>` 必填，`<lastmod>` 可选（W3C 日期），所有 URL 同一 host；超过 5 万就用 sitemap index。Google 的文档讲格式 + 提交。用于：第 0007 课（sitemap + IndexNow），在发布管线里生成/校验 sitemap。

### 公认权威（基于证据）

- [Beginner's Guide to SEO — Ahrefs](https://ahrefs.com/seo)
  干净的 10 章入门，如今还加了 AI 搜索的章节。从零到入门，最好的免费结构化课程。
- [The Beginner's Guide to SEO — Moz](https://moz.com/beginners-guide-to-seo)
  由来已久、厂商中立的概念基础。和 Ahrefs 搭配，给基础知识第二种讲法。

### AI Overviews / AEO / GEO

- [AI features and your website — Google Search Central](https://developers.google.com/search/docs/appearance/ai-features)
  Google 公开表态：AI Overviews / AI Mode 如何挑选内容，以及如何控制是否被纳入（`nosnippet`、`noindex`）。这是戳破大多数 AEO 神话的一手来源。
- [Optimizing your website for generative AI features on Google Search — Google Search Central](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
  Google 明确的“AEO/GEO 仍然就是 SEO”指引（2026 年 5 月）。每当有厂商声称你需要 `llms.txt` 或特殊 AI 标记时取用。（[公告](https://developers.google.com/search/blog/2026/05/a-new-resource-for-optimizing)）
- [Introducing Search Generative AI performance reports in Search Console — Google (June 2026)](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
  最新的一手来源：Google *自己*报告你的内容在 AI 体验中的表现。这是最接近第一方 AEO 测量数据源的东西（UI 报告——关于 API 见“空白”一节）。
- [GEO: Generative Engine Optimization — Aggarwal, Murahari, Rajpurohit, Kalyan, Narasimhan, Deshpande (arXiv:2311.09735, KDD 2024)](https://arxiv.org/abs/2311.09735)
  *那篇*权威学术论文。提出了“GEO”，引入了 GEO-bench，测量了各种手法（可见度最高提升约 40%）。它是营销博客噪声之下那条严谨的基线。（[ACM 出处](https://dl.acm.org/doi/10.1145/3637528.3671900)）
- [7 Steps for Tracking Your ChatGPT Visibility With Ahrefs — Louise Linehan (Ahrefs)](https://ahrefs.com/blog/chatgpt-visibility-tracking/)
  一篇具体、对开发者友好的实操：AI share of voice、citation 分析、fan-out query。在设计自己的 AEO 追踪器该算哪些指标时取用。

## 智慧（社区）

- [r/TechSEO](https://www.reddit.com/r/TechSEO/)（约 4.1 万）
  技术/工程一侧：rendering、日志分析、响应头、indexing、API 怪癖。最适合在调试工具的开发者。
- [r/bigseo](https://www.reddit.com/r/bigseo/)（约 12.7 万）
  信号更高的从业者讨论，连接技术与策略。过了入门阶段就来这里问。
- [r/SEO](https://www.reddit.com/r/SEO/)
  最大的 SEO 公共广场。适合追踪算法更新和快速核对（信号里夹着噪声，要有预期）。
- AEO/GEO 小众子版块 + 厂商 Discord（Profound、Ahrefs）
  较新的 AEO 讨论很分散。当作趋势雷达，**而非**权威——每条说法都拿上面 Google 的一手文档去验证。

> 社区偏好：尚未表态。等用户开始做动手的技术工作时，再建议加入 r/TechSEO。

## 空白（Gaps）

- **没有第一方的 AEO 测量 API。** OpenAI、Anthropic、Perplexity 或 Google 都没有公开 API 让你查询“我的品牌在 AI 答案里被引用得多频繁 / 在哪里”。Google 2026 年 6 月的 gen-AI 表现报告是 Search Console 的 *UI 报告，（暂）不在 API 里*。**这是最大的工具空白——也正好落在‘动手构建’这个使命上。** 自建的追踪器只能爬 UI 或等待。
- **AEO 追踪器依赖 proxy 方法，而非 ground truth。** 每个商业工具（Profound、Ahrefs Brand Radar、Peec、Otterly）都是拿一个 prompt 库去跑引擎并解析回复——这是合成抽样，不是引擎真实的 query 分布。不存在经审计的“AI share of voice”标准；不同工具的数字没法比。自己搭 = 重新发明同一个 proxy。
- **AEO/GEO 的文字内容绝大多数是厂商的内容营销。** 除了那篇 GEO 论文和 Google 的文档，2024–2026 年几乎所有“AEO 指南”材料都带厂商利益。那篇论文 + Google 一手文档是仅有的完全中立的锚点。
- **没有针对 AI 爬虫控制的稳定规范。** `llms.txt` 和 AI 专用标记的提案存在，但未标准化，且被 Google 称为不必要。对于治理生成式 AI 的纳入，目前没有像 robots.txt/sitemap 那样有引擎背书、已成定论的对应物。
