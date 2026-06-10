# Parallel Pi Execution Pattern

## Quando usar paralelismo

Features dentro de uma Sprint são **independentes** quando tocam schema/model/service/api/ui/test **diferentes**. O grafo de dependências típico:

```
F1 (Foundation)  F2 (GCal)      F3 (MCP)       F4 (UI)         F5 (Infra)
Schema            Crypto/Retry   FastMCP dep     Bug fix          Config
Model             Repo           ActionTokenStore Webhook UI       CI/CD
Repo              Service        Auth            GTD Tutorial     Doc sync
Service+API       API+Routes     Server          Reports          E2E test
UI                Tests          Tools+Tests     FocusMode
Tests                                             Bulk edit
```

Cada coluna independente → paralelo real. **Mas o paralelismo não precisa ser por feature — pode ser por gabarito de dependência.**

## Estratégia real: 3 ondas por grafo de dependência (não 1 Pi por feature)

Em vez de lançar todos os Pi simultaneamente (que causa conflitos quando features compartilham arquivos), analisar o grafo de dependências do arquivo de code-tasks e agrupar em ondas:

### Onda 1 — Critical Path + Independentes (lançados juntos)

| Pi | Tasks | Conteúdo | Justificativa |
|:---|:------|:---------|:--------------|
| **w1-critical** | 30-40 | F1 Foundation (schema→model→repo→service→API→tests) | Bloqueia F2 e F3. Único que toca `task.py`, `task_repository.py`, `alembic/` | 
| **w1-utils** | 10-15 | Crypto, Retry, ActionTokenStore, AuthMiddleware, Webhook UI, GTD Tutorial, Config settings | Nenhum depende de F1 — tocam arquivos independentes (`core/`, `mcp/`, `frontend/`, `config.py`) |
| **w1-mcp-core** | 15-20 | MCP server.py, 6 core tools, 4 GTD tools, resources, prompts | ActionTokenStore + AuthMiddleware podem ser criados em paralelo com w1-utils (mesmo arquivo, primeiro que escrever ganha) |

### Onda 2 — Após F1 completar (ou com F1 já commitado)

A Onda 2 executa features que dependem das mudanças estruturais de F1 (migrations, model 7-state, schemas, services). Como F1 já está commitado, todos os 3 Pi podem rodar em paralelo — tocam conjuntos de arquivos diferentes:

| Pi | Tasks | Conteúdo | Toca arquivos |
|:---|:------|:---------|:--------------|
| **w2-gcal** | 15-20 | GCal service, OAuth flow, push/pull, freebusy, API routes, tests | `services/gcal_service.py`, `api/routes/integrations_google.py`, `schemas/gcal.py` |
| **w2-ui** | 20-25 | Morning Report, FocusMode, Sidebar 7-state, BulkEdit, GTD Tutorial, OverdueBadge, Webhooks UI, NLP preview | `frontend/src/pages/*`, `frontend/src/components/*`, `api/routes/tasks_bulk.py` |
| **w2-infra** | 10-12 | Docker compose, CI workflow, EventBus, doc sync, E2E smoke test | `docker-compose.yml`, `.github/workflows/`, `core/events.py`, `product/engineering/*.md` |

### Onda 3 — QA + Review

| Pi | Tasks |
|:---|:------|
| Hermes verifies full suite; agy reviews engineering; Pi best fixes bugs found by agy |

> **Nota:** Se a Onda 1 incluiu F3 MCP, a Onda 2 não repete MCP. Ajustar as ondas conforme o que já foi executado.

## Como analisar dependências do code-tasks

O arquivo `Sprint-N-code-tasks.md` de 3000+ linhas tem tasks com campo `**Depende de:**`. Estratégia:

```bash
# 1. Extrair tasks com dependência "—" (sem nada) — podem começar AGORA
grep -A5 "Depende de: —" Sprint-N-code-tasks.md | grep "^### Task-" | sed 's/.*\(T-[0-9]*\).*/\1/'

# 2. Extrair a tabela de resumo no final do arquivo (mostra paralelizáveis por feature)
tail -50 Sprint-N-code-tasks.md | grep -E "^\|\|.*\|.*\|"

# 3. Layer N de features diferentes são sempre paralelos
#    Layer 1 (schema) de F1 + Layer 1 de F3 (deps) rodam juntos
```

## Criação de prompts por batch

**NÃO** passar o code-tasks inteiro para cada Pi. Extrair só as tasks relevantes:

```
Cada prompt deve conter:
1. Contexto do projeto (mesmo para todos)
2. Tasks específicas do batch, na ordem de execução, com specs completas do code-tasks
3. Instrução de verificação: rodar pytest ao final e marcar PHASE_COMPLETE
```

### Template de prompt

```markdown
Projeto: {nome}
Diretório: /workspace/code/workstation/{projeto}

Você é um engenheiro de software. Execute as tasks abaixo na ORDEM em que estão listadas.

CONTEXTO:
- FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL/SQLite
- Branch: {branch}
- Baseline: {N} testes, todos verdes

====== TASKS ======

### Task-NNN: {descrição}
Local: {arquivo}
O que fazer:
{spec detalhada}

### Task-NNN+1: ...
```

## ⚠️ REGRA CRÍTICA: SEMPRE especificar `--provider` + `--model`

**NUNCA execute `pi -p "..."` sem passar `--provider` e `--model` explicitamente.**

O `pi` binary tem `--provider` default = `google`, que NÃO tem API key configurada no auth.json. Quando google falha, Pi **fallback silenciosamente** para o primeiro provider disponível (`deepseek`) com o modelo padrão (`deepseek-v4-pro`) — que custa $0.14/M input, $0.42/M output, **97× mais caro** que o Zen free.

Sintoma: você acha que está rodando no free tier mas está pagando API direta.

**Correção:** wrapper `pi-cost` fixa o provider/model correto:
```bash
# Em vez de:
pi -p "prompt" --name "task"

# Use SEMPRE:
pi-cost -p "prompt" --name "task"
# ou
pi -p "prompt" --name "task" --provider opencode --model opencode/deepseek-v4-flash-free
```

O wrapper `/opt/data/pi-global/bin/pi-cost` já existe e fixa:
```
pi --provider opencode --model opencode/deepseek-v4-flash-free "$@"
```

## Comando de execução paralela

```bash
# Onda 1 — 3 Pi em paralelo (usando wrapper pi-cost)
terminal background=true notify_on_complete=true: \
  cd /projeto && pi-cost -p "$(cat prompts/w1-critical.md)" --name "w1-critical"

terminal background=true notify_on_complete=true: \
  cd /projeto && pi-cost -p "$(cat prompts/w1-utils.md)" --name "w1-utils"

terminal background=true notify_on_complete=true: \
  cd /projeto && pi-cost -p "$(cat prompts/w1-mcp.md)" --name "w1-mcp"
```

Provider priority para Pi cost (SEMPRE especificar `--provider` + `--model`):
- 🥇 `--provider opencode --model opencode/deepseek-v4-flash-free` (Zen gratuito, $0/M)
- 🥈 `--provider opencode-go --model deepseek-v4-flash` (Go $30/sem, fallback se Zen lento/ratelimit)
- 🥉 `--provider deepseek --model deepseek-v4-flash` (API direta $0.14/M input, último recurso)

> ⚠️ **NUNCA usar `pi -p` sem `--provider`.** Default do Pi é `google` (sem key) → cai em `deepseek-v4-pro` (caro). Sempre passar explicitamente ou usar wrapper `pi-cost`.

3 Pi simultâneos usam ~560MB RAM total (~186MB cada com Zen free) — seguro no Oracle ARM.

## Monitoramento durante execução paralela

```bash
# 1. Verificar se todos os processos estão vivos
ps aux | grep " pi$" | grep -v grep

# 2. Verificar sessions JSONL (crescimento = progresso)
#    Path: ~/.pi/agent/sessions/--<slug>--/<timestamp>.jsonl
#    Onde slug = path com hífens (ex: --opt-data-code-workstation-PROJETO--)
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-{projeto}--/*.jsonl | head -5

# 3. Verificar entries por sessão (valores crescentes = ativo)
wc -l ~/.pi/agent/sessions/--opt-data-code-workstation-{projeto}--/*.jsonl | tail -5

# 4. Verificar arquivos criados (output real)
find /opt/data/code/workstation/{projeto} -name "*.py" -mmin -10 | sort

# 5. CPUs e memória
ps aux | grep " pi$" | awk '{printf "%s CPU=%s%% MEM=%dMB\\n", $2, $3, $6/1024}'
```

### Sinais de stall vs progresso

| Cenário | Sessions | Files | Ação |
|---------|----------|-------|------|
| 🟢 Progredindo | entries crescendo a cada minuto | novos arquivos .py aparecendo | Aguardar |
| 🟡 Lento mas vivo | entries estáveis mas >10 | arquivo sendo reescrito | Aguardar (Zen é lento) |
| 🔴 Travado | entries parados >5min, CPU 0% | sem arquivos novos | Matar e re-lançar com fallback Go |
| 🔴 Saiu cedo | exit code 0 inesperado | PHASE_COMPLETE ausente | Verificar output, re-lançar |

## Métricas reais (Sprint 1 TaskFlow, Jun 2026 — 122 tasks, 3 Pi paralelos)

- **Onda 1 (3 Pi):** F1 Foundation + Utils + MCP Core
  - Tempo total: ~15 min para primeiros outputs visíveis
  - ~18 arquivos criados nos primeiros 5 min
  - 3 sessions JSONL com 67-95 entries cada (crescendo)
  - RAM: ~186MB por processo Pi (total ~560MB)
  - Provider: Zen free (opencode/deepseek-v4-flash-free)
  - Custo: $0

- **Onda 2 (3 Pi):** GCal + MCP Full + UI Dependent
  - Estimado: ~20 min
  - Custo: $0

- **Onda 3 (1 Pi):** Infra + Doc sync + E2E
  - Estimado: ~10 min

## Padrão de nomes (--name)

Usar prefixo de onda + feature para rastreamento fácil:

| Nome | Onda | Conteúdo |
|------|------|----------|
| `w1-f1-foundation` | 1 | Critical path |
| `w1-utils` | 1 | Independent utilities |
| `w1-f3-mcp` | 1 | MCP core |
| `w2-gcal` | 2 | Google Calendar |
| `w2-mcp-full` | 2 | MCP remainder |
| `w2-ui-dependent` | 2 | UI que depende de F1 |

## Lições aprendidas

1. **Não confiar apenas em notify_on_complete** — Pi sai com exit 0 mesmo stallado. Sempre verificar session JSONL entries + file creation timestamps.
2. **Zen free é lento mas confiável** — 2-3x mais lento que Go, mas não rate-limitou durante execução de 3 paralelos. Primeiros outputs aparecem em ~1-2 min.
3. **3 paralelos é o sweet spot** — 4+ pode causar contenção de I/O no shared volume. 1 é desperdício de paralelismo.
4. **Prompt engineering é o bottleneck** — gastar tempo estruturando prompts por batch compensa mais que número de paralelos. Um prompt mal escrito = Pi gera código errado = retrabalho.
5. **Pi Cost é suficiente para code-tasks de implementação** — DeepSeek V4 Flash lida bem com tasks de 2-15 min de schema/API/UI. Não precisa de MiniMax M3 para tasks rotineiras.

## Limitações

- Features que tocam a MESMA tabela/arquivo NÃO são paralelizáveis (ex: F1 schema + F2 model no mesmo `task.py`)
- Mais de ~6 Pi simultâneos competem por RAM mesmo no Oracle ARM (cada Pi ~186MB com Zen free, ~300MB com Go)
- Pi Cost (Zen) pode falhar com rate-limit em horários de pico — ter fallback Go pronto
- Conflito de escrita: se 2 Pi escrevem o mesmo arquivo simultaneamente, o último que escrever vence. Para arquivos compartilhados (ex: `tools/gtd.py`), apenas 1 Pi deve ser responsável.
