# Gateway Hygiene Commit-Fence Timeout — worked case

Caso real (2026-08-12): sessão Telegram `20260810_221657_10d46263` (projeto CFP,
ativa há 2 dias) com compactação falhando em loop. Este arquivo é o caso
completo — log lines, código, queries — para o padrão do Step 8 da SKILL.md.

## Sintoma reportado pelo usuário

"Compressão de contexto na minha última sessão ativa do Telegram falhou."

## Linha do tempo observada (gateway log + errors.log)

```
2026-08-11 20:51:04.140  📦 Preflight compression: ~684,280 tokens >= 650,000 threshold.
2026-08-11 20:51:04.165  🗜️ Compacting context — summarizing earlier conversation...
2026-08-12 02:52:32,252 WARNING gateway.run: Session hygiene compression for session
    20260810_221657_10d46263 made no progress for 30.0s (total wait 41.5s, ceiling
    600.0s); continuing without compression
2026-08-12 02:52:32,798 WARNING gateway.run: Session hygiene auto-compress failed:
2026-08-12 03:23:53,058 WARNING gateway.run: Session hygiene compression for session
    20260810_221657_10d46263 made no progress for 30.0s (total wait 30.1s, ceiling
    600.0s); continuing without compression
2026-08-12 03:23:53,624 WARNING gateway.run: Session hygiene auto-compress failed:
```

Duas falhas idênticas em ~30 min. Entre elas, compactações que PASSARAM
(02:57 em 13.4s, 03:12 em 8.8s, 03:18 em 69.3s com waits estendidos) — prova de
que o provider NÃO estava quebrado; a latência do modelo auxiliar é a variável.

## Por que aconteceu (cadeia causal)

1. `compression.hygiene_hard_message_limit: 1000` no config.yaml; a sessão tinha
   **1047 mensagens ativas** (`active=1`) — acima do limite.
2. Hygiene dispara em **toda mensagem nova** quando a sessão está acima do limite.
3. Contexto enorme: cada turno envia ~300K tokens de input
   (`in=293K–307K` nos API calls), 8.3M tokens acumulados, 1.455 API calls.
4. Modelo de sumarização `gemini-flash-lite-latest` (auxiliary.compression,
   provider gemini) demora >30s para o primeiro token com 300K+ tokens.
5. Fence do gateway aborta aos 30s sem progresso (`_hyg_timeout_seconds = 30.0`
   default, NÃO sobrescrito no config → loop de falhas).

## Assinaturas no agent.log (a fonte autoritativa)

```
INFO agent.conversation_compression: context compression started:
    session=20260810_221657_10d46263 messages=1025 tokens=~308,557 model=deepseek-v4-flash focus=None
INFO agent.auxiliary_client: Auxiliary compression: using gemini (gemini-flash-lite-latest)
    at https://generativelanguage.googleapis.com/v1beta
INFO agent.conversation_compression: context compression attempt telemetry:
    {"attempt_id":"...","chunk_count":0,"chunking":false,"commit_status":"aborted",
     "event":"compression_attempt","failure_class":"commit_fence_cancelled",
     "fallback_used":false,"session_id":"20260810_221657_10d46263",
     "split_status":"aborted","total_duration_ms":40953}
```

Sucesso (para comparação):

```
INFO agent.conversation_compression: context compression done:
    session=... messages=1221->1037 rough_tokens=~311,147 awaiting_real_usage=true
INFO agent.conversation_compression: context compression attempt telemetry:
    {"commit_status":"committed","split_status":"in_place_committed","total_duration_ms":13447}
```

## Código relevante (gateway/run.py)

- `_hyg_timeout_seconds = 30.0` (default, linha ~17132) — quanto tempo o fence
  tolera sem progresso antes de abortar.
- `_hyg_total_ceiling_seconds = 600.0` (linha ~17133) — teto absoluto de espera.
- Override via config: `compression.hygiene_timeout_seconds` /
  `compression.hygiene_timeout_ceiling_seconds` (lido em `_comp_cfg.get(...)`, ~17180).
- Timeout → envia ao usuário "⚠️ Context compression timed out after 30.0s with
  no output from the summary model" (linha ~17571) → re-raise (`raise` vazio,
  linha ~17594) → o `except Exception as e` de fora loga
  `Session hygiene auto-compress failed: %s` com `e = TimeoutError` → string vazia.
- Cooldown persistido SÓ se `_hyg_failure_cooldown_seconds >= 0` (linha ~17540) —
  caso contrário `compression_failure_error`/`compression_failure_cooldown_until`
  ficam NULL na state.db mesmo com falha.

## Queries usadas no diagnóstico

```python
import sqlite3, datetime
db = sqlite3.connect('/opt/data/state.db')
c = db.cursor()
sid = '20260810_221657_10d46263'

# Sessões telegram recentes (achar a ativa)
c.execute("""SELECT id, title, source, started_at, ended_at, end_reason,
             message_count, compression_failure_error
             FROM sessions WHERE source LIKE '%telegram%'
             ORDER BY started_at DESC LIMIT 10""")

# Campos de compressão da sessão
c.execute("""SELECT compression_failure_cooldown_until, compression_failure_error,
             compression_fallback_streak, compression_ineffective_count,
             message_count, api_call_count, input_tokens
             FROM sessions WHERE id=?""", (sid,))

# Mensagens ativas vs total (sessão acima do hygiene_hard_message_limit?)
c.execute("SELECT COUNT(*) FROM messages WHERE session_id=? AND active=1", (sid,))

# Markers de compactação bem-sucedida
c.execute("""SELECT id, timestamp FROM messages
             WHERE session_id=? AND content LIKE '%CONTEXT COMPACTION%'
             ORDER BY id""", (sid,))
```

## Verificação de que o provider auxiliar está saudável

A chave Google funciona e o modelo existe (não é problema de credencial):

```python
import json, urllib.request
key = open('/opt/data/.env').read().split('GOOGLE_API_KEY=')[1].splitlines()[0].strip()
url = 'https://generativelanguage.googleapis.com/v1beta/models?key=' + key
data = json.load(urllib.request.urlopen(url, timeout=15))
print([m['name'] for m in data['models'] if 'flash' in m['name'].lower()])
# → 'models/gemini-flash-lite-latest' presente
```

## Remediação aplicada/recomendada

1. `hermes config set compression.hygiene_timeout_seconds 120`
2. `hermes config set compression.hygiene_hard_message_limit 1500`
3. `/reset` na sessão gigante (histórico preservado em session_search)
4. Opcional: modelo de compressão mais rápido (gemini-2.5-flash)

⚠️ Nunca aplicar mudanças de config sem instrução explícita do usuário —
ver `references/config-change-protocol.md`.
