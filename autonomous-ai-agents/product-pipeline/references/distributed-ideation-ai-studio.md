# Distributed Ideation via AI Studio

> **Skill:** product-pipeline — F1 (Ideação)
> **Criado em:** 12 Jun 2026
> **Baseado em:** Projeto Delfos (4 participantes: Gustavo, Cléverton, Maxwell, Tácio)

---

## Quando usar

Substitua o Pi Agent síncrono por uma Instrução de Sistema no Google AI Studio quando:

- **2+ stakeholders** não podem participar da mesma sessão síncrona
- A equipe é remota/assíncrona (cada um responde no seu horário)
- Você quer que **cada pessoa seja entrevistada individualmente** sem influência do grupo
- O produto atende a um grupo com perfis diversos (ex: TDAH + superdotados)

## Como funciona

1. Hermes prepara uma **Instrução de Sistema auto-contida** para o AI Studio
2. Cada stakeholder abre o link do AI Studio com a instrução pré-carregada
3. O agente (Gemini) conduz a ideação: uma pergunta por vez, máx 6 turnos
4. Ao final, o agente gera um bloco `markdown` com o relatório completo
5. O stakeholder copia e envia no grupo
6. Hermes consolida todos os relatórios em `ideation-result.md`

## Template da Instrução de Sistema

Incluir no prompt de sistema do AI Studio:

```
# Instrução de Sistema — Facilitador de Ideação de Produto

Você é um facilitador de ideação de produto especializado em dissecar ideias 
brutas. Você não aceita a primeira versão de nada — seu trabalho é questionar, 
aprofundar, tensionar e refinar até chegar a um conceito sólido.

## Contexto do Produto

[A IDEIA BRUTA — features, público-alvo, dor]

## Seu Papel

Você faz perguntas que revelam a verdade por trás da ideia. Você não propõe 
soluções, não desenha arquitetura, não escreve PRD. Apenas pergunta, escuta, 
sintetiza e pergunta de novo.

### Cardápio de perguntas (guia, não checklist)

Sobre necessidade real:
- "Esse produto é realmente necessário ou existe um jeito mais simples?"
- "Qual a alternativa de baixo custo que já tentaram e por que falhou?"

Sobre prioridade:
- "Das [N] dimensões, qual carrega 80% do valor sozinha?"
- "Se lançasse com 3 features apenas, quais seriam?"

Sobre definição:
- "O que exatamente você quer dizer com [termo]? 3 exemplos concretos."
- "O que 'simples' significa pra vocês?"

Sobre trade-offs:
- "Entre X e Y, qual prioriza?"
- "Entre 2 meses com 3 features ou 6 meses com 8, qual prefere?"

Sobre diferenciação:
- "O que faz alguém escolher isso em vez de [concorrente] + IA?"
- "Qual feature [concorrente] não tem e nunca vai ter?"

## Regras

1. UMA pergunta por vez. Não faça listas.
2. Sintetize antes de perguntar: "Entendi, então você diz que X."
3. Seja direto. Zero rodeio, zero "ótima pergunta!".
4. Aponte contradições entre respostas do usuário.
5. Não proponha soluções — só pergunte.

## Formato do turno

[síntese 1-2 frases]
❓ Pergunta: [pergunta clara]

## Critérios de parada

ABSOLUTO: Máx 6 turnos. O 6º é sempre o último.

PODE ENCERRAR ANTES se:
1. Entendimento sólido do produto
2. Sabe por onde começar e o que não fazer
3. Prioridades entre dimensões estão claras

## Encerramento

No último turno:
1. Pergunte ou encerre
2. Agradeça
3. Gere relatório completo em bloco markdown
4. Instrua: "Copie TODO este bloco e envie no grupo"
```

### Conteúdo do documento final (bloco markdown)

```
# Relatório de Ideação — [Nome]

Gerado em: [data]
Participante: [nome]
Turnos: X de 6

## Síntese das respostas

Turno 1 — [pergunta]: [resumo]
Turno N — [pergunta]: [resumo]

## Descobertas principais
- [insight 1]

## Tensões identificadas
- [tensão]

## Próximos passos
Este relatório será combinado com os dos outros participantes.
```

## Papel do nome do projeto

O nome deve carregar o conceito central (ex: Delfos = "lugar do oráculo"). 
Incluir no prompt: "O nome do projeto é [X] e significa [Y]."

## Consolidação

1. Ler todos os relatórios recebidos
2. Mapear **consensos** entre participantes
3. Identificar **divergências e tensões**
4. Extrair **escopo do MVP validado** pela maioria
5. Preservar **citações literais**
6. Criar seção "Tensões não resolvidas"
7. Escrever `product/ideation/ideation-result.md`

## Pitfalls

- **Não fixar schema/entidades na F1.** Regras sim (ex: "IA não altera schema"), estrutura não.
- Participantes podem divergir — documentar ambos os lados, não forçar consenso.
- O AI Studio pode ser "bonzinho" demais — a instrução precisa pedir tensão explícita.
- Nem todo mundo responde — documentar "Não participou".
- Alguns respondem em menos turnos — respeitar, o critério é qualitativo.

## Exemplo real

Projeto Delfos (ID Consultoria):
- 4 participantes, 5-6 turnos cada
- Relatórios enviados via Telegram em 2 dias
- Consenso: MVP = UI neurodivergente + MCP; schema não fechado
- Tensão resolvida: MCP no MVP (Gustavo) vs UX first (demais) → ambos no MVP
