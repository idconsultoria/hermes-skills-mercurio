---
name: reunioes-diarizadas
description: "Use ao extrair encaminhamentos de reuniões diarizadas."
trigger: Pedido de encaminhamentos, decisões, ações ou pendências de reunião cujo material é uma transcrição diarizada automaticamente (com ou sem ata).
related_skills: [context-kb, autonomous-ai-agents, document-to-action-items]
type: Orchestrator
timestamp: 2026-09-21T12:00:00Z
---

# Reuniões diarizadas → encaminhamentos

Transcrição automática de reunião longa é fonte **ruidosa e volumosa**: 4-5h de sessão rendem 250-280 mil caracteres, com falantes mal atribuídos e trechos repetidos. Ler tudo queima contexto e ainda deixa passar item; a saída certa é aferir a qualidade da fonte, minerar por candidatos e ler integralmente só o que importa.

## Quando usar

- "Quais foram os encaminhamentos dessas sessões?"
- "O que ficou decidido e quem ficou responsável?"
- Consolidação de atas/pendências de reunião recorrente (planejamento, comitê, ritual semanal).

## Procedimento

### 1. Localizar a fonte e medir antes de ler

A fonte Reuniões da KB vive em `<HERMES_HOME>/context-kb/sources/reunioes/meetings/` — um arquivo por reunião, com o JSON de metadados, o bloco `## Ata` no topo e `## Transcrição diarizada` abaixo. Fathom, Drive e a pipeline de áudio geram o mesmo formato.

Meça primeiro: `wc -l -c <arquivo>`. Acima de ~150 mil caracteres, **não leia inteiro** — vá para o passo 3.

### 2. Aferir a qualidade da fonte antes de confiar nela

- **Turnos duplicados:** a pipeline de áudio reprocessa blocos, então falas aparecem duas vezes com timestamp deslocado. Conte antes de extrair (dedupe por corpo da fala) e trate a duplicação como normal, não como ênfase. Em sessão real, 16% dos turnos eram repetição.
- **Timestamps degradados:** no terço final o timestamp costuma repetir em quase todos os turnos (clamp da pipeline) ou vir como HH:MM:SS de relógio. **Nunca use timestamp como ordem ou posição** — use a ordem das linhas.
- **Falantes:** a ata costuma declarar confiabilidade (ex. "falantes 5/10, transcrição 3/10"). Nomes vêm deformados (Maxwell/Maxuel, Cléverton/Coelho/Kel, BiotechSE/Biotex, Solution Master/"Soluções Mágicas"). Atribua dono **só quando o nome é citado**; caso contrário marque confiança baixa.
- **Censo de rótulos antes de acreditar em qualquer nome.** Conte os rótulos do arquivo:
  `grep -o '^\[[^]]*\]' <arquivo> | sort | uniq -c | sort -rn`.
  (a) Leia o **bloco de abertura** (primeiros ~2 min): sessão que faz rodada de identificação de
  voz ("eu sou o Fulano") entrega ali a lista real de presentes — é a única atribuição de falante
  que se pode tratar como fato.
  (b) Se **um rótulo absorve a sessão** (centenas de turnos) e a pessoa daquele nome aparece só
  de passagem — ou não é do time —, o rótulo é **erro de diarização** cobrindo falas alheias.
  Nesse caso **nenhum** nome daquela sessão serve para atribuir dono: marque tudo como não
  atribuído e leve a dúvida ao usuário.

### 3. Minerar por candidatos (receita em `references/mineracao-transcricoes.md`)

Pipeline determinístico, na ordem: **dedupe → fatiar em sentenças → filtrar por regex de compromisso (PT-BR) → ler só os candidatos**. Isso reduz 260 mil caracteres a ~20 mil de candidatos, com recall alto para o que é ação.

Complemente lendo **integralmente o fechamento (últimos ~25%)**: é onde as sessões concentram metas, prazos, donos e próximos passos — e é justamente onde a diarização piora, então ali a leitura humana vale mais que o filtro.

### 4. Separar os tipos de item

Não misture as categorias ao reportar:

- **Decisão** — o que foi pactuado, com consequência prática.
- **Ação com dono** — quem faz o quê, com prazo literal quando houver.
- **Próximo passo anunciado** — encadeamento declarado pelo facilitador.
- **Item em aberto / estacionado** — o que ficou para depois por falta de decisão.

### 5. Cruzar ata × transcrição — sempre

A ata é o índice confiável, **não** a fonte completa: metas, valores e acordos comerciais hoje saem só da transcrição. Marque cada item como **"consta na ata"** ou **"só na transcrição"** e entregue as lacunas da ata em lista separada — é isso que o usuário cobra.

### 6. Entregar

Formato que funciona: numerar por sessão (`S1-3`, `S2-7`) para permitir cobrança depois; por item, dono nominal (ou "não atribuído" — nunca invente), prazo literal, evidência citada e a marca de confiança. Termine oferecendo o próximo passo: registrar os encaminhamentos como tarefas com dono/prazo, e consolidar na KB via `kb_note`/`kb_correct` (esta rama propõe, não escreve no canônico).

## Consulta dirigida — "o que a gente combinou sobre X?"

Pergunta do tipo "qual foi o rito/regra/decisão que combinamos na sessão N?" não é extração de encaminhamentos: é **rastreamento de um acordo específico**. Caminho certo, nesta ordem:

1. **Vá direto ao arquivo da reunião pela data no nome.** `ls <HERMES_HOME>/context-kb/sources/reunioes/meetings/ | grep <YYYY-MM-DD>`. O nome é `YYYY-MM-DD-HHMM-<título slugificado>` — busque pela data, porque o slug não casa com o nome que o usuário usa ("sessão 2 de planejamento" → `...-reuni-o-pe-sess-o-2.md`).
2. **`kb_search` não responde "o que foi falado".** As páginas de conceito (`rituals/`, `decisions/`, `projects/`) guardam a síntese; a mecânica exata combinada — as palavras que definem a regra — pode existir só no transcript bruto. Busca na KB voltando vazia para algo que você sabe que foi dito é sinal para descer ao `sources/`, não para variar a query (máx. 2-3 buscas, depois vá à fonte).
3. **Leia a ata primeiro** (blocos `## 3. Decisões` e `## 4. Ações/Pendências` do topo), **depois grepe o transcript** pelas palavras do usuário e pelos sinônimos próximos: `grep -n -iE "rito|ritual|cadência|semanal|check|telegram|cobrança|confirmar|OK"`. O grep devolve os turnos com timestamp — é a evidência que fecha a resposta.
4. **Cite os turnos com timestamp** e mostre a diferença entre as duas camadas: a **ata generaliza** ("entrega individualizada com confirmação de leitura"), o **transcript carrega a regra operacional como ela foi dita** (o gatilho, o mecanismo, quem cobra). Quem pergunta "o que a gente combinou" quer a segunda e costuma se lembrar de uma versão aproximada — corrija a versão dele com a citação, sem desmentir de graça.
5. **Compare com o estado real de hoje antes de dizer que o rito está de pé.** O acordo costuma estar registrado como ação "em andamento" e implementado pela metade (ex.: a entrega automática existe, a confirmação de leitura não). Entregue **rito × estado atual × o que falta** e ofereça o ajuste — é isso que o usuário cobra depois.

## Delegação em faixas (regra geral para fonte longa)

Subagente tem teto de relógio (~10 min) e **perde tudo** no estouro, inclusive o que já leu. Fonte longa se fatia, não se delega inteira:

1. **Fatie por faixa de linhas** (~700-900 por filho) e rode as faixas em paralelo; arquivo inteiro numa criança só = timeout sem artefato.
2. **Exija o artefato antes da resposta final** ("grave o arquivo primeiro, depois responda em ≤30 linhas"): filho que compõe narrativa longa primeiro entrega nada.
3. **O pai confere se o arquivo existe** depois de despachar — resumo de filho é auto-relato; o arquivo é a prova.
4. **Depois de um timeout, nunca redespache o mesmo escopo grande** — divida mais.
5. **Antes de delegar, tente o pré-filtro determinístico** (dedupe + regex) no processo pai: resolve a maior parte da extração sem subagente nenhum.

## Pitfalls

- **Ler a transcrição inteira "para não perder nada" é o erro que custa o contexto.** Minerar por candidatos + ler o fechamento cobre mais que a leitura linear e sobrevive ao limite de tempo.
- **Nunca delegue o arquivo inteiro a um subagente.** Subagente tem teto de relógio e devolve nada quando estoura — fatie por faixa de linhas e exija o artefato gravado antes da resposta final (regra em `autonomous-ai-agents`).
- **Confiar no timestamp** para reconstruir a ordem da conversa: inviável no fechamento das sessões, onde o timestamp é constante.
- **Tratar a ata como completa.** A ata sistematicamente omite metas numéricas, valores e acordos comerciais; e às vezes contradiz a transcrição ou a decisão de outra sessão (ex.: nome do supervisor de vendas). Divergência se reporta, não se resolve sozinha.
- **Atribuir dono por proximidade.** Falante mal diarizado não é dono da ação; sem nome citado, o dono é "não atribuído".
- **Deixar a dúvida de quem é quem se espalhar pelo artefato.** Quando a ambiguidade de nomes
  trava a atribuição de donos, faça **uma pergunta ao usuário, em bloco** (os nomes duvidosos +
  as divergências de dono/regra que você encontrou na fonte), em vez de marcar "a confirmar" item
  por item: uma resposta dele destrava o artefato inteiro, enquanto "a confirmar" repetido em
  cada linha deixa o plano sem dono nenhum — inutilizável para cobrar depois.
- **Transformar brainstorm em decisão.** Ideia discutida e não fechada vai para "item em aberto".
- **Concluir "isso não foi combinado" porque a KB não achou.** A síntese da KB não substitui o transcript: o acordo pode existir só no áudio bruto (regra operacional ditada ao agente, por exemplo). Vá ao arquivo da reunião antes de negar o fato — e não narre a busca vazia como se fosse resposta.

## Verificação

- [ ] Volume medido e estratégia de leitura declarada (mineração/faixa), não leitura cega.
- [ ] Duplicação e integridade de timestamp aferidas antes de extrair.
- [ ] Todo item tem evidência citada; dono e prazo sem invenção ("não atribuído"/"não informado").
- [ ] Itens separados por decisão / ação / próximo passo / em aberto, e por "consta na ata" × "só na transcrição".
- [ ] Lacunas da ata listadas em seção própria.
- [ ] Consulta sobre acordo passado: turnos citados com timestamp a partir do transcript, e comparação explícita entre o combinado e o que está implementado hoje.
