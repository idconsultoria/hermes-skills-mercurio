---
name: systematic-research
description: "Single-agent deep research via direct source URLs.

Load this skill when web_search is consistently unavailable (returns empty arrays for ALL queries after 2+ attempts) and you need thorough research without multi-agent dispatch. Uses domain knowledge to identify authoritative source URLs, batch parallel web_extract calls, handle blocked/404 pages, and page through large truncated encyclopedia-style articles. Produces cited, structured reports with source attribution. Complementary to deep-research (which covers multi-agent dispatch)."
category: research
type: Research
timestamp: 2026-08-09T05:08:04Z
---

# Systematic Single-Agent Research

Load this when web_search is unavailable (returns empty arrays for ALL queries after 2+ attempts) or when you need focused research on known-authority domains without multi-agent overhead.

## Pipeline

```
web_search fails × 2-4 (all empty)
        │
        ▼
  Step 1: Decompose into N sub-topics
        │
        ▼
  Step 2: Identify 2-5 known authority URLs per sub-topic
        │
        ▼
  Step 3: Parallel web_extract batches (max 5 URLs each)
        │
        ▼
  Step 4: Handle 404s/blocked — browser_navigate or alternatives
        │
        ▼
  Step 5: Read truncated full-article saves from cache
        │
        ▼
  Step 6: Deep-dive into specific sub-concepts found
        │
        ▼
  Step 7: Synthesize into structured report by sub-topic
```

## Step 1: Topic Decomposition

Split the research topic into 3-5 orthogonal sub-topics. Each sub-topic should be independently researchable from a different domain/authority.

**Example decomposition** (CFP IA financial planner research):
1. Psicologia do endividamento / vieses cognitivos
2. Mecânicas de gamificação em apps comportamentais
3. Estratégias de mudança de comportamento (Fogg, nudges)
4. UX em temas sensíveis (dívidas, dark patterns)

## Step 2: Authority URL Identification

Use known domain patterns. This is the critical step — you must know which URL patterns consistently work with `web_extract` for each topic class.

### Behavioral Economics & Cognitive Biases
```
behavioraleconomics.com/resources/mini-encyclopedia-of-be/concept-name/
  → Reliable encyclopedia entries for: loss-aversion, status-quo-bias,
    commitment, precommitment, framing-effect, choice-architecture,
    decision-fatigue, inertia, myopic-procrastination, present-bias,
    anchoring-heuristic, availability-heuristic, cognitive-dissonance,
    default-optionsetting, zero-price-effect

behavioraleconomics.com/nudge-action-overcoming-decision-inertia-in-financial-planning-tools/
  → Research article on financial decision support with data
```

### Gamification & Product Behavior
```
blog.duolingo.com/how-duolingo-streak-builds-habit/
  → Streak mechanics, loss aversion, retention data (+1.7%, 3.6× completion)
blog.duolingo.com/friend-streak/
  → Social gamification, +22% daily lesson completion
blog.duolingo.com/sticking-with-it-tips-for-staying-motivated/
  → Motivation features overview
```

### Behavior Models & Nudge Theory
```
behaviormodel.org
  → Fogg Behavior Model B=MAP (single page, no deep links)
en.wikipedia.org/wiki/Nudge_theory
  → Comprehensive nudge theory with research context
```

### Overview Concepts (Wikipedia — reliable scraping)
```python
en.wikipedia.org/wiki/Gamification
en.wikipedia.org/wiki/Behavioral_economics
en.wikipedia.org/wiki/Time_preference
en.wikipedia.org/wiki/Nudge_theory
```

### Brazilian Politics & Election Research (validado 06/08/2026)
Quando os subagentes do deep-research timeoutam e o tema é política brasileira (eleições, candidatos, governos), estes padrões de URL direta funcionaram de forma confiável via `web_extract`:

```python
# Biografias e instituições — Wikipédia pt
pt.wikipedia.org/wiki/<Nome>                                   # Lula, Flávio_Bolsonaro, Romeu_Zema...
pt.wikipedia.org/wiki/Governo_Lula_(2003%E2%80%932011)        # períodos de governo têm página própria
pt.wikipedia.org/wiki/Governo_Lula_(2023%E2%80%932026)
pt.wikipedia.org/wiki/Gest%C3%A3o_Ronaldo_Caiado_no_governo_de_Goi%C3%A1s
pt.wikipedia.org/wiki/Campanha_presidencial_de_Fl%C3%A1vio_Bolsonaro_em_2026
pt.wikipedia.org/wiki/Partido_Miss%C3%A3o                     # partidos: filiados, bancada, ideologia
# Nota: título pode ter sufixo de desambiguação — tente sem sufixo primeiro (Renan_Santos, não Renan_Santos_(político))

# Imprensa — G1 eleições (funciona bem com web_extract)
g1.globo.com/politica/eleicoes/2026/noticia/<ano>/<mes>/<dia>/<slug>.ghtml

# Pesquisas eleitorais — Gazeta do Povo publica tabelas COMPLETAS
# (espontâneo, estimulado, 2º turno, rejeição, conhece-e-votaria) em texto plano
gazetadopovo.com.br/eleicoes/2026/pesquisa-eleitoral-2026/<instituto>-presidente-<mes>-2026/
```

**Atenção:** `web_extract` falha intermitentemente com `document_antibot` em pt.wikipedia — use o bypass `action=raw` (Step 4b) ou a página de campanha/gestão dedicada, que costuma passar quando a biografia falha.

### Propostas comerciais de consultoria (validado 14/08/2026)
Tabela com 20 fontes verificadas (RAIN Group, Win Without Pitching/Blair Enns, NetSuite, HubSpot, The Proposal Lab, Paperbell, Slideworks, Proposify×2, Mike Monteiro, Qwilr, Better Proposals×2, Rock Content/BR, Stipleit, Poesius, Forbes, Responsive) com URLs, datas, confiabilidade e pontos-chave → `references/propostas-comerciais-consultoria-fontes.md`. Inclui os 7 princípios de consenso (proposta = conclusão da venda consultiva; problema→impacto→solução→resultado; VTL; prova social; escopo anti-creep; condições comerciais + validade 14–30 dias; follow-up 2×), os DADOS DE CONVERSÃO citáveis (tabela de preços +35,8%; 3+ stakeholders → 1,9×; 24h pós-reunião; 50% decididas em 24h; 37% falta de fit; 66% personalização; 93% apelo visual) e o registro dos bloqueios (Medium/Cloudflare, Google CAPTCHA, Bing off-topic, PandaDoc/Vercel, WWP só abre no browser).

## Step 2b: Mineração de fatos de páginas grandes (extract_facts)

Páginas da Wikipédia de governos/campanhas têm 100K–880K chars — NUNCA traga isso ao contexto. Depois do `web_extract` truncado salvar o full text em cache, mine com `execute_code`:

```python
import re
def extract_facts(path, keywords, max_chars=9000):
    text = open(path, encoding='utf-8').read()
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)   # remove links markdown, mantém texto
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(l for l in lines if any(k.lower() in l.lower() for k in keywords))[:max_chars]
```

- Chame com keywords por área: `['PIB','inflação','Bolsa Família','aprovação']` para economia, `['rachadinha','Queiroz','Coaf']` para escândalos, `['Ideb','segurança','homicídio']` para gestão estadual.
- Retorna só as linhas com números verificáveis + contexto — alimenta diretamente capítulos de relatório sem re-pesquisa.
- **Produza notas no formato "15+ fatos numerados cada um com URL" por sujeito** (padrão dos arquivos `samara-martins.md`, `edmilson-costa.md`, `hertz-dias.md` desta sessão) — é o formato que sustenta capítulos de relatório de 10+ páginas.

**Fallback quando deep-research timeouta:** NÃO retente subagentes — o caminho de recuperação é exatamente este skill: `web_extract` direto nas URLs conhecidas + extract_facts. Levou ~10 min para reconstruir 5 perfis que 3 subagentes não terminaram em 600s.

### UX / Design
```
nngroup.com  → Use specific article URLs. 404 common — verify first
medium.com   → Blocks scraping — do NOT rely on. Skip or use browser.
```

## Step 3: Parallel web_extract

Batch all independent URLs in a single call. The runtime executes them concurrently.

```
Call 1: URLs for sub-topic A (e.g., 3 behavioral economics articles)
Call 2: URLs for sub-topic B (e.g., 3 Duolingo blog posts)
Call 3: URLs for sub-topic C (e.g., 2 Wikipedia + behaviorModel)
```

**Limits:**
- Max 5 URLs per web_extract call
- Max ~50K chars per page before truncation
- Subsequent calls can be made immediately after (no serial dependency)

## Step 4: Handle Failures

| Failure Pattern | Handling |
|----------------|----------|
| 404 on page | Try `browser_navigate` to the same URL. If still 404, find alternative source. |
| Medium article | Skip — Medium blocks scraping AND the real browser (Cloudflare "Attention Required"). Wayback often has NO captures. Find equivalent content elsewhere, or cite the author's book/product page (verifiable URL) and note the original is offline. Never fabricate a URL. |
| NNGroup article | Try with and without trailing slash; verify first via browser if critical |
| Anti-bot page (Wikipedia) | Do NOT skip — use the `action=raw` curl bypass (Step 4b below) |
| Anti-bot page (other) | Do NOT skip yet — try `browser_navigate` first. Some sites (e.g. winwithoutpitching.com) block headless fetch engines but serve the real browser fine. Only accept the gap after the browser also fails. |
| Empty response | Try `browser_navigate(url)` as fallback |
| Google search | CAPTCHA "sorry" page (browser shows IP address + "Why did this happen?") — abandon immediately, do NOT insist |
| Bing via browser | Can return semantically-mis-tokenized garbage (query "RAIN Group proposal" → rain/weather results) AND, under bot detection, render ZERO organic results (snapshot shows only header/nav — validated 15/08/2026). Check the snapshot for result links; if none or off-topic, abandon, don't page through |
| DuckDuckGo / curl to search engines | `html.duckduckgo.com` blocked by web_extract fetch engines; `lite.duckduckgo.com` returns http:000 from curl and `mojeek.com` hits document_antibot (validated 15/08/2026). Don't burn time here — the direct-URL pipeline below is the reliable path |
| HubSpot/CMS blog (e.g. blog.hubspot.com, rainsalestraining.com) | web_extract may return only a 'Loading page…' JS shell — NOT dead. The real browser renders these fine. Try `browser_navigate` before abandoning (validated 14/08/2026). |
| Vercel Security Checkpoint / strict anti-bot (e.g. pandadoc.com blog) | Browser ALSO blocked (empty page, no elements). Skip and find an alternative source covering the same stat — never fabricate the data. |
| Cloudflare blocks web_extract AND browser (e.g. grandviewresearch.com report pages) | DON'T give up — run `web_search("<domain> <topic> market size USD billion")`: the headline number often appears in the official page's own snippet (validated 15/08/2026: GVR food safety testing US$ 26.2B/2025 pulled this way). Cite the number, note the page itself was Cloudflare-blocked, keep confidence ALTA for origin. |
| Semantic Scholar API | 429 sem chave de API — não insista, não vale retry em loop; troque para OpenAlex (sem auth) — validado 15/08/2026 |
| PMC (pmc.ncbi.nlm.nih.gov) | reCAPTCHA bloqueia web_extract — baixe o fullTextXML via Europe PMC (`/rest/PMC<ID>/fullTextXML`) — validado 15/08/2026 |

### Search-engine fallback ladder (validated 14/08/2026)

web_search is flaky, not just binary: it can return results for some queries in a batch and empty arrays for the rest, then go fully empty. The ladder that worked:

```
1. web_search retry (2-4 queries, mixed) → if ≥2 consecutive empty batches, stop
2. Bing via browser → relevance-check results; usually garbage, abandon quickly
3. GO DIRECT: domain knowledge → known authority URLs → web_extract batches
4. web_extract blocked on a site → browser_navigate same URL (browser passes where fetch fails)
5. Domain dead / no captures → cite verifiable product/book page + flag limitation in report
```

Steps 3-5 are the productive path; steps 1-2 are quick probes, not the plan.

### Pesquisa de mercado — Brasil (validado 15/08/2026)

Padrões que funcionaram para research de TAM/mercado com foco no Brasil (caso: mercado de análise laboratorial de alimentos):

- **web_search em português frequentemente retorna lixo** (tokenização: "preço análise resíduos agrotóxicos" → dicionários, lojas, mapas). Padrão que funciona: números de mercado SEMPRE em inglês (`<topic> market size USD billion 2024`); dados oficiais BR via URLs diretas de domínios conhecidos (gov.br, in.gov.br, anvisalegis.datalegis.net).
- **gov.br (MAPA/Inmetro):** web_extract funciona na maioria das páginas. Links de card às vezes NÃO navegam com browser_click (a página fica a mesma) — extrair href via browser_console `Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('<termo>')).map(a => a.href)` e navegar direto.
- **Regulamento brasileiro (Anvisa):** textos de IN/RDC via AnvisaLegis com URL pattern `anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&tipo=INM&numeroAto=<00000160>&seqAto=000&valorAno=<2022>&orgao=ANVISA/MS` (tipo=RDC também funciona). Achei assim que a "IN 160/2022" é da ANVISA (LMT de contaminantes), não do MAPA — sempre confirmar o órgão emitente.
- **Sem TAM oficial brasileiro para a maioria dos nichos** — o padrão é: achar o número país-específico em relatório (ex.: MarketsandMarkets tem páginas `.../Market-Reports/geography/<market>/Brazil`), senão estimar por share de PIB (~2,1–2,5%) e MARCAR como estimativa BAIXA, nunca como dado.
- **Preços de serviços laboratoriais BR não são publicados** (tabelas privadas raramente públicas; órgãos como Instituto Biológico/SP podem estar fora do ar) — usar faixa internacional citável e declarar a lacuna.
- Mapa de fontes validado p/ mercado de análise laboratorial de alimentos (números globais e BR, MAPA/Inmetro/Anvisa, PARA/PNCRC, players, preços) → `references/mercado-analise-laboratorial-alimentos.md`.

### Busca interna de sites de notícia — padrão `?s=` (validado 15/08/2026)

Quando web_search retorna lixo (resultados off-topic) e você já conhece os veículos relevantes, a busca interna do próprio site é o atalho mais produtivo: quase toda imprensa BR roda WordPress e `https://<site>/?s=<termo>` **extrai limpa via web_extract**, com título, data, autor e descrição no HTML:

- **AgFeed** (`agfeed.com.br/?s=<termo>`) — melhor cobertura de agronegócio/negócios BR; lista resultados com data (dd/mm/aaaa) no próprio HTML.
- **NeoFeed** (`neofeed.com.br/?s=<termo>`) — tag page `neofeed.com.br/noticias-sobre/<empresa>/` lista todos os artigos sobre uma empresa (ex.: /noticias-sobre/biotrop/).
- **Startupi** (`startupi.com.br/?s=<termo>`) — rodadas e investimento em startups BR.
- **Não funciona (não perca tempo):** Globo Rural (busca é JS — extract volta vazio), InfoMoney (JS), Exame (`/busca/` → 404), Forbes BR (antibot). WordPress busca por palavra-chave — use `?s=superbac` e `?s=simbiose` separados, não `?s=superbac+receita` (multi-termo pode retornar vazio).

Fluxo validado: (1) web_extract na lista de resultados do `?s=`; (2) web_extract nos 2–4 artigos principais (máx. 5 URLs por call); (3) artigo truncado no meio → ler o arquivo cache completo (`Full text saved to: /opt/data/cache/web/<dominio>-<hash>.md`) com read_file offset/limit — é onde ficam os números-chave (ex.: receita da Biotrop 2021 estava no meio do artigo da NeoFeed); (4) **conflito entre artigos** (ex.: Biotrop 2023 = R$ 618 mi em 03/2024 vs R$ 550 mi em retrospectiva de 07/2025 vs R$ 650 mi dito pelo CEO em 11/2023) → preferir a afirmação contemporânea ao fato e reportar o conflito explicitamente no relatório; (5) números com declaração de CEO/fundador = confiança MÉDIA (não auditado), números de balanço/veículo = ALTA.

### APIs acadêmicas sem auth (validado 15/08/2026)

Quando o tema é acadêmico/científico e Semantic Scholar responde 429, use **OpenAlex** como fallback nº 1 (sem auth, rate limits generosos):

```bash
curl -s 'https://api.openalex.org/works?search=valuation%20biotechnology%20rNPV&per-page=5&select=display_name,publication_year,cited_by_count,doi'
curl -s 'https://api.openalex.org/works?filter=title.search:<term>&per-page=5&select=display_name,publication_year,cited_by_count,doi'
curl -s 'https://api.openalex.org/works/doi:<doi>?select=display_name,publication_year,cited_by_count,abstract_inverted_index'
```

- `abstract_inverted_index` é dict `{palavra: [posições]}` — reconstruir o abstract ordenando pelas posições.
- **Europe PMC fullTextXML** contorna o reCAPTCHA do PMC: `curl -s 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC<ID>/fullTextXML' -o paper.xml` → parse com regex de `<table-wrap>` (tabelas de dados, ex.: probabilidades por fase clínica) e frases com números.
- **NCBI eutils** confirma PMID/PMC/DOI: `esearch.fcgi?db=pmc&term=<q>&retmode=json` + `esummary.fcgi?db=pubmed&id=<id>&retmode=json`.
- **GitHub API** para descoberta de repos: `https://api.github.com/search/repositories?q=<q>&sort=stars&order=desc&per_page=5` — responde rápido e sem rate-limit para volumes moderados (8 queries em ~5s).
- Receita completa com comandos testados → `references/academic-api-fallbacks.md`.

**Subagentes timeout → live transcripts.** Cada subagente do deep-research grava um log append-only em `/opt/data/cache/delegation/live/<delegation_id>/task-<N>.log` com o trace completo de tools (resultados de web_extract às vezes inteiros, caminhos de cache `/opt/data/cache/web/*.md`, outputs de execute_code). Ler com read_file ANTES de caçar no state.db — é a fonte mais rápida de achados parciais e mostra exatamente onde o agente parou (validado 15/08/2026: 3 subagentes timeout → 100+ achados recuperados dos logs em 2 leituras).

### Blog-index mining for article slugs

When a blog index page extracts successfully (can be 200K+ chars, saved to cache), grep the cached file for your topic keywords to discover exact article URLs — no search engine needed:

```bash
search_files(pattern="proposal", path="/opt/data/cache/web/raingroup.com-*.md", output_mode="content")
```

Returns matching lines WITH the `[Read More](url)` links — extract the real article slugs, then web_extract the top 2-3 posts directly. This turned one RAIN Group blog listing into three cited articles in one pass.

**Alternative when the listing only renders in the real browser** (HubSpot/CMS blogs often return just a 'Loading page…' shell to web_extract): navigate the browser to the site's own blog/search page (e.g. `site.com/blog?search=keyword`), then extract exact hrefs with browser_console JS:

```js
Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('TITLE_KEYWORD')).map(a => a.href)
```

Then web_extract the real article URLs directly. Validated 14/08/2026 on RAIN Group: the guessed slug (`/blog/how-to-write-a-winning-sales-proposal`) 404'd, but the console-extracted real slug (`/blog/how-to-write-a-sales-proposal`) extracted cleanly. The site's own blog listing is its index — slug-guessing is the slow path; console-extraction of hrefs is the fast one.

## Step 4b: Wikipedia Anti-Bot Bypass (`action=raw`)

`web_extract` frequently fails on Wikipedia with `Internal Server Error: Failed to scrape ... (document_antibot)` — on BOTH the desktop and mobile domains. Do not accept the gap; fetch the raw wikitext directly:

```bash
curl -s -A "Mozilla/5.0" "https://pt.wikipedia.org/w/index.php?title=<Page_Name>&action=raw" > /tmp/page.txt
```

- Spaces → underscores; URL-encode accented chars (`Candidato_Mart%C3%ADn` style).
- Returns the FULL wikitext: infobox (facts + their cited refs), history sections, election/result tables — often more verifiable detail than the rendered page.
- Parse with a short python heredoc: list section headers with `re.findall(r'^==+ .* ==+$', t, re.M)`, then slice from a header to the next.
- Works across language editions (pt/en/es/de/fr...). The `-A "Mozilla/5.0"` UA matters; plain curl sometimes gets blocked.
- If `action=raw` is also blocked, retry the rendered page via `web_extract` on the mobile domain `<lang>.m.wikipedia.org` — it intermittently passes when the desktop domain fails.

Full tested recipe (exact commands, wikitext parsing, discrepancy case study, dossier skeleton) → `references/wikipedia-action-raw-bypass.md`.

## Step 4c: Wayback Machine para URLs oficiais mortas

Quando uma URL oficial (blog da empresa, página do autor, ferramenta) dá 404 ao vivo, antes de desistir de citá-la:

```bash
# 1. Verificar se existe snapshot arquivado (responde JSON; {} = sem captura)
curl -s -m 20 "http://archive.org/wayback/available?url=<dominio>/<caminho>"

# 2. Descobrir URLs arquivadas por palavra-chave (CDX API + filtro regex)
curl -s -m 25 "http://web.archive.org/cdx/search/cdx?url=<dominio>/<prefixo>*&filter=original:.*<keyword>.*&limit=15&collapse=urlkey&fl=original,timestamp&output=json"
```

- Regra: se `archived_snapshots` vier vazio e o CDX não achar nada, citar a fonte canônica (livro do autor, página oficial viva da ferramenta) e MARCAR no relatório que a URL original está fora do ar — nunca fabricar URL nem citar URL morta como verificada.
- Validado 15/08/2026: `salesforce.com/blog/v2mom/` e `eosworldwide.com/blog/destination-postcard` → 404 ao vivo E sem snapshots; conteúdo citado via livros *Behind the Cloud* (Benioff) e *Traction* (Wickman), com confiança MEDIUM só quanto à URL.

## Step 5: Read Full Truncated Content

`web_extract` truncates at ~15KB. Encyclopedia-style pages (Wikipedia, BehavioralEconomics.com index) are routinely 50K-280K chars. The footer of the truncated output tells you where the full file was saved:

```
Full text saved to: /opt/data/cache/web/<domain>-<hash>.md
To read the omitted middle: read_file(path="...", offset=N, limit=200)
```

**Always read the omitted middle** for:
- Behavioral economics concept pages
- Wikipedia articles
- Any page that seems to stop mid-content

**Reference-URL mining:** the saved full text embeds the page's footnote/reference list at the bottom. Grep the cache file for news-domain patterns to discover primary-source URLs for the next extraction wave:

```bash
search_files(pattern="g1.globo|folha.uol|poder360|cnnbrasil|estadao", path="<cache-file>.md", output_mode="content")
```

This is how you go from an encyclopedia overview to the actual news articles, official party sites, and court documents the article cites — no web_search needed.

## Step 6: Deep Dive on Specific Concepts

After the first pass, you'll find cross-references to specific sub-concepts:

> "Status quo bias is consistent with loss aversion"
> "Loss aversion has been used to explain the endowment effect"

Follow these cross-references with a second wave of focused URL requests:
```
First pass: concept index page
       │
       ▼
       Found: links to loss-aversion, endowment-effect
       │
       ▼
       Second wave: web_extract to those specific URLs
```

Add a third wave only if the topic demands it and time permits.

## Step 7: Synthesize Structured Report

Organize final report by sub-topic, not by source. Each section should include:
- **Concept** named and defined
- **Source** cited (URL is fine for internal docs)
- **Data/statistics** with numbers where available
- **Implication** for your current project
- **Reference list** at the end

**Format preference** (Brazilian Portuguese audience): structured markdown with tables for comparative data, bullet points for lists, section headers for clarity. Minimize prose blocks.

**Machine-validated JSON variant** (subagent research tasks): parent agents sometimes require the final report as a single JSON object matching a schema (e.g. `descobrimentos[]` with `titulo/fonte/url/tipo/conteudo/confiabilidade` + `sintese`), with NO prose outside the JSON. Build it with `write_file` (auto-lints JSON) rather than string-concatenating inside `execute_code` — inline JSON assembly produced a SyntaxError this session; writing the file directly and printing it worked first try. **Validated alternative:** build a Python dict and emit with `json.dumps(report, ensure_ascii=False)` from `execute_code`, asserting the schema keys and enum values (e.g. `confiabilidade in ALTA/MÉDIA/BAIXA`, `url.startswith('http')`) BEFORE printing — a self-check that catches schema drift before submission (worked 14/08/2026 with 12 findings). If the task also demands a "## Descoberta N — ..." markdown report, embed the formatted header (Fonte, Data, Tipo, Confiabilidade) at the top of each finding's `conteudo` so both contracts are satisfied. Cite ONLY URLs actually fetched/verified this session; when a page lacks a date, write "sem data explícita" instead of guessing; flag attribution errors found during research (e.g. task said "Blaise Brosnan" for Win Without Pitching — founder is Blair Enns).

**Cross-check numeric discrepancies:** Wikipedia bios routinely carry wrong numbers (e.g. a politician's own article copying the result of a DIFFERENT election year). When sources disagree: (1) prefer the official table — party site, TSE/court data, government portal — over a biography page; (2) flag the discrepancy explicitly in the report ("fonte A diz X, tabela oficial do partido diz Y") instead of silently picking one. Never present a disputed number as settled without noting the conflict.

**Person/candidate dossiers** (political research): structure per person as — perfil curto → N fatos numerados cada um com URL → história da organização → vice/companheiros de chapa → contexto eleitoral → riscos → seção de avaliação honesta (ex.: "sem experiência em gestão pública", com o que a qualifica de fato). For dossiê-style tasks with multiple subjects, one file per subject, same skeleton.

## When NOT to Use This Pattern

- When web_search IS working — use it as the primary tool, web_extract for known URLs
- When you need multi-domain exploration (web + GitHub + news + academic) — use `deep-research` skill with delegate_task
- When the topic has NO known authority URLs — use web_search to discover them first
- When the single known URL for a concept is Medium.com — find an alternative source

## Comparison with deep-research Skill

| Aspect | systematic-research (this) | deep-research |
|--------|---------------------------|---------------|
| Architecture | Single-agent, parallel web_extract | Multi-agent via delegate_task |
| Best when | web_search is down, known sources exist | Exploratory research, web_search works |
| Concurrency | 5 parallel URL fetches | 3 parallel subagents |
| Reliability | High (simple HTTP) | Medium (subagent timeout risk) |
| Coverage | Focused (known domains) | Broad (multiple channels) |
| Time | 10-30 min | 20-60+ min |
