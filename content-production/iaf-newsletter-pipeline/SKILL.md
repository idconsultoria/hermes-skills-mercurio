---
name: iaf-newsletter-pipeline
description: Daily automated pipeline for IAF (IA que Funciona) newsletter — from multi-source data collection through ranking, HTML synthesis, Chromium PDF generation, and multi-platform delivery. Covers cron scheduling, content scoring, WhatsApp companion format, and delivery mechanics for Telegram origin.
trigger: User asks to set up, modify, run, or troubleshoot the IAF daily newsletter pipeline. Also use when generating any multi-source curated report with ranking, PDF, and WhatsApp-style companion text.
---

# IAF Newsletter Pipeline — Manhã Aumentada

Full automated daily pipeline: coleta → ranqueamento → HTML → PDF → entrega no Telegram + WhatsApp.

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

**Toolsets:** terminal, web, file  
**Deliver:** local  
**Skill:** hermes-agent

Collects from:
- **Reddit:** runs `/opt/data/skills/read-reddit/scripts/reddit_rss_parser.py` → `iaf_reddit.md`
- **Hacker News:** `web_extract` frontpage + /newest → `iaf_hackernews.md`
- **General news:** `web_search` for "AI news today", "generative AI latest", etc. → `iaf_noticias_gerais.md`
- **Social/discussions:** `web_search` Reddit + forums for AI discussions → `iaf_social.md`

Rules: date/time at top, every entry MUST have a clickable link, markdown format, continue on failure.

## Cron #2 — Newsletters (07:30 GMT-3)

**Toolsets:** web, file  
**Deliver:** local  
**Skill:** hermes-agent

Extracts from:
- therundown.ai → `iaf_especializados.md`
- superhuman.ai → appended to same file

Only runs later because these newsletters update around 7h local time.

## Cron #3 — Síntese + Ranqueamento + PDF (07:50 GMT-3)

**Toolsets:** terminal, file  
**Deliver:** origin (Telegram)  
**Skills:** newsletter-curation, copywriting, humanizer, html-to-pdf-chromium

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
8. **Convert to PDF** with Chromium headless → output named `manhã_aumentada_DDMMYYYY.pdf` (not `iaf-v3-verdadeiro.pdf`)
9. **Save to history**: `iaf_YYYY-MM-DD.html` + `.pdf` + `iaf-ranking_YYYY-MM-DD.md`
10. **Deliver** — response starts with `MEDIA:/tmp/manha_aumentada_DDMMYYYY.pdf` (first line, nothing before)

## Cron #4 — Entrega do Ranqueamento (07:55 GMT-3)

**Toolsets:** file, terminal  
**Deliver:** origin (Telegram)  
Chain: context_from Cron #3

Reads latest output from `e418042f0c99/`, extracts the ranking table, saves to `/tmp/iaf-ranking.md`, delivers as downloadable `.md` file via `MEDIA:/tmp/iaf-ranking.md` (first line of response).

## 🚨 Recuperação Manual Após Falha do Cron #3

Use quando o Cron #3 falhou (ex: créditos insuficientes, timeout, erro 402) mas os coletores (Cron #1 e #2) rodaram com sucesso. O objetivo é gerar a newsletter manualmente a partir dos dados já coletados.

### Diagnóstico — Passo 0

1. **Listar crons** com `cronjob(action='list')` — verificar `last_status` de cada job
2. **Verificar dados coletados** — Cron #1 e #2 devem ter `last_status=ok`
3. **Ler arquivos individuais** em `/opt/data/cron/output/iaf_*.md` — são 5 arquivos:
   - `iaf_reddit.md` (RSS de 10 subreddits)
   - `iaf_hackernews.md` (HN frontpage + /newest)
   - `iaf_noticias_gerais.md` (web_search de notícias)
   - `iaf_social.md` (discussões em fóruns)
   - `iaf_especializados.md` (The Rundown + Superhuman AI)
4. **Ler ranking dos dias anteriores** em `/opt/data/cron/history/iaf-ranking_YYYY-MM-DD.md` para mapear o que já foi coberto (mais rápido que ler HTMLs inteiros)
5. **Ler histórico HTML** em `/opt/data/cron/history/` — foco nos arquivos `iaf_YYYY-MM-DD.html` (sem sufixo `-tarde`, `-light`, `-v5`, `-second-edition` que são rascunhos)

Se o Cron #3 output deu erro `Insufficient Balance` (402), os dados coletados estão intactos. Pode prosseguir.

### Processo de Recuperação (Substitui o Cron #3 manualmente)

1. **Ler os 5 arquivos de coleta** de `/opt/data/cron/output/iaf_*.md` — extrair título, descrição, link e categoria de cada item
2. **Construir patrimônio editorial de 14 dias** — ler histórico (HTMLs + rankings), extrair títulos/links das edições publicadas
3. **Pré-selecionar 20 itens** mais interessantes do pool completo (ignorar itens não-IA conforme Filter Rules)
4. **Dedup pós-seleção** — verificar cada um dos 20 contra o patrimônio. Descartar repetidos, puxar substitutos do pool até ter 20 estritamente inéditos
5. **Ranquear** com scores Impacto (1-10), Utilidade (1-10), Intriga (1-10). Salvar em `/tmp/iaf-ranking.md`
6. **Selecionar alocação por seção:**
   - **Editorial** (Hot Take) → fusão dos top 3-5 itens com maior apelo emocional
   - **Análise** (Deep Dive) → top 3 itens do ranking, expandidos (2-4 parágrafos cada)
   - **Radar de Notícias** → demais notícias (não discussões), formato compacto 1-2 linhas
   - **Pulso da Comunidade** → discussões, primeiras 2 expandidas, resto compacto (sem overlap com Radar)
   - **Aplicação Prática** → 1 item tutorial passo a passo
7. **Gerar HTML** a partir de `/opt/data/references/iaf_v3_reference.html` — manter CSS/layout exato (light mode, #0a8f88 accent). Usar placeholders reais, sem sintaxe de template
8. **Converter para PDF** com Chromium headless:
   ```bash
   DATA_PDF=$(date +%d%m%Y)
   OUTPUT="/tmp/manha_aumentada_${DATA_PDF}.pdf"
   CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
   LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium \
     timeout 90 $CHROMIUM --headless --no-sandbox --disable-gpu \
     --disable-software-rasterizer --no-pdf-header-footer \
     --print-to-pdf="$OUTPUT" "file:///tmp/iaf_v3.html"
   ```
9. **Salvar no histórico:**
   ```bash
   cp /tmp/iaf_v3.html /opt/data/cron/history/iaf_$(date +%Y-%m-%d).html
   cp /tmp/manha_aumentada_$(date +%d%m%Y).pdf /opt/data/cron/history/iaf_$(date +%Y-%m-%d).pdf
   cp /tmp/iaf-ranking.md /opt/data/cron/history/iaf-ranking_$(date +%Y-%m-%d).md
   ```
10. **Entregar** — resposta começa com `MEDIA:/tmp/manha_aumentada_DDMMYYYY.pdf`, depois bloco WhatsApp em ```text

### Pitfalls da Recuperação

- **Dados enormes:** Os 5 arquivos somam ~55K. Pode ser necessário ler em chunks. Foco nos títulos e links — descrições longas podem ser resumidas.
- **Google Fonts no PDF:** O template importa Google Fonts (Outfit, Inter, Fira Code). O Chromium headless lida bem com elas, mas em ambientes sem internet o PDF trava. Remover a tag `<link href="https://fonts.googleapis.com/...">` e usar fallback system fonts se necessário.
- **Dedup contra drafts:** Ignorar arquivos no history com sufixos `-tarde`, `-light`, `-v5`, `-second-edition`. Só considerar os canônicos (`iaf_YYYY-MM-DD.html`).
- **DBus errors no Chromium:** Mensagens `Failed to connect to the bus` são normais em servidor sem desktop. Ignorar.
- **Assinatura de API insuficiente:** Se o erro foi 402/insufficient balance, não adianta re-tentar o cron — é necessário recarregar créditos ou mudar de provider/modelo. A recuperação manual contorna isso gerando a edição no chat atual.

## Revisão Manual de Edição (human-requested revision)

Quando o usuário pedir para revisar, deduplicar ou re-gerar uma edição já publicada (fora do CRON):

### Processo

1. **Ler edição mais recente publicada** de `/opt/data/cron/history/` (ignorar arquivos `*tarde*`, `*second-edition*`, `*v5*`, `*light*` — são rascunhos/vespertinas não publicadas)
2. **Ler arquivos fonte** de `/opt/data/cron/output/` (iaf_hackernews.md, iaf_reddit.md, etc.)
3. **Construir índice de tópicos** da edição publicada: editorial, deep dives, radar, comunidade, aplicação prática
4. **Dedup cruzado** — para cada candidato, comparar título e tópico central contra o índice. Descartar duplicatas, puxar substitutos inéditos do pool completo
5. **Gerar ranking revisado** com scores Impacto/Utilidade/Intriga, salvar em `/tmp/iaf-ranking.md`
6. **Montar HTML revisado** com base no template `iaf_v3_reference.html`, só com conteúdo inédito
7. **Converter para PDF** com Chromium → `/tmp/manha_aumentada_DDMMYYYY.pdf`
8. **ENTREGAR AMBOS OS ARQUIVOS** — incluir `MEDIA:/tmp/manha_aumentada_DDMMYYYY.pdf` e `MEDIA:/tmp/iaf-ranking.md` na resposta como anexos reais (caminhos que existem no disco), não como descrições
9. **Mensagem WhatsApp** no ```text block, conforme formato padrão

### Regras da revisão
- A edição revisada NÃO deve indicar ser uma revisão — tratar como primeira e única versão
- Dedup é contra a edição publicada mais recente APENAS (ignorar edições não-publicadas/vespertinas)
- Ambos os arquivos (PDF + .md) devem ser anexados fisicamente via MEDIA:

## WhatsApp Companion Format (exact)

Used in Cron #3's response and in manual revisions. Delivered inside ```text block:

```text
📰 *IAF — Manhã Aumentada* · [DATA]

*[PRIMEIRA FRASE DO EDITORIAL EM NEGRITO]* [resto do parágrafo editorial em texto normal, sem negrito]

🔥 *Destaques do dia*
• [top 1 ranking] — [descrição curta]
• [top 2 ranking] — [descrição curta]
• [top 3 ranking] — [descrição curta]

🎯 *Aplicação prática de hoje*
[descrição em 1 linha, texto normal, sem negrito]
```

Rules:
- 📰 before title
- First sentence of editorial in **bold** + period, rest in normal text (no bold)
- 🔥 *Destaques do dia* as italic header, then 3 bullets by ranking score
- 🎯 *Aplicação prática de hoje* as header line, description on next line
- Zero sign-offs, zero metadata, zero anglicisms

## MEDIA Delivery from Cron

The cron auto-delivery system sends the agent's final response. To attach a file:
- `MEDIA:/absolute/path/to/file` must be the **first line** of the response
- Blank line after, then content
- This triggers file attachment in Telegram

## Content Rules

- **Zero anglicisms** — 100% Portuguese. If an English term is unavoidable (IPO, GPT), explain it parenthetically on first occurrence.
- **Tone:** warm, opinionated, professional (Stratechery/Every style)
- **Every single item must have a clickable link** — no exceptions
- **Humanizer pass** at the end for natural language flow
- **14-day context window** for deduplication — scan history HTMLs before synthesis

## Filter Rules — AI-Only Content

⚠️ **CRÍTICO: filtrar APENAS conteúdo de IA.** O Superhuman AI newsletter mistura ciência, gadgets e notícias gerais com IA. Todo item deve ser verificado:

**INCLUIR apenas itens cujo TEMA CENTRAL é IA:**
- Modelos, frameworks, ferramentas de IA
- Aplicações de IA (qualquer setor)
- Regulação, política, impacto social da IA
- Startups, investimentos, IPOs de IA
- Infraestrutura de IA (chips, data centers, compute)
- Pesquisa em machine learning / deep learning
- Robótica com IA
- Ciência FEITA POR IA (ex: "vacina desenhada por IA", "proteína modelada por IA")
- Agentes de IA, sistemas autônomos

**EXCLUIR:**
- Descobertas científicas sem IA (edição genética CRISPR/base-editing, novos medicamentos, tratamentos sem IA como ferramenta central)
- Gadgets de consumo (teclados, lava-louças, wearables sem IA)
- Aviões, jatos, carros sem IA
- Fósseis, dinossauros, paleontologia
- "Apenas boas notícias" sem conexão com IA
- Qualquer item onde IA é mencionada apenas de passagem

**Regra de ouro:** a notícia PRECISA ser SOBRE inteligência artificial, não apenas mencionar IA de raspão. Em caso de dúvida, EXCLUA.

## References Directory

- `references/iaf-ranking-methodology.md` — full ranking criteria and scoring guide
- `references/iaf-whatsapp-format.md` — WhatsApp message template and rules
