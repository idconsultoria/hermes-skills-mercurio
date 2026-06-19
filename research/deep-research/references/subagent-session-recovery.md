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

## ⚠️ XML Wrapper Format — web_extract results

Tool results stored in `messages.content` are **wrapped in XML tags**, NOT raw JSON.
The actual JSON payload is embedded inside `<untrusted_tool_result source="web_extract">` ... `</untrusted_tool_result>`.

Example of raw content from state.db:
```
<untrusted_tool_result source="web_extract">
The following content was retrieved from an external source...
{
  "results": [
    {
      "url": "https://example.com",
      "title": "Page Title",
      "content": "# Markdown body..."
    }
  ]
}
[/untrusted_tool_result]
```

### Parsing function

Use this to extract the JSON from the wrapper:

```python
import json, re

def extract_from_wrapper(raw: str) -> dict | None:
    \"\"\"Extract JSON payload from state.db's XML-wrapped tool results.\"\"\"
    # Find the outermost JSON object (brace-delimited)
    start = raw.find('{')
    end = raw.rfind('}')
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end+1])
        except json.JSONDecodeError:
            pass
    return None
```

### Multi-result vs single-result shape

web_extract results come in two shapes:
- **Array shape** (`"results": [{...}, {...}]`) — 3 URLs per call → iterate `data['results']`
- **Single shape** (`"url": "...", "content": "..."`) — 1 URL per call → use directly

Both parse correctly with the function above. Check for `'results'` key to distinguish.

## Tool usage diagnosis

Before extracting large volumes, check what tools were called and how much content each produced:

```python
# Quick scan: what tools did the subagent use, and how many have real content?
tool_summary = conn.execute('''
    SELECT tool_name, COUNT(*) AS total,
           SUM(CASE WHEN LENGTH(content) > 500 THEN 1 ELSE 0 END) AS with_body
    FROM messages
    WHERE session_id = ? AND role = "tool"
    GROUP BY tool_name
    ORDER BY total DESC
''', (session_id,)).fetchall()
# web_extract with with_body > 0 = pages successfully extracted
# web_search with total >> with_body = search backend blocked
# assistant with length(content) > 200 = some synthesis happened
```

## Exemplo real 2 (Deep Research Augmentação — 18 Jun 2026)

2 subagentes timeoutaram com dezenas de tool calls cada. Recuperação bem-sucedida:

| Subagente | Msgs | Tool calls | Conteúdo recuperado |
|-----------|------|------------|---------------------|
| AI Agencies & Tech Stack | 76 | **50** | 18 web_extract: LangChain, Anthropic, Dify, RAGFlow, GitHub Copilot, Loop Engineering |
| Org Change & Modelos Emergentes | 128 | **85** | 22 web_extract: Deloitte Tech Trends, WEF Future of Jobs, HITL vs HOTL, Kotter+IA, AI Literacy, Superagency McKinsey |

**Recovery steps performed:**

1. **Find sessions** — Query `sessions` WHERE `parent_session_id IS NOT NULL` AND `end_reason IS NULL` (timed out). Sort by `started_at DESC`, limit 15.
2. **Diagnose tool usage** — `SELECT tool_name, COUNT(*), SUM(LENGTH(content)>500) ... GROUP BY tool_name` to see what was collected and what has real content.
3. **Extract web_search URLs** — Parse JSON from each result, deduplicate by URL, prioritize URLs with descriptions.
4. **Extract web_extract pages** — Parse XML wrapper (see above), extract url/title/content. Filter to results with `len(content) > 300` to skip error/redirect pages.
5. **Extract browser_navigate URLs** — Highest-value sources (primary docs, GitHub repos, official blogs).
6. **Assess coverage** — If 20+ pages and 50+ URLs exist, do targeted fallback only on gaps.
7. **Fallback + synthesize** — 2-3 direct web searches on uncovered topics, then full synthesis.

**Lições da recuperação:**
- Se o agente fez mais `web_extract` do que `web_search`, o recovery quase sempre vale a pena
- Se o agente só fez `web_search` (retornando vazio por bloqueio), o recovery rende pouco
- Foque em extrair o `content` dos resultados de `web_extract` — é onde está o valor real
- **Assistant messages são meta-pobres** — subagentes escrevem "Vou pesquisar..." em vez de sintetizar. O valor está nos tool results, não nas mensagens de assistente.

## Quando usar

- Subagentes timeoutaram com calls relevantes (20+ tool calls cada)
- Você quer enriquecer relatórios com dados coletados pelos subagentes
- Precisa de URLs ou trechos de páginas que os subagentes encontraram

## Quando NÃO usar

- Pesquisa direta já produziu relatórios equivalentes (fallback mais rápido)
- Subagentes completaram com sucesso (summary basta)
- Banco está em uso ativo (esperar fim da sessão)
- Poucas tool calls (<5) — provavelmente não coletaram nada útil
