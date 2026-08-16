# Mercado de análise laboratorial de alimentos — mapa de fontes validado (15/08/2026)

Pesquisa de TAM para valuation de startup de biotecnologia (análises cromatográficas HPLC/LC-MS, GC-MS para controle de qualidade na indústria de alimentos). Todas as URLs funcionaram via web_extract/browser na data indicada; números citados exatamente como reportados pelas fontes.

## Global — food safety testing (números centrais)

| Fonte | Número | URL | Notas |
|---|---|---|---|
| Mordor Intelligence | US$ 23,98B (2025) → US$ 37,13B (2031), CAGR 7,56% | mordorintelligence.com/industry-reports/food-safety-testing-market | web_extract OK. Dá share por tecnologia: cromatografia/espectrometria CAGR 8,53%; PCR 46,4% da receita 2025; patógenos 51,5% do share |
| Grand View Research | US$ 26,2B (2025) → US$ 48,0B (2033), CAGR 7,8% | grandviewresearch.com/industry-analysis/food-safety-testing-industry | Página bloqueada por Cloudflare (web_extract document_antibot + browser "Just a moment"); número obtido via snippet de web_search do próprio domínio (grandviewresearch.com/industry/food-safety-and-processing) |
| MarketsandMarkets | US$ 21,1B (2022) → US$ 31,1B (2027), CAGR 8,1% | marketsandmarkets.com/Market-Reports/food-safety-365.html | Report FB 3059, set/2022 |
| Market.us | US$ 28,4B (2025) → US$ 57,0B (2035), CAGR 7,2% | market.us/report/food-safety-testing-market/ | Agregadora; confiança MÉDIA |

## Global — subsegmentos e tecnologias

- Food pathogen testing: US$ 16,49B (2026) → US$ 23,90B (2031), CAGR 7,7% (M&M, abr/2026) — marketsandmarkets.com/food-testing-services-logistics-market-research-243.html (hub de relatórios Food Safety & TIC; web_extract OK)
- Mycotoxin testing: US$ 2,3B até 2029, CAGR 6,7% (M&M)
- Rapid food safety testing (global): US$ 19,65B (2025) → US$ 31,22B (2030), CAGR 9,7% (M&M)
- Food allergen testing: US$ 1,35B (2026) → US$ 1,89B (2031), CAGR 6,96% (Mordor)
- Feed testing: US$ 2,54B (2024) → US$ 4,04B (2029) (Mordor)
- HPLC: US$ 5,0B (2024) → US$ 7,0B (2030) (GVR, snippet); US$ 5,44B (2025) → US$ 5,62B (2026) (Mordor)
- Agricultural testing services: US$ 6,7B (2026) → US$ 8,7B (2036), CAGR 2,7% (Future Market Insights)
- Food traceability (driver): US$ 21,8B (2024) → US$ 38,5B (2029), CAGR 10,1% (BCC Research press release, 03/06/2025)
- Concentração: Eurofins/SGS/Intertek/ALS/Bureau Veritas ≈ 35–40% da receita de serviços de teste (Mordor, shelf-life testing services report)

## Brasil

- **Único número país-específico encontrado:** MarketsandMarkets "Brazil Rapid Food Safety Testing Market" — US$ 499,5M (2025) → US$ 735M (2030), CAGR 8,0% (Report FB 9547 BRA, jun/2026). URL: marketsandmarkets.com/Market-Reports/geography/rapid-food-safety-testing-market/Brazil — padrão de URL `.../geography/<market>/Brazil` vale para outros mercados M&M. Atenção: é subconjunto (tecnologias rápidas), não o total de food testing.
- **Sem TAM oficial brasileiro de análise de alimentos.** Estimativa por share de PIB (~2,1–2,5% do global) → US$ ~0,5–0,65B (2025); marcar BAIXA.
- **MAPA — rede oficial:** 6 Laboratórios Federais de Defesa Agropecuária (LFDAs). gov.br/agricultura/pt-br/assuntos/lfda
- **MAPA — credenciados por área:** gov.br/agricultura/pt-br/assuntos/defesa-agropecuaria/laboratorios-credenciados → "Consultar laboratórios credenciados" → páginas por área. Ex.: `.../produtos-de-origem-vegetal/residuos-e-contaminantes` = 5 labs p/ resíduos/contaminantes em vegetais (ITEP/PE, NSF Bioensaios/RS, Eurofins do Brasil/Indaiatuba-SP, Instituto Biológico/SP, Bioagri/SP — atual. 29/07/2026). Outras áreas: agrotoxicos-e-afins, produtos-de-origem-animal, sementes-e-mudas.
- **gov.br pitfall:** link "Laboratórios Credenciados" não navega com browser_click — extrair href via browser_console e navegar direto.
- **Credenciamento:** Portaria MAPA nº 747/2024 (novo regime desde 02/01/2025, por edital SDA); antes IN MAPA nº 57/2013. Portarias 819/2025 e 875/2025 alteram prazos.
- **Inmetro/Cgcre:** sem total consolidado citável em página; base pública RBLE em inmetro.gov.br/laboratorios/rble/ (via gov.br/inmetro/pt-br/assuntos/acreditacao-reconhecimento-bpl/organismos-acreditados).
- **Anvisa:** IN nº 160, de 01/07/2022 = limites máximos tolerados (LMT) de contaminantes em alimentos (junto com RDC nº 722/2022). Texto em anvisalegis.datalegis.net (pattern: tipo=INM&numeroAto=00000160&valorAno=2022&orgao=ANVISA/MS). **É ANVISA, não MAPA.**

## Programas oficiais de monitoramento (drivers)

- **PNCRC/MAPA** (origem animal): artigo Foods/MDPI 2023 "The Wind of Change in Brazilian Monitoring" (PMC10222520) — via Europe PMC fullTextXML (`curl ebi.ac.uk/europepmc/webservices/rest/PMC10222520/fullTextXML`): 3.793 amostras bovinas em 2021, 0,26% não conformes; métodos oficiais = UHPLC-MS/MS.
- **PARA/Anvisa** (origem vegetal): revisão "Resíduos de Agrotóxicos em Alimentos no Brasil (2018 a 2025)" (Revista ARACÊ v.7 n.10 2025, PDF extrai OK em periodicos.newsciencepubl.com): não conformidade estável ~25–26% (2018/19: 3.296 amostras, 25,6% NC; 2022: 1.772, 25,0% NC; 2023: 3.294, 26,1% NC); risco agudo 0,67% (2023) → 0,45% (2025).

## Preços por análise cromatográfica

- BR: tabelas públicas NÃO encontradas (laboratórios privados não publicam; Instituto Biológico/SP fora do ar — ERR_NAME_NOT_RESOLVED + cert inválido). Declarar a lacuna no relatório.
- Internacional citável: Detox Project US$ 200/produto (certificação glyphosate residue-free, detoxproject.org); blogs US$ 240–500/amostra multirresíduo. Faixa prática US$ 200–500/amostra LC-MS/MS.

## Players operando no Brasil (confirmados)

Eurofins do Brasil (Indaiatuba/SP — credenciado MAPA), Bioagri (SP — Mérieux NutriSciences, e-mail @mxns.com), NSF Bioensaios (Viamão/RS), ITEP (Recife/PE), Instituto Biológico (SP), SGS (primeira certificadora no Brasil com acreditação Inmetro — sgs.com/pt-br), Intertek, Bureau Veritas do Brasil, ALS.
