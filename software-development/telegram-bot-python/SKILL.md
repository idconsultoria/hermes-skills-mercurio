---
name: telegram-bot-python
description: "Telegram bots: mock-first, MarkdownV2, python-telegram-bot.

Load this skill when building or debugging a Telegram bot in Python — mock-first development, MarkdownV2 formatting rules, and python-telegram-bot patterns that avoid silent send failures."
version: 1.0.0
author: Hermes Agent
tags: [telegram, bot, python, messaging, python-telegram-bot, formatting]
type: ToolIntegration
timestamp: 2026-08-12T03:30:00Z
---

# Telegram Bot (Python) — Build & Polish

Class-level guide for building Telegram bots with `python-telegram-bot` v22.x — from
architecture decisions to rich message formatting. Validated building the CFP IA demo bot
(mock-deterministic + optional LLM hook, 11 interaction flows, formatting inspired by the
Hermes Agent Telegram adapter).

## When to use

- Creating a new Telegram bot (prototype or production)
- Extending an existing bot with rich formatting, streaming, reactions, or multi-flow state
- Porting a web app's interaction flows into a chat-first interface

## Architecture: mock-first + optional LLM hook (proven for demo/prototype bots)

**Default = deterministic mock; LLM is an optional add-on.** For demo bots this beats a
raw-LLM bot: reproducible, zero cost, never drifts off the script. If the user wants real AI
later, expose a hook — the state machine stays identical.

```
telegram-bot/
├── bot.py            # Entrypoint: Application + handlers (Telegram ⇄ events only)
├── config.py         # Env vars (TELEGRAM_BOT_TOKEN required; LLM keys optional)
├── estado.py         # Per-chat FSM: Sessao dataclass + GerenciadorEstado (dict)
├── cerebro.py        # The "brain": decide(sessao, evento) -> Plano of Mensagens (mock)
├── llm_provider.py   # Optional OpenAI-compatible client (any base_url)
├── roteiros.py       # IA speech per flow/state (product copy, tone-of-voice)
├── formatacao.py     # MarkdownV2 escaping + markdown→MDV2 + 4096 split
├── dados_mock.py     # Same mock data as the web prototype (parity!)
└── requirements.txt  # python-telegram-bot>=22.6, httpx
```

Key design: `bot.py` **never decides anything** — it translates Telegram updates into
`evento` dicts (`{"tipo": "comando"|"texto"|"callback"|"arquivo", ...}`) and calls
`cerebro.decidir(sessao, evento) -> Plano`. `Plano.mensagens: list[Mensagem]` where
`Mensagem(texto, botoes: list[list[Botao]], editar, delay)`. This keeps logic unit-testable
without Telegram.

## Rich formatting (the Hermes way)

Reference implementation: Hermes Agent's Telegram adapter at
`/opt/hermes/plugins/platforms/telegram/adapter.py` (~10k lines). Patterns worth copying:

1. **MarkdownV2 with proper escaping** — ALWAYS use `ParseMode.MARKDOWN_V2`, but Telegram
   rejects unescaped special chars (`_ * [ ] ( ) ~ \` > # + - = | { } . !`) with 400 Bad
   Request. Protect fenced/inline code blocks first, convert markdown, then escape the rest
   (see `references/hermes-adapter-patterns.md` for the algorithm and a working
   `formatacao.py` spec).
2. **Typing indicator with cooldown** — `send_chat_action("typing")` before processing, then
   re-send every ~4s while work is pending; cooldown ≥3s per chat to avoid flood limits
   (Hermes: `_telegram_typing_cooldown_seconds`).
3. **Streaming via edits** — send one message, then `edit_message_text` progressively
   ("Recebi! Processando…" → "Extraí os números…" → card with buttons). Reuse message_id.
   Less chat noise, feels like a real assistant.
4. **Reactions** — `set_message_reaction` for lightweight feedback (⏳ on file received, ✅
   on confirm, 🎉 on celebration). Feature-detect + try/except so older libs don't crash.
5. **4096-char split** — Telegram hard cap. Split on line boundaries without breaking code
   fences; append `(1/2)` continuator.
6. **Bot profile** — register at boot: `setMyCommands`, `setMyShortDescription`,
   `setMyDescription` (all 200 OK in logs when working).
7. **Inline keyboards for every choice** — never require free text where a button suffices.
   Use prefixed callback data (`start:comecar`, `lgpd:aceitar`, `q3:claro`, `docs:vamos`) —
   easy to route and debug.

## Tone-of-voice integration

When the product has a voice doc (e.g. CFP IA `tom-voz.md`): forbid jargão and
imperative-shaming words; "vamos" as default calls-to-action. The mock speech in
`roteiros.py` must match the web prototype copy.

**Emojis in copy — ask the user, don't assume.** Default discipline is emojis
only in reactions/status, BUT this user explicitly requested emojis inline in
copy too — with parcimônia. Their validated rules (CFP IA bot, Turno 3):
- **1 emoji per short message; 2-3 max in a long card** — never one per line.
- Restricted vocabulary fitting the domain: `👋` (welcome) `🔒` (LGPD/security)
  `💡` (tip) `📄` (documents) `🎯` (mission) `📈` (progress/streak) `📊`
  (summary/predictive) `🤝` (human support) `🛡️` (reserve). NEVER money/fire
  emojis (`💰🤑🔥`) or decorative excess.
- **Anti-duplication rule:** if the bot already sends a Telegram *reaction*
  (✅/🎉) for an event, the copy must NOT repeat that emoji inline at the same
  point. Example: celebration gets reaction 🎉 → copy uses 📈; doc confirm gets
  reaction ✅ → copy says "Fechado, *extrato confirmado*!" without ✅.
- Confirm with the user before applying either style — they may want one, the
  other, or both (they chose both for CFP IA).

## Command naming: Portuguese-first with canonical aliases

Users often want bot commands in their own language. Telegram command tokens
only accept `a-z 0-9 _` (no accents), and `/start` is special — the Telegram
client sends it automatically when the user taps the bot, so `/start` must
NEVER be removed. Pattern proven on CFP IA (Turno 5):

```python
COMANDO_CANONICO = {
    "/iniciar": "/start", "/start": "/start",        # PT-first, alias kept
    "/sequencia": "/streak", "/streak": "/streak",
    "/reiniciar": "/reset", "/reset": "/reset",
    "/comandos": "/ajuda", "/ajuda": "/ajuda",
}
# cerebro dispatcher: comando = COMANDO_CANONICO.get(comando, comando)
# bot handlers: CommandHandler(["iniciar", "start"], handler)
```

- Register BOTH names in `CommandHandler`; normalize in the brain via the map so
  PT and legacy commands hit the SAME handler.
- `setMyCommands` exposes only the PT names in the visible menu.
- Update every in-copy command reference (help text, reset hint) to the PT name;
  keep old names working silently.
- Test each PT command and its legacy alias produce identical output.

## Deployment on Oracle host (shared-volume quirk)

- **Never create the venv inside the shared volume** (`/home/ubuntu/selfhost/shared/...`) —
  it's owned by the container user (uid 10000); `python3 -m venv` fails with EACCES even as
  ubuntu. Create venv in `/home/ubuntu/<app>/` (host-local), install requirements from the
  shared path, run the code from the shared path.
- Host needs `python3.12-venv` (`sudo apt install python3.12-venv`) or `ensurepip` is missing.
- **Token security**: write bot token to `/home/ubuntu/<app>/.token` (chmod 600), read it in
  a `start-bot.sh` wrapper (`TOKEN="$(cat .token)"`), never in shell history or repo.
- Start detached: `(setsid nohup /home/ubuntu/<app>/start-bot.sh > /tmp/<app>-bot.log 2>&1 < /dev/null &)`.
- To restart after code changes: `pkill -9 -f "path/to/bot.py"`, then re-launch in a SEPARATE
  ssh command (pkill in the same command kills the launcher too).

## Session reset (`/reset`) — destructive action needs confirmation

Users test demos repeatedly; they need a way to wipe state. Implement as an
explicit two-step, never instant:
- `/reset` with NO active session → direct reply: "Você ainda não começou —
  pode seguir com `/start`." (no confirmation prompt needed).
- `/reset` WITH progress → confirmation message + buttons
  `[Sim, resetar]` / `[Cancelar]` (callback data `reset:confirmar` /
  `reset:cancelar`). Cancel leaves state untouched and replies warmly
  ("Tranquilo, seguimos de onde estávamos.").
- The brain signals deletion via a flag on the plan (`Plano.resetar = True`);
  `bot.py` deletes the session from `GerenciadorEstado` BEFORE executing the
  plan — so state is never wiped without an explicit confirm.
- Add `/reset` to `setMyCommands` and to `/ajuda`.

## Verification without Telegram
- `python3 -m py_compile bot.py *.py` — syntax gate.
- Unit-test the brain by simulating events headlessly (no network): call
  `await cerebro.decidir(sessao, evento)` with a `GerenciadorEstado` and assert
  `plano.mensagens[0].texto` / `sessao.estado` transitions. Works fully offline in mock mode.
- Note the API shape: `Plano.mensagens` (each `Mensagem` has `.texto` and `.botoes` rows),
  `Sessao.estado` (not `.etapa`), callback data is PREFIXED (`start:comecar`) — check
  `grep 'bt(' cerebro.py` before guessing button payloads.

## Pitfalls

- **400 Bad Request on send** = unescaped MarkdownV2 char. Escape everything outside code
  fences; test with a message containing `(50%)` and `[x]`.
- **Sessao field names**: `s.estado` (state name), `s.pergunta` (calibration step), not
  `s.etapa`.
- **Reaction API** may be unavailable on some lib versions — wrap in try/except.
- **Long messages**: always route through the 4096 splitter; a raw send over cap silently
  truncates or errors depending on lib version.
- **LLM fallback**: when `llm_provider` fails, fall back to roteiro text — the demo must
  never break because the model errored.

## Support files

- `references/hermes-adapter-patterns.md` — condensed Hermes Telegram adapter patterns
  (escaping algorithm, typing cooldown, split logic) extracted from the reference source.
