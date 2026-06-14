# Subagent Session Recovery from state.db

> **Skill:** deep-research
> **Criado em:** 12 Jun 2026

---

## Contexto

Subagentes `delegate_task` que timeoutam perdem o summary final, mas suas sessões
**persistem no state.db do Hermes** com todas as tool calls e resultados intermediários.
É possível recuperar dados parciais consultando o banco SQLite diretamente.

## Localização

```bash
/opt/data/state.db
```

## Schema relevante

### sessions
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | TEXT | Session ID (22-33 chars, comprimento variável) |
| parent_session_id | TEXT | Preenchido para subagentes |
| started_at / ended_at | REAL | Timestamps Unix |
| message_count | INTEGER | Total de mensagens |
| tool_call_count | INTEGER | Total de tool calls |
| end_reason | TEXT | NULL se timeout (não finalizou) |
| title | TEXT | Título (geralmente None para subagentes) |

### messages
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | PK |
| session_id | TEXT | FK para sessions |
| role | TEXT | user / assistant / tool |
| content | TEXT | Conteúdo ou resultado da tool |
| tool_name | TEXT | Nome da tool (apenas role="tool") |
| token_count | INTEGER | Tokens usados |

## Queries essenciais

### 1. Encontrar subagentes timeoutados

```python
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')

# Subagentes com parent_session_id (são filhos de delegate_task)
subs = conn.execute('''
    SELECT id, started_at, message_count, tool_call_count, end_reason
    FROM sessions
    WHERE parent_session_id IS NOT NULL
      AND parent_session_id != ""
    ORDER BY started_at DESC
    LIMIT 10
''').fetchall()
```

### 2. Extrair tool results de uma sessão específica

```python
# Tool results (web_search, web_extract, browser, etc.)
tool_msgs = conn.execute('''
    SELECT tool_name, content
    FROM messages
    WHERE session_id = ?
      AND role = "tool"
      AND content IS NOT NULL
      AND content != ""
    ORDER BY id ASC
''', (session_id,)).fetchall()

# Assistant messages (raciocínio — geralmente meta, pouca substância)
asst_msgs = conn.execute('''
    SELECT content
    FROM messages
    WHERE session_id = ?
      AND role = "assistant"
      AND content IS NOT NULL
      AND content != ""
    ORDER BY id ASC
''', (session_id,)).fetchall()

# User message (o goal que foi passado)
user_goal = conn.execute('''
    SELECT content FROM messages
    WHERE session_id = ? AND role = "user"
    ORDER BY id ASC LIMIT 1
''', (session_id,)).fetchone()
```

### 3. Extrair URLs de web_extract e browser_navigate

```python
import re

# Extrair URLs de resultados de tools
urls = re.findall(r'"url"\s*:\s*"(https?://[^"]+)"', content)
```

## Como interpretar os dados

### Tool results com conteúdo real
- `web_search` com `"web": [{...}]` — resultados reais com URLs e títulos
- `web_extract` com `"content": "..."` (>200 chars) — páginas extraídas
- `browser_vision` com `"analysis": "..."` — análises de screenshot
- `browser_navigate` com `"url": "..."` — páginas visitadas

### Tool results sem valor
- `web_search` com `"web": []` — vazio (Google bloqueando)
- `web_extract` com `"error": "..."` — página não acessível
- `browser_navigate` com `"bot_detection_warning"` — bloqueado

## Exemplo real (Delfos — 12 Jun 2026)

3 subagentes rodaram em paralelo com timeout de 600s cada, fazendo
15-23 chamadas de API antes de timeoutar:

| Subagente | Msgs | Tool calls | Conteúdo recuperado |
|-----------|------|------------|---------------------|
| NOTION | 69 | 45 | browser Linear.app/NNGroup, web_extract docs |
| MCP+LLM | 55 | 40 | **94 URLs**, 23 web_extract (MCP servers, ClickUp, GitHub) |
| UX+Tiimo | 63 | 42 | **116 URLs**, Tiimo browser_vision, ADHD sources |

## Limitações

1. **Assistant messages são pobres** — subagentes escrevem "Vou pesquisar..."
   em vez de sintetizar findings. O valor está nos tool results.
2. **Google bloqueia** — muitas web_search retornam vazias. Fonte confiável:
   DuckDuckGo html mode, Bing, URLs diretas, GitHub, docs oficiais.
3. **Lock contention** — não consultar state.db enquanto subagentes estão
   rodando ativamente (pode dar lock). Esperar término ou timeout.
4. **IDs truncados** — session_id tem comprimento variável (22-33 chars).
   Usar substring matching quando logs mostrarem apenas os primeiros N chars.

## Quando usar

- Subagentes timeoutaram com calls relevantes (20+ tool calls cada)
- Você quer enriquecer relatórios com dados coletados pelos subagentes
- Precisa de URLs ou trechos de páginas que os subagentes encontraram

## Quando NÃO usar

- Pesquisa direta já produziu relatórios equivalentes (fallback mais rápido)
- Subagentes completaram com sucesso (summary basta)
- Banco está em uso ativo (esperar fim da sessão)
- Poucas tool calls (<5) — provavelmente não coletaram nada útil
