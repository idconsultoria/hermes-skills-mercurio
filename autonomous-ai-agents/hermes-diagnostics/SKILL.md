---
name: hermes-diagnostics
description: "Diagnose Hermes Agent issues — session resets, context loss, compression.

Load this skill when the user reports Hermes misbehaving: conversations resetting mid-turn, context being lost, sessions ending abruptly, repeated model fallbacks, or provider errors. Covers the full diagnostic pipeline: config analysis (compression, auxiliary models, session_reset settings), gateway log inspection (fallback patterns, compression events, error signatures), state.db SQLite analysis (session lifecycle, end_reasons, compression_failures, session_key chains), compressor source-code review, provider chain analysis, and causal-chain synthesis into a concrete remediation plan."
type: Research
timestamp: 2026-07-15T08:00:00Z
---

# Hermes Diagnostics

> Metodologia sistemática para diagnosticar problemas comportamentais do Hermes Agent — sessões que resetam sozinhas, contexto perdido, compressão silenciosamente falhando, provedores caindo em cadeia, e sessões órfãs.

## Load this skill when

- ~~Usuário relata que conversas resetam "do nada" no meio do diálogo~~
- ~~Contexto é perdido ou a compressão não está funcionando~~
- ~~O gateway mostra "Switched to fallback model" repetidamente~~
- ~~Sessões terminam abruptamente sem razão aparente~~
- ~~O modelo retorna `finish_reason='error'` ou tool calls truncados~~
- ~~Precisa investigar por que uma conversa longa morre silenciosamente~~

Load this skill when investigating ANY Hermes Agent behavioral issue where the root cause isn't immediately obvious.

## Diagnostic Pipeline

### Step 1 — Check Compression Configuration

Read `/opt/data/config.yaml` (or `hermes config path` → `read_file`). Focus on the `compression:` and `auxiliary.compression:` sections.

**Key questions:**
- `compression.enabled` — is compression on?
- `compression.threshold` — when does it trigger? (default 0.75 = 75% of context)
- `compression.target_ratio` — how much to compress to? (default 0.20)
- `compression.abort_on_summary_failure` — what happens when summary fails? `false` = silent failure → degraded fallback → session death
- `compression.in_place` — in-place compression (true) vs rotation (false)
- `auxiliary.compression.provider` — WHICH model does compression use?
- `auxiliary.compression.model` — is a specific model configured, or is it empty?

**Most common root cause:** `auxiliary.compression.provider: auto` with `model: ''` — no dedicated compression model. The `auto` provider tries the primary provider chain, which hits HTTP 402/429 (credits exhausted / rate limited). Compression fails silently, context grows unbounded, session is force-terminated with `end_reason=session_reset`.

**Fix:** Pin a free/cheap model explicitly:
```yaml
auxiliary:
  compression:
    provider: gemini          # or openrouter with a cheap model
    model: gemini-flash-lite-latest
    timeout: 120
```

Also check `compression.abort_on_summary_failure`. When `false` (default), a failed summary creates a degraded fallback that pollutes the context. Set to `true` if you'd rather crash loudly than corrupt silently.

### Step 2 — Check session_reset Configuration

In config.yaml, look at `session_reset:`:
```yaml
session_reset:
  at_hour: 4          # Hour of day for scheduled reset
  idle_minutes: 1440  # Idle time before reset (1440 = 24h)
  mode: none          # none | scheduled | idle | both
```

If `mode` is `none`, no automatic reset is configured. But the state.db may still show `session_reset` as an end_reason — this comes from internal session handling, not the auto-reset feature.

### Step 3 — Read Gateway Logs

Gateway logs live at `/opt/data/logs/gateways/default/current` (or `~/.hermes/logs/gateway.log`). Read with:
```
cat /opt/data/logs/gateways/default/current
```

**Patterns to look for:**

| Log pattern | Indicates |
|---|---|
| `⟳ compacting context…` / `🗜️ Compacting context` | Compression fired — check frequency |
| `📦 Preflight compression: ~N tokens >= threshold` | Context near ceiling; pre-call compression about to run — note the token count (huge counts here → hygiene timeouts likely, see Step 8) |
| `Switched to fallback model: A → B` | Primary provider failing — note the source and target models |
| `⚡ Interrupted during API call.` | API timeout or crash — often context-length related |
| `⚠️ Truncated tool call arguments (finish_reason='error')` | Model output was cut off — context too large or provider error |
| `database is locked` | SQLite contention — session store degraded to JSONL |
| `Error code: 402` | Credits exhausted for the auxiliary model |
| `Quota exceeded` / `rate limit` | Provider hitting API limits |

**Frequency analysis:** if fallback switching happens multiple times per minute, the provider chain is fundamentally unstable.

### Step 4 — Query state.db for Session Lifecycle Analysis

The state database at `/opt/data/state.db` (or `~/.hermes/state.db`) contains full session lifecycle data. Use Python (sqlite3) to query it.

**Key tables:**
- `sessions` — session metadata, lifecycle, end_reasons, compression failures
- `messages` — individual messages (for session depth analysis)
- `gateway_routing` — which session the gateway routes to per chat
- `compression_locks` — compression contention records

**Essential queries:**

```python
import sqlite3
db = sqlite3.connect('/opt/data/state.db')

# 1. Sessions by end_reason — see what kills sessions
c.execute("SELECT end_reason, COUNT(*) FROM sessions WHERE end_reason != '' GROUP BY end_reason ORDER BY COUNT(*) DESC")
for r in c.fetchall(): print(f"  {r[0]}: {r[1]}")

# 2. Recent sessions with reasons
c.execute("""
    SELECT id, title, source, started_at, ended_at, end_reason, message_count
    FROM sessions ORDER BY started_at DESC LIMIT 20
""")

# 3. Sessions with compression failures
c.execute("""
    SELECT id, title, source, compression_failure_error, message_count
    FROM sessions WHERE compression_failure_error IS NOT NULL
    ORDER BY started_at DESC LIMIT 10
""")

# 4. Session chain for a specific user/chat (trace resets)
c.execute("""
    SELECT id, source, started_at, end_reason, message_count, session_key
    FROM sessions WHERE session_key = '<key>'
    ORDER BY started_at
""")

# 5. Highest message counts (sessions that grew large before dying)
c.execute("""
    SELECT id, title, source, message_count, end_reason
    FROM sessions ORDER BY message_count DESC LIMIT 10
""")
```

**Critical fields in sessions table:**
- `end_reason` — why session ended (`session_reset`, `agent_close`, `ws_orphan_reap`, `compression`, `cron_complete`)
- `compression_failure_error` — error message from last failed compression
- `compression_failure_cooldown_until` — timestamp of cooldown after failure
- `session_key` — routing key that links sessions for the same chat (e.g. `agent:main:telegram:dm:6171996969`)
- `parent_session_id` — parent session reference (compression rotation creates child sessions)
- `message_count` — how many messages in the session
- `handoff_state` / `handoff_error` — handoff data (often empty on abrupt resets)

**Diagnostic pattern:** If `session_reset` sessions have `compression_failure_error` with HTTP 402, the chain is: compression fails → fallback degraded → session force-closed → new session created = user feels "reset".

### Step 5 — Check Gateway Routing

Query `gateway_routing` table to see which session the gateway currently routes to:
```sql
SELECT * FROM gateway_routing LIMIT 10
```

The routing JSON contains `session_id`, `was_auto_reset`, `auto_reset_reason`, and `model_override`. If the routing points to an ended session, the routing is stale — the gateway lost track.

### Step 6 — Review Compressor Source Code

The context compressor lives at `agent/context_compressor.py` in the Hermes source (usually `/opt/hermes/hermes-agent/agent/context_compressor.py` or fetch from GitHub raw).

**Key behaviors to verify:**
- `_SUMMARY_FAILURE_COOLDOWN_SECONDS = 600` — compressor waits 10 min after a failure
- `abort_on_summary_failure: false` → compressor creates a **fallback summary** (last N turns verbatim) when LLM summarization fails
- The fallback summary can be poor quality, causing the model to lose context or misbehave
- `hygiene_hard_message_limit: 400` — absolute ceiling on messages before forced action
- When multiple compression failures accumulate, the session is eventually terminated with `session_reset`

### Step 7 — Provider Chain Analysis

Check the fallback chain in config.yaml:
```yaml
fallback_providers:
  - base_url: https://opencode.ai/zen/v1
    model: deepseek-v4-flash-free
    provider: opencode-zen
  - base_url: https://opencode.ai/zen/go/v1
    model: deepseek-v4-flash
    provider: opencode-go
```

Cross-reference with gateway logs showing `Switched to fallback model`. If the primary provider fails on large contexts (common with free-tier models that have low context limits or aggressive rate limiting), every long conversation will eventually hit:
1. Large context → primary model timeout/crash
2. Fallback fires → fallback model has even smaller context → fails faster
3. Chain completes → session dies

**Fix:** Either (a) use a provider with reliable large-context support, (b) compress earlier (lower `threshold`), or (c) configure a dedicated compression model so compression works before the context gets too large.

#### Diagnóstico de falha em cadeia de fallbacks

Quando a sessão atual **não corresponde** ao modelo primário configurado (verificar header `Model: X / Provider: Y` no início da sessão), significa que os primeiros N fallbacks falharam. Onde a sessão aterrissou indica onde a cadeia quebrou.

**Padrão 1 — `opencode-zen` primário cai direto para `opencode-go`**

Sintoma: `model.default: mimo-v2.5-free` com `model.provider: opencode-zen`, mas a sessão roda `deepseek-v4-flash` via `opencode-go`.

Causa raiz mais provável: **base_url built-in do `opencode-zen` está errada**. O Hermes tem um bug conhecido ([#11661](https://github.com/NousResearch/hermes-agent/issues/11661)): a URL padrão é `https://api.opencode-zen.com/v1` (não resolve), quando deveria ser `https://opencode.ai/zen/v1`.

Verificação:
```bash
grep -A5 '^model:' /opt/data/config.yaml
```
Se `base_url` não estiver presente ou estiver `api.opencode-zen.com`, este é o problema.

Correção:
```yaml
model:
  default: <model>
  provider: opencode-zen
  base_url: https://opencode.ai/zen/v1
  api_mode: chat_completions
```

Ou descomentar `OPENCODE_ZEN_BASE_URL=https://opencode.ai/zen/v1` no `.env`.

**Padrão 2 — Fallback com modelo específico falha silenciosamente**

Sintoma: fallback usa `model: deepseek-v4-flash-free` mas a cadeia pula para o próximo.

Causa raiz: **`model.aliases` pode estar mapeando o nome do modelo de fallback para outro modelo**. Alias como `deepseek-v4-flash-free: deepseek-v4-pro` faz o fallback resolver para o modelo errado.

Verificação:
```bash
grep -A2 'aliases' /opt/data/config.yaml
```

Se um alias tem o mesmo nome de um modelo real usado nos fallbacks, removê-lo ou mudar a chave do alias.

**Padrão 3 — Fallback usa `opencode-zen` mas só `opencode-go` funciona**

Sintoma: fallbacks com `provider: opencode-zen` falham, mas `provider: opencode-go` funciona.

Verificar:
1. Se `OPENCODE_ZEN_API_KEY` está setada no `.env` (e não expirada)
2. Se `base_url` do fallback está explícita e correta (`https://opencode.ai/zen/v1`)
3. Se o modelo existe no catálogo Zen (`GET https://opencode.ai/zen/v1/models`)
4. Se o alias não está interferindo (ver Padrão 2)

**Fix:** Either (a) use a provider with reliable large-context support, (b) compress earlier (lower `threshold`), or (c) configure a dedicated compression model so compression works before the context gets too large.

### Step 8 — Gateway Hygiene Commit-Fence Timeout (empty "auto-compress failed")

Signature in errors.log (the error text is EMPTY — that is the expected signature, not a missing log):

```
WARNING gateway.run: Session hygiene compression for session X made no progress for 30.0s (total wait 41.5s, ceiling 600.0s); continuing without compression
WARNING gateway.run: Session hygiene auto-compress failed:
```

What it means: gateway hygiene spawned a fresh AIAgent to compress; the commit fence aborts when the worker shows no progress for `_hyg_timeout_seconds = 30.0` (gateway/run.py, overridable via `compression.hygiene_timeout_seconds`; ceiling `_hyg_total_ceiling_seconds = 600.0`). The empty error is a re-raised `asyncio.TimeoutError` — `str()` is `""`, so don't hunt for missing error text. Typical trigger chain:

1. Session at/over `compression.hygiene_hard_message_limit` (e.g. 1000) → hygiene fires on EVERY new message → stress loop
2. Context is huge (100K–700K tokens; check `sessions.message_count` vs `messages` rows where `active=1`)
3. Aux summary model (e.g. gemini-flash-lite-latest) takes >30s to first token → fence aborts
4. User receives "⚠️ Context compression timed out after 30.0s with no output from the summary model"

Verify in agent.log, NOT state.db (state.db may show `compression_failure_error` NULL — the cooldown record is gated on `compression.hygiene_failure_cooldown_seconds >= 0`):

```
INFO agent.conversation_compression: context compression started: session=X messages=1025 tokens=~308,557 model=<main> focus=None
INFO agent.auxiliary_client: Auxiliary compression: using gemini (gemini-flash-lite-latest) ...
INFO agent.conversation_compression: context compression attempt telemetry: {... "commit_status":"aborted","failure_class":"commit_fence_cancelled","total_duration_ms":40953}
```

Successes look like `"commit_status":"committed","split_status":"in_place_committed"` + `context compression done: messages=N->M`. A session can interleave successes (8s–70s) and timeouts — aux-model latency is the variable, not a broken provider.

Fix ladder:
1. `hermes config set compression.hygiene_timeout_seconds 120` — give the summary model room on large contexts
2. `hermes config set compression.hygiene_hard_message_limit 1500` — reduce firing frequency (or lower it to compress earlier)
3. `/reset` sessions with 20K+ message rows / millions of input tokens — history stays in session_search
4. Faster aux compression model (e.g. gemini-2.5-flash over flash-lite at scale)

Full worked case + code line numbers + query recipe: `references/gateway-hygiene-timeout.md`.

### Step 9 — Shallow Compression ("comprimiu muito pouco")

Symptom: compression now COMMITS (timeout fixed) but barely reduces anything — e.g. `messages=1047->978` (69 msgs) and `rough_tokens=~323,300 -> ~306,946` (5%). User asks "por que comprimiu tão pouco?".

Root causes, in the order to check:

1. **Hygiene fired on MESSAGE COUNT, not tokens.** The hygiene log line names the trigger: `Session hygiene: 1025 messages, ~308,557 tokens — auto-compressing (threshold: 85% of 1,000,000 = 850,000 tokens)`. If tokens are far below the token threshold but msgs >= `hygiene_hard_message_limit`, the compress has no token pressure → shallow cut. It only needs to drop the count back under the limit.
2. **In-place compaction is incremental.** `split_status: in_place_committed` absorbs only the span between the previous `[CONTEXT COMPACTION]` marker and the new cut — it does NOT re-compact the whole session. Sessions compacted many times (29 markers seen) have a head that is already summary-of-summary: little dense material left to squeeze.
3. **Tail protection limits the cut.** `protect_last_n: 15` + `_ensure_last_user_message_in_tail` + tool-group alignment: bulky recent tool outputs (10K+ tokens each) exhaust the tail token budget (`threshold_tokens * summary_target_ratio`, ~130K) fast, so the cut lands near the head and absorbs only small old messages.

**Pathology flags in state.db** (session is a lost cause, recommend `/reset`):
- 20K+ message rows, `compacted=1` on 95%+ of rows, 20+ `CONTEXT COMPACTION` markers
- Duplicate message rows: same content, different ids (query `GROUP BY role, content HAVING cnt > 1`) — a symptom of repeated in-place rewrites
- `message_count` oscillating around `hygiene_hard_message_limit` across days

**Vicious cycle:** grows to ~1040 msgs → hygiene compresses shallow (count-only relief) → grows again. The token threshold (850K) is so far away that hygiene never cuts deep.

**Recommendation:** `/reset` the session — history remains in session_search. Raising `hygiene_hard_message_limit` only reduces trigger frequency, it does not make cuts deeper. Verify expectations: on an already-29x-compacted session, a 5% token reduction IS the designed behavior of in-place compaction; do not call it a bug.

Full worked case: `references/shallow-compression.md` (log lines, queries, duplicate-marker measurements).

## Common Diagnoses

| Symptom | Most Likely Root Cause | Fix |
|---|---|---|
| Session resets mid-conversation | No dedicated compression model → compression fails (402) → session_reset | Pin `auxiliary.compression.model` |
| Repeated "Switched to fallback" | Primary provider unstable with large contexts | Lower compression threshold, fix provider |
| "Compacting context" never appears in logs | Compression disabled OR auxiliary model failing silently | Check `compression.enabled` and `auxiliary.compression` config |
| SQLite database is locked | Multiple gateway processes or long write operations | Restart gateway, add WAL mode |
| finish_reason='error' with truncated tool calls | Context too large for model's output window | Lower `compression.threshold`, compress earlier |
| Session ends with `ws_orphan_reap` | Gateway restart left websocket sessions orphaned | Normal cleanup; check gateway stability |
| `auto-compress failed:` with EMPTY error + `made no progress for 30.0s` | Gateway hygiene commit-fence timeout — aux summary model too slow on a huge context (session over `hygiene_hard_message_limit`) | Raise `compression.hygiene_timeout_seconds`, raise `hygiene_hard_message_limit`, `/reset` giant sessions; see Step 8 |
| Compression commits but reduces little (e.g. 1047→978 msgs, 5% tokens) | Hygiene fired on message count while tokens far below threshold; in-place compaction is incremental (marker-to-marker); tail protection + huge recent tool outputs cap the cut | Check the hygiene trigger line (msgs vs token threshold); `/reset` sessions with 20K+ rows / 20+ compaction markers; see Step 9 |
| Sessão cai em fallback inesperado | `opencode-zen` base_url built-in errada OU `model.aliases` interferindo | Verificar base_url do model section + model.aliases |

## Remediation Sequence

1. **Pin compression model** (solves ~80% of session-reset cases)
2. **Lower threshold** to 0.60-0.65 (compress earlier, when context is smaller)
3. **Set abort_on_summary_failure: true** (fail loudly instead of corrupting context)
4. **Verify provider stability** — if primary provider keeps falling back, evaluate alternatives
5. **Check gateway routing** — ensure routing points to an active session
6. **Consider WAL mode** for state.db to reduce lock contention

## Related

- `hermes-agent` skill — general Hermes setup and configuration (bundled, read-only)
- `messaging-platforms` — cross-platform message delivery diagnostics
- `references/config-change-protocol.md` — protocol for modifying Hermes config: never change provider/model/compression without explicit user instruction
- `references/dashboard-auth-env-override.md` — dashboard login failing with `Invalid username or password` despite correct `dashboard.basic_auth` in config.yaml: env-over-config precedence in the basic_auth plugin, verification via `/auth/password-login` curl, fixing without dropping the gateway
- `pi-session-audit` — Pi Agent session cost/token auditing (related methodology)

## Pitfalls

⚠️ **Compression failure ≠ crash.** With `abort_on_summary_failure: false`, the compressor silently creates a degraded fallback. The session continues but loses quality. Only after repeated failures does the session die with `session_reset`. Don't expect crash logs — look for `compression_failure_error` in state.db.

⚠️ **Gateway logs may be truncated.** The s6 logger rotates files. If `current` is small, check archived logs: `ls -la /opt/data/logs/gateways/default/` and read the `.u` files (uncompressed).

⚠️ **state.db can be 800MB+.** The full messages table is indexed by FTS5. Queries scanning the messages table without a session filter can be slow. Always filter by `session_id` when possible.

⚠️ **session_key=None in some rows.** Sessions created without a gateway routing context (e.g. after DB lock at startup) may have `session_key = NULL`. These are "orphan" sessions — they won't appear in the routing chain. Use `chat_id` and `source` to correlate instead.

⚠️ **Multiple ACTIVE sessions for the same chat.** If the gateway routing is stale, new messages may create new sessions while the old one is still marked ACTIVE. Check `gateway_routing` for the authoritative current session.

⚠️ **session_reset reason has no handoff data.** The `session_reset` end_reason is set without populating `handoff_state` or `handoff_error`, making it hard to trace the exact trigger from the database alone. Cross-reference with gateway log timestamps near the session's `ended_at`.

⚠️ **Provider fallback can cascade silently.** The fallback chain may complete (all providers tried) without any final error surfacing to the user. The session just dies. Check logs for the last provider in the chain failing.

⚠️ **"auto-compress failed:" with empty message ≠ unknown error.** In the gateway hygiene path, an empty error string after `auto-compress failed:` is the re-raised `asyncio.TimeoutError` (`str() == ""`) from the commit fence — it means the summary model produced no output within `hygiene_timeout_seconds` (default 30.0s). Don't chase the missing error text; confirm via agent.log telemetry `"failure_class":"commit_fence_cancelled"` (see Step 8).

⚠️ **state.db `compression_failure_error` may stay NULL even when compression fails.** Hygiene commit-fence timeouts record the cooldown only when `compression.hygiene_failure_cooldown_seconds >= 0`; otherwise the failure exists solely in errors.log/agent.log. Always cross-check logs, not just the DB columns.
