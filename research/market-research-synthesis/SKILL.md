---
name: market-research-synthesis
description: "Produce market analysis reports — personas, journeys, expectations, behavior.

Load this skill when conducting market research for Brazilian/LATAM markets where web research tools face comprehensive blocking. Produces structured reports covering buyer personas, customer journeys, expectations hierarchies, purchasing behavior, and retention/fidelization. Pivots to domain-knowledge synthesis with transparent caveats when web tools fail."
category: research
type: Research
timestamp: 2026-07-12T00:00:00Z
---

# Market Research Synthesis

Produce structured market analysis reports covering buyer personas, customer journey, expectations, purchase behavior, and retention. Designed for markets where web research tools may face comprehensive blocking.

## Trigger Conditions

Load this skill when:
- User asks for market research, persona analysis, customer journey mapping, or GTM research
- User asks about "perfil do aluno", "jornada do cliente", "comportamento de compra", "expectativas", "retenção e fidelização"
- The target market is Brazilian/LATAM (expect web research tools to fail)
- User wants a comprehensive report with data and strategic implications

## Output Structure

For comprehensive market analysis reports, cover these sections:

### 1. Personas (buyer/user profiles)
- 3-5 personas with demographic profiles, motivations, objections, willingness to pay, purchase behavior
- Percentage estimates of market share per persona
- Specific to the market/industry (e.g., technology courses, SaaS, consumer goods)

### 2. Customer Journey (antes, durante, depois)
- Pre-purchase phase: triggers, research duration, channels, friction points, drop-off rates
- During product/course: critical abandonment moments with rates, factors that reduce churn
- Post-purchase: what drives referrals, what creates detractors

### 3. Expectations Hierarchy
- Ranked attributes by persona (what they value most → least)
- Weight percentages where available
- Premium willingness-to-pay drivers (what makes them pay 30-60% more)

### 4. Purchase Behavior
- When they buy (time of day, day of week, payday cycles, seasonal peaks) with percentages
- Research-to-purchase timeline by price tier
- Objections by price band
- Urgency triggers that work in the target market

### 5. Retention & Fidelization
- What drives repurchase (weighted factors with percentages)
- What causes abandonment (reasons with percentages)
- Short/medium/long-term retention strategies
- Cross-sell/upsell conversion rates between product tiers

### 6. Strategic Implications
- Pricing recommendations by tier
- Launch timing strategy
- Retention hooks between products
- Specific to the user's project/product

## Research Methodology

### Primary Approach: Web Research

1. **Start with web_search** across multiple queries covering all research areas
2. **Extract from known sources** — government databases (INEP, ABED), industry associations, edtech company blogs, news sites
3. **Cross-validate** findings across sources

### Fallback: Domain Knowledge Synthesis (CRITICAL)

When web research tools fail — watch for the **triple-blockage pattern**:

| Signal | Meaning |
|--------|---------|
| `web_search` returns `{"data": {"web": []}}` for ALL queries | Backend issue, NOT "no results exist" |
| `web_extract` returns 404s or Cloudflare pages for most URLs | Anti-bot protection on target sites |
| `browser_navigate` triggers CAPTCHA/Cloudflare challenge | Browser-based search also blocked |

**Do NOT keep retrying.** When all three signals fire:

1. **Acknowledge the limitation** to the user
2. **Compile from domain knowledge** — use what you know about the market, citing known benchmarks, industry reports, and public data points
3. **Label data provenance clearly** — distinguish verified data from benchmarks/estimates
4. **Structure the output** exactly as if web research had succeeded — same sections, same level of detail
5. **Save as a well-formatted markdown file** for the user to review and validate
6. **Note in the methodology section** which sources are public/verified vs. domain estimates

### Brazil-Specific Challenges

Brazilian websites deploy aggressive anti-bot protection:
- **Cloudflare:** Nearly all Brazilian commercial blogs, news sites, and edtech portals use Cloudflare bot protection
- **CMS migration:** Many Brazilian content sites have restructured blogs, making old URLs return 404
- **Google/Bing CAPTCHAs:** Both search engines trigger CAPTCHA for automated access from cloud IPs
- **JavaScript requirements:** Most Brazilian sites require JS execution — raw curl fails

**Verified persistent sources** (Brazilian market, as of July 2026):
- INEP/MEC (gov.br) — Censo da Educação Superior: raw data available but requires JS for navigation
- ABED (abed.org.br) — Censo EAD.BR: often blocked but is the primary source for distance education data
- Brasscom — IT workforce deficit data: available through press releases and news coverage
- Hotmart, Eduzz, Sympla — transaction data: generally blocked, use second-hand citations from news articles
- **Wikipedia (pt.wikipedia.org)** — API via terminal works reliably for baseline statistics. Passos: (a) `curl -sL "https://pt.wikipedia.org/w/api.php?action=query&titles=TITLE&format=json&prop=extracts&exintro=1&explaintext=1" -o /tmp/wiki.json`, (b) `python3 -c "import json; d=json.load(open('/tmp/wiki.json')); pages=d['query']['pages']; [print(v.get('extract','')) for v in pages.values()]"`. Use para dados econômicos, demográficos, educacionais — sempre o primeiro passo antes de perseguir portais bloqueados.
- **Banco Central do Brasil (bcb.gov.br)** — JS-heavy frontend but static HTML structure accessible via curl. Use for economic indicators, Open Finance stats, and inflation data.
- **B2C fintech pricing pages** — B2C Brazilian fintech apps DO publish prices openly (e.g., organizze.com.br/planos). The "never publishes prices" rule applies to B2B enterprise SaaS only. Always try `/planos`, `/precos`, `/pricing` on consumer-facing apps before falling back to benchmarks.
- **CropLife Brasil / CropData** — primary source for the Brazilian agricultural bioinputs market (faturamento real em R$, área tratada, share por segmento/cultura/região). Site itself is JS-heavy, but its data is republished with full numbers by CNN Brasil, Globo Rural, Jornal do Comércio, R7, aRede — extract those articles instead. Also: Embrapa releases (FBN/inoculantes) via Pensar Agro/Plenário MT; ANPII Bio (inoculantes) via press/Instagram. Full verified dataset in `references/brazilian-agbio-inputs-market-data.md`.

See `references/brazilian-market-web-blockage.md` for the full blockage pattern, specific blocked sites, and tested workarounds.
See `references/brazilian-agricultural-saas-landscape.md` for a worked example of competitor analysis in the Brazilian ag SaaS vertical (July 2026), including verified URLs, alternative TLD patterns, and market gaps.
See `references/brazilian-fintech-personal-finance-landscape.md` for a worked example of market research in the Brazilian personal finance app vertical (July 2026), with competitor pricing data, Open Finance context, and market sizing.
See `references/brazilian-agbio-inputs-market-data.md` for verified TAM/CAGR data of the Brazilian & South American agricultural bioinputs market — CropLife CropData series, inoculantes/biofertilizantes/bioestimulantes/controle biológico, Mordor & MarketsandMarkets projections, with URLs, dates and confidence levels (Aug 2026). Use for valuations of ag-biotech startups.
See `references/tam-som-valuation-workflow.md` for the validated TAM/SAM/SOM sizing workflow (3 parallel subagents, grounded-citations ledger, SOM trajectory benchmarks, ticket derivation and scenario bands) — load when the deliverable feeds a valuation.
See `references/brasil-bioinsumos-company-trajectories.md` for company-level revenue benchmarks of Brazilian bioinput/biotech-agri players (Biotrop full year-by-year series 2021–2025, SuperBac, Simbiose, Koppert BR, Vittia, Satis, Nitro, Orígeo/Bunge-UPL, rodadas comparáveis, and year-5 SOM scenario bands) — every number with URL + date + confidence (Aug 2026). Use to calibrate revenue scenarios for ag-biotech startup valuations; pairs with `brazilian-agbio-inputs-market-data.md` (TAM side).

## Pitfalls

- **Don't fight the blockage.** If web_search + web_extract + browser all fail in the first 3-5 attempts, pivot to domain-knowledge synthesis immediately. Each retry costs 30-60 seconds with no ROI.
- **Search snippets survive Cloudflare.** When a key market-research page is bot-blocked (grandviewresearch.com, fortunebusinessinsights.com), the exact figures usually still appear in the search-result snippet itself. Quote the snippet's number, cite the page URL, and label the datum "MÉDIA — via snippet". Tested ago/2026: GVR "industrial water treatment USD 46.1B in 2024"; FBI "South America water & wastewater USD 12.73B in 2025, 3.40% of global demand". This rescued the two most important global numbers of the session.
- **Size a country niche by triangulation — and say so.** When no public figure exists for a country-level niche (ex.: bioaumentação no Brasil), derive an estimate from regional market × segment share × country share (ex.: LatAm US$148M × ~40–50% Brasil ≈ US$60–75M/yr) and mark it explicitly "estimativa própria — confiança BAIXA" in the deliverable. Never let a derived estimate masquerade as a sourced number; state in the report that no public Brazil-specific figure was found.
- **Bing RSS parses cleanly; Bing HTML does not.** `https://www.bing.com/search?format=rss&q=<query>&count=N` via curl + `xml.etree` beats regexing Bing HTML (regex broke on the page structure). Caveat: in ago/2026 both web_search and Bing/DDG returned degraded word-matching garbage (dictionaries, Mercado Libre, baseball stats) on many queries — for market-sizing data, direct-URL extraction to known report pages outperformed every search engine.
- **r.jina.ai does not bypass Cloudflare** (tested on GVR/FBI — returns the challenge page). Don't burn calls on it; use the snippet-citation pattern instead.
- **Mordor/TechSci country-specific pages mostly 404.** Mordor's working URL pattern is `mordorintelligence.com/pt/industry-reports/<topic>-market` (PT-localized global pages); `brazil-<topic>-market` variants 404. Country-level reports often don't exist — plan for global/LatAm numbers plus triangulation.
- **Tested source matrix + data bank:** see `references/market-sizing-blocked-sites-playbook.md` — which market-research sites extract cleanly vs are Cloudflare-blocked (tested ago/2026), fallback citation recipes, and the wastewater/bioaumentação market data bank (numbers + URLs + confidence) so a future valuation session does not redo the research.
- **Don't fabricate data.** When using domain knowledge, use phrases like "benchmarks typically show", "industry data suggests", "estimated at". Never present estimates as verified facts.
- **Don't skip the strategic implications section.** The user needs actionable recommendations for their specific project/product, not just raw market data.
- **Brazilian URLs are unstable.** Blog posts from 2022-2024 on Brazilian edtech sites have a high probability of 404. Prefer .gov.br sources and industry-wide reports over individual blog posts.
- **Language matters.** Research queries for Brazilian markets MUST be in Portuguese. English queries return sparse or irrelevant results for Brazil-specific data. But web_search tool may fail regardless of language — the issue is the backend, not the query.
- **Brazilian B2B SaaS never publishes prices.** Enterprise B2B SaaS companies universally use demo-based/consultative sales. "Planos", "Preços", and "Pricing" pages return 404 or redirect to "fale conosco". **EXCEPTION:** B2C fintech/consumer apps (Mobills, Organizze, etc.) DO publish transparent pricing. Distinguish the segment before spending time hunting — check if the product serves consumers (likely published) or enterprises (likely hidden).
- **Alternative TLDs often work when .com.br fails.** Many Brazilian companies use non-obvious domains: .app, .com (without .br), .agr.br. When the obvious .com.br returns errors or blocks, try alternative TLDs. LinkedIn company pages also reliably confirm existence and positioning even when the main site is fully down.
- **Brazilian acronyms collide across entities — validate before citing.** Same acronym often belongs to unrelated organizations: ABBI = "Associação Brasileira de Bioinovação" (bioeconomia), but abbi.com.br is the Associação Brasileira de Bancos Internacionais; "Spark" no agro = Spark Smarter Decisions (sparksmarterdecisions.com, blocked to bots) ≠ Spark Inteligência e Estratégia (sparkinteligencia.com.br, political consultancy in Fortaleza). Check the site's actual content/CNPJ before attributing data. Same trap applies to ABRAS, ABED, etc.
- **Market-size scope divergence between consultancies is normal — report both.** E.g., global agricultural inoculants: Mordor counts ~US$ 11–19 bi (broad, includes biocontrol/consortia) vs MarketsandMarkets ~US$ 1,7 bi (narrow). Trade-association revenue figures (e.g., CropLife CropData for Brazil) differ from consultancy projections and from narrow "registered products only" estimates (Mordor's regional sub-reports systematically understate Brazil). Flag the definition, never average them.
- **Mordor Intelligence regional sub-pages are a goldmine for LATAM agriculture.** URLs of the form mordorintelligence.com/industry-reports/<region>-<segment>-market (e.g., south-america-biofertilizers-market, brazil-biofertilizer-market, south-america-biostimulants-market, agricultural-inoculants-market) load cleanly via web_extract and give TAM + CAGR + players per country/region. Check "Page last updated" for freshness.
- **Subagents can `reset` the shared citations ledger (validado 15/08/2026).** When the parent uses grounded-citations and delegates research to parallel subagents, a subagent following the ledger skill's own "reset at task start" instruction wipes the parent's source ids (they share `$HERMES_HOME`; this happened in the BiotechSe session — the bioaugmentation agent's reset replaced the parent's TAM source ids mid-flight). Fix: give each subagent a dedicated ledger (`--ledger /path/child-N.json`) and explicitly forbid `reset` in their instructions. If clobbered anyway: re-`add` the parent sources (they get new ids), fix the draft's inline ids, re-run `render --replace-in` + `verify` — never hand-edit the Sources block.
- **No LaTeX / formatted math in user-facing deliverables (preferência do Gustavo, validada 15/08/2026).** Write calculations in plain text — "45 projetos por ano vezes 100 mil reais, cerca de 4,5 milhões por ano" — never equations, math notation, or LaTeX. Applies to all valuation/research report conversations.

## Direct-URL Extraction Technique (CRITICAL)

When `web_search` returns empty arrays but you have a list of target companies/URLs, **skip search entirely** and go directly to `web_extract` with the known URLs. This is consistently the most productive path:

1. Batch up to 5 competitor URLs in one `web_extract` call
2. For sites that fail in `web_extract` (anti-bot), fall back to `browser_navigate`
3. For sites that are fully down (404 on all pages), use LinkedIn company pages for positioning confirmation
4. When a site loads partially, use `read_file` with offset/limit on the cached copy to get the full content
5. **Mine `web_search` result batches before pivoting.** Even when the backend returns mostly garbage (calculators, foreign-language dictionaries, unrelated brands), each batch typically contains 1–3 REAL hits — in the bioaumentação session, brand-name queries surfaced Nutrenzi, Biogenix, Biotri, Aqua Viridi, Genetica Bioscience (via cnpj.biz snippet), Superbac/Exame articles and the Cetrel/Solví JV. Run 3–5 different phrasings of the same target (brand alone; brand + segment; brand + city) and harvest the real URLs; treat the noise as cost, not as "no results exist". This refines the "do not keep retrying" guidance above: give up only when ALL three blockage signals fire across several queries — not after the first garbage batch.
6. **WordPress search-URL pattern for niche Brazilian portals.** Portals like tratamentodeagua.com.br expose `?s=<term>` (search) and `?tag=<tag>` (tag archive) pages that extract cleanly via web_extract — e.g. `https://www.tratamentodeagua.com.br/?s=bioaumenta%C3%A7%C3%A3o` and `?tag=bioaumentacao` surfaced the only public bioaugmentation articles on the portal, plus a company directory (`/empresa/<slug>/`) listing dozens of sector players. Try `/?s=` and `/?tag=` on any niche portal whose internal search seems missing.
7. **Verify Brazilian companies via CNPJ lookups when their sites are down.** Sites like cnpj.biz (`https://cnpj.biz/<cnpj>`) expose razão social, founding date and segment. Extraction may be bot-blocked, but the search-result snippet itself carries the founding date/razão social — enough to confirm existence and age (worked for Genetica Bioscience: "Genetica Tecnologias Ambientais LTDA, CNPJ 07.699.054/0001-36, fundada 10/11/2005").

This approach yielded rich data for 5/7 competitors in one session even when `web_search` was completely non-functional across 10+ queries.

## Competitor Analysis Workflow (Brazilian Market)

When the task is competitor/market analysis for a Brazilian vertical:

1. **Map known players** from the user's brief — they usually name the top competitors
2. **Batch-extract competitor websites** via `web_extract` (5 URLs per call)
3. **Check segment: B2C vs B2B early.** Consumer fintech/apps likely publish prices on `/planos` or `/precos`. Enterprise B2B SaaS hides them behind demo walls. Distinguish before spending time hunting.
4. **Build a comparison matrix** early: features, pricing model, target audience, differentiators, scale metrics
5. **Identify pricing patterns**: If the segment is B2B, note consultative sales as market norm (and potential differentiator if the client adopts transparent pricing). If B2C, collect all published prices and identify the market range.
6. **Hunt for gaps**: focus on features NO competitor offers (checking site menus, FAQ, feature pages)
7. **Note exit signals**: competitors with dead websites, 404s across all pages, or empty social media are market exit signals — these are opportunities for the client
8. **Save as structured markdown** with tables for features, pricing, and a dedicated "gaps and opportunities" section

See `references/brazilian-agricultural-saas-landscape.md` for the full competitor data from the agricultural SaaS session (July 2026) as a reference template.
See `references/brazilian-fintech-personal-finance-landscape.md` for the fintech/personal-finance-app vertical (July 2026) with competitor pricing data and market sizing.
