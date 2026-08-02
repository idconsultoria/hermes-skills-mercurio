---
name: taskflow-mcp-rules
description: "TaskFlow MCP usage rules — timezone, date patterns, best practices.

Carregue esta skill ao usar as ferramentas MCP do TaskFlow: converte datas UTC para BRT (UTC-3) ao exibir, segue o padrão de confirmação em 2 passos para escritas com ActionToken, e usa os comandos de leitura disponíveis. Cobre regras de exibição de prioridade e boas práticas de escrita."
type: Reference
timestamp: 2026-08-02T00:00:00Z
---

# TaskFlow MCP Rules

## Datas e Timezone
- O servidor TaskFlow está **UTC**. O usuário está em **BRT (UTC-3)**.
- Todo `due_date` vindo do MCP está em formato ISO 8601 com offset `+00:00`.
- **Sempre converter** ao exibir: subtrair 3h do horário UTC para mostrar no fuso do usuário.
- Exemplo: `2026-07-27T02:59:00+00:00` vence às `2026-07-26T23:59:00-03:00`.
- O Panorama (`taskflow_panorama_report`) também usa data UTC — verificar se o "hoje" dele corresponde ao BRT do usuário.

## Comandos MCP Disponíveis

### Leitura (sem confirmação)
| Comando | Uso |
|---------|-----|
| `taskflow_panorama_report` | Panorama diário — inbox, atrasadas, pendentes do dia, top 3 |
| `taskflow_get_next_actions` | Próximas ações ordenadas por prioridade/data |
| `taskflow_list_tasks` | Listar com filtros (status, contexto, projeto, prioridade) |
| `taskflow_get_task(id)` | Detalhe de uma task específica |
| `taskflow_weekly_review` | Revisão semanal GTD |
| `taskflow_get_prompt(name)` | Prompt nomeado |
| `taskflow_process_inbox(id)` | Sugerir processamento de item do inbox (requer confirmação) |

### Escrita (2-step com ActionToken — requer confirmação)
| Comando | Descrição |
|---------|-----------|
| `taskflow_create_task` | Criar task (2-step: preview → confirma) |
| `taskflow_update_task` | Atualizar task existente |
| `taskflow_complete_task` | Marcar como concluída |
| `taskflow_delete_task` | Soft delete (vai pra lixeira) |
| `taskflow_quick_add_nlp` | Adicionar via texto natural |

**Regra:** toda escrita exige confirmação do usuário antes do segundo step.

## Exibição
- Prioridade: #1 = 🔴, #2 = 🟠, #3 = 🟢, #4 = 🔵, null = —
- Agrupar tarefas por data de vencimento no fuso do usuário
- Destacar vencimentos nas próximas 24h
