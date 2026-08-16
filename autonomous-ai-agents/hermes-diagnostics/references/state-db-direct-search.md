# Busca direta no state.db — quando o session_search não encontra

> Validado em 14/08/2026. O `session_search` (FTS5) pode NÃO encontrar uma sessão que
> existe no banco (sessão não indexada, índice atrasado, ou o usuário pede "olhe no
> banco diretamente"). A fonte da verdade é o SQLite `/opt/data/state.db`.

## Localização e schema

- Banco: `/opt/data/state.db` (o `~/.hermes/state.db` é vazio/irrelevante).
- Tabelas: `sessions` (metadados) e `messages` (conteúdo).
- `sessions`: `id` (TEXT, PK), `title`, `source`, `model`, `started_at` (REAL unix),
  `ended_at`, `end_reason`, `message_count`, `last_activity_at`.
- `messages`: `id` (INTEGER PK), `session_id` (TEXT), `role`, `content`, `tool_calls`
  (JSON), `tool_name`, `timestamp` (REAL unix), `active`, `compacted`.
- **IDs truncados:** o `session_search` exibe IDs com prefixo de ~20 chars
  (ex.: `20260813_123130_dda538`), mas o ID real é mais longo
  (`20260813_123130_dda5382b`). Consultas SQL devem usar `LIKE '<prefixo>%'` ou pegar
  o ID completo via `SELECT id FROM sessions WHERE id LIKE '<prefixo>%'`.

## Consultas úteis

```python
import sqlite3, datetime
con = sqlite3.connect("/opt/data/state.db")
con.row_factory = sqlite3.Row

# 1. Sessões recentes (por atividade)
rows = con.execute("""SELECT id, title, source, started_at, last_activity_at,
                      (SELECT COUNT(*) FROM messages m WHERE m.session_id = s.id) as real_msgs
                      FROM sessions s ORDER BY last_activity_at DESC LIMIT 20""").fetchall()

# 2. Buscar conteúdo por palavra-chave (sessões de hoje BRT = UTC-3)
day_start = datetime.datetime(2026,8,13,3,0,0).timestamp()
rows = con.execute("""SELECT m.session_id, m.role, m.timestamp, substr(m.content,1,200) as c
                      FROM messages m
                      WHERE m.timestamp >= ? AND lower(m.content) LIKE '%quinzena 3%'
                      ORDER BY m.timestamp LIMIT 30""", (day_start,)).fetchall()

# 3. Ler o fluxo de uma sessão (user/assistant/tool)
rows = con.execute("""SELECT id, role, content, tool_name, timestamp FROM messages
                      WHERE session_id=? ORDER BY id""", (SID,)).fetchall()
# tool content é JSON: j.get('output') ou j.get('content') para resumir
```

## Pitfalls

- **Fuso:** timestamps são unix UTC; para "hoje em BRT" subtrair 3h (day_start =
  meia-noite BRT = 03:00 UTC).
- **Tool messages:** `content` é JSON string — usar `json.loads` e pegar `output`/`content`.
- **`total: 0` no session_search NÃO significa que a sessão não existe** — sempre
  confirmar via SQL direto quando o usuário afirmar que a conversa existiu.
- **Full ID:** prefixo truncado → `LIKE` no SQL antes de qualquer `WHERE session_id =`.
- Sessões podem ter `parent_session_id` (linhagem de compactação) — a raiz real é o
  `parent`; útil para "qual foi a sessão original".
