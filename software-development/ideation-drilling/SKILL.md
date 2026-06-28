---
name: ideation-drilling
description: "Product ideation (Fase 1): refine raw ideas through structured drilling.

Load this skill at the start of the product pipeline (Fase 1) when the user has a raw idea for a product or feature. Covers structured ideation drilling, user interview integration, competitor analysis, and producing a refined product concept ready for further pipeline stages."
category: software-development
type: Orchestrator
timestamp: 2026-06-12T02:23:22Z
---

# Ideation Drilling (Hermes — Orchestrator)

> Skill orquestradora. Chama o Pi Agent com `/skill:ideation-drilling` para
> conduzir a fase de ideação, gerencia o projeto, e captura o resultado.

## Quando Usar

- O usuário diz: "Tenho uma ideia para um produto/feature"
- O usuário pede: "Me ajude a refinar essa ideia"
- Início do pipeline de produto (Fase 1)
- A brief está vaga, contraditória ou incompleta

## Pré-requisitos

- Pi Agent acessível via `oracle-host` → `pi-agent`
- Skill `ideation-drilling` instalada no Pi em `~/.pi/agent/skills/ideation-drilling/`
- Shared Volume ativo: `/opt/data/code/<projeto>` (Hermes) = `/workspace/code/<projeto>` (Pi)
- Modelos definidos: `best` = `opencode-go/minimax-m3`, `cost-effective` = `deepseek/deepseek-v4-flash`

## Fluxo

```
1. Hermes pergunta o nome/natureza do projeto
2. Hermes cria estrutura: /opt/data/code/<projeto>/
   ├── product/
   │   └── ideation/
   │       └── (vazio por enquanto)
   └── (outros diretórios criados pelas fases seguintes)
3. Hermes invoca Pi via SSH com skill e contexto inicial
4. Pi conduz ideation drilling (própria skill dele)
5. Pi escreve ideation-result.md no shared volume
6. Hermes detecta <!-- PHASE_COMPLETE: ideation -->
7. Hermes copia ideation-result.md para product/ideation/
8. Hermes confirma conclusão e avança para Fase 2
```

## Execução Passo a Passo

### Passo 1: Entender a Ideia

Pergunte ao usuário:
1. **Qual o nome do projeto?** (nome-para-pasta, lowercase, hífens)
2. **Qual a ideia em uma frase?** (brief inicial)

Decida se o drilling deve ser feito **por você (Hermes)** ou **delegado ao Pi**:

| Cenário | Quem faz drilling |
|---------|------------------|
| Ideia técnica de software | Pi (melhor para código/tech) |
| Ideia de produto/serviço | Pi |
| Ideia de conteúdo/sistema/flow | Hermes (você mesmo) |
| Usuário quer conversar rápido | Hermes |
| Pipeline completo de produto | Pi (modelo superior opencode-go/minimax-m3) |

> Para o pipeline de produto descrito no SOUL.md, **sempre delegue ao Pi**
> com modelo superior. Você orquestra; ele faz o trabalho pesado de ideação.

### Passo 2: Preparar Estrutura do Projeto

**Via Pi** (única forma de escrever no shared volume):

```bash
ssh oracle-host 'pi-shell "mkdir -p /workspace/code/PROJETO/product/ideation && \
  cd /workspace/code/PROJETO && git init && \
  git add -A 2>/dev/null; git commit -m \"chore: init project structure\" 2>/dev/null || true"'
```

Substitua `PROJETO` pelo nome do projeto.

### Passo 3: Invocar Pi com Ideation Drilling

Use o modelo **best** (MiniMax M3 via OpenCode Go) e **cost-effective** (DeepSeek v4 Flash via DeepSeek API):

```bash
# Montar contexto inicial com a brief do usuário
CONTEXT="O usuário quer construir: [BRIEF DO USUÁRIO]

Projeto: <projeto>
Diretório de trabalho: /workspace/code/<projeto>

Sua missão é carregar /skill:ideation-drilling e conduzir a ideação.
Quando terminar, escreva ideation-result.md em product/ideation/.
Inclua o marcador <!-- PHASE_COMPLETE: ideation --> ao final do documento."

# Invocar Pi com modelo BEST (MiniMax M3)
ssh oracle-host "LC_DIR=code/<projeto> pi-agent \\
  'pi -p \"$CONTEXT\" --provider opencode-go --model minimax-m3'"

# Para tarefas repetitivas, usar modelo COST-EFFECTIVE (DeepSeek v4 Flash)
ssh oracle-host "LC_DIR=code/<projeto> pi-agent \\
  'pi -p \"$CONTEXT\" --provider deepseek --model deepseek-v4-flash'"
```

> **Nota:** O provider `opencode-go` usa a chave `OPENCODE_API_KEY`. O provider `deepseek` usa `DEEPSEEK_API_KEY`. Ambos já devem estar configurados no `.env` do Pi.

> **Nota:** O Pi precisa de permissão para escrever arquivos. A skill instrui
> o Pi a criar o `ideation-result.md`. Como o shared volume já está montado,
> o Pi escreve em `/workspace/code/<projeto>/` que = `/opt/data/code/<projeto>/`.

### Passo 3b: Alternativa — Hermes faz o drilling diretamente

Se decidiu que Hermes faz o drilling (não delega ao Pi):

1. Carregue **esta mesma skill** e siga o protocolo de drilling descrito abaixo
2. Use o mesmo formato de `ideation-result.md`
3. Inclua o marcador `<!-- PHASE_COMPLETE: ideation -->`

O protocolo de drilling é o mesmo que está na skill do Pi (veja as seções abaixo).

### Passo 3c: Alternativa — AI Studio (ideação assíncrona multi-participante)

Quando a ideação precisa envolver **2+ pessoas que não podem participar da mesma sessão síncrona** — cada pessoa roda seu próprio agente no Google AI Studio, no seu ritmo, e os relatórios são compilados depois.

#### Cenários típicos

- Equipe com 3+ stakeholders em horários diferentes
- Participantes sem acesso ao Pi Agent / Hermes
- Precisa-se de respostas independentes, sem influência entre participantes
- Briefing inicial já rico o suficiente para drilling individual

#### Fluxo

1. **Hermes cria** um prompt de sistema auto-contido para Google AI Studio, que incorpora a metodologia de `/skill:ideation-drilling`:
   - Máximo de **6 turnos** por participante (critério absoluto de parada)
   - **Cardápio de perguntas**: necessidade real, alternativa, escopo, clareza, risco, usuário
   - Uma pergunta por vez com síntese antes de cada novo turno
   - Formato de saída: bloco ````markdown` copiável com relatório completo

2. **Cada participante** abre o AI Studio, cola a instrução de sistema, e conversa com o agente

3. **Ao final**, o agente no AI Studio:
   - Agradece o participante
   - Gera bloco markdown com relatório completo (perguntas, respostas, insights)
   - Instrui: *"Copie TODO o conteúdo deste bloco e envie no grupo da equipe"*

4. **Hermes compila** os relatórios na Fase 2 (Pesquisa) como `product/research/user-interview-<nome>.md`

#### Template da instrução de sistema

O template completo está em `references/ai-studio-ideation-system-instruction.md` nesta skill.

O prompt inclui:
- Contexto do produto (brief inicial)
- Papel do agente: facilitador de ideação
- Cardápio de 6 tipos de pergunta
- Regras: uma pergunta por vez, sintetizar, apontar tensões
- Critérios de parada: absoluto (6 turnos) + skill-based (entendimento sólido)
- Formato do relatório final: bloco markdown copiável

### Passo 4: Monitorar e Coletar Resultado

Após invocar o Pi, aguarde. O Pi pode levar vários turns para completar o drilling.

**Detecção de conclusão:**
- O Pi escreverá `ideation-result.md` diretamente em `product/ideation/` no shared volume
- O arquivo conterá `<!-- PHASE_COMPLETE: ideation -->`

```bash
# Verificar se o arquivo foi criado
ls -la /opt/data/code/<projeto>/product/ideation/ideation-result.md
```

> **Nota:** Hermes não pode `mv` ou escrever no shared volume. O contexto do Pi
> instrui ele a escrever o resultado direto em `product/ideation/ideation-result.md`.
> Se por algum motivo escreveu na raiz, peça ao Pi para mover:
> ```bash
> ssh oracle-host 'pi-shell \"mv /workspace/code/PROJETO/ideation-result.md /workspace/code/PROJETO/product/ideation/\"'
> ```

### Passo 5: Relatar ao Usuário

Resuma para o usuário:
- **Veredito:** Proceed / Proceed with caveats / Rethink
- **Confiança:** High / Medium / Low
- **Principais decisões:** bullet points
- **Próximo passo:** "Avançar para Fase 2 (Pesquisa)?"

Se o veredito for "Proceed" ou "Proceed with caveats", pergunte se quer avançar.
Se "Rethink", pergunte se quer iterar na ideia ou abandonar.

## Protocolo de Drilling (para quando Hermes faz diretamente)

Se você, Hermes, estiver fazendo o drilling (não delegou ao Pi), siga este protocolo:

### Fase 0: Mapeamento de Superfície (1-3 turns)

Antes de aprofundar, mapeie o território:

- **Qual a ideia em uma frase?** Force clareza imediata.
- **Para quem é?** Perfil do usuário — contexto, dor, motivação.
- **O que gerou essa ideia?** Uma dor específica? Uma tecnologia? Um concorrente?
- **Qual a versão mais simples que poderia funcionar?** O mínimo dos mínimos.

**Meta:** Responder "Temos superfície suficiente para perfurar?" Se sim, prossiga.

### Fase 1: As Sete Dimensões de Perfuração

Escolha 4-6 dimensões que mais importam para esta ideia específica. Pule as triviais.

#### 1. NECESSIDADE — "Isso precisa existir?"
- Que problema real isso resolve? (Seja específico)
- O que acontece se isso *não* existir?
- Teste ácido: se o usuário pudesse resolver a causa raiz com um passe de mágica, esse produto ainda seria necessário?

#### 2. ALTERNATIVAS — "Por que não algo mais simples?"
- O que o usuário usa hoje? (Planilha? Papel? Outro app?)
- Qual a alternativa mais barata e mais burra possível?
- Teste ácido: qual a coisa mais simples que resolveria 80% da dor?

#### 3. ESCOPO — "O que exatamente estamos construindo?"
- Qual a menor versão *útil*?
- O que é obrigatório vs. diferencial vs. ruído?
- Mapa de três círculos: "Essencial" / "Legal ter" / "Agora não"

#### 4. CLAREZA — "O que você quer dizer com X?"
- Toda palavra vaga ("melhor", "inteligente", "automático", "simples") — crave definições precisas.
- Seja cirurgicamente irritante. Cada palavra vaga é um futuro bug.

#### 5. RISCO — "O que pode matar isso?"
- Risco técnico, adoção, plataforma, timeline, skill, mercado
- Top 3 riscos com "se isso acontecer, nós..."

#### 6. USUÁRIO — "Quem exatamente é o usuário?"
- Técnico? Leigo? Poderoso? Casual?
- Quais ferramentas eles já usam? (Seu produto compete por atenção com elas)
- Narrativa de 3-5 frases: "Conheça [Nome]. Toda manhã eles... A maior frustração é... Eles já tentaram... O que eles realmente querem é..."

#### 7. TIMING — "Por que agora?"
- Mudança tecnológica? Mercado pronto? Janela pessoal?
- O que acontece se esperar 6 meses?

### Fase 2: Síntese

Após perfurar, sintetize:

1. **Reafirme a ideia** em uma frase precisa
2. **Liste as decisões-chave** com racionais
3. **Sinalize questões em aberto**
4. **Recomende:** Proceed / Proceed with caveats / Rethink

Escreva o documento `ideation-result.md` conforme template abaixo.

## Template do Ideation Result

```markdown
# Ideation Result: [Project Name]

## One-Line Summary
> Descrição precisa em uma frase

## The Core Idea (Phase 0 Restatement)
[Parágrafo descrevendo a ideia refinada]

## Drilling Record

### 1. [Dimensão]
**Questions asked:** [O que foi perguntado]
**Answers received:** [O que foi respondido]
**Resolution:** [O que foi decidido e por quê]

### 2. [Dimensão]
...

## Key Decisions & Rationales
| Decision | Rationale | What was considered |
|----------|-----------|---------------------|
| ...      | ...       | ...                 |

## Boundary Map
### Must Have (MVP)
- Feature 1: [por quê]
- Feature 2: [por quê]

### Nice to Have
- Feature 3
- Feature 4

### Not Now
- Feature 5: [por quê]

## Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ...  | H/M/L     | H/M/L  | ...        |

## User Narrative
[Narrativa de 3-5 frases da Dimensão 6]

## Open Questions
1. ...
2. ...

## Verdict
**Confidence:** [High / Medium / Low]
**Recommendation:** [Proceed / Proceed with caveats / Rethink]
**Next step:** [O que acontece agora]

<!-- PHASE_COMPLETE: ideation -->
```

## Meta-Instruções

### Iteração, Não Interrogatório

É uma *conversa*, não uma sabatina. Uma ou duas perguntas por turno.
Se o usuário der uma resposta rica, mergulhe *naquela* dimensão — não mude aleatoriamente.

### Navegando Resistência

- "Só constrói, para de perguntar": Reconheça a urgência, explique que cada dimensão previne retrabalho. Comprometa-se.
- Respostas vagas: Reafirme como proposta específica ("Quando você diz melhor, quer dizer resposta em <200ms?")
- Usuário não sabe: Tudo bem. Anote como questão em aberto. Siga em frente.

### Critério de Saída

Você não precisa de todas as respostas. Só precisa de:
- **Sem impeditivos** — coisas que tornariam a ideia inteira estúpida
- **Clareza suficiente** para escrever algo que outra pessoa entenderia
- **Alinhamento** entre você e o usuário sobre o que "pronto" significa

Quando esses três existirem, escreva o Ideation Result com `<!-- PHASE_COMPLETE: ideation -->`.

## Integração com o Pipeline

Esta skill é a **Fase 1** do pipeline de produto. Após a conclusão:

```bash
# Verificar resultado
ls -la /opt/data/code/<projeto>/product/ideation/ideation-result.md

# Commitar via Pi (Hermes não escreve no shared volume)
ssh oracle-host 'pi-shell "cd /workspace/code/PROJETO && \
  git add product/ideation/ && \
  git commit -m \"feat: ideation result for PROJETO\" 2>/dev/null || true"'
```

**Próxima fase:** Carregar a skill de pesquisa (deep-research) ou a próxima skill do pipeline.

## Pitfalls

⚠️ **Pi pode demorar:** O drilling tem múltiplos turns de ida-e-volta dentro do Pi. O SSH pode parecer "travado" por vários minutos. Configure timeout alto (120s+).

⚠️ **Modelo superior vs custo-benefício:** O drilling precisa de modelo inteligente (raciocínio). Não economize no modelo desta fase.

⚠️ **Marcador PHASE_COMPLETE:** O Pi pode esquecer de incluir o marcador. Se o arquivo for criado mas sem o marcador, leia o conteúdo e verifique se o drilling parece completo. Confirme com o usuário se necessário.

⚠️ **Comandos longos no SSH:** O contexto passado para o Pi pode ser grande. Use variáveis de ambiente (CONTEXT) em vez de argumentos inline para evitar limite de tamanho de comando.

⚠️ **Permissão de escrita no Pi:** O Pi pode não ter permissão para escrever no shared volume se o dono não for `pi`. Verificar `chmod` se necessário.

⚠️ **Shared volume: Hermes READ-ONLY:** `/opt/data/code/` é owned por uid 1001, Hermes roda como uid diferente. Hermes **não pode criar nem escrever** arquivos/pastas no shared volume. Todo `mkdir`, `touch`, `git init`, `mv` precisa ser delegado ao Pi via `ssh oracle-host 'pi-shell "comando"'`. Ambos os agentes leem sem problema.

⚠️ **Rota SSH correta:** Não usar IP público direto (timeout). A rota correta é via Docker gateway: `ssh oracle-host "pi-agent 'pi ...'"` ou `ssh oracle-host 'pi-shell "bash cmd"'`.
