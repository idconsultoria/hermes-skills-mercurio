# Dados de POS, custos, deals e rounds — benchmarks com fonte e confiança

Referência para a skill `valuation-consultivo`. **Regra: todo número usado na conversa deve ter fonte e data. Confiança ALTA = verificado em sessão de pesquisa (15/08/2026); MÉDIA = amplamente reportado, não re-verificado; BAIXA = domínio, validar antes de usar com cliente.**

## 1. Probabilidade de sucesso clínico (POS) por fase — CONFIANÇA ALTA

**Fonte:** Wong, Siah & Lo (2019), "Estimation of clinical trial success rates and related parameters", *Biostatistics*, doi 10.1093/biostatistics/kxx069 (PMC6409418). Texto completo analisado. Amostra: 406.038 registros de trials, 21.143 compostos, Jan/2000–Out/2015, método path-by-path, indústria, all indications.

| Grupo terapêutico | Fase 1→2 | Fase 2→3 | Fase 3→Aprovação | POS geral (F1→App) |
|---|---|---|---|---|
| Oncologia | 57,6% | 32,7% | 35,5% | **3,4%** |
| Metabólica/Endócrino | 76,2% | 59,7% | 51,6% | 19,6% |
| Cardiovascular | 73,3% | 65,7% | 62,2% | 25,5% |
| CNS | 73,2% | 51,9% | 51,1% | 15,0% |
| Autoimune/Inflamação | 69,8% | 45,7% | 63,7% | 15,1% |
| Geniturinário | 68,7% | 57,1% | 66,5% | 21,6% |
| Infecciosas | 70,1% | 58,3% | 75,3% | 25,2% |
| Oftalmologia | 87,1% | 60,7% | 74,9% | 32,6% |
| Vacinas (infec.) | 76,8% | 58,2% | 85,4% | 33,4% |
| **Overall** | **66,4%** | **58,3%** | **59,0%** | **13,8%** |

**Comparações:** Hay et al. (2014) LOA 10,4%; Thomas et al. (2016) 9,6%. Wong 13,8% (método path-by-path, amostra maior).

**Uso na skill:** programa pré-clínico tem POS até aprovação < 13,8% (F1→App). **Sempre por área terapêutica**, nunca número global fixo.

## 2. Custo de desenvolvimento de fármacos — CONFIANÇA ALTA (abstracts analisados)

- **Wouters, McKee & Luyten (2020), JAMA** — "Estimated Research and Development Investment Needed to Bring a New Medicine to Market, 2009-2018": estimativas de **US$ 314M a US$ 2,8B** por novo medicamento (média ~US$ 1,3B).
- **DiMasi, Grabowski & Hansen (2016), J Health Econ** — "Innovation in the pharmaceutical industry: New estimates of R&D costs" (3.318 citações): estimativa mais alta, ~US$ 2,6B incluindo custo de capital e falhas.

**Uso na skill:** inputs de custo por fase em rNPV; e argumento de "por que rodada grande": desenvolver até aprovação custa centenas de milhões.

## 3. Deals de licenciamento (âncora de mercado) — CONFIANÇA ALTA para os citados

| Deal | Upfront | Milestones | Fonte |
|---|---|---|---|
| **Prime Medicine × BMS** (set/2024) — reagentes de prime editing p/ T-cell therapy ex vivo | US$ 110M | até US$ 3,5B | Fierce Biotech (via Wikipedia) |
| **Prime Medicine × Cystic Fibrosis Foundation** (jan/2024) | US$ 15M | + US$ 24M (jul/2025) | Global Genes/BioWorld (via Wikipedia) |
| **Beam × Pfizer** (jan/2022) — CRISPR doenças raras | colaboração multi-target | — | Pfizer (via Wikipedia) |
| **Verve × Lilly** (jun/2025) — aquisição de 100% do equity | aquisição integral | — | Verve press release (via Wikipedia) |

**Faixas típicas de royalty (pharma):** ~2–15%, medianas ~5–8% — **CONFIANÇA BAIXA/MÉDIA (domínio, validar por deal)**. Agri-biotech: % sobre venda de sementes ou $/hectare — validar caso a caso.

## 4. Rodadas comparáveis (âncora de mercado) — CONFIANÇA MÉDIA nos valores de round

| Empresa | Estágio/tecnologia | Rounds | Verificado em sessão |
|---|---|---|---|
| **Beam Therapeutics** (base editing, 2017) | plataforma validada em lab acadêmico | ~US$ 1B VC pré-IPO; IPO fev/2020 US$ 180M | ALTA (Wikipedia) — rounds individuais (A US$ 87M 2018, B US$ 135M 2019) MÉDIA |
| **Prime Medicine** (prime editing, 2019) | plataforma validada | Series A US$ 115M (2021), B US$ 315M (2021), IPO 2022 | MÉDIA (widely reported) |
| **Verve Therapeutics** (base editing cardiovascular, 2018) | plataforma validada | Series A US$ 58,5M (2019), B US$ 94M (2020), IPO 2021 | MÉDIA (widely reported) |

**Padrão observado (inferência MÉDIA):** biotech early-stage com lab + tecnologia validada levanta Series A de **US$ 60–120M** e Series B de **US$ 100–350M**; valuations pre-money típicos **US$ 300M–1B+**. Brasil: mercado menor — usar como piso/contexto com ajuste de liquidez.

## 5. Notas agri-biotech (primeiro caso de uso)

- **Processo regulatório ≠ trial clínico humano.** Não aplicar as taxas da tabela acima a aprovação de OGM/traits. Usar: probabilidades de aprovação regulatória (Brasil: CTNBio, MAPA) e timelines típicas — validar com o cliente/fontes do setor (CONFIANÇA BAIXA, domínio).
- **Âncoras de mercado:** deals de traits/licenciamento de sementes (upfront + milestones + royalties por unidade de semente/hectare) e rodadas de agritech comparáveis — buscar dados atuais por deal antes de usar.
- **Mercado:** modelar por cultura (hectares plantados × preço de semente × prêmio do trait × penetração × anos de exclusividade).
- **Comparable útil:** valuation de startups de biotecnologia agrícola em estágio similar (ex: empresas de inoculantes, bioinsumos, melhoramento genético) — pesquisa por rodada quando aplicável.

## 6. Como registrar na planilha

Aba `Fontes` deve conter: premissa | valor | fonte | URL/DOI | data | confiança (ALTA/MÉDIA/BAIXA) | status (verificado/a validar). Toda premissa sem fonte vira "suposição a validar" — e é dito ao usuário assim.
