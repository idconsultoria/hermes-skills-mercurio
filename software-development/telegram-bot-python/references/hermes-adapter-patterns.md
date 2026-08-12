# Hermes Telegram Adapter — Condensed Patterns

Extracted from the Hermes Agent Telegram adapter
(`/opt/hermes/plugins/platforms/telegram/adapter.py`, ~10k lines, `python-telegram-bot` 22.x).
These are the patterns worth copying when building a rich Telegram bot.

## 1. MarkdownV2 escaping algorithm (`format_message` ~L7710, `_escape_mdv2` ~L466)

Telegram `ParseMode.MARKDOWN_V2` rejects unescaped special chars with 400 Bad Request.
Special chars that MUST be escaped with `\`: `_ * [ ] ( ) ~ ` > # + - = | { } . !`

Algorithm (in order):
1. **Protect fenced code blocks** (``` ... ```) — stash behind placeholder tokens
   (`\x00PH0\x00`) so escaping never touches code. Inside fences, escape `\` and backtick.
2. **Protect inline code** (`` `...` ``) — same placeholder technique.
3. Convert standard markdown → MarkdownV2 (bold `**x**`→`*x*`, italic `_x_`→`_x_`... careful:
   single `*` is italic in MDv2, `**` is bold).
4. Escape all remaining special chars in non-protected regions.
5. Restore placeholders.

Also: GFM pipe tables → `_wrap_markdown_tables` (row groups) before MDv2 conversion.

**Fallback stripping** (`_strip_mdv2` ~L471): when sending plain text (e.g. error path),
strip MDv2 markers: `**bold**`→`bold`, MarkdownV2 bold `*x*`→`x`, italic, strikethrough
`~x~`, spoiler `||x||` — and remove escape backslashes.

## 2. Message length cap and chunking (~L645-655)

- `MAX_MESSAGE_LENGTH = 4096` — Telegram hard cap.
- `splits_long_messages = True` — send() chunks via `truncate_message(MAX_MESSAGE_LENGTH)`.
- Chunk continuator: `(1/2)`, `(2/2)` appended to chunk end.
- `_separate_chunk_indicator_from_fence` (~L498): if a chunk had to close an in-progress
  fenced code block, the `(N/M)` marker must move OFF the code-fence line.

## 3. Typing indicator with cooldown (~L751-756)

- Send `chat_action="typing"` when the agent starts working.
- Re-send while work is pending (keep-typing budget) but respect a **cooldown per chat**
  (`_telegram_typing_cooldown_seconds`, default ~0.3-1.0s; a longer cooldown ~3s avoids
  flood-limit errors on long operations).
- Track `_telegram_typing_cooldown_until: Dict[chat_id, float]`; skip send if within cooldown.

## 4. Streaming via edits

- Send an initial "working…" message, then `edit_message_text` on the SAME message_id
  progressively (finalize=True path — when raw text unchanged between streamed drafts,
  short-circuit to avoid redundant edits).
- Streaming edits respect the 4096 preview cap; if an oversized edit saturates at the cap,
  the continuation goes out as a new message (flood-control aware, ~0.8s per edit).

## 5. Reactions

- `set_message_reaction` — lightweight status feedback without extra messages.
- Guard with feature-detect / try-except: not every lib version / chat type supports it.
- Used by Hermes for quick ack (✅) while text content arrives separately.

## 6. Bot profile registration at boot

Register via Bot API at startup (all return 200 when working):
- `setMyCommands` — slash-command menu with descriptions.
- `setMyShortDescription` / `setMyDescription` — bot about text.

## Working implementation reference (CFP IA bot)

`telegram-bot/formatacao.py` in the CFP IA repo implements the full pattern:
- `escapar_mdv2(texto)` — escape special chars.
- `md_para_mdv2(texto)` — placeholder-protect code, convert markdown, escape, restore.
- `dividir_mensagem(texto, max_len=4096)` — split on line boundaries, `(1/2)` continuator.

Unit-test probes that pass:
- `md_para_mdv2('*A Cerca de Proteção* — dia 3 de 7 (50% pronto)')` → keeps `*bold*`,
  escapes `(50%)` as `\(50%\)`.
- `escapar_mdv2('R$ 6.000,00 [teste]')` → `R$ 6\.000,00 \[teste\]`.
- `dividir_mensagem('x'*5000)` → 2 chunks.
