# Token Usage Daily Breakdown

> Queries para extrair consumo diário de tokens do Hermes `state.db`, com
> breakdown por **input miss**, **output**, **cache hit**, e agrupamento por
> **fonte**, **horário**, e **modelo**.

## Schema Relevante

Tabela `sessions` — colunas de token:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `input_tokens` | INTEGER | Tokens de input **sem cache** (cache miss) |
| `output_tokens` | INTEGER | Tokens gerados (completion + reasoning) |
| `cache_read_tokens` | INTEGER | Cache hit (contexto reutilizado) |
| `cache_write_tokens` | INTEGER | Cache write (escrita inicial) |
| `reasoning_tokens` | INTEGER | Reasoning separado (quando reportado) |
| `estimated_cost_usd` | REAL | Custo estimado (nem sempre) |
| `actual_cost_usd` | REAL | Custo real (raro) |
| `source` | TEXT | `telegram`, `cron`, `tui`, `cli`, etc. |
| `started_at` | REAL | Unix epoch (segundos) |
| `model` | TEXT | Nome do modelo usado |
| `api_call_count` | INTEGER | Quantas chamadas de API na sessão |
| `tool_call_count` | INTEGER | Tool calls na sessão |

## Query Base — Consumo de um Dia Específico

```python
import sqlite3
from datetime import datetime, timezone

day_start = int(datetime(2026, 6, 15, tzinfo=timezone.utc).timestamp())
day_end   = int(datetime(2026, 6, 15, 23, 59, 59, tzinfo=timezone.utc).timestamp())

conn = sqlite3.connect('/opt/data/state.db')
rows = conn.execute('''
  SELECT id, source, model,
         input_tokens, output_tokens,
         cache_read_tokens, cache_write_tokens, reasoning_tokens,
         estimated_cost_usd, api_call_count, tool_call_count,
         datetime(started_at, 'unixepoch') as started
  FROM sessions
  WHERE started_at >= ? AND started_at <= ?
  ORDER BY started_at
''', (day_start, day_end)).fetchall()
```

## Por Fonte/Plataforma

```sql
SELECT source,
       COUNT(*)                              AS sessions,
       SUM(input_tokens)                     AS input_miss,
       SUM(output_tokens)                    AS output,
       SUM(cache_read_tokens)                AS cache_hit,
       SUM(cache_write_tokens)               AS cache_write,
       SUM(reasoning_tokens)                 AS reasoning,
       SUM(api_call_count)                   AS api_calls,
       SUM(tool_call_count)                  AS tool_calls,
       SUM(estimated_cost_usd)               AS cost_est
FROM sessions
WHERE started_at >= ? AND started_at <= ?
GROUP BY source
ORDER BY SUM(input_tokens) + SUM(output_tokens) DESC;
```

Fontes comuns: `telegram`, `cron`, `tui`, `cli`, `discord`, `whatsapp`, `slack`.

## Por Hora do Dia

```sql
SELECT CAST(strftime('%H', started_at, 'unixepoch') AS INTEGER) AS hour,
       COUNT(*)           AS sessions,
       SUM(input_tokens)  AS input_miss,
       SUM(output_tokens) AS output,
       SUM(cache_read_tokens) AS cache_hit,
       SUM(estimated_cost_usd) AS cost_est
FROM sessions
WHERE started_at >= ? AND started_at <= ?
GROUP BY hour
ORDER BY hour;
```

## Por Modelo

```sql
SELECT COALESCE(NULLIF(model, ''), 'unknown') AS model,
       COUNT(*)           AS sessions,
       SUM(input_tokens)  AS input_miss,
       SUM(output_tokens) AS output,
       SUM(cache_read_tokens) AS cache_hit,
       SUM(api_call_count) AS api_calls,
       SUM(estimated_cost_usd) AS cost_est
FROM sessions
WHERE started_at >= ? AND started_at <= ?
GROUP BY model
ORDER BY SUM(input_tokens) + SUM(output_tokens) DESC;
```

## Totais Agregados

```sql
SELECT SUM(input_tokens),
       SUM(output_tokens),
       SUM(cache_read_tokens),
       SUM(cache_write_tokens),
       SUM(reasoning_tokens),
       SUM(estimated_cost_usd),
       COUNT(*),
       SUM(api_call_count),
       SUM(tool_call_count),
       SUM(message_count)
FROM sessions
WHERE started_at >= ? AND started_at <= ?;
```

## Cálculo de Cache Hit Rate

```sql
SELECT source,
       SUM(cache_read_tokens) * 1.0 /
         (SUM(input_tokens) + SUM(cache_read_tokens) + 1) AS hit_rate,
       SUM(input_tokens) AS input_miss,
       SUM(cache_read_tokens) AS cache_hit
FROM sessions
WHERE started_at >= ? AND started_at <= ?
GROUP BY source;
```

## Múltiplos Dias (Range)

```python
day_start = int(datetime(2026, 6, 1, tzinfo=timezone.utc).timestamp())
day_end   = int(datetime(2026, 6, 15, 23, 59, 59, tzinfo=timezone.utc).timestamp())
```

Ou agrupar por data:

```sql
SELECT DATE(started_at, 'unixepoch') AS day,
       SUM(input_tokens) AS input_miss,
       SUM(output_tokens) AS output,
       SUM(cache_read_tokens) AS cache_hit
FROM sessions
WHERE started_at >= ? AND started_at <= ?
GROUP BY day
ORDER BY day;
```

## Message-Level Breakdown

Quando o `token_count` nas mensagens está preenchido (depende do provider):

```sql
SELECT m.role,
       SUM(COALESCE(m.token_count, 0)) AS total_tokens,
       COUNT(*) AS messages
FROM messages m
JOIN sessions s ON m.session_id = s.id
WHERE s.started_at >= ? AND s.started_at <= ?
  AND m.role IN ('user', 'assistant')
GROUP BY m.role;
```

> ⚠ A coluna `messages.token_count` nem sempre é preenchida por todos os providers.
> O nível `sessions` é mais confiável para agregados.

## Exemplo: Script Completo de Relatório Diário

```python
import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('/opt/data/state.db')

day_start = int(datetime(2026, 6, 15, tzinfo=timezone.utc).timestamp())
day_end   = int(datetime(2026, 6, 15, 23, 59, 59, tzinfo=timezone.utc).timestamp())

# --- Totais ---
ti, to, cr, cw, re, cost, sess, api, tools, msgs = conn.execute('''
  SELECT SUM(input_tokens), SUM(output_tokens),
         SUM(cache_read_tokens), SUM(cache_write_tokens),
         SUM(reasoning_tokens), SUM(estimated_cost_usd),
         COUNT(*), SUM(api_call_count), SUM(tool_call_count), SUM(message_count)
  FROM sessions WHERE started_at >= ? AND started_at <= ?
''', (day_start, day_end)).fetchone()

print(f"Sessões: {sess}")
print(f"Input miss:  {ti or 0:>12,}")
print(f"Output:      {to or 0:>12,}")
print(f"Cache hit:   {cr or 0:>12,}")
print(f"Total:       {(ti or 0)+(to or 0)+(cr or 0):>12,}")
print(f"API calls:   {api or 0:,}")
print(f"Tool calls:  {tools or 0:,}")
print(f"Messages:    {msgs or 0:,}")

# --- Por fonte ---
for row in conn.execute('''
  SELECT source, COUNT(*), SUM(input_tokens), SUM(output_tokens),
         SUM(cache_read_tokens)
  FROM sessions WHERE started_at >= ? AND started_at <= ?
  GROUP BY source ORDER BY SUM(input_tokens) + SUM(output_tokens) DESC
''', (day_start, day_end)):
    src, cnt, ti2, to2, cr2 = row
    print(f"  {src:10s} sess={cnt} in={ti2 or 0:>9,} out={to2 or 0:>9,} cache={cr2 or 0:>11,}")

conn.close()
```
