---
name: backlog-and-sprint
description: >-
  Backlog management and Sprint execution for product iteration (Fase 5).
  Mantém uma backlog não-estruturada de pedidos de melhoria, e orquestra
  Sprints completas (PM → UX/UI → Engineering → Review → Close).
category: software-development
---

# Backlog & Sprint

> **Agente:** Hermes (orquestrador) + Pi best + Antigravity
> **Local da backlog:** `workstation/<projeto>/product/backlog.md`
> **Workstation (rw para Hermes e Pi):** `/opt/data/code/workstation/` = `/workspace/code/workstation/`

## Visão Geral

```
Usuário dá feedback
       │
       ▼
┌──────────────┐
│   Backlog    │ ← Hermes adiciona itens livremente (workstation 777)
│  não-triada  │
└──────┬───────┘
       │ usuário: "quero implementar as melhorias"
       ▼
┌──────────────┐\n│   SPRINT i   │\n├──────────────┤\n│ 0. Brief     │ ← Hermes entrevista usuário para clarificar\n│ 1. Planning  │ ← Pi best + PM skills → user stories\n│ 2. Design    │ ← Pi best + UX skills → agy revisa → feedbacks_sprint_i.md\n│ 3. Eng       │ ← Pi best + eng skills → code-tasks → execução\n│ 4. MCP       │ ← Hermes registra MCP server (se houver)\n│ 5. Review    │ ← Hermes reporta pro usuário\n│ 6. Close     │ ← usuário aprova\n└──────────────┘
       │
       ▼
  Próximo ciclo...
```

---

## 1. Backlog Não-Estruturada

### 1.1 Localização

```
workstation/<projeto>/product/backlog.md
```

Caminhos reais:
- **Hermes:** `/opt/data/code/workstation/<projeto>/product/backlog.md`
- **Pi:** `/workspace/code/workstation/<projeto>/product/backlog.md`

> Ambos leem e escrevem sem restrição (workstation é 777).

### 1.2 Formato

```markdown
# Backlog: <Nome do Projeto>

> Última atualização: YYYY-MM-DD HH:MM

## 📥 Não Triados

Itens que o usuário mencionou mas ainda não foram para uma Sprint.

### BACKLOG-001: <Título curto>
**Tipo:** [feature|melhoria|bug|refactor|docs|design]
**Fonte:** [feedback do usuário | auto-detectado | revisão agy]
**Quando:** YYYY-MM-DD
**Detalhes:**
<descrição do que o usuário pediu>

### BACKLOG-002: <Título curto>
...

---

## 📋 Sprint 1 (planejada: YYYY-MM-DD)

Itens selecionados para a Sprint 1.

### Sprint 1 — User Stories

- [ ] US-001: <título> (BACKLOG-001)
- [ ] US-002: <título> (BACKLOG-003)

### Sprint 1 — Status

**Status:** [planning | design | engineering | review | closed]
**Design feedbacks:** `feedbacks_sprint_1.md`
**Code-tasks:** `Sprint-1-code-tasks.md`

---

## 📋 Sprint 2

...
```

### 1.3 Adicionar Item (Hermes)

Quando o usuário dá feedback ou pede melhoria:

```bash
# Hermes cria/atualiza a backlog
# Como Hermes escreve no workstation, pode usar os tools de file diretamente

# Verificar se backlog existe
ls /opt/data/code/workstation/<projeto>/product/backlog.md

# Se não existir, criar:
mkdir -p /opt/data/code/workstation/<projeto>/product
cat >> /opt/data/code/workstation/<projeto>/product/backlog.md << 'EOF'
# Backlog: <Projeto>

## 📥 Não Triados

### BACKLOG-001: <Título>
**Tipo:** feature
**Fonte:** feedback do usuário
**Quando:** $(date +%Y-%m-%d)
**Detalhes:**
<descrição>
EOF
```

Para adicionar novo item a uma backlog existente:

```markdown
### BACKLOG-NNN: <Título>
**Tipo:** [feature|melhoria|bug|refactor|docs|design]
**Fonte:** feedback do usuário
**Quando:** YYYY-MM-DD
**Detalhes:**
<descrição>
```

### 1.4 Listar Backlog

```bash
# Ler backlog
cat /opt/data/code/workstation/<projeto>/product/backlog.md
```

---

## 2.0 No Time Limit: Running Agents Without Timeouts

Pi e agy rodam sem timeout artificial. Estratégia varia por tipo de tarefa.

### Hierarquia de Uso

```
CARO/ESCASSO     agy ─── Consultor externo especialista (design, UX, estratégia)
ESCASSO          Pi best ── Eng. sênior interno (MiniMax M3 via Go)
BARATO/ABUNDANTE Pi cost ─ Dev júnior (DeepSeek V4 Flash Free)
GRATUITO         Pi cost ── Free tier Zen
```

### Pi CLI — o binário é sempre `pi`

`opencode`, `opencode-go` e `deepseek` são **nomes de providers** no auth.json, não CLIs.

Nunca escreva: `opencode -m "..."` ou `opencode-go -p "..."`
Sempre escreva: `pi ... --provider <nome> --model <id>`

### Modelos disponíveis (este setup)

| Papel | Provider | Model ID | Custo |
|-------|----------|----------|-------|
| **Pi best** 🥇 | `opencode-go` | `minimax-m3` | Cota semanal $30 |
| **Pi best (fallback)** 🥈 | `opencode-go` | `deepseek-v4-pro` | Cota semanal $30 |
| **Pi best (último recurso)** 🥉 | `deepseek` | `deepseek-v4-pro` | $0.14/M input, $0.42/M output |
| **Pi cost** 🥇 | `opencode` (Zen) | `opencode/deepseek-v4-flash-free` | **Gratuito** |
| **Pi cost** 🥈 | `opencode-go` (Go) | `deepseek-v4-flash` | Cota semanal $30 |
| **Pi cost** 🥉 | `deepseek` (API direta) | `deepseek-v4-flash` | $0.14/M input |
| openrouter | `openrouter` | `openrouter/<model-id>` | Variável |

> ✅ OpenCode API key ativa (atualizada 2026-06-08). Todos os 4 providers funcionam:
> `opencode/deepseek-v4-flash-free` (gratuito, Zen), `opencode-go/*` (Go, cota $30/semana), `deepseek/*` (direto, pago).
> Prioridade: **cost → free primeiro**, best → MiniMax M3 via Go.

Testar conectividade (Pi é local — invocação direta, sem SSH):
```bash
# Testar 1° opção (free)
pi -p "echo test" --provider opencode --model opencode/deepseek-v4-flash-free
# Testar 2° opção (cota Go)
pi -p "echo test" --provider opencode-go --model deepseek-v4-flash
# Testar 3° opção (API direta)
pi -p "echo test" --provider deepseek --model deepseek-v4-flash
```

Para **Pi best** (planejamento, design, docs complexos) usar MiniMax M3 via OpenCode Go:
```bash
--provider opencode-go --model minimax-m3
```

Fallback se cota Go do minimax-m3 esgotar: DeepSeek V4 Pro também via Go:
```bash
--provider opencode-go --model deepseek-v4-pro
```

Último recurso: DeepSeek V4 Pro via API direta:
```bash
--provider deepseek --model deepseek-v4-pro
```

### Pi — Tarefas longas (Sprint Planning, Design, Engineering docs)

Provider: **Pi best** (`opencode-go/minimax-m3`). Tarefas longas exigem qualidade de raciocínio — Pi cost (Zen free) é lento e produz output raso para docs complexos.

```bash
PROJETO="<projeto>"
mkdir -p /opt/data/code/workstation/$PROJETO/prompts
cat > /opt/data/code/workstation/$PROJETO/prompts/pi-prompt.md << 'PROMPT'
Seu prompt longo aqui...
PROMPT

# Pi best — MiniMax M3 via Go (cota semanal $30)
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "$(cat /opt/data/code/workstation/$PROJETO/prompts/pi-prompt.md)" \
  --provider opencode-go --model minimax-m3 \
  --name "sprint-N-tarefa"

# Fallback se cota Go esgotar: DeepSeek V4 Pro (API direta, pago)
# PATH="/opt/data/pi-global/bin:$PATH" \
#   pi -p "$(cat ...)" --provider deepseek --model deepseek-v4-pro \
#   --name "sprint-N-tarefa"
```

⚠️ **NUNCA usar `timeout N` com Pi.** Pi pode estar gerando output corretamente mas lentamente. `timeout` mata o processo, exit code 0 engana, arquivo nunca é escrito. Sempre rodar sem timeout e verificar o arquivo de saída.

### Pi — Tarefas curtas (fixes, code tasks)

Provider priority (tarefas curtas — NUNCA para tarefas longas): free Zen → Go → DeepSeek API direta.

> ⚠️ **Não confundir com tarefas longas.** A seção "Pi — Tarefas longas" acima é quem dita o provider para tarefas de planejamento, design, docs e engenharia complexa — essas vão para **Pi best** (`opencode-go/minimax-m3`). A prioridade abaixo (Zen free → Go → API direta) é **exclusivamente para tarefas curtas (< 15 linhas de prompt)**.

```bash
# 1° Gratuito (tentar primeiro)
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "Task curta aqui" --provider opencode --model opencode/deepseek-v4-flash-free

# 2° Fallback se Zen rate-limited
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "Task curta aqui" --provider opencode-go --model deepseek-v4-flash

# 3° Último recurso
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "Task curta aqui" --provider deepseek --model deepseek-v4-flash
```

### Agy — Validação completa (Sprint Design Review, Engineering Review)

Usar **tmux session persistente** no host (já validado na F4e do pipeline). O agy pode rodar queries SQL, testar endpoints e editar arquivos sem pressa.

**⚠️ CRÍTICO: usar `-x 120 -y 40` no tmux.** Sem estas flags, o agy crasha silenciosamente (sessão some, output vazio). Elas definem tamanho mínimo de terminal — agy precisa de um terminal razoável para a TUI.

**⚠️ CRÍTICO: matar sessões agy velhas ANTES de criar novas.** Agy sessions podem vazar (já observado 24h+ rodando). Sempre limpar:

```bash
# 0. Matar sessões velhas E processos agy órfãos PRIMEIRO
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
ssh oracle-host "ps aux | grep 'bin/agy' | grep -v grep | awk '{print \$2}' | xargs -r kill 2>/dev/null"

# 1. Iniciar tmux com agy (sempre com -x -y flags!)
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
ssh oracle-host 'tmux new-session -d -s agy-sprint -x 120 -y 40 \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'

# 2. Aguardar TUI carregar
sleep 8

# 3. Enviar prompt linha a linha
ssh oracle-host 'tmux send-keys -t agy-sprint "Review Sprint N design..." Enter'
ssh oracle-host 'tmux send-keys -t agy-sprint "Check product/sprint_N/design/" Enter'

# 4. Monitorar a cada 60s
ssh oracle-host 'tmux capture-pane -t agy-sprint -p -S -30'

# 5. Matar ao concluir
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
```

### Agy — Revisão pontual (feedback rápido, design check)

```bash
# Foreground com timeout generoso
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  timeout 300 /home/ubuntu/.local/bin/agy -p "Quick review: ..."'
```

### Polling de conclusão (padrão para ambas as skills)

```bash
# Template de polling — verificar shared volume a cada 30s
for i in $(seq 1 20); do
  echo "--- Poll $i/20 ($(date +%H:%M:%S)) ---"

  # Verificar session files do Pi (se aplicável)
  ssh oracle-host '
    SESS=$(ls -dt ~pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--* 2>/dev/null | head -1)
    [ -n "$SESS" ] && echo "Turnos: $(wc -l < "$SESS"/*.jsonl 2>/dev/null || echo 0)" || echo "Sessão: aguardando"
  '

  # Verificar arquivos de saída
  if ls /opt/data/code/workstation/PROJETO/product/sprint_N/user-stories.md 2>/dev/null; then
    echo "✅ Arquivo de saída encontrado!"
    break
  fi

  # Verificar tmux agy (se aplicável)
  ssh oracle-host 'tmux capture-pane -t agy-sprint -p -S -5 2>/dev/null | tail -3' || echo "tmux: não encontrado"

  sleep 30
done
```

---

## ⛓️ Regra de Ouro — COMMIT SEMPRE

**🚨 Toda fase do ciclo DEVE terminar com `git add + git commit` na branch da Sprint. Push só no deploy do preview.**

Pi agents escrevem arquivos no disco, mas **não commitam**. Um `git checkout`, `git reset`, `git stash`, ou simplesmente trocar de branch **destrói todo o trabalho não commitado** irremediavelmente.

### O que fazer, em ordem, ao final de cada fase:

```bash
# 1. Verificar o que foi criado/modificado
git status --short

# 2. Adicionar tudo que pertence à Sprint
#    (excluir __pycache__, node_modules, .env, databases)
git add -A
git status --short  # confirmar staging

# 3. Commitar com mensagem descritiva
git commit -m "feat: <feature implementada nesta fase>"

# 4. Sem push automático — push só no deploy do preview
#    ⛔ NÃO git push após cada fase.
#    Commits são LOCAIS (protegem o trabalho contra checkout).
#    Push é só quando for implantar o preview (disparar CI/CD).
#    git push origin feat/sprint-N-v1  # ⛔ só no final
```

### Quando comitar (não negociável):

| Fase | O que commitar | Mensagem exemplo |
|------|---------------|------------------|
| Brief (2.2a) | `product/sprint_N/brief-notes.md` | `docs: add sprint N brief notes` |
| Planning (2.3) | `product/sprint_N/user-stories.md` + backlog.md | `docs: add sprint N user stories and backlog` |
| Design (2.4) | `product/sprint_N/design/*` | `feat: add sprint N design (wireframes, flows, prototype)` |
| Engineering Layer 1 | migrations + models | `feat: add migrations and models for feature X` |
| Engineering Layer 2 | services + API routes | `feat: implement feature X service and API` |
| Engineering Layer 3 | UI components | `feat: add feature X UI components` |
| Engineering Layer 4 | tests | `test: add feature X tests` |
| Review (2.6) | `product/sprint_N/engineering/feedbacks.md` | `docs: add sprint N engineering review` |
| PR Creation | tudo + PR | `feat: sprint N complete` |

### ⚠️ Antes de QUALQUER `git checkout` ou mudança de branch:

```bash
# SEMPRE verificar se há trabalho não commitado
git status --short
# Se mostrar arquivos modified/untracked:
# → OU commitar (se for da Sprint atual)
# → OU stash (se for investigativo/temporário)
# → NUNCA fazer checkout com working directory sujo
```

Esta regra substitui qualquer outra consideração de velocidade. **Um commit a mais é barato. Um dia de trabalho perdido é caro.** Comitar até mesmo fases intermediárias — ciclos Pi→agy que geram/refatoram arquivos existentes também produzem novas versões que merecem checkpoint.

### Fluxo de branch

```bash
# Branch da Sprint
git checkout -b feat/sprint-N-v1
git push -u origin feat/sprint-N-v1

# Entre fases: SEMPRE commit, push só no deploy do preview
# Ao final de todas as fases: PR está pronta
```

> ⚠️ **NUNCA force push.** Se precisar atualizar a branch remota depois de commits intermediários, use `git merge` normal. Force push destrói commits de fix que podem ter sido feitos por outros processos (Pi, agy).

---

## 2. Sprint Cycle

### 2.1 Gatilho

O usuário diz algo como:
- "Quero implementar as melhorias pendentes"
- "Bora fazer uma Sprint"
- "O que temos na backlog?"

### 2.2 Preparação

Antes de começar a Sprint, criar estrutura:

```bash
ssh oracle-host 'pi-shell "mkdir -p /workspace/code/workstation/PROJETO/product/sprint_N"'
```

### 2.2a Sprint Brief — User Interview for Clarification (Hermes)

**Antes de delegar para Pi best.** Hermes conduz uma breve entrevista com o usuário para clarificar os itens da backlog que entrarão na Sprint. O Pi só recebe especificações precisas — ambiguidade vira especulação e retrabalho.

#### Quando fazer

Sempre que a Sprint tiver **pelo menos um item** que:
- Não tem critérios de aceitação escritos
- Envolve fluxos de usuário com múltiplos caminhos (ex: OAuth redirect, sync bidirecional, MCP tools)
- Exige decisão de design que não está documentada (ex: "inbox com status ou filtro virtual?")
- O usuário mencionou verbalmente mas não detalhou por escrito

#### Formato da entrevista

```markdown
## Sprint N — Brief de Esclarecimento

**Itens a clarificar:**

1. **[BACKLOG-NNN]** <Título>
   - O que exatamente acontece quando <condição de borda>?
   - Como devem se comportar <situação ambígua A> vs <situação B>?
   - <Decisão específica pendente>?

2. **[BACKLOG-MMM]** <Título>
   - ...
```

Hermes pergunta, usuário responde. **Mínimo de perguntas possível** — não é uma F1 de ideação, é só clarificar pontos cegos. 2-5 perguntas por Sprint normalmente bastam.

#### Antes de invocar Pi best

Hermes compila um **contexto enriquecido** combinando:

```
product/backlog.md (itens da Sprint)
+ respostas do usuário (brief)
+ PRD e user-stories existentes (contexto do produto)
+ roadmaps e docs de engenharia (contexto técnico)
```

Esse contexto enriquecido (não a backlog crua) é o que vai no prompt do Pi best.

#### Pós-entrevista

Atualizar a backlog com as respostas do usuário como notas nos itens clarificados:

```markdown
### BACKLOG-NNN: <Título>
**Clarificação:** <resumo da decisão do usuário>
```

E registrar no diário da Sprint (se houver) ou em `product/sprint_N/brief-notes.md`.

> 🔐 **Permissões — arquivos criados por Hermes:** O Hermes (uid 10000) cria arquivos que o Pi (uid 1001 dentro do container) não consegue ler. Após criar QUALQUER arquivo no shared volume via Hermes, corrigir permissões para 644 imediatamente:
> ```bash
> ssh oracle-host 'find /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/ -type f -exec sudo chmod 644 {} \; 2>/dev/null'
> ```
> Isso vale para: brief-notes.md, prompts, backlog.md, e qualquer arquivo que Pi precise ler.

> ⚠️ **Símbolos NLP decididos no brief não chegam ao Pi se brief-notes.md estiver com permissão errada.** Pi não consegue ler brief-notes.md se Hermes o criou (uid mismatch). Consequência: Pi gera designs com símbolos antigos (ex: `!p` em vez de `!ok`). **Após o brief, SEMPRE:**
> 1. Corrigir permissões do brief-notes.md (`chmod 644`)
> 2. Passar as decisões de símbolos NLP explicitamente no prompt do Pi, não confiando que ele vai ler o arquivo
> 3. Após o Pi gerar os designs, verificar se os símbolos NLP estão corretos — se não, fazer patch nos 3 arquivos de design (wireframes.md, user-flows.md, prototype.html)

> 📘 **Template do brief-notes.md:** `skill_view(name='backlog-and-sprint', file_path='references/sprint-brief-template.md')` — estrutura pronta para registrar perguntas, respostas e decisões do brief.

### 2.3 Sprint Planning (Pi best + PM skills) — background

Hermes invoca Pi com modelo **best**. Como o Pi leva minutos para gerar user stories com Gherkin, usar **background + session monitoring** (ver `## 2.0 No Time Limit`):

```bash
# 1. Escrever o contexto enriquecido num arquivo no shared volume
PROJETO="<projeto>"
mkdir -p /opt/data/code/workstation/$PROJETO/prompts
cat > /opt/data/code/workstation/$PROJETO/prompts/pi-sprint-planning.md << 'PROMPT'
Projeto: <projeto>
Diretório: /workspace/code/workstation/<projeto>

Você é um Product Manager. Carregue suas skills de PM (/skill:roadmap-planning,
/skill:user-story, /skill:prioritization-advisor).

CONTEXTO ENRIQUECIDO (backlog + respostas do brief + docs existentes):

=== BACKLOG DA SPRINT ===
<conteúdo da backlog para a Sprint N>

=== BRIEF DE ESCLARECIMENTO ===
<respostas do usuário do passo 2.2a>

=== CONTEXTO DO PRODUTO ===
<PRD.md resumido, user-stories.md existentes>

Leia todo o contexto acima.
Selecione itens prioritários para esta Sprint.
Crie user stories no formato Mike Cohn com critérios Gherkin.
Escreva as stories em product/sprint_N/user-stories.md.

Considere: dependências, esforço estimado, valor para o usuário.

Quando terminar, inclua <!-- PHASE_COMPLETE: planning --> ao final do arquivo.
PROMPT

# 2. Copiar pro host e disparar em background
scp -o StrictHostKeyChecking=no \
  /opt/data/code/workstation/$PROJETO/prompts/pi-sprint-planning.md \
  oracle-host:/home/ubuntu/selfhost/shared/code/workstation/$PROJETO/prompts/pi-sprint-planning.md

ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
LC_DIR=code/workstation/PROJETO \
  nohup pi-agent 'pi --name "sprint-N-planning" \
  -p "$(cat prompts/pi-sprint-planning.md)" \
  --provider opencode-go --model minimax-m3' \
  > /tmp/pi-sprint-N-planning.log 2>&1 &
echo "Pi PID: $!"
ENDSCRIPT

# 3. Polling até o arquivo de saída aparecer
echo "⏳ Pi gerando user stories (background)..."
for i in $(seq 1 40); do
  sleep 30

  # Mostrar progresso via session files
  ssh oracle-host '
    SESS=$(ls -dt ~pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--* 2>/dev/null | head -1)
    if [ -n "$SESS" ]; then
      TURNOS=$(wc -l < "$SESS"/*.jsonl 2>/dev/null || echo 0)
      echo "  Turnos gerados: $TURNOS"
    fi
  ' 2>/dev/null

  # Verificar se terminou
  if grep -q "PHASE_COMPLETE" /opt/data/code/workstation/$PROJETO/product/sprint_N/user-stories.md 2>/dev/null; then
    echo "✅ Sprint Planning completo!"
    break
  fi
  echo "  Aguardando... ($((i * 30))s)"
done
```

**Saída esperada:**
```
Você é um Product Manager. Carregue suas skills de PM (/skill:roadmap-planning,
/skill:user-story, /skill:prioritization-advisor).

Leia a backlog em product/backlog.md.
Selecione itens prioritários para esta Sprint.
Crie user stories no formato Mike Cohn com critérios Gherkin.
Escreva as stories em product/sprint_N/user-stories.md.

Considere: dependências, esforço estimado, valor para o usuário."

ssh oracle-host "LC_DIR=code/workstation/PROJETO pi-agent \
  'pi -p \"$CONTEXT\" --provider opencode-go --model minimax-m3'"
```

**Saída esperada:**
```
product/sprint_N/user-stories.md
```

E a backlog é atualizada: itens selecionados movidos para a seção da Sprint.

### 2.4 Sprint Design (Pi best + UX skills + agy) — background + tmux

**Pi (background, sem timeout):**

> 📊 **Após lançar Pi, carregar `pi-session-audit`** (`skill_view(name='pi-session-audit')`) para monitorar progresso real da sessão — entries, custo, último toolCall. Não confiar em `notify_on_complete` apenas — Pi sai com exit 0 mesmo stallado. O script de auditoria mostra se Pi está lendo, escrevendo ou travado.

```bash
cat > /opt/data/code/workstation/PROJETO/prompts/pi-sprint-design.md << 'PROMPT'
Projeto: <projeto>
Diretório: /workspace/code/workstation/<projeto>

Você é um UX/UI Designer. Carregue suas skills de design.
Leia as user stories em product/sprint_N/user-stories.md.
Crie wireframes, user flows, e protótipo para as novas funcionalidades.

Guarde tudo em product/sprint_N/design/.
Inclua: wireframes.md, user-flows.md, prototype.html

Quando terminar, inclua <!-- PHASE_COMPLETE: design --> ao final de product/sprint_N/design/wireframes.md
PROMPT

scp -o StrictHostKeyChecking=no \
  /opt/data/code/workstation/PROJETO/prompts/pi-sprint-design.md \
  oracle-host:/home/ubuntu/selfhost/shared/code/workstation/PROJETO/prompts/pi-sprint-design.md

ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
LC_DIR=code/workstation/PROJETO \
  nohup pi-agent 'pi --name "sprint-N-design" \
  -p "$(cat prompts/pi-sprint-design.md)" \
  --provider opencode-go --model minimax-m3' \
  > /tmp/pi-sprint-N-design.log 2>&1 &
ENDSCRIPT

for i in $(seq 1 40); do
  sleep 30
  ssh oracle-host '
    SESS=$(ls -dt ~pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--* 2>/dev/null | head -1)
    [ -n "$SESS" ] && echo "  Turnos: $(wc -l < "$SESS"/*.jsonl 2>/dev/null || echo 0)"
  ' 2>/dev/null

  if grep -q "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/sprint_N/design/wireframes.md 2>/dev/null; then
    echo "✅ Pi Design completo!"
    break
  fi
  echo "  ($((i * 30))s)"
done
```

**⚠️ Verificação de saída do Pi:**
O monitoramento via session files (`~pi/.pi/agent/sessions/*.jsonl`) é **efêmero** — os logs ficam dentro do container Pi e somem quando ele morre. **Sempre verificar os arquivos de output no shared volume** como fonte da verdade:
```bash
# ✅ CONFIÁVEL: arquivos de output persistem no shared volume
ls -la /opt/data/code/workstation/PROJETO/product/sprint_N/design/wireframes.md 2>/dev/null
grep "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/sprint_N/design/wireframes.md 2>/dev/null

# ❌ EFÊMERO: session logs somem quando o container morre
ssh oracle-host 'wc -l ~pi/.pi/agent/sessions/*.jsonl'  # pode falhar
```

Pi pode parecer travado (idle longo, CPU ~0%) mas já ter completado todo o output. Verificar os 3 arquivos esperados antes de concluir que falhou.

> 📘 **Design system version check:** `skill_view(name='backlog-and-sprint', file_path='references/design-system-version-check.md')` — como verificar se o Pi usou V1 ou V2 no prototype, com tabela comparativa de variáveis CSS.
> 📘 **Agy re-approval cycle (real example):** `skill_view(name='backlog-and-sprint', file_path='references/agy-reapproval-sprint1.md')` — exemplo real de Pi best corrigindo 3 ressalvas, agy implementando feature faltante no prototype, e aprovação final SEM RESSALVAS. Inclui custo, duração, lições sobre permissões e diff-check.

**⚠️ NÃO PULAR ESTA ETAPA.** O agy review é parte obrigatória da fase de Design. Sem ele, a Sprint avança com designs não validados visualmente. O marcador `ACORDO: AVANÇAR PARA ENGENHARIA` no feedback é o gate entre Design e Engineering.

**Antigravity (tmux — sem timeout):**

> ⚡ **Agy não só revisa — ele implementa.** Agy (Gemini 3.5 Flash) tem capacidade de escrever código. Durante a revisão de design, se agy encontrar uma feature especificada nos docs mas ausente no prototype (ex: botão "Desfazer" do backtracking documentado mas não implementado), ele pode implementá-la diretamente. Esse padrão "review + fix" reduz ciclos Pi→agy→Pi. O prompt de review deve incluir "*If something is missing that the spec requires, implement it*" para ativar esse comportamento. Agy também pode commit as alterações no git (autorizar com option 3: "always allow"). Atenção: agy pode pedir permissão para cada comando — ao aprovar com option 3 (always allow in settings.json), as próximas permissões para comandos similares são automáticas.

```bash
# 1. Matar sessão anterior (se houver)
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'

# 2. Iniciar tmux com agy
ssh oracle-host 'tmux new-session -d -s agy-sprint -x 120 -y 40 \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'

# 3. Aguardar TUI carregar
sleep 8

# 4. Enviar prompt de revisão em múltiplos send-keys
#    (o prompt completo em 1 send só é truncado; rate-limited a ~3 send-keys)
#    O prompt usa o path REAL do host, não o do container:
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "Review Sprint N design at /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/design/. Write feedback in /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/feedbacks_sprint_N.md" Enter'
sleep 2
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "Check visual consistency (colors, fonts, spacing, design system), verify all user stories are covered, spot missing flows or usability issues." Enter'
sleep 2
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "When satisfied, end the file with: ACORDO: AVANCAR PARA ENGENHARIA" Enter'

> ⚠️ **agy output token limit:** Ao revisar/reconstruir arquivos grandes (>50KB), agy (Gemini Flash 3.5) pode estourar o limite de tokens de saída. Ele se recupera compactando, mas partes podem ser truncadas. Se o resultado parecer incompleto, pedir versão compacta ou quebrar em partes.

**Pi responde e itera** até agy aprovar (ciclo: Pi background → agy tmux). Registrado em `feedbacks_sprint_N.md`.



**Marcador de aprovação:**
  ssh oracle-host 'tmux capture-pane -t agy-sprint -p -S -10' 2>/dev/null
  if ssh oracle-host "grep -q 'ACORDO\\|APROVADO' \
    /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/feedbacks_sprint_N.md" 2>/dev/null; then
    echo "✅ agy aprovou!"
    break
  fi
done

# 6. Limpar
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
```

> 📘 **Preview deployment pattern:** `skill_view(name='backlog-and-sprint', file_path='references/preview-deployment-pattern.md')` — template de docker-compose override, GitHub Actions workflow, e scripts NPM para PR preview com subdomínio dinâmico.
> 📘 **Test-fix loop pattern:** `skill_view(name='backlog-and-sprint', file_path='references/test-fix-loop-pattern.md')` — padrão de QA multi-camada (Pi cost → Pi best → agy → verify) usado em Sprint 1 TaskFlow.\n> 📘 **Parallel execution pattern:** `skill_view(name='backlog-and-sprint', file_path='references/parallel-execution-pattern.md')` — quando e como executar features independentes em paralelo com múltiplos Pi processes.
> 📘 **UID mismatch workaround (legacy dirs):** `skill_view(name='backlog-and-sprint', file_path='references/uid-mismatch-workaround.md')` — workarounds quando Pi não consegue escrever em diretórios owned por uid 1001.
> 📘 **Agy re-approval cycle (real example):** `skill_view(name='backlog-and-sprint', file_path='references/agy-reapproval-sprint1.md')` — exemplo real de Pi best corrigindo 3 ressalvas, agy implementando feature faltante no prototype, e aprovação final SEM RESSALVAS.
> 📘 **Agy engineering review (re-review pattern):** `skill_view(name='backlog-and-sprint', file_path='references/agy-engineering-review.md')` — fluxo de re-review agy → Pi best → agy → aprovação. Inclui prompts, permission handling, checklist e marcadores.
> 📘 **Agy design review prompt:** `skill_view(name='backlog-and-sprint', file_path='references/agy-design-review-prompt.md')` — contém o prompt exato de 3 send-keys com critérios de revisão visual, cobertura de stories e usabilidade.
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "When satisfied, end the file with: ACORDO: AVANCAR PARA ENGENHARIA" Enter'

> ⚠️ **agy output token limit:** Ao revisar/reconstruir arquivos grandes (>50KB), agy (Gemini Flash 3.5) pode estourar o limite de tokens de saída. Ele se recupera compactando, mas partes podem ser truncadas. Se o resultado parecer incompleto, pedir versão compacta ou quebrar em partes.

**Pi responde e itera** até agy aprovar (ciclo: Pi background → agy tmux). Registrado em `feedbacks_sprint_N.md`.

**Marcador de aprovação:**

> ⚠️ **agy pode confundir paths similares.** O prompt do agy deve usar o path absoluto MAIS longo e específico possível. Se existirem cópias antigas dos mesmos arquivos em diretórios diferentes (ex: `product/design/` da v1 vs `product/sprint_N/design/` da Sprint), o agy pode ler a versão errada. Para corrigir: enviar `STOP. Use o path /full/absolute/path/` via tmux send-keys. A correção só é processada após a fila de prompts anteriores drenar — não há como interromper o agy no meio de uma geração.

> ⚠️ **Mudanças de símbolos/convenções decididas no Brief (2.2a) precisam de verificação explícita no output do Pi.** Se o brief alterar um símbolo (ex: `!p` → `!ok`), o Pi pode não ter recebido essa informação (UID mismatch no brief-notes.md). Hermes DEVE verificar o output do Pi nos 3 arquivos de design (wireframes.md, user-flows.md, prototype.html) após a geração, e fazer patch via SSH se necessário. Não confiar que o Pi leu o brief corretamente.

> ⚠️ **A fase de design pode ter múltiplas rodadas de agy para propósitos diferentes.** Numa Sprint real, o agy pode ser invocado mais de uma vez na mesma fase com objetivos distintos (ex: primeiro revisar os designs do Pi, depois refazer o prototype para um design system específico, depois adicionar uma nova feature educacional). Cada rodada é uma sessão tmux independente com seu próprio prompt. O ciclo não é "Pi → agy → aprova" — pode ser "Pi → agy → Pi ajusta → agy redesign → Pi ajusta → aprova".

> ⚠️ **agy pode confundir paths similares.** O prompt do agy deve usar o path absoluto MAIS longo e específico possível. Se existirem cópias antigas dos mesmos arquivos em diretórios diferentes (ex: `product/design/` da v1 vs `product/sprint_N/design/` da Sprint), o agy pode ler a versão errada. Para corrigir: enviar `STOP. Use o path /full/absolute/path/` via tmux send-keys. A correção só é processada após a fila de prompts anteriores drenar — não há como interromper o agy no meio de uma geração.

> ⚠️ **Mudanças de símbolos/convenções decididas no Brief (2.2a) precisam de verificação explícita no output do Pi.** Se o brief alterar um símbolo (ex: `!p` → `!ok`), o Pi pode não ter recebido essa informação (UID mismatch no brief-notes.md). Hermes DEVE verificar o output do Pi nos 3 arquivos de design (wireframes.md, user-flows.md, prototype.html) após a geração, e fazer patch via SSH se necessário. Não confiar que o Pi leu o brief corretamente.
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "When satisfied, end the file with: ACORDO: AVANCAR PARA ENGENHARIA" Enter'

> ⚠️ **agy output token limit:** Ao revisar/reconstruir arquivos grandes (>50KB), agy (Gemini Flash 3.5) pode estourar o limite de tokens de saída. Ele se recupera compactando, mas partes podem ser truncadas. Se o resultado parecer incompleto, pedir versão compacta ou quebrar em partes.

**Pi responde e itera** até agy aprovar (ciclo: Pi background → agy tmux). Registrado em `feedbacks_sprint_N.md`.

**Marcador de aprovação:**
```markdown
## ACORDO: AVANÇAR PARA ENGENHARIA
```

### Agy Re-Review (após correções do Pi)

Quando agy aprova com ressalvas e Pi corrige, rodar uma segunda rodada de revisão para confirmar sem caveats:

```bash
# 1. Matar sessão anterior e criar nova
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
ssh oracle-host 'tmux new-session -d -s agy-sprint -x 120 -y 40 \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'
sleep 8

# 2. Prompt de re-revisão — foco nas correções
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "Re-review Sprint N design at /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/design/. Read the feedback in /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/feedbacks_sprint_N.md and verify all corrections were applied correctly." Enter'
sleep 2
ssh oracle-host 'tmux send-keys -t agy-sprint \
  "Verify: (1) [correção 1], (2) [correção 2], (3) [correção 3]. If all satisfactory, confirm with: DESIGN REVIEW FINAL: APROVADO SEM RESSALVAS" Enter'

# 3. Aprovar permissões — agy pede confirmação para cada comando
#    Usar option "3" (always allow) para git e grep para evitar prompts repetitivos
#    Ex: tmux send-keys -t agy-sprint "3" Enter

# 4. Monitorar conclusão
for i in $(seq 1 20); do
  sleep 30
  if grep -q "APROVADO SEM RESSALVAS" /opt/data/code/workstation/PROJETO/product/sprint_N/feedbacks_sprint_N.md 2>/dev/null; then
    echo "✅ Agy aprovou sem ressalvas!"
    break
  fi
  # Verificar se agy está esperando permissão
  ssh oracle-host 'tmux capture-pane -t agy-sprint -p -S -3 2>/dev/null | tail -1 | grep -q "Do you want to proceed" && echo "⚡ Permission prompt detected, approving..." && tmux send-keys -t agy-sprint "2" Enter'
done

# 5. Limpar
ssh oracle-host 'tmux kill-session -t agy-sprint 2>/dev/null; true'
```

> ⚠️ **Re-review pode gerar novas correções.** Agy na segunda rodada pode encontrar inconsistências adicionais ou, se o prompt pedir, implementar features faltantes diretamente no prototype (ver padrão "review + fix" acima). Sempre verificar o git diff após agy concluir para capturar alterações que ele fez no código.

### 2.5 Sprint Engineering (Pi best + Pi cost + parallelism)

**🚀 Regra de execução autônoma:** Uma vez que o usuário deu sinal verde ("pode mandar ver"), NÃO pedir confirmação entre batches. Executar autonomamente todos os lotes até concluir. Apenas enviar mensagens de atualização do progresso. Micro-confirmações ("posso prosseguir?", "quer que continue?") interrompem o fluxo e frustram o usuário.

> ⚡ **Integração Hermes-MCP no final da Sprint:** Ver `## 2.5a Sprint MCP Integration`.

**Fases da engenharia:**

1. **Pi best** — Gera Sprint-1-code-tasks.md (ver 2.5i)
2. **Usuário revisa** code-tasks e aprova
3. **Pi cost** — Executa as code-tasks em lotes por layer (paralelo)
4. **Auditoria** — Extrai tokens/custo/duração da sessão `.jsonl`
5. **Agy review** — Revisão final

#### Code Tasks Format

> 📘 **Full task format specification:** `skill_view(name='backlog-and-sprint', file_path='references/code-tasks-format.md')` — task structure, field definitions, granularity rules, template, and pitfalls.

Code-tasks are bite-sized engineering tasks (2-15 min each) generated by Pi best from user stories, SAD, ERD, API contracts, and tech-specs. Each task has a type (`schema`, `model`, `api`, `service`, `test`, `config`, `docs`, `refactor`), explicit dependencies on other tasks, an effort estimate, actionable instructions, an acceptance criteria checklist, and affected file paths. Tasks are organized in dependency order and executed in parallel batches by feature layer. The full format, including the `code-tasks.md` template, granularity rules, and execution pitfalls, is documented in the reference file above.

### 2.5i Engineering Phase 1 — Code-Tasks Generation

Antes de executar qualquer código, **Pi best gera as code-tasks específicas da Sprint**:

1. Pi best recebe: user stories, SAD, ERD, API contracts, tech-specs, design feedback
2. Gera tasks de 2-15 min agrupadas por feature, com dependências explicitadas
3. Salva em `product/sprint_N/engineering/Sprint-N-code-tasks.md`
4. Adiciona `<!-- PHASE_COMPLETE: code-tasks -->`

**Após geração — parada obrigatória:** o arquivo de code-tasks é enviado ao usuário para revisão antes de qualquer execução. Isso garante que o escopo está correto antes de queimar tokens com Pi cost.

**Commit:** `git add product/sprint_N/engineering/Sprint-N-code-tasks.md && git commit -m "docs: add Sprint N code-tasks"`

### 2.5j Pre-Flight — Check Existing Pi Processes

**Antes de executar engineering, SEMPRE verificar se já existe um Pi rodando:**

```bash
ps aux | grep " pi " | grep -v grep
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl | head -3
```

Se um Pi estiver progredindo (entries crescendo, custo acumulando), **não iniciar outro do zero**. Deixar o atual terminar ou retomar com `--session`. Ver `pi-agent-coordination` skill para detalhes do pre-launch check.

#### 2.5a Execução paralela das code-tasks

As features dentro de uma Sprint são **independentes entre si** (cada uma toca schema/model/service/api/ui/test diferentes). Isso permite executar em paralelo:

**Grafo de dependências típico:**

```
F1 (GCal Sync)  F2 (Focus Mode)  F3 (Past-Date)  F4 (Bulk)  F5 (MCP)
Schema           UI-only          UI-only          Service+API Schema
Model                                                  UI      Model
Service+API                                            Tests   Service+API
UI+Tests                                                        UI+Tests
```

Cada coluna é **independente** das outras. Rodam em paralelo via `terminal(background=true, notify_on_complete=true)` — um Pi process por feature chain. Não usar `delegate_task` (overhead de ~30s por subagente).

**Execução em lotes por camada (sequential intra-feature):**

```bash
# Para cada feature F1..F5:
#   Layer 1: Schema (migrations) — sequential
#   Layer 2: Model (ORM) — sequential
#   Layer 3: Service + API — sequential
#   Layer 4: UI — sequential
#   Layer 5: Tests — sequential
#
# Layer N de diferentes features: PARALELO
# Ex: Layer 2 de F1 + Layer 2 de F5 rodam simultaneamente
```

**Execução (Pi cost):** tasks em background (nunca timeout). Provider priority: free Zen → Go → API direta:

```bash
PATH="/opt/data/pi-global/bin:$PATH" \\
  pi -p "$(cat prompts/pi-layer3a-f1-gcal.md)" \\
  --provider opencode --model opencode/deepseek-v4-flash-free \\
  --name "sprint1-layer3a"
```

#### 2.5b Pós-execução: Auditoria de sessão

Após cada Pi executar, extrair métricas do `.jsonl` da sessão para relatório de custo:

```bash
python3 -c "
import json
p = '/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/***.jsonl'  # última
u={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'totalTokens':0}
c={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'total':0}
for l in open(p):
    e=json.loads(l.strip())
    if e.get('type')=='message' and e.get('message',{}).get('role')=='assistant':
        w=e['message'].get('usage',{})
        if w:
            for k in u: u[k]+=w.get(k,0)
            for k in c: c[k]+=w.get('cost',{}).get(k,0)
print(f'Duração: {round(dur/60,1)} min')
print(f'Tokens: {u}')
print(f'Custo: \${c[\"total\"]:.4f}')
"
```

Carregar `skill_view(name='pi-session-audit')` para script completo de auditoria.

#### 2.5d Deploy via SSH (UID mismatch workaround)

Pi (uid 10000) não escreve em diretórios owned por uid 1001. Quando Pi escreve em staging/:

```bash
ssh -o StrictHostKeyChecking=no oracle-host "
  find /home/ubuntu/selfhost/shared/code/workstation/PROJETO/_sprint*_staging -type f 2>/dev/null | while read f; do
    rel=\${f#*/_sprint*_staging/}
    cp \"\$f\" \"/home/ubuntu/selfhost/shared/code/workstation/PROJETO/\$rel\"
  done
"
```

Para tests/unit/ (757 world-writable), Pi escreve direto. Para tests/integration/ (755), copiar via SSH.

#### 2.5e Multi-layer QA cycle (Pi cost → Pi best → agy → verify)

Após a execução das code-tasks (Pi cost), um ciclo de QA de 3-5 camadas:

```
Layer 1 — Pi cost: executa code tasks (47 tasks, ~20min)
Layer 2 — Agy review: diagnóstico inicial (via tmux, ~5min)
Layer 3 — Pi best: corrige bugs (sessão dedicada, MiniMax M3, $~0.60)
Layer 4 — Agy final: corrige bugs restantes, valida suite
Layer 5 — Hermes verify: roda suite no container, confirma
```

**Marcador de aprovação final:** `## ACORDO: SPRINT N CONCLUIDA` no feedbacks.md

#### 2.5f Stall detection e verificação

⚠️ **Pi pode sair com exit code 0 sem gerar output.** `notify_on_complete` engana. Verificação obrigatória:

```bash
ls -la product/sprint_N/engineering/Sprint-N-code-tasks.md 2>/dev/null && \
  grep "PHASE_COMPLETE" product/sprint_N/engineering/Sprint-N-code-tasks.md || \
  echo "❌ ARQUIVO NÃO GERADO — Pi stallou silenciosamente"
```

**Antigravity revisa engenharia (tmux — sem timeout):**

```bash
ssh oracle-host 'tmux kill-session -t agy-eng 2>/dev/null; true'
ssh oracle-host 'tmux new-session -d -s agy-eng -x 120 -y 40 \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'
sleep 8
ssh oracle-host 'tmux send-keys -t agy-eng \
  "Review Sprint N engineering at product/sprint_N/engineering/." Enter'
ssh oracle-host 'tmux send-keys -t agy-eng \
  "Write feedback in product/sprint_N/engineering/feedbacks.md" Enter'

for i in $(seq 1 20); do
  sleep 60
  ssh oracle-host 'tmux capture-pane -t agy-eng -p -S -10' 2>/dev/null
  if ssh oracle-host "grep -q 'APROVADO\|ACORDO' \
    /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/engineering/feedbacks.md" 2>/dev/null; then
    echo "Agy aprovou engenharia!"; break
  fi
done
ssh oracle-host 'tmux kill-session -t agy-eng 2>/dev/null; true'
```

**Ciclo de feedback Pi ↔ agy** via `product/sprint_N/engineering/feedbacks.md` até aprovação.

### 2.5b Sprint Preview Deployment (PR Preview via NPM)

Se o projeto tem CI/CD (GitHub Actions + GHCR + Nginx Proxy Manager), pode-se gerar um **preview environment isolado por PR** — subdomínio dinâmico apontando para containers com banco próprio.

**Arquivos padrão:**

| Arquivo | Função |
|---------|--------|
| `docker-compose.preview.yml` | Override: isola container_name, DB, portas |
| `scripts/register-preview.sh` | Registra proxy host no NPM (SQLite) |
| `scripts/unregister-preview.sh` | Remove proxy host do NPM |
| `scripts/register-proxy-host.py` | INSERT no SQLite do NPM |
| `.github/workflows/preview.yml` | CI: build/deploy em PR open, cleanup em PR close |

**Fluxo:**

```
PR #N aberta → CI builda :pr-N images → push GHCR
  → pull no servidor → docker compose -f override up -d
  → CREATE DATABASE taskflow_pr_N → alembic upgrade head
  → INSERT proxy_host no SQLite do NPM
  → subdomínio {N}.dominio.com → taskflow-backend-N:8000

PR mergeada → CI cleanup:
  → unregister-preview.sh (soft delete no SQLite)
  → docker stop/rm containers
  → DROP DATABASE → docker rmi :pr-N images
```

**Docker Compose override key rules:**

- `container_name` único por PR evita conflito com o original
- `ports: ["0:8000"]` (porta aleatória) ou omitir — NPM acessa pela rede interna
- `DATABASE_URL` com database isolado (`taskflow_pr_N`)
- Conectar à `proxy_network` para NPM alcançar o container
- `db-init` profile manual para criar database

**NPM SQLite — proxy host schema:**

```bash
# Copiar DB, modificar, copiar de volta
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite
python3 /path/to/register-proxy-host.py --db /tmp/npm.sqlite --domain ...
docker cp /tmp/npm.sqlite nginx_proxy_manager:/data/database.sqlite
```

Colunas obrigatórias em `proxy_host` (NOT NULL com default):
| Coluna | Default | Notas |
|--------|---------|-------|
| `access_list_id` | 0 | usar 0 |
| `certificate_id` | 0 | 0 = sem SSL, usar se tiver wildcard cert |
| `ssl_forced` | 0 | 1 se tiver cert HTTPS |
| `forward_scheme` | `'http'` | ou `'https'` |
| `meta` | `'{}'` | JSON object |
| `locations` | `'[]'` | JSON array |
| `advanced_config` | `''` | string vazia |

**DNS para subdomínios wildcard:**
- **sslip.io/nip.io:** `{N}.{ip}.sslip.io` funciona sem config — mas verificar resolução (alguns IPs com 4 octetos falham)
- **Domínio próprio (gotdns.ch, Cloudflare):** Adicionar registro `*` → IP do servidor
- **Cloudflare:** wildcard DNS incluso no free plan

**⚠️ GHCR pull no deploy preview:** O `secrets.GITHUB_TOKEN` gerado no CI **não tem permissão de pull** de fora do Actions runner. O deploy via `appleboy/ssh-action` precisa de um **PAT clássico** com escopo `read:packages`, salvo como segredo do repositório. Ver `skill_view(name='oracle-host-access', file_path='references/ghcr-auth.md')`.

> 📘 **Referência completa:** `skill_view(name='backlog-and-sprint', file_path='references/preview-deployment-pattern.md')` — template completo de docker-compose.preview.yml, GitHub Actions workflow, e scripts NPM.

### 2.5a Sprint MCP Integration (Hermes)

Se a Sprint produz ou atualiza um servidor MCP (ex: MCP Server do TaskFlow), registrar no Hermes ao final da engenharia para que o agente ganhe tools nativas (`mcp_taskflow_*`):

```bash
# 1. Descobrir comando/url do server MCP
#    - Se for stdio: path para o script Python
#    - Se for HTTP: URL (ex: http://localhost:8020/mcp)

# 2. Registrar no Hermes
hermes mcp add taskflow --command "uv run mcp-taskflow-server"
# ou
hermes mcp add taskflow --url "http://localhost:8020/mcp"

# 3. Testar conexão
hermes mcp test taskflow

# 4. Ver tools disponíveis
hermes mcp list
# → taskflow: ✓ enabled (12 tools)
```

**Onde vive a config:** `mcp_servers:` no `config.yaml`. Cada server adicionado vira tools com prefixo `mcp_<server>_<tool>` (ex: `mcp_taskflow_create_task`, `mcp_taskflow_quick_add`). O Hermes carrega MCP tools automaticamente em todas as sessões após registro.

**Checklist de verificação:**
- [ ] `hermes mcp add` executou sem erro
- [ ] `hermes mcp test` retorna sucesso
- [ ] Tools aparecem em `hermes mcp list`
- [ ] Pelo menos 1 tool funcional: `mcp_taskflow_create_task` ou similar

### 2.6 Sprint Review (Hermes → Usuário)

Hermes reporta para o usuário no formato que ele prefere: **compacto, orientado a dados, com tabelas de métricas**. Zero floreios.

Formato preferido:
```markdown
## 📋 Sprint N — Relatório

**Resultado:** ✅ Concluída | `199 passed, 1 xpassed, 1 warning` — 100% GREEN

### O que foi feito
| Feature | Status | Tests | Notas |
|---------|--------|-------|-------|
| F1 — GCal Sync | ✅ | 21 pass | push/retry com limite de falhas |
| F2 — MCP Server | ✅ | 14+10 pass | issue/validate/consume lifecycle |
| ... | ✅ | ... | ... |

### Custo da Sprint
| Recurso | Custo |
|---------|-------|
| Pi cost (Zen gratis) | $0.00 |
| Pi best (MiniMax M3) | $0.62 |
| **Total** | **$0.62** |

### Para testar
- <instruções sucintas>

### Próximos passos
- <backlog pendente>
```

**Regras:**
- Arquivos .MD entregues como MEDIA (anexo), nunca como texto inline
- Tabelas com números reais, sem placeholder
- Custo total em destaque
- Lista de bugs corrigidos ao final

### 2.7 Sprint Close — PR Creation

Após a Sprint ser aprovada (agi review concluído, suite verde), o agente DEVE:

1. **Sincronizar documentação de produto** (se o projeto tiver AGENTS.md com essa regra)
2. **Criar a Pull Request** com todo o trabalho da Sprint

#### Pre-PR: Sync Product Documentation

**Se o projeto tem uma regra em AGENTS.md sobre sincronizar docs antes de PR, siga-a.** Exemplo comum: docs sob `product/management/`, `product/engineering/`, `product/design/` precisam refletir o estado real do código.

**O que syncar (checklist):**

| Doc | O que verificar |
|-----|----------------|
| `product-management/PRD.md` | Features table — novas features marcadas como Done. Notas desatualizadas removidas |
| `product-management/product-roadmap.md` | Sprints/Horizons concluídos movidos para RELEASED |
| `product-management/user-stories.md` | Histórias adiadas que foram entregues — mover para Released |
| `product-engineering/release-notes.md` | Nova seção de release com features, endpoints, test counts |
| `product-engineering/test-plan.md` | Test counts atualizados, novas suítes adicionadas |
| `product-engineering/SAD-ERD-tech-specs.md` | Verificar divergências com o código real |

**Estratégia de execução:** Estas são 5+ edições independentes — **executar em paralelo** via `delegate_task(tasks=...)`. Cada subagente recebe instruções precisas de patch. Se o sistema suporta até 3 tasks paralelas, fazer 2 lotes (3 + 2). Cada task leva ~40s. Total: ~80s para todas as edições vs ~5min sequencial.

**Padrão de prompt para cada subagente:**

```python
# Template de prompt de doc sync
f"""O {doc_path} está em /opt/data/code/workstation/{projeto}/{doc_path}. Mudanças:

[LISTA DE PATCHES COM old_string + new_string EXATOS]

Use o tool patch para editar o arquivo. Verifique cada patch com read_file depois."""
```

**Verificação pós-sync:** Após todos os subagentes concluírem, rodar `git status` para confirmar que todos os arquivos foram modificados, depois `git diff --stat` para rever o escopo. Commitar como `"chore: sync product docs — <milestone> promoted to RELEASED"`.

#### Estratégia de PR Creation

**Pi best para PR creation:** Pi best (MiniMax M3) é lento e tem cota limitada (5h/mês no OpenCode Go). Para PR creation, Pi precisa:
1. Ler todo o diff da Sprint (centenas de arquivos) — 5-10 min só de leitura
2. Escrever 6-7 commits convencionais
3. Fazer git push + gh pr create

⚠️ **Cada execução de Pi best consome 5-10 min de cota que poderiam ser usados em tarefas mais complexas.** PR creation é puramente mecânico (git add → commit → push → gh pr create) e não requer a inteligência do MiniMax M3.

**Alternativa recomendada: execução manual (Hermes em vez de Pi).** Quando possível, o agente Hermes deve:
1. Criar a branch
2. Fazer os commits granulares com staging
3. Fazer push + gh pr create

Isso é mais rápido (2-3 min vs 30 min) e não gasta cota do Pi.

#### ⚠️ Pi best timeout — OpenCode Go tem cota mensal de 5h

O provider `opencode-go` (MiniMax M3) tem limite de **5 horas mensais de uso**. Quando excede, retorna `GoUsageLimitError`:
```
429 GoUsageLimitError: "5-hour usage limit reached. Resets in 3hr 22min."
```

Neste caso:
- **Aguardar reset** (~3h) ou
- **Trocar provider** para `deepseek/deepseek-v4-pro` (API direta, $0.14/M input) — mais cara mas sem cota
- **Fazer manualmente** (recomendado para PR creation)

#### ⚠️ Pi best — precisa de ~30 min e nunca rodar em foreground

Pi best leva 5-10 min só lendo contexto antes de começar a escrever. No foreground do Hermes (timeout 180s) é morto antes de produzir output. Sempre usar `background=true, notify_on_complete=true` para Pi best.

**Se Pi morrer antes de escrever:** Verificar session files e retomar com `--session` (ver skill `pi-agent-coordination`).

#### Fluxo de PR Creation

```bash
# 1. Criar branch
git checkout -b feat/sprint-N-v1

# 2. Commits granulares (conventional commits)
git add <files-do-GCal>
git commit -m "feat: add Google Calendar sync with retry and failure badge"
git add <files-do-MCP>
git commit -m "feat: implement MCP action token lifecycle"
# ... etc

# 3. Push + PR
git push -u origin HEAD
gh pr create \
  --title "Sprint N: features" \
  --body "## Sprint N\n\nTabela de features, testes, custo" \
  --label "enhancement"
```

#### Sprint Close — Optional: PR Preview CI/CD

If the project has Nginx Proxy Manager on the same host, set up automatic preview environments per Pull Request:

1. Create `docker-compose.preview.yml` — override with `container_name: app-pr-${PR_NUMBER}`, DB isolation
2. Create `scripts/register-preview.sh` — registers proxy host in NPM SQLite DB (see `npm-database-schema.md` in oracle-host-access skill)
3. Create `.github/workflows/preview.yml` — builds + deploys on PR open, cleans up on PR close, comments URL
4. Use sslip.io for wildcard DNS: `https://{PR_NUMBER}.{IP}.sslip.io`

This gives every PR its own subdomain pointing to isolated containers. The production pipeline (`ci.yml`) should only deploy on push to `master` (PR merge).

---

## 2.8 Sprint Reattempt (Re-tentativa)

Quando a Sprint falhou no meio da execução (engineering não concluída, revisão pendente, working directory poluído) e você quer recomeçar com uma branch limpa:

### Gatilho

- Sprint anterior morreu na engenharia (staging dirs, prompts avulsos, código incompleto)
- Usuário quer "segunda tentativa" com mesmo escopo
- Working directory poluído com artefatos da tentativa anterior

### Fluxo

```bash
# 0. Branch naming: sprintN-v2 (ex: sprint1-v2 = reattempt da Sprint 1)
#    NUNCA sprintN.5 (isso sugere um complemento, não reattempt)

# 1. Criar branch limpa a partir de master (ver seção 3.3)
git checkout master && git pull
git checkout -b sprint1-v2

# 2. Preservar docs da Sprint anterior (user-stories, brief, design)
#    Usar git log para encontrar o commit que contém os docs
git log --all --oneline -- product/sprint_1/ | head -5
git checkout <HASH> -- product/sprint_1/

# 3. ⚠️ LIMPAR working directory — remover lixo da tentativa anterior
#    Prompts Pi, staging dirs, scripts avulsos, test files, migrations fora do lugar
rm -rf \
  prompts/ \
  _sprint*_staging/ \
  staging/ \
  _deploy_*.sh \
  backend/taskflow/migrations/ \  # se fora do alembic/
  scripts/deploy-*.sh \
  data/ \
  .github_backup/
```

### Decidir por onde recomeçar

O usuário valida se as fases já concluídas ainda fazem sentido:

| Fase | Se docs OK | Se docs desatualizados |
|------|-----------|----------------------|
| **Brief (2.2a)** | Pular | Re-entrevistar |
| **Planning (2.3)** | Pular | Re-gerar user stories |
| **Design (2.4)** | Pular | Re-gerar designs |
| **Agy review (2.4)** | ❌ **Nunca pular** — agy review é o gate | Rodar novamente |
| **Engineering (2.5)** | ❌ Fase que falhou | Re-começar daqui |

### Regras da Reattempt

1. **Commitar o feedback do agy** antes de iniciar engineering — se o agy review foi pulado na tentativa anterior, ele DEVE ser executado agora (gate obrigatório)
2. **Working directory deve ficar limpo** antes de começar — rastro da tentativa anterior confunde Pi e Hermes
3. **Branch naming claro**: `sprint1-v2` comunica "reattempt", `sprint1.5` comunica "complemento". Use o primeiro.
4. **NUNCA force push** na branch reattempt — se precisar atualizar, merge

---

## 3. Comandos Úteis

### 3.1 Ver Itens da Backlog

```bash
grep "^### BACKLOG" /opt/data/code/workstation/<projeto>/product/backlog.md
```

### 3.2 Ver Sprints

```bash
ls -d /opt/data/code/workstation/<projeto>/product/sprint_*/ 2>/dev/null
```

### 3.3 Criar Nova Sprint (Clean Branch)

⚠️ **NUNCA continuar na branch da Sprint anterior.** Após o MVP ou após uma Sprint concluída, criar uma **branch limpa a partir da master**. A branch antiga mantém o histórico de engenharia; a nova branch carrega só a documentação e a infraestrutura de CI/CD.

> **Nomenclatura por propósito:**
> - Nova Sprint com features adicionais: `sprintN.5` ou `feat/sprint-N-v2` (ex: sprint 1, depois sprint 1.5)
> - **Reattempt** de Sprint que falhou no meio: `sprintN-v2` (ex: `sprint1-v2` = segunda tentativa de completar a Sprint 1)
> - O nome `sprintN.5` sugere uma continuação/complemento. `sprintN-v2` comunica claramente "nova tentativa, mesmo escopo".

#### Fluxo completo:

```bash
# 1. VERIFICAR branch antiga existe (segurança)
git branch -a | grep feat/sprint-N-v1

# 2. Ir para master e atualizar
git checkout master
git pull origin master

# 3. Criar nova branch a partir de master
#    Se for REATTEMPT de Sprint: sprint1-v2
#    Se for complemento/pipeline: sprint1.5
git checkout -b sprint1-v2

# 4. Preservar documentação da Sprint anterior
#    (cherry-pick APENAS os arquivos de docs, NUNCA código de engenharia)
#    Identificar o commit com os docs:
git log --all --oneline -- product/sprint_N/ | head -5
#    Copiar os arquivos específicos:
COMMIT="<hash-do-commit-com-docs>"
git checkout $COMMIT -- product/sprint_N/user-stories.md
git checkout $COMMIT -- product/sprint_N/brief-notes.md
git checkout $COMMIT -- product/sprint_N/design/
#    (Opcional: feedbacks da sprint se quiser preservar)
# git checkout $COMMIT -- product/sprint_N/feedbacks_sprint_N.md

# 5. Garantir pipeline de preview na nova branch
#    Se a Sprint anterior tinha preview CI, cherry-pick os arquivos:
OLD_BRANCH="feat/sprint-N-v1"
git checkout $OLD_BRANCH -- .github/workflows/preview.yml
git checkout $OLD_BRANCH -- docker-compose.preview.yml
git checkout $OLD_BRANCH -- scripts/register-preview.sh
git checkout $OLD_BRANCH -- scripts/unregister-preview.sh
git checkout $OLD_BRANCH -- scripts/register-proxy-host.py

# 6. VERIFICAR: preview CI precisa ser genérico (não branch-specific)
#    O trigger deve ser pull_request sem filtro de branch:
#    on:
#      pull_request:
#        types: [opened, synchronize, reopened, closed]
#    Os scripts devem usar só PR_NUMBER, nunca nome de branch.
cat .github/workflows/preview.yml | grep "branches:" || echo "✅ Sem filtro de branch — genérico"
#    Verificar scripts:
head -20 docker-compose.preview.yml  # container_name usa ${PR_NUMBER}
head -20 scripts/register-preview.sh  # Fora do deploy, sem hardcode de URLs

# 7. Commitar
git add -A
git commit -m "feat: sprint N.5 — docs + preview pipeline"
git push -u origin HEAD
```

#### Documentos a preservar:

| O que | De onde | Exemplo |
|-------|---------|---------|
| User stories | `product/sprint_N/user-stories.md` | 17 stories em Mike Cohn + Gherkin |
| Brief notes | `product/sprint_N/brief-notes.md` | Perguntas/respostas do brief de clarificação |
| Design files | `product/sprint_N/design/` | wireframes.md, user-flows.md, prototype.html |
| Preview CI | Sprints anteriores | preview.yml, compose override, scripts NPM |

#### NUNCA preservar da Sprint anterior:

- `product/sprint_N/engineering/` (code-tasks, feedbacks de engenharia — são do ciclo passado)
- Código fonte (migrations, models, services, API, UI, testes)
- Branch antiga (deixar como histórico, não reutilizar)

#### AGENTS.md e mudanças de infraestrutura

Se a Sprint anterior identificou regras ou workarounds que devem valer para todas as Sprints futuras (ex: regra de bloqueio por permissão), commitá-las **na master separadamente**, não na branch da Sprint:

```bash
git checkout master
# editar AGENTS.md para adicionar a regra
git add AGENTS.md
git commit -m "docs: AGENTS.md — regra de bloqueio por permissão de arquivo"
git push origin master
```

Isso garante que a regra valha para TODAS as branches futuras, não só para a Sprint atual.

#### Preview pipeline — checklist de genericidade

Antes de abrir um PR de uma nova branch, verificar:

- [ ] `.github/workflows/preview.yml` trigger: `pull_request: [opened, synchronize, reopened, closed]` (sem `branches: [master]` ou similar)
- [ ] `docker-compose.preview.yml` usa `container_name: app-${PR_NUMBER}` (não nome fixo)
- [ ] `register-preview.sh` usa `PR_NUMBER` para nome do container, domínio, DB
- [ ] `register-proxy-host.py` não tem hardcode de IP/domínio
- [ ] `unregister-preview.sh` limpa por `PR_NUMBER`
- [ ] NPM SQLite acessível (docker cp) e script de registro funcional
- [ ] GHCR_TOKEN ou PAT com escopo `read:packages` configurado no repositório

### 3.4 Atualizar Status da Sprint no Backlog

```patch
## 📋 Sprint N (planejada: YYYY-MM-DD)
→
## 📋 Sprint N (planejada: YYYY-MM-DD) — [design] ← trocar status
```

### 3.5 Sprint Readiness Checklist

Antes de começar a executar uma Sprint (Brief → Planning → Design → Engineering), verificar:

> 📘 `skill_view(name='backlog-and-sprint', file_path='references/sprint-readiness-checklist.md')` — checklist completo: baseline da branch, preview pipeline, docs preservados, fase do ciclo, lixo do working tree.

---

## 4. Formato do feedbacks_sprint_i.md

```markdown
# Feedbacks — Sprint <N>

## Iteração 1 — Pi (Design)

<wireframes criados, protótipos>

## Iteração 2 — Antigravity (Revisão)

<feedback visual, melhorias>

## Iteração 3 — Pi (Ajustes)

<ajustes implementados>

## ACORDO: AVANÇAR PARA ENGENHARIA

Ambos concordam.
```

---

## 5. Integração com o Pipeline

Esta skill é carregada quando:

- **Fase 5 é iniciada** (Iteração e Melhoria)
- **Usuário dá feedback** que adiciona item à backlog
- **Usuário solicita Sprint** ("quero implementar")
- **Sprint está em andamento** e precisa de revisão

Carregar junto com:
- `code-tasks-format` (`skill_view(name='backlog-and-sprint', file_path='references/code-tasks-format.md')`) — task format, fields, template and pitfalls
- `pi-agent-coordination` (para invocação do Pi)
- `product-pipeline` (para contexto do fluxo geral)
- `pi-session-audit` (para auditoria pós-execução: tokens, custo, duração e **monitoramento em tempo real de sessões Pi — carregar logo após lançar Pi**)
- `oracle-host-access` (para SSH, Docker, NPM SQLite, agy watchdog)

---

## Pitfalls

⚠️ **NÃO assuma alucinação do Pi best nos docs — o escopo da Sprint evolui durante a execução.** Pi best (MiniMax M3) frequentemente atualiza `product/engineering/` com features que foram implementadas mas você não reconhece do planejamento original. Ao ver um release-notes.md com "7-state GTD model" ou "Morning Report" que você não planejou explicitamente:
   1. **VERIFIQUE no código real primeiro:** `grep -rn "feature_name" backend/taskflow/models/*.py`, `grep -rn "endpoint" backend/taskflow/api/routes/`
   2. **VERIFIQUE no git diff** quais arquivos foram modificados e por qual sessão Pi
   3. Só reverta se a feature realmente não existir no código
   4. Erro comum: agentes assumirem que docs editados numa sessão Pi foram obra de uma sessão posterior que nunca escreveu nada — sempre verificar qual sessão editou quais arquivos via timestamp do JSONL

⚠️ **Sessão Pi efêmera — output persiste no shared volume:** Session logs do Pi (`*.jsonl`) vivem DENTRO do container Pi e somem quando o container morre ou o tmux é encerrado. Os arquivos de output (`product/sprint_N/design/wireframes.md`, etc.) persistem no shared volume. Sempre verificar os arquivos no shared volume antes de concluir que o Pi falhou — ele pode ter completado todo o trabalho e o que sumiu foi só o log.

⚠️ **Pi `--session` exige path .jsonl completo (partial UUID não funciona):** `pi --session 019ea544` retorna "No session found". O único modo confiável é:
   ```bash
   pi --session /home/pi/.pi/agent/sessions/--<dirname>--/<filename>.jsonl
   ```
   Ou use `pi -r` (seletor interativo). Para sessões headless (`pi -p`), elas NÃO aparecem no seletor — só o path direto funciona. Ver `references/pi-session-inspection.md`.

⚠️ **Pi permission block no `PHASE_COMPLETE` — adicionar manualmente.** Pi segue a REGRA ABSOLUTA do AGENTS.md e bloqueia se não consegue escrever no arquivo alvo. O cenário mais comum: Pi completa todas as tarefas mas trava ao adicionar `<!-- PHASE_COMPLETE: ... -->` por EACCES (arquivo owned por uid 1001, Pi é 10000). Sintoma: Pi sai com exit 0, log de permissão criado, mas marcador ausente. Fix: `ssh oracle-host 'sudo chmod -R o+w /home/ubuntu/selfhost/shared/code/workstation/PROJETO/product/sprint_N/'` e adicionar o marcador manualmente via patch.

⚠️ **Após lançar Pi best, carregar `pi-session-audit` para monitorar.** Não confiar apenas em `notify_on_complete` — Pi exit 0 não significa que escreveu arquivos. Carregar `skill_view(name='pi-session-audit')` e extrair métricas da sessão periodicamente: entries, custo, último toolCall. Último toolCall = `bash` com `cat >` = escrevendo. Último toolCall = `bash` com `git diff` = ainda lendo. Session vazia ou entries < 10 = Pi pode ter stallado.

⚠️ **Workstation paths:** Hermes vê `/opt/data/code/workstation/PROJETO`, Pi vê `/workspace/code/workstation/PROJETO`. São a mesma pasta. Sempre use o path correto para cada lado.

⚠️ **Backlog pode ficar desorganizada:** Conforme os itens crescem, o Hermes pode querer agrupar por tipo (feature, bug, refactor) ou por área. Se ficar grande demais, considere migrar para um formato estruturado (ex: JSON).

⚠️ **Sprints não concluídas:** Se o usuário pedir para parar no meio de uma Sprint, marcar itens como "não concluídos" e mover de volta para "Não Triados". Não perder o trabalho já feito.

⚠️ **Pi não sabe da backlog:** Pi não tem acesso automático à backlog. O contexto passado para Pi (modelo best) precisa incluir o conteúdo da backlog ou o path para ela.

⚠️ **Prompt files no shared volume:** Pi e Hermes compartilham o mesmo filesystem. `write_file()` funciona direto. Prompts podem ser escritos diretamente em `/opt/data/code/workstation/PROJETO/prompts/`.

⚠️ **Pi orphans — matar antes de re-lançar:** Cada `pi -p` carrega o modelo. Se múltiplos processos acumularem, competem por memória. Antes de lançar, limpar:

```bash
pkill -f "^pi$" 2>/dev/null; true
```

⚠️ **Pular o brief de clarificação (2.2a) gera user stories genéricas:** Pi best sem contexto claro do usuário produz histórias que parecem certas mas não capturam as decisões reais — ambuigidade vira especulação, que vira retrabalho na engenharia. 2-5 perguntas na entrevista economizam horas de código errado.

⚠️ **Agy session leak — matar sempre antes de recriar:** Agy sessions tmux podem sobreviver ao comando que as criou. Já observado: agy rodando por 24h+ sem completar, consumindo CPU. O processo `script -q -c env HOME=... /home/ubuntu/.local/bin/agy` fica vivo mesmo após `tmux kill-session`. Sempre verificar e limpar:
   ```bash
   ssh oracle-host 'tmux ls 2>/dev/null | grep agy'
   ssh oracle-host 'ps aux | grep "/bin/agy" | grep -v grep'
   ```
   Se houver processos órfãos: `ssh oracle-host "ps aux | grep '/bin/agy' | grep -v grep | awk '{print \$2}' | xargs -r kill"`

⚠️ **Agy -p mode vs tmux interativo para engineering review:** `agy -p` (print mode) tenta executar comandos (pytest, docker, ls) e pede permissão para cada um. No engineering review, agy inevitavelmente tenta rodar os testes — e o Docker exec timeouta. Em vez disso:
   - **Para code review:** usar tmux interativo, aprovar permissões em lote (option 3 "always allow"), ou
   - **Rodar testes manualmente** (Hermes executa pytest via docker, agrega resultados), depois
   - **Escrever feedback manualmente** combinando análise do agy + resultados reais dos testes
   - agy é bom para análise de código (migrations, schemas, rotas) — RUIM para execução de testes

⚠️ **Provider `--provider` + `--model` é OBRIGATÓRIO — o default `google` cai em `deepseek-v4-pro` (caro).** O Pi default provider é `google` (built-in), mas não há key configurada para ele. Sem `--provider`, Pi faz fallback silencioso para o primeiro provider com key no auth.json: `deepseek`, e o modelo padrão do `deepseek` é `deepseek-v4-pro` ($0.14/M input, $0.42/M output) — **não** o `v4-flash` mais barato. **Sempre passar `--provider` + `--model` explicitamente.** Usar wrapper `pi-cost` (`/opt/data/pi-global/bin/pi-cost`) que já fixa `--provider opencode --model opencode/deepseek-v4-flash-free`. Verificar via `pi --help | grep "default:"` para confirmar o provider padrão atual.

⚠️ **NUNCA usar `timeout N` com Pi.** Pi pode estar gerando output corretamente mas lentamente. O Zen gratuito é particularmente lento (2-3x mais que API direta). `timeout` mata o processo com exit code 0 (não 124!), `notify_on_complete` dispara, mas nenhum arquivo foi escrito. Sempre rodar sem timeout e verificar o arquivo de saída.

⚠️ **Vitest vs npm run build — erros diferentes.** Vitest transforma em tempo real e só type-checka arquivos sob teste. `npm run build` roda `tsc -b` que type-checka toda a codebase. Padrões que vitest perde: import paths errados em testes, `require()` em `.tsx` ESM, props ausentes na interface, `EventListener` type mismatch. Sempre rodar `npm run build` antes de push.

⚠️ **Force push sobrescreve commits do Pi no remoto.** A branch `feat/sprint-1-v1` no GitHub é compartilhada entre Hermes e Pi. Force-push a partir de branch local desatualizada remove commits de fix do Pi que corrigiam TS errors. Antes de force-push: `git fetch origin <branch> && git log HEAD..origin/<branch> --oneline`. Se houver commits remotos não incorporados, merge ou rebase, nunca force push por cima. Ver também **⛓️ Regra de Ouro — COMMIT SEMPRE** no topo do Sprint Cycle.

⚠️ **NUNCA fazer git checkout/branch switch sem antes verificar git status.** Um checkout descartou WORKING DIRECTORY inteiro (dezenas de arquivos de 5 features da Sprint 1) que Pi agents tinham gerado mas não estavam commitados. Não havia como recuperar — nem reflog, nem stash. A única proteção é commit antes de checkout. Ver **⛓️ Regra de Ouro — COMMIT SEMPRE** no topo do Sprint Cycle.

⚠️ **TrailingSlashMiddleware SKIP_PREFIXES + startswith bloqueia sub-rotas silenciosamente.** O TaskFlow usa `TrailingSlashMiddleware` com `redirect_slashes=False` no FastAPI. O middleware tem um set `SKIP_PREFIXES` e usa `path.startswith(prefix + "/")` para decidir se pula o redirect. Adicionar um prefixo como `"/api/v1/mcp"` ao `SKIP_PREFIXES` bloqueia o redirect para TODAS as sub-rotas (`/api/v1/mcp/action-tokens`, `/api/v1/mcp/foo`), não apenas a raiz. Se uma rota usa trailing slash (`@router.post("/action-tokens/")`) e o teste/cliente envia sem slash (`POST /api/v1/mcp/action-tokens`), o middleware pula o redirect → FastAPI recebe sem slash → não casa com a rota → 404. Debugging: (1) `git diff backend/taskflow/api/middleware/trailing_slash.py` — verificar se `SKIP_PREFIXES` foi modificado sem commit nesta sessão. (2) `git blame` mostra `"00000000 (Not Committed Yet)"` para mudanças não-commitadas — o maior sinal de alerta durante debugging de regressão. (3) Verificar se a rota usa trailing slash vs sem slash, e se o `_should_skip()` está bloqueando o redirect.

⚠️ **httpx AsyncClient (TestClient do FastAPI) não segue 307 em POST por segurança.** Mesmo com o TrailingSlashMiddleware corrigido (removendo o prefixo do SKIP_PREFIXES), o TestClient retorna 307 em vez de seguir o redirect quando o método é POST. Isso é comportamento padrão do httpx: POST redirects não são seguidos para evitar repetição acidental de mutações. A correção NÃO é forçar o follow_redirects — é eliminar a divergência entre a rota e o request: (a) alinhar o teste para usar o mesmo padrão de trailing slash da rota (`action-tokens/` com slash, como os demais endpoints), ou (b) remover o trailing slash da definição da rota. Preferir (a): convenção do projeto é usar trailing slash nos endpoints, e os testes de tasks/projects/contextos já seguem essa convenção. Sintoma: mesmo erro de status, mas muda de 404 (quando prefixo bloqueava) para 307 (quando prefixo foi removido). O 307 "passou a funcionar" significa que o redirect está ativo — o problema agora é que httpx não segue.

⚠️ **Vitest: `require()` não resolve módulos .tsx/.ts em runtime.** Diferente de `vi.mock()` (que é transformado e hoisted pelo vitest), o `require()` síncrono do Node.js não consegue resolver módulos TypeScript/JSX. Sintoma: `Cannot find module '../../contexts/ToastContext'` mesmo com path correto. A correção é usar uma referência mutável (`let mockRef = vi.fn()`) antes do `vi.mock()`, capturada por closure no factory function do mock. No teste, basta reatribuir `mockRef = vi.fn()` para injetar um mock específico — sem require(), sem mockReturnValue, sem redefinição do mock. Padrão:
   ```ts
   // No topo do arquivo, ANTES do vi.mock
   let toastMock = vi.fn();
   vi.mock("../contexts/ToastContext", () => ({
     useToast: () => ({ toast: toastMock }),
   }));
   
   // No teste específico
   it("teste com mock controlado", () => {
     toastMock = vi.fn();  // reatribui para este teste
     // ... assert using toastMock
   });
   ```

⚠️ **Arquivos .MD entregues via MEDIA, nunca como texto inline.** Quando o usuário pede um arquivo .md (skill content, relatório, documento de produto, log de testes), salvar o conteúdo em disco e entregar via `MEDIA:/path/to/file` no Telegram. Texto inline de .md longo é truncado, quebra formatação, e o usuário não consegue baixar. Esta regra se aplica a QUALQUER pedido de arquivo .md, não apenas em contexto de sprint.

⚠️ **agy atinge output token limit ao gerar prototypes grandes (>70KB):** O agy (Gemini 3.5 Flash) estoura o limite de tokens de saída ao escrever prototypes HTML acima de ~70KB. Sintoma: aparece \"model's generation exceeded the maximum output token limit\" no tmux log. agy tenta reescrever versão mais compacta automaticamente, mas pode perder funcionalidades. Se isso ocorrer:
   1. Aguardar — agy faz retry com versão menor automático
   2. Verificar se o arquivo foi escrito (`ls -la prototype.html`)
   3. Se versão compacta perdeu features (ex: 5 views → 3), quebrar o prompt: primeiro gerar o CSS isolado, depois o HTML estrutural, depois o JS
   4. Se precisar de rebuild completo (ex: mudança de design system), usar tmux interativo com múltiplos send-keys em vez de `agy -p`

⚠️ **UID mismatch (10000 vs 1001) — ainda existe, de arquivos legados:** Pi roda local (uid 10000), mas o shared volume `workstation/` contém arquivos/diretórios criados pelo **antigo container Docker Pi (uid 1001)**. Pi local (10000) **não consegue escrever** em diretórios owned por 1001 mesmo com 755. Sintoma: Pi escreve em local alternativo (ex: `backend/taskflow/migrations/` em vez de `backend/alembic/versions/`) quando o diretório alvo é owned por 1001.

Workarounds que funcionam:
   - **Via host SSH (confiável):** `ssh oracle-host "cp /host/path/source.py /host/path/dest/"`
   - **Via python3 (se o diretório alvo for world-writable):** usar `shutil.copy2()`
   - **Fix permanente:** `ssh oracle-host 'sudo chown -R ubuntu:ubuntu /home/ubuntu/selfhost/shared/code/workstation/PROJETO/'` — corrige ownership de todo o projeto
   - **NÃO funciona:** `write_file()`, `patch()`, `cp` do container, `python3 open()` para criar arquivo novo em diretório 755 owned por 1001

⚠️ **Restauração/alteração de enum cascadeia por todo o stack:** Mudar um enum de status (ex: adicionar `inbox`, restaurar 7 estados GTD) não é só backend — a cascata inclui:
   - **Model:** `Task.status` — adicionar/remover valores no SQLAlchemy Enum
   - **Migration:** Alembic migration para alterar a coluna (cuidado: SQLite não suporta `ALTER COLUMN`; PostgreSQL requer `ALTER TYPE` em transação separada)
   - **Schemas Pydantic:** `TaskCreate`, `TaskResponse`, `TaskUpdate` — validam contra o enum
   - **Queries/Repositories:** Filtros que usam `status` (ex: inbox agora é `status=inbox`, não "sem projeto E sem contexto")
   - **Frontend:** List views (Inbox, Today, Upcoming), filtros, badges de status, processamento inbox
   - **Testes:** Fixtures e assertions que referenciam valores antigos do enum
   - **Documentação:** user-stories.md, release-notes.md, api-contracts.yaml
   Estratégia: **fazer a migration primeiro**, depois atualizar model + schemas, depois queries, depois frontend, depois testes. Cada camada confirmada antes de avançar.

⚠️ **FastMCP decorators — `@mcp.tool()`, `@mcp.prompt()`, `@mcp.resource()` wrappam funções em objetos não-callable.** Os três decoradores do FastMCP transformam a função asíncrona em objetos `FunctionTool`, `FunctionPrompt`, ou `FunctionResource` — executáveis apenas pelo servidor MCP, nunca diretamente. Testes que importam a função decorada e tentam `await fn(...)` falham com `TypeError: 'FunctionX' object is not callable`.

   **Causa:** FastMCP v2+ converte funções decoradas em objetos internos que só rodam via `mcp.run()` ou RPC. A função original é perdida.
   
   **Solução única (padrão `_impl` + wrapper) para os 3 decoradores:**
   ```python
   # tools/core.py
   async def _create_task_impl(title, priority, ...):  # lógica pura, testável
       ...
   
   @mcp.tool()
   async def taskflow_create_task(title, priority, ...):
       return await _create_task_impl(title, priority, ...)
   
   # prompts/definitions.py
   async def _prompt_process_inbox_impl(title, status="next_action", ...):
       ...
   
   @mcp.prompt()
   async def prompt_process_inbox(title, status, ...):
       return await _prompt_process_inbox_impl(title, status, ...)
   
   # resources/stats.py  
   async def _stats_inbox_impl():
       ...
   
   @mcp.resource()
   async def stats_inbox():
       return await _stats_inbox_impl()
   
   # tests/test_mcp.py
   from taskflow.mcp.tools.core import _create_task_impl  # ✅ funciona
   from taskflow.mcp.prompts.definitions import _prompt_process_inbox_impl  # ✅ funciona
   from taskflow.mcp.resources.stats import _stats_inbox_impl  # ✅ funciona
   ```
   
   **IMPORTANTE:** O padrão `_impl` + wrapper é o **único** modo de testar a lógica dos 3 tipos de decorador FastMCP. Os testes de integração (contra o servidor MCP rodando) são uma alternativa mais pesada. O padrão thin wrapper garante que o decorador não interfere na testabilidade.
   
   **Verificação no CI:** Se o CI falhar com `FunctionPrompt object is not callable` nos tests de MCP prompts/resources/tools, a causa é sempre a mesma: os testes importam a função decorada em vez da `_impl`. O patch é extrair a lógica para `_impl` + criar wrapper decorado, e ajustar o import nos testes.
   
   **Nota:** `@mcp.tool()/prompt()/resource()` são do `fastmcp` (v2+). Não confundir com decoradores de outras libs MCP. Verificar a versão do fastmcp no `pyproject.toml`.

⚠️ **Reattempt sprint: `PHASE_COMPLETE: design` não significa design completo — o gate é o `ACORDO` do agy.** Pi best marca `<!-- PHASE_COMPLETE: design -->` ao terminar de gerar wireframes/user-flows/prototype. Isso é a conclusão da **geração Pi**, não da **fase de design**. A fase de design só termina quando o agy revisa e registra `ACORDO: AVANÇAR PARA ENGENHARIA` no `feedbacks_sprint_N.md`. Numa reattempt, é comum encontrar `PHASE_COMPLETE` sem `ACORDO` — a Sprint anterior pulou o agy review. Neste caso, **rodar agy review antes de qualquer engineering**, mesmo que os designs já existam.
