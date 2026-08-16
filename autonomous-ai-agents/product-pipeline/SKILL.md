---
name: product-pipeline
description: "Multi-agent product pipeline — idea to MVP via sprints. Hermes orchestration.

Load this skill when building a product from scratch through the full pipeline — ideation, research, design, sprints, and delivery. Covers orchestrating a multi-agent team with Hermes as coordinator, Pi Agent for execution, and Antigravity for visual design review."
category: autonomous-ai-agents
type: Orchestrator
timestamp: 2026-06-14T05:19:11Z
---

# Product Development Pipeline

> **Orquestrador:** Hermes
> **Executores:** Pi Agent (local, v0.78.1) + Antigravity (revisor visual)
> **Shared volume:** `/opt/data/code/` ↔ `/workspace/code/`

## Retomar sessão do Pi (REQUISITO do usuário)

Para continuar uma tarefa do Pi (Turno 2, correções, iterações), **sempre retomar a MESMA sessão**
com `pi --session /caminho/sessao.jsonl -p "<prompt>"` — nunca criar sessão nova. Verificar que a
retomada funcionou: o JSONL cresce por APPEND (mesmo arquivo, tamanho aumenta) e o Pi lembra do
contexto anterior (ex.: cita o próprio commit). Requisito explícito do usuário — repetido em
múltiplas sessões.

## Preferências do Usuário (ID Consultoria / Gustavo)

Este bloco codifica o estilo de trabalho das pessoas que usam este pipeline.
**Carregar sempre que a skill for ativada — antes de qualquer ação.**

> Multi-onda: `references/multi-wave-execution-pitfalls.md` (reset --hard proibido no shared volume).

### Estilo de comunicação
- **Direto e pragmático:** Usuário quer ação, não explicação. "Mande aqui", "Faça", "Cheque" são comandos, não sugestões.
- **Recap antes de executar nova run:** Quando o usuário pede uma nova rodada de correções ("Rode uma nova run"), SEMPRE recapitular o processo primeiro — listar as fases do pipeline que serão executadas (Pi → Agy → fix loop → Dogfood → Deploy → Relatório). Não é opcional — é o contrato de execução.
- **Correções são diretas:** "É para fazer o contrário", "Mova X para futuro" — aplicar a correção imediatamente em TODAS as seções afetadas, sem questionar.
- **Zero jargão corporativo:** "Prioridade máxima é funcionar para a ID" > "avaliaremos escalabilidade em V2".
- **Espera versão funcional, não especulação:** Se disser para construir algo, construir de verdade. Se não for possível, falar o obstáculo concreto.

### Estilo de entrega
- **Entregar arquivos, não descrições:** Usuário pediu um documento → salvar em disco e enviar via MEDIA. Não descrever o que faria.
- **Iteração é o padrão:** Primeira versão raramente é a final. Usuário vai pedir ajustes. Aplicar feedback SISTEMATICAMENTE em todas as seções (checklist PRD Revision Cycle).
- **Zero emojis na UI — ícones SVG do design system:** NÃO usar emojis Unicode (🚧, 📊, ⚠️, 📦) em placeholders, badges, botões ou QUALQUER elemento visual da aplicação. Esta é uma exigência explícita do usuário ("IMPORTANTE: Não deixe emojis na entrega final, use ícones bem feitos e adequados no lugar"). Usar exclusivamente ícones SVG do design system (`VERO.svgIcons.*`). Se um ícone não existir, adicioná-lo ao `svg-icons.js` antes de usar. Emojis quebram a consistência visual e passam impressão de produto amador. Após cada execução, verificar com `grep -r '&#x1F\|🚧\|📊\|⚠️\|📦' public/` — zero resultados é o esperado.
- **Múltiplos canais:** Usuário alterna entre Telegram (DM), WhatsApp (grupos), Google Workspace (Docs/Agenda). Respeitar o canal onde a mensagem chegou.
- **Google Docs para revisão colaborativa:** Quando enviar PRD para Google Docs, NUNCA sobrescrever com markdown local. O doc é a fonte da verdade colaborativa. Sync-back é Google Docs → markdown local, nunca o contrário.

### Preferências técnicas
- **Responsividade mobile é requisito, não opcional:** HTML sem responsivo testado = não entregue.
- **Pi Agent em background:** Pi com DeepSeek V4 Pro gera output silencioso por minutos. Monitorar via `ls -la` nos arquivos de saída, não via stdout.
- **Pre-flight check antes de cada fase:** Usuário não quer gastar tokens debugando permissão.

### Preferências de documento
- **Formato limpo e enxuto:** Documentos de produto (personas, PRD, etc.) DEVEM ser focados no que importa — sem poluição de fontes inline, sem metadados de pesquisa no texto. Fontes são implícitas ou registradas no histórico, não no corpo. Exemplo real: user-personas foi reduzido de 265 linhas para 106 (60% mais enxuto) a pedido do usuário.
- **Template proto-persona do Pi Agent:** Usar o formato do Pi Agent (`~/.pi/agent/skills/pm-skills/skills/proto-persona/template.md`) como referência de estrutura: Bio & Demographics → Quotes (2-3) → Pains (2-3) → What/Goals → Attitudes & Influences. Sem tabelas enormes, sem fontes a cada linha.
- **Clone digital é insumo, não verdade absoluta:** Dados de clone digital alimentam a persona, mas NÃO substituem o que o usuário confirma sobre si mesmo. Se o usuário corrigir algo do clone, a correção vence — o clone pode ter alucinado características.

---

## Arquitetura de Agentes

```
┌───────────────────────────────────────────────────┐
│                     Hermes                         │
│  Orquestrador • valida • agenda • pesquisa • integra│
│  Tools: delegate_task, web, file, terminal, pi CLI  │
└──────┬──────────────────────────────┬──────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐        ┌──────────────────┐
│    Pi Agent      │        │   Antigravity    │
│   (local CLI)    │        │   (agy 1.0.6)    │
├──────────────────┤        ├──────────────────┤
│ F1: Ideação      │        │ Revisor visual   │
│ F3: PM docs      │        │ Autoridade final │
│ F4a: UX/UI       │        │ em design        │
│ F4b: Engenharia  │        │                  │
│ F5: Sprints      │        │                  │
└──────────────────┘        └──────────────────┘

### Hierarquia de uso

```
CARO/ESCASSO     agy --- Consultor externo especialista (design, UX, estrategia)
ESCASSO          Pi best -- Eng. senior interno (DeepSeek V4 Pro via Go)
BARATO/ABUNDANTE Pi cost -- Dev junior (DeepSeek V4 Flash Free)
GRATUITO         Pi cost -- Free tier Zen
```

> **Nota (ago/2026, CFP IA):** v4 Flash supera o v4 Pro anterior — p/ CFP IA **Pi cost substitui Pi best em todas as fases**; confirmar hierarquia em projetos novos. **Code-tasks: papéis FIXOS por modelo (Pi best spec → Pi cost execução → agy revisão → Pi best max correção → Pi cost max docs) + política 🔴/🟢 + pitfalls CI/Postgres → `references/code-task-model-roles.md`.** **Refinamento Zera (14/08/2026): ciclo por papel — Pi best gera code-tasks, Pi cost executa, agy revisa, Pi best max corrige (mesma sessão), Pi cost max documenta** — ver `references/code-task-execution-workflow.md`.

Ver skill pi-agent-coordination para detalhes completos.

### Conexões

| Conexão | Como |
|---------|------|
| **Hermes ↔ Pi (one-shot)** | `pi -p "..." --provider deepseek --model deepseek-v4-flash` (local, sem SSH) |
| **Hermes ↔ Pi (persistent session)** | Primeiro: `pi --name "sessao" -p "..."`, depois: `pi -c -p "..."` |
| **Hermes ↔ Pi (sessão id)** | `pi --session /path/to/session.jsonl -p "..."` — continuar a MESMA sessão (append na mesma JSONL). Detalhes e verificação: `references/pi-session-continuation.md` |
| **Hermes ↔ agy** | `ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && /home/ubuntu/.local/bin/agy -p "..."'` |
| **Pi → agy (design feedback)** | Pi salva protótipo → Hermes chama agy → agy escreve em `feedbacks.md` |

> **Sem limite de tempo:** Toda invocacao de Pi e agy no pipeline roda **sem timeout**. Pi pode gerar output por minutos sem streamar stdout — `timeout N` mata o processo silenciosamente (exit code 0 não indica erro). agy pode levar minutos analisando código. Nunca usar `timeout` com Pi ou agy. Para Pi: usar `terminal(background=true)` ou foreground sem flag de timeout. Para agy: usar tmux interativo OU `agy -p "..." --dangerously-skip-permissions --print-timeout 15m` (sem `--dangerously-skip-permissions` o agy aborta quando stdin não é TTY — ver `references/design-review-loop.md`).
> Pi e local — nao ha SSH, nao ha timeout de conexao, nao ha quoting hell.
> Para tarefas muito longas (>5min), Pi pode stallar — usar agy ou quebrar em partes.
> Ver skill pi-agent-coordination para detalhes de fallback entre modelos.

### Modelos

#### Pi Best (planejamento, design, docs complexos)

Priorizar DeepSeek V4 Pro via Go:

| Opção | Provider | Model ID | Custo | Notas |
|-------|----------|----------|-------|-------|
| **Pi best** | `opencode-go` | `deepseek-v4-pro` | Cota semanal $30 | Preferido. Chave ativa |
| **Fallback 1 (via Go)** | `opencode-go` | `minimax-m3` | Cota semanal $30 | Mesmo provider, modelo diferente |
| **Fallback 2 (API direta)** | `deepseek` | `deepseek-v4-pro` | $0.14/M input, $0.42/M output | Último recurso |

#### Pi Cost (execução de code-tasks, fixes, docs)

| Prioridade | Provider | Model ID | Custo | Notas |
|-----------|----------|----------|-------|-------|
| 1 | `opencode` (Zen) | `opencode/deepseek-v4-flash-free` | **Gratuito** | Preferido. Chave OpenCode ativa |
| 2 | `opencode-go` (Go) | `deepseek-v4-flash` | Cota semanal $30 | Fallback se Zen rate-limited |
| 3 | `deepseek` (API direta) | `deepseek-v4-flash` | $0.14/M input | Último recurso |

> ⚠️ **DeepSeek v4 Flash tem modo reasoning que engole o budget de tokens.** Ao chamar o modelo diretamente (OpenRouter/opencode-go), com `max_tokens` baixo (ex: 256) a resposta sai **VAZIA** (`content: ""`) — todo o budget vai para `reasoning_content` antes do texto final. Uso observado: ~380 tokens de reasoning + ~130 de resposta por chamada. **Fix: `max_tokens ≥ 1024`.** Sintoma no usage: `completion_tokens_details.reasoning_tokens ≈ max_tokens` com content vazio. Isso também eleva a latência para ~12s por chamada (vs alvo 3s) — considerar streaming/cache/modelo sem reasoning para produção.

**Teste de conectividade (sempre verificar antes de invocar):**
```bash
# Pi Cost — tentar 1, 2, 3 em ordem
pi -p "echo test" --provider opencode --model opencode/deepseek-v4-flash-free
pi -p "echo test" --provider opencode-go --model deepseek-v4-flash
pi -p "echo test" --provider deepseek --model deepseek-v4-flash

# Pi Best
pi -p "echo test" --provider opencode-go --model deepseek-v4-pro
```

---

## Estrutura do Projeto

```
<projeto>/
├── product/
│   ├── ideation/
│   │   └── ideation-result.md
│   ├── research/
│   │   ├── <topico-1>.md
│   │   ├── <topico-2>.md
│   │   ├── mercado.md
│   │   └── user-interview.md
│   ├── management/
│   │   ├── PRD.md
│   │   ├── user-personas.md
│   │   ├── opportunity-solution-tree.md
│   │   ├── user-stories.md
│   │   └── product-roadmap.md
│   ├── design/
│   │   ├── wireframes.md
│   │   ├── design-system.md
│   │   ├── empathy-map.md
│   │   ├── journey-map.md
│   │   ├── prototype.html
│   │   └── feedbacks.md
│   └── engineering/
│       ├── SAD.md
│       ├── tech-specs.md
│       ├── ERD.md
│       ├── api-contracts.yaml
│       ├── test-plan.md
│       ├── release-notes.md
│       ├── code-tasks.md
│       └── feedbacks.md
├── src/
├── tests/
├── .gitignore
└── README.md
```

---

## Fases do Pipeline

```
[Ideia] → F1: Ideação → F2: Pesquisa → F3: Conceito → F4: MVP → F5: Iteração
             ↑              ↑              ↑              ↑              ↑
           Hermes→Pi    Hermes+DR     Pi best PM      Pi+agy→Docker   Hermes sprints
                                                        ↓
                                                  4e: Agy valida
                                                   app rodando
```

---

## Pre-flight Check (Obrigatorio antes de CADA fase)

O usuario **explicitamente pediu** para nao gastar tokens debugando permissao. Executar antes de invocar qualquer agente:

```bash
# 1. Pi acessivel? (PATH pode não incluir /opt/data/pi-global/bin)
export PATH="/opt/data/pi-global/bin:$PATH"
pi --version

# 2. Skills do Pi carregadas?
pi -p "list your skills" --provider deepseek --model deepseek-v4-flash

# 3. Shared volume funcional?
ls /opt/data/code/workstation/PROJETO/product/ 2>/dev/null
touch /opt/data/code/workstation/PROJETO/.perm-check 2>/dev/null && rm $_ && echo "Hermes rw: OK" || echo "Hermes rw: BLOQUEADO"

# 4. Docs da fase anterior legiveis?
ls -la /opt/data/code/workstation/PROJETO/product/FASE_ANTERIOR/*.md 2>/dev/null | head -3

# 5. Agy funcional?
ssh oracle-host 'echo "n" | timeout 5 /home/ubuntu/.local/bin/agy 2>&1 | head -3'
```

Se qualquer check falhar, **corrigir antes de prosseguir** — não invocar Pi até estar verde.

---

## ⛔ REGRA DE OURO: Hermes NUNCA escreve código

**Hermes orquestra. Pi gera. agy revisa.** Esta é a única arquitetura válida.

- ❌ NUNCA use write_file/patch/terminal para criar ou editar HTML, CSS, JS, ou qualquer código-fonte
- ❌ NUNCA pule etapas da pipeline para "agilizar" — o usuário explicitamente rejeitou atalhos
- ❌ NUNCA avance para a próxima fase sem a atual estar 100% concluída e verificada
- ✅ Todo código é gerado por Pi Agent (best para design/docs, cost para execução)
- ✅ Toda revisão de design/código é feita por agy via SSH no Oracle host
- ✅ Espere CADA etapa terminar (process wait/poll) antes de iniciar a próxima

> **Se o usuário disser "rápido", "direto ao deploy", "pular etapas":** IGNORE. Siga a pipeline completa. O usuário já corrigiu este comportamento 2x. A pipeline é o contrato.

---

**Agente:** Hermes → Pi (modelo best)

### Fluxo (padrão: Pi Agent síncrono)

1. Hermes cria a estrutura inicial. **Pi e Hermes compartilham o mesmo filesystem** — nao ha mais UID mismatch:

   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/ideation /opt/data/code/workstation/PROJETO/prompts
   cd /opt/data/code/workstation/PROJETO && git init -b main 2>/dev/null
   git add -A 2>/dev/null; git commit -m "chore: init" 2>/dev/null || true
   ```

2. Hermes cria **sessão Pi persistente com nome** e envia a ideia inicial:

   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/prompts
   cat > /opt/data/code/workstation/PROJETO/prompts/pi-ideation.md << 'PROMPT'
   IDEIA: [brief completa do usuário]
   Projeto: <projeto>
   Diretório: /workspace/code/<projeto>
   Sua missão: carregar /skill:ideation-drilling e conduzir a ideação.
   Quando terminar, escreva ideation-result.md em product/ideation/.
   Inclua <!-- PHASE_COMPLETE: ideation --> ao final.
   PROMPT

   pi --name "PROJETO-ideation" -p "$(cat prompts/pi-ideation.md)" --provider opencode-go --model deepseek-v4-pro
   ```

3. **Pi carrega `ideation-drilling`** e faz sequência longa de perguntas:
   - "Esse produto é realmente necessário?"
   - "Não há alternativa mais simples e barata?"
   - "Essa feature é essencial?"
   - "Se faltar X, o projeto ainda atinge o objetivo?"
   - "O que exatamente você quer dizer por Y?"
   - "Seria mais ou menos isso e isso?"

4. Quando agente e humano se dão por **plenamente satisfeitos**, Pi escreve **`product/ideation/ideation-result.md`** com:
   - Detalhamento completo da ideia final
   - Lista de racionais para cada decisão

> **Relay pattern:** Pi não usa `clarify`. Se fizer perguntas, Hermes relay: mostra pro usuário, coleta resposta, reenvia ao Pi com `pi -c`.

### Variante: Ideação Distribuída (AI Studio, múltiplos stakeholders)

> **Referência completa:** `skill_view(name='product-pipeline', file_path='references/distributed-ideation-ai-studio.md')`

Quando a ideação envolve **2+ pessoas** que não podem participar da mesma sessão síncrona (stakeholders em horários diferentes, equipe remota, sócios com agendas conflitantes), substitua o Pi Agent por:

1. **Hermes cria uma Instrução de Sistema auto-contida** para o Google AI Studio, que transforma o modelo num facilitador de ideação com:
   - Máx 6 turnos por participante (absoluto)
   - Uma pergunta por vez, com síntese antes de cada turno
   - Cardápio de perguntas: necessidade real, prioridade, definição, trade-off, diferenciação, público
   - Formato de saída: bloco markdown copiável

2. **Cada stakeholder roda no próprio AI Studio**, no seu ritmo. O agente faz perguntas, o stakeholder responde.

3. **Ao final**, o agente gera um relatório em bloco ````markdown` e instrui: *"Copie TODO o conteúdo e envie no grupo."*

4. **Hermes consolida** os relatórios em `product/ideation/ideation-result.md`:
   - Mapeia consensos entre participantes
   - Identifica divergências e tensões
   - Extrai o escopo do MVP validado
   - Preserva citações literais
   - Inclui seção "Tensões não resolvidas"

5. O documento consolidado segue para aprovação do usuário (mesmo fluxo abaixo).

> **Dica:** Incluir no prompt de sistema que o nome do projeto deve carregar o conceito (ex: Delfos = "lugar do oráculo"). Registrar o significado no relatório final.

### Saída

```
product/ideation/ideation-result.md
```

Com marcador `<!-- PHASE_COMPLETE: ideation -->`

> **Arquivos .MD entregues via MEDIA, nunca como texto inline.** Quando o usuário pede um arquivo .md, salvar em disco e entregar via `MEDIA:/path/to/file` no Telegram.

### Detecção de conclusão

```bash
grep "PHASE_COMPLETE" /opt/data/code/<projeto>/product/ideation/ideation-result.md
```

### Revisão pelo usuário

Após o Pi escrever `ideation-result.md`, Hermes:
1. Verifica se o arquivo existe e contém o marcador `PHASE_COMPLETE`
2. Envia o `.md` ao usuário **como arquivo anexado (MEDIA)** no Telegram
3. **Aguarda a aprovação explícita do usuário** antes de seguir para F2

> **Essa pausa é obrigatória.** O usuário precisa validar o entendimento mútuo antes de prosseguir.

### Git commit

```bash
cd /opt/data/code/workstation/PROJETO
git add product/ideation/ && git commit -m "feat: F1 ideation complete"
```

---

## Fase 2: Pesquisa

**Agente:** Hermes

### ⏱️ Tempo de pesquisa — AUMENTAR TIMEOUT, não aceitar timeout

O usuário quer que subagentes **sempre tenham tempo suficiente** para completar. O timeout
padrão de 600s do `delegate_task` frequentemente não basta para pesquisas com 15-25 chamadas
de API (cada web_search/web_extract/browser leva ~20-40s com modelos lentos).

**Regra:** Sempre que possível, configure o timeout máximo disponível. Se o `delegate_task`
não aceitar timeout por parâmetro, assegure que:
1. O contexto do subagente seja focado e auto-contido (menos chamadas = mais rápido)
2. Se houver risco de timeout (>8 tópicos), quebre em 2 rodadas de delegate_task
3. Em último caso, faça a pesquisa diretamente (fallback comprovado)

**Fluxo recomendado:**
1. Disparar 2-3 subagentes paralelos com contextos detalhados e auto-contidos
2. Instruir subagentes a **não insistir em fontes bloqueadas** — se Google/Reddit/bloqueio, trocar imediatamente por DuckDuckGo, Bing, ou URLs diretas
3. Se precisar de conteúdo do Reddit, carregar a skill `read-reddit` (RSS feeds, não bloq.)
4. Se timeoutarem, **não retentar subagentes** — ir para pesquisa direta com `web_search` + `web_extract`
5. A pesquisa direta é mais rápida porque pula overhead de contexto do subagente
6. Sintetizar findings em relatórios `.md` em `product/research/`

> 💡 **Nota técnica:** Os subagentes deixam sessões no state.db mesmo quando timeoutam.
> É possível extrair tool_results do banco via SQLite para recuperar dados parciais
> (ver `skill_view(name='product-pipeline', file_path='references/subagent-session-recovery.md')`),
> mas o conteúdo mais valioso está nos relatórios produzidos pela pesquisa direta.

> 📊 **Pesquisa de mercado / GTM:** Para pesquisas de go-to-market, cursos online, edtech ou 
> benchmarks de conversão, ver `skill_view(name='product-pipeline', file_path='references/market-gtm-research-sources.md')` 
> — contém recomendações de fontes, padrão de rate-limit do web_search, e lista de URLs verificadas 
> com dados persistentes (Jul 2026).

### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/research
   ```

2. **Planejar pesquisa** — definir tópicos com base no ideation-result.md:
   - Referências explícitas (softwares mencionados, conceitos-chave)
   - Referências implícitas (domínios relacionados)
   - Mercado, concorrência, perfil de usuário

3. Disparar sub-agentes `deep-research` para cada tópico (conceder tempo máximo disponível):
   ```python
   delegate_task(
       goal="Pesquisar profundamente sobre [tópico]",
       context="Contexto do projeto + perguntas específicas",
       toolsets=["web", "browser"]
   )
   ```

4. **Fallback:** Se subagentes timeoutarem, pesquisar diretamente:
   ```python
   web_search(query="...", limit=10)
   web_extract(urls=["...", "..."])
   ```

5. **Entrevista de usuário:**
   - Carregar skill `user-interview`
   - **Produto pessoal:** Hermes entrevista o usuário diretamente
   - **Produto com outros perfis:** simular entrevista para cada perfil de usuário

   **Simulação paralela (recomendada p/ 3+ perfis):** Disparar subagentes via `delegate_task` em paralelo, cada um simulando um perfil diferente com persona detalhada (idade, renda, situação financeira, citação típica). Cada subagente produz um `.md` individual com transcrição completa + análise (pain points, desired outcomes, emotional arc, concept test reaction).

   **Cross-interview synthesis:** Consolidar os relatórios individuais em `user-interview.md` com:
   - Tabela comparativa dos perfis (renda, dores, gatilhos, preço aceitável)
   - Temas recorrentes (mencionados por 2+ perfis) — estes viram recomendações P0
   - Non-obvious insights (padrões que contrariam suposições iniciais)
   - Recomendações de produto priorizadas (P0/P1/P2) baseadas na frequência entre perfis
   - Seção de cada perfil com resumo + emotional arc + key quotes

6. Cada resultado de pesquisa armazenado como `.md` em `product/research/`.

   ```bash
   git add -A && git commit -m "feat: F2 research complete"
   ```

### Research Suite Output: Raw + Premium + Synthesis

When F2 research needs both source documents (.md) and polished deliverables (.html):

```
                    ┌─────────────────────────────┐
                    │  Decompose research into    │
                    │  N topics (explicitas,       │
                    │  implicitas, mercado, reg.)   │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  Dispatch N subagents in     │
                    │  parallel (delegate_task     │
                    │  batch), each writes 1 .md   │
                    │  report to product/research/ │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │  Run "direto" research items │
                    │  yourself (web_search +       │
                    │  web_extract), write .md      │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │  Create a design system     │
                    │  HTML (single-file, tokens)  │
                    │  — shared visual foundation  │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │  Convert each .md → .html   │
                    │  premium (via agy SSH):      │
                    │  SSH host, agy --print       │
                    │  --dangerously-skip-perms    │
                    │  Each HTML embeds design     │
                    │  system CSS (single-file)    │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │  Generate 1 synthesis .html │
                    │  (executive summary +       │
                    │  key findings from all)     │
                    └─────────────────────────────┘
```

**When to use:** User asks for "research folder / base de referências" and expects both raw markdown and polished deliverables + executive summary.

**Key details:**
- **Markdown reports (.md):** Written by subagents, each focused on ONE angle. Saved under `product/research/`.
- **Design system HTML:** Created once, shared visual foundation. CSS custom properties for colors, typography, spacing. Dark mode support. Inspired by Notion/Stripe/Linear minimal aesthetic. Saved as `product/research/design_system_minimal_neutral.html`.
- **Premium HTML versions:** One per report. Embed the design system CSS directly (single-file, no external deps). Add navbar, sections with alternating backgrounds, pure-CSS charts (progress bars, quadrant matrices, bar charts), dark mode toggle, scroll animations, IntersectionObserver sidebar highlighting.

**Report formatting rules (user preference, apply to ALL reports):**
- Labels "nível", "status", "projeto" ou "data" NÃO devem aparecer em lugar algum
- Sempre adicionar seção "Sobre este Relatório" no início: o que é, como foi feito, o que pretende informar
- Máxima consistência visual entre relatórios — mesmo design system (:root CSS tokens idênticos), mesma navbar glass, mesma estrutura de seções
- Tabelas SEMPRE usando `.table-wrap > table` padrão — nunca grid customizado com CSS

**Synthesis report (executive summary):**
- **Abordagem MBB (McKinsey/BCG/Bain):** Capa branca limpa, minimalista, sem gradientes decorativos, glassmorphism ou floreios visuais. NADA de decorativo que não sirva à informação.
- **Framework SCR:** Organizar a capa em Situação → Complicação → Resolução. A Resolução ocupa 60-70% do espaço. Cada claim em negrito com dados de suporte.
- **Métricas visuais:** Números em destaque com mini barras de progresso ou badges. Grid limpo, hierarquia tipográfica.
- **Conteúdo manda:** "Silent read test" — a página deve ser compreendida sem apresentador. Zero jargão de consultoria. Claims completos com evidências. page-break-after para PDF.
- **Sem metadados irrelevantes:** Não incluir nomes de consultoria, fases, confidencialidade ou datas na capa a menos que o usuário peça.

**PDF generation (post-HTML, opcional):**
- Usar Chromium headless: `LD_LIBRARY_PATH=.../chromium .../chromium --headless --no-sandbox --disable-gpu --print-to-pdf-no-header --print-to-pdf="output.pdf" "file://input.html"`
- Adicionar `@page { margin: 0; }` no CSS para remover margens padrão de impressão
- Google Drive upload opcional: `$GAPI drive upload file.pdf --name "file.pdf" --parent FOLDER_ID`

**agy integration:** Copy design system + reports to host, SSH in, run `agy --dangerously-skip-permissions --print "$(cat prompt.md)"`. Each call generates one single-file HTML. Copy back with `scp`.
- **Pitfall: filename collisions.** Assign distinct filenames in each subagent's context. Use `mkdir -p product/research/` before dispatching.
- **Pitfall: agy headless needs --dangerously-skip-permissions.** Without it, `write_file` is denied.
- **Pitfall: executive summary florals.** User explicitly rejected decorative-only heroes. If the hero doesn't communicate real SCR-structured information with data, it will be rejected. Content-first, data-driven, clean hierarchy.
> **Referência completa:** `skill_view(name='product-pipeline', file_path='references/mbb-executive-summary-standards.md')` — pesquisa completa sobre padrões McKinsey/BCG/Bain.

### Saída

```
product/research/
├── index.html                (opcional — página consolidada com visual Agy)
├── design_system_minimal_neutral.html  (design system compartilhado)
├── <topico-1>.md
├── <topico-2>.html            (versão premium, opcional)
├── mercado.md
├── mercado.html               (versão premium, opcional)
├── user-interview.md
├── sintese-executiva.html     (relatório-síntese final)
└── <outros>.md
```

> **HTML responsivo (⚠️ comum quebrar no mobile):** Se o usuário pedir deploy de
> página HTML consolidando as pesquisas, garantir mobile responsiveness antes de
> publicar. Ver `skill_view(name='product-pipeline', file_path='references/mobile-responsive-html-deliverables.md')`
> para checklist e diagnóstico de overflow horizontal.

---

## Fase 3: Desenvolvimento de Conceito

**Agente:** Pi (modelo best)

### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/management
   ```

2. Hermes invoca **Pi com modelo best** em sessão persistente (background), carregando skills de PM:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/prompts
   cat > /opt/data/code/workstation/PROJETO/prompts/pi-pm-docs.md << 'PROMPT'
   [contexto completo com path dos arquivos, skills a carregar, docs a produzir]
   PROMPT

   pi --name "PROJETO-pm" -p "$(cat prompts/pi-pm-docs.md)" --provider opencode-go --model deepseek-v4-pro
   ```

3. **Monitorar progresso — verificar arquivos de saída, NÃO o stdout do processo:**
   ```bash
   # Pi gera output silencioso (sem stdout até o final). Monitorar assim:
   ls -la /opt/data/code/workstation/PROJETO/product/management/*.md
   # Ou polling periódico com process(action='poll')
   ```
   Pi com DeepSeek V4 Pro leva ~4-5 min por documento e não streama stdout intermediário.
   Não matar o processo achando que travou — verificar os arquivos primeiro.

4. Pi carrega skills instaladas e elabora:
   - **PRD** — `/skill:prd-development`
   - **User Personas** — (ver seção abaixo sobre estratégia de pesquisa)
   - **Opportunity Solution Tree** — `/skill:opportunity-solution-tree`
   - **User Stories** — `/skill:user-story`
   - **Product Roadmap** — `/skill:roadmap-planning`
     - Se existir uma planilha/roadmap anterior no Google Drive, lê-la primeiro e fazer o novo roadmap ser um SUPERSET (preservar quinzenas existentes, expandir com mais granularidade e horizontes futuros)
   - (e outros que julgar necessários)

#### Persona Research Strategy: Proto vs. Pessoas Reais

O pipeline precisa decidir qual abordagem de persona usar com base no que se sabe sobre a equipe/usuários:

| Situação | Abordagem | Quem executa |
|----------|-----------|--------------|
| **Personas fictícias** — perfil genérico de usuário, sem nome/pessoa real conhecida | Pi gera proto-personas via `/skill:proto-persona` com base no PRD e entrevistas | Pi Agent (best) |
| **Pessoas reais da equipe** — membros conhecidos do time (sócios, colaboradores) | Pesquisa web profunda → clone digital → persona documentada. Seguir o protocolo em `skill_view(name='product-pipeline', file_path='references/persona-research-deep-dive.md')#7-montagem-do-clone-digital` | Hermes (pesquisa + montagem) |
| **Público externo** — usuários-alvo que não são da equipe | Entrevista simulada via `user-interview` + proto-personas | Hermes + Pi Agent |

**Fluxo para pessoas reais:**

1. **Antes** de invocar o Pi, Hermes pesquisa cada indivíduo real na web:
   - **Plataformas prioritárias:** LinkedIn, Instagram, Behance/Dribbble, Medium, GitHub, Escavador, site pessoal/empresa
   - **Técnica primária:** navegar diretamente via browser para plataformas específicas (não confiar só em web_search — buscadores podem retornar 0 resultados mesmo quando a pessoa tem presença digital rica)
   - **Se web_search retornar VAZIO (não timeout):** Tentar browser direto nas plataformas antes de reportar "não encontrado". O buscador pode estar bloqueado por CAPTCHA/rate-limit enquanto o browser funciona com navegação direta.
   - Se a busca no buscador retornar **zero resultados**, tentar navegação direta por URL (`linkedin.com/in/<username>`, `instagram.com/<user>`, `behance.net/<user>`)
   - Se ainda assim não achar, **pedir ao usuário um link direto** — não persistir tentando

2. **Técnicas avançadas após encontrar um perfil:**

   Uma vez que uma plataforma é encontrada (ex: GitHub), extrair dados complementares:

   a) **Análise de commits (GitHub API via terminal):**
      ```bash
      curl -sL "https://api.github.com/repos/<user>/<repo>/commits" | python3 -c "import json,sys; [print(c['sha'][:7],'|',c['commit']['message'].split(chr(10))[0]) for c in json.load(sys.stdin)]"
      ```
      Commits revelam vocabulário de trabalho ("cinematic composition", "premium gold gradients"), estilo, stack, autor (pode ser empresa, não username), e tipo de contribuição.

   b) **Análise de CSS em produção (se houver Vercel/Netlify deploy):**
      ```bash
      curl -sL "https://<projeto>.vercel.app/assets/<hash>.css" | head -200
      ```
      Extrair paleta de cores, tipografia, glassmorphism, animações — o sistema de design real da pessoa.

   c) **GitHub API para metadados do perfil:**
      ```bash
      curl -sL "https://api.github.com/users/<username>"
      ```
      Data de criação, número de repositórios, followers, bio (mesmo vazia), company (mesmo null — dados nulos são informativos).

   d) **Browser vision para páginas com antibot/accessibility tree truncada:**
      Quando Bing, Behance ou outras plataformas carregam visualmente mas o DOM snapshot vem truncado (Cloudflare, JS-rendered), usar `browser_vision(annotate=True)` para ler o conteúdo visual e identificar elementos clicáveis.

3. Seguir o protocolo completo em skill_view(name='product-pipeline', file_path='references/persona-research-deep-dive.md')
   (multi-plataforma recon → extrair → estruturar → consolidar clone digital)

4. A persona resultante (clone digital) alimenta o Pi para que os documentos (PRD, user stories, roadmap) reflitam **pessoas reais**, não arquétipos genéricos

5. **Referência viva:** A persona de cada membro real deve ser salva como `/opt/data/<nome>-digital-clone.md` para reúso em futuros projetos. O caminho pode ser consultado em memória ou passado ao Pi como contexto.

#### Formato de saída: user-personas.md

O documento final de personas DEVE seguir o formato proto-persona do Pi Agent, NÃO o formato verboso com fontes inline. Ver `references/persona-output-format.md` para template completo e regras.

```markdown
### Nome Real — "Persona Name"

> *Quote principal*

### Bio & Demographics
- Idade, localização, formação, cargo, empresas, perfil online
- Stack técnica / especialidades
- Perfil neurodivergente (se aplicável): 1 linha

### Quotes
- *"[Frase real 1]"*
- *"[Frase real 2]"*

### Pains
- **Dor nomeada:** Descrição em 1-2 linhas

### What is This Person Trying to Accomplish?
- 2-3 bullets concisos

### Goals
- **Alpha/X.X:** Meta específica para cada fase

### Attitudes & Influences
- Autoridade de decisão, influenciadores, crenças
```

**Regras:**
- **Sem fontes inline.** Nada de `[FONTE: pesquisa web]` no corpo. Fontes vão no histórico.
- **Sem tabela resumo gigante.** Máximo 8 itens no mapa de cobertura.
- **Sem linhas desnecessárias.** Cada seção tem 2-4 bullets, não 10.
- **Idades corretas.** Verificar com o usuário se houver dúvida.
- **Clone digital é rascunho.** O que o usuário confirmar é o documento final.

> **Prova do conceito:** Na prática, o Tácio Brito (sócio designer da ID) tem presença em GitHub (nosterviz), LinkedIn, Instagram e um Vercel deploy com CSS completo que revela seu sistema de design pessoal. O buscador padrão retornou 0 resultados — navegação direta + análise de commits/CSS foi essencial.

#### ⚠️ Pitfall Crítico — Clone Digital ≠ Pessoa Real

O clone digital é uma **hipótese**, não um retrato fiel. O LLM pode inferir características, crenças ou filosofias que a pessoa real não endossa. **Sempre**:

1. Separar o que é **dado verificável** (idade, formação, premiações, links, commit messages) do que é **inferência do LLM** (filosofia pessoal, crenças, citações inventadas)
2. Apresentar a persona ao usuário para validação explícita
3. Aplicar correções do usuário como verdade definitiva — NUNCA defender o que o clone disse contra o que o usuário afirma
4. Se o usuário disser "isso não é algo que Tácio se importa" sobre um traço do clone, remover imediatamente de TODAS as seções

**Exemplo real:** O clone digital do Tácio atribuiu a ele a crença "o método é a jaula" (schema fixo). O usuário corrigiu: "Isso não é algo que Tácio se importa não. Foi só algo que o clone digital dele disse." — a correção foi aplicada em 5 pontos do documento e o traço completamente removido.

> **Regra de ouro:** Clone digital gera hipóteses. Usuário confirma ou descarta. A correção do usuário é o documento final — o clone digital é só rascunho.

> ⚠️ **Não delegar a pesquisa de pessoas reais ao Pi Agent.** Hermes faz a pesquisa web diretamente. Pi gera o documento de persona estruturado a partir dos achados da pesquisa. (Pi não tem ferramentas de navegação web — pedir para ele pesquisar é ineficaz.)

5. **Hermes revisa o PRD antes de apresentar ao usuário** — análise de gaps práticos:

   > **PRD Review Checklist** — verificar antes de enviar para aprovação:
   >
   > - [ ] **Timeline / visualização no tempo**: Sistemas de gestão de projetos precisam de alguma forma de ver prazos e etapas no tempo. Se o PRD não menciona timeline, Gantt ou calendário, questionar se deve ir pro MVP.
   > - [ ] **Categorização de projetos**: Projetos internos vs. clientes é uma necessidade operacional básica em consultorias. Se o schema não prevê `type` ou `category`, adicionar.
   > - [ ] **O schema resolve o problema real?** Verificar se as entidades (Task, Project, etc.) cobrem o vocabulário do dia-a-dia da equipe, não só conceitos abstratos.
   > - [ ] **Consistência interna**: Resumo executivo, features MVP e critérios de aceite usam a mesma contagem de views? Números batem? Features mencionadas no resumo aparecem na tabela de escopo?
   > - [ ] **Nomes e versão**: Header do documento reflete versão atual com data. Histórico de atualizações presente.
   >
   > Se o PRD falhar em qualquer item acima, corrigir antes de enviar ao usuário.

> **PRD Revision Cycle (pós-primeira entrega):** Quando o usuário pedir ajustes no PRD,
> aplicar as mudanças SISTEMATICAMENTE em todas as seções impactadas — não apenas na tabela
> de features. O checklist abaixo garante consistência:
>
> - [ ] **Resumo Executivo** — reflete o novo conjunto de features? Números de views batem?
> - [ ] **Features MVP (5.1)** — features adicionadas/removidas na tabela?
> - [ ] **Fora do MVP (5.2)** — item movido para V2/futuro adicionado aqui?
> - [ ] **Critérios de aceite (5.3)** — novos critérios para as novas features?
> - [ ] **Features pós-MVP (6)** — V2/V3 movido, removido ou renumerado?
> - [ ] **Riscos (8)** — menções à contagem de views, features, escopo?
> - [ ] **Anexo — Decisões** — novas decisões adicionadas? Status de decisões antigas mudou?
> - [ ] **Cabeçalho** — versão bumpada (v1.0 → v1.1 → v1.2)?
> - [ ] **Histórico de atualizações** — entrada da revisão adicionada?
> - [ ] **Consistência numérica** — "4 views" vs "5 views" em TODO o documento?
>
> Esse padrão evita o erro comum de alterar só a tabela de features e deixar o resumo
> executivo, riscos e anexos inconsistentes.

> **PRD Sync-Back (Google Docs → Local):** Quando o PRD é compartilhado no Google Docs
> e a equipe faz edições diretamente lá, o fluxo reverso de sincronização exige atenção:
>
> 1. **Extrair texto do Google Doc** via Docs API (docs.documents.get → body.content →
>    paragraph.elements.textRun)
> 2. **Identificar mudanças significativas** comparando com o markdown local: seções
>    novas, renomeações, decisões registradas
> 3. **Aplicar no markdown local** preservando formatação (tabelas, negrito, listas)
> 4. **NÃO sobrescrever o Google Doc** — a equipe pode estar usando o doc como fonte
>    da verdade. Só atualizar se o usuário pedir explicitamente.
> 5. **Registrar no histórico** com autor "Equipe ID (edição no Google Docs)"
>
> Ver `skill_view(name='product-pipeline', file_path='references/google-docs-prd-delivery.md')`
> para detalhes completos do fluxo reverso, código Python e padrões comuns de edição.

#### Entrega do PRD

O usuário pode solicitar o PRD em diferentes formatos:

| Formato | Como entregar |
|---------|---------------|
| **Markdown (.md)** | Salvar em `product/management/PRD.md` e enviar via `MEDIA:/path` no Telegram |
| **Google Docs** | Ver `skill_view(name='product-pipeline', file_path='references/google-docs-prd-delivery.md')` |

Para Google Docs, o fluxo inclui verificação de token OAuth, re-autenticação PKCE (se necessário),
criação do doc, e compartilhamento com permissão "qualquer pessoa com o link pode comentar".

> ⚠️ **Regra crítica — direção do sync:** Uma vez que o Google Doc é compartilhado com a equipe
> para revisão, o doc passa a ser a **fonte da verdade colaborativa**. NUNCA sobrescrever o Google Doc
> com markdown local a menos que o usuário peça explicitamente. A direção correta é:
> **Google Docs (equipe) → markdown local (Hermes)**. Inserir markdown puro no doc destrói
> o trabalho de formatação da equipe — se o conteúdo já está no doc, leia de lá e atualize o
> markdown local, nunca o contrário.

### Saída

```
product/management/
├── PRD.md
├── user-personas.md
├── opportunity-solution-tree.md
├── user-stories.md
└── product-roadmap.md
```

---

## Fase 4: MVP

### 4a. Design (Pi modelo best + Antigravity + Stitch MCP)

> **Design System HTML é obrigatório desde o início.** Pi sempre produz `design-system.html` (todos os componentes renderizados visualmente) junto com os documentos de design. agy revisa em loop de 2+ iterações. O padrão: **Pi cria → agy revisa → Pi corrige → agy confirma**. Cada iteração registrada em `feedbacks.md` com `## Iteração N — Agente`. O loop termina com `## ACORDO: DESIGN SYSTEM FINALIZADO`.
>
> **Stitch MCP (último passo):** Google Stitch MCP é usado APÓS o design system estar aprovado, para gerar screens de UI finais a partir dos componentes já definidos. Stitch extrai DNA visual e acelera a prototipagem das telas finais. Ver `skill_view(name='product-pipeline', file_path='references/google-stitch-mcp.md')` para setup, tools disponíveis e fluxos de uso.

#### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/design
   ```

2. **Pi carrega skills de UX/UI design** (modelo best) e produz:
   - Wireframes (`/skill:ux-wireframing`)
   - Design System (`/skill:ux-design-system`)
   - Mapa de Empatia (`/skill:ux-empathy-map`)
   - Mapa de Jornada do Usuário (`/skill:ux-journey-map`)
   - User Flows (`/skill:ux-user-flow`)

3. **Pi implementa `design-system.html`** — HTML/CSS completo com todos os componentes do design system renderizados visualmente, usando dados mockados. Deve incluir paleta de cores, tipografia, botões, cards, formulários, navegação, modais, e grid system. Quebrar em lotes se necessário (v4-flash: ~2 docs/sessão, v4-pro: ~3 docs/sessão).

4. **Verificação de saída do Pi — NÃO confiar só no monitoramento de sessão:**
   ```bash
   # CERTO: verificar arquivos de output
   ls -la /opt/data/code/workstation/PROJETO/product/design/wireframes.md
   grep "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/design/wireframes.md
   ```
   Pi pode parecer travado mas já ter completado todo o output. Sempre verificar os arquivos no shared volume antes de matar ou reiniciar.

5. **Loop de revisão Antigravity (MANDATÓRIO — mín. 2 iterações):**

   O loop NÃO é opcional. Pi NUNCA acerta tudo na primeira tentativa. Formato:

   ```
   ITERAÇÃO 1:  Pi cria → agy revisa → feedbacks.md  (sempre tem issues)
   ITERAÇÃO 2:  Pi corrige → agy re-revisa → feedbacks.md atualizado
   ITERAÇÃO N:  ...repetir até agy escrever ACORDO no feedbacks.md
   ```

   **Condição de parada:** agy escreve `## ACORDO: DESIGN SYSTEM FINALIZADO` no `feedbacks.md`. Igual para F4b: `## ACORDO: ENGENHARIA FINALIZADA`. Sem ACORDO, não avance para a próxima fase.

   **Comando por iteração:**
   ```bash
   # Iteração 1: revisão inicial
   ssh oracle-host '/home/ubuntu/.local/bin/agy --print "$(cat /tmp/prompt.md)" --dangerously-skip-permissions'

   # Iteração 2: re-revisão pós-fix do Pi
   ssh oracle-host '/home/ubuntu/.local/bin/agy --print "$(cat /tmp/prompt-confirm.md)" --dangerously-skip-permissions'
   ```

   - Cada iteração registrada em `feedbacks.md` com `## Iteração N — Antigravity`
   - **Agy executa do HOST, não do container**
   - Mesmo fluxo se aplica à F4b (engenharia): agy → Pi → agy até `ACORDO: ENGENHARIA FINALIZADA`

6. **Stitch MCP — geração de telas finais (último passo):**
   Com o design system aprovado, usar Stitch MCP para gerar cada tela.

   **Pré-requisitos:**
   - Stitch MCP configurado como HTTP direto no `/opt/data/config.yaml` (NÃO no `.hermes/config.yaml`)
   - Design system verificado e atualizado ANTES de gerar — conferir: `colorMode` (DARK/LIGHT), fontes, cores primárias
   - `/reload-mcp` feito para ativar as tools

   **Workflow:**
   a) **Verificar design system existente** no projeto Stitch via `list_design_systems`
   b) **Atualizar/criar** design system com tokens corretos antes de gerar screens
      - Atenção: `UpdateDesignSystem` não aceita todas as fontes (BRICOLAGE_GROTESQUE falha, usar SPACE_GROTESK)
      - `CreateDesignSystem` aceita mais fontes mas pode dropá-las silenciosamente
   c) **Gerar mobile primeiro** (`deviceType=MOBILE`), depois desktop (`deviceType=DESKTOP`)
      - Usar `generate_screen_from_text` com prompts detalhados (mencionar tokens exatos: hex colors, font names, radius)
      - Incluir sempre `designSystem: assets/<id>` para consistência visual
   d) **Baixar screenshots** full-res: URL + `=s0` → salvar em `/opt/data/delfos-screens/`
   e) **Enviar via MEDIA** para o usuário
   f) **Gerar protótipo HTML** via agy após Stitch screens aprovadas:
      ```bash
      ssh oracle-host "cat prompt.txt | /home/ubuntu/.local/bin/agy --print --model gemini-3.1-pro --print-timeout 5m"
      ```
   g) Iterar com `edit_screens` + `generate_variants` se necessário
   - Stitch é o passo final da F4a — só depois que agy aprovou o design system

### Saída

```
product/design/
├── wireframes.md
├── design-system.md
├── design-system.html    (obrigatório — componentes renderizados)
├── empathy-map.md
├── journey-map.md
├── feedbacks.md
└── stitch-screens/       (telas geradas pelo Stitch MCP, última etapa)
```

---

### 4b. Engineering (Pi modelo best + cost + Antigravity)

> Na prática, `delegate_task` timeoutou ao orquestrar Pi via SSH de dentro de um subagente. Executar Pi diretamente do Hermes pai. v4-flash é suficiente para documentação técnica; v4-pro reservado para decisões arquiteturais complexas.

#### Fluxo

1. Criar subpasta:
   ```bash
   mkdir -p /opt/data/code/workstation/PROJETO/product/engineering
   ```

2. **Pi carrega skills de engenharia** (modelo best) e produz:
   - SAD, TechSpecs, ERD, API contracts, Test Plan, Release Notes

3. Pi gera lista de tarefas em **`product/engineering/code-tasks.md`**

4. **Execução — Hermes instancia Pi (modelo cost) em LOTES por layer:**
   - Agrupa tasks relacionadas em um único prompt
   - Invoca Pi UMA vez com todas as tasks do lote
   - Pi escreve todos os arquivos do lote
   - Hermes verifica e commita
   - Avança para o próximo layer (continua mesma sessão Pi com `-c`)

> ⚠️ **CRÍTICO — Frontend layers DEVEM ler design HTMLs como contexto visual:**
> Quando o lote incluir frontend (Layer 3-4), o prompt do Pi **DEVE instruí-lo a ler**
> os arquivos de design diretamente do disco antes de escrever código — não basta
> copiar tokens hex no prompt. Incluir no prompt do Pi:
> ```
> Before writing any frontend code, read these files for visual context:
> - `cat product/design/design-system.html` — design system renderizado (glassmorphism, cores reais, spacing)
> - `cat index.html` (ou `product/design/prototype.html`) — protótipo de alta fidelidade com layout aprovado
> - `cat product/design/design-system.md` — tokens, tipografia, componentes
> Use the EXACT same CSS custom properties (--bg-primary, --accent-gold, etc.), spacing, and glassmorphism.
> Do NOT invent new tokens or deviate from the visual design system.
> ```
> Após o Pi finalizar, auditar a sessão JSONL para confirmar que os arquivos foram lidos
> (ver `pi-session-audit` e referência abaixo).

5. **Antigravity revisa código e testes → produz `review-report.md`**

   ```bash
   ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && cat /tmp/prompt.md | /home/ubuntu/.local/bin/agy --print "$(cat /tmp/prompt.md)"'
   ```
   agy escreve o relatório em `product/engineering/review-report.md`.

6. **Pi modelo best implementa correções baseado na revisão do agy**

   Após agy gerar o `review-report.md`, Pi best (não Hermes) deve implementar as correções:

   ```bash
   pi --name "PROJETO-fixes" -p "$(cat prompts/pi-fixes.md)" --provider opencode-go --model deepseek-v4-pro
   ```

   O prompt do Pi best DEVE incluir:
   - `cat product/engineering/review-report.md` — issues encontradas
   - `cat product/design/design-system.html` — contexto visual do design system
   - `cat product/design/design-system.md` — tokens e especificações
   - `cat index.html` — protótipo aprovado

   ⚠️ **Não fazer os fixes manualmente no Hermes.** O Pi best precisa ver o contexto visual dos HTMLs de design para acertar cores, glassmorphism, tipografia e layout. Fixes manuais sem o contexto visual produzem código funcional mas com drift visual.

8. **Verificação pós-Pi — auditar sessão JSONL para confirmar acesso aos design files:**
   ```bash
   python3 -c "
   import json, glob
   session_dir = sorted(glob.glob('/opt/data/home/.pi/agent/sessions/--*delfos*--/*.jsonl'))[-1]
   text = open(session_dir).read()
   for kw in ['design-system.html', 'prototype.html', 'index.html']:
       if kw in text:
           # Check if it was a READ (cat/read_file) not just ls output
           for line in text.split(chr(10)):
               if kw in line and ('cat ' in line.lower() or 'read_file' in line.lower()):
                   print(f'✅ DESIGN FILE READ: {kw}')
                   break
           else:
               print(f'⚠️  DESIGN FILE MENTIONED but NOT READ (likely ls output): {kw}')
   "
   ```
   Se os arquivos de design não foram lidos (apenas mencionados em `ls`), **recriar o prompt explicitamente instruindo o Pi a ler os HTMLs** antes de gerar frontend. Não aceitar tokens copiados — o Pi precisa ver o layout renderizado.

8. Quando código e testes forem aprovados → avançar para **4d. Docker Build & Deploy**

### Saída

```
product/engineering/
├── SAD.md
├── tech-specs.md
├── ERD.md
├── api-contracts.yaml
├── test-plan.md
├── release-notes.md
├── code-tasks.md
└── feedbacks.md
```

---

### 4c. Post-Code: Test Execution & Debug Loop

> **Referência:** `skill_view(name='product-pipeline', file_path='references/first-test-run-pipeline.md')`

Após executar todas as code-tasks, Pi gera código funcional mas com incompatibilidades de ambiente. Padrão que resolveu ~95% dos erros:

```
1. INSTALAR deps: uv venv + uv pip install -e ".[dev]"
2. CRIAR pytest.ini: asyncio_mode = auto
3. RODAR tests unitários primeiro
4. RODAR tests de integração
5. PI BEST revisa falhas e CORRIGE DIRETAMENTE
6. HERMES valida os fixes
7. COMMIT + AGY re-avalia
```

#### Ordem de prioridade para fixes

| Prioridade | Fix | Impacto típico |
|-----------|-----|----------------|
| 1 | ForeignKey nos models | ~55 erros |
| 2 | bcrypt==4.0.1 | ~10 erros |
| 3 | aiosqlite nas deps | ~2 erros |
| 4 | `from __future__ import annotations` | ~13 erros |
| 5 | pytest.ini com asyncio_mode=auto | ~68 erros |
| 6 | Conftest de integração | ~39 erros |
| 7 | MissingGreenlet | ~25 erros |
| 8 | Trailing slash 307 | ~12 erros |
| 9 | `_task_to_response` sem relationships | ~16 erros |
| 10 | SQLite Date/Time | ~5 erros |
| 11 | Deprecations (utcnow, class Config) | warnings |

---

### 4d. Docker Build & Deploy

> **Referência:** `skill_view(name='product-pipeline', file_path='references/docker-build-deploy.md')`

1. Garantir Dockerfiles (frontend + backend)
2. `docker compose build 2>&1`
3. Corrigir falhas no build
4. Gerar `.env`
5. `docker compose up -d`
6. Verificar com checklist
7. Avançar para **4e. Validação Final**

#### Pitfalls comuns na Oracle VM

| Problema | Solução |
|----------|---------|
| ghcr.io inacessivel | `pip install uv` |
| Porta 80 ocupada | Remapear para `8080:80` |
| Boolean default `0`/`1` no PostgreSQL | Trocar para `sa.text("false")` / `sa.text("true")` |
| Healthcheck 401 | Verificar prefixo do router |

## Deploy: GitHub + Systemd + Nginx

Após o Antigravity aprovar (4e), estruturar o deploy final.

### Oracle Cloud: apenas portas 80/443 abertas externamente

A Oracle Cloud Application Firewall só expõe as portas 80 e 443. Usar Nginx Proxy Manager na porta 80 para expor o app.

**Passos:**

1. **Criar repositório GitHub privado e fazer push**
2. **Clonar para selfhost/** no host
3. **Systemd service** (auto-start no boot)
4. **Conectar à rede do Nginx Proxy Manager**
5. **Proxy reverso** via NPM ou nginx do host

> **Trailing slash bug:** FastAPI gera redirects 307. `$http_host` vs `$host` no proxy_set_header. Solução real: middleware FastAPI com redirect relativo + `redirect_slashes=False`.

---

### 4e. Validação Final pelo Antigravity

> Carrega a skill `dogfood` para QA exploratório antes do veredito.

#### Fluxo

> ⚠️ **Sync crítico entre iterações:** Pi corrige → sincronizar local→shared volume → build → deploy → SÓ ENTÃO agy re-revisa. Ver `references/f4e-review-loop-sync.md` para a sequência completa e checklist de verificação.

0. **Dogfood QA** — teste exploratório sistemático
1. **Hermes coleta evidências** via browser (7 screenshots padrão)
2. **Entrega prints ao usuário** via MEDIA
3. **Salva prompt do agy** como `.md` em `product/engineering/dogfood/prompt-para-antigravity.md`\
   (Se o diretório não puder ser criado por permissão, salvar em `prompts/` e referenciar de lá)
4. **Invocar agy via SSH com `--print`** (ou tmux interativo para prompts longos)
5. **Verificar o veredito** no `feedbacks.md`
6. Se aprovado → Deploy
7. Se rejeitado → Loop de correção

> **Hermes NÃO diagnóstica bugs.** Apenas coleta evidência. A análise é do Antigravity.
>
> ⚠️ **agy code review sozinho NÃO detecta erros de runtime JS** — `fmt is not defined`, `TypeError: Cannot read properties of undefined`, e outros erros de escopo/variável só aparecem quando o navegador executa o código. agy revisando os arquivos `.js` pode aprovar código que quebra em runtime. **Sempre complementar a revisão do agy com verificação no browser:** navegar entre 3-4 views, checar `browser_console()` em cada transição, verificar se a tabela renderiza dados reais. O loop completo é: agy revisa código → browser verifica runtime → se ambos OK → ACORDO.
>
> **Na prática, agy também corrige rotas frontend-backend durante a validação final.**

### Decisão final

| Resultado | Próximo passo |
|-----------|---------------|
| **APROVADO** | MVP concluído. Avançar para F5 ou **deploy frontend separado** (ex: Vercel) |

#### Deploy Frontend Separado (Vercel / Netlify)

Quando o frontend SPA é hospedado separadamente do backend (ex: Vercel + Oracle host):

1. **Criar `frontend/js/config.js`** com `API_BASE` apontando para o backend público:
   ```js
   const API_BASE = 'http://<IP_PUBLICO>:<PORTA>/api/v1';
   ```

2. **Incluir `<script src="js/config.js"></script>` antes dos outros scripts no `<head>`** — config.js deve ser o primeiro script (api.js, auth.js, app.js dependem de `API_BASE`).

3. **Atualizar `api.js` e `auth.js`** para usar `API_BASE` de `config.js` em vez de prefixo relativo:
   - `api.js`: `credentials: 'include'` (não `'same-origin'`)
   - `auth.js`: `fetch(\`${API_BASE}/auth/login\`)` em vez de `fetch('/api/v1/auth/login')`

4. **Atualizar CORS no backend** para incluir o domínio do Vercel na lista de origins.

4. **Criar `vercel.json`** no projeto raiz:
   ```json
   {
     \"version\": 2,
     \"buildCommand\": null,
     \"outputDirectory\": \".\",
     \"rewrites\": [
       { \"source\": \"/(.*)\", \"destination\": \"/index.html\" }
     ]
   }
   ```

5. **Deploy prebuilt** (confiável, evita cache de conteúdo antigo):
   ```bash
   vercel build --prod --yes
   vercel deploy --prebuilt --prod --yes
   ```

6. **Verificar** com `curl -s -o /dev/null -w \"%{http_code}\" https://<projeto>.vercel.app/`

> **Pitfall:** API QA via `execute_code()` não alcança containers no Oracle host via localhost. Usar `ssh oracle-host` + curl diretamente.

⚠️ **Vercel deploy cache — `.vercel/output` stale causa deploys travados** — Após várias iterações de deploy, o diretório `.vercel/output` acumula artefatos de builds anteriores que fazem o `vercel build --prod` gerar output inconsistente. O sintoma: deploy fica eternamente "Building…" no Vercel (status UNKNOWN), múltiplos deploys seguidos ficam travados, upload de apenas 4.8KB quando deveria ser 180KB+. **Fix:** `rm -rf .vercel/output` antes de cada `vercel build --prod`. Após limpar, o build gera o output correto e o deploy completa em <10s.

---
---

## Fase 5: Iteração e Melhoria

> **Skill principal:** `backlog-and-sprint`

1. Usuário testa o MVP
2. Backlog não-estruturada
3. Melhorias pontuais rápidas
4. Sprints (quando solicitado)

---

## Formato do feedbacks.md

Estruturados como **conversas multi-turno entre agentes**:

```markdown
## Turno N — @AgenteRemetente

**Para:** @AgenteDestinatário
**Em resposta ao:** Turno N-1

### Conteúdo

Com status ( / / ), citações, código.

### O que espero de você, @AgenteDestinatário:
- [ ] Ação concreta
```

- **Turno 1** não tem "Em resposta ao"
- **Turno final**: `**Decisão final:** ACORDO: ...`
- Menções a `@Pi`, `@Antigravity`, `@Hermes` são permitidas

---

## Phase Completion Audit

Após cada fase, auditar entregáveis:

```bash
echo "=== FASE [N]: [Nome] ==="
ls -la product/[fase]/*.md 2>/dev/null
grep "PHASE_COMPLETE: [fase]" product/[fase]/PRD.md
```

Itens a verificar:
- [ ] Todos os arquivos da `## Saída` existem?
- [ ] Marcador `<!-- PHASE_COMPLETE: ... -->` presente?
- [ ] F4e: Dogfood QA report gerado?
- [ ] F4e: Antigravity aprovou?
- [ ] Tudo commitado?
- [ ] Usuário revisou e aprovou (F1)?

---

## Pitfalls

⚠️ **agy via SSH pode quebrar permissões do container** — agy (SSH host, uid 1001) pode executar `sudo chown -R ubuntu:ubuntu` no diretório do projeto, e o container Hermes (uid 10000) perde escrita. **Fix REAL (comprovado CFP IA ago/2026):** `sudo chmod -R 777` pelo hermes FALHA com "Operation not permitted" quando o diretório pertence ao uid 1001 — o hermes não é dono nem tem permissão de escrita no pai. A correção que funciona é pelo host: `ssh oracle-host 'sudo chown -R 10000:10000 /home/ubuntu/selfhost/shared/code/workstation/PROJETO'`. Verificar permissões após agy executar. **Prevenir:** antes de cada invocação do agy, rodar o chown de ida; depois, o chown de volta — ou conferir com `ls -ld` se o dono é `hermes`.

⚠️ **Stitch MCP — config no `/opt/data/config.yaml`, NÃO no `.hermes/config.yaml`** — O override (`~/.hermes/config.yaml`) funciona para desenvolvimento rápido, mas o config principal (`/opt/data/config.yaml`) é o repositório oficial. Stitch MCP HTTP não funciona via npx proxy — usar `url:` + `headers:` + `transport: http`. A API key vai no header `X-Goog-Api-Key`. Editar via SSH no host com Python (não sed) para evitar YAML malformado.

⚠️ **Stitch MCP — design system ANTES das screens** — Sempre verificar/atualizar o design system no Stitch antes de gerar screens. Screens geradas com tokens errados (LIGHT em vez de DARK, fonte errada) precisam ser descartadas e regeneradas.

⚠️ **Stitch UpdateDesignSystem — fontes limitadas** — BRICOLAGE_GROTESQUE não funciona no UpdateDesignSystem. Usar SPACE_GROTESK como alternativa. Testar fontes no Update antes de tentar no Create.

⚠️ **Stitch MCP — usar o mesmo design system id em todas as telas** — Para consistência visual, passar `designSystem: assets/<id>` em toda chamada de `generate_screen_from_text`.

⚠️ **agy prototype — executar no host, não no container** — agy está em `/home/ubuntu/.local/bin/agy` no host Oracle. Usar `ssh oracle-host` com `--print` para geração não-interativa. O modelo `gemini-3.1-pro` funciona bem para protótipos complexos. `--print-timeout 5m` evita timeout prematuro.

⚠️ **Stitch MCP — usar HTTP direto, não stdio proxy** — A API key funciona no header `X-Goog-Api-Key` quando usada via HTTP MCP direto (`url:` + `headers:`). O `@_davideast/stitch-mcp` package tem um subcomando `tool` que NÃO funciona com API key. Usar `transport: http` com headers no config do Hermes. Ver `skill_view(name='product-pipeline', file_path='references/google-stitch-mcp.md')`.

⚠️ **Pi best não streama stdout intermediário** — Com DeepSeek V4 Pro, Pi pode levar alguns minutos por documento sem produzir stdout. Monitorar pelos arquivos de saída, não pelo output do processo. Usar `terminal(background=true)` + `ls -la` periódico.

⚠️ **Pi PATH pode não estar definido** — Pi está em `/opt/data/pi-global/bin/pi`. Se `which pi` falhar, exportar PATH ou usar caminho absoluto.

⚠️ **batch-splitting para tarefas grandes do Pi** — Quebrar em lotes de 2-3 docs. v4-pro aguenta ~3 docs/sessão; v4-flash ~2.

⚠️ **Pi parece travado mas output já está completo** — Verificar arquivos no shared volume antes de matar.

⚠️ **Pi cost frontend sem contexto visual dos design HTMLs** — O prompt pode ter os tokens hex copiados, mas Pi NÃO vê o layout renderizado (glassmorphism, posicionamento, protótipo). Isso produz frontend com tokens corretos mas layout genérico. **Sempre incluir `cat design-system.html` e `cat index.html` (protótipo) no prompt do Pi cost** quando o layer for frontend. Verificar pós-execução com auditoria de sessão (passo 8 do F4b).

⚠️ **Prompt file ausente mata Pi silenciosamente** — Se o prompt file não existe (ex: `cat prompts/pi-layer6-polish.md`), Pi morre imediatamente com exit code 1. Verificar `ls prompts/` antes de invocar. Se um layer não tem prompt, criar antes de disparar Pi.

⚠️ **agy SSH: prompt file deve ser copiado para o host** — agy roda no Oracle host, não no container Hermes. O prompt file precisa ser copiado via `cat prompts/file.md | ssh oracle-host 'cat > /tmp/file.md'` antes de invocar. Referenciar com `agy --print "$(cat /tmp/file.md)"` no host. Não é possível ler arquivos do container diretamente do host via agy.

⚠️ **Seed script requer tabelas criadas** — `app/seed.py` assume que as tabelas existem (SELECT antes de INSERT). No container com PostgreSQL, as tabelas são criadas por Alembic. Para testar localmente com SQLite, primeiro criar tabelas: `Base.metadata.create_all(engine)` antes de rodar seed. Seed é idempotente — segunda execução mostra ⏭️ para todas as entradas.

⚠️ **Dockerfile: permissão 600 no host vira arquivo de 0 bytes na imagem** — Quando um arquivo tem permissão `-rw-------` (600) e o dono é o usuário do container (hermes, uid 10000), o Docker daemon não consegue ler o conteúdo durante COPY, resultando em arquivo de 0 bytes na imagem. **Solução:** `chmod 644` em todos os novos arquivos antes de `docker compose build`.

⚠️ **Alembic env.py não deve substituir asyncpg por psycopg2** — O env.py gerado pode conter `configuration["sqlalchemy.url"].replace("postgresql+asyncpg://", "postgresql+psycopg2://")`. `psycopg2` não está instalado na imagem slim. Remover a substituição — `async_engine_from_config()` funciona com asyncpg para DDL. Se migrations não existirem, gerar com `alembic revision --autogenerate -m "initial_schema"` dentro do container.

⚠️ **Portas ocupadas no host Oracle** — Portas comuns (5432, 8000, 80, 8080, 6379) podem estar ocupadas por outros projetos. Verificar com `ss -tlnp | grep -E ":{port} "`. Para db, usar `expose:` em vez de `ports:`. Para backend, usar `expose:` e deixar nginx como única porta externa. Escolher porta alternativa (>8080) e atualizar CORS origins.

⚠️ **Verificação de leitura de design files pelo Pi — auditoria JSONL** — Após Pi gerar frontend, verificar se ele realmente leu os arquivos de design ou só os mencionou em `ls`. Técnica:
```python
import json, glob
for sf in sorted(glob.glob(os.path.expanduser('~/.pi/agent/sessions/--*projeto*--/*.jsonl')))[-5:]:
    text = open(sf).read()
    for kw in ['design-system.html', 'index.html']:
        if kw in text:
            found = any(kw in line and ('cat ' in line.lower() or 'read_file' in line.lower()) for line in text.split(chr(10)))
            print(f'  {"✅" if found else "⚠️"} {kw}: {"lido" if found else "mencionado mas não lido"}')
```
Se não foram lidos, recriar o prompt instruindo explicitamente `cat product/design/design-system.html` antes de escrever frontend.

⚠️ **Frontend pode usar endpoints que não existem no backend** — Pi cost gera frontend e backend separadamente, e o frontend pode referenciar rotas que o backend não implementou (ex: `/actions` em vez de `/tasks`). Verificar todas as URLs no frontend JS contra os routers registrados em main.py. Padrão: `api.get('/actions')` → `api.get('/tasks')`, `api.patch('/actions/${id}')` → `api.patch('/tasks/${id}')`.

⚠️ **Dashboard/Weekly/Timeline routes não existem por padrão** — Pi cost gera apenas CRUD básico (tasks, projects, contexts, auth, search). Endpoints agregados **não são criados** a menos que o prompt os peça explicitamente. Incluir seção de rotas agregadas obrigatórias no prompt.

⚠️ **CORS + credentials + wildcard é inválido** — `allow_origins=["*"] + allow_credentials=True` é rejeitado por navegadores. Usar `allow_origins=settings.CORS_ORIGINS` com lista explícita.

⚠️ **Commit + tag ANTES de invocar Pi para fixes** — Criar checkpoint antes de Pi modificar código.

⚠️ **Tests fora do Docker build context** — `docker cp` obrigatório.

⚠️ **Oracle Cloud: portas** — Apenas 80/443 externas. Usar NPM.

⚠️ **SQLite `func.now()`** — Precisão de segundos. Usar `default=datetime.now(timezone.utc)` em vez de `server_default`.

⚠️ **delegate_task timeout (600s)** — Executar Pi diretamente do Hermes, não delegar.

⚠️ **v4-flash para docs de engenharia** — Suficiente. v4-pro reservado para decisões arquiteturais.

⚠️ **API QA via execute_code não alcança containers Docker** — `execute_code()` roda dentro do container Hermes e não consegue alcançar containers no Oracle host via localhost. Para API QA, usar `ssh oracle-host` + curl diretamente no terminal, ou apontar para o IP do gateway Docker (`172.19.0.1`).

⚠️ **`agy -p` stallou em Docker commands**

⚠️ **`agy design` NÃO valida código existente** — Gera novo design hipotético. Usar browser tools.

⚠️ **Hermes coleta evidência, NÃO diagnóstica bugs na 4e** — Só reportar o que viu.

⚠️ **Permissão do container — agy pode quebrar com chown** — evitar. Ver pitfall "agy via SSH" acima.

⚠️ **agy output token limit (>70KB)** — Quebrar em CSS/HTML/JS separados.

⚠️ **UID mismatch** — Hermes (10000) vs Pi (1001). Verificar permissões antes de cada fase.

⚠️ **Pre-flight check** — Verificar antes de cada fase. O usuário não quer gastar tokens debugando permissão.

⚠️ **Workstation 777 não herda** — Rodar `chmod -R 777` após criar pastas.

⚠️ **Git add com path explícito** — `git add product/management/` em vez de `-A`.

⚠️ **Pi skills não existem por padrão** — Instalar manualmente.

⚠️ **MiniMax M3 free encerrado** — Usar `opencode-go/deepseek-v4-pro`.

⚠️ **DeepSeek v4-Pro timeout** — Usar v4-flash ou `/compact preserve:context`.

⚠️ **F1 scope: manter conceitual** — Feature matrix, schema de dados, entidades e arquitetura são materiais de F3 em diante. A ideação deve ficar em nível de promessa, persona, nome/conceito e delimitação de escopo. **Não fixar entidades, schemas ou campos durante a consolidação da F1** — o que importa são as regras (ex: "IA não altera o schema"), não a estrutura em si. O nome do projeto carrega o conceito — registrar no `ideation-result.md`.

⚠️ **Mirror `<projeto>.old/`** — Verificar e remover lixo após corrigir permissões.

⚠️ **Frontend scaffolding** — Criar arquivos manualmente, não usar `create-vite`.

⚠️ **Pi adora "***" como placeholder de senha** — Substituir por `"secret123"`.

⚠️ **Backend restart: ConnectionResetError** — Aguardar health check 200.

⚠️ **UUID no PostgreSQL vs String(36)** — Usar `UUID` do dialect PostgreSQL.

⚠️ **Pi best overshoot em conftest** — Não aceitar mudança no `event_loop` sem testar.

⚠️ **Prompt files no shared volume** — UID mismatch bloqueia leitura do Pi.

⚠️ **web_search rate-limit por sessão** — Primeiras 1-2 chamadas paralelas de `web_search` funcionam, mas chamadas subsequentes na mesma sessão retornam `{"data": {"web": []}}`. Isso NÃO é "backend quebrado" — é exaustão de cota por sessão. **Workaround:** front-load TODAS as queries críticas na primeira chamada paralela (até 5 queries em um batch). Se queries subsequentes falharem, ir direto para `web_extract` em URLs de alta autoridade conhecidas. Não retentar `web_search` com phrasing diferente — não vai recuperar. Ver `references/market-gtm-research-sources.md`.

⚠️ **Blogs de plataformas edtech reestruturados** — Thinkific, Kajabi, LearnWorlds, Teachfloor, Mighty Networks e similares reestruturaram blogs em 2024-2025. URLs de artigos 2022-2024 retornam 404 generalizado. Para pesquisa de mercado de cursos/edtech, usar sites de research/CRO (acceleroi.com, firstpagesage.com, digitalapplied.com) e market research firms (gminsights.com) — essas fontes têm dados de benchmark persistentes. Ver `references/market-gtm-research-sources.md`.

⚠️ **bcrypt pin** — `bcrypt==4.0.1` no Dockerfile.

⚠️ **patch/write_file falha com UID 1001** — `chmod o+w` no diretório pai ou usar SSH.

⚠️ **Google OAuth PKCE — setup.py não persiste code_verifier** — O script `setup.py` do google-workspace gera URLs de auth sem salvar o PKCE verifier. A troca falha com `Missing code verifier`. Usar `google_oauth_gen.py` + `google_oauth_exchange.py`. Ver `skill_view(name='product-pipeline', file_path='references/google-oauth-pkce-workaround.md')`.

⚠️ **Google token expira após ~7 dias** — Refresh falha com `invalid_grant`. Re-autenticação completa PKCE necessária.

⚠️ **Pi salva arquivos no path LOCAL, não no shared volume — sincronizar ANTES da revisão do agy** — Quando o projeto está clonado em `/opt/data/<projeto>/`, o Pi Agent salva em `/opt/data/<projeto>/product/` (path local), mas o agy SEMPRE lê de `/home/ubuntu/selfhost/shared/code/workstation/<projeto>/product/` (shared volume). Se a sincronização for feita só depois do deploy, o agy vê os arquivos ANTIGOS e reporta "NÃO RESOLVIDO" para correções que já foram aplicadas. Isso força uma iteração extra no loop de revisão — desperdiçando tokens e tempo.

**Sequência correta após Pi terminar:**
```bash
# 1. Sincronizar do path local → shared volume (ANTES de qualquer review)
cp /opt/data/<projeto>/product/design/js/app.js /opt/data/code/workstation/<projeto>/product/design/js/app.js
cp /opt/data/<projeto>/product/design/js/router.js /opt/data/code/workstation/<projeto>/product/design/js/router.js
cp /opt/data/<projeto>/product/design/js/views/*.js /opt/data/code/workstation/<projeto>/product/design/js/views/
cp /opt/data/<projeto>/product/engineering/*.md /opt/data/code/workstation/<projeto>/product/engineering/

# 2. Rodar build.sh do path LOCAL (copia para public/)
cd /opt/data/<projeto>/product/design && bash build.sh

# 3. Deploy (vercel build + vercel deploy --prebuilt)

# 4. SÓ ENTÃO invocar agy (que lê do shared volume)
ssh oracle-host '/home/ubuntu/.local/bin/agy --print "..." --dangerously-skip-permissions'
```

**Verificação de sincronização:**
```bash
# Comparar timestamps — shared volume deve ser >= local
ls -la /opt/data/<projeto>/product/design/js/app.js /opt/data/code/workstation/<projeto>/product/design/js/app.js
```

> Exemplo real: VERO F4e — agy reportou 4 issues como "NÃO RESOLVIDO" na iteração 2 porque o router.js e app.js corrigidos pelo Pi não foram sincronizados para o shared volume. O Pi corrigiu corretamente (try/catch, admin route, compras view, secondaryNavs), mas o agy leu as versões antigas. Após `cp` manual, agy aprovou `ACORDO: MVP APROVADO`.

⚠️ **agy headless requer --dangerously-skip-permissions** — Sem essa flag, o agy em modo `--print` (não-interativo) NÃO consegue usar `write_file`. O output será: `no output produced — a tool required the "write_file" permission that headless mode cannot prompt for, so it was auto-denied`. **Sempre usar:**
```bash
ssh oracle-host '/home/ubuntu/.local/bin/agy --print "$(cat /tmp/prompt.md)" --dangerously-skip-permissions'
```

⚠️ **NUNCA avançar fases sem a anterior concluída** — O usuário corrigiu este comportamento 2x: "Espere cada etapa terminar antes de seguir para a próxima. Seja fiel à skill." e "Espere as revisões terminarem antes de seguir as etapas seguintes." Execução sequencial estrita é mandatória. Use `process(action='wait')` para bloquear até o processo terminar antes de iniciar a próxima fase.

⚠️ **Verificar TODAS as issues do agy antes de fazer deploy** — Após Pi corrigir baseado no feedback do agy, verificar CADA issue listada no `feedbacks.md` ou `review-report.md`. Não confiar que "Pi corrigiu tudo" — auditar explicitamente. Padrão: `grep "RESOLVIDO\|🟢\|ACORDO"` no arquivo de feedback. Só fazer deploy quando TODAS as issues 🔴 estiverem resolvidas e agy tiver escrito `ACORDO`.

⚠️ **Subagentes F2 precisam de instrução explícita de fallback** — web_search rate-limita após 1-2 chamadas. Subagentes não sabem disso e ficam em loop de retry. Instruir NO CONTEXTO do delegate_task: "Se web_search retornar vazio 2x seguidas, ABANDONE web_search e use SOMENTE web_extract + browser_navigate em URLs diretas. Não insista em web_search com phrasing diferente."

⚠️ **NUNCA escrever frontend manualmente** — "Aliás, pode apagar tudo de frontend feito manualmente por você na última tentativa." Todo HTML/CSS/JS é gerado exclusivamente por Pi Agent. Hermes não edita código. Se o Pi gerou algo incompleto, Pi corrige (com feedback do agy), nunca Hermes.

⚠️ **design-system.html PODE ser o frontend deployável** — Para MVPs puramente frontend (SPA estática com dados mockados, deploy Vercel/Netlify), o `design-system.html` gerado pelo Pi na F4a frequentemente é funcional o suficiente para ser o frontend final. Não precisa executar 103 code-tasks da F4b se o HTML já cobre todos os módulos. Decisão: verificar se o design-system.html tem SPA routing, todos os modais do PRD e dados mockados. Se sim → deploy direto. Se não → Pi cost executa code-tasks para preencher gaps.

⚠️ **F4b code-tasks docs são corrigidos no MESMO loop que o código** — Quando agy revisa F4b, ele encontra issues tanto no código quanto nos docs de engenharia (code-tasks.md, ERD.md, test-plan.md, etc.). O Pi best DEVE corrigir AMBOS na mesma iteração. Não corrigir só o código e deixar os docs com issues pendentes — isso gera deploy com docs inconsistentes.

⚠️ **Gap review após pull/rebrand — verificar estado real antes de agir** — Quando o usuário faz alterações no repo (pull, rebrand, refactor), o estado do código pode ser radicalmente diferente do esperado. Antes de fazer deploy ou correções, executar `git pull` e depois Pi best faz revisão exaustiva (code-review + dogfood QA) gerando `gap-report.md` que mapeia TODOS os gaps vs PRD + referência de UI. Só então decidir se deploya direto ou executa correções. Exemplo real: V6.0 rebrand reduziu design-system.html de 118KB para 1.3KB placeholder — deploy sem gap review teria publicado shell vazio. Template do relatório em `skill_view(name='product-pipeline', file_path='references/gap-report-template.md')`.

⚠️ **Gap report define plano de ação, não apenas diagnóstico** — O gap-report.md de 83 itens do VERO organizou as correções em 5 fases com estimativas de esforço (Fundação 8h → Services 6h → Modais 14h → Fluxos 6h → UX 6h), totalizando ~40h alinhadas com o code-tasks.md. Esse padrão de fases é reutilizável: usar como template para qualquer projeto que precise de correção pós-gap-review.

⚠️ **Pi best refatora monólito → modular em uma sessão** — Com deepseek-v4-pro, Pi consegue refatorar um arquivo HTML monolítico de 80KB em 35+ arquivos modulares (CSS, JS, views, services, utils, store) em ~12 minutos. Incluir no prompt: estrutura de diretórios desejada, regras de modularização, e seed data expandido. O build.sh e verificação `node --check` garantem que a saída é funcional. Padrão comprovado no VERO Fase 1.

⚠️ **F4a e F4b têm o MESMO loop de revisão (agy→Pi→agy até ACORDO)** — Não tratar F4b como "revisão única". O fluxo é idêntico ao F4a: agy revisa → Pi corrige → agy re-revisa → repete até agy escrever `ACORDO: ENGENHARIA FINALIZADA`. Na prática, foram necessárias 2 iterações para F4b (6 issues na 1ª, 0 na 2ª). Nunca fazer deploy com issues 🔴 pendentes no review-report.md.
- ⚠️ **O loop de revisão agy é OBRIGATÓRIO também em code-tasks de demonstração 100% mock (F4a demo loop).** Correção real do usuário (CFP IA, ago/2026): *"Você não parece ter carregado todo o loop da skill. Tem a parte de revisão com o Agy no final. Relembre a skill product-pipeline corretamente"* — eu tinha planejado só Pi gera → build → commit, sem agy. O plano correto para QUALQUER execução de code-tasks (mesmo mock-only, fechando lacunas de demonstração) é: Pi gera (lotes sequenciais, nunca paralelo) → **sync local→shared volume** → agy Turno 1 (escreve feedbacks.md) → Pi Turno 2 (correções) → agy Turno 3 (re-review até `ACORDO: DEMO FINALIZADA`) → build → commit.
- ⚠️ **Auditoria de protótipo F4a: mock data é ESPERADO, não é gap.** Ao auditar rastreabilidade de protótipo de alta fidelidade (pré-integração), avaliar se cada passo de cada fluxo é **REPRODUZÍVEL na tela com dados mockados** — e NÃO se está conectado ao backend. Usar a classificação DEMONSTRADO / DEMONSTRÁVEL PARCIAL / NÃO DEMONSTRÁVEL. Dois passos de auditoria: v1 (critério backend — marca tudo PARCIAL) e v2 (critério mock — isola gaps reais de demonstração). Método completo, matriz card-a-card do dashboard e checklist do que NÃO é gap: `references/prototipo-mock-audit-criterio.md`.

⚠️ **Verificação de completude de formulários — comparar campo a campo** — Modais de criação frequentemente têm 70-90% dos campos ausentes. Para verificar: ler `referencia_completa_de_ui.md` (checklist definitiva), abrir cada modal no browser, comparar cada campo individualmente. Exemplo: modal de Aplicação tem 6 blocos com 25+ campos na referência, mas implementação atual tem 1 campo. Usar Pi + dogfood para auditoria sistemática, NÃO confiar em inspeção visual rápida.

⚠️ **Correção massiva de modais em um único prompt Pi** — Após gap review, é mais eficiente consolidar TODAS as correções de modais (Fases 3-5) em UM prompt Pi best (~9KB) do que em sprints separados. Um prompt exaustivo listando cada campo de cada modal (referenciando `referencia_completa_de_ui.md`) permite que o Pi reescreva todas as views em uma sessão (~12-15 min, deepseek-v4-pro). O padrão: "Para cada view, completar TODOS os campos da referência de UI. Nenhum campo pode faltar." Testado com 8 views reescritas em uma execução (VERO Fase 3-5).

⚠️ **Monitoramento de Pi — intervalos curtos** — Usuário prefere monitoramento frequente com intervalos de 2-3 minutos (não 5+). Verificar arquivos de saída com `find` a cada ~120s. Se o Pi ficar 5+ minutos sem escrever novos arquivos, auditar a sessão JSONL para ver se estagnou (skill `pi-session-audit`).

⚠️ **SPA vanilla: 3 registros obrigatórios ao adicionar uma nova view** — Quando Pi cria uma nova view (ex: `compras.js`, `admin.js`) em uma SPA vanilla, o `app.js` precisa de 3 registros explícitos ou a navegação quebra silenciosamente (clique no sidebar não faz nada, sem erro visível, fica na página anterior):
1. **Rota:** `VERO.router.route('compras', () => VERO.views.compras.render(container))` — sem isso, o router não encontra o handler
2. **secondaryNavs:** `secondaryNavs.compras = [...]` ou `secondaryNavs.compras = null` — sem isso, `updateSecondarySidebar()` lança TypeError ao acessar propriedade de `undefined`
3. **RBAC (se necessário):** `if (!VERO.authService.temPermissao('admin')) { renderAcessoRestrito(); return; }` — sem isso, usuários sem permissão acessam rotas restritas

**Verificação pós-Pi:**
```bash
# Confirmar que cada nova view tem os 3 registros
grep "router.route.*compras\|router.route.*admin\|router.route.*faturamento" js/app.js
grep "secondaryNavs.*compras\|secondaryNavs.*admin\|secondaryNavs.*faturamento" js/app.js
grep "temPermissao.*admin" js/app.js
```
> Exemplo real: VERO F4e — agy identificou 4 bugs de router (admin não registrado, compras como placeholder, secondaryNavs sem apontamentos, JS exception na troca de views) mesmo com o código de view correto. Todos eram falhas de wiring no app.js.
>
> **Quando o wiring quebra em massa (50+ placeholders com todas as views existindo):** Ver `references/mass-route-reconnection.md` — padrão de reescrita do router que conecta as views existentes em uma sessão Pi, eliminando todos os renderPlaceholder de uma vez.

⚠️ **IIFE closure scope bug em views vanilla JS** — Padrão recorrente em SPA com módulos IIFE: `var store = VERO.store, dom = VERO.dom, fmt = VERO.format` declarado DENTRO de `render()`, mas funções helper como `_renderRows()`, `_paginationHtml()`, `_modalHtml()` tentam usar essas variáveis sem tê-las em escopo. O erro em runtime é `ReferenceError: fmt is not defined` ou `TypeError: Cannot read properties of undefined (reading 'get')`.

**Sintoma:** Router tenta carregar a view, console mostra `VERO Router: erro ao carregar módulo "apontamentos"`, tela mostra fallback "⚠️ Erro ao carregar módulo".

**Fix correto:** Passar `fmt`/`store`/`dom` como PARÂMETROS para as funções helper que precisam deles:
```js
// ERRADO — fmt só existe dentro de render()
function render(container) {
  var store = VERO.store, fmt = VERO.format;
  html += _renderRows(store, items);  // _renderRows não acessa fmt
}
function _renderRows(store, items) {
  items.forEach(function(a) {
    html += '<td>' + fmt.formatData(a.data) + '</td>';  // ReferenceError!
  });
}

// CERTO — passar fmt como parâmetro
function render(container) {
  var store = VERO.store, fmt = VERO.format;
  html += _renderRows(store, items, fmt);
}
function _renderRows(store, items, fmt) { ... }

// Também cerTO — declarar no escopo IIFE (se a view for carregada depois das deps)
VERO.views.apontamentos = (function() {
  var store = VERO.store, dom = VERO.dom, fmt = VERO.format;  // IIFE scope
  function render(container) { ... }
  function _renderRows(items) { ... }  // acessa fmt do closure
})();
```
**Atenção com IIFE-level:** Só funciona se o script da view carregar DEPOIS de store.js, dom.js e format.js no index.html. Se houver dúvida sobre ordem de carregamento, prefira passar como parâmetro.

**Verificação pós-Pi em todas as views:**
```bash
# Encontrar funções helper que usam fmt/store/dom mas não os recebem como parâmetro
for f in js/views/*.js; do
  helpers=$(grep -n "function _" "$f" | grep -v "render")
  fmt_in_render=$(sed -n '/function render/,/^  }/p' "$f" | grep -c "var.*fmt = VERO.format")
  echo "$f: render declara fmt=$fmt_in_render, helpers=$(echo "$helpers" | wc -l)"
done
```

**Variante: variable shadowing em callbacks aninhados** — O mesmo padrão de escopo pode ocorrer via shadowing acidental: `var s = VERO.store` declarado no topo, mas um `reduce` interno usa `s` como nome de acumulador, sombreando a store. Sintoma: `TypeError: s.find is not a function` (porque `s` virou número). **Fix:** usar nomes distintos (`store` para a store, `acc`/`sum` para acumuladores). Ver `references/variable-shadowing-in-callbacks.md` para diagnóstico completo, checklist de nomes e script de detecção. Exemplo real: `nutricao-aplicacoes.js` — `s` era `VERO.store` mas foi sombreado por `s` no `reduce` interno.

> Exemplo real: VERO — apontamentos.js quebrou após modularização. `fmt` declarado em `render()` mas usado em `_renderRows()` e `_refreshTable()`. Corrigido passando `fmt` como 3º parâmetro. Outras 6 views não usavam `fmt` e estavam OK.

⚠️ **Pi "done" summary NÃO é evidência — agy SEMPRE re-verifica** — Após Pi executar um lote grande de tasks (ex: 81 tasks), o output summary do Pi lista bullet points do que foi feito, mas isso é ASPIRACIONAL, não factual. Na prática: Pi disse que implementou CSS da sidebar secundária, conectou 21 views ao router, expandiu seed data e atualizou 7 modais — agy verificou e NENHUMA dessas entregas estava completa. O CSS não existia, as views estavam órfãs (`renderPlaceholder`), seed data não foi expandido, e só 1 de 7 modais foi atualizado. **Nunca pular a revisão do agy após Pi executar code-tasks em lote — Pi superestima seu próprio progresso.** O agy é a única fonte confiável de verificação de completude.

⚠️ **Hierarchy-driven expansion — quando o usuário fornece uma especificação de UI completa** — Se um documento como `hierarquia_de_páginas_e_componentes.md` é fornecido definindo cada página, sub-página, filtro, coluna de tabela e campo de modal, o fluxo correto é:
1. `git pull` para obter o estado mais recente (inclui design-system atualizado + hierarquia)
2. Pi best gera `code-tasks-v2.md` analisando o delta entre implementação atual e a hierarquia
3. Pi best executa TODAS as tasks em uma sessão (deepseek-v4-pro, timeout 60min)
4. SINCRONIZAR local → shared volume
5. Build + deploy
6. agy revisa integridade estrutural (views conectadas? CSS implementado? seed data expandido?)
7. Pi corrige issues do agy → agy confirma → ACORDO
8. Dogfood QA no browser (verificar runtime JS, navegação entre 3-4 views)
9. Relatório + commit + push

> Cuidado: Pi tende a implementar ~60% do escopo na primeira execução e reportar 100%. O agy normalmente encontra 3-5 issues críticas (CSS ausente, views órfãs, seed data não expandido). Uma segunda iteração resolve.

⚠️ **Sidebar alignment audit — verificar contra referencia_completa_de_ui.md** — Após Pi gerar o sidebar (app.js + index.html), SEMPRE verificar contra a referência de UI item por item. Pi frequentemente introduz desvios:

| Desvio comum | Exemplo real | Correção |
|-------------|-------------|----------|
| **Nome errado** | "MIP e MID" em vez de "MIP e MED" | Renomear no HTML do sidebar |
| **Item ausente** | "Apontamentos" não listado | Adicionar à lista de links |
| **Item extra** | "Colheita" no sidebar (não está na ref) | Remover — Colheita é sub-fluxo, não item do menu |
| **Sem grupos** | Todos os links planos, sem labels de seção | Adicionar section headers (PRODUÇÃO AGRÍCOLA, etc.) |
| **Admin ausente** | "⚙️ Administrador" não aparece | Adicionar ao final do sidebar com RBAC |
| **Telas placeholder** | Módulos secundários renderizam `renderPlaceholder()` em vez da view real | Registrar rota com `VERO.views.compras.render(container)` |

**Checklist de verificação pós-Pi:**
```bash
# 1. Sidebar tem todos os itens da referência?
grep -c "Apontamentos\|MIP e MED\|Administrador\|PRODUÇÃO AGRÍCOLA" index.html

# 2. Nenhum placeholder escapou? (não deve ter nenhum match)
grep -c "renderPlaceholder" js/app.js

# 3. Colheita NÃO está no sidebar? (deve ser 0)
grep -c "Colheita" index.html | grep -v "title\|heading"

# 4. Nomes estão corretos? (deve ser 0)
grep -c "MIP e MID" index.html js/app.js
```
> Exemplo real: VERO — sidebar tinha "MIP e MID", faltava "Apontamentos" e "Administrador", incluía "Colheita" indevidamente, 9 telas mostravam "Em desenvolvimento". Tudo corrigido em um prompt Pi de 4.8KB.

⚠️ **design-system.html PODE ser o frontend deployável** — Para MVPs puramente frontend (SPA estática com dados mockados, deploy Vercel/Netlify), o `design-system.html` gerado pelo Pi na F4a frequentemente é funcional o suficiente para ser o frontend final. Não precisa executar 103 code-tasks da F4b se o HTML já cobre todos os módulos. Decisão: verificar se o design-system.html tem SPA routing, todos os modais do PRD e dados mockados. Se sim → deploy direto. Se não → Pi cost executa code-tasks para preencher gaps.

## Status Audit Quinzenal (pós-reunião com parceiro)

Quando o usuário pede "verifique em que ponto estamos" em projeto de ciclo quinzenal (ex: CFP IA), o fluxo comprovado é: **triangular** repo local (`git log` + `git status` + `git log origin/main`) + `session_search` + Google Docs (transcrição da reunião e docs do parceiro via `$GAPI docs get`), **cruzar** decisões da reunião vs. PRD/roadmap para achar lacunas, e entregar DOIS arquivos .md no repo: relatório de status + plano de ação com responsáveis e dependências.

**Referência completa:** `skill_view(name='product-pipeline', file_path='references/quinzenal-status-audit.md')` — extração de transcrições Fathom/Google Docs (JSON → body separado → ler em blocos), estrutura do relatório, formato do plano de ação por blocos (A–G) e pitfalls (Write denied fora de /opt/data, token expirado, decisão ≠ implementação). Se `session_search` não achar a sessão (FTS5 não indexa a mais recente), consultar `/opt/data/state.db` direto — `references/hermes-recent-session-lookup.md` (IDs truncados: casar com `LIKE '<prefixo>%'`).

### Reorganização do plano em Workstreams (quando o usuário decide execução simultânea)

Quando o usuário decide que duas quinzenas/fases serão executadas de forma **coordenada e simultânea** (ex: Q2+Q3 com culminação única), **reorganizar o plano de ação em workstreams paralelos (WS-N)**, não em blocos sequenciais por fase. Padrão comprovado no CFP IA (ago/2026):

- Cada WS agrupa tarefas de um domínio (ex: WS-1 Fundação/Spec, WS-2 UX & Conceito, WS-3 Conteúdo do parceiro, WS-4 Engenharia).
- Cada item mantém: responsável, prazo, e **o que bloqueia** (coluna "Bloqueia" — mapeia dependências em cadeia).
- Incluir uma linha do tempo de **checkpoints** (ex: 14/08 fundação, 18/08 specs, 21/08 integração, 24/08 culminação) — marcos de verificação, não fases isoladas.
- Identificar explicitamente o(s) item(ns) **independente(s)** que podem começar imediatamente (no CFP IA: o motor de cálculo não dependia de ninguém).
- **Manter o roadmap original intocado** — a reorganização é do plano de execução, não do cronograma. O usuário explicitamente pediu para não alterar o roadmap.
- Itens que o usuário marca como "responsável = parceiro" NÃO são executados por você: preparar o contexto/insumos e atribuir a ele.

> **Caso completo:** `skill_view(name='product-pipeline', file_path='references/cfp-ia-q2q3-integrated-cycle.md')` — decisões do usuário, Base Técnica (arquitetura: núcleo agêntico Hermes-like + MCP + API única + Next.js + WhatsApp/Telegram + knowledge engine OKF), documentos produzidos no repo e pitfalls do ciclo.

### Execução autônoma de workstreams — PUBLICAR a matriz de dependências ANTES de rodar

> 📖 Ondas + 🔴/🟢 + pitfalls: `references/execucao-autonoma-ondas-politica-decisao.md` · espectador TUI ao vivo: `references/live-session-viewer-pi-tui.md`

Usuário aprova execução autônoma → **análise de dependências publicada antes**, não sequencial silenciosa. Correção real (CFP IA, ago/2026): *"Você chegou a verificar quais pontos do WS4 já poderiam ser feitos antes da conclusão do WS3? Ou só saiu fazendo tudo?"*

Padrão comprovado:
1. **Publique a matriz de dependências primeiro** — para cada item do WS que "não depende" do bloco do parceiro, diga: `❌ Não depende → ✅ posso fazer agora` vs `✅ Depende → ⏸️ aguardando`. O usuário quer VER o raciocínio, não descobrir depois.
2. **Identifique o item independente mais valioso e comece por ele** — no CFP IA foi o motor de cálculo determinístico (spec 100% pronta nas diretrizes, zero dependência externa).
3. **Dispare jobs Pi cost em background SEQUENCIAL** — `pi --name "PROJETO-tarefa" -p "$(cat prompts/pi-x.md)" --provider opencode-go --model deepseek-v4-flash` com `background=true` + `notify_on_complete=true`. Não rode 2+ jobs Pi pesados em paralelo (v4-flash demora 5–16 min por job grande; paralelismo não acelera e arrisca rate-limit).
4. **Monitore pelos ARQUIVOS, não pelo stdout** — Pi escreve em rajadas: `ls -la` nos diretórios de saída; audite o JSONL da sessão (`pi-session-audit`) para distinguir "lendo contexto" (poucas entries, sem toolCall) de "escrevendo" (entries com `cat >`).
5. **Não bloqueie no wait** — prepare o prompt do PRÓXIMO job enquanto o atual roda (padrão: `prompts/pi-ws4-*.md` prontos antes do job anterior terminar).
6. **Registre pendências explícitas do usuário** — itens que só ele resolve (ex.: chave OpenRouter, créditos, sinalização de fim de sprint) viram linha no relatório final, nunca ficam implícitos.
7. **Reporte explicitamente as FASES DO PIPELINE adiadas** — quando o usuário manda "adiante tudo que não depender do WS3", avançar só o back-end não significa que F4a/F4d/F4e foram concluídas. Correção real (CFP IA, ago/2026): *"Temos o protótipo de alta fidelidade gerado? ... você as pulou por estar esperando alguma entrega minha e do Igor ou por esquecimento?"* Padrão: no relatório final, listar por fase o que foi feito vs. adiado e POR QUÊ (bloqueio real vs. dependência vs. decisão de escopo). F4a (design system renderizado + protótipo de alta fidelidade Next.js + Stitch) costuma ser o elo perdido quando a instrução foi só "adiante o back-end". Nunca deixar o usuário descobrir a fase pulada perguntando.

### Auditoria de rastreabilidade (produto ↔ design ↔ código)

Quando o usuário pergunta se PM/designer/engenharia "concordariam que tudo está encadeado e implementado" (user stories e flows implementados?), NÃO responder por opinião — executar auditoria com evidências: inventariar código (endpoints, motor, telas), rodar testes (`.venv/bin/python -m pytest tests/ -q`), detectar descontinuidade frontend↔API (mock vs fetch por tela) e entregar tabela de rastreabilidade por camada. Protótipo de alta fidelidade usar mock data é esperado (F4a); integração é fase separada (F4d). Ver `references/traceability-audit.md`.

### Casos completos para especialista de domínio — artefatos brutos simulados obrigatórios

Quando "casos completos" de usuários são insumo para um especialista humano (CFP, consultor), o usuário exige que os **artefatos brutos simulados sejam os que a pessoa subiria no app**: extratos bancários, faturas de cartão, contratos com taxas/CET — com números batendo exatamente com o orçamento do caso. Requisito explícito do usuário (ago/2026): *"Os arquivos de cada usuário das entrevistas devem ser os mesmos que ele subiria se usasse a aplicação como fonte."* Ver `references/casos-completos-artefatos-brutos.md` para o padrão completo (geração via Pi cost com design system temporário, consistência numérica, PDF via WeasyPrint, entrega no Drive em Google Docs/PDF — nunca .md para o parceiro).

**Chaves de provedor para validação de LLM:** as chaves de teste do ambiente estão em `~/.pi/agent/auth.json` (campos `openrouter.key`, `opencode.key`, `opencode-go.key`, `deepseek.key`). Para validar um LLM (ex.: WS4-13), ler a chave daí em vez de pedir ao usuário — mas NUNCA expor a chave completa em outputs/logs (mascarar). Se a chave do provedor-alvo não existir, rodar em `--dry-run` e reportar como pendência do usuário — nunca inventar resultado. Detalhes de endpoint/auth/armadilhas (opencode-go aceita `Authorization: Bearer` e NÃO `x-api-key`; urllib precisa de User-Agent Mozilla senão Cloudflare 403 error 1010; `GET /models` pode dar 403 mesmo com auth ok — ir direto no POST; falso positivo do detector de palavras proibidas quando o usuário ecoa a palavra): `skill_view(name='product-pipeline', file_path='references/llm-endpoint-probe.md')`.

### Entregáveis para parceiro não-técnico (Google Docs/Sheets/PDF, nunca .md)

> 📖 **Flowcharts mermaid → imagens no Google Docs:** quando o espelhamento para o Drive exige substituir blocos ```` ```mermaid ```` por imagens renderizadas, ver `references/mermaid-flowcharts-to-docs.md` — render via mmdc + headless_shell do Hermes, fundo transparente 2x, upload Drive público, `insertInlineImage` com dimensionamento para caber (pageless não existe na API), e a regra de NUNCA tocar no browser do host.

> 📖 **Auditoria de rastreabilidade (protótipo vs user flows/stories):** quando o usuário pergunta se as US/fluxos estão contemplados no protótipo, ver `references/prototype-traceability-audit.md` — prompt Pi Cost auto-contido, validação com pi-session-audit, estrutura do relatório (matrizes US/fluxo, gaps, backend pronto para conectar).

Quando um parceiro do projeto (ex: CFP certificado, especialista de domínio) tem disponibilidade limitada e **não lê .md nem código**, todo material para ele deve ser preparado em formatos de apresentação:

- **Google Docs / Google Planilha / PDF exportado de HTML** (usando o design system temporário como base visual).
- Estruturar como **UM documento mestre único, simples e didático, não muito extenso**, contendo: entregáveis claros, relevância de cada entrega (por que é crítica), o que é necessário para prosseguir (dependências), e onde está o contexto de apoio (links para os Docs do Drive).
- Todo contexto de apoio deve estar **na pasta do Google Drive do projeto, propriamente formatado** — o parceiro não vai abrir o repo.
- Casos completos montados por você (ex: dados completos dos 3 perfis) viram insumo para o parceiro escrever recomendações em texto corrido; depois você gamifica/estrutura.
- **Organização no Drive em subpastas numeradas por entrega (01..N)** com templates preenchíveis, PDFs de docs ricos (tom, casos) via WeasyPrint com o design system, guia mestre com links diretos, e move de arquivos via PATCH na API (GET parents → PATCH addParents/removeParents com token de `google_token.json`). Padrão completo e pitfalls (search sem `trashed=false` inclui lixeira; `drive delete` → trashed reversível): `skill_view(name='product-pipeline', file_path='references/partner-drive-deliverable-package.md')`.
- **Flowcharts mermaid → imagem nos Google Docs:** `.md` ficam só texto; o espelhamento renderiza ` ```mermaid ` como PNG transparente 2x (mmdc + headless_shell do Hermes — NUNCA o Chromium snap do host) e insere via `insertInlineImage` dimensionado para caber. Pageless NÃO é possível via API (issue 227875469). Ver `skill_view(name='product-pipeline', file_path='references/mermaid-to-docs-images.md')`.

### AGENTS.md na raiz do repo (governança de documentos)

Estabelecer `AGENTS.md` na raiz do repositório do projeto registrando:
- **Hierarquia de documentos em caso de conflito** (padrão CFP IA): 1) decisões de reuniões/transcrições → 2) PRD → 3) documento de diretrizes → 4) demais documentos. Regra prática: decisão de reunião vence e o PRD deve ser atualizado.
- **Regra de sincronização com Google Drive**: subpasta "Produto" do Drive só é atualizada quando o usuário sinalizar explicitamente que a sprint/quinzena foi finalizada — nunca automaticamente.
- **Design system temporário como referência visual de TODOS os documentos do projeto** (não só pesquisa) — quando o usuário ampliar o escopo, atualizar o AGENTS.md e o skill.

## Verificacao Rapida

```bash
# Antes de iniciar o pipeline ou cada fase
pi --version
pi -p "list skills" --provider deepseek --model deepseek-v4-flash
ls /opt/data/code/workstation/PROJETO/product/ 2>/dev/null
ssh oracle-host 'echo "n" | timeout 5 /home/ubuntu/.local/bin/agy 2>&1 | head -3'
git config user.name && git config user.email
touch /opt/data/code/workstation/PROJETO/.perm-check 2>/dev/null && rm $_ && echo "OK" || echo "BLOQUEADO"
```

## Gap Review (pós-pull / rebrand)

Quando o usuário faz alterações não-coordenadas no repo (pull, rebrand, refactor manual), o estado do código pode divergir radicalmente do esperado. Executar gap review formal ANTES de deploy ou correções.

**Fluxo completo:** `skill_view(name='product-pipeline', file_path='references/gap-review-post-pull.md')`

**Template de relatório:** `skill_view(name='product-pipeline', file_path='references/gap-report-template.md')` — formato comprovado com 83 gaps mapeados no VERO.

Resumo rápido:
1. `git pull` + verificar diff de tamanho dos arquivos
2. Pi best faz revisão dupla (code-review + dogfood QA) contra PRD + UI ref
3. Output: `gap-report.md` com gaps mapeados por módulo, severidade e linha
4. Decidir: deploy direto (se aprovado) ou execução de correções (se gaps críticos)
5. O gap report se torna o plano de ação: fases de correção com estimativas por lote
