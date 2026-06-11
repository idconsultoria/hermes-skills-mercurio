---
name: iaf-newsletter-pipeline
description: "Umbrella skill for newsletter, briefing, and digest pipelines with cron scheduling and multi-source curation.\n\nLoad this skill to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline — IAF Manhã Aumentada, Daily AI Digest, or similar. Covers multi-source content collection, editorial ranking and dedup, HTML-to-PDF rendering, Telegram and WhatsApp delivery, and chained cron job architecture."
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

```\nGMT-3          UTC           Cron\n─────────────────────────────────────────────────\n04:00      →  07:00    🔵  #1 Coleta de Fontes\n07:30      →  10:30    🟡  #2 Newsletters\n07:40      →  10:40    🔴  #3 Síntese + PDF (ranking é interno)\n07:50      →  10:50    🟢  #4 Deploy Web (Vercel)\n```\n\nChaining: `#3 context_from: [#1, #2]` | `#4 context_from: [#3]`

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

## Cron #3 — Síntese + PDF (07:40 GMT-3 / 10:40 UTC)

**Toolsets:** terminal, file  \\
**Deliver:** origin (Telegram)  \\
**Skills:** copywriting, humanizer, html-to-pdf-chromium

### Pipeline Steps

> ⚠️ **ATENÇÃO: NÃO PULE A ETAPA DE DEDUP.** A etapa 2 (patrimônio) e etapa 4 (dedup) são OBRIGATÓRIAS. Já houve caso de newsletter refeita 3× porque o agente pulou a dedup. Leia os HTMLs do histórico para extrair títulos/links — não presuma que sabe o que já saiu.

1. **Read all collected files** from `/opt/data/cron/output/`
2. **Build 14-day editorial patrimony** from `/opt/data/cron/history/` — extract all titles/links. Leia os HTMLs (`iaf_YYYY-MM-DD.html`) do período, não presuma. Um tópico publicado em edição anterior NÃO pode repetir.
3. **Pre-selection** — skim all items, pick **20** most interesting
4. **Post-selection dedup** — check each of the 20 against the 14-day patrimony. **Dica: busque por palavras-chave no conteúdo dos HTMLs históricos** (`search_files` com `file_glob`). Se um tópico já apareceu como deep dive ou radar nos últimos 14 dias, remova. Pull replacements from the full pool until you have **20 strictly inéditos**
5. **Rank pre-selected items** on 3 criteria (1-10 each):
   - Impact (market relevance)
   - Utility (actionable today)
   - Intrigue (novelty/engagement)
   - Average score → sorted table (uso interno apenas)
6. **Select content** from ranking:
   - Editorial/hot take → top 5, highest emotional impact
   - Análise → top 3 (deep dive)
   - Radar → remaining news items (compact, 1-2 lines each)
   - Community → top discussions
   - Practical application → **1 item, must be broadly accessible (not tech/dev-only)**
7. **Generate HTML** from template `/opt/data/references/iaf_v3_reference.html` — keep exact CSS/layout
   ⚠️ **Verifique o header-metadata-box.** O template tem placeholders `Hora:`, `Data:`, `Edição Diária`. NUNCA substitua `Hora:` por metadata interna do pipeline (ex: `Dedup: 14 dias ✓`). Isso já vazou para o leitor — a linha deve mostrar o horário de publicação, não métricas de curadoria. Confira visualmente no HTML gerado antes de salvar.
8. **Convert to PDF** with Chromium headless → output named `manhã_aumentada_DDMMYYYY.pdf`
9. **Save to history**: `iaf_YYYY-MM-DD.html` + `.pdf`
10. **Deliver** — response starts with `MEDIA:/tmp/manha_aumentada_DDMMYYYY.pdf` (first line, nothing before)

## Cron #4 — Deploy Web (07:50 GMT-3 / 10:50 UTC)

**Toolsets:** file, terminal  \\\
**Deliver:** origin (Telegram)  \\\
Chain: context_from Cron #3

Faz o deploy da edição do dia no site `https://iaf-newsletter.vercel.app`. O fluxo:

1. Roda `python3 /opt/data/iaf-edicoes-archive/_deploy_new_edition.py`
2. O script detecta o HTML mais recente em `/opt/data/cron/history/`, registra no arquivo, roda transform para versão web responsiva
3. Executa `vercel build --prod --yes` + `vercel deploy --prebuilt --prod --yes`
4. **Verifica alias:** o deploy `--prod` pode não atualizar `iaf-newsletter.vercel.app` se o alias de produção do projeto divergiu. Execute `vercel alias set <deployment-url> iaf-newsletter.vercel.app` para garantir.
5. Entrega o link no Telegram: `https://iaf-newsletter.vercel.app/{SLUG}`

Se o script retornar `"No new editions to deploy"`, a resposta deve ser `[SILENT]` (já foi deployado hoje).

Vercel CLI em `/opt/data/.npm-global/bin/vercel`. Sempre usar `--prebuilt` para evitar rebuild do zero.

Verificar deploy: `curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/{SLUG}"` → 200.

**Script de deploy:** `/opt/data/iaf-edicoes-archive/_deploy_new_edition.py`

### ⚠️ Pitfalls do deploy

**Regex do excerpt editorial quebrado:**
A função `extract_editorial_first_paragraph()` em `_deploy_new_edition.py` busca no HTML do template pelo texto do editorial para gerar o preview no index. O padrão original `class="hot-take"` não casa com `class="hot-take-box"` — o `"` literal no fim da regex exige que a classe termine exatamente em "hot-take". Use `class="hot-take[^"]*"` para casar qualquer classe que comece com "hot-take" (hot-take-box, hot-take-text, etc.). Se o regex falha, o fallback pega CSS bruto do `<style>` e o preview da edição no index mostra lixo. Verifique sempre o excerpt no index.html depois do deploy.

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
  → Synthesizer + PDF (cron #3, deliver to user, context_from: [#1, #2])
  → Deploy Web (cron #4, deliver to user, context_from: [#3])
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
- **Aplicação Prática: must be broadly accessible.** Não pode ser nichado para devs/engenheiros — exemplos que qualquer leitor possa usar no dia a dia (análise de documentos, simulação de conversas, roteiro de apresentações). Se o conteúdo for técnico demais, troque. ✨ *Exemplo bom: "5 perguntas para fazer ao Fable 5 hoje" — qualquer pessoa testa. Exemplo ruim: "Proteja seu pipeline de supply chain" — só dev entende.*
- **Quando um tópico teve edição especial dedicada:** limite a cobertura a **1 artigo** na edição regular, apontando para o link da edição especial. O link deve ser o URL de produção (`https://iaf-newsletter.vercel.app/especial-{slug}`), não o caminho local.

## Filter Rules — AI-Only Content

**INCLUIR** apenas itens cujo TEMA CENTRAL é IA: modelos, frameworks, ferramentas, aplicações, regulação, startups, infraestrutura, pesquisa ML/DL, robótica com IA, ciência feita POR IA, agentes.

**EXCLUIR:** ciência sem IA, gadgets sem IA, "boas notícias" sem IA, menções de passagem.

**Regra de ouro:** a notícia PRECISA ser SOBRE inteligência artificial. Em dúvida, EXCLUA.
