---
name: taskflow-mcp
description: "Interact with the TaskFlow MCP server via Hermes Agent for GTD task management with SSE transport and 2-step confirmation.\n\nLoad this skill when managing tasks through the TaskFlow MCP system. Covers SSE transport setup, full tool catalog (list/get/create/update/delete tasks and next actions), 2-step confirmation flow for writes, context UUID requirements, NLP quick-add workflows, and GTD pipeline integration."
related_skills: [notion, apple-reminders]
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
| `create_task` | title, description, priority, context, project, due_date, due_time | **context aceita UUID, não nome** (ex: "@casa" → erro). use UUID do contexto. |
| `update_task` | task_id + campos a alterar | Mesma regra: context/project como UUID. |
| `complete_task` | task_id | Marca como done. |
| `delete_task` | task_id | Soft delete → trash. |
| `process_inbox` | task_id, status, context, project, priority | Para triagem GTD do inbox. |
| `quick_add_nlp` | raw_text | ✅ **Superior para criação rápida** — parseia NLP natural. |

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

## Pitfalls

- `context` em `create_task`/`update_task` espera **UUID**, não nome textual
- 2-step confirmation: **reenvie todos os campos** no segundo call — o preview não é usado para preencher lacunas
- `quick_add_nlp` pode truncar o título removendo tokens parseados (ex: "10h" some do title mas a data fica correta)
- `create_task` sem context/project cria a task sem contexto — use `update_task` depois se precisar adicionar
- A task criada vai para inbox independente do status informado — precisa de `process_inbox` para triar
