# Session Diagnostic SQL Queries

Queries for investigating Hermes Agent session lifecycle issues via the SQLite state.db at `/opt/data/state.db` (or `~/.hermes/state.db`).

## Schema Reference

```
sessions:
  id                   TEXT PRIMARY KEY     — session ID (e.g. 20260715_071830_...)
  source               TEXT                 — telegram, whatsapp, cron, subagent, tui, cli
  user_id              TEXT                 — platform user ID
  model                TEXT                 — model used
  started_at           REAL                 — unix timestamp
  ended_at             REAL                 — unix timestamp (NULL = ACTIVE)
  end_reason           TEXT                 — why session ended
  message_count        INTEGER              — messages in session
  input_tokens         INTEGER              — total input tokens
  output_tokens        INTEGER              — total output tokens
  session_key          TEXT                 — routing key (e.g. agent:main:telegram:dm:6171996969)
  parent_session_id    TEXT                 — compression rotation parent
  compression_failure_error      TEXT       — error from last failed compression
  compression_failure_cooldown_until REAL  — cooldown timestamp
  chat_id              TEXT                 — platform chat ID
  chat_type            TEXT                 — dm, group, supergroup
  handoff_state        TEXT                 — handoff state (often empty on reset)
  handoff_error        TEXT                 — handoff error
  title                TEXT                 — session title
  archived             INTEGER              — 1 if archived
```

## Queries

### 1. Session count by end reason (diagnostic: see what kills sessions)

```sql
SELECT end_reason, COUNT(*) as cnt
FROM sessions
WHERE end_reason IS NOT NULL AND end_reason != ''
GROUP BY end_reason
ORDER BY cnt DESC;
```

**Interpretation:**
- `session_reset`: high count = forced resets (likely compression failure or provider crash)
- `agent_close`: normal session end
- `ws_orphan_reap`: gateway restart orphan cleanup (normal)
- `cron_complete`: cron jobs finishing (normal)
- `compression`: normal compression rotation (expected, count = active compression runs)

### 2. Sessions with compression failures

```sql
SELECT id, title, source, started_at, message_count,
       compression_failure_error,
       compression_failure_cooldown_until
FROM sessions
WHERE compression_failure_error IS NOT NULL
ORDER BY started_at DESC
LIMIT 10;
```

The `compression_failure_error` field contains the exact error message (e.g. "Error code: 402 - ..." = credits exhausted).

### 3. Session chain for a specific chat (trace the reset history)

```sql
SELECT id, source, started_at, ended_at, end_reason, message_count
FROM sessions
WHERE session_key = 'agent:main:telegram:dm:6171996969'
ORDER BY started_at;
```

Replace the session_key value with the target. Sessions with 0 messages followed immediately by another session = rapid reset loop.

### 4. Most recent sessions (recent activity overview)

```sql
SELECT id, title, source, started_at, ended_at, end_reason, message_count
FROM sessions
ORDER BY started_at DESC
LIMIT 20;
```

### 5. Sessions with most messages (largest conversations)

```sql
SELECT id, title, source, message_count, end_reason, input_tokens, output_tokens
FROM sessions
ORDER BY message_count DESC
LIMIT 10;
```

Sessions with 200+ messages and `end_reason='session_reset'` are prime candidates for the compression failure diagnosis.

### 6. Sessions that ended with specific reasons, grouped by time

```sql
SELECT DATE(started_at, 'unixepoch') as day,
       end_reason,
       COUNT(*) as cnt
FROM sessions
WHERE end_reason IN ('session_reset', 'agent_close', 'compression')
GROUP BY day, end_reason
ORDER BY day DESC, cnt DESC
LIMIT 30;
```

### 7. Gateway routing state

```sql
SELECT * FROM gateway_routing;
```

The routing JSON contains:
- `session_id`: current session the gateway routes to
- `was_auto_reset`: if the session was auto-reset
- `auto_reset_reason`: why it was auto-reset
- `model_override`: the model being used for this route
- `expiry_finalized`: if the session was finalized

### 8. Telegram session identification

```sql
SELECT id, session_key, chat_id, chat_type, display_name, source, started_at, end_reason
FROM sessions
WHERE source = 'telegram'
ORDER BY started_at DESC
LIMIT 20;
```

### 9. Orphan sessions (no session_key)

```sql
SELECT id, source, chat_id, chat_type, started_at, message_count
FROM sessions
WHERE session_key IS NULL OR session_key = ''
ORDER BY started_at DESC
LIMIT 15;
```

Sessions without `session_key` are orphaned — the gateway doesn't know they exist. This happens when the DB was locked at startup and the gateway fell back to JSONL storage.

### 10. Session model usage over time

```sql
SELECT * FROM session_model_usage
ORDER BY started_at DESC
LIMIT 20;
```

## Combined Diagnosis Script

Here's a complete Python script that runs all diagnostic queries at once:

```python
#!/usr/bin/env python3
import sqlite3

db = sqlite3.connect('/opt/data/state.db')
db.text_factory = str
c = db.cursor()

print("=== SESSION END REASONS ===")
c.execute("SELECT end_reason, COUNT(*) FROM sessions WHERE end_reason != '' GROUP BY end_reason ORDER BY COUNT(*) DESC")
for r in c.fetchall(): print(f"  {r[0]}: {r[1]}")

print("\n=== COMPRESSION FAILURES ===")
c.execute("SELECT id, substr(compression_failure_error,1,80), message_count FROM sessions WHERE compression_failure_error IS NOT NULL ORDER BY started_at DESC LIMIT 10")
for r in c.fetchall(): print(f"  {r[0][:14]} | err={r[1]} | msg={r[2]}")

print("\n=== LARGEST SESSIONS (top 10 by message count) ===")
c.execute("SELECT id, source, message_count, end_reason FROM sessions WHERE message_count > 0 ORDER BY message_count DESC LIMIT 10")
for r in c.fetchall(): print(f"  {r[0][:14]} | {r[1]} | {r[2]} msgs | end={r[3]}")

print("\n=== RECENT TELEGRAM SESSIONS (last 15) ===")
c.execute("SELECT id, started_at, ended_at, end_reason, message_count FROM sessions WHERE source='telegram' ORDER BY started_at DESC LIMIT 15")
for r in c.fetchall():
    end = f"ended={r[2]}" if r[2] else "ACTIVE"
    print(f"  {r[0][:14]} | started={r[1]} | {end} | reason={r[3]} | msg={r[4]}")

db.close()
```

## Key Diagnostic Pattern

When investigating session resets:

1. **Check `compression_failure_error`** — if it shows HTTP 402, the compression auxiliary model has no credits
2. **Check `end_reason` distribution** — high `session_reset` count confirms forced resets
3. **Check gateway log for `compacting context`** — if never appears, compression is either disabled or failing before logging
4. **Check config.yaml `auxiliary.compression`** — if `model: ''` and `provider: auto`, the compressor has no dedicated model
5. **Check `gateway_routing`** — if routing points to an ended session, the routing is stale (usually from DB lock at startup)

The causal chain: no compression model → compression fails (402) → fallback degraded → session grows unbounded → session force-closed (`session_reset`) → user feels "conversation reset".
