---
name: daily-ai-digest
description: "Produce a branded daily AI news digest/magazine from multiple collection sources. Covers multi-source pipeline design, content ranking/curation (notícia vs discussão), editorial rules (zero anglicisms), brand-consistent HTML→PDF rendering, history-based dedup, and companion delivery formats (WhatsApp summary)."
version: 1.1.0
---

# Daily AI Digest Production

Produce a branded daily AI news digest (e.g. "IAF — Manhã Aumentada") using a multi-source collection pipeline, content ranking, and editorial formatting. This skill covers the end-to-end workflow from raw data collection through polished PDF delivery.

## Pipeline Architecture

### Collection Phase (5 parallel sources)

Run as separate cron jobs or delegate_task calls, staggered to avoid resource contention:

| # | Source | Method | Recommended Time |
|---|--------|--------|-----------------|
| 1 | **General AI news** | `web_search("AI news today")` + `web_extract` top articles | 04:00 |
| 2 | **Hacker News** | `web_extract` front page + `/newest` | 04:15 |
| 3 | **Reddit (10+ subs)** | RSS feeds via `reddit_rss_parser.py` (see `read-reddit` skill) | 04:30 |
| 4 | **X + discussions** | `web_search` with broad AI application terms (no `site:` filter) | 04:45 |
| 5 | **Specialized newsletters** | `web_extract` on therundown.ai, superhuman.ai + latest articles | 07:30 |

Each collector saves a markdown file. **Every entry MUST include a clickable source URL** — enforce this in the delegation context.

### Synthesis Phase (07:50 → 08:00 deliver)

Reads all 5 collector files + last 14 days of history, then:

1. **Pré-selecionar** — scan all items, pick only the 10–15 most newsletter-worthy (relevance, novelty, discussion potential, applicability). Do NOT rank everything.
2. **Rank** each pré-selected item on 3 criteria (see `references/ranking-criteria.md`)
3. **Classify** each as `notícia` or `discussão`
4. **Build a ranking table** (title, category, tipo, scores, average — sorted desc) and **include it in the final response** so the user can see it
5. **Distribute** by type and rank into sections (top 3 scores = Deep Dive regardless of tipo)
6. **Write** the editorial (Hot Take) with an opinionated, professional voice
7. **Render** HTML with brand identity → convert to PDF (primary: Chromium headless; fallback: weasyprint)
8. **Write** a companion WhatsApp summary (markdown with WhatsApp notation — see Companion WhatsApp Summary section below)
9. **Save** the HTML to `/opt/data/cron/history/iaf_YYYY-MM-DD.html`
10. **Deliver** PDF via MEDIA: protocol + ranking table + WhatsApp message

## Digest Structure (IAF Template)

### Sections in order

1. **Editorial / Hot Take** — Opinionated 1-2 paragraph take on the day's biggest topic. Voice: professional but personal, like Ben Thompson's Stratechery. Must provoke emotion and opinion, not just report facts.

2. **Análise / Deep Dive** — Top 3 items from the ranking by total score (any combination of notícia and discussão). Each gets 3-5 paragraphs with analysis, context, and a link. **Deep Dive and expanded news are the same thing** — don't treat them differently.

3. **Radar de Notícias** — Remaining `notícia` items in compact format (1-2 lines each, with link). No expandidas — those went to Deep Dive.

4. **Pulso da Comunidade** — Remaining `discussão` items. First 2 highest-scored get expanded format (like Deep Dive cards). Rest get compact format with link. **Do not repeat** any discussion that was already used in a Deep Dive.

5. **Aplicação Prática** — 1 single extensive tutorial/recipe item. Last section. Must include "O que você ganha" (benefit box) explaining the value of executing the solution.

### Editorial Rules

- **Zero anglicisms**: Replace "keynote" → "grandes palcos", "ship" → "entregar", "deadline" → "prazo", "brainstorm" → "tempestade de ideias", etc. When a foreign term is unavoidable, explain it clearly and didactically.
- **Every item has a link**: No exception. Every news bullet, community pulse, and deep dive must include a source URL.
- **Voice**: Opinionated but professional. The Hot Take should feel like a newsletter from an expert peer, not a news wire.
- **Line breaks**: Use plenty of paragraph breaks. Dense walls of text lose the reader.

## Brand Identity (IAF)

**IMPORTANT**: The IAF brand identity uses **Light Mode ☀️** colors. The dark mode listed in older versions of this skill is deprecated. Use these colors:

| Token | Value | Use |
|-------|-------|-----|
| Background primary | `#ffffff` | Page background |
| Background secondary | `#f4f7f9` | Cards, blocks |
| Accent primary | `#0a8f88` | Section titles, header, borders |
| Accent hover/neon | `#06b8a0` | Highlights, glow, hot take |
| Accent muted | `rgba(10,143,136,0.08)` | Subtle backgrounds |
| Accent terracotta | `#c75b3e` | Business/analysis tags |
| Accent sage | `#5f7a6b` | Creative/product tags |
| Accent amber | `#b8860b` | Alert/security tags |
| Text primary | `#1a1f24` | Body text |
| Text secondary | `#5a6b72` | Metadata, subtitles |
| Border | `rgba(10, 143, 136, 0.18)` | Card borders, separators |
| Title font | Outfit (900 for main, 700 for sections) |
| Editorial font | Spectral (serif, for long-form text) |
| Body font | Inter (400-500) |
| Code font | Fira Code |

The definitive visual identity is in `iaf-newsletter` skill. This skill provides the editorial pipeline; that skill provides the design system. When generating visual output, load `iaf-newsletter` for the latest design rules.

### Font sizing for PDF output

When rendering to PDF via Chromium headless, **font sizes that look correct at browser width (~800px) appear undersized at A4 (210mm)**. Use these minimum sizes:

| Element | Minimum | Font |
|---------|---------|------|
| Editorial body (long-form) | 15.5px | Spectral |
| Card body text | 13.5px | Inter |
| Table text | 10px | Fira Code |
| Section titles | 17px | Outfit 700 |
| Footer metadata | 9px | Fira Code |

**Line-height**: 1.75 for Spectral editorial, 1.65 for Inter body text.

### Source attribution requirement

Every informational card and data claim must include a `.sources-block` with clickable links:
```html
<div class="sources-block">
  <strong>Fontes:</strong> <a href="URL">Publication — Title</a>
</div>
```

## History-Based Dedup

Before the final synthesis, read all HTML files from `/opt/data/cron/history/` within the last 14 days. Extract the major story headlines and URLs from each. During ranking, flag any item whose topic overlaps with a story from the last 14 days and deprioritize or exclude it.

## PDF Rendering

### Primary: Chromium Headless (UPDATED 2026-06-09)

**Critical rules for PDF output:**

| Rule | Value | Why |
|------|-------|-----|
| `@page` | `size: 210mm 297mm; margin: 0;` | Explicit mm, not "A4" |
| `body bg` | `#ffffff; margin: 0; padding: 0;` | Prevents gray borders |
| `.page` width | `width: 100%` | Let @page handle A4 sizing |
| Page breaks | `page-break-before: always` on `.page` | More reliable than `after` |
| `page-break-inside: avoid` | cards, callouts, pullquotes, stats, timeline | Prevents awkward splits |
| Footers | **Remove all** between sections | Break visual flow |

**Command:**
```bash
CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium \
  $CHROMIUM --headless --no-sandbox --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="/tmp/output.pdf" "file:///tmp/input.html"
```

**Minimum font sizes for PDF readability:**
| Element | Minimum |
|---------|---------|
| Editorial body | 15.5px |
| Card body | 13.5px |
| Tables (Fira Code) | 10px |
| Section titles | 17px |
| Pull quotes | 20px |
| Stat numbers | 32px |

### Mobile HTML (separate file for browser viewing)

When deploying HTML for direct browser viewing (GitHub Pages):
- `body { background: #e8edf0 }` (original IAF background)
- `.page { width: 100%; max-width: 800px; margin: 0 auto }`
- Kill all page-breaks with `!important`
- Fonts 15-20% larger than PDF
- Include responsive breakpoints at 600px and 768px
- Remove footers (same as PDF)

### Gray space around PDF page

**Symptom:** Gray/colored borders visible on right and bottom of PDF pages.

**Fix:** `html, body { margin: 0; padding: 0; background-color: #ffffff; }` in PDF HTML. Chromium includes body background in PDF output. Any non-white body background creates visible borders even with `@page { margin: 0 }`.

### Source attribution

Every informational card MUST have a `.sources-block` with clickable links:
```html
<div class="sources-block">
  <strong>Fontes:</strong> <a href="URL">Publication — Title</a>
</div>
```

### Fallback: WeasyPrint

Use when Chromium binary is unavailable. Note: `-webkit-background-clip: text` is NOT supported — gradient titles render as solid `#0da69e`.

- Use `@page { size: A4; margin: 1.5cm 1.8cm; }` for proper print layout
- Add `page-break-inside: avoid` to deep-dive cards and the hot-take box
- Avoid `-webkit-background-clip: text` — weasyprint doesn't support it. Use solid colors or standard CSS gradients instead
- Fonts: preload via `<link href="https://fonts.googleapis.com/...">` — weasyprint downloads them at render time

## Correction Principle

When the user requests a correction to the digest output, **change ONLY what was explicitly requested**. Do not reformat, reword, or reorder sections that weren't flagged. If a secondary issue is worth noting, raise it separately after delivering the correction.

## Companion WhatsApp Summary

After sending the PDF, also deliver a WhatsApp-format companion message inside a markdown code block so formatting survives copy-paste. The user copies this from Telegram into WhatsApp groups.

**Format Rules:**
- 📰 emoji before the newsletter name header
- 🔥 emoji before `*Destaques do dia*`
- 🎯 emoji before `*Aplicação prática de hoje:*`
- First sentence of the editorial in **bold**
- The 3 bullets = **top 3 scores from the ranking** (any tipo — notícia or discussão, whichever scored highest). Ranking determines selection, NOT section assignment.
- Keep it tight: 2-3 phone screens on WhatsApp max

**Exact template:**
```text
📰 *IAF — Manhã Aumentada* · DD/MM/AAAA

*[PRIMEIRA FRASE DO EDITORIAL EM NEGRITO]* Restante do editorial continua aqui. 1-2 parágrafos opinionados.

🔥 *Destaques do dia*
• [Top 1 do ranking — bullet curto e impactante + contexto]
• [Top 2 do ranking — bullet curto e impactante + contexto]
• [Top 3 do ranking — bullet curto e impactante + contexto]

🎯 *Aplicação prática de hoje:* [1 linha — do briefing ao post pronto, sem repetir comando.]
```

**Ranking rule** (learned from user correction): The 3 bullets under "Destaques do dia" are the **top 3 scores in the ranking** regardless of tipo (notícia or discussão). If a discussão scores higher than a notícia, the discussão takes the slot. The editorial's opening topic should be the single item with the highest overall narrative/emotional impact — not necessarily the top score, but the most compelling story.

**Pre-selection before ranking** (learned from user correction): Do NOT rank all collected items. First scan everything, select only the 10-15 most newsletter-worthy candidates, then rank ONLY those. This avoids token waste and focuses quality on the candidates most likely to appear.

## Delivery

- **PDF sent via MEDIA: protocol** — the cron's final response MUST include the literal text `MEDIA:/tmp/iaf-v3-verdadeiro.pdf` (or equivalent path) at the top of the response. Without this, the Telegram gateway won't attach the file. `deliver: origin` sends the response text but does NOT auto-attach files — only the `MEDIA:` marker triggers file delivery.
- **HTML** saved to history directory as reference
- **Ranking table** included in the response as markdown so the user can see the scores
- **WhatsApp companion** sent as inline code block (```text) for copy-paste preservation
- **GitHub Pages** — for shareable links, deploy HTML via `gh repo create` + GitHub Pages API (see `iaf-newsletter` skill for the exact commands)

## Edições Extraordinárias (Single-Topic)

When the user requests a special edition focused on one topic, abandon the multi-section ranking format. See the `iaf-newsletter` skill for the full special edition workflow: cover page, long-form editorial in Spectral, multi-page feats catalog with source blocks, timeline, and mobile-responsive CSS. The reference template is at `iaf-newsletter/references/iaf-especial-template.html`.
