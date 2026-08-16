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

### 11. Content-based session lookup (session_search FTS fallback)

When the user asks "which session did we talk about X" and `session_search` returns 0 results — even with exact quoted phrases or a distinctive string like a messageId — do NOT conclude it doesn't exist. The FTS5 index (`messages_fts`) misses content that the raw `messages` table has (notably strings embedded in tool-output JSON, and sometimes exact phrases). The raw LIKE query finds it instantly:

```python
import sqlite3
# mode=ro: NEVER open the live 1.5GB gateway DB read-write from a probe script.
con = sqlite3.connect('file:/opt/data/state.db?mode=ro', uri=True)
cur = con.cursor()

# Try the most distinctive needles: messageIds, exact quoted phrases,
# script names, unique error text. One LIKE hit is enough to locate the session.
needles = ['<messageId-or-unique-phrase>', '<another-distinctive-string>']
for needle in needles:
    cur.execute(
        "SELECT session_id, id, role, substr(content,1,200) FROM messages WHERE content LIKE ? LIMIT 5",
        (f'%{needle}%',)
    )
    for r in cur.fetchall():
        print(r)

# Confirm session identity + title once a session_id is found:
cur.execute("SELECT id, title, source, started_at FROM sessions WHERE id = ?", ('<session_id>',))
print(cur.fetchone())
```

### 11b. Full-column deep scan (when content-only LIKE fails)

If `content` LIKE returns only your own investigation messages (self-noise) or nothing, the needle lives in a column FTS never indexes. The `messages` table has SIX text-bearing columns besides `content` — `tool_calls` (JSON of function-call arguments, including full file contents passed to `write_file`), `reasoning`, `reasoning_content`, `reasoning_details`, `codex_reasoning_items`, `codex_message_items`. Scan them all, exclude the current session, and group by session to triage:

```python
import sqlite3
con = sqlite3.connect('file:/opt/data/state.db?mode=ro', uri=True)
cur = con.cursor()

NEEDLE = '%rio de janeiro%'  # any distinctive substring
CURRENT_SESSION = '<the-session-id-you-are-running-in>'  # never trust its own hits

for col in ['content', 'tool_calls', 'reasoning', 'reasoning_content',
            'reasoning_details', 'codex_reasoning_items', 'codex_message_items']:
    rows = cur.execute(f"""
        SELECT m.session_id, COUNT(*) FROM messages m
        WHERE lower(m.{col}) LIKE ? AND m.session_id != ?
        GROUP BY m.session_id ORDER BY COUNT(*) DESC LIMIT 10
    """, (NEEDLE, CURRENT_SESSION)).fetchall()
    print(f'=== {col}: {len(rows)} sessions')
    for r in rows:
        print('  ', r[0][:40], r[1], 'msgs')
```

Triage rules:
- **Filter self-noise**: your own session contains every needle you searched (assistant + tool rows echo your queries). Always exclude the current `session_id`.
- **Group before reading**: `GROUP BY session_id` gives the session map in one pass — read individual messages only after a candidate session emerges.
- **Heavy DB, be polite**: `state.db` is ~1.5GB. Always filter by `session_id` when you already have a candidate; use `mode=ro`; add `timeout` to long scans.

### 11c. Corroborate with artifact state (which session = where we stopped)

A recall request ("where did we stop", "which session created X") is only answered by matching DB hits to ON-DISK artifacts. Cross-check in this order:

1. **Cron jobs**: `/opt/data/cron/jobs.json` — job `id`, `created_at`, `last_run_at`, `script`, `prompt` identify which session created/edited a cron. (Worked case: job `e962f5a06576` "Zera — Lembrete Demandas Igor" was created 2026-08-13 14:04 UTC → its builder session is that day's window.)
2. **Git state of the project repo**: `git log --oneline -8` + `git status` — the HEAD commit timestamp is the last thing done in that workstream. (Worked case: HEAD `225839a` at 19:26 UTC dated the last CFP/Zera work.)
3. **Pi agent session JSONL**: `/opt/data/home/.pi/agent/sessions/--<workspace-normalizado>--/*.jsonl` sorted by mtime — the newest file is the last thing the Pi did in that workspace. The `Entries: N` line count is a checkpoint marker for long builds (monitor growth: 153 → 202 = progress).
4. **Script/file mtimes**: `stat` on `/opt/data/scripts/*.py`, cron `output/` artifacts (e.g. `cfp_guia_demandas.pdf`).

If no DB hit matches the user's description after all scans — **do not guess**. Report the candidates found, state that the exact pattern is absent, and ask which part to continue (user rule: "padrão exato ausente = avisar e NÃO executar").

Notes:
- The `messages` table keeps content for ALL roles (`user`, `assistant`, `tool`) — tool rows store output as JSON-escaped text, which FTS often misses but LIKE matches.
- `session_search` FTS and `content`-only LIKE both miss strings that live ONLY in `tool_calls` arguments (e.g. a document body passed to `write_file`) or in `reasoning*` columns — that is what § 11b scans for.
- Corroborate timing to narrow the target: cron job creation (`cronjob action=list` → `last_run_at`/state), script mtimes (`stat` on `/opt/data/scripts/…`), file ctimes. If the artifact was created today at 14:27 UTC, expect the session in today's window.
- `sqlite3` CLI may not exist on the host; Python's stdlib `sqlite3` always works.
- Worked case (2026-08-13): user asked for the session that created the "Zera — Lembrete Demandas Igor" cron. session_search returned 0 across ~10 query variants including the literal messageId `3EB0BE3D83318C47BA80E4`; one LIKE on the messageId in `messages.content` resolved `20260813_123130_dda5382b` immediately.
- Worked case (2026-08-13, deep scan): user asked to resume "where we stopped" on the CFP/Zera project, naming a number that matched nothing in `content`. Content-only LIKE across the DB surfaced only the probe's own messages; the real anchor (`Entries: 153` — Pi session JSONL entry count during the WS4 API build) was found in a `tool` row and confirmed against Pi session mtimes + `git log`. The user then corrected the anchor description twice ("só no banco de dados", "esqueça o Rio") — treat vague recall descriptors as unreliable; trust the DB + artifacts, then ASK.

### 12. Direct-DB fast path when the user says "look in the database, not the tool"

When the user explicitly says a session exists but `session_search` can't find it (or you get a *plausible-looking but wrong* session — FTS matched generic terms while the real session uses different wording), go straight to the DB. The user's descriptor may differ from the transcript's actual words (worked case: user said "quinzena 3", FTS returned the quinzena-2 session because both contain "transcrição"/"roadmap").

1. **Use the RIGHT database file.** `/opt/data/state.db` is the live session DB. `~/.hermes/state.db` (= `/opt/data/home/.hermes/state.db`) can exist with **zero tables** — don't get fooled by its presence; check `.tables` first.
2. **Narrow by date window first.** For "a session from today": `WHERE m.timestamp >= <day_start_utc>` (13/08 BRT 00:00 = 13/08 03:00 UTC). Combined with distinctive terms this cuts a 1.5GB table down to nothing fast.
3. **The session ID shown by `session_search` is TRUNCATED.** Displayed IDs are ~22-char prefixes (e.g. `20260813_123130_dda538`); `messages.session_id` and `sessions.id` store the FULL id (`20260813_123130_dda5382b`). An exact-match `WHERE session_id = '<truncated>'` returns 0 rows and looks like a dead end. Resolve with `SELECT id FROM sessions WHERE id LIKE '<prefix>%'` before querying messages.
4. **No sqlite3 CLI?** Python's stdlib `sqlite3` always works (`import sqlite3; con = sqlite3.connect('/opt/data/state.db')`). `sqlite3` shell may be missing on the host.
5. **Answer "where did it stop" from session metadata, not message tail alone.** After dumping the last messages, read `sessions.ended_at`, `end_reason` (`session_reset` = reset later, not interrupted mid-task; `agent_close` = natural end), and `last_activity_at` (real last touch — can be hours before `ended_at`). A session that ended `session_reset` with a complete final assistant message finished its work; only a truncated/erroring tail indicates an interruption.

### 13. Full-session read for recall ("give me the summary of what that session did")

Once the full session ID is known, dump the whole flow ordered by `id` and collapse `tool` rows to their `output`/`content` first 150–200 chars:

```python
import sqlite3, datetime, json
con = sqlite3.connect("file:/opt/data/state.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
def ts(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M")
rows = con.execute("SELECT id, role, content, tool_name, timestamp FROM messages WHERE session_id=? ORDER BY id", (FULL_SID,)).fetchall()
for r in rows:
    c = (r['content'] or "").strip()
    if r['role'] == 'tool':
        try:
            j = json.loads(c); c = (j.get('output') or j.get('content') or str(j))[:200]
        except Exception: c = c[:200]
        print(f"[{ts(r['timestamp'])}] TOOL {r['tool_name']}: {c}")
    else:
        print(f"[{ts(r['timestamp'])}] {r['role'].upper()}: {c[:500]}")
```

Timestamps are REAL unix epoch; convert to BRT (UTC-3) for display. Tool rows store JSON-escaped output — `json.loads` before truncating. Read `sessions` meta (see § 12.5) to frame the tail.

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
