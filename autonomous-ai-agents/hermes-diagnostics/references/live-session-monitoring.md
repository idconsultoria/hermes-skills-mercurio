# Monitorar sessão ao vivo — "tem outra sessão sua rodando, me atualize"

> Padrão validado em 14/08/2026 (usuário pediu acompanhar sessão que produzia skill
> `elaboracao-proposta-comercial`). Roteiro para responder "o que a outra sessão está
> fazendo AGORA" e decidir se ainda está trabalhando ou já terminou.

## Roteiro

1. **Achar as candidatas em execução:**
   ```bash
   ps aux | grep -E "hermes|pi" | grep -v grep
   ```
   - TUI do Hermes = processo `hermes` (CLI). Jobs Pi em background = `pi` + espectadores `pi_follow_tui.mjs`.
   - Não confie em `ps` sozinho: TUI fica em `ep_poll` esperando input mesmo DEPOIS de terminar o trabalho.

2. **Listar sessões abertas no state.db:**
   ```python
   import sqlite3, datetime, time
   con = sqlite3.connect('/opt/data/state.db')
   cur = con.cursor()
   rows = cur.execute("""
       SELECT id, source, title, last_activity_at, message_count
       FROM sessions
       WHERE ended_at IS NULL AND last_activity_at > ?
       ORDER BY last_activity_at DESC""", (time.time() - 3*3600,)).fetchall()
   # `ended_at IS NULL` NÃO é prova de atividade — cruzar com last_activity_at.
   ```

3. **Ler o fluxo recente da sessão candidata** (o que ela fez no último minuto):
   ```python
   rows = cur.execute("""
       SELECT role, content, timestamp, tool_name FROM messages
       WHERE session_id = ? ORDER BY id DESC LIMIT 10""", (SID,)).fetchall()
   # role=tool + tool_name + content (JSON) mostram o passo atual.
   # Ex.: tool_name='skill_manage' + content com 'Patched...' = skill sendo editada AGORA.
   ```

4. **Decidir ativo vs concluído:**
   - Ativa = `last_activity_at` recente (segundos/minutos) E novas mensagens continuam entrando.
   - Concluída = última mensagem antiga e nada novo entrando — mesmo com `ended_at IS NULL` e processo vivo. Reporte o resultado final (ex.: "skill pronta, zip enviado msg_id X") em vez de montar monitor.

5. **Sessões Pi NÃO estão no state.db.** O fluxo delas vive no JSONL:
   `~/.pi/agent/sessions/--<cwd-normalizado>--/<timestamp>_<uuid>.jsonl`
   — eventos `session` / `session_info` (nome via `--name`) / `message` com conteúdo aninhado em `message.message.content[]`. Schema completo e resumo de monitoramento: skill `pi-agent-internals` → `references/pi-internals-anatomy.md` § Sessões.

## Pegadinhas

⚠️ **Processo vivo ≠ sessão trabalhando.** TUI em `ep_poll` + `ended_at IS NULL` ainda podem significar "trabalho acabou". A verdade está nos timestamps das mensagens.

⚠️ **Mesmo trabalho pode ter dois donos.** Ex.: skill construída numa TUI (`source=tui`) enquanto outra sessão (`source=telegram`) apenas monitora um job Pi que executa code-tasks. Para "qual sessão produz X", leia o conteúdo das tool calls, não só o `source`.

⚠️ **Nome da sessão Pi fica em `session_info`, não no filename.** O JSONL `2026-08-14T06-44-59-651Z_<uuid>.jsonl` não diz o nome; o segundo evento (`"type":"session_info","name":"zera-onda5-lote2"`) tem.

⚠️ **`toolResult.content` pode ser lista** de `{"type":"text","text":...}` — não assumir string no parse (primeira tentativa falha silenciosamente).
