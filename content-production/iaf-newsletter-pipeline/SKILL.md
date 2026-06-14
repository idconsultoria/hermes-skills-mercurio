---
name: iaf-newsletter-pipeline
description: "Umbrella skill for newsletters and digests — cron scheduling, multi-source curation.
Load this skill to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline. Covers multi-source content collection, editorial ranking and dedup, HTML-to-PDF rendering, Telegram and WhatsApp delivery, and chained cron job architecture."
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
07:40      →  10:40    🔴  #3 Síntese + PDF (ranking é interno)
07:50      →  10:50    🟢  #4 Deploy Web (Vercel)
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

## Cron #3 — Síntese + PDF (07:40 GMT-3 / 10:40 UTC)

**Toolsets:** terminal, file  \\\
**Deliver:** origin (Telegram)  \\\
**Skills configuradas:** copywriting, humanizer, html-to-pdf-chromium, newsletter-curation, iaf-newsletter

> ⚠️ **Skills que podem não existir:** `newsletter-curation` e `iaf-newsletter` não existem em todas as instalações. Se estiverem faltando, o agente recebe um aviso no topo do contexto que polui o prompt e degrada a qualidade da síntese. Antes de uma execução crítica, verifique com `skills_list()` se as skills carregam sem erro. Se não existirem, remova-as do cron job com `cronjob(action='update', skills=[...])` e confie apenas em `copywriting + humanizer + html-to-pdf-chromium`.

### Pipeline Steps

> ⚠️⚠️⚠️ **REGRA ABSOLUTA — VERIFIQUE DATAS ANTES DE SELECIONAR. STALE NEWS QUEIMAM CREDIBILIDADE.**
>
> A coleta de fontes (Cron #1) **não filtra por data**. Itens de dias ou semanas atrás aparecem lado a lado com os de hoje. Cabe a você verificar a data de publicação de cada item antes de incluí-lo. Ver referência `references/news-verification-pitfalls.md` para o método completo.
>
> **Passo obrigatório entre a leitura dos arquivos e a pré-seleção:**
> 1. Para cada item candidato, verifique a data de publicação real (não a data de coleta)
> 2. Se o item tem mais de 48h, DESCARTE — a menos que seja um desenvolvimento novo sobre um tópico contínuo (ex: Fable 5 SHUTDOWN é novo, mesmo sendo sobre Fable 5 que foi lançado antes)
> 3. Prefira fontes com data explícita (artigos de news, comunicados oficiais) a posts de Reddit/HN sem data clara
> 4. Desconfie de listas "top N coisas que aconteceram" — essas sempre misturam old e new

> ⚠️⚠️⚠️ **REGRA ABSOLUTA — DEDUP NÃO É OPCIONAL. ISTO NÃO É UMA SUGESTÃO.**
> 
> **Três vezes seguidas** a newsletter saiu com notícias repetidas porque o agente pulou ou fez dedup superficial. Isso é **inaceitável**.
> 
> A partir de junho/2026, o dedup usa um **manifesto de títulos** (~6KB JSON em vez de ler 14 HTMLs = ~560KB). O script `dedup_manifest.py` extrai e mantém o manifesto. Você NÃO lê os HTMLs brutos — lê o JSON.
> 
> **Seu trabalho:**
> 1. Rode o script (pré-escrita): `python3 /opt/data/cron/scripts/dedup_manifest.py`
> 2. Leia `/opt/data/cron/history/iaf_manifest.json` — use `titles_flat` como patrimônio editorial
> 3. Compare CADA item selecionado contra o manifesto
> 4. Se o mesmo título OU tópico central já apareceu nos últimos 14 dias → **REMOVA**
> 5. Depois de salvar o HTML, rode o script de novo (pós-escrita) pra atualizar o manifesto
> 
> **Não confie na sua memória. Leia o manifesto.**
> **Non-negotiable. Se você pular esta etapa, a newsletter sai com defeito.**

1. **Read all collected files** from `/opt/data/cron/output/`
2. **Verify publication dates** — Before selecting anything, scan each item for date signals (URL dates, datelines, Reddit timestamps). Cross-reference against `references/news-verification-pitfalls.md`. **Discard anything >48h old** unless it's a genuine new development on a continuing story (Fable 5 shutdown is new; Fable 5 launch from last week is not).
3. **Build 14-day editorial patrimony via manifest** — Run `python3 /opt/data/cron/scripts/dedup_manifest.py` (script em `scripts/dedup_manifest.py`), then read `/opt/data/cron/history/iaf_manifest.json`. Use `titles_flat` — a lista plana de todos os títulos publicados nos últimos 14 dias. Compare por similaridade semântica aproximada (palavras-chave, entidades nomeadas, tópico central), não apenas igualdade exata de string. O script é idempotente e custa 0 tokens.
4. **Pre-selection** — skim all items, pick **20** most interesting
5. **Post-selection dedup** — check each of the 20 against `titles_flat` do manifesto. Se um tópico já apareceu como deep dive ou radar nos últimos 14 dias, remova. Pull replacements from the full pool until you have **20 strictly inéditos**.
   
   ⚠️ **Não confie em similaridade aproximada para excluir um match do manifesto.** Se o tópico central é o mesmo (ex: "Google AI Overviews liability" = "Alemanha decide que Google é responsável"), mesmo com título diferente, ele é duplicata e deve ser removido. **Grep manual de cada título contra `titles_flat` é obrigatório antes de finalizar a seleção.**
6. **🔍 LOG obrigatório da dedup** — após concluir a dedup, DOCUMENTE explicitamente no seu raciocínio:
    - Quantos itens foram descartados por já terem sido publicados (ex: "3 itens descartados: 'Drones autônomos' (edit. 11/06), 'Flórida vs OpenAI' (edit. 11/06)")
    - Quantos itens de reposição foram puxados do pool completo
    - Confirmação final: **"20 itens rigorosamente inéditos ✓"**
    - Se zero descartes, diga expressamente: "0 duplicatas encontradas no patrimônio de 14 dias"
    
    ⚠️ **Este log é essencial para auditoria.** A etapa de dedup é invisível no output final — sem este log, não há como verificar se foi executada. Pular o log é considerado **não ter feito a dedup**.
6. **Rank pre-selected items** on 3 criteria (1-10 each):
   - Impact (market relevance)
   - Utility (actionable today)
   - Intrigue (novelty/engagement)
   - Average score → sorted table (uso interno apenas)
7. **Select content** from ranking:
   - Editorial/hot take → top 5, highest emotional impact
   - Análise → top 3 (deep dive)
   - Radar → remaining news items (compact, 1-2 lines each)
   - Community → top discussions
   - Practical application → **1 item, must be broadly accessible (not tech/dev-only)**
8. **Generate HTML** from template `/opt/data/references/iaf_v3_reference.html` — keep exact CSS/layout
   ⚠️ **Verifique o header-metadata-box.** O template tem placeholders `Hora:`, `Data:`, `Edição Diária`. NUNCA substitua `Hora:` por metadata interna do pipeline (ex: `Dedup: 14 dias ✓`). Isso já vazou para o leitor — a linha deve mostrar o horário de publicação, não métricas de curadoria. Confira visualmente no HTML gerado antes de salvar.
9. **Convert to PDF** with Chromium headless → output named `manhã_aumentada_DDMMYYYY.pdf`
   ⚠️ **REGRRA ABSOLUTA: NUNCA use WeasyPrint ou bibliotecas Python para gerar o PDF.** WeasyPrint perde CSS features (gradientes, webkit-background-clip, grid, glow) e produz PDF de ~100KB em vez de 500KB+. Use SEMPRE o Chromium Headless:
   ```bash
   CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
   LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium \
     timeout 120 $CHROMIUM \
     --headless --no-sandbox --disable-gpu \
     --disable-software-rasterizer --no-pdf-header-footer \
     --deterministic-mode \
     --print-to-pdf="$PDF" "file://$HTML"
   ```
   **Verificação:** `ls -lh "$PDF"` — mínimo **300KB**. Se menor, refaça com Chromium.
10. **Save to history**: `iaf_YYYY-MM-DD.html` + `.pdf`
11. **Update dedup manifest** (pós-escrita): `python3 /opt/data/cron/scripts/dedup_manifest.py` — adiciona a edição de hoje ao manifesto rolante
12. **Deliver** — response starts with `MEDIA:/tmp/manha_aumentada_DDMMYYYY.pdf` (first line, nothing before)

## Cron #4 — Deploy Web (07:50 GMT-3 / 10:50 UTC)

**Toolsets:** file, terminal  \\\
**Deliver:** origin (Telegram)  \\\
Chain: context_from Cron #3

Faz o deploy da edição do dia no site `https://iaf-newsletter.vercel.app`.

### Domínios — Arquitetura

O projeto Vercel chama-se `iaf-edicoes-archive`. Ele tem duas URLs:

| Tipo | URL |
|------|-----|
| **Domínio original (produção)** | `https://iaf-edicoes-archive.vercel.app` |
| **Alias (domínio personalizado)** | `https://iaf-newsletter.vercel.app` |

O `vercel deploy --prod` aliaseia automaticamente para o domínio original (`iaf-edicoes-archive.vercel.app`). O alias personalizado (`iaf-newsletter.vercel.app`) **pode NÃO ser atualizado** — é necessário verificar e re-aliasear explicitamente.

**Sempre verificar e corrigir o alias após o deploy** (ver referência `vercel-deploy-pipeline.md` e a seção "Verifica alias" abaixo).

### Fluxo de deploy

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
- 14-day sliding window via **manifest script**: `python3 /opt/data/cron/scripts/dedup_manifest.py` → lê `iaf_manifest.json`
- ~6KB JSON (vs ~560KB de HTMLs brutos) — redução de ~99% tokens
- Script roda **pré-dedup** (prepara referência) e **pós-escrita** (atualiza com edição nova)
- Compare titles AND topic centroids contra `titles_flat`
- Pull replacements from full pool until 20 strictly inéditos
- **🔍 LOG obrigatório** — documente descartes, reposições, confirmação final (ver step 5 do Cron #3)

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

1. **Check cron job skills** — `cronjob(action='list')` and verify the skills list for Cron #3.
   - If skills show as missing, run `skills_list()` to check if they still exist
   - **Skills may have been merged/renamed** during a prior consolidation cycle (check `log.md` in the skills repo for merge records: `grep -i "newsletter\|curation" /opt/data/skills/log.md`). The fix is typically to replace the old skill names with the umbrella skill that absorbed them.
   - Update the cron job with `cronjob(action='update', job_id='...', skills=[...])` — keep only skills that actually exist

2. **Execute the full Pipeline Steps (1-12 above)** — the complete workflow IS the recovery process. Start at Step 1 (read collected files) and proceed through all 12 steps without skipping:
   - Read collected files → dedup → pre-select → rank → write HTML → convert PDF → save history → update manifest → deliver
   - All 12 steps are designed to work in manual mode as well as cron mode

3. **Run the deploy** (Cron #4) separately:
   - Execute `python3 /opt/data/iaf-edicoes-archive/_deploy_new_edition.py`
   - ⚠️ **Verifique o alias Vercel:** após o deploy, o domínio personalizado `iaf-newsletter.vercel.app` pode não ser atualizado. Teste com `curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/{SLUG}"` — se 404, re-aliasseie:
     ```
     vercel alias set <deployment-url-from-script> iaf-newsletter.vercel.app
     ```
   - Confirme 200 no alias antes de entregar o link

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

> 📖 **Leia também:** `references/news-verification-pitfalls.md` — guia completo para verificar datas de publicação e evitar notícias desatualizadas ou duplicadas.

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