---
name: analise-edital-fomento-id
description: "Use ao analisar edital de fomento para a ID.

Carregue esta skill quando a ID avaliar edital de fomento: leitura das exigências, checklist de elegibilidade e documentação, aderência ao portfólio da ID e decisão de submeter ou não."
category: business
type: Orchestrator
license: MIT
author: Mercúrio
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [edital, fomento, elegibilidade, fapesp, cnpq, finep, ict, documentos]
    scopes: [id]
    related_skills: [agenda-id, elaboracao-proposta-comercial, contratos-justos-id]
timestamp: 2026-10-20T00:00:00Z
---

# Análise de edital de fomento para a ID

## Quando usar

Um sócio manda o link de uma chamada/edital (FAPESP, CNPq, FINEP, Sebrae, ICT+empresa,
internacionais) pedindo análise, elegibilidade, prazos, ou "liste os documentos que dá para
preparar". Serve também ao Radar de Oportunidades da ID.

## Ordem de leitura — nesta ordem, sempre

1. **Página da chamada**: cronograma, modalidades, valores máximos, critérios de avaliação.
2. **FAQ da chamada**: quase sempre página separada, linkada no corpo (na FAPESP tem página
   própria). É onde estão as respostas de elegibilidade que decidem o resto.
3. **Normas de cada modalidade**: a lista de documentos e o formato da proposta **não** estão na
   chamada — estão na norma da modalidade (ex.: `fapesp.br/apr`, `fapesp.br/tematico`). A chamada
   remete a elas e cobra "as especificidades" por cima.
4. **Anexo da agência nacional**, quando a chamada é internacional: o anexo brasileiro repete a
   chamada em português; em caso de divergência prevalece a versão em inglês.
5. **Não inventar exigência**: o que não estiver nessas páginas não entra na lista de documentos.

## Elegibilidade — antes de qualquer lista

- Diga **quem recebe recurso** e **onde a ID entra**. Na FAPESP o recurso é de pesquisador doutor
  com vínculo em instituição de pesquisa **do estado de São Paulo**; pesquisador de outro estado
  participa como **Pesquisador Associado (colaborador)** e **não é elegível a financiamento**.
- A ID não é instituição de pesquisa. O caminho institucional da casa é a **ICT** (Sergipetec,
  onde o Gustavo é residente) em chamadas **ICT + empresa**, com a ID contratada como executora
  dentro do projeto — o mesmo arranjo desenhado com a BiotechSE em edital CNPq.
- Chamada acadêmica ainda abre porta: stakeholder não acadêmico é explicitamente incentivado na
  categoria de Pesquisador Associado.
- **Conflito de interesse**: coordenador que também é sócio da empresa executora precisa de
  anuência da ICT e não pode indicar a própria empresa como recebedora.
- Critério de desempate entre agências: **contrapartida**. Edital que não exige contrapartida já
  venceu o comparativo na casa — registre esse critério na recomendação, não só o valor.

## Gate de cronograma — antes de montar a lista de documentos

- Chamadas internacionais têm fases habilitadoras: **aviso de interesse (NOI) → carta de intenção
  (LOI) → proposta completa**. NOI e LOI são eliminatórias e vencem meses antes da janela de
  submissão final.
- **Janela aberta ≠ submissão possível.** Se a fase habilitadora passou e a equipe não passou por
  ela, não há como entrar nesta edição. Diga isso **na primeira frase** e reposicione o trabalho
  (acervo reutilizável para o próximo ciclo, ou outro edital). Entregar a lista de documentos sem
  esse aviso cria expectativa falsa e queima a rodada.
- Datas do cronograma vêm da página; a data de hoje vem de fonte externa **que não possa estar em
  cache** (o header `Date` de página pública chega por CDN e já veio com um dia de atraso — ver
  regra de data em `agenda-id`).

## Lista de documentos — blocos típicos

Separe por **fase** (o que era da fase vencida e o que ainda dá para preparar) e por **agência**
(sistema nacional × sistema estrangeiro), com o responsável por cada peça.

- **Acadêmico**: súmula curricular do pesquisador responsável (modelo da agência), dos
  pesquisadores principais e dos responsáveis nas instituições parceiras; cadastro e confirmação de
  participação de cada membro no sistema da agência.
- **Projeto**: sumário executivo com limite de páginas (a modalidade diz o limite) e projeto de
  pesquisa completo com limite próprio.
- **Orçamento**: orçamento na aba de valores do sistema; 3 cotações para material permanente acima
  do teto em salários mínimos.
- **Institucional**: manifestação do dirigente da instituição sede (modelo do próprio sistema),
  informação sobre infraestrutura institucional assinada pelo responsável e pelo dirigente, anuência
  do dirigente de cada instituição parceira, termo de vinculação não empregatícia quando o
  responsável não tem vínculo com a sede.
- **Conformidade**: plano de gestão de dados (o que será gerado e como será preservado e
  disponibilizado), declaração de equidade/diversidade/inclusão na prática de pesquisa, atestado de
  segurança de pesquisa quando a tecnologia for sensível, resultados de auxílios anteriores da
  agência nos últimos 5 anos (ou declaração de que não houve).
- **Consórcio**: acordo entre parceiros cobrindo guarda e acesso a dados, repositórios, regras de
  coautoria e propriedade intelectual — não vai na submissão, mas a agência pode exigir a qualquer
  momento.
- **Bolsas**: plano de atividades individual para **cada** bolsa solicitada.

## Formato da entrega

- **Lista primeiro, análise depois.** Sócio que pede "o que dá para preparar" quer o parcial agora:
  entregue o que já está verificado e diga o que falta (regra de parcial em
  `id-comunicacao-multiusuario`).
- Diga em uma linha o **papel da ID** no arranjo (executora, associada, parceira) e o que ela **não**
  recebe.
- Feche com as decisões dos sócios: quem coordena, qual instituição sedia, quem assina, contrapartida.
- O **acervo se reusa** entre editais (súmulas, currículos, declarações, plano de dados): ofereça
  mantê-lo pronto em vez de refazer a cada chamada.

## Pitfalls

- **Modalidade muda a lista.** Regular × Temático têm valor, prazo e documentos diferentes: leia a
  norma da modalidade escolhida, não só a chamada.
- **Prazo vencido vira pergunta, nunca afirmação** de que "ainda dá tempo".
- **Não confunda "página atualizada em" com prazo** — o prazo é o item do cronograma.
- **Não presuma que a chamada está aberta para a ID** só porque a janela de submissão está aberta:
  a fase habilitadora é que decide.
