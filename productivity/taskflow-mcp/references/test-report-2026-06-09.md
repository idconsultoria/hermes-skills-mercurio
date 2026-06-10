# TaskFlow MCP — Test Report 2026-06-09

## Ambiente

- Transport: SSE (`http://172.19.0.1/mcp/sse`)
- Container: `taskflow-mcp-4`
- Nginx NPM: location `/messages/` sem trailing slash (bidirectional SSE)
- Usuário no sistema: Maria Silva (`e7ae299b-...`)

## Resultados dos Testes

### Read-Only (9/9 ✅)

| Tool | Status | Observação |
|------|--------|------------|
| `list_resources` | ✅ | 3 resources retornados |
| `list_prompts` | ✅ | 3 prompts retornados |
| `read_resource(inbox)` | ✅ | Inbox: 2 tasks |
| `read_resource(weekly)` | ✅ | Stats Seg 1✅+2➕, Ter 2✅+1➕ |
| `read_resource(gtd/guide)` | ✅ | Guia GTD markdown completo |
| `get_next_actions` | ✅ | 5 ações, ordenadas por prioridade |
| `list_tasks` | ✅ | Paginação via next_cursor |
| `weekly_review` | ✅ | JSON com 5 seções, 9 contextos |
| `get_prompt(weekly-review)` | ✅ | Template funcional |

### Escrita (2-step confirmation)

#### quick_add_nlp — ✅ Sucesso

Entrada:
```
Revisar landing page do site novo com equipe criativa amanhã as 10h !p1 @computador
```

Resultado: task criada em inbox, P1, due_date `2026-06-10T10:00:00`, contexto computador
Bug menor: título ficou "Revisar landing page do site novo com equipe criativa  as" — o "10h" sumiu

#### create_task — ⚠️ Duas tentativas

**Tentativa 1 (context=@loja):** ❌ Erro UUID
```
invalid input for query argument $1: '@loja' (invalid UUID '@loja': length must be between 32..36 characters, got 5)
SELECT contexts.id FROM contexts WHERE contexts.id = $1::UUID
```

**Tentativa 2 (sem context):** ✅ Criada mas perdeu description/priority/due_date
- Causa: o segundo call (confirm) não reenviou esses campos
- Preview do primeiro call tinha os dados, mas não foram usados

#### complete_task — ✅ Sucesso

Ambas as tasks de teste concluídas sem erro via 2-step flow.

## Contextos existentes (UUIDs conhecidos)

Extraído dos dados da sessão. Útil para `create_task`/`update_task`:

| Nome | UUID |
|------|------|
| @computador | `f07523b9-fb9e-4c0b-9d73-4d8557bf84a6` (observado via NLP quick-add) |

Nota: não foi possível extrair os demais UUIDs de contexto — o `weekly_review` retorna nomes, não UUIDs.
Para obter o UUID de um contexto, crie uma task via `quick_add_nlp` com `@context` e leia o `context_id` da task criada.
