# Hermes state.db — Lookup de sessão recente quando session_search não acha

> Validação real: 13/08/2026 (Zera/CFP IA). Usuário pediu para procurar "no banco de dados mesmo"
> porque `session_search` (FTS5) não retornava a sessão mais recente. Query direta resolveu.

## Quando usar

- `session_search` não acha uma sessão que SABEMOS que existe (sessão muito recente, FTS5 não
  indexou ainda, ou o termo buscado não está no conteúdo indexado).
- Precisamos reconstruir uma conversa inteira (mensagens user/assistant/tool) sem depender do FTS.

## Banco e schema

- Banco: `/opt/data/state.db` (SQLite).
- Tabela `sessions`: `id` (TEXT, chave), `source`, `model`, `title`, `started_at` (REAL epoch),
  `last_activity_at`, `end_reason`, `message_count`, `archived`, `chat_id`, `parent_session_id`.
- Tabela `messages`: `id` (INTEGER), `session_id`, `role` (user/assistant/tool), `content`,
  `tool_calls` (JSON string), `tool_name`, `timestamp` (REAL epoch).
- Timestamps são epoch **segundos** (REAL). Converter para BRT (UTC-3) ao exibir.

## ⚠️ Pitfall principal — IDs truncados nos resultados de busca

Os IDs de sessão exibidos pelos resultados de `session_search` (e nas mensagens) são **prefixos
truncados** (~22 chars). O ID completo no banco é mais longo (ex.: `20260813_123130_dda5382b` vs
prefixo `20260813_123130_dda538`). Sempre casar com `LIKE '<prefixo>%'`, nunca com igualdade.

```python
import sqlite3, datetime
con = sqlite3.connect("/opt/data/state.db")
con.row_factory = sqlite3.Row

# 1. Listar sessões recentes (por atividade)
for r in con.execute("""
    SELECT id, title, source, started_at, last_activity_at,
           (SELECT COUNT(*) FROM messages m WHERE m.session_id = s.id) AS real_msgs
    FROM sessions s ORDER BY last_activity_at DESC LIMIT 20"""):
    ts = lambda t: datetime.datetime.fromtimestamp(t, datetime.timezone(datetime.timedelta(hours=-3))).strftime("%d/%m %H:%M") if t else ""
    print(f"- {r['id'][:22]} | {ts(r['started_at'])}→{ts(r['last_activity_at'])} | msgs={r['real_msgs']} | {(r['title'] or '')[:60]}")

# 2. Achar sessão por prefixo truncado
prefixo = "20260813_123130"
sid = con.execute("SELECT id FROM sessions WHERE id LIKE ?", (prefixo + "%",)).fetchone()[0]
print("ID completo:", sid)

# 3. Reconstruir a conversa (user/assistant/tool) em ordem
for r in con.execute("SELECT id, role, content, tool_name, timestamp FROM messages WHERE session_id=? ORDER BY id", (sid,)):
    t = ts(r["timestamp"])
    c = (r["content"] or "").strip()
    if r["role"] == "tool":
        try:
            import json
            j = json.loads(c)
            c = (j.get("output") or j.get("content") or str(j))[:150]
        except Exception:
            c = c[:150]
        print(f"[{t}] TOOL {r['tool_name']}: {c}")
    else:
        print(f"[{t}] {r['role'].upper()}: {c[:400]}")
```

## Dicas

- `sqlite3` CLI não existe no container — usar Python `sqlite3` (stdlib).
- Para descobrir sessões de "hoje": `WHERE started_at >= <epoch de 00:00 BRT>` (calcular: BRT = UTC-3,
  então 00:00 BRT de 13/08 = 13/08 03:00 UTC).
- Ferramenta `session_search` aceita `session_id` + `around_message_id` para scroll, mas para sessões
  fora do índice o scroll também falha — o caminho é a query direta.
- Procurar por conteúdo: `LIKE '%termo%'` em `messages.content` (ex.: 'quinzena 3', 'transcrição') é
  o fallback natural quando o FTS não indexou.
