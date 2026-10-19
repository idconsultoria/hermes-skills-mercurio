# `state.db` — esquema e cookbook SQL

Store de sessões do Hermes Agent (SQLite, um arquivo por perfil/instalação). Consultar
**read-only** via `sqlite3` do Python:

```python
import sqlite3
con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
```

## Tabelas que importam

**`sessions`** — uma linha por sessão:

- `id` (TEXT): `AAAAMMDD_HHMMSS_sufixo` para sessões normais, `cron_<job>_<data>` para crons.
- `source` (telegram | whatsapp | tui | cli | cron | subagent | …), `chat_id`, `chat_type`,
  `display_name`, `thread_id`.
- `title`, `title_source`, `profile_name`, `parent_session_id`.
- `started_at`, `ended_at`, `last_activity_at` (REAL, epoch), `message_count`,
  `tool_call_count`, `tool_names`.
- `model`, tokens (`input_tokens`/`output_tokens`/`cache_*`), `estimated_cost_usd`,
  `actual_cost_usd`, `billing_provider`.
- `cwd`, `git_branch`, `git_repo_root` (útil para achar onde o trabalho foi feito).
- `archived`, `pinned`, `hidden`, `end_reason`, `handoff_*`, `compression_*`.

**`messages`** — uma linha por mensagem:

- `id`, `session_id`, `role` (user | assistant | tool | system), `content` (TEXT, o campo
  que interessa na busca), `tool_name`, `tool_calls`, `tool_call_id`, `timestamp` (REAL).
- `token_count`, `reasoning*`, `display_kind`/`display_metadata`, `active`, `compacted`,
  `_compressed_summary` (mensagem compactada ainda tem `content` — a busca acha).

**FTS**: `messages_fts` e `messages_fts_trigram`, ambas com `content='messages'`
(colunas `content`, `tool_name`, `tool_calls`). Bom para frase; `LIKE` segue mais
previsível para substring curta e não depende de tokenização.

Outras tabelas vistas conforme a versão: `session_model_usage`, `system_prompts`,
`gateway_*`, `delivery_obligations`, `hosted_room_*`, `_litestream_*` (replicação).

## Cookbook

Termo 1 + termo 2 discriminante, ranqueado por sessão:
```sql
SELECT session_id, count(*) c, min(timestamp), max(timestamp)
  FROM messages
 WHERE lower(content) LIKE '%cliente%'
   AND lower(content) LIKE '%artefato%'
 GROUP BY 1 HAVING count(*) >= 3 ORDER BY c DESC LIMIT 40;
```

Hidratar as candidatas com título/fonte:
```sql
SELECT id, title, source, chat_id, message_count, started_at, ended_at, cwd
  FROM sessions WHERE id = ?;
```

Sessões por período (epoch REAL; converta com `time.localtime`):
```sql
SELECT id, title, source, started_at, message_count FROM sessions
 WHERE started_at BETWEEN ? AND ? ORDER BY started_at;
```

Bookends de uma sessão (objetivo + resolução) sem despejar a sessão:
```sql
-- objetivo
SELECT timestamp, content FROM messages
 WHERE session_id=? AND role='user' AND content IS NOT NULL AND length(content)>40
 ORDER BY timestamp LIMIT 2;
-- resolução
SELECT timestamp, content FROM messages
 WHERE session_id=? AND role='assistant' AND content IS NOT NULL AND length(content)>200
 ORDER BY timestamp DESC LIMIT 1;
```

Achar onde um artefato/URL aparece (domínio de deploy, nome de arquivo, nome de repo):
```sql
SELECT session_id, count(*), min(timestamp) FROM messages
 WHERE content LIKE '%vercel.app%' GROUP BY 1 ORDER BY 2 DESC;
```

Sessões sem título (tui/cli migradas) que precisam de nome:
```sql
SELECT id, source, started_at, message_count FROM sessions
 WHERE title IS NULL OR title='' ORDER BY started_at DESC LIMIT 50;
```

Filtrar títulos por assunto:
```sql
SELECT id, title, source, started_at FROM sessions
 WHERE lower(coalesce(title,'')) LIKE '%<assunto>%' ORDER BY started_at DESC;
```

## Ao ler o corpo das mensagens

`content` pode trazer markdown/tabelas grandes. Ao reportar, achate espaços
(`re.sub(r'\s+',' ',txt)`) e corte em ~1.200 caracteres por mensagem — o suficiente para
identificar objetivo/resolução sem estourar o contexto.
