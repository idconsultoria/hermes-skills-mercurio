# state.db — Tabela `sessions` (Schema Descoberto via PRAGMA)

Fonte: `/opt/data/state.db` (canonical Hermes session store, SQLite + FTS5)

## Colunas da Tabela `sessions`

```
id                    TEXT     PRIMARY KEY (session UUID)
source                TEXT     'cron' | 'cli' | 'telegram' | 'discord' | etc.
user_id               TEXT     user identifier
model                 TEXT     model name (e.g. 'deepseek-v4-flash')
model_config          TEXT     JSON blob with model config details
system_prompt         TEXT     system prompt used
parent_session_id     TEXT     for delegation chains
started_at            REAL     Unix epoch (seconds, float)
ended_at              REAL     Unix epoch (seconds, float, nullable)
end_reason            TEXT     why session ended
message_count         INTEGER  number of messages in session
tool_call_count       INTEGER  number of tool calls
input_tokens          INTEGER  prompt tokens
output_tokens         INTEGER  completion tokens
cache_read_tokens     INTEGER  cache hit tokens (e.g. DeepSeek context caching)
cache_write_tokens    INTEGER  cache write tokens
reasoning_tokens      INTEGER  chain-of-thought / reasoning tokens
cwd                   TEXT     working directory
billing_provider      TEXT     provider used for billing
billing_base_url      TEXT     base URL for billing
billing_mode          TEXT     billing mode
estimated_cost_usd    REAL     cost estimated by Hermes
actual_cost_usd       REAL     actual cost reported by provider (rare)
cost_status           TEXT     'unknown' | 'estimated' | 'confirmed'
cost_source           TEXT     source of cost data
pricing_version       TEXT     pricing table version used
title                 TEXT     session title (if named)
api_call_count        INTEGER  number of API calls
handoff_state         TEXT     handoff status
handoff_platform      TEXT     platform for handoff
handoff_error         TEXT     error during handoff (nullable)
rewind_count          INTEGER  number of rewinds (default 0)
archived              INTEGER  whether session is archived (default 0)
```

## Observações

- A maioria das colunas de token/custo fica em **0** ou **NULL** até o fim da sessão (quando o Hermes finaliza os totais).
- `cache_read_tokens` domina o volume em sessões com skills carregadas (reuso de system prompt + contexto via prompt caching do provider).
- `estimated_cost_usd` fica em 0 para providers que não reportam preços via API billing (ex: DeepSeek via API key direta).
- `started_at` e `ended_at` são **Unix epoch em segundos** (float) — para converter: `datetime.fromtimestamp(ts, tz=timezone.utc)`.

## Query Útil para Cron Jobs

```sql
SELECT id, started_at, input_tokens, output_tokens,
       cache_read_tokens, cache_write_tokens, reasoning_tokens,
       estimated_cost_usd, message_count, model
FROM sessions
WHERE source = 'cron'
  AND started_at >= <epoch_start_of_day>
  AND started_at < <epoch_start_of_next_day>
ORDER BY started_at;
```
