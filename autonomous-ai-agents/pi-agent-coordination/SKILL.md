---
name: pi-agent-coordination
description: "Pi Coder Agent local no Hermes. Hierarquia: agy > Pi best > Pi cost. Invoacao direta sem Docker/SSH."
category: autonomous-ai-agents
---

# Pi Agent (Local)

> Pi Coder Agent v0.78.1 instalado como npm global LOCALMENTE no Hermes.
> Nada de Docker, SSH hops, split filesystem ou quoting hell.
>
> **Hierarquia:** agy (consultor externo) → Pi best (eng. sênior) → Pi cost (dev júnior)

## Hierarquia de Uso

```
CARO/ESCASSO     agy ─── Consultor externo especialista (design, UX, estratégia)
                     │   Usar em momentos estratégicos. Pouco e certeiro.
                     │   Prompt complexo, leitura de arquivos.
                     │
ESCASSO          Pi best ── Eng. sênior interno (MiniMax M3 via Go)
                     │   Planejamento, user stories, docs conceituais.
                     │   Tempo precioso, qualidade acima de velocidade.
                     │
BARATO/ABUNDANTE Pi cost ─ Dev júnior (DeepSeek V4 Flash)
                         Code tasks, fixes, revisões. Escopo restrito,
                         tarefas bem definidas previamente.
```

### Regra prática

| Tipo de tarefa | Quem |
|----------------|------|
| Design, UX, estratégia, pesquisa | **agy** (SSH host) |
| Planejamento, user stories, docs conceituais | **Pi best** (`opencode-go/minimax-m3`) |
| Code tasks, fixes, testes, revisões | **Pi cost** (`deepseek/deepseek-v4-flash`) |
| Tarefa muito simples (< 3 linhas) | Qualquer, preferir Pi cost |

## Localização

```
Binário:  /opt/data/pi-global/bin/pi
Config:   ~/.pi/agent/  (= /opt/data/home/.pi/agent/)
├── auth.json      — 4 providers
├── settings.json  — v0.78.1
└── skills/        — 21 skills (PM + UX + UI + Eng)
Dotfiles: gh:gustavomello9600/pi-dotfiles
```

## Providers e Modelos

| Provider | Model ID | Chave | Custo | Papel |
|----------|----------|-------|-------|-------|
| `opencode` (Zen) | `opencode/deepseek-v4-flash-free` | `OPENCODE_API_KEY` | **Gratuito** | **Pi cost** 🥇 |
| `opencode-go` (Go) | `deepseek-v4-flash` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi cost** 🥈 |
| `deepseek` (API direta) | `deepseek-v4-flash` | `DEEPSEEK_API_KEY` | $0.14/M input | **Pi cost** 🥉 |
| `opencode-go` (Go) | `minimax-m3` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** 🥇 |
| `opencode-go` (Go) | `deepseek-v4-pro` | `OPENCODE_API_KEY` | Cota ~$30/sem | **Pi best** fallback 1 🥈 |
| `deepseek` (API direta) | `deepseek-v4-pro` | `DEEPSEEK_API_KEY` | $0.14/M + $0.42/M | **Pi best** fallback 2 🥉 |
| `openrouter` | `openrouter/<model-id>` | `OPENROUTER_API_KEY` | Variável | Reserva |

### ⚠️ GoUsageLimitError — Cota do OpenCode Go

O provider `opencode-go` (usado para Pi best e Pi cost 🥈) tem um limite mensal
de **5 horas de uso**. Quando estoura, retorna:

```
429 {"type":"error","error":{"type":"GoUsageLimitError",
     "message":"5-hour usage limit reached. Resets in Xh Ymin."}}
```

**Sintomas:**
- Pi termina imediatamente com exit code 1 e sem output
- Nenhum token consumido (a chamada é rejeitada antes de processar)
- A sessão `.jsonl` fica com 1 única entrada de erro

**Ação imediata — fallback automático:**

1. **Se Pi best (`opencode-go/minimax-m3`) estourou cota:**
   ```bash
   # Fallback via deepseek direto (V4 Pro é mais caro mas melhor que nada)
   pi --session ~/caminho/da/sessao.jsonl --provider deepseek --model deepseek-v4-pro
   ```

2. **Se Pi cost (`opencode-go/deepseek-v4-flash`) estourou cota:**
   ```bash
   # Fallback via deepseek direct (V4 Flash, $0.14/M input)
   pi --session ~/caminho/da/sessao.jsonl --provider deepseek --model deepseek-v4-flash
   # Ou via Zen gratuito (mais lento, sem custo)
   pi --session ~/caminho/da/sessao.jsonl --provider opencode --model opencode/deepseek-v4-flash-free
   ```

**Regra de fallback na tabela de providers:**
| Provider principal | Quando falha | Fallback |
|-------------------|--------------|----------|
| `opencode-go/minimax-m3` (Pi best 🥇) | Quota 5h/mês | `opencode-go/deepseek-v4-pro` (🥈, via Go) → `deepseek/deepseek-v4-pro` (🥉, API direta) |
| `opencode-go/deepseek-v4-flash` (Pi cost 🥈) | Quota 5h/mês | `deepseek/deepseek-v4-flash` (🥉) ou `opencode/deepseek-v4-flash-free` (🥇) |

**NUNCA relance o prompt do zero** quando o erro for só de cota — a sessão
existente tem contexto valioso. Use `pi --session ...` com o fallback provider.

## ⚠️ Pi CLI ≠ Providers

`opencode`, `opencode-go`, `deepseek` são **nomes de providers** no auth.json, não CLIs.

| Correto | Errado |
|---------|--------|
| `pi -p "msg" --provider deepseek --model deepseek-v4-flash` | `deepseek -p "msg"` |

## ⚠️ Recuperar Sessão Interrompida (--session)

**SEMPRE** antes de relançar um Pi best que morreu, verificar se a sessão
original pode ser retomada. Relançar do zero = perder 5-10 min de leitura +
centenas de milhares de tokens já gastos.

Pi best (MiniMax M3) leva 5-10+ min só lendo arquivos antes de começar a
escrever. Se o processo morrer (timeout Hermes, kill, crash), **NÃO reinicie
do zero** — a sessão morta tem todo o contexto acumulado queimado.

Use `--session /path/to/session.jsonl` para continuar exatamente de onde parou:

```bash
# 1. IDENTIFICAR a sessão morta — buscar pelo --name usado
ls -lt ~/.pi/agent/sessions/--*/ | grep "sprint1-pr"

# 2. VERIFICAR se a sessão tem progresso real
python3 -c "
import json
with open('CAMINHO_DO_JSONL') as f:
    entries = [l for l in f if l.strip()]
print(f'{len(entries)} entradas')
last = json.loads(entries[-1])
print(f'Ultimo tipo: {last.get(\"type\",\"?\")}')
"

# 3. RETOMAR (Pi carrega o histórico e continua)
pi --session ~/.pi/agent/sessions/--<dir>--/<timestamp>_<uuid>.jsonl \
  --provider opencode-go --model minimax-m3
```

**Identificação correta:** entre sessões com o mesmo `--name`, o arquivo com
mais entradas é o que morreu mais tarde (mais progresso). Pi append ao mesmo
arquivo quando retomado — não cria um novo.

**Flags conflitantes:** `--session` e `-p` são mutuamente exclusivos.
`--session` carrega o prompt original da sessão. Se precisar modificar o
prompt, edite a primeira entrada do `.jsonl` diretamente.

## OpenCode Go — Cota Mensal de 5h

O provider `opencode-go` (MiniMax M3 e DeepSeek V4 Flash) tem **limite de
5 horas mensais de uso** por workspace. Quando estoura:

```
429 GoUsageLimitError: "5-hour usage limit reached. Resets in 3hr 22min."
```

**Fallback providers por prioridade:**
| Situação | Provider | Modelo | Custo |
|----------|----------|--------|-------|
| Pi best (Go exaurido) — 1º | `opencode-go` | `deepseek-v4-pro` | Cota semanal $30 |
| Pi best (Go exaurido) — 2º | `deepseek` | `deepseek-v4-pro` | $0.14/M input |
| Pi cost (Go exaurido) | `deepseek` | `deepseek-v4-flash` | $0.14/M input |
| Último recurso | `openrouter` | Varia | Variável |

**Comandos de fallback:**
```bash
# Pi best sem Go — 1° tentativa (via Go, mesmo provider)
pi -p "prompt" --provider opencode-go --model deepseek-v4-pro

# Pi best sem Go — 2° tentativa (API direta)
pi -p "prompt" --provider deepseek --model deepseek-v4-pro

# Pi cost sem Go
pi -p "prompt" --provider deepseek --model deepseek-v4-flash
```

⚠️ **NUNCA omitir `--provider` e `--model` ao invocar Pi.** O default do `pi` é `google` (built-in), mas não há provider "google" no auth.json. Pi cai em fallback para o primeiro provider disponível com key (`deepseek`) e o modelo padrão do deepseek é `deepseek-v4-pro` (não `v4-flash`). Consequência: toda sessão roda no tier mais caro sem você perceber. **Sempre explicitamente passar `--provider opencode --model opencode/deepseek-v4-flash-free` (gratuito) ou `--provider deepseek --model deepseek-v4-flash` (barato) ao lançar Pi Cost.** Verificar via `model_change` event no session `.jsonl` se o provider/model esperado foi usado.

⚠️ **Wrapper `pi-cost` disponível** em `/opt/data/pi-global/bin/pi-cost` que já fixa `--provider opencode --model opencode/deepseek-v4-flash-free`. Use `pi-cost` no lugar de `pi` quando quiser garantir o tier gratuito.

⚠️ **NÃO prefixar com `opencode-go/`** quando usando fallback.
`opencode-go/deepseek-v4-pro` tenta o provider Go (sem cota).
Use só `deepseek` como provider.

## Acessar Pi do Host via Docker Exec

As chaves do Pi vivem dentro do container Hermes em `/opt/data/home/.pi/agent/auth.json`.
Para usar o Pi via `docker exec` do host:

```bash
# ❌ ERRO: docker exec como root → ~ = /root/, sem chaves
docker exec -it hermes_agent pi ...  # "no API keys configured"

# ✅ CERTO: --user hermes + caminho absoluto
docker exec -it --user hermes hermes_agent \
  /opt/data/pi-global/bin/pi \
  --session /opt/data/home/.pi/agent/.../file.jsonl \
  --provider deepseek --model deepseek-v4-pro

# ✅ Se HOME não for herdado, passar explicitamente
docker exec -it --user hermes \
  -e HOME=/opt/data/home \
  -e DEEPSEEK_API_KEY=$(docker exec --user hermes hermes_agent \
    python3 -c "import json; print(json.load(open('/opt/data/home/.pi/agent/auth.json'))['deepseek']['key'])") \
  hermes_agent \
  /opt/data/pi-global/bin/pi \
  --session ...jsonl
```

O binário `pi` não está no PATH do user hermes — **sempre usar caminho completo**
`/opt/data/pi-global/bin/pi`. O `--user hermes` é obrigatório para acessar
as chaves em `/opt/data/home/.pi/agent/auth.json`.

## Como Invocar

### Padrão A — Prompt inline (curto, sem `$`, `` ` ``, `'`)
```bash
pi -p "seu prompt" --provider deepseek --model deepseek-v4-flash
```

### Padrão B — Prompt file (multi-linha, caracteres especiais)
```bash
pi -p "$(cat prompts/task.md)" --provider deepseek --model deepseek-v4-flash \
  --name "sprint-N-tarefa"
```

⚠️ **Sempre usar `--name "sprint-N-descricao"`.** O nome aparece no header do `.jsonl` de sessão e permite:
- Identificar qual sessão corresponde a qual tarefa na auditoria
- Resumir sessão pelo nome via `pi -r` (seletor interativo)
- Extrair tokens/custo depois via `skill_view(name='pi-session-audit')`

### Padrão B2 — Batch paralelo (features independentes)
Para features independentes dentro de uma Sprint (ex: F1 GCal e F5 MCP), rodar Pi em paralelo. Cada feature recebe seu próprio prompt e escreve em arquivos diferentes:

```bash
# Terminal 1: F1 GCal
pi -p "$(cat prompts/f1-gcal.md)" --provider deepseek --model deepseek-v4-flash --name "sprint1-f1"

# Terminal 2: F5 MCP (simultâneo)
pi -p "$(cat prompts/f5-mcp.md)" --provider deepseek --model deepseek-v4-flash --name "sprint1-f5"
```

Features são paralelizáveis quando não compartilham os mesmos arquivos de output (schema → model → service → api → ui → test de cada feature é isolado).

**⚠️ Zen gratuito é lento demais para execução paralela.** O provider `opencode/deepseek-v4-flash-free` tem rate-limit — 4 Pi paralelos com esse provider demoraram >10 min. Para paralelismo real, usar `deepseek/deepseek-v4-flash` (API direta, ~2-4 min cada) ou agrupar em 1-2 batches por vez com o Zen.

**Regra prática para paralelismo:**
| Cenário | Provider | Pi calls paralelas |
|---------|----------|-------------------|
| Features independentes (< 5 tasks cada) | `deepseek/deepseek-v4-flash` | Até 4 |
| Features independentes (> 5 tasks cada) | `deepseek/deepseek-v4-flash` | Até 2 |
| Qualquer tarefa com Zen free | `opencode/deepseek-v4-flash-free` | 1-2 (sequencial é mais rápido) |

### Padrão C — agy (design, UX, pesquisa estratégica)
```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  /home/ubuntu/.local/bin/agy -p "prompt complexo"'
```

### Padrão D — Pi via tmux (tarefas longas, preferido do usuário)
Para tarefas que podem levar minutos (code tasks, geração de docs), usar tmux em vez de `terminal(background=true)`. Dá visibilidade em tempo real e evita stall silencioso sem diagnóstico:

```bash
cat > /tmp/pi-prompt.md << 'EOF'
prompt aqui...
EOF
tmux kill-session -t pi-sessao 2>/dev/null; true
tmux new-session -d -s pi-sessao \
  "pi -p \"$(cat /tmp/pi-prompt.md)\" --provider deepseek --model deepseek-v4-flash"
sleep 30
tmux capture-pane -t pi-sessao -p -S -10  # ver progresso
```

### Sessões interativas (Termux)
```bash
# Instalar Pi (qualquer máquina)
bash <(curl -fsSL https://raw.githubusercontent.com/gustavomello9600/pi-dotfiles/main/scripts/bootstrap.sh)

# Rodar
cd ~/projetos/taskflow && pi
```

## ⚠️ Pre-Launch Check — Reuse Existing Pi Sessions

**Antes de lançar qualquer Pi novo, SEMPRE verificar:**

1. **Pi já está rodando?** `ps aux | grep " pi " | grep -v grep`
2. **Sessão ativa no JSONL?** A última sessão tem entries crescendo?
3. **Se estiver progredindo** (entries > 10, custo > $0.05, último toolCall é `read`/`bash`/`write`), **deixe terminar** — não reinicie do zero.
4. **Se stalled** (entries paradas por >120s), verificar o que Pi estava fazendo (últimas entries) e decidir: retomar com `--session` vs relançar.
5. **Se já gerou o arquivo esperado** mas não adicionou `PHASE_COMPLETE` (por EACCES), adicionar manualmente via `patch` em vez de relançar.

### Regra

```bash
# 1. Verificar processos
ps aux | grep " pi " | grep -v grep

# 2. Verificar última sessão
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl | head -3
python3 -c "
import json, glob
p = sorted(glob.glob('/opt/data/home/.pi/agent/sessions/--*/--*.jsonl'))[-1]
entries = [json.loads(l) for l in open(p) if l.strip()]
last = entries[-1]
print(f'{len(entries)} entries')
print(f'Ultimo tipo: {last.get(\"type\",\"?\")}')
if last.get('type')=='message':
    for c in last['message'].get('content',[]):
        if isinstance(c,dict) and c.get('type')=='toolCall':
            print(f'Ultima acao: {c.get(\"name\")}: {str(c.get(\"arguments\",{}))[:200]}')
"

# 3. Só lançar novo Pi se:
#    - Nenhum Pi rodando
#    - Última sessão completou (PHASE_COMPLETE presente ou >5min idle)
#    - Arquivo esperado não existe
```

**NUNCA faça isso** — recomeçar do zero queima tokens e perde contexto:
- ❌ `pkill -f "pi$" && pi -p "..."` (mata sessão produtiva)
- ❌ Relançar sem verificar se já existe arquivo de output
- ❌ Ignorar sessão `--session` viável e criar nova do zero

## ⚠️ Stall Detection & Parallel Execution

### ⚠️ Pi best (MiniMax M3) é LENTO — não confunda com stall

Pi best (`opencode-go/minimax-m3`) rotineiramente leva **5-10+ minutos só lendo**
arquivos antes de gerar o primeiro output. Numa sessão real de 181 entradas,
Pi passou 100+ entradas (~7 min) lendo código, docs, git diffs e schemas
antes de começar a escrever. **Não é stall — é o modelo montando contexto.**

Pi cost (`deepseek/deepseek-v4-flash`) é mais rápido nessa fase de leitura
(~30-60s), mas também pode passar 2-3 min em contexto grande.

**Sinal de stall real:** >120s sem que a contagem de entradas do JSONL cresça.
Verificar:
```bash
wc -l ~/.pi/agent/sessions/--*/$(ls -t ~/.pi/agent/sessions/--*/ | head -1)
```

**Sinal de leitura normal:** entradas crescendo, custo acumulando, última
entrada contendo snippets de código, diffs, ou schemas.

### Execução de Pi best sem timeout

Pi best (MiniMax M3) NUNCA deve rodar em foreground do Hermes — o timeout
padrão de 180s mata a sessão antes de Pi começar a escrever, mesmo que Pi
esteja progredindo normalmente na fase de leitura.

**Sempre usar background para Pi best:**
```bash
terminal(
  command="cd /opt/data/code/workstation/PROJETO && pi -p \"$(cat prompts/tarefa.md)\" --provider opencode-go --model minimax-m3 --name \"sprint-N-tarefa\"",
  background=true,
  notify_on_complete=true
)
```

Para Pi cost (DeepSeek V4 Flash), foreground com timeout=300 geralmente é
suficiente, mas background é mais seguro para prompts >30 linhas.

Pi pode stallar com prompts muito complexos (> 15 linhas). Sintoma: > 60s sem output.

### Diagnóstico

Verificar se Pi está realmente stallado VS apenas lento:

```bash
# 1. Verificar session files — se entries crescem, NÃO está stallado
wc -l ~/.pi/agent/sessions/--*/$(ls -t ~/.pi/agent/sessions/--*/ | head -1)
# 2. Verificar se há output visível via tmux (se usando tmux)
tmux capture-pane -t pi-sessao -p -S -5 2>/dev/null
```

### Execução paralela (features independentes)

Features de uma Sprint que tocam arquivos diferentes (ex: F1 GCal + F5 MCP) podem rodar **simultaneamente** em múltiplos Pi processes. Pi é leve o bastante para 4 processos paralelos sem competição de memória.

```bash
# Terminal 1: F1 GCal
pi -p "$(cat prompts/f1.md)" --provider opencode --model opencode/deepseek-v4-flash-free --name "sprint1-f1"
# Terminal 2: F5 MCP (lançar simultaneamente)
pi -p "$(cat prompts/f5.md)" --provider opencode --model opencode/deepseek-v4-flash-free --name "sprint1-f5"
```

⚠️ **NÃO usar `pkill` quando executando Pi em paralelo.** O padrão `pkill -f \"^pi$\"` mata todos os processos Pi, incluindo features independentes rodando em paralelo. Só matar zumbis específicos por PID ou session name.

### Quando stallar de verdade

```bash
pkill -f "pi --name.*sprint1-"   # matar APENAS um session específico
# migrar para agy (se tarefa for estratégica/design)
```

### ⚠️ Stall Silencioso

Pi pode **sair com exit code 0 sem produzir output**. O processo termina normalmente mas o arquivo esperado não é gerado. Acontece especialmente com:
- **DeepSeek V4 Pro** (modelo mais lento, maior chance de stall)
- Prompts que exigem ler + escrever múltiplos arquivos (> 3 simultâneos)
- Pi rodando em **foreground com timeout** (morre antes de escrever o output)

Exit code 0 **não é garantia** de sucesso. Sempre verificar o arquivo de output (ex: `ls -la`, `grep PHASE_COMPLETE`) independente do exit code.

### 🔍 Monitoramento via tmux (preferido)

O usuário prefere o **padrão tmux** (mesmo usado com agy) para tarefas longas do Pi, em vez de `terminal(background=true, notify_on_complete=true)`:

```bash
# 1. Escrever prompt como arquivo
cat > /tmp/pi-prompt.md << 'EOF'
prompt completo aqui...
EOF

# 2. Rodar Pi em tmux (mesmo container, sem SSH)
tmux kill-session -t pi-sessao 2>/dev/null; true
tmux new-session -d -s pi-sessao \
  "pi -p \"$(cat /tmp/pi-prompt.md)\" --provider deepseek --model deepseek-v4-flash"

# 3. Monitorar a cada 30s (visibilidade em tempo real)
for i in $(seq 1 40); do
  sleep 30
  echo "--- Poll $i ---"
  tmux capture-pane -t pi-sessao -p -S -5 2>/dev/null
  if [ -f "product/sprint_N/engineering/Sprint-N-code-tasks.md" ]; then
    echo "✅ Arquivo gerado!"
    break
  fi
done

# 4. Limpar
tmux kill-session -t pi-sessao 2>/dev/null; true
```

**Vantagem:** visibilidade em tempo real do que Pi está gerando, mesmo quando não crasha mas também não produz output.

### Modelos: V4 Flash > V4 Pro para code tasks

DeepSeek **V4 Flash é mais confiável** que V4 Pro para code tasks. V4 Pro stallou mais vezes com prompts equivalentes no mesmo setup. Usar V4 Pro APENAS para:
- Decisões arquiteturais complexas (ADR, escolha de stack, trade-offs)
- Documentos com análise de riscos/custos
- Prompts curtos (< 10 linhas) onde a profundidade do raciocínio importa

## Skills (21)

| Categoria | Skills | Qtd |
|-----------|--------|-----|
| 🌀 Ideação | `ideation-drilling` | 1 |
| 📋 PM (19) | `opportunity-solution-tree`, `prd-development`, `proto-persona`, `user-story`, etc. | 19 |
| 🧠 UX | `ux-design-principles`, `ux-empathy-map`, `ux-journey-map`, etc. | 7 |
| 🎨 UI | `ui-design-principles`, `ui-interaction-design`, `ui-form-design`, etc. | 5 |
| ⚙️ Eng | `software-architecture`, `tech-specs`, `entity-relationship-diagram`, etc. | 6 |

## Manutenção de Dotfiles

Configuração versionada em `gh:gustavomello9600/pi-dotfiles`:

```bash
# Máquina nova: instalar Pi + restaurar tudo
bash <(curl -fsSL https://raw.githubusercontent.com/gustavomello9600/pi-dotfiles/main/scripts/bootstrap.sh)

# Sincronizar skills (qualquer máquina)
cd ~/.pi-dotfiles && bash scripts/sync.sh pull   # repo → local
cd ~/.pi-dotfiles && bash scripts/sync.sh push   # local → repo
```

## Auditoria Pós-Execução

Após Pi completar uma tarefa, extrair métricas de uso da sessão `.jsonl`:

```bash
# Auditar última sessão
skill_view(name='pi-session-audit')
# ou comando direto
ls -lt ~/.pi/agent/sessions/--*/ | head -3
```

Carregar `pi-session-audit` para script completo de extração de tokens, custo e duração.

## ⚠️ Model Drift — Pi Best (MiniMax M3) Refatora Sem Aviso

Pi best (`opencode-go/minimax-m3`) tem **alta propensão a drift**: pode refatorar
APIs de serviços existentes, renomear arquivos e deletar arquivos não relacionados
sem instrução explícita. É um efeito da capacidade do modelo — ele "melhora" o que vê.

**Problemas observados:**
- **Renomeia arquivos:** `mcp_tokens.py` → `mcp.py` (sem ser instruído)
- **Refatora APIs:** Muda assinatura de métodos do service (`issue_token` retorno,
  `validate_token` parâmetros), quebra compatibilidade com testes e routes existentes
- **Deleta arquivos:** Remove `test_mcp_action_token_service.py` como efeito colateral
  de `rm` durante debugging
- **Muda schemas de rota:** Altera estrutura de request/response esperada pela API

**⚠️ PITFALL CRÍTICO — Não assuma alucinação em docs**

Pi best modifica `product/engineering/` durante sprint execution (release-notes,
tech-specs, ERD, SAD, api-contracts) como parte do fluxo normal de trabalho.
**Isso não é alucinação, é documentação do que foi implementado.**

Caso real: Pi incluiu "7-state GTD model", "Morning Report" e "GTD Tutorial" no
release-notes — features que realmente existiam no código. O agente que reverteu
esses docs sem verificar perdeu horas de trabalho e queimou tokens desnecessários.

**Regra:** antes de reverter qualquer alteração do Pi nos docs de engenharia:

```bash
# 1. Verificar se as features mencionadas existem no código
grep -n "feature_name\|new_field" backend/taskflow/models/*.py 2>/dev/null
grep -rn "endpoint_name" backend/taskflow/api/routes/ 2>/dev/null
ls frontend/src/components/NovoComponente* 2>/dev/null

# 2. Confirmar com git diff o que mudou — se as features existem, o doc está correto
git diff product/engineering/
```

Se a feature existir no código, o doc está correto — não reverta.

**Checklist pós-Pi best (drift detection):**

```bash
# 1. Checar arquivos deletados ou renomeados
cd /opt/data/code/workstation/PROJETO
git diff --name-status HEAD
echo "=== Arquivos esperados ==="
ls backend/taskflow/api/routes/mcp*.py 2>/dev/null
ls tests/unit/test_mcp*.py 2>/dev/null

# 2. Checar se API do service mudou (diff de assinatura)
grep -n "^    async def " backend/taskflow/services/*.py

# 3. Rodar testes que Pi best pode ter quebrado
pytest tests/unit/test_mcp* tests/integration/test_mcp* -v --tb=short

# 4. Se drift for detectado, restaurar do git e re-aplicar só o necessário
git checkout -- backend/taskflow/services/mcp_action_token_service.py
# depois aplicar correção seletiva em vez de reescrever o arquivo todo
```

## ⚠️ UID Mismatch & Deploy

Pi escreve em staging (`_sprint1_F*_staging/`, `/tmp/`, `staging/`) quando o diretório
alvo é owned por uid 1001 (projetos do container Pi antigo). Para implantar:

```
skill_view(name='pi-agent-coordination', file_path='references/deploy-host-ssh.md')
```

**⚠️ Cuidado com o path correto.** O volume montado no container é:
```
host:/home/ubuntu/selfhost/shared/code/ → container:/opt/data/code/
host:/home/ubuntu/selfhost/hermes/data/ → container:/opt/data/
```

Portanto:
- **Working tree (Pi escreve):** `host:/home/ubuntu/selfhost/shared/code/workstation/taskflow/`
- **CI deploy:** `host:/home/ubuntu/selfhost/taskflow/` (clone separado)

Sempre aplicar `chmod` no path correto — o `shared/code/` é o volume ativo.

### ⚡ Git Permission Fix (UID 1001 ↔ 10000)

`git add` falha com `"insufficient permission for adding an object"` quando `.git/objects/`
e `.git/refs/` têm permissão restritiva e o dono é UID 1001 (host) mas o agente roda como
UID 10000 (container).

**⚠️ `sudo chown -R` NÃO funciona em arquivos do `.git/`** — o Docker overlay filesystem
retém o UID original mesmo após chown. O Hermes não tem sudo. A correção é via SSH no host:

```bash
# Via SSH no host — tornar .git/ world-writable
ssh oracle-host 'sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type d -exec chmod 777 {} \; && sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type f -exec chmod 666 {} \;'
```

**Verificação:** após o comando, testar `git add` localmente.

**Aplicação no setup atual:**
```bash
ssh oracle-host 'sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type d -exec chmod 777 {} \; && sudo find /home/ubuntu/selfhost/shared/code/workstation/taskflow/.git -type f -exec chmod 666 {} \;'
```

### 🔄 Arquivos Novos Deletados pelo `git checkout`

`git checkout <branch>` deleta **arquivos untracked** que não existem na branch de
destino. Com UID 1001, o `Permission denied` impede a deleção — mas o arquivo some
mesmo assim (git tenta unlink e, falhando, o arquivo fica em estado inconsistente).

**Recuperação:** se existe um clone (`/opt/data/taskflow-pr/`) com os commits, copiar
de lá:

```bash
cd /opt/data/taskflow-pr
git diff --name-only origin/master HEAD --diff-filter=A | \
  while IFS= read -r f; do
    ssh oracle-host "mkdir -p /home/ubuntu/selfhost/taskflow/\$(dirname \"$f\")" 2>/dev/null
    ssh oracle-host "cat > /home/ubuntu/selfhost/taskflow/\$f" < "\$f"
  done
```

Se o clone não existe, o arquivo está perdido — só recuperável da sessão `.jsonl` do Pi.

**Prevenção:** antes de mudar de branch numa working tree com untracked files,
verificar com `git status --short | grep '^??'` e fazer stash ou commit primeiro.

## Verificação

```bash
pi --version                    # → 0.78.1
pi -p "OK" --provider deepseek --model deepseek-v4-flash  # → OK
ls ~/.pi/agent/skills/          # → 21 skills
```

## Referências

- `references/fastmcp-testability-pattern.md` — Como testar MCP tools com FastMCP (impl/wrapper pattern para contornar `'FunctionTool' object is not callable`)
