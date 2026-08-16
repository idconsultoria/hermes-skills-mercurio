# Market sizing — blocked-sites playbook & data bank (tested ago/2026)

From the wastewater-treatment/bioaumentação valuation research session (15/08/2026).
Full deliverable: `/opt/data/mercado_tratamento_efluentes_bioaumentacao.md`.

## 1. Source access matrix (tested ago/2026)

**Extractable via `web_extract` (clean pages, no anti-bot):**
- `precedenceresearch.com` — full report pages (market size, segments, regional notes, "Last Updated" date)
- `mordorintelligence.com/pt/industry-reports/<topic>-market` — PT-localized global pages extract well (EN pages sometimes 404 — always try the PT slug)
- `marketsandmarkets.com` — extractable (note: page meta may say old "Report Code Dec 2021" while body says "Updated on: Sept 2025")
- `marketintelo.com` — extractable
- `metatechinsights.com/pt/industry-insights/...` — extractable (has PHP warnings, ignore)
- `prnewswire.com` — extractable (older report announcements, useful historical baselines)
- `exame.com`, `noticias.r7.com` — extractable
- gov.br sites (ibama noticias) — works via browser; ibama.gov.br legacy root is JS-empty
- ANA Conjuntura 2021 survives at `relatorio-conjuntura-ana-2021.webflow.io/capitulos/usos-da-agua` — the old gov.br ANA URLs (conjuntura, atlas-esgotos) were removed in the gov.br migration; webflow mirror is the stable copy

**Blocked (Cloudflare "Just a moment..." / 403):**
- `grandviewresearch.com` — Cloudflare, blocks web_extract AND browser_navigate AND r.jina.ai
- `fortunebusinessinsights.com` — Cloudflare (same)
- `cetesb.sp.gov.br` — 403 even via browser (use press/secondary coverage instead)
- 404 traps (don't retry): Mordor `brazil-*-market` / `global-industrial-wastewater-treatment-*` slugs; TechSci `brazil-*-market`; verifiedmarketresearch `brazil-*` pages; `gov.br/ana/.../conjuntura-dos-recursos-hidricos`, `gov.br/ana/.../atlas-esgotos`

**Search engine state (ago/2026):** web_search AND Bing RSS AND DuckDuckGo HTML all returned degraded word-matching garbage for many queries (dictionaries, Mercado Libre, baseball stats, ANA = All Nippon Airways). Not a per-query problem — backend-wide. Direct-URL extraction won.

## 2. Fallback citation recipes

1. **Snippet citation** (Cloudflare-blocked page): number from the search-result snippet + page URL + label "MÉDIA — via snippet". Worked: GVR industrial water treatment USD 46.1B (2024); FBI South America water & wastewater USD 12.73B (2025, 3.40% of global); FBI bioremediation USD 11.91B (2026).
2. **Third-party verbatim quote**: when a vendor page quotes a research firm (e.g., trevisystems.com/market quoting FBI "USD 19.06 billion in 2024"), cite the quoting page AND the original report URL; label MÉDIA.
3. **Triangulated country estimate**: regional market × segment share × country share, explicitly labeled "estimativa própria — confiança BAIXA". Example: Brasil bioaumentação ≈ LatAm US$148M (8,2% de US$1,8B globais) × 40–50% ≈ US$60–75M/ano. Never present as sourced.
4. **Bing RSS**: `curl -s "https://www.bing.com/search?format=rss&q=<urlencoded>&count=10"` parses with `xml.etree` (item/title/link/description). Bing HTML regex is brittle — don't bother.

## 3. Data bank — tratamento de efluentes industriais & bioaumentação

### Mercado global — tratamento de efluentes industriais
- **US$ 19,06 bi (2024) → 20,01 bi (2025) → 28,95 bi (2032), CAGR 5,4%** — Fortune Business Insights, via trevisystems.com/market (página FBI bloqueada). Confiança MÉDIA.
- **US$ 18,28 bi (2024) / 19,41 bi (2025) / 20,63 bi (2026) → 34,11 bi (2034), CAGR 6,44%** — Precedence Research (atualizado 17/11/2025). **"Biological treatment" = maior segmento por tecnologia em 2024.** Confiança ALTA. URL: precedenceresearch.com/industrial-wastewater-treatment-market
- Mordor (PT): tecnologias água/águas residuais US$ 65,15 bi (2025) → 92,58 bi (2031), CAGR 6,03%; municipal 57,62% (2025) → industrial+outros ≈ 42%; tratamento biológico CAGR 7,04%. ALTA.
- MarketsandMarkets: químicos p/ efluentes industriais US$ 12,8 bi (2021) → 16,6 bi (2026), CAGR 5,3%. ALTA.
- GVR: tratamento de água industrial US$ 46,1 bi (2024) → ~71,6 bi (2033). MÉDIA (snippet).

### Brasil / América do Sul
- FBI: América do Sul água+efluentes **US$ 12,73 bi (2025) = 3,40% do global (US$ 372,39 bi)**, 13,66 bi (2026). MÉDIA (snippet).
- Histórico Brasil: mercado de ETEs (municipal+industrial) **US$ 1,72 bi (2012)**, municipal dominante — PRNewswire/Reportlinker (jan/2014). MÉDIA (desatualizado).
- **Estimativa (própria): Brasil efluentes industriais ≈ US$ 1,2–2,7 bi/ano** (América do Sul × ~42% industrial × 40–50% Brasil). BAIXA.
- Saneamento (driver regulatório): **R$ 46,3 bi/ano necessários 2023–2033** (total ~R$ 509 bi) vs média investida R$ 20,9 bi/ano; universalização só em 2070 no ritmo atual — Instituto Trata Brasil/SNIS 2022 via Exame (15/07/2024). ALTA.
- ANA Conjuntura 2021: retirada total 1.947 m³/s (2020) → 2.770 m³/s (2040); irrigação ~50%, urbano ~25%. ALTA.
- Atlas Esgotos (ANA 2017, via CEBDS): ~110 mil km de rios em classes 3/4 (DBO₅>5 mg/L). ALTA.
- Reúso de efluentes tratados: 50,5 bi L/ano (12,3% do potencial). ALTA.
- Caso de capex: AB Brasil R$ 150 mi em ETE (ago/2022). ALTA (caso único).

### Nicho bioaumentação / biorremediação
- **Bioaumentação global: US$ 1,8 bi (2025) → 3,4 bi (2034), CAGR 8,2%** — MarketIntelo (11/06/2026); consórcios microbianos 38,5%; segmento efluentes CAGR 9,1%; **LatAm 8,2% ≈ US$ 148 mi (2025), CAGR 8,9%** (Brasil/México/Chile citados como motores). MÉDIA-ALTA.
- **Estimativa (própria): Brasil bioaumentação ≈ US$ 60–75 mi/ano (R$ ~300–390 mi)** — nenhuma fonte pública Brasil-específica encontrada. BAIXA.
- Biorremediação (guarda-chuva): US$ 16,52 bi (2024) → 50,0 bi (2035), CAGR 10,6%, **bioaumentação = segmento de crescimento mais rápido** — MetaTech Insights PT (jun/2025). MÉDIA.
- FBI biorremediação: US$ 11,91 bi (2026) → 24,25 bi (2034), CAGR 9,30%. MÉDIA (snippet).
- Corroboração histórica: BCC (2018) — bioaumentação ≈ 1/9 do mercado de biorremediação. BAIXA.

### Gasto regulatório / enforcement
- IBAMA: autos de infração >30 mil/ano (déc. 1990) → <16 mil/ano (recentes); LC 140/2011 transferiu licenciamento/fiscalização local a estados/municípios — R7 (07/08/2026). ALTA.
- IBAMA multas (estoque): R$ 29,1 bi voltaram a ser cobrados (anuladas no gov. anterior) — Midia Ninja (22/03/2023). MÉDIA.
- CETESB multas por caso: R$ 22,5 mi e R$ 15 mi (exemplos) — AmbScience. MÉDIA.
- Base legal: CONAMA 430/2011 (padrões de lançamento); licenciamento obrigatório em SP desde 1976; Marco Legal do Saneamento (Lei 14.026/2020): 99% água / 90% esgoto até 2033.

## 4. Sessão-referência
Relatório completo (formato: número principal / tabela dado|valor|fonte|data|confiança / nicho / fontes): `/opt/data/mercado_tratamento_efluentes_bioaumentacao.md`

## 5. Data bank — PLAYERS, TICKETS e CRESCIMENTO (sessão 15/08/2026, p/ SOM)
Relatório completo: `/opt/data/mercado_bioaumentacao_players_tickets_som.md`

### Players verificados (site extraído, ALTA)
- **Superbac** (Cotia-SP/biofábrica Mandaguari-PR): líder nacional em blends microbianos (efluentes, O&G, agro, papel/celulose, consumo). Trajetória: faturamento <R$ 20 mi até 2015 (est. CEO) → meta R$ 1 bi em 2022; plano 25% a.a.×10 anos; 50 mil L/24h; ~70 pesquisadores. Exame 21/10/2021 (URL no relatório). MÉDIA (autodeclarado; nota: artigo ambíguo R$100 mi vs US$100 mi em aportes).
- **MicroCiclo** (Natal-RN, UFRN, 2019/20): primeira biofábrica do NE; consórcios por seleção genômica; clientes Schulz/Tupy/Ciser/AES/Camanor; POCs desde 2022; fábrica operando 2026; patente INPI (UFRN). Pré-scale, receita não pública. BiotechTown 08/11/2022 + microciclo.com.br.
- **Nutrenzi** (Araçoiaba da Serra-SP): 25+ anos, produto microbiano customizado p/ efluentes/papel-celulose/odores.
- **Genetica Bioscience** (Chapecó-SC): razão social Genetica Tecnologias Ambientais, CNPJ 07.699.054/0001-36, fundada 10/11/2005; porte não verificado (cnpj.biz snippet + LinkedIn).
- **Biogenix** (RS), **Biotri** (Uberlândia-MG), **Aqua Viridi** (AM, microalgas): PMEs/startups, MÉDIA/BAIXA.
- **AmbScience** (SP): consultoria ambiental (áreas contaminadas, efluentes, licenciamento) — modelo consultoria pura.
- **Opersan** (SP): O&M águas/efluentes industriais; **R$ 120 mi (2022)**, 65 operações OnSite, ~1.000 clientes (2022), 6 unidades OffSite, fundo Pátria. Exame 09/02/2022 + opersan.com.br. **Derivação: ~R$ 1,8 mi/ano por operação OnSite; ticket médio R$ 120-180 mil/ano/cliente.**
- **Cetrel** (Camaçari-BA): efluentes/resíduos industriais + água industrial do polo (Braskem 63,7%); **JV Solví+Braskem (GRI+Emergencial+Cetrel) nasceu com R$ 750 mi faturamento e EV R$ 1,4 bi** (Exame Insight 13/06/2024) → múltiplo ~1,9× receita p/ player consolidado.
- **Biotecs** (RP-SP): engenharia/EPC de ETEIs; **Veolia WT**: presença global, modelos AOT; **Ramboll**: biorremediação em áreas contaminadas.

### Tickets (não há tabela pública no Brasil — B2B privado)
- **Ancla real da startup-alvo (contexto, não público):** 1º contrato R$ 122 mil / 16 parcelas de R$ 7.653,72 (~R$ 92 mil/ano recorrente); consultoria de bioprocessos em negociação R$ 120 mil.
- Faixas estimadas (BAIXA): bioaumentação R$ 50-250 mil/ano por ETE média; consultoria R$ 80-120 mil/projeto; O&M ~R$ 1,8 mi/ano/operação (derivação Opersan, MÉDIA).

### Casos de crescimento (análogos p/ SOM)
- **Gênica** (Piracicaba, 2015, bioinsumos agro): R$ 130 mi (2023) → R$ 230 mi (2024E, +70%); dobrou todos os anos desde 2019; EBITDA+ desde 2019; R$ 68 mi Série C Mitsubishi (<10%, 2024); ~R$ 150 mi levantados (R$ 100 mi dívida + R$ 50 mi equity). Brazil Journal 26/06/2024. **Melhor análogo de startup microbiana que escalou em ~9 anos — com capital.**
- **Biotrop**: vendida à Biobest por R$ 2,8 bi (2023, >11× EBITDA proj.); ~R$ 900 mi 2025. **Vittia**: IPO B3 2021; biológicos = 30% receita/50% lucro bruto (2023). **Nitro**: R$ 2,5 bi 2023 (R$ 1,3 bi insumos; biológicos >R$ 100 mi via Biocontrol). **Opersan**: 30+ anos p/ R$ 120 mi. **Superbac**: 20 anos p/ R$ 20 mi.
- **Recomendação SOM ano 5 (startup bioaumentação+consultoria):** conservador R$ 1,2-2,5 mi; base R$ 3-6 mi (1-1,7% do nicho R$ 300-390 mi); agressivo R$ 8-15 mi (exige capital R$ 20-50 mi + biofábrica/registro, padrão Gênica).

### Não localizados (declarar explicitamente em relatórios futuros)
- TecnoSulfato; Biopreservação (domínios não resolvem; buscadores degradados/bloqueados — Google CAPTCHA, Bing RSS e HTML garbage, DDG timeout).
- Tabela pública de preços/tickets de bioaumentação no Brasil; valores de contratos individuais.
