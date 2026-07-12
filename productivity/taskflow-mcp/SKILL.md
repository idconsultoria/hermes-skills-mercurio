---
name: taskflow-mcp
description: "GTD task management via MCP (Model Context Protocol) — connects over SSE.

Load this skill when managing tasks via the TaskFlow MCP server. Covers connecting over SSE (StreamableHTTP POST does not work), creating and updating tasks, managing contexts and projects, processing inbox items, and running weekly GTD reviews."
related_skills: [notion, apple-reminders]
type: ToolIntegration
timestamp: 2026-06-14T05:15:09Z
---

# TaskFlow MCP — Ferramentas e Workflows

TaskFlow é um sistema GTD de gerenciamento de tarefas exposto via MCP (Model Context Protocol).
Conecta-se via SSE (StreamableHTTP POST não funciona — SSE deve ser explícito).

## Conexão

```
Transport: SSE (StreamableHTTP POST padrão do Hermes não funciona)
URL:       http://172.19.0.1/mcp/sse
Messages:  http://172.19.0.1/messages/  (sem trailing slash no Nginx NPM)
```

## 🌐 Ambiente & Contexto de Usuário

### MCP user

O MCP server determina o usuário operacional via env vars no startup (`server.py:_ensure_default_user()`):

| Variável | Default | Preview (`docker-compose.preview.yml`) |
|----------|---------|----------------------------------------|
| `MCP_USER_EMAIL` | `mcp@taskflow.local` | `demo@taskflow.dev` |
| `MCP_USER_NAME` | `MCP User` | `Maria Silva` |

O server faz `get_by_email()` no banco apontado por `DATABASE_URL`. Se não existe, cria. **Toda operação MCP (criar task, listar, completar) age como esse usuário** — não como o git config do repositório nem como o GitHub do desenvolvedor.

### Conexão Hermes → Preview

No `config.yaml` do Hermes, o MCP taskflow aponta para:

```yaml
taskflow:
  url: http://172.19.0.1/mcp/sse
  headers:
    Host: 4.praxis.129.146.163.107.sslip.io
  transport: sse
```

O `Host` header corresponde ao **número do preview** (ex: `4.praxis...` = preview #4). Cada preview roda em container isolado com banco próprio (`taskflow_pr_{PR_NUMBER}`).

### Git config local vs global

O repositório `code/workstation/taskflow/` tem git config **local** diferente do **global**:

| Escopo | user.name | user.email |
|--------|-----------|------------|
| Local (repo) | `Hermes Agent` | `hermes@taskflow` |
| Global (padrão) | `Gustavo Mello` | `gustavomelloenciv@gmail.com` |

Commits saem como "Hermes Agent". O MCP opera como `MCP_USER_EMAIL`. **São dois contextos distintos**: um controla a autoria do commit, outro controla quem cria/altera dados via MCP.

## Ferramentas (10 total)

### Read-Only (sem confirmação)

| Tool | Descrição |
|------|-----------|
| `list_tasks` | Lista tasks com filtros: status, context, project, priority, due_date, search. Paginação via `next_cursor`. |
| `get_task` | Retorna task individual por UUID. |
| `get_next_actions` | Próximas ações ordenadas por prioridade. Parâmetro: `context` (filtro), `limit`. |
| `weekly_review` | Revisão semanal GTD completa: open_loops, someday_review, completed_this_week, inbox_count, next_actions_by_context. |

### 2-Step (requer confirmação via ActionToken)

Todas as ferramentas de escrita seguem fluxo de **2-step confirmation**:

1. **Primeiro call** → retorna `requires_confirmation: true`, `preview` com dados parseados, `action_token`
2. **Segundo call** → passa `action_token` como `confirm_token` para efetivar

⚠️ **IMPORTANTE — Bug conhecido**: o call de confirmação precisa **reenviar todos os campos** (title, description, priority, etc.). Campos omitidos no segundo call são perdidos mesmo que estivessem no preview.

| Tool | Parâmetros | Notas |
|------|-----------|-------|
| `create_task` | title, description, priority, context, project, due_date, due_time | ✅ **aceita nomes** para context e project — resolve automaticamente pra UUID. |
| `update_task` | task_id + campos a alterar | ⚠️ context/project **exigem UUID** — nomes causam DataError. Use o UUID retornado por `create_task` ou pela listagem. |
| `complete_task` | task_id | Marca como done. |
| `delete_task` | task_id | Soft delete → trash. |
| `process_inbox` | task_id, status, context, project, priority | ⚠️ context/project **exigem UUID** (mesmo bug do update_task). Use UUIDs. |
| `quick_add_nlp` | raw_text | ✅ **Superior para criação rápida** — parseia NLP natural. |

### Status válidos (check constraint `ck_tasks_status`)

Nem todos os valores passam na constraint do banco. **Confirmados funcionais:**

| Status | Uso | Equivalente PT-BR |
|--------|-----|-------------------|
| `inbox` | Padrão — task não processada | Caixa de entrada |
| `next_action` | Próxima ação concreta | Próxima ação |
| `waiting` | Aguardando algo externo | Aguardando |
| `completed` | Task concluída | Concluída |
| `trash` | Soft delete | Lixeira |

**⚠️ `pending` NÃO funciona** — viola `ck_tasks_status`. Use `waiting` para "aguardando".
**⚠️ `in_progress` NÃO funciona** — use `next_action` para tasks em andamento.

## NLP Quick-Add (recomendado)

O `quick_add_nlp` é a ferramenta mais potente para criar tasks rapidamente. Sintaxe reconhecida:

```
"Comprar leite #casa !p2"
"Revisar PR do TaskFlow amanhã !p1"
"Revisar landing page com equipe amanhã as 10h !p1 @computador"
```

Tokens parseados:
- `!p1`, `!p2`, `!p3`, `!p4` → prioridade
- `@context` → contexto (mapeado para UUID interno)
- `amanhã`, `hoje`, `segunda` → datas relativas
- `as 10h`, `as 14:30` → horário

A task vai para **inbox** por padrão. Use `process_inbox` depois para triar.

## Resources (3)

| URI | Descrição |
|-----|-----------|
| `taskflow://stats/inbox` | Contagem de tasks no inbox (sem contexto nem projeto) |
| `taskflow://stats/weekly` | Stats por dia: concluídas ✅ e adicionadas ➕ |
| `resource://gtd/guide` | Guia rápido do método GTD adaptado para o TaskFlow |

## Prompts (3)

| Prompt | Descrição |
|--------|-----------|
| `process-inbox` | Template para processar task específica do inbox. Args: title, status, context, priority |
| `morning-briefing` | Briefing matinal com tasks atrasadas, inbox e pendências |
| `weekly-review` | Revisão semanal com loops abertos e concluídas |

## Workflow GTD no TaskFlow

1. **Manhã**: execute o prompt `morning-briefing` (via `get_prompt`)
2. **Captura**: use `quick_add_nlp` para tasks soltas
3. **Triagem**: use `process_inbox` para cada item do inbox (status, contexto, projeto, prioridade)
4. **Execução**: filtre `get_next_actions` por contexto
5. **Revisão semanal**: use `weekly_review` + resource `taskflow://stats/weekly`

## Diagnóstico — Production vs Preview

Quando o MCP retorna erros (502, 404, dados errados), verifique qual ambiente está ativo:

### 1. Host header no config.yaml

```bash
grep -A5 'taskflow:' ~/.hermes/config.yaml
# ou
grep -A5 'taskflow:' /opt/data/config.yaml
```

O `Host` header determina qual container o NPM roteia:
- `Host: 4.praxis.129.146.163.107.sslip.io` → preview da PR #4 (banco `taskflow_pr_4`)
- `Host: praxis.129.146.163.107.sslip.io` (sem número) → produção (banco `taskflow`)
- Sem Host header → rota padrão do NPM (pode ser 404)

### 2. DATABASE_URL no .env

```bash
grep DATABASE_URL /opt/data/taskflow-pr/.env
```

- `taskflow` → produção
- `taskflow_pr_N` → preview da PR N

**⚠️ Cuidado com mismatch:** o Host header pode apontar para preview enquanto o .env aponta para produção (ou vice-versa). Confira ambos.

### 3. Testar conectividade

```bash
# Com Host header (simula o que o Hermes faz)
curl -s -m 5 -H "Host: 4.praxis.129.146.163.107.sslip.io" http://172.19.0.1/mcp/sse

# Respostas:
# 200 + text/event-stream → MCP vivo e funcionando
# 502 Bad Gateway → container do backend não está rodando
# 404 → Host header não bate com nenhum proxy host no NPM
```

### 4. Status dos containers

```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep taskflow
```

Se nenhum container aparece, o compose não foi iniciado. Para subir:
```bash
cd /opt/data/taskflow-pr
PR_NUMBER=4 docker compose \
  -f docker-compose.yml \
  -f docker-compose.preview.yml \
  up -d
```

## Pitfalls

- `context`/`project` em `create_task` **aceita nomes** (ex: "celular", "casa") — resolve automaticamente pra UUID
- `context`/`project` em `update_task`/`process_inbox` **exige UUID** — nomes causam DataError. Use o UUID retornado por `create_task`
- Para descobrir UUID de um contexto existente, crie uma task dummy com `create_task` usando o nome e veja o `context_id` retornado, depois delete a task
- 2-step confirmation: **reenvie todos os campos** no segundo call — o preview não é usado para preencher lacunas
- `quick_add_nlp` pode truncar o título removendo tokens parseados (ex: "10h" some do title mas a data fica correta)
- `create_task` sem context/project cria a task sem contexto — use `update_task` depois se precisar adicionar
- A task criada vai para **inbox** independente dos parâmetros — precisa de `update_task` ou `process_inbox` para mudar o status
- Status `pending` e `in_progress` violam `ck_tasks_status` — use `waiting` para "aguardando" e `next_action` para em andamento
- O MCP não usa o mesmo user do git config local — sempre verificar MCP_USER_EMAIL antes de assumir identidade
- **Hora padrão do usuário:** quando não especificada, usar 23:59 como due_time
