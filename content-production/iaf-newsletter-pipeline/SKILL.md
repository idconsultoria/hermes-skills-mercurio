---
name: iaf-newsletter-pipeline
description: "Umbrella skill for newsletters — cron scheduling, curation, dedup, deploy.

Load this skill to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline. Covers multi-source content collection, editorial ranking and dedup, HTML generation, deploy no Vercel, e entrega via Telegram no formato WhatsApp-style."
trigger: User asks to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline. Also when designing cron-based content aggregation patterns.
metadata:
  hermes:
    tags: [newsletter, pipeline, cron, iaf, briefing, digest, curation]
    related_skills: [brand-iaf-conteudo]
type: Orchestrator
timestamp: 2026-08-09T05:08:04Z
---

# IAF Newsletter Pipeline — Manhã Aumentada

Full automated daily pipeline: coleta → ranqueamento → HTML → deploy → entrega.

> This skill is the umbrella for all newsletter/briefing patterns. See sections below for:
> - [Production pipeline](#pipeline-architecture) — current IAF cron setup
> - [Daily AI Digest](#daily-ai-digest-patterns) — branded magazine-style digest
> - [Cron scheduling](#cron-design-patterns) — chained cron job architecture
> - [Editorial curation](#editorial-curation--ranking) — scoring, dedup, editorial rules

## Pipeline Architecture

Três chained cron jobs, scheduled in **GMT-3** (user's local time). Cron system runs in UTC (+3h).

```
GMT-3          UTC           Cron
─────────────────────────────────────────────────
04:00      →  07:00    🔵  #1 Coleta de Fontes
07:30      →  10:30    🟡  #2 Newsletters
07:40      →  10:40    🔴  #3 Síntese + Deploy + Entrega (ranking é interno)
```

Chaining: `#3 context_from: [#1, #2]`

**Delivery:** origin (Telegram), formato WhatsApp-style (texto curto, link no topo, sem PDF). Cron #3 faz tudo: síntese, deploy no site Vercel e entrega. Cron #4 foi abolido — incorporado no #3.

## Cron #1 — Coleta de Fontes (04:00 GMT-3)

**Toolsets:** terminal, web, file  \
**Deliver:** local  \
**Skill:** hermes-agent

Collects from:
- **Reddit:** runs `/opt/data/scripts/reddit_rss_parser.py` (via terminal) → consolidated into `iaf_coleta_*.md`
  - Uses old.reddit.com with browser User-Agent (Cloudflare bypass)
  - Multi-strategy fallback: old.reddit → www.reddit
  - File-based cache (TTL 120s) for parallel cron calls
  - Rate-limit aware (respects `x-ratelimit-reset` header)
  - Parses Atom feed format (what old.reddit returns)
  - See `references/reddit-rss-architecture.md`
- **Hacker News:** `web_extract` frontpage (via Firecrawl :3000) → `iaf_hackernews.md`
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

## Cron #3 — Síntese + Deploy + Entrega (07:40 GMT-3 / 10:40 UTC)

**Toolsets:** terminal, file  \\
**Deliver:** origin (Telegram)  \\
**Skills configuradas:** copywriting, humanizer, iaf-newsletter-pipeline

**Responsabilidades integradas:**
- Ler dados dos Crons #1 e #2 (injetados via `context_from`)
- Selecionar e ranquear 20 notícias com dedup em 4 camadas
- Gerar HTML final para deploy (CSS responsivo, sem @page, sem PDF)
- Fazer deploy no Vercel via `_deploy_new_edition.py`
- Entregar mensagem no Telegram em formato WhatsApp-style (link no topo, conciso)

> ⚠️⚠️⚠️ **REGRA ABSOLUTA — DEPLOY ANTES DA MENSAGEM.** O link precisa estar vivo (curl 200) antes de entregar. Não existe "link previsto" — só link confirmado.

### Dedup — 4 Camadas Obrigatórias

> ⚠️ **Três vezes seguidas** a newsletter saiu com notícias repetidas. As regras abaixo existem por este motivo. Não pule nenhuma camada.

### Pipeline Steps

> ⚠️⚠️⚠️ **REGRA ABSOLUTA — VERIFIQUE DATAS ANTES DE SELECIONAR. STALE NEWS QUEIMAM CREDIBILIDADE.**

 ⚠️ **ARMADILHA: roundups de agregadores.** Um agregador (AIToolly, TechCrunch, etc.) pode publicar no dia X uma matéria \"Empresa Y lança Z\" que na verdade é um **roundup de releases dos últimos meses**. A data do artigo NÃO é a data dos lançamentos. Para cada release mencionado no roundup, busque a fonte oficial da empresa e verifique a data real de publicação. Se o release tem semanas ou meses, descarte o item — não é notícia nova. Exemplo real (28/06/2026): AIToolly publicou roundup do Meituan; os releases eram de abril a junho de 2026, NÃO de 27/06.
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
2. **Verify publication dates** — Before selecting anything, scan each item for date signals (URL dates, datelines, Reddit timestamps). Cross-reference against `references/news-verification-pitfalls.md`. **Discard anything >48h old** unless it's a genuine new development on a continuing story. **ATENÇÃO: a exceção de "desenvolvimento novo" não autoriza recontar o mesmo fato.** Só vale se o estado do tópico MUDOU — fato novo objetivo que altera o entendimento anterior. Recontar o mesmo fato com ângulo diferente continua sendo duplicata e deve ser descartado.
3. **Build 14-day editorial patrimony via manifest** — Run `python3 /opt/data/cron/scripts/dedup_manifest.py` (script em `scripts/dedup_manifest.py`), then read `/opt/data/cron/history/iaf_manifest.json`. Use `titles_flat` — a lista plana de todos os títulos publicados nos últimos 14 dias. Compare por similaridade semântica aproximada (palavras-chave, entidades nomeadas, tópico central), não apenas igualdade exata de string. O script é idempotente e custa 0 tokens.
4. **Pre-selection** — skim all items, pick **20** most interesting
5. **Post-selection dedup** — check each of the 20 against `titles_flat` do manifesto. Se um tópico já apareceu como deep dive ou radar nos últimos 14 dias, remova. Pull replacements from the full pool until you have **20 strictly inéditos**.
   
   ⚠️ **Não confie em similaridade aproximada para excluir um match do manifesto.** Se o tópico central é o mesmo (ex: "Google AI Overviews liability" = "Alemanha decide que Google é responsável"), mesmo com título diferente, ele é duplicata e deve ser removido. **Grep manual de cada título contra `titles_flat` é obrigatório antes de finalizar a seleção.**

   ⚠️⚠️⚠️ **REGRAS REFORÇADAS (15/06/2026) — DEDUP SEMÂNTICO E LIMITE DE FREQUÊNCIA**

      **⚠️⚠️⚠️ DEDUP — 4 CAMADAS OBRIGATÓRIAS**

   **Camada 1 — FATO (todas as seções):** mesmo VERBO CENTRAL + mesma ENTIDADE = mesmo fato → REMOVA. Ex: "OpenAI limitou GPT-5.6" = "GPT-5.6 restrito pelo governo" (verbo: restringir, entidade: GPT-5.6).

   **Camada 2 — ENTIDADE (todas as seções):** desenvolvimento NOVO sobre mesma entidade = VÁLIDO. Ex: "Anthropic protocola IPO" ≠ "Anthropic perde executivos". Entity frequency é INFORMATIVA. ⛔ EXAUSTO alerta, não exclui.

   **Camada 3 — TESE EDITORIAL (hot-take APENAS):** LEIA o hot-take-box dos últimos 14 HTMLs em /opt/data/cron/history/. Se a mesma tese central já apareceu em 2+ edições, TROQUE. Ex real: "governo gatekeeper" foi editorial em 26/06 e 27/06.

   **Camada 4 — EDIÇÕES ESPECIAIS:** se o tema do editorial tem edição especial em `/opt/data/iaf-edicoes-archive/edicoes/especial-*.html`, não reescreva. Limite a 1 artigo apontando para o link da especial.

   ⚠️ **LOG obrigatório:** descartes por camada + "20 itens rigorosamente inéditos ✓". Sem log = dedup não feita. (empresa, modelo, pessoa, sigla de índice, evento) apareceu no mesmo papel temático em edições anteriores. Exemplos:
   - "S&P 500 rejeita entrada" ≈ "S&P 500 barra OpenAI" ≈ "S&P 500 bloqueia IPO" → **mesmo tópico** (S&P 500 + entrave regulatório a IPOs de IA)
   - "Fable 5 proibido" ≈ "Anthropic desliga Mythos" ≈ "Governo dos EUA vs Fable" → **mesmo tópico** (desligamento/debate regulatório do Fable 5)
   - "Nova onda de modelos abertos" ≈ "Enxurrada de modelos abertos" ≈ "Onda de lançamentos open-weight" → **mesmo tópico**

   **Como aplicar:** extraia as 2-3 entidades centrais de cada item selecionado (ex: "S&P 500", "rejeição", "OpenAI"). Se o mesmo trio de entidades aparecer em QUALQUER título de `titles_flat` nos últimos 14 dias, o item é duplicata — mesmo que as palavras sejam diferentes.

   ⚠️⚠️⚠️ **REGRA DE DEDUP — TRÊS CAMADAS**

   **1. FATO (radar/deep dive):** mesmo fato com ângulo diferente = duplicata. Verbo central + entidade = mesmo fato? Remove.
   **2. ENTIDADE (todas as seções):** mesma entidade com desenvolvimento NOVO = válido. Não remova por frequência.
   **3. TESE EDITORIAL (hot-take):** antes de definir o tema do editorial, VERIFIQUE a tese central nos últimos 14 DIAS de editoriais. Para isso:
      - Leia os HTMLs em `/opt/data/cron/history/iaf_*-*/*.html` (últimos 14)
      - Extraia o primeiro parágrafo do hot-take-box
      - Identifique a TESE CENTRAL (ex: "governo gatekeeper", "custo da IA", "China vs EUA")
      - Se a mesma tese central apareceu em 2+ edições anteriores → REMOVA. Escolha outra tese.
   
   **Por que isso existe:** o editorial de 26/06 usou "governo virou gatekeeper", o de 27/06 reforçou "governo é porteiro", e o de 29/06 (erro) repetiu "portão trancou". Três edições com a MESMA TESE. O leitor já absorveu esse argumento.

   ⚠️ **Estas regras existem porque a newsletter repetiu os mesmos tópicos 5-7 vezes em 11 edições. O leitor já se informou. Pare de recontar a mesma história.**

6. **🔍 LOG obrigatório da dedup** — após concluir a dedup, DOCUMENTE explicitamente no seu raciocínio:
    - Quantos itens foram descartados por já terem sido publicados (ex: "3 itens descartados: 'Drones autônomos' (edit. 11/06), 'Flórida vs OpenAI' (edit. 11/06)")
    - Quantos itens de reposição foram puxados do pool completo
    - **Confirmação de Regra A:** "Nenhuma entidade duplicada encontrada em títulos semanticamente diferentes" (ou liste quais entidades denunciaram duplicata)
    - **Confirmação de Regra B:** lista dos 5 tópicos mais frequentes e contagem de aparições (ex: "Fable/Mythos: 5 edições ⛔ EXCLUÍDO, S&P 500: 6 edições ⛔ EXCLUÍDO, modelos abertos: 2 edições ✅")
    - Confirmação final: **"20 itens rigorosamente inéditos ✓"**
    - Se zero descartes, diga expressamente: "0 duplicatas encontradas no patrimônio de 14 dias"

    ⚠️ **Este log é essencial para auditoria.** A etapa de dedup é invisível no output final — sem este log, não há como verificar se foi executada. Pular o log é considerado **não ter feito a dedup**.
6. **Rank pre-selected items**
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

   ⚠️⚠️⚠️ **VERIFICAÇÃO DE ENTIDADES DO EDITORIAL — REGRA ABSOLUTA**
   > O editorial é a seção de MAIOR VISIBILIDADE da newsletter. Uma entidade repetida aqui queima mais credibilidade do que em qualquer outra seção.

   Antes de redigir o editorial, extraia TODAS as entidades nomeadas (empresas, produtos, pessoas, siglas) que você planeja usar como elementos centrais da narrativa. Para cada entidade, faça um grep manual em `titles_flat` do manifesto. Se a entidade já apareceu no MESMO PAPEL TEMÁTICO nos últimos 14 dias, substitua esse elemento da narrativa por outro diferente do pool.

   **Exemplo real (1906/2026):** "Midjourney scanner médico" foi entidade central do editorial de 18/06. No dia 19/06, o editorial tentou usar "Midjourney scanner" como contraponto à OpenAI — mesma entidade, mesmo papel (empresa de IA fazendo algo inesperado). A entidade já estava no manifesto e deveria ter sido barrada.

   **Como aplicar na prática:**
   1. Esboce os 2-3 parágrafos do editorial (use o top 5 + gancho narrativo)
   2. Extraia as entidades-chave usadas (ex: "OpenAI", "Anthropic", "SearchLeak", "Midjourney")
   3. Para cada entidade, busque em `titles_flat` do manifesto
   4. Se alguma entidade apareceu nos últimos 14 dias no mesmo papel temático → **troque o elemento narrativo por um diferente**
   5. O editorial final deve conter **zero entidades repetidas** do manifesto

   A exceção de "desenvolvimento novo" (Regra C) se aplica, mas com critério MAIS RESTRITIVO no editorial: o fato novo deve ser tão relevante que justifique a repetição da entidade. Em dúvida, troque.
8. **Generate HTML** from template `/opt/data/references/iaf_v3_reference.html` — keep exact CSS/layout
   ⚠️ **Use APENAS as classes do template.** As classes oficiais são:
   - `.hot-take-box` / `.hot-take-text` (editorial)
   - `.deep-dive-card` / `.deep-dive-header` / `.deep-dive-title` / `.deep-dive-body` / `.deep-dive-link` + `.dd-tag.tag-analysis|tag-product|tag-community` (análise)
   - `.news-grid` / `.news-item` / `.news-bullet` / `.news-text` + `.news-tag.tag-biz|tag-creative|tag-alert` (radar)
   - `.community-grid` / `.community-item` / `.community-sentiment.sentiment-hot|mixed|negative` (comunidade)
   - `.app-card` / `.app-header` / `.app-source` / `.app-title` / `.app-desc` / `.app-benefit` (aplicação prática)
   - `.footer` / `.footer-left` / `.footer-center` / `.footer-right`
   - `.promo-teaser` / `.promo-card` / `.promo-card-label` / `.promo-card-title` / `.promo-card-desc` / `.promo-card-features` / `.promo-card-feature` / `.promo-card-link` (anúncio fixo Jornada de IA — ver seção Anúncio Fixo abaixo)
   - `.promo-teaser` / `.promo-card` / `.promo-card-label` / `.promo-card-title` / `.promo-card-desc` / `.promo-card-features` / `.promo-card-feature` / `.promo-card-link` / `.feat-dot` (anúncio fixo Jornada de IA — **NÃO REMOVER**, ver seção Anúncio Fixo abaixo)
   - NÃO invente classes. NUNCA use `footer-note`, `radar-item`, `radar-source`, `aplicacao-box` ou outras classes fora do template.
   ⚠️ **Quantidade de itens por seção:**
   - Radar: mínimo **10 itens** (ver edições anteriores: 11-14)
   - Comunidade: **2 expandidos** (deep-dive-card) + **4 compactos** (community-grid) = 6 total
   - Deep dive: exatamente **3 cards**
   ⚠️ **Google Fonts:** inclua o link para Inter + Outfit + Fira Code (cabeçalho do template). O deep-dive-grid usa flex-direction:column com gap fixo — cards muito longos podem desbalancear a estrutura HTML do card seguinte (perda de divs de fechamento, formatação incorreta). Limite cada card de análise a **no máximo 3-4 parágrafos**. Se o conteúdo for extenso, condense: agrupe múltiplos lançamentos num só parágrafo (ex: lista compacta de bullet points inline em vez de um parágrafo por item) e mova detalhes para o link de referência. Verifique a estrutura HTML dos cards adjacentes após qualquer edição manual.
   ⚠️ **Verifique o header-metadata-box.** O template tem placeholders `Hora:`, `Data:`, `Edição Diária`. NUNCA substitua `Hora:` por metadata interna do pipeline (ex: `Dedup: 14 dias ✓`). Isso já vazou para o leitor — a linha deve mostrar o horário de publicação, não métricas de curadoria. Confira visualmente no HTML gerado antes de salvar.
9. **Save to history**: `iaf_YYYY-MM-DD.html`
10. **Update dedup manifest** (pós-escrita): `python3 /opt/data/cron/scripts/dedup_manifest.py` — adiciona a edição de hoje ao manifesto rolante
11. **Deliver — WHATSAPP VIA BRIDGE (NÃO PULE — SEPARADO DA ENTREGA TELEGRAM)**

    ⚠️⚠️⚠️ **REGRA ABSOLUTA — ENTREGAR WHATSAPP É OBRIGATÓRIO E DISTINTO DA ENTREGA TELEGRAM.**
    A entrega WhatsApp (via bridge API) e a entrega Telegram (via `deliver: origin` da resposta final) são DUAS AÇÕES SEPARADAS. A primeira NÃO substitui a segunda, e vice-versa. O agente PULA o WhatsApp consistentemente por confundir as duas — não cometa este erro.

    > **ARMADILHA CONFIRMADA (08/07/2026):** O agente chega até aqui, gera a mensagem, e em vez de chamar a bridge, coloca o conteúdo na resposta final como se fosse a "entrega Telegram". A resposta final vai para Telegram SIM, mas o WhatsApp fica sem enviar. A instrução "Resposta final" no fim do prompt confunde o agente, que trata a resposta como substituta do curl.

    **Para evitar, siga esta ORDEM:**

    a) **Primeiro — WhatsApp:** Formate a mensagem curta (15-25 linhas) no padrão WhatsApp Companion Format. Salve em `/tmp/iaf_whatsapp_{SLUG}.txt` **usando terminal com heredoc** (`cat > /tmp/iaf_whatsapp_{SLUG}.txt << 'HERMES_EOF'`). **⚠️ NUNCA use `write_file` para escrever em `/tmp/` — ele bloqueia caminhos em `/tmp/` por segurança, e o agente alucina sucesso mesmo com o write negado.** Só depois de receber `messageId` você pode passar ao próximo passo.

    b) **Depois — Resposta final:** Escreva a confirmação curta (formato abaixo) que vai para o Telegram via `deliver: origin`.

    **Método de envio (use TERMINAL, não Python urllib):**

    ```bash
    curl -s -X POST http://127.0.0.1:3000/send \
      -H "Content-Type: application/json" \
      -d "$(python3 -c "import json; print(json.dumps({'chatId':'120363419131378682@g.us','message':open('/tmp/iaf_whatsapp_{SLUG}.txt').read()}))")"
    ```

    **Verificação obrigatória:** o JSON de resposta deve conter `"success":true` e um `"messageId"` não vazio. Sem isso, a mensagem não chegou ao grupo.

    **Confirmação visual de que você NÃO pulou o WhatsApp:** se sua resposta final não contém um messageId, você pulou a entrega WhatsApp. Refaça.

> 📖 **Leia também:** `references/whatsapp-telegram-conflation.md` — histórico completo do bug, causa raiz e verificação.

Agora Cron #3 faz tudo: síntese, deploy e entrega. O deploy está no passo 10 do Pipeline Steps.

(Abaixo, referência de deploy mantida para fallback manual — Cron #4 foi incorporado ao #3)

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
5. Entrega o link no WhatsApp: `https://iaf-newsletter.vercel.app/{SLUG}`

Se o script retornar 'No new editions to deploy', verifique o MOTIVO:
   - Se é uma edição nova que falhou ao registrar: execute os passos manualmente (vercel build --prod --yes + vercel deploy --prebuilt --prod --yes)
   - Se é uma CORREÇÃO de edição já publicada: NÃO use o script — siga o workflow em references/manual-redeploy.md (copiar HTML corrigido → rebuild → deploy → verificar alias)

Vercel CLI em `/opt/data/.npm-global/bin/vercel`. Sempre usar `--prebuilt` para evitar rebuild do zero.

Verificar deploy: `curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/{SLUG}"` → 200.

**Script de deploy:** `/opt/data/iaf-edicoes-archive/_deploy_new_edition.py`

### ⚠️ Pitfalls do deploy

**Regex do excerpt editorial quebrado:**
A função `extract_editorial_first_paragraph()` em `_deploy_new_edition.py` busca no HTML do template pelo texto do editorial para gerar o preview no index. O padrão original `class="hot-take"` não casa com `class="hot-take-box"` — o literal no fim da regex exige que a classe termine exatamente em "hot-take". Use `class="hot-take[^"]*"` para casar qualquer classe que comece com "hot-take" (hot-take-box, hot-take-text, etc.). Se o regex falha, o fallback pega CSS bruto do `<style>` e o preview da edição no index mostra lixo. Verifique sempre o excerpt no index.html depois do deploy.

**Context compaction manda o passo WhatsApp pro espaço:**
Quando o agente sofre context compaction (especialmente com erro 402 de sumarização), ele perde as instruções de entrega WhatsApp e entra em modo "relatório verboso" — produz um sumário longo em vez de formatar a mensagem curta e chamar a bridge. Para mitigar:
- O passo de entrega WhatsApp (step 11) está marcado como REGRA ABSOLUTA. Leia-o com atenção após qualquer recuperação de contexto.
- A formatação NÃO é opcional: gere exatamente 15-25 linhas no formato WhatsApp Companion Format.
- NÃO substitua a mensagem curta por um relatório de execução. A resposta final deve conter APENAS: URL do deploy + HTTP status + messageId.
- Se sentir que seu contexto está truncado ou que você "pulou" alguma etapa, volte ao Pipeline Steps e verifique cada passo antes de finalizar.
- Confirmação visual: se sua resposta final tem mais de 30 linhas, provavelmente você está no modo "relatório" — recomece.

## Diagnóstico & Auditoria de Cron Runs

Quando o usuário pedir análise de uma execução do pipeline (consumo de tokens, URLs visitadas, tool calls, falhas), use este método.

### 1. Identificar a sessão

Cada cron job cria uma sessão com ID no formato `cron_{job_id}_{timestamp}`.

```python
# 1. Listar cron jobs → job_id para "IAF — Coleta de Fontes" é b874e9037245
cronjob(action='list')

# 2. Buscar a última sessão do job
session_search(query="b874e9037245", limit=3)
# Retorna session_id como "cron_b874e9037245_20260616_070047"

# 3. Ler a sessão completa
session_search(session_id="cron_b874e9037245_20260616_070047")
```

### 2. Ler o relatório do cron

O sistema salva um relatório de cada execução:
```bash
ls /opt/data/cron/output/{job_id}/
```

### 3. Contar tool calls

Ler a sessão pelo `session_search` (modo read ou scroll). Agrupar por `function.name` de cada `tool_call` nas mensagens `role='assistant'`.

**Tool call inventory típica do Cron #1 (27 calls):**

| Fase | Tools | Qtd |
|---|---|---|
| Setup | terminal (mkdir), read_file | 2 |
| Reddit RSS | terminal × 14 (7 subs × Hot + Top) | 14 |
| HN | web_extract | 1 |
| Web searches | web_search × 8 | 8 |
| Output | write_file + read_file | 2 |

### 4. URL counting

- **web_extract** → 1 URL visitada por chamada (HTTP real via Firecrawl)
- **terminal com `reddit_rss_parser.py`** → 1 requisição HTTP por chamada (embora falhe, é uma URL tentada)
- **web_search** → retorna URLs como metadados, NÃO visita individualmente
- **Arquivo de output** → contém ~30-50 links incorporados

### 5. Token consumption from state.db (accurate, preferred)

The Hermes session database at `/opt/data/state.db` stores exact token counts.

```python
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
rows = conn.execute('''
SELECT id, source, model, started_at, ended_at, message_count, tool_call_count,
       input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, 
       reasoning_tokens, estimated_cost_usd, actual_cost_usd, cost_status, title
FROM sessions 
WHERE id LIKE 'cron_{job_id}%'
ORDER BY started_at DESC
''').fetchall()
```

**Columns of interest:**

| Column | Meaning |
|--------|---------|
| `input_tokens` | Tokens sent to API (cache miss portion) |
| `output_tokens` | Tokens generated by model |
| `cache_read_tokens` | Tokens served from cache (billed at ~10% rate) |
| `reasoning_tokens` | DeepSeek thinking tokens (0 for Flash model) |
| `tool_call_count` | Total function calls made in session |
| `estimated_cost_usd` | Cost estimate (may be 0 if cost_status=unknown) |

**Cache hit rate:** `cache_read_tokens / (input_tokens + cache_read_tokens) * 100`

Typical Cron #1 Coleta de Fontes: ~85-93% cache hit, ~R$ 0.15-0.23 per run.

### 6. Token estimation (when DB is not accessible)

Use this method only when you cannot access `state.db` (e.g., running in a context without Python/sqlite3). Prefer the DB approach for accuracy.

| Componente | Tokens (típico) |
|---|---|
| Prompt do sistema + ferramentas | ~5.500 |
| User prompt | ~800 |
| Reddit RSS results | ~2.800 |
| web_extract (HN frontpage) | ~8.000-12.000 |
| web_search (8 consultas) | ~10.000-15.000 |
| Raciocínio do agente | ~3.000-5.000 |
| Output file | ~3.000-4.000 |
| **Total estimado** | **~30.000-40.000** |

Cache hit do modelo (~98%) reduz custo real a centavos.

### 6. Arquitetura dos backends (por tool)

| Tool | Backend | Firecrawl? |
|---|---|---|
| `web_extract` | Firecrawl Docker :3000 (Chromium headless) | ✅ Sim |
| `web_search` | Provider search API (Tavily/Similarweb) | ❌ Não |
| `terminal` | Docker host shell (Python 3.13) | ❌ Não |

Mais detalhes em `references/tool-backend-architecture.md`.

### 7. Problemas comuns na auditoria

- **Reddit bloqueado** — HTTP 403/429 do Cloudflare em `www.reddit.com`. **FIX:** o script `reddit_rss_parser.py` agora usa `old.reddit.com` com browser User-Agent + cache file-based + retry com backoff. Isso resolve o bloqueio Cloudflare na maioria dos casos. O script também faz fallback automático entre old.reddit e www.reddit. Se ainda falhar, use `web_search` como fallback na coleta.
- **web_search retorna vazio** — aconteceu em 16/06. Tentar reformular a query ou usar web_extract.
- **Arquivos de coleta desatualizados (stale).** Os arquivos `iaf_noticias_gerais.md`, `iaf_reddit.md` etc. REFLETEM a data/hora da ÚLTIMA execução do Cron #1, não necessariamente o dia atual. Se o Cron #1 falhar por vários dias, os arquivos ficam parados no tempo. **Sempre verificar a data de coleta no cabeçalho de cada arquivo** (ex: "Coleta: 2026-06-09 07:00 UTC"). Se a data de coleta for >24h atrás, NÃO confiar no conteúdo desses arquivos — executar `web_search` fresco para cada categoria antes de iniciar a pré-seleção. O marcador de data está no cabeçalho do arquivo (linha 2-3 do markdown). Ignorar este passo = notícias velhas na newsletter.
- **Sessão não encontrada** — FTS5 pode não ter indexado sessões muito antigas. Buscar por prefixo.

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
  → Synthesizer + Deploy + WhatsApp (cron #3, deliver to user, context_from: [#1, #2])
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

> **TODOS os crons falharam na mesma janela?** Provavelmente provider outage, não
> bugs independentes. Ver `references/pipeline-failure-modes.md` → "Provider Outage
> (all crons failed)" para triagem + rerun em ordem de dependência. Sinal clássico:
> `TimeoutError: idle for 600s — waiting for non-streaming API response` no
> errors.log, com jobs OK antes e depois da janela.

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
   - Read collected files → dedup → pre-select → rank → write HTML → save history → update manifest → deliver
   - All 12 steps are designed to work in manual mode as well as cron mode

3. O deploy agora é feito pelo próprio Cron #3 (passo 10 do Pipeline Steps). Em recovery manual, execute o deploy manualmente via _deploy_new_edition.py. Confirme curl 200 antes de entregar.
   - Execute `python3 /opt/data/iaf-edicoes-archive/_deploy_new_edition.py`
   - ⚠️ **Verifique o alias Vercel:** após o deploy, o domínio personalizado `iaf-newsletter.vercel.app` pode não ser atualizado. Teste com `curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/{SLUG}"` — se 404, re-aliasseie:
     ```
     vercel alias set <deployment-url-from-script> iaf-newsletter.vercel.app
     ```
   - Confirme 200 no alias antes de entregar o link

## WhatsApp Companion Format

> ⚠️ **ANTIPADRÃO CONFIRMADO — NUNCA incluir seção "O que mais importa" na mensagem WhatsApp.**
> Esta seção foi usada em edições passadas e está **PROIBIDA**. A mensagem WhatsApp deve seguir ESTRITAMENTE o formato abaixo com 🔥 *Destaques do dia*, SEM variações. Se você encontrar exemplos anteriores com "O que mais importa", IGNORE-OS.
> Motivo: o leitor do WhatsApp já recebe o link da edição web como primeira informação. A seção "O que mais importa" duplica o editorial sem valor agregado e alonga a mensagem desnecessariamente.

Formato aprovado (exemplo real da edição de 28/06):

```
📰 *IAF — Manhã Aumentada* · DD/MM/AAAA
🌐 https://iaf-newsletter.vercel.app/SLUG

*[FRASE DE ABERTURA DO EDITORIAL]* [resto em texto normal, máximo 3-4 linhas]

🔥 *Destaques do dia*
• [EMOJI] *[Título em negrito]* — [descrição concisa em 1 linha, sem quebra]
• [EMOJI] *[Título em negrito]* — [descrição concisa em 1 linha, sem quebra]
• [EMOJI] *[Título em negrito]* — [descrição concisa em 1 linha, sem quebra]

🎯 *Aplicação prática de hoje*
[1-2 linhas, imperativo, acionável hoje, sem enrolação]

🎓 *Jornada de IA:* idconsultoria.ai/jornada-ia
```

### Especificações exatas:

**Cabeçalho:**
```📰 *IAF — Manhã Aumentada* · DD/MM/AAAA```
**Linha 2 — LINK do deploy como primeira informação:**
```🌐 https://iaf-newsletter.vercel.app/SLUG```
O link da edição web é a PRIMEIRA informação de conteúdo que o leitor vê, logo abaixo do cabeçalho. Sempre inclua.

**Editorial:**
- Máximo 3-4 linhas
- Primeira frase em negrito com `*...*`, termina com ponto final
- Resto em texto normal, sem negrito
- Deve introduzir o tema central sem recontar a edição inteira
- NUNCA repetir tese de editoriais anteriores (ver Camada 3 do dedup)

**Destaques do dia:**
- EXATAMENTE 3 itens. Nem mais, nem menos.
- Cada item: `• [EMOJI] *Título em negrito* — descrição em texto normal`
- EMOJI deve ser relevante ao conteúdo:
  - 🧠 = pesquisa/descoberta científica
  - 🔐 = segurança/regulação
  - 🏭 = indústria/negócios
  - 🤖 = robótica/agentes
  - 📱 = produto/ferramenta
  - 🏛️ = governo/política
  - 💰 = investimentos/financeiro
  - ⚡ = infraestrutura/hardware
  - 🌏 = geopolítica
  - 🎨 = criativo/mídia
  - 🔬 = paper/pesquisa acadêmica
- Título em negrito: máximo 5-6 palavras
- Descrição: 1 linha, máximo ~150 caracteres, direto ao ponto
- NUNCA usar dois pontos ou traços extra — só `—` separa título da descrição

**Aplicação prática:**
- 1-2 linhas no máximo
- Imperativo (ex: "Teste 3 modelos...", "Pegue uma tarefa...")
- Acionável hoje, não genérico
- Acessível a não-devs
- Sem bullet points, sem estrutura extra

**Regras gerais:**
- SEM link do site na mensagem (o link está na edição web, que o leitor acessa pelo navegador)
- SEM separadores visuais (—, ---, ===) entre seções
- SEM "Destaques do dia:" com dois pontos no título — só 🔥 *Destaques do dia*
- SEM "Aplicação prática de hoje:" com dois pontos — só 🎯 *Aplicação prática de hoje*
- Total da mensagem: idealmente **15-25 linhas**. Não ultrapassar 30.
- Zero anglicismos verbais ("deployar", "buildar", "open-sourcar")
- Um espaçamento entre seções (linha em branco), não mais
- O formato é para Telegram (Markdown). *texto* vira itálico, *texto* com asterisco duplo vira negrito.

## Anúncio Fixo — Jornada de IA (Template)

> 📖 **CSS + HTML completos em:** `references/jornada-ia-anuncio.md`

Bloco de anúncio persistente da Jornada de IA da ID Consultoria (idconsultoria.ai/jornada-ia). Inserido **no template** (`/opt/data/references/iaf_v3_reference.html`) e **nunca removido** pelo agente durante a geração.

### Posição no HTML

| Elemento | Posição | Âncora |
|----------|---------|--------|
| **Teaser** (`.promo-teaser`) | Entre o `</header>` e o `<!-- HOT TAKE -->` | `href="#anuncio-jornada"` — clica e rola até o card |
| **Card** (`.promo-card`) | Entre o `</section>` da Análise e o `<!-- RADAR -->` | `id="anuncio-jornada"` — destino da âncora |

```html
<!-- Estrutura resumida — ver referência para HTML/CSS completo -->
<a href="#anuncio-jornada" class="promo-teaser">...</a>   <!-- antes do Editorial -->
<section class="section" id="anuncio-jornada">            <!-- entre Análise e Radar -->
  <div class="promo-card">...</div>
</section>
```

### Regras

- ⚠️ **NÃO REMOVER.** O bloco tem comentário `<!-- ⚠️ ANÚNCIO FIXO — NÃO REMOVER -->`. Se aparecer no template, mantenha no HTML final exatamente como está.
- As classes `.promo-teaser` e `.promo-card*` usam cores âmbar/dourado (`--accent-amber`) para se diferenciar visualmente do teal editorial.
- O CSS deve ser incluído no `<style>` de toda edição gerada. Ver referência para o bloco completo.
- O teaser e o card são **estáticos** — não altere o texto, preços ou link. A copy só muda quando o usuário solicitar explicitamente.

### Conteúdo do card

- **Label:** "Jornada de IA · ID Consultoria"
- **Título:** "Do zero ao agente autônomo em 3 cursos práticos"
- **Descrição:** Lives semanais + comunidade + zero assinatura + inscrições abertas
- **Features:** C1 R$597, C2 R$1.497, C3 R$2.497, 30 dias de garantia
- **Link:** `https://idconsultoria.ai/jornada-ia`

### Preview

Exemplo funcional em `/opt/data/cron/history/iaf_2026-07-17_preview_anuncio.html`.

## Anúncio Fixo — Jornada de IA · ID Consultoria

> ⚠️⚠️⚠️ **REGRA ABSOLUTA — O ANÚNCIO NÃO PODE SER REMOVIDO.**

O template `/opt/data/references/iaf_v3_reference.html` contém dois blocos de anúncio da Jornada de IA que **devem ser preservados exatamente como estão** em toda edição gerada:

### Elementos no template

| Elemento | Posição | Classes |
|----------|---------|---------|
| **Teaser** | Após `</header>`, antes do `<!-- HOT TAKE -->` | `.promo-teaser` |
| **Card** | Após `</section>` da Análise, antes do `<!-- RADAR -->` | `.promo-card`, `.promo-card-label`, `.promo-card-title`, `.promo-card-desc`, `.promo-card-features`, `.promo-card-feature`, `.feat-dot`, `.promo-card-link` |

### Comportamento esperado

- O teaser tem `href="#anuncio-jornada"` — ao clicar, rola a página até o card (que tem `id="anuncio-jornada"`)
- Ambos os blocos têm comentário `<!-- ⚠️ ANÚNCIO FIXO — NÃO REMOVER -->`
- **NÃO altere o texto, preços ou link.** A copy é fixa: C1 R$597, C2 R$1.497, C3 R$2.497, garantia 30 dias, link `https://idconsultoria.ai/jornada-ia`
- O CSS das classes `.promo-teaser` e `.promo-card*` já está no template — **não o remova do `<style>`**
- Cores: âmbar/dourado (`--accent-amber`) para diferenciar do teal editorial

### Preview

Arquivo de referência: `/opt/data/cron/history/iaf_2026-07-17_preview_anuncio.html`

### Na mensagem WhatsApp

Adicione **1 linha extra** após a Aplicação Prática:

```
🎓 *Jornada de IA:* idconsultoria.ai/jornada-ia
```

Esta linha é fixa e deve ser incluída em toda mensagem de entrega (Telegram e WhatsApp).

## Content Rules

> 📖 **Leia também:** `references/news-verification-pitfalls.md` — guia completo para verificar datas de publicação e evitar notícias desatualizadas ou duplicadas.
> 📖 **Leia também:** `references/manual-redeploy.md` — como forçar o redeploy de uma edição já publicada (correções editoriais).
> 📖 **Leia também:** `references/meituan-longcat-sources.md` — fontes oficiais do ecossistema Meituan LongCat, com datas reais de cada release e links diretos para o tech blog da empresa.

- **Zero anglicisms** — 100% Portuguese, sem pseudo-verbos de origem inglesa. Especificamente: NÃO use "open-sourcar" / "open-sourcou" (prefira "disponibilizar em código aberto", "lançar como open-source" — mantendo "open-source" como adjetivo, não verbo). NÃO use "deployar" (prefira "publicar", "implantar"). NÃO use "buildar" (prefira "compilar", "construir"). NÃO use "testar via rollout" (prefira "lançar gradualmente"). Anglismos técnicos consolidados (open-source, benchmark, framework, deploy, pipeline) são aceitos como **substantivos** — nunca como verbos conjugados em português.
- **Tone:** warm, opinionated, professional (Stratechery/Every style)
- **Every item must have a clickable link**
- **Humanizer pass** at the end
- **14-day context window** for deduplication
- **Aplicação Prática: must be broadly accessible.** Não pode ser nichado para devs/engenheiros — exemplos que qualquer leitor possa usar no dia a dia (análise de documentos, simulação de conversas, roteiro de apresentações). Se o conteúdo for técnico demais, troque. ✨ *Exemplo bom: "5 perguntas para fazer ao Fable 5 hoje" — qualquer pessoa testa. Exemplo ruim: "Proteja seu pipeline de supply chain" — só dev entende.*
- 📖 **Leia também:** `references/editorial-writing-guide.md` — guia de estrutura, tom e verificação de fontes para o editorial (hot-take). Consulte sempre ao redigir o editorial, especialmente para conferir a tese e os padrões de tom.
- 📖 **Leia também:** `references/special-edition-template.md` — template HTML completo para edições especiais: CSS, estrutura de páginas, anatomia da capa, e formato WhatsApp. Use ao criar edições extraordinárias sobre lançamentos de modelos ou eventos regulatórios.
- **Quando um tópico teve edição especial dedicada:** limite a cobertura a **1 artigo** na edição regular, apontando para o link da edição especial. O link deve ser o URL de produção (`https://iaf-newsletter.vercel.app/especial-{slug}`), não o caminho local.

## Filter Rules — AI-Only Content

**INCLUIR** apenas itens cujo TEMA CENTRAL é IA: modelos, frameworks, ferramentas, aplicações, regulação, startups, infraestrutura, pesquisa ML/DL, robótica com IA, ciência feita POR IA, agentes.

**EXCLUIR:** ciência sem IA, gadgets sem IA, "boas notícias" sem IA, menções de passagem.

**Regra de ouro:** a notícia PRECISA ser SOBRE inteligência artificial. Em dúvida, EXCLUA.