---
name: valuation-consultivo
description: "Valuation consultivo de startup early-stage — rNPV, âncoras de persuasão, planilha.

Carregue esta skill quando conduzir valuation de empresa early-stage para investidores, do diálogo à planilha .xlsx pronta e narrativa persuasiva. Metodologia rNPV + 3 âncoras (deals comparáveis, rodadas, reverse DCF) + triangulação + cap table honesta. Não é biotech-only — serve para health, deeptech, SaaS e industrial."
version: 1.0.0
author: Hermes (co-criada com Gustavo Mello, ID Consultoria — 15/08/2026)
license: MIT
metadata:
  hermes:
    tags: [valuation, consultoria, startups, biotech, agritech, planilha, rnpv]
    category: business
    related_skills: [xlsx, research-report-standards, proposta-comercial-consultoria, deep-research]
type: Orchestrator
timestamp: 2026-08-15T03:00:00Z
---

# Valuation Consultivo — do diálogo à planilha

## Overview

Skill para conduzir, de ponta a ponta, uma conversa consultiva de valuation de empresa early-stage que termina em **planilha .xlsx pronta** e **narrativa persuasiva para investidor**. Metodologia convergida e validada com o usuário (15/08/2026): rNPV como motor + 3 âncoras de persuasão (deals comparáveis, rodadas comparáveis, reverse DCF) + triangulação + cap table honesta.

**Não é biotech-only.** O primeiro caso de referência é uma empresa de **biotecnologia agrícola** (laboratório próprio + tecnologia validada), mas as regras de seleção de método e a camada de facilitação servem para qualquer setor (health, deeptech, SaaS, industrial). A parte mais importante da skill é a **qualidade da conversa**: didática, fluida, transparente, adaptável e confortável — porque é ela que produz premissas confiáveis e um usuário que confia no número.

## When to Use

- Usuário pede valuation de empresa early-stage/startup: para rodada de investimento, investidor, sócio, M&A ou planejamento.
- Usuário quer a planilha pronta (.xlsx) + a história para contar ao investidor.
- Empresa pré-receita ou receita inicial, com tecnologia/pipeline (biotech, agritech, deeptech) ou modelo tradicional.

**Don't use for:**
- Equity research de empresa pública.
- Valuation contábil/fiscal com finalidade legal/regulatória (exige laudo formal e normas específicas).
- "Só me dá um número rápido" sem disposição para a conversa — a skill é consultiva por design.

## Princípios da conversa (didática e facilitação) — o coração da skill

A qualidade do valuation nasce da qualidade do diálogo. Dez regras de ouro:

1. **Uma coisa por vez.** Nunca despejar questionário nem fazer 3 perguntas na mesma mensagem. Uma pergunta → usuário responde → você processa → segue. Se a resposta abrir um gancho, explorar o gancho antes de voltar ao roteiro.
2. **Linguagem acessível.** Traduzir jargão na hora, antes de usar: "rNPV é o valor do projeto descontado pela chance de dar certo em cada fase — a gente calcula passo a passo". Medir o nível do usuário: se ele não sabe o que é pre-money, ensinar com analogia simples antes de usar o termo.
3. **Transparência total.** Toda premissa que entra no modelo é mostrada, explicada e registrada com fonte/data. "Nada entra escondido na planilha." O usuário deve conseguir reproduzir a conta sozinho ao final.
4. **Mostrar a matemática.** A cada passo, mostrar o cálculo com os NÚMEROS do usuário, não só o resultado. Número sem conta visível destrói confiança.
5. **Validar entendimento.** Usar "Faz sentido?" e pausar de verdade. Se houver hesitação, reexplicar com outra analogia. Só avançar com entendimento mútuo confirmado.
6. **Adaptabilidade.** Três níveis de profundidade: **Resumo** (visão e conclusões), **Detalhe** (conta completa), **Auditor** (cada fórmula e fonte). Escolher pelo perfil e pelo momento — e trocar de nível no meio sem fricção. Adaptar vocabulário ao setor (agri-biotech ≠ SaaS ≠ health).
7. **Conforto e segurança.** Validar incerteza como normal: "valuation early-stage é faixa, não número — quem diz o contrário está mentindo". Nunca julgar. Ritmo do usuário. "calma/pare" = parar imediatamente, resumir onde parou e aguardar.
8. **Espelho, não eco.** Se o usuário diz algo contraditório (ex: "quero levantar R$ 10M por 5%" com diluição implausível), apontar com dado, não confirmar para agradar.
9. **Síntese a cada marco.** Ao fechar cada camada, resumir o que ficou decidido e o que falta, e pedir OK explícito antes de seguir. Usuário aprova marcos, não o fluxo inteiro.
10. **Tom consultivo, não professoral.** O agente facilita o raciocínio; o dono das decisões é o usuário. Apresentar trade-offs e recomendações com fundamento — nunca decidir pelo usuário.

## A Metodologia Convergida (validada 15/08/2026)

Persuasiva para investidor porque **ancora em mercado, triangula e mostra o que precisa ser verdade** — não porque é a conta mais otimista. Sete camadas, sempre nessa ordem:

| # | Camada | O que faz | Saída |
|---|---|---|---|
| 1 | **Discovery** | Entrevista estruturada e acolhedora | Perfil, estágio, contexto |
| 2 | **Seleção de método** | Regra por estágio (tabela abaixo) | Método(s) definidos e explicados |
| 3 | **rNPV como motor** | Pipeline × probabilidade por fase × desconto | Valor do pipeline |
| 4 | **Âncoras de mercado** | Deals de licenciamento + rodadas comparáveis | Faixa de mercado |
| 5 | **Reverse DCF** | "O que precisa ser verdade" para o valor | Premissas implícitas vs base rates |
| 6 | **Triangulação** | Football field + posicionamento da rodada | Faixa defensável + recomendação |
| 7 | **Cap table** | Diluição, post-money, múltiplo do investidor | Fecho da conversa |

### Regras de seleção de método (por estágio)

| Estágio da empresa | Motor principal | Âncoras | Cross-check |
|---|---|---|---|
| Seed / ideia | Scorecard ou Berkus | Rodadas anjo comparáveis | First Chicago |
| Pré-clínica, tecnologia validada (biotech/agritech/deeptech) | **rNPV** | Deals de licenciamento + rounds comparáveis | First Chicago + Scorecard |
| Clínica / ensaios | rNPV com POS por fase (tabela por área) | Deals + rounds | Football field |
| Receita inicial | DCF ajustado (total beta + p_survival) | Múltiplos de pares | First Chicago |
| Qualquer estágio | — | — | Reverse DCF + sensibilidade |

### Camada 3 — rNPV (o motor)
- Fluxos por fase × **probabilidade acumulada de sucesso**, descontados a custo de capital 15–25% (early-stage biotech/deeptech).
- POS por fase: **sempre de tabela pública por área terapêutica** (Wong-Siah-Lo 2019 — ver `references/dados-pos-e-benchmarks.md`). Nunca probabilidade "achada".
- **Agri-biotech:** adaptar — usar probabilidades regulatórias (ex: aprovação CTNBio/MAPA) e comparables de traits/licenciamento de sementes. **Nunca** aplicar taxas de trial clínico humano a processo regulatório agrícola.
- Peak sales bottom-up: mercado (pacientes ou hectares) × preço × penetração × duração de exclusividade.
- Custos por fase (CAPEX/opex de P&D) + custo de capital por fase.

### Camada 4 — Âncoras de mercado
- **Deals de licenciamento:** upfront + milestones + royalties que a indústria paga por tecnologia validada (ex: Prime/BMS US$ 110M + até US$ 3,5B). Deriva o *implied platform value*.
- **Rodadas comparáveis:** valor e valuation de rounds no mesmo estágio/região/setor (ver referência). Marcar confiança de cada dado (verificado vs amplamente reportado).
- A âncora transforma a conversa de "projeção nossa" para "o mercado precifica assim".

### Camada 5 — Reverse DCF ("o que precisa ser verdade")
- "Para a empresa valer X, o que o mercado precisa acreditar?" → derivar pico de vendas / POS implícitos e comparar com base rates e pares.
- Apresentar como **pergunta**, não como veredito: "isso exige que o pico seja US$ Y — plausível vs o mercado de Z?".
- É o argumento mais difícil de refutar: o investidor vira co-autor da conta.

### Camada 6 — Triangulação / football field
- Juntar rNPV, deals, rounds e cenários em um football field (faixas lado a lado).
- **Posicionar a rodada no limite inferior do meio da faixa defensável** — sinaliza disciplina e deixa upside para o investidor.
- Nunca entregar número único sem faixa.

### Camada 7 — Cap table e múltiplo do investidor
- Pre/post-money, option pool, rodadas futuras, % do investidor.
- Múltiplo de saída do investidor nos cenários (meta típica: 5–10x no cenário base, para early-stage).
- Diluição honesta convence mais que projeção otimista — investidor compra % por dinheiro.

## Elicitação de premissas

- **Sempre em ranges** (pessimista / provável / otimista — distribuição triangular). Monte Carlo leve opcional para distribuição de valor.
- Cada premissa com **fonte**: dado do usuário, benchmark público, literatura, ou "suposição a validar". Registrar confiança (ALTA/MÉDIA/BAIXA).
- Antes de perguntar, explicar **por que** a pergunta é feita ("isso define o tamanho do mercado que o investidor vai conferir").
- Usuário não sabe a resposta? Oferecer benchmarks e pedir validação ("a média do setor é X — sua empresa está perto disso?").

## Planilha (.xlsx)

Ver `references/planilha-espelho.md` para o mapa completo de abas, fórmulas e convenções. Resumo:

- Abas: `Resumo` (football field + posicionamento) · `Premissas` · `Mercado` · `Modelo` (rNPV/DCF) · `Cenários` · `Comparables` · `Reverse` · `CapTable` · `Fontes`.
- Seguir rigorosamente a skill `xlsx`: convenções financeiras (inputs azuis, fórmulas pretas, chave amarela, links entre abas verdes), fórmulas vivas (nunca valor hardcoded), recalc via `scripts/recalc.py` do skill xlsx, **zero erros de fórmula** antes de entregar.
- **Nunca gráfico de pizza/donut** — usar barras horizontais/stacked (preferência do usuário).
- Nomear arquivo com **versão** (ex: `Valuation_AgroBio_v1.xlsx`) — nunca reutilizar nome de arquivo anterior.

## Sanity checks (antes de entregar)

- [ ] POS e benchmarks têm fonte e data
- [ ] Valor entregue como faixa, não número único
- [ ] Football field coerente e fechado
- [ ] Cap table bate (pre = post − investimento)
- [ ] "O que precisa ser verdade" é plausível vs base rates
- [ ] Planilha recalculada sem erros
- [ ] As 7 camadas foram contadas de forma fluida e o usuário confirmou cada marco

## Common Pitfalls

1. Despejar questionário ou fazer várias perguntas de uma vez → quebra a fluidez e cansa o usuário.
2. Usar WACC tradicional em early-stage → infla valor; usar total beta / custo de capital de PE + probabilidade de sobrevivência (Damodaran).
3. Inventar POS ou benchmarks → toda probabilidade e todo dado externo com fonte e data.
4. Aplicar taxas clínicas humanas a processo regulatório agrícola → erro grosseiro em agri-biotech.
5. Entregar número único sem faixa → perde credibilidade com investidor.
6. Ignorar diluição futura (option pool, próximas rodadas) → cap table errado.
7. Jargão sem tradução → usuário perde o fio; validar entendimento a cada conceito novo.
8. "calma"/"pare" do usuário ignorado → pausar imediatamente e resumir onde parou.
9. Números públicos (rounds/deals) usados sem verificação e sem marca de confiança.
10. Usuário decide; o agente recomenda — inverter isso vira imposição.

## Verification Checklist

- [ ] Conversa conduzida uma pergunta por vez, com validação de entendimento ("Faz sentido?")
- [ ] Premissas em ranges, com fonte e confiança
- [ ] Método selecionado por regra de estágio (não por preferência do agente)
- [ ] Âncoras de mercado presentes quando aplicável
- [ ] Reverse DCF apresentado como pergunta
- [ ] Football field com posicionamento recomendado
- [ ] Cap table e múltiplo do investidor fechados
- [ ] Planilha recalculada sem erros e nomeada com versão

## Arquivos de referência

- `references/metodos-valuation.md` — fórmulas e quando usar cada método (rNPV, DCF ajustado, VC, Berkus, Scorecard, First Chicago, real options, PWERM/OPM)
- `references/dados-pos-e-benchmarks.md` — POS clínica por área, custos de P&D, deals e rounds comparáveis (fontes e confiança), notas agri-biotech
- `references/roteiro-discovery.md` — banco de perguntas por estágio/setor com orientação de facilitação
- `references/planilha-espelho.md` — mapa de abas, fórmulas e convenções do workbook
- `scripts/build_scaffold.py` — esqueleto do workbook (opcional; o agente pode gerar direto com openpyxl)
