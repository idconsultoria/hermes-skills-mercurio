# TAM/SAM/SOM sizing para valuations — workflow validado

Validado em 15/08/2026 (caso BiotechSe, valuation-consultivo — user pediu explicitamente
"faça a pesquisa para esses indicadores também"). Quando o usuário não sabe os números de
mercado, **pesquisar antes de pedir chutes** — o usuário valida cenários propostos, não chuta
no escuro. Dados de TAM por segmento: ver `brazilian-agbio-inputs-market-data.md` e
`market-sizing-blocked-sites-playbook.md`.

## 1. A escada (explicar antes de perguntar)

- **TAM** = bolo inteiro (se todo mundo que poderia comprar comprasse amanhã) — teto teórico.
- **SAM** = fatia alcançável (geografia, segmento, capacidade de entrega).
- **SOM** = receita real em 5–7 anos (3 cenários: pessimista/provável/otimista) — o número que
  o investidor confere contra o plano.

## 2. Disparo: 1 subagente por segmento (3 paralelos)

Cada subagente recebe: contexto do valuation + fontes a priorizar + REGRAS + FORMATO DE SAÍDA.
Regras críticas no prompt (copiar):

```
- Cada dado deve vir com URL da fonte e data de publicação. Cite o número exato como a fonte reporta.
- Marque confiança: ALTA (múltiplas fontes concordam), MÉDIA (fonte única confiável), BAIXA (estimativa não verificada).
- Distinga: faturamento real do mercado (associações do setor) vs projeções de consultorias (tendem a ser otimistas).
- Use buscas sem aspas duplas. Se web_search retornar vazio, tente Bing/DuckDuckGo ou navegue direto em sites conhecidos.
- Não invente números. Se não encontrar, diga explicitamente que não encontrou.
```

FORMATO DE SAÍDA (markdown):
```
## Segmento: <nome>
### Número principal: [valor] ([fonte], [data])
### Dados adicionais: (tabela: dado | valor | fonte/URL | data | confiança)
### [extras por segmento]
### Fontes consultadas: lista completa de URLs
```

## 3. Consolidação com grounded-citations

1. `python3 sources.py reset` (ledger limpo por tarefa)
2. Registrar as URLs-chave retornadas pelos subagentes: `python3 sources.py add <url1> <url2> ...`
3. Escrever o relatório com citações inline [n] após cada frase suportada
4. `python3 sources.py verify <relatorio>` — verde antes de entregar
5. `python3 sources.py render --replace-in <relatorio>` — bloco Sources mecânico (nunca digitar URL à mão)
6. Entregar com nome de versão (ex: `TAM_mercados_<empresa>_v1.md`)

## 4. Enquadramento do TAM — duas camadas

| Camada | O que é | Uso |
|---|---|---|
| Núcleo servível | O bolo que a empresa realmente pode atacar (segmento específico) | Narrativa e metas (ex: 0,1% = X; 1% = Y) |
| Teto absoluto | O bolo inteiro do setor | Contexto/ambição |

- **Derivações (cálculos próprios a partir de fontes) sempre marcadas BAIXA** e rotuladas
  ("cálculo próprio") — nunca apresentadas como dado de fonte.
- **Declarar gaps explicitamente**: "nenhuma fonte pública Brasil-específica foi encontrada"
  vale mais que um número inventado.

## 5. SOM — benchmarks de trajetórias de receita (segunda rodada)

3 subagentes paralelos pesquisando empresas comparáveis (mesma região/estágio):
- Startups do setor (ex. bioinsumos BR: Biotrop, SuperBac, Simbiose) — tempo para R$ 5/20/50 mi, rodadas
- Prestadores de serviço comparáveis (ex. laboratórios regionais de análise de alimentos) — receita, preço/amostra, capacidade por equipamento
- Players do nicho (ex. bioaumentação BR: MicroCiclo etc.) — modelo de negócio, tickets de contrato

Propor os 3 cenários (pessimista/provável/otimista) e pedir validação. Cruzar com a capacidade
real da empresa (N projetos/ano × ticket médio) — bottom-up confere com o benchmark.

### Calibrar tickets sem tabela pública (B2B industrial) — padrão validado 15/08/2026

- **Derivar tickets de números públicos ÷ contagens operacionais**: Opersan R$ 120 mi (2022, Exame)
  ÷ 65 operações OnSite ≈ R$ 1,8 mi/ano por operação; ÷ ~1.000 clientes ≈ R$ 120–180 mil/ano
  ticket médio. Marcar "derivação — MÉDIA", nunca como dado de fonte.
- **Âncora bottom-up real**: contrato fechado do cliente (R$ 122 mil / 16 × R$ 7.653,72 ≈
  R$ 92 mil/ano recorrente) + pipeline (R$ 120 mil consultoria); mix-alvo 80% recorrente / 20% projeto.
- **Análogos de trajetória (soluções microbianas/efluentes BR)**: Gênica (2015→R$ 130 mi 2023→
  R$ 230 mi 2024E; dobrou/ano desde 2019; ~R$ 150 mi levantados — startup COM capital, padrão de
  escala em ~9 anos); Superbac (<R$ 20 mi até 2015 → meta R$ 1 bi 2022 — bootstrapped, décadas);
  Opersan (30+ anos p/ R$ 120 mi — O&M asset-heavy); Biotrop (venda R$ 2,8 bi 2023; ~R$ 900 mi 2025 —
  teto de exit do segmento); MicroCiclo (2019→2026 ainda pré-scale — velocidade realista do ciclo
  B2B de efluentes).
- **Faixas SOM ano 5 validadas (BiotechSe, bioaumentação+consultoria)**: conservador R$ 1,2–2,5 mi
  (0,3–0,7% do nicho R$ 300–390 mi); base R$ 3–6 mi (1–1,7%); agressivo R$ 8–15 mi (2–4%, exige
  capital R$ 20–50 mi + biofábrica/registro, padrão Gênica). Base só é defensável como caso central
  com produto padronizado + conversão projeto→recorrente.
- Data bank completo de players/tickets/crescimento (Superbac, MicroCiclo, Nutrenzi, Genetica
  Bioscience, Opersan, Cetrel/Solví, Veolia, Gênica, Nitro...): `market-sizing-blocked-sites-playbook.md` §5.

## Caso BiotechSe (15/08/2026) — números de referência

| Segmento | Núcleo servível | Teto absoluto | Confiança |
|---|---|---|---|
| Agro — inóculos personalizados | R$ 0,8–2,0 bi/ano (13% de R$ 6,2 bi; escopo amplo Mordor) | R$ 6,2 bi (bioinsumos BR 2025, CropLife) → R$ 9 bi 2030 | MÉDIA/ALTA |
| Efluentes — bioaumentação | R$ 300–390 mi/ano (US$ 60–75 mi, derivado de LatAm US$ 148 mi) | R$ 6–14 bi/ano (trat. efluentes industriais BR, derivado) | BAIXA |
| Alimentos — análise cromatográfica | R$ 2,6 bi/ano (US$ 499,5 mi 2025, M&M rapid food safety) | R$ 2,6–3,4 bi/ano | ALTA |

Fontes-chave: CropLife/CropData via imprensa (R$ 6,2 bi, mar/2026) · Mordor (inoculantes global
US$ 12,35→19,46 bi, CAGR 9,52%) · Embrapa (FBN R$ 142,8 bi/safra) · Precedence (efluentes US$ 19,4 bi
2025; tratamento biológico = maior segmento) · MarketIntelo (bioaumentação global US$ 1,8 bi 2025) ·
M&M Brazil rapid food safety (US$ 499,5 mi, único dado país-específico ALTA) · MAPA (5 laboratórios
credenciados para resíduos em vegetais).

## Lições de facilitação da sessão

- **"Sem concorrentes" dito pelo usuário** → pesquisa de mercado não feita, não monopólio. O
  concorrente real de P&D sob demanda é o status quo do cliente (insumo genérico). Vira risco a
  pesquisar, nunca prêmio de valuation.
- **Mostrar a matemática do contrato fechado** (16 × R$ 7.653,72 = R$ 122.459,52; margem ~74% com
  custo diluído R$ 32k) — conta visível constrói confiança; afirmar margem sem conta destrói.
- **Consolidar as premissas da entrevista** em `premissas_discovery_v1.md` (fonte + confiança por
  linha) — vira a base da aba Premissas da planilha de valuation.
