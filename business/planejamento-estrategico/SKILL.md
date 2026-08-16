---
name: planejamento-estrategico
description: "Planejar estratégia de PME em sessão única de 2h — EOS, OKR, V2MOM, 1 página.

Carregue esta skill quando um dono de PME (10-250 funcionários) + time pequeno pedirem planejamento estratégico em uma sessão de até 2h. Escolhe frameworks (EOS V/TO, OPSP, V2MOM, OKR) pelo tempo disponível e perfil da empresa, conduz a facilitação e entrega tudo em UMA página ao final. Trabalho em PT-BR com markdown estruturado e tabelas comparativas."
version: 1.0.0
author: hermes-curator
license: CC-BY-4.0
category: business
type: Orchestrator
timestamp: 2026-08-15T00:00:00Z
metadata:
  tags: [planejamento-estrategico, pme, estrategia, facilitacao, workshops]
  related_skills: [systematic-research]
---

# Planejamento Estratégico para PME em Sessões Curtas (≤2h)

## Quando usar
- Dono de PME (10–250 funcionários) + time pequeno (3–12 pessoas) querem planejamento estratégico em UMA sessão de até 2h.
- Pedidos típicos: "workshop de planejamento estratégico", "definir visão/missão/metas", "alinhar o time", "definir prioridades do trimestre".
- Precisa escolher entre frameworks (EOS, OKR, BSC, Hoshin, V2MOM…) pelo tempo disponível e perfil da empresa.
- Idioma de trabalho e entrega: PT-BR (formatos: markdown estruturado, tabelas comparativas, blocos curtos).

## Regra de ouro
- **2h NÃO comporta frameworks pesados:** BSC completo (semanas, Nine Steps) e Hoshin Kanri (ciclo anual, X-Matrix/catchball) ficam de fora — no máximo como lente conceitual para um brainstorm rápido.
- **Tudo cabe em UMA página** ao final da sessão (V/TO, OPSP ou V2MOM preenchidos).
- **Sem pré-trabalho enviado 48h antes, a sessão vira 1h de contexto** — exija pré-trabalho (rascunhos individuais, Destination Postcard, dados financeiros).

## Seleção de framework por adequação a 2h
| Adequação | Framework | Por quê |
|---|---|---|
| ALTA | EOS / V/TO (Wickman) | Calibrado para PME (10–250); 8 perguntas em 1 página; ferramentas oficiais gratuitas |
| ALTA | V2MOM (Salesforce) | 5 perguntas (Vision, Values, Methods, Obstacles, Measures), 1 página, 60–120 min |
| ALTA | OKR (Doerr/Grove) | Workshop padrão 90 min–2h; entrega objetivo + métricas executáveis no trimestre |
| ALTA | One-Page Strategic Plan (Harnish) | Plano holístico em 1 página (BHAG→metas→Rocks→KPIs); cabe em 2h com pré-trabalho |
| ALTA | Playing to Win (Lafley & Martin) | A estratégia inteira = 5 escolhas (cascade); percorrível em 2h com contexto pré-coletado |
| ALTA* | Business Model Canvas | Canvas completo em 90–120 min — mas cobre modelo de negócio, não metas/execução |
| ALTA* | 4DX (FranklinCovey) | WIG + lead measures em 90 min — mas assume visão já definida; melhor como fechamento |
| MÉDIA | BHAG (Collins & Porras) | Componente de 30–45 min, ótimo bloco de abertura — não é framework completo |
| BAIXA | Balanced Scorecard | Exige semanas/múltiplos workshops (4 perspectivas, mapa, cascata, KPIs) |
| BAIXA | Hoshin Kanri | Ciclo anual contínuo (X-Matrix, catchball, PDCA); sessão única rende pouco |

\* escopo estreito — combinar com outro framework do grupo ALTA.

## Sequência de blocos recomendada (2h)
1. **Destination Postcard** (30–45 min): cada participante escreve, em 1ª pessoa e presente, a empresa daqui a 10 anos; compartilhar e sintetizar a visão comum. Gera o material emocional/qualitativo do resto da sessão.
2. **Núcleo estratégico** (60–70 min): escolher UM — EOS V/TO (8 perguntas) OU Playing to Win (5 escolhas). Não misturar dois núcleos.
3. **Fechamento executável** (30–45 min): OKR da empresa OU WIG de 4DX — objetivo + 3–5 métricas com dono. Registrar decisões e data de revisão de 90 dias.

## Saída obrigatória da sessão
- 1 página preenchida (V/TO, OPSP ou V2MOM)
- 3–5 prioridades de 90 dias com **dono nomeado** e data
- Data de revisão agendada (90 dias)
- Se time > 5 pessoas: accountability/roles definidos

## Pitfalls
- **Misturar frameworks no núcleo** (ex.: V/TO + BSC) — escolher UM núcleo por sessão.
- "BSC light" / "Hoshin light" em 2h entregam ilusão de planejamento — recusar ou deixar explícito que é só brainstorm de lente.
- URLs oficiais de V2MOM (salesforce.com/blog/v2mom) e Destination Postcard (eosworldwide.com/blog/destination-postcard) estão **fora do ar** — citar livros canônicos (*Behind the Cloud*, *Traction*) e ferramentas oficiais vivas (eosworldwide.com/vto-download). Validado 15/08/2026.
- OKR sem métrica mensurável não é OKR; meta sem dono não sai do papel.
- Tempo típico informativo: EOS V/TO = 2 sessões de meio dia; OKR = trimestre; OPSP = retiro anual de 1–2 dias; BMC = 90 min–2h; 4DX = WIG 90 min + cadência semanal de 20–30 min.

## Catálogo completo
Origem, elementos centrais, tempo típico, templates e agendas com URL, fontes oficiais e confiança (HIGH/MEDIUM/LOW) das 11 metodologias → `references/frameworks-2h.md`

## Pesquisa de fontes (se precisar revalidar)
- Fontes oficiais preferidas (HIGH): eosworldwide.com, whatmatters.com, balancedscorecard.org, rogerlmartin.com, lean.org, scalingup.com, jimcollins.com, strategyzer.com, franklincovey.com.
- Se web_search falhar/retornar vazio: usar o skill `systematic-research` (URLs diretas + Wayback availability API para URLs mortas) — nunca citar URL não verificada.
