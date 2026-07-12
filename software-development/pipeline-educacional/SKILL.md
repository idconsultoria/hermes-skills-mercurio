---
name: pipeline-educacional
description: "Pipeline de produto educacional — da concepção pedagógica ao lançamento.

Carregue esta skill quando for projetar um curso, treinamento, bootcamp ou jornada de aprendizado. Cobre a pipeline completa do design instrucional: análise de público, definição de objetivos, design de conteúdo, produção, lançamento e iteração contínua. Base de referência em IA e design instrucional (ADDIE, Backward Design, SAM, Kirkpatrick)."
version: 2.0.2
author: Gustavo Mello (via Hermes)
tags: [educação, curso, treinamento, pipeline, produto-educacional, design-instrucional]
related_skills: [copywriting, ideation-drilling, product-pipeline, backwards-design-unit-planner, scope-and-sequence-designer, curriculum-knowledge-architecture-designer, competency-framework-translator, leverage-and-response-design, mental-model-mapper]
type: Orchestrator
timestamp: 2026-07-12T00:00:00Z
---

# Pipeline de Produto Educacional

> **Orquestrador:** Hermes
> **Domínio:** Produtos educacionais — cursos, treinamentos, bootcamps, jornadas de aprendizado
> **Base teórica:** ADDIE, Backward Design (Wiggins & McTighe), SAM (Allen), Kirkpatrick 4 Níveis

## Preferências do Usuário

Este bloco codifica preferências de estilo de trabalho de quem usa este pipeline. Carregar sempre.

- **Direto e pragmático:** Quer entrega, não explicação. "Faça", "Cheque", "Mande aqui" são comandos.
- **Correções são diretas:** Aplicar feedback em TODAS as seções afetadas imediatamente.
- **Zero jargão corporativo:** Comunicação limpa, sem palavras proibidas (elevate, empower, seamless, leverage, alavancar, desbloquear, revolucionar).
- **Zero anglicismos:** Usar equivalente em português sempre que possível. Exceção: nomes próprios de ferramentas e plataformas.
- **Documentos enxutos:** Sem poluição de fontes inline. Sem metadados de pesquisa no corpo.
- **Entregar arquivos, não descrições:** Salvar em disco e referenciar o path.

### Substituições obrigatórias (PT-BR)

| Evite | Use |
|-------|-----|
| mindset | mentalidade / visão |
| deadline | prazo |
| feedback | retorno |
| onboarding | integração / ambientação |
| deploy | implementar |
| benchmark | referência / comparativo |
| workflow | fluxo de trabalho |
| open-source (verbo) | disponibilizar em código aberto |
| ship / shipar | entregar / lançar |

---

## Fundamentos Teóricos

Este pipeline integra 4 frameworks de design instrucional. Nenhum é obrigatório — use o que serve ao projeto.

> **Referência expandida:** `references/design-instrucional-benchmarks.md` — dados completos de benchmarks, frameworks e criadores de curso.
> **Ecossistema de skills:** `references/external-skills-ecosystem.md` — como buscar e instalar skills de Claude Code, OpenCode, Codex.
> **Entrega cross-platform:** `references/cross-platform-delivery.md` — padrão de entrega de arquivos do TUI para canais de mensageria.

### ADDIE — Estrutura completa (1975, Florida State University)

| Fase | Pergunta-chave | Artefatos |
|---|---|---|
| **Analysis** | Qual o gap entre o que o aluno sabe e o que precisa saber? | Learner persona, análise de necessidades, restrições técnicas |
| **Design** | Como vamos preencher esse gap? | Objetivos de aprendizagem, storyboard, plano de avaliação |
| **Development** | Produzir o conteúdo e materiais | Aulas gravadas, slides, exercícios, templates |
| **Implementation** | Entregar aos alunos | Roteiro de facilitação, onboarding, canais de comunicação |
| **Evaluation** | Funcionou? | Relatório de avaliação, NPS, métricas de conclusão |

### Backward Design — Comece pelo fim (Wiggins & McTighe, 2005)

**Princípio:** Só planeje as aulas depois de definir o que o aluno deve PRODUZIR.

| Estágio | Ação |
|---|---|
| **1. Resultados desejados** | O que o aluno vai PENSAR e FAZER ao final? Use Bloom's Taxonomy (verbos de ação mensuráveis) |
| **2. Evidências** | Como provar que aprendeu? Projeto final, rubricas, critérios de aceitação |
| **3. Experiências** | Só agora: planejar aulas, atividades, materiais |

**Backward Design é o melhor fit para cursos práticos** porque força o alinhamento entre objetivos → avaliação → conteúdo. Ideal para cursos orientados a projeto e competência.

### SAM — Desenvolvimento ágil (Allen)

**Princípio:** "Progress over perfection" — prototipar rápido, testar, iterar.

| Fase | Ação |
|---|---|
| **Preparation** | Reunião inicial (Savvy Start) com stakeholders. Rascunhar o curso inteiro em 1-2 dias |
| **Iterative Design** | Prototipar → testar com 3-5 beta testers → ajustar → repetir |
| **Iterative Development** | Alpha (funcional completo) → Beta (corrigido) → Gold (versão de mercado) |

**Ideal para cursos de tecnologia** onde ferramentas e conteúdo envelhecem rápido.

### Kirkpatrick 4 Níveis — Avaliação de eficácia (1959)

| Nível | Pergunta | Aplicação prática |
|---|---|---|
| **1 — Reação** | Os alunos acharam relevante? | NPS, pulse check semanal |
| **2 — Aprendizagem** | Adquiriram conhecimento e CONFIANÇA? | Projeto entregue, demonstração prática |
| **3 — Comportamento** | Estão APLICANDO no trabalho? | Follow-up 30/60/90 dias |
| **4 — Resultados** | Gerou impacto mensurável? | Horas economizadas, projetos implementados |

---

## Estrutura do Projeto

```
meu-curso/
├── produto/
│   ├── concepcao/
│   │   ├── analise-publico.md         # Quem são os alunos, dores, objetivos
│   │   ├── definicao-niveis.md        # Se houver múltiplos níveis: progressão entre eles
│   │   └── promessa.md                # Transformação prometida, diferencial, objeções
│   ├── design-instrucional/
│   │   ├── objetivos-aprendizagem.md   # Bloom Taxonomy: o que o aluno SABE FAZER ao final
│   │   ├── mapa-modulos.md            # Estrutura de módulos com carga horária
│   │   ├── sequenciamento.md          # Ordem pedagógica e pré-requisitos
│   │   └── estrategia-avaliacao.md    # Como medir aprendizado (Kirkpatrick)
│   ├── producao/
│   │   ├── roteiros/                  # Roteiro detalhado de cada módulo (template abaixo)
│   │   ├── materiais-apoio/           # Aprofundamento opcional
│   │   └── projetos-praticos/         # Projeto(s) que percorrem o curso
│   ├── validacao/
│   │   ├── teste-piloto.md            # Resultado com alunos beta
│   │   └── ajustes-pre-lancamento.md
│   ├── lancamento/
│   │   ├── cronograma-turmas.md
│   │   ├── precificacao.md
│   │   └── pagina-vendas.md           # Copy de conversão
│   └── operacao/
│       ├── plataforma.md
│       ├── fluxo-matricula.md
│       └── metricas.md                # NPS, conclusão, retenção, conversão
├── site/
├── assets/
└── referencias/
```

---

## Fases do Pipeline

```
[Demanda] → F1: Concepção → F2: Design Instrucional → F3: Produção → F4: Validação → F5: Lançamento → F6: Iteração
```

---

## Fase 1: Concepção

**Objetivo:** Definir PARA QUEM, QUAL a transformação e COMO se diferencia.

> **Skills de apoio:** `competency-framework-translator` — para mapear competências entre níveis. `mental-model-mapper` — para identificar modelos mentais dos alunos e calibrar a promessa.

### Processo

1. **Análise de público-alvo:**
   - Perfil demográfico e técnico (cargo, nível de conhecimento, ferramentas que já usa)
   - Dores e objetivos (o que quer resolver? O que já tentou?)
   - Pré-requisitos reais (não idealizados)
   - Por que compraria ISSO e não outra coisa?

2. **Definição da promessa:**
   - Transformação específica em uma frase
   - Ganho concreto (produtividade, economia, novo skill)
   - Diferencial vs. alternativas (YouTube, concorrentes, aprender sozinho)
   - Objeções antecipadas e respostas

3. **Se houver múltiplos níveis ("escadinha"):**
   - O que cada nível entrega e onde o aluno chega
   - Pré-requisitos entre níveis (validar que N-1 cobre o que N exige)
   - Gatilhos de transição: o que faz o aluno querer o próximo?

4. **Validação de demanda:**
   - Quantas pessoas demonstraram interesse?
   - Existe disposição a pagar validada (pré-venda, comparação com similares)?

### Saída
```
produto/concepcao/
├── analise-publico.md
├── definicao-niveis.md    (se escadinha)
└── promessa.md
```

### Marcador
`<!-- PHASE_COMPLETE: concepcao -->`

---

## Fase 2: Design Instrucional

**Objetivo:** Estruturar pedagogicamente — o que o aluno aprende, em que ordem, com quais atividades e como medimos.

> **Skills de apoio:** `backwards-design-unit-planner` — operacionaliza o planejamento backward design. `scope-and-sequence-designer` — define escopo e sequência de módulos. `curriculum-knowledge-architecture-designer` — audita a arquitetura de conhecimento do currículo.

### Processo (Backward Design)

#### 2.1 Objetivos de Aprendizagem (Estágio 1)

Para cada curso/nível:

- **Objetivo terminal:** Ao final, o aluno É CAPAZ DE... (1 frase com verbo de ação)
- **Objetivos específicos:** 4–6 objetivos mensuráveis

Use Bloom's Taxonomy (verbos): Criar, Avaliar, Analisar, Aplicar, Compreender, Lembrar.

> Ruim: "Entender o assunto X"
> Bom: "Construir um X funcional que resolve Y em menos de Z minutos"

#### 2.2 Evidências de Aprendizagem (Estágio 2)

- **Projeto prático:** O que o aluno CONSTRÓI durante o curso?
- **Checkpoints:** Marcos intermediários onde verificamos progresso
- **Sessões ao vivo:** Espaço para destravar projetos (se aplicável)
- **Rubricas:** Critérios objetivos de "entregue com sucesso"

#### 2.3 Mapa de Módulos (Estágio 3)

Só agora planejar as aulas. Para cada módulo:

| Campo | Descrição |
|---|---|
| **Título** | Focado no RESULTADO, não no conteúdo |
| **Duração** | Carga horária total (ex: 2h) |
| **Objetivo** | O que o aluno SABE FAZER ao final deste módulo |
| **Tópicos** | 4–6 tópicos em sequência lógica |
| **Mão na massa** | O que o aluno CONSTRÓI neste módulo |
| **Conexão com projeto** | Como este módulo avança o projeto prático |
| **Pré-requisitos** | O que precisa ter feito antes |

#### 2.4 Sequenciamento

- Ordem dos módulos e por quê
- Dependências entre tópicos
- Rotas alternativas (dá para pular? dá para fazer em ordem diferente?)

#### 2.5 Estratégia de Avaliação (Kirkpatrick)

| Nível | Como aplicar |
|---|---|
| **1 — Reação** | NPS ao final de cada módulo, pesquisa de satisfação |
| **2 — Aprendizagem** | Projeto prático funcional como evidência (não quiz) |
| **3 — Comportamento** | Follow-up 30 e 90 dias: o aluno aplicou? |
| **4 — Resultados** | Ganho de produtividade, economia, projetos implementados |

### Saída
```
produto/design-instrucional/
├── objetivos-aprendizagem.md
├── mapa-modulos.md
├── sequenciamento.md
└── estrategia-avaliacao.md
```

### Marcador
`<!-- PHASE_COMPLETE: design-instrucional -->`

---

## Fase 3: Produção de Conteúdo

**Objetivo:** Transformar o design instrucional em conteúdo real.

### Processo

#### 3.1 Roteiros de Aula

Template para cada módulo:

```markdown
# Módulo X: [Título focado em resultado]

## Metadados
- Duração: [carga horária]
- Pré-requisitos: [links para módulos anteriores]
- Projeto prático: [referência]

## Roteiro

### Abertura (5 min)
- Gatilho: problema real que o aluno enfrenta
- Promessa: o que vai conseguir fazer ao final

### Tópico 1: [Nome] ([duração])
- Conceito: explicação direta
- Demonstração: mostrando na prática
- Mão na massa 1: o aluno executa

### Tópico 2: [Nome] ([duração])
...

### Tópico N: [Nome] ([duração])
...

### Fechamento (5-10 min)
- Recap: o que construímos
- Próximo passo antes da próxima aula
```

> **Regra de ouro:** Se o aluno pausar a cada 5 minutos, ele conseguiu reproduzir? Se não, o ritmo está errado.

#### 3.2 Duração de Conteúdo

Referência de mercado (para calibrar):

| Fonte | Duração por unidade |
|---|---|
| **DeepLearning.AI** | 5–15 min por vídeo (micro-learning) |
| **Fast.ai** | 90 min por lição |
| **Maven (cohort)** | 90–120 min por live session |
| **Coursera** | 5–15 min por vídeo |

**Recomendação:** Dividir sessões longas em pílulas de 15–20 min para maximizar retenção. Agrupar pílulas em módulos temáticos.

#### 3.3 Materiais de Apoio

Material de aprofundamento **opcional**:
- Guias escritos com fundamentos
- Diagramas e esquemas visuais
- Leituras complementares
- Templates e arquivos de configuração

> Princípio: o material de apoio é para quem quer ir além. A aula se basta sozinha.

#### 3.4 Projetos Práticos

Cada curso tem um projeto que percorre todos os módulos. O projeto é a espinha dorsal — cada módulo avança uma parte dele.

### Saída
```
produto/producao/
├── roteiros/
│   └── modulo-X.md
├── materiais-apoio/
└── projetos-praticos/
```

### Marcador
`<!-- PHASE_COMPLETE: producao -->`

---

## Fase 4: Validação (Piloto)

**Objetivo:** Testar com alunos reais antes do lançamento oficial.

### Processo

1. **Selecionar beta testers:** 3–8 alunos. Diversidade de background.
2. **Rodar o piloto** no mesmo formato do curso real.
3. **Coletar dados:**
   - Taxa de conclusão por módulo
   - Tempo médio por módulo
   - Perguntas mais frequentes
   - NPS por módulo e geral
   - Depoimentos (com autorização)
4. **Ajustar:** Clareza de roteiros, ritmo, tópicos desnecessários, gaps de conteúdo.

### Saída
```
produto/validacao/
├── teste-piloto.md
└── ajustes-pre-lancamento.md
```

### Marcador
`<!-- PHASE_COMPLETE: validacao -->`

---

## Fase 5: Lançamento

**Objetivo:** Estruturar a operação de venda e entrega.

### Processo

#### 5.1 Cronograma de Turmas

| Elemento | Definição |
|---|---|
| Abertura de matrículas | Data |
| Início da turma | Data |
| Duração | N semanas |
| Intervalo entre turmas | Se houver |
| Lives/Sessões ao vivo | Dias e horários fixos |
| Limite de alunos | Máximo por turma |

#### 5.2 Precificação

| Campo | Descrição |
|---|---|
| Preço base | Valor |
| Justificativa | Horas de conteúdo, suporte ao vivo, material incluso |
| Comparação | Quanto custam alternativas similares? |
| Descontos | Early bird, pacotes, ex-alunos |
| Garantia | Período e condições |

**Referência de mercado para calibrar preço:**

| Modelo | Faixa típica | Exemplos |
|---|---|---|
| **Cohort premium** | $500–$5.000/aluno | Maven, Reforge |
| **Assinatura all-inclusive** | $25–59/mês | DeepLearning.AI, Coursera Plus, Alura |
| **Marketplace one-time** | $47–500 | Hotmart, Udemy |
| **Gratuito + upsell** | $0 → $500 (avançado) | Fast.ai |

#### 5.3 Página de Vendas

Estrutura de copy:
- **Headline:** Promessa + ganho concreto
- **Subheadline:** Para quem é, o que entrega
- **Seções:** Problema → Solução → Ementa → Prova social → Instrutor → Preço → CTA
- **FAQ:** Objeções reais respondidas

> Skill de apoio: `copywriting` para headlines, CTAs e copy de conversão.

#### 5.4 Fluxo de Matrícula

```
Aluno → página de vendas → CTA → checkout/pagamento → confirmação → acesso ao conteúdo
```

### Saída
```
produto/lancamento/
├── cronograma-turmas.md
├── precificacao.md
└── pagina-vendas.md
```

### Marcador
`<!-- PHASE_COMPLETE: lancamento -->`

---

## Fase 6: Iteração

**Objetivo:** Coletar dados da turma real e melhorar continuamente.

> **Skill de apoio:** `leverage-and-response-design` — identifica alavancas de alto impacto no sistema educacional para priorizar iterações.

### Processo

1. **Durante o curso:** NPS por módulo, taxa de conclusão, presença em lives, dúvidas recorrentes.
2. **Pós-curso:** NPS geral, ganho reportado, depoimentos, conversão para próximos níveis.
3. **Priorizar melhorias:** impacto × esforço. O que gerou mais atrito? O que os alunos pediram?
4. **Aplicar:** Atualizar roteiros, ajustar ritmo, melhorar materiais.

### Métricas-chave

| Métrica | Alvo saudável | Ação se abaixo |
|---|---|---|
| **NPS** | ≥ 80 | Investigar módulos com menor nota |
| **Taxa de conclusão** | ≥ 80% | Ritmo adequado? Pré-requisitos cobertos? |
| **Presença em lives** | ≥ 60% | Ajustar dia/horário, reforçar valor da live |
| **Conversão N→N+1** | ≥ 40% | Gatilhos de transição entre níveis |
| **Tempo médio por módulo** | ≤ 1.5× o planejado | Simplificar tópicos complexos |
| **Retenção (se assinatura)** | ≥ 85% | Conteúdo novo com frequência adequada? |

### Saída
```
produto/operacao/
├── plataforma.md
├── fluxo-matricula.md
└── metricas.md
```

### Marcador
`<!-- PHASE_COMPLETE: iteracao -->`

---

## Apêndice A: Benchmarks de Mercado (Cursos de IA)

Dados de referência coletados em julho/2026. Use para calibrar decisões de formato, duração e preço.

### Formato dominante: Cohort-Based Courses (CBCs)

O modelo de "turma fechada com data de início/fim + comunidade + lives + projetos" domina o segmento premium.

| Elemento | Padrão |
|---|---|
| Duração | 4–6 semanas |
| Lives | 1–2 por semana, 90–120 min |
| Conteúdo gravado | 70% assíncrono / 30% síncrono |
| Projeto | Obrigatório, semanal + capstone |
| Comunidade | Slack/Discord privado por turma |
| Preço | $500–$5.000 |

**Wes Kao (Maven) — 12 alavancas de design de curso:**
1. Duração (4–6 semanas para cursos profundos)
2. Número de alunos (8–15 primeira turma, 30+ com TAs)
3. Preço (reflete transformação prometida, não horas de conteúdo)
4. Intensidade (mais intensidade = mais transformação)
5. Orientado a projeto (cursos com capstone > cursos só de conteúdo)
6. Interação em grupo (breakout rooms, peer feedback)
7. Envolvimento de coaches (TAs que dão feedback individualizado)
8. Presença do instrutor (nas lives e na comunidade)
9. Qualidade de produção (gravação, slides, materiais)
10. Conteúdo pré-gravado (liberado antes da live)
11. Processo seletivo (filtro de entrada aumenta comprometimento)
12. Frequência de turmas (quantas por ano)

### Equilíbrio teoria/prática

| Plataforma | Teoria | Prática |
|---|---|---|
| Maven | 30% | 70% |
| Fast.ai | 20% | 80% |
| DeepLearning.AI | 50% | 50% |
| Coursera | 40% | 60% |

**Padrão ouro:** 70–80% prática. Mínimo aceitável: 50%.

### Progressão em níveis (escadinha)

**Achado:** Quase ninguém empacota cursos em trilha integrada de 3 níveis com upsell. DeepLearning.AI tem progressão implícita; Maven tem cursos separados com upsell manual. Uma trilha integrada é **diferencial competitivo real**.

### Comunidade como produto

Em cursos premium, comunidade **não é opcional — é o core product**. Elementos que justificam preço:
- Comunidade privada ativa (Slack/Discord/WhatsApp)
- Office hours semanais
- Guest lectures de parceiros
- Acesso vitalício ao conteúdo + comunidade pós-curso
- Alumni network

---

## Apêndice B: Framework Híbrido Recomendado

Para cursos práticos (qualquer domínio), a combinação mais eficaz:

```
BACKWARD DESIGN  →  SAM (Desenvolvimento)  →  KIRKPATRICK (Avaliação)
(Design curricular)  (Prototipagem ágil)     (Medição de eficácia)
       +                      +                        +
  ADDIE (Documentação e estrutura BASE)
```

### Ritmo semanal recomendado

```
Segunda: Módulo novo liberado (vídeos de 15-20 min + material)
Terça–Quarta: Alunos assistem e fazem exercício prático
Quinta: Sessão ao vivo (20 min revisão + 40 min prática/coaching)
Sexta: Entrega do checkpoint semanal
Sábado (opcional): Office hours
```

### Princípios operacionais

1. **Todo módulo tem OUTPUT:** Nenhum módulo termina sem algo construído
2. **80% COMO, 20% O QUÊ:** Conteúdo focado em execução prática
3. **Feedback em <24h:** Alunos recebem retorno rápido sobre seus projetos
4. **Comunidade ativa:** Discussões estruturadas, não "qualquer dúvida?"
5. **Instrutor presente:** Lives ao vivo, participação na comunidade
6. **Ritmo previsível:** Mesma cadência toda semana reduz ansiedade
7. **Semana zero:** Setup técnico antes do conteúdo começar (onboarding week)

---

## Apêndice C: Skills de Educação Instaladas

Skills do ecossistema `education-agent-skills` (GarethManning, CC BY-SA 4.0) instaladas e disponíveis. Carregue com `/skill <nome>` quando a fase correspondente exigir.

| Skill | Fase | Uso |
|-------|------|-----|
| `competency-framework-translator` | F1 — Concepção | Mapear competências entre níveis da escadinha |
| `mental-model-mapper` | F1 — Concepção | Identificar modelos mentais do público-alvo |
| `backwards-design-unit-planner` | F2 — Design Instrucional | Operacionalizar planejamento backward design |
| `scope-and-sequence-designer` | F2 — Design Instrucional | Definir escopo e sequência de módulos |
| `curriculum-knowledge-architecture-designer` | F2 / F4 — Design / Validação | Auditar arquitetura de conhecimento do currículo |
| `leverage-and-response-design` | F6 — Iteração | Identificar alavancas de alto impacto para melhoria contínua |

## Pitfalls

⚠️ **Não confundir design instrucional com criação de conteúdo.** Design define O QUE e EM QUE ORDEM. Produção é COMO. Não pule para roteiros antes de ter objetivos de aprendizagem.

⚠️ **Síndrome do especialista:** Você sabe MUITO mais que o aluno. O "óbvio" para você, o aluno nunca viu. Teste com alguém do público-alvo real.

⚠️ **Material de apoio não substitui aula.** Se o aluno precisa ler o material para entender a aula, o design falhou.

⚠️ **Sessão ao vivo não é repeteco da gravada.** Live serve para DESTRAVAR projetos. Se virar aula 2, você duplicou trabalho e frustrou quem assistiu a gravada.

⚠️ **Taxa de conclusão é a métrica mais importante.** NPS 100 com 10% de conclusão = produto quebrado.

⚠️ **Pré-requisitos reais, não idealizados.** Se um nível exige conhecimento X e o nível anterior não ensinou X, você perdeu o aluno.

⚠️ **Vídeos longos têm baixa retenção.** Referência: pílulas de 15–20 min (DeepLearning.AI). Vídeos de 2h são o limite superior. Considere dividir.

⚠️ **Precificação não é aleatória.** O preço comunica posicionamento. Compare com similares e justifique o delta.

⚠️ **SAM sem disciplina vira caos.** Iterar rápido não significa pular etapas. Cada ciclo precisa de feedback real antes do próximo.

⚠️ **Kirkpatrick Nível 3 é o mais negligenciado.** Follow-up pós-curso é o que separa curso bom de curso transformacional. Ninguém faz — é diferencial.

⚠️ **Backward Design parece contra-intuitivo.** É tentador começar planejando aulas. Resista: comece pelo projeto final.

⚠️ **Comunidade sem moderação morre.** Designar alguém para puxar discussões, responder dúvidas, manter o espaço vivo.

⚠️ **Garantia de reembolso é sinal de confiança, não de fraqueza.** Write of Passage (David Perell) oferece 14 dias sem perguntas. Isso AUMENTA conversão.

⚠️ **Busque skills em todo o ecossistema de agentes, não só no hub Hermes.** Skills compatíveis com o padrão Agent Skills 1.0 existem em repositórios de Claude Code, OpenCode, Codex e Cursor. Antes de criar uma skill, pesquise na web com `"agent-skills" <domínio> github` e `"SKILL.md" <domínio>`. Ex: `education-agent-skills` (GarethManning, 395★) tem 165 skills pedagógicas compatíveis com Hermes, encontrado via ecossistema Claude Code.

⚠️ **Filtre skills externas — não instale tudo.** Ao encontrar um repositório com dezenas de skills, analise quais são diretamente úteis para a tarefa atual e instale só essas. Ex: das 165 skills do `education-agent-skills`, apenas 7 (4,2%) eram relevantes para produto educacional. Instalar tudo polui o catálogo e reduz a qualidade das recomendações.

⚠️ **Nome de skill deve ser generalista, não domínio-específico.** `pipeline-educacional`, não `pipeline-curso-ia`. Se o nome só faz sentido para o projeto da sessão atual, está errado. Skills são classes de tarefa, não artefatos de uma sessão.

⚠️ **Pesquisa com subagentes: 1 por seção, não 3 para o documento inteiro.** Quando o documento tem múltiplas seções que dependem de dados externos (estratégia, GTM, precificação, operação), spawne pelo menos **1 subagente por seção**. Ex: documento de 9 seções = 6–9 subagentes em 2–3 rodadas. Subagentes de tema amplo produzem generalidades; subagentes focados em uma seção produzem dados utilizáveis. Lote em rodadas para respeitar o limite de paralelismo.

⚠️ **Entrega cross-platform a partir do TUI:** `MEDIA:` não atravessa plataformas na sessão atual. Para entregar arquivos em canais de mensageria (Telegram, WhatsApp, etc.), use `cronjob` one-shot com `deliver` apontando para o destino. Ex: `cronjob(action='create', schedule='<ISO>', prompt='Entregue MEDIA:/path/arquivo.zip', deliver='telegram')`.
