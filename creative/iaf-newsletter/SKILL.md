---
name: iaf-newsletter
description: "Produce the IAF 'Manhã Aumentada' daily newsletter — a curated AI intelligence report delivered as a styled PDF via Telegram. Covers the full pipeline: multi-source data collection, ranking-based editorial triage, copywriting with zero anglicisms, HTML rendering with IAF visual identity, Chromium headless PDF generation, Telegram delivery, and automatic web deployment. Use when generating any issue of this newsletter or when producing similar daily curated reports."
version: 1.4.0
author: IAF pipeline
---

# IAF — Manhã Aumentada Newsletter Production

## Pipeline Architecture (4 Crons)

The newsletter is produced by 4 scheduled cron jobs:

```
04:00 ── Cron #1: Coleta de Fontes ────────────┐
     Reddit (RSS), HN, Notícias Gerais, Social  │
     Toolsets: terminal, web, file               │
                                                 │
07:30 ── Cron #2: Newsletters ──────────────────┤── context_from ──→
     therundown.ai, superhuman.ai                │                   │
     Toolsets: web, file                          │                   │
                                                 │                   08:00 ── Cron #3: Síntese + PDF
                                                                              Reads all outputs + 14d history
                                                                              Ranks → writes HTML (PDF+responsive CSS)
                                                                              → Chromium → PDF
                                                                              Skills: newsletter-curation, copywriting,
                                                                                      humanizer, html-to-pdf-chromium
                                                                              Toolsets: terminal, file
                                                                              Deliver: origin (Telegram PDF + WhatsApp text)
                                                                                        │
                                                                                        │ context_from (automatic via timing)
                                                                                        ▼
                                                                              08:20 ── Cron #4: Deploy Web
                                                                                Reads the HTML saved by Cron #3
                                                                                Runs _deploy_new_edition.py script:
                                                                                  → adds to _transform.py EDITIONS
                                                                                  → runs transform → responsive HTML
                                                                                  → updates index.html + vercel.json
                                                                                  → vercel build + deploy
                                                                                Sends Telegram message with web link
                                                                                Skills: hermes-agent
                                                                                Toolsets: terminal, file
                                                                                Deliver: origin (Telegram link)
```

### Chaining strategy
- Cron #1 and #2 run independently (different sources, different schedules)
- Cron #3 runs at 08:00 after both collectors are done (Cron #1 at 04:00, Cron #2 at 07:30)
- Cron #4 runs at 08:20, 20 minutes after Cron #3 — enough time for HTML generation + PDF rendering
- No `context_from` between #3 and #4 — Cron #4 uses the file system to detect new editions

### Why 4 crons and not more?
- **Fewer points of failure**: 4 scheduled windows for the full pipeline
- **Natural timing**: newsletters (therundown, superhuman) only update around 07:00 UTC
- **Parallel collection inside Cron #1**: Multiple sources handled in one LLM session
- **Dedicated deploy cron**: Keeps web deployment separate from PDF generation, avoiding timeout issues

### 14-Day Context
Cron #3 scans all HTML files in `/opt/data/cron/history/` to extract titles from the last 14 days. Before writing, it compares candidate items against this list and drops or deprioritizes repeats.

## Data Files
All collectors write to `/opt/data/cron/output/`:
- `iaf_reddit.md` — Reddit RSS (10 subreddits across categories)
- `iaf_hackernews.md` — HN frontpage + newest
- `iaf_noticias_gerais.md` — Web search for general AI news
- `iaf_social.md` — X/forum discussions (web_search broad terms)
- `iaf_especializados.md` — therundown.ai + superhuman.ai newsletters

Each file has date/timestamp at top, and every entry includes **title, short description, and LINK** (mandatory).

## Editorial Workflow
Every item must pass through this process before it reaches the reader:

### Step 0: Pré-seleção (before ranking!)
Do NOT rank all collected items. First scan everything, select only the **10-15 most newsletter-worthy** candidates (relevance, novelty, discussion potential, applicability). Only these pass to the ranking step.

### Step 1: Rank Each Pré-selected Item
Score each news item AND discussion on three criteria (scale 1–10):
| Criterion | What it measures |
|-----------|-----------------|
| **Impacto** | How much does this move the needle for the AI industry/market? |
| **Utilidade** | Can the reader act on this today? Applicability. |
| **Intriga** | Is this novel, surprising, or thought-provoking? |

Also assign a **Tipo** (notícia or discussão) to control section routing. **Average** = (Impacto + Utilidade + Intriga) / 3.

>The ranking table is for **internal production only** — never include scores in the public newsletter. Cron #4 does NOT deliver the ranking — it was removed from the pipeline.

### Step 2: Route Items to Sections
| Section | Source | Selection Rule | Format |
|---------|--------|----------------|--------|
| **🔥 Editorial / Hot Take** | Writer's analysis | 1 opinionated take on the day's most important theme | 1–2 paragraphs |
| **🔵 Análise** | Ranking top 3 | Highest average scores (any tipo) | Expanded cards with full context + link |
| **🟢 Radar de Notícias** | Notícias | Remaining news items after top 3 | Compact summaries + link |
| **🟣 Pulso da Comunidade** | Discussões | Top 2 expanded + rest compact | 2 expanded + N compact with links |
| **💡 Aplicação Prática** | Most useful item | 1 item with highest practical utility | Extensive tutorial + benefit box |

### Step 3: Deduplicate Sections
Discussions in Pulso da Comunidade must NOT overlap with content already covered in Análise. If a discussion is related to an expanded topic, move it to compact format or drop it.

## Newsletter Structure (Final Order)
1. **Header** — Title "Manhã Aumentada", date, IAF logo, metadata (edition, time: **08:00**)
2. **🔥 Editorial / Hot Take** — 1–2 paragraphs, opinionated, data-backed
3. **🔵 Análise** — Top 3 ranked items, expanded
4. **🟢 Radar de Notícias** — Compact news summaries with inline links
5. **🟣 Pulso da Comunidade** — 2 expanded discussions + compact summaries
6. **💡 Aplicação Prática** — 1 extensive tutorial with "O que você ganha" box
7. **Footer** — Sources line + "Gerado por Hermes Agent"

## PDF Improvements (from Special Edition learnings)

### @page and body
```css
@page { size: 210mm 297mm; margin: 0; }  /* NOT size: A4 */
html, body { margin: 0; padding: 0; background-color: #ffffff; }
```

### @media print
```css
@media print {
  html, body { width: 100%; margin: 0; padding: 0; background: #ffffff; }
  .page { overflow: visible !important; page-break-inside: auto; border: none !important; }
  .cover-page { overflow: hidden !important; width: 100% !important; height: 100vh !important; }
}
```

### Minimum font sizes for PDF
| Element | Size | Line-height |
|---------|------|-------------|
| Editorial body (Spectral) | 15.5px | 1.75 |
| Card body (Inter) | 13.5px | 1.65 |
| Bench table (Fira Code) | 10px | — |
| Section titles (Outfit 700) | 17px | — |
| Pull quotes (Spectral italic) | 20px | 1.45 |
| Stat numbers (Outfit 900) | 32px | 1.0 |
| Cover title (Outfit 900) | 46px | 1.15 |
| Callout boxes | 13.5px | 1.65 |
| Timeline text | 13px | 1.5 |
| Footer | 9px | — |

## Correction Principle (Important!)
When the user asks for a correction to the newsletter output (WhatsApp text, PDF, etc.), **change ONLY what was explicitly requested**. Do not reformat other sections, reword unflagged copy, add/remove/reorder items beyond the specific change, or "improve" adjacent content proactively. If a secondary issue is important, surface it as a suggestion *after* delivering the correction.

## WhatsApp Companion Message Format
After delivering the PDF, provide the WhatsApp-friendly text inside ```text:

```text
📰 *IAF — Manhã Aumentada* · DD/MM/AAAA

*[PRIMEIRA FRASE DO EDITORIAL EM NEGRITO]* Restante do editorial...

🔥 *Destaques do dia*
• [Top 1 do ranking — bullet curto]
• [Top 2 do ranking — bullet curto]
• [Top 3 do ranking — bullet curto]

🎯 *Aplicação prática de hoje:* [1 linha]
```

The 3 bullets = top 3 scores regardless of tipo (notícia or discussão).

## Writing Rules
- **Zero anglicisms** — never use English words when Portuguese exists. Explain unavoidable English terms (IPO, GPT, SWE-bench) on first use.
- **Every item must have a link** to the original source.
- **Tone:** Opinionated but professional, like Stratechery. Short paragraphs (3-5 sentences). Vary rhythm.
- **No emojis in HTML** — replace with inline SVGs `stroke="#06b8a0" stroke-width="2.2"`.

## Visual Identity (IAF)
- Colors: --bg-primary #fff, --bg-secondary #f4f7f9, --accent-primary #0a8f88, --accent-hover #06b8a0
- Fonts: Outfit (titles), Inter (body), Fira Code (code/tags)
- Template: `/opt/data/referencias/iaf_v3_reference.html`

## Web Archive (Vercel)
**URL:** `https://iaf-newsletter.vercel.app`
**Projeto:** `/opt/data/iaf-edicoes-archive/`

A landing page com hero + sidebar. Cada edição é HTML responsivo, deployado automaticamente pelo Cron #4.

### Auto-deploy (Cron #4)
Quando o Cron #4 roda, o script `_deploy_new_edition.py`:
1. Detecta o HTML mais recente em `/opt/data/cron/history/` não processado
2. Adiciona entrada ao `_transform.py` EDITIONS
3. Executa `_transform.py` para gerar HTML responsivo
4. Adiciona entrada ao `index.html` editions array
5. Adiciona rewrite ao `vercel.json`
6. Roda `vercel build --prod --yes && vercel deploy --prebuilt --prod --yes`
7. Retorna slug + URL para o cron reportar

### Manual deploy
```bash
cd /opt/data/iaf-edicoes-archive
export PATH="/opt/data/.npm-global/bin:$PATH"
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

### vercel.json
```json
{
  "version": 2,
  "buildCommand": null,
  "outputDirectory": ".",
  "rewrites": [
    { "source": "/05062026", "destination": "/edicoes/05062026.html" },
    ...
  ]
}
```

## Skills Used in Pipeline
| Skill | Cron | Purpose |
|-------|------|---------|
| `hermes-agent` | #1–#4 | General tool usage |
| `newsletter-curation` | #3 | Editorial structure |
| `copywriting` | #3 | Prose quality |
| `humanizer` | #3 | Natural voice |
| `html-to-pdf-chromium` | #3 | Chromium PDF conversion |
| `read-reddit` | (script tool) | Reddit RSS parser |

## Related Files
- `references/iaf-template.html` — Master HTML/CSS template
- `references/iaf-especial-template.html` — Single-topic special edition template
- `/opt/data/iaf-edicoes-archive/_deploy_new_edition.py` — Automated web deploy script
- `/opt/data/iaf-edicoes-archive/_transform.py` — PDF→responsive conversion
- `../productivity/html-to-pdf-chromium` — Chromium PDF skill
