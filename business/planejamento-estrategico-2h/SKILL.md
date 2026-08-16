---
name: planejamento-estrategico-2h
description: "Facilitar planejamento estratégico em 2h — EOS V/TO + One-Page Strategic Plan.

Carregue esta skill quando precisar facilitar uma sessão única de planejamento estratégico para dono de PME + time pequeno (3-12 pessoas), com entregável obrigatório de 1 página. Usa EOS V/TO (Wickman) + One-Page Strategic Plan (Harnish), técnicas Liberating Structures, pré-mortem e timeboxing rigoroso. BSC e Hoshin Kanri não fecham em 2h — servem só como lente conceitual. Absorveu planejamento-estrategico (merge 16/08/2026): tabela de adequação de 11 frameworks + catálogo."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [planejamento-estrategico, facilitacao, workshop, pme, estrategia]
    related_skills: [meeting-action-items, weekly-review-planning]
type: Orchestrator
timestamp: 2026-08-15T02:39:34Z
---

# Facilitação de Planejamento Estratégico em 2 Horas

## Overview

Sessão única de planejamento estratégico para dono de PME + time pequeno (3–12 pessoas), com duração máxima de 120 minutos. A espinha dorsal é o **EOS V/TO** (Wickman, 8 perguntas em 1 página) + **One-Page Strategic Plan** (Harnish) — os dois frameworks calibrados para PME com entregável de 1 página. Técnicas de facilitação: **Liberating Structures** (1-2-4-All, 15% Solutions), **pré-mortem** (Klein/HBR), **timeboxing** rigoroso.

Regra de ouro: **a saída obrigatória é 1 página** — visão, meta de 1 ano, 3–5 prioridades de 90 dias, 1 número crítico, riscos e responsáveis. Sem isso, a reunião foi só conversa.

Não tente fechar BSC (Kaplan) ou Hoshin Kanri em 2h — exigem semanas ou ciclo contínuo. Servem apenas como lente conceitual (ex.: 4 perspectivas do BSC como brainstorming, disciplinas do Hoshin como inspiração de execução).

## When to Use

- Cliente/empresa pede "planejamento estratégico" e tem no máximo uma tarde
- Time nunca fez PE e precisa do primeiro ciclo em formato executável
- Replanejamento rápido (ex.: ano novo, crise, mudança de mercado)
- Precisa sair da reunião com prioridades de 90 dias + responsáveis

**Não usar para:** PE institucional completo (BSC com dezenas de KPIs, Hoshin Kanri com X-Matrix), planejamento orçamentário detalhado, reunião de acompanhamento (use `meeting-action-items`).

## Pré-sessão (15 min do facilitador, assíncrono)

1. Enviar ao dono 3 perguntas (resposta em 5 min, sem preparação pesada):
   - Quais os números atuais? (receita mensal aproximada, margem, nº de funcionários)
   - Qual a maior dor hoje?
   - O que não pode mudar? (valores/propósito)
2. Criar board colaborativo (Miro recomendado — plano grátis tem 3 boards; alternativas Mural/FigJam; **evitar Google Jamboard, descontinuado**) com 5 áreas:
   - SWOT (4 quadrantes)
   - Visão (core focus + metas)
   - Prioridades (área de agrupamento + votação)
   - Riscos (pré-mortem)
   - One-Page Plan (template final — ver `templates/one-page-plan.md`)
3. Confirmar participantes (3–12), data/hora, link de vídeo e quem será o **timekeeper** (pode ser o próprio facilitador).
4. Timer visível na tela (o timeboxing é a técnica mais importante da sessão).

## Agenda — 120 minutos

> **Regra de timeboxing:** cada bloco termina no horário, sem exceção. O que não couber vai para a **Issues List** (lista de pendências visível no board) e é tratado depois. O facilitador NÃO salva o grupo — corta e segue.

### Bloco 0 — Abertura e regras (5 min)
- Propósito em 1 frase: "Vamos sair daqui com a estratégia de 1 página: para onde vamos, as 3–5 prioridades dos próximos 90 dias e quem faz o quê."
- Regras: timeboxing (cada bloco termina no horário; pendências → Issues List); **todas as vozes, sem hierarquia**; celular no mudo.
- Nomear timekeeper.

### Bloco 1 — Check-in e panorama (10 min)
- Cada pessoa, 1 frase: "Como está a empresa hoje?"
- Dono apresenta os números (receita, margem, time) e a maior dor.
- Facilitador anota as dores em post-its visíveis (viram matéria-prima da SWOT e dos Rocks).

### Bloco 2 — SWOT relâmpago (20 min)
Técnica **1-2-4-All** (Liberating Structures):
1. Individual, silêncio: cada um escreve forças, fraquezas, oportunidades, ameaças (2 min)
2. Pares: consolidam (5 min)
3. Grupos de 4: consolidam (8 min)
4. Plenária: leitura rápida + **dot-voting** — cada pessoa 2 votos (5 min)
- Saída: top 3 forças, 3 fraquezas, 3 oportunidades, 3 ameaças fixadas no board.
- O resto vai para a Issues List.

### Bloco 3 — Visão e direção (25 min)
Perguntas V/TO condensadas:
- **Core Focus (5 min):** "Qual é o nosso propósito? Para quem servimos?" → 1 frase.
- **Meta de 3 anos (7 min):** "Daqui a 3 anos, onde estamos?" → 1 frase **com número** (ex.: "R$ 2M/ano com 15 pessoas").
- **Meta de 1 ano (7 min):** receita + 1 resultado-chave não financeiro.
- **Backcasting leve (6 min):** "O que precisa ser verdade daqui a 3 anos para chegarmos lá?" → trabalhar de trás para frente.
- Fechar com a **One-Phrase Strategy**: "Nossa estratégia em uma frase." (o dono decide; o resto vota antes, silenciosamente).

### Bloco 4 — Prioridades (25 min)
1. **Geração silenciosa (5 min):** cada um escreve 2–3 iniciativas que levam à meta de 1 ano (estilo Design Sprint: voto silencioso antes do debate).
2. **Agrupar + dot-voting (10 min):** 3 votos por pessoa; agrupar temas.
3. **Dono decide (5 min):** 3–5 **Rocks** do trimestre — "Quais 3–5 coisas, se feitas nos próximos 90 dias, nos movem mais?"
4. **Número crítico (5 min):** "Qual a ÚNICA métrica que diz que estamos no caminho?" (Critical Number do V/TO).

> O dot-voting é **input**, não decisão. O dono decide os Rocks e o número crítico.

### Bloco 5 — Pré-mortem (15 min)
Gary Klein (HBR): "É daqui a 90 dias e o plano falhou. Por quê?"
1. Cada um escreve em silêncio 2–3 motivos plausíveis (5 min) — dá voz segura ao pessimista.
2. Compartilhar e agrupar causas (5 min).
3. Top 3 riscos → contramedidas (5 min) → entram no one-page plan como mitigação.

### Bloco 6 — Plano de ação (15 min)
- **WWW (Who/What/When)** para cada Rock: dono atribui responsável + prazo (10 min).
- Preencher o **One-Page Plan ao vivo** no board (5 min): visão, metas, prioridades, número crítico, riscos, responsáveis.
- Saída obrigatória: **1 página**.

### Bloco 7 — Fechamento (5 min)
- **15% Solutions** (Liberating Structures): cada pessoa anuncia 1 ação que fará nos próximos 7 dias **sem pedir permissão**.
- **Agendar follow-up na hora:** reunião semanal de 15–30 min para revisar o WWW (estilo Level 10/EOS) + revisão trimestral.
- Dono confirma a versão final do one-page plan.

## Pós-sessão (30 min do facilitador)

1. Exportar o board (PDF/PNG) e entregar o one-page plan + plano de ações em **5W2H** (planilha/Google Sheets).
2. Transferir o plano para o local de trabalho contínuo (Notion/Drive) — o one-page plan é a "memória viva", não um PDF engavetado.
3. Agendar na agenda do cliente: reuniões semanais de follow-up + revisão trimestral (data fixa, booking na hora).
4. Enviar resumo em 24h: decisões, Rocks, responsáveis, datas.

## Ferramentas

| Papel | Recomendação |
|---|---|
| Quadro colaborativo | Miro (grátis, 3 boards; templates SWOT/OKR/action plan prontos) ou Mural/FigJam |
| Timer | Visível na tela (app de pomodoro serve) |
| Entregável | One-Page Plan (1 página) + planilha 5W2H |
| Memória viva | Notion/Drive pós-sessão |
| Evitar | Google Jamboard (descontinuado); Canva serve só para artefato final, não colaboração |

## Common Pitfalls

1. **Deixar bloco estourar.** O timeboxing é o que torna 2h possível. Timekeeper corta, pendência → Issues List. Sem isso a sessão vira 3h e o plano sai pela metade.
2. **Dono monopolizando.** Regra "todas as vozes" + voto silencioso ANTES do debate. O time pequeno tem a informação que o dono não tem.
3. **Tentar BSC/Hoshin em 2h.** Fora de escopo — usam-se só como lente. Cobrar escopo na abertura evita a discussão.
4. **Sair sem data de follow-up.** Plano sem ritual de revisão morre em 30 dias. A reunião semanal de 15–30 min é obrigatória.
5. **Sessão sem números.** Pedir os números antes (pré-sessão). "Dados aproximados bastam" — sem eles a meta de 1 ano é chute.
6. **Decidir por votação.** Dot-voting ranqueia; o dono decide. Delegação de decisão é como a sessão perde o compromisso.
7. **Entregar 10 páginas.** O valor está em caber em 1 página. Se não coube, não está priorizado.

## Verification Checklist

- [ ] Pré-sessão enviada (3 perguntas ao dono) e board montado com 5 áreas
- [ ] Agenda de 120 min cumprida com timekeeper cortando cada bloco no tempo
- [ ] Saída: one-page plan preenchido ao vivo (visão, meta 1 ano, 3–5 Rocks, número crítico, riscos, responsáveis)
- [ ] WWW (Who/What/When) preenchido para cada Rock
- [ ] 15% Solutions: cada participante anunciou 1 ação de 7 dias
- [ ] Follow-up semanal + revisão trimestral agendados com data
- [ ] Board exportado, plano entregue (1 página + 5W2H) e resumo enviado em 24h

## Seleção de framework por adequação a 2h

Absorvido de `business/planejamento-estrategico` (merge 16/08/2026). Catálogo completo das 11 metodologias com URLs e confiança: `references/frameworks-2h.md`.

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

> ⚠️ URLs oficiais de V2MOM (salesforce.com/blog/v2mom) e Destination Postcard (eosworldwide.com/blog/destination-postcard) estão **fora do ar** — citar livros canônicos (*Behind the Cloud*, *Traction*) e ferramentas oficiais vivas (eosworldwide.com/vto-download). Validado 15/08/2026.

## Referências

Fontes e URLs da pesquisa que embasou esta skill: `references/fontes-pesquisa.md`. Template do entregável: `templates/one-page-plan.md`. Catálogo de frameworks: `references/frameworks-2h.md`.
