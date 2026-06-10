---
name: iaf-newsletter-pipeline
description: Umbrella skill for newsletter/briefing/digest pipelines: IAF Manhã Aumentada, Daily AI Digest, editorial curation, cron scheduling. Covers multi-source collection, ranking, HTML→PDF, delivery.
trigger: User asks to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline. Also when designing cron-based content aggregation patterns.
metadata:
  hermes:
    tags: [newsletter, pipeline, cron, iaf, briefing, digest, curation]
    related_skills: [brand-iaf-conteudo]
---

# IAF Newsletter Pipeline — Manhã Aumentada

Full automated daily pipeline: coleta → ranqueamento → HTML → PDF → entrega no Telegram + WhatsApp.

> This skill is the umbrella for all newsletter/briefing patterns. See sections below for:
> - [Production pipeline](#pipeline-architecture) — current IAF cron setup
> - [Daily AI Digest](#daily-ai-digest-patterns) — branded magazine-style digest
> - [Cron scheduling](#cron-design-patterns) — chained cron job architecture
> - [Editorial curation](#editorial-curation--ranking) — scoring, dedup, editorial rules

## Pipeline Architecture

Four chained cron jobs, scheduled in **GMT-3** (user's local time). Cron system runs in UTC (+3h).

```
GMT-3          UTC           Cron
─────────────────────────────────────────────────
04:00      →  07:00    🔵  #1 Coleta de Fontes
07:30      →  10:30    🟡  #2 Newsletters
07:50      →  10:50    🔴  #3 Síntese + HTML + PDF
07:55      →  10:55    🟢  #4 Entrega do Ranqueamento (.md)
```

Chaining: `#3 context_from: [#1, #2]` | `#4 context_from: [#3]`

## Cron #1 — Coleta de Fontes (04:00 GMT-3)

**Toolsets:** terminal, web, file  \
**Deliver:** local  \
**Skill:** hermes-agent

Collects from:
- **Reddit:** runs `/opt/data/skills/read-reddit/scripts/reddit_rss_parser.py` → `iaf_reddit.md`
- **Hacker News:** `web_extract` frontpage + /newest → `iaf_hackernews.md`
- **General news:** `web_search` for "AI news today", "generative AI latest", etc. → `iaf_noticias_gerais.md`
- **Social/discussions:** `web_search` Reddit + forums for AI discussions → `iaf_social.md`

Rules: date/time at top, every entry MUST have a clickable link, markdown format, continue on failure.

## Cron #2 — Newsletters (07:30 GMT-3)

**Toolsets:** web, file  \
**Deliver:** local  \
**Skill:** hermes-agent

Extracts from:
- therundown.ai → `iaf_especializados.md`
- superhuman.ai → appended to same file

Only runs later because these newsletters update around 7h local time.

## Cron #3 — Síntese + Ranqueamento + PDF (07:50 GMT-3)

**Toolsets:** terminal, file  \
**Deliver:** origin (Telegram)  \
**Skills:** copywriting, humanizer, html-to-pdf-chromium

### Pipeline Steps

1. **Read all collected files** from `/opt/data/cron/output/`
2. **Build 14-day editorial patrimony** from `/opt/data/cron/history/` — extract all titles/links
3. **Pre-selection** — skim all items, pick **20** most interesting
4. **Post-selection dedup** — check each of the 20 against the 14-day patrimony. Drop duplicates, pull replacements from the full pool until you have **20 strictly inéditos**
5. **Rank pre-selected items** on 3 criteria (1-10 each):
   - Impact (market relevance)
   - Utility (actionable today)
   - Intrigue (novelty/engagement)
   - Average score → sorted table
   - **Save ranking to `/tmp/iaf-ranking.md`** for Cron #4
6. **Select content** from ranking:
   - Editorial/hot take → top 5, highest emotional impact
   - Radar → top 2-3 news (deep dive)
   - Community → top 2-3 discussions (deep dive), no topic overlap with Radar
   - Practical application → 1 item, step-by-step tutorial
7. **Generate HTML** from template `/opt/data/references/iaf_v3_reference.html` — keep exact CSS/layout
8. **Convert to PDF** with Chromium headless → output named `manhã_aumentada_DDMMYYYY.pdf`
9. **Save to history**: `iaf_YYYY-MM-DD.html` + `.pdf` + `iaf-ranking_YYYY-MM-DD.md`
10. **Deliver** — response starts with `MEDIA:/tmp/manha_aumentada_DDMMYYYY.pdf` (first line, nothing before)

## Cron #4 — Entrega do Ranqueamento (07:55 GMT-3)

**Toolsets:** file, terminal  \
**Deliver:** origin (Telegram)  \
Chain: context_from Cron #3

Reads latest output, extracts the ranking table, saves to `/tmp/iaf-ranking.md`, delivers via `MEDIA:/tmp/iaf-ranking.md`.

## Daily AI Digest Patterns

Alternative format: branded magazine-style digest (more visual, less structured). Use when the user requests a "digest" or "magazine" format instead of the standard IAF newsletter.

### Key differences from IAF pipeline:
- **Visual branding:** Magazine-style HTML with cover story, section headers, bylines
- **Content mix:** Notícia vs discussão classification, balanced mix
- **Ranking criteria:** News value + discussion depth + novelty
- **Delivery:** Single PDF attachment, no WhatsApp companion
- **History-based dedup:** Same 14-day patrimony system

### Implementation
- Uses same cron architecture as IAF pipeline
- Different HTML template (magazine layout vs IAF report layout)
- Same Chromium PDF pipeline
- Zero anglicisms rule applies

## Cron Design Patterns

**Chained cron architecture** for multi-stage pipelines:

```
Collector (cron #1, local, no agent=True script pattern)
  → Newsletter fetcher (cron #2, local)
  → Synthesizer (cron #3, deliver to user, context_from: [#1, #2])
  → Ranking delivery (cron #4, deliver to user, context_from: [#3])
```

### Key concepts:
- `context_from: [job_id]` — injects previous cron's output as context
- `deliver: 'local'` — save-only, no message to user
- `deliver: 'origin'` — sends result to originating chat
- **File naming:** `iaf_YYYY-MM-DD.html`, `iaf-ranking_YYYY-MM-DD.md`
- **Output path:** `/opt/data/cron/output/` for collection, `/opt/data/cron/history/` for published editions
- **Recovery:** If synthesis cron fails, use manual recovery process (see below)

### Data-collection pattern (no agent):
For pure data collection without LLM cost:
```bash
cronjob(action='create', schedule='...', script='/path/to/collector.py', no_agent=True)
```
The script's stdout is delivered verbatim.

## Editorial Curation & Ranking

### Three-axis scoring (each 1-10):
- **Impact:** Market relevance / how many people affected
- **Utility:** Actionable today / practical value
- **Intrigue:** Novelty / engagement / surprise factor

### Dedup methodology:
- 14-day sliding window editorial patrimony
- Compare titles AND topic centroids
- Pull replacements from full pool until 20 strictly inéditos

### Section allocation:
- **Editorial (Hot Take):** top 5 by emotional impact, merged into narrative
- **Análise (Deep Dive):** top 3 expanded (2-4 paragraphs each)
- **Radar:** compact news (1-2 lines each), no overlap with Deep Dive topics
- **Pulso da Comunidade:** discussions, first 2 expanded, rest compact
- **Aplicação Prática:** 1 step-by-step tutorial

## Recovery Manual (After Cron #3 Failure)

Use when Cron #3 failed but #1 and #2 succeeded.

### Diagnosis
1. `cronjob(action='list')` — check `last_status`
2. Read 5 collected files in `/opt/data/cron/output/iaf_*.md`
3. Read history rankings in `/opt/data/cron/history/iaf-ranking_*.md`
4. Read canonical HTMLs (`iaf_YYYY-MM-DD.html`, no suffix)

### Process
1. Read 5 collection files → extract title, description, link, category
2. Build 14-day patrimony from history
3. Pre-select 20 items, dedup, rank (Impact/Utility/Intrigue)
4. Allocate by section (Editorial/Analysis/Radar/Community/Practical)
5. Generate HTML from `/opt/data/references/iaf_v3_reference.html`
6. Convert to PDF with Chromium headless
7. Save to history + deliver MEDIA

## WhatsApp Companion Format

Delivered inside ```text block:

```text
📰 *IAF — Manhã Aumentada* · [DATA]

*[PRIMEIRA FRASE DO EDITORIAL EM NEGRITO]* [resto em texto normal]

🔥 *Destaques do dia*
• [top 1] — [descrição curta]
• [top 2] — [descrição curta]
• [top 3] — [descrição curta]

🎯 *Aplicação prática de hoje*
[descrição em 1 linha]
```

## Content Rules

- **Zero anglicisms** — 100% Portuguese
- **Tone:** warm, opinionated, professional (Stratechery/Every style)
- **Every item must have a clickable link**
- **Humanizer pass** at the end
- **14-day context window** for deduplication

## Filter Rules — AI-Only Content

**INCLUIR** apenas itens cujo TEMA CENTRAL é IA: modelos, frameworks, ferramentas, aplicações, regulação, startups, infraestrutura, pesquisa ML/DL, robótica com IA, ciência feita POR IA, agentes.

**EXCLUIR:** ciência sem IA, gadgets sem IA, "boas notícias" sem IA, menções de passagem.

**Regra de ouro:** a notícia PRECISA ser SOBRE inteligência artificial. Em dúvida, EXCLUA.
