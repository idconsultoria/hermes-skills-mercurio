# Subagent Session Recovery from state.db

> **Skill:** product-pipeline — F2 (Pesquisa)
> **Criado em:** 12 Jun 2026

---

## Contexto

Subagentes `delegate_task` que timeoutam perdem o summary final, mas suas sessões
**persistem no state.db do Hermes** com todas as tool calls e resultados intermediários.
É possível recuperar dados parciais consultando o banco SQLite diretamente.

## Localização

```bash
/opt/data/state.db  # (ou caminho configurado no Hermes)
```

## Schema

### sessions
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | TEXT | Session ID único |
| parent_session_id | TEXT | Session pai (preenchido para subagentes) |
| started_at / ended_at | REAL | Timestamps |
| message_count | INTEGER | Total de mensagens |
| tool_call_count | INTEGER | Total de chamadas de ferramentas |
| end_reason | TEXT | Motivo do término (NULL se timeout) |

### messages
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | PK |
| session_id | TEXT | FK para sessions |
| role | TEXT | user / assistant / tool |
| content | TEXT | Conteúdo da mensagem ou resultado da tool |
| tool_name | TEXT | Nome da tool (para role="tool") |

## Query para encontrar subagentes timeoutados

```python
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')

# Encontrar subagentes (parent_session_id não nulo)
subs = conn.execute('''
    SELECT id, started_at, message_count, tool_call_count
    FROM sessions
    WHERE parent_session_id IS NOT NULL
      AND parent_session_id != ""
    ORDER BY started_at DESC
    LIMIT 10
''').fetchall()
```

## Query para extrair tool results de subagentes timeoutados

```python
# Extrair resultados de tools de uma sessão específica
tool_msgs = conn.execute('''
    SELECT tool_name, content
    FROM messages
    WHERE session_id = ?
      AND role = "tool"
      AND content IS NOT NULL
      AND content != ""
    ORDER BY id ASC
''', (session_id,)).fetchall()

# Extrair mensagens do assistant (raciocínio intercalado)
asst_msgs = conn.execute('''
    SELECT content
    FROM messages
    WHERE session_id = ?
      AND role = "assistant"
      AND content IS NOT NULL
      AND content != ""
    ORDER BY id ASC
''', (session_id,)).fetchall()
```

## Exemplo real (Delfos project — 12 Jun 2026)

3 subagentes timeoutaram com 600s cada. Dados recuperados:

| ID | Msgs | Tool calls | Conteúdo recuperável |
|----|------|------------|----------------------|
| c83940 | 69 | 45 | web_search (vazios), web_extract (Linear, NNGroup), browser (DuckDuckGo) |
| 5ae82f | 55 | 40 | web_search (MCP servers, ClickUp, GitHub), web_extract (docs) |
| 2037ad | 63 | 42 | web_search (ADHD, Tiimo), browser_vision (Tiimo UI), web_extract |

## Limitações

- Apenas tool results são preservados — o raciocínio do subagente (assistant msgs)
  costuma ser meta-comentário ("Vou pesquisar...") sem substância.
- Resultados de web_search que retornaram vazios (Google bloqueando) consomem
  espaço mas não têm valor.
- O banco pode estar lockado durante sessão ativa — fazer consultas entre
  tool calls ou aguardar término.
- session_id tem comprimento variável (22-33 chars). Usar LIKE ou substring
  para matching parcial quando truncado em logs.

## Quando usar

1. Subagentes timeoutaram e você quer recuperar dados parciais
2. Um subagente em particular parece ter coletado algo útil antes de timeoutar
3. Comparar quantitativo de tool calls entre subagentes bem-sucedidos e falhos

## Quando NÃO usar

- Se a pesquisa direta já produziu relatórios equivalentes (como no Delfos)
- Para subagentes que completaram com sucesso (o summary já basta)
- Se o banco está em uso ativo (pode causar lock contention)
