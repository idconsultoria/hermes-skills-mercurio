# Sending individual / multiple messages via the `hermes send` CLI

## When to use

The agent's single final response becomes **ONE** message on the platform. If the user
wants several **distinct** messages (e.g. "manda 5 histórias como mensagens separadas",
or "me manda cada item numa mensagem"), a normal reply can't split into N. Use the
gateway's `send` CLI, which reuses platform credentials — **no LLM, no agent loop**.

## Usage

```bash
# Target forms: platform, platform:chat_id, platform:chat_id:thread_id
HERMES_HOME=/opt/mercurio-data hermes send --to telegram:6171996969 "📖 História 1/5 — ..."
HERMES_HOME=/opt/mercurio-data hermes send --to telegram:6171996969 "📖 História 2/5 — ..."
```

- `--to` target examples: `telegram`, `telegram:6171996969`, `telegram:<chat_id>:<thread_id>`,
  `discord:#ops`, `slack:C0123ABCD`, `signal:+55...`.
- N messages = N `hermes send` calls. Put `sleep 0.5` between them to keep arrival order.
- Message body from arg, `--file <path>`, or stdin. `--json` = machine-readable result.
- `--list [platform]` enumerates available targets. `-q` suppresses stdout (exit code only).
- Exit codes: `0` ok, `1` delivery/backend error, `2` usage error.

## Pitfalls

- The CLI messages land as **NEW** messages — they are not the current session's own
  reply. If exact count/ordering matters, confirm with the user afterward.
- Always set `HERMES_HOME` so delivery uses the target profile's credentials, not the
  default home.
- Works even with no running gateway for bot-token platforms (Telegram/Discord/Slack/Signal).
