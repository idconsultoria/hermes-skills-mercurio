---
name: messaging-platforms
description: "Reference for Hermes cross-platform messaging — platform quirks, ID formats, and

Load this skill when troubleshooting message delivery across platforms, or when the user reports inconsistent response lag between platforms. Covers Telegram MEDIA file delivery rules, WhatsApp JID/group ID formats, bridge processes, known file-type limitations, platform-specific workarounds, and per-platform API latency diagnostics."
metadata:
  hermes:
    tags: [messaging, platforms, telegram, whatsapp, signal, matrix, discord, slack, bridge]
    related_skills: [whatsapp-bridge-baileys]
type: Reference
timestamp: 2026-06-28T05:11:55Z
---

# Messaging Platforms

Hermes sends messages through platform-specific bridge processes (Node.js for WhatsApp, direct API for Telegram, etc.). Each platform has distinct ID format requirements for recipients.

## Telegram — MEDIA File Delivery

**Critical rule: MEDIA: must be the very first line of the message.** Any content before it (text, formatting, other MEDIA lines) prevents the file from ever arriving. The platform silently drops it.

> ⚠️ **MEDIA: only works from gateway sessions.** When running in TUI (terminal UI), MEDIA: delivers locally — the file never reaches Telegram. Use direct Bot API instead: see `references/telegram-bot-api-file-delivery.md`.

Example — WORKS:
```
MEDIA:/tmp/report.pdf
Here's the file you asked for.
```

Example — NEVER ARRIVES (file silently dropped):
```
Here's the file you asked for.
MEDIA:/tmp/report.pdf
```

### Known file-type limitations

Telegram's media handler only recognizes common types natively:

| Extension | Result | Workaround |
|-----------|--------|------------|
| `.png`, `.jpg`, `.webp` | ✅ Photo | native |
| `.mp4` | ✅ Video | native |
| `.ogg` (opus) | ✅ Voice | native |
| `.txt`, `.md` | ✅ Document | native |
| `.html` | ❌ silent drop | zip with Python: `shutil.make_archive('name','zip','.','file.html')` |
| `.sh`, `.bat`, `.ps1` | ❌ silent drop | rename to `.txt` |
| `.py`, `.js`, `.ts`, `.go` | ❌ silent drop | rename to `.txt` |
| `.key`, `.pem`, `.env` | ❌ silent drop | rename to `.txt` |

**Pattern**: for scripts/configs/keys, deliver as `.txt` and tell the user to rename. Or paste content in a code block.

### Multiple files

One MEDIA per message. N files = N separate responses.

### MEDIA Auto-Delivery Pitfall

When `text_to_speech` returns a `MEDIA:` path, the platform's auto-delivery handles sending it as a native audio message — no extra step needed.

**Do NOT also call `send_message` with the same `MEDIA:` path.** This causes the audio to arrive twice:

```
❌ Double-send (wrong):
   text_to_speech(...) → returns MEDIA:/path
   send_message(target="telegram", message="MEDIA:/path")  ← DUPLICATE

✅ Let auto-delivery handle it (correct):
   text_to_speech(...) → returns MEDIA:/path
   (just let the response's MEDIA: tag deliver naturally)
```

This also applies to any file delivered via `MEDIA:` in a final response — the gateway sends it once automatically.

---

## Gateway Display — User-Facing Bot Mode

### Display Settings Per-Platform

The Hermes gateway resolves display/verbosity settings with this priority order:

```
1. display.platforms.<platform>.<key>   — explicit per-platform override
2. display.<key>                         — global user setting
3. Built-in platform default             — sensible default per platform
4. Built-in global default               — last resort
```

**Key settings that control what users see:**

| Setting | Values | Effect |
|---------|--------|--------|
| `tool_progress` | `all`, `new`, `off` / `none` | Show tool calls progress |
| `interim_assistant_messages` | `true`, `false` | Show assistant chattering mid-execution |
| `busy_ack_detail` | `true`, `false` | Verbose busy acknowledgements |
| `long_running_notifications` | `true`, `false` | Heartbeat during long tasks |

### Platform Defaults

Telegram comes with a clean display by default (`tool_progress="off"`, `busy_ack_detail=false`) — but the **global** `display.tool_progress: all` in config.yaml overrides it. So if you set `display.tool_progress: all` globally, Telegram users see tool calls too.

To make Telegram clean but keep CLI verbose:

```yaml
display:
  tool_progress: all                       # CLI sees everything
  platforms:
    telegram:
      tool_progress: off                   # Telegram users see clean responses
      interim_assistant_messages: false    # no intermediate chatter
```

The per-platform override in `display.platforms.telegram` wins over the global setting.

### Full Clean-Bot Config

```yaml
display:
  tool_progress: none
  interim_assistant_messages: false
  long_running_notifications: false
  busy_ack_detail: false
  cleanup_progress: true                   # removes progress bubbles after final response
```

**Requires:** Gateway `/restart` or `hermes gateway restart` to take effect.
**CLI unaffected:** These settings only change gateway behavior; CLI sessions remain unchanged.

### Different UX for Yourself vs Other Users (Multi-Bot Pattern)

Display settings are **per-platform, not per-user** — all Telegram users see the same display. To have different experiences (verbose for you, clean for others), run multiple Telegram bots each on its own Hermes profile.

#### Approach A: Multiplexing Gateway (Recommended — Single Process)

With `gateway.multiplex_profiles: true`, **one** gateway process serves all profiles. Each profile keeps its own bot token, config, skills, SOUL, and memory. Sessions are namespaced per profile (`agent:<profile>:...`).

```yaml
# default profile's config.yaml
gateway:
  multiplex_profiles: true
```

Steps:

1. Create a second Telegram bot via [@BotFather](https://t.me/botfather)
2. Create a Hermes profile: `hermes profile create public`
3. Configure the public profile's Telegram token and set `display.tool_progress: none` in its config.yaml
4. Start **just** the default gateway: `hermes gateway start`

| Profile | Bot Token | Config | Audience |
|---------|-----------|--------|----------|
| `default` | Bot A (private) | `tool_progress: all` | You see everything |
| `public` | Bot B (public) | `tool_progress: none` | Public sees clean responses |

Rules when multiplexing is on:
- Secondary profiles **must not** start their own gateway (`hermes -p public gateway start` fails with a clear error)
- Each profile needs its **own** bot token — two profiles sharing the same token crashes startup
- HTTP-inbound platforms use `/p/<profile>/` URL prefix on the default listener
- Sessions are namespaced, existing default-profile history is untouched

See [docs: Running Many Gateways at Once](https://hermes-agent.nousresearch.com/docs/user-guide/running-many-gateways) for full details.

#### Approach B: Separate Gateway Per Profile (Multiple Processes)

The classic approach — each profile runs its own gateway process:

1. Create a second Telegram bot via [@BotFather](https://t.me/botfather)
2. Create a Hermes profile: `hermes profile create public`
3. Configure the public profile's Telegram gateway with the new bot token
4. In the public profile's config.yaml, set `display.tool_progress: none`
5. Start the second gateway: `hermes -p public gateway`

Use this when you want hard process-level isolation (separate crash domains, restart one without touching others).

Both approaches let you set different permitted features per profile (e.g., restrict terminal access on the public one).

## Telegram — DM Topics & Multi-Session Mode

Two features let you run multiple isolated workspaces within a **single** Telegram bot DM:

### Config-Driven DM Topics

Declare fixed topics in config.yaml — each topic gets its own session, history, and optional auto-loaded skill:

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: SEU_USER_ID
        topics:
        - name: Dev
          icon_color: 9367192
          skill: github-pr-workflow
        - name: Pesquisa
          icon_color: 16766590
          skill: deep-research
```

- Each topic maps to an isolated session key: `agent:<profile>:telegram:dm:{chat_id}:{thread_id}`
- Topics with a `skill` field auto-load that skill on session reset (/reset, idle timeout)
- Set `ignore_root_dm: true` to turn the root DM into a system-commands-only lobby for users with topics

Prerequisite: user must enable Topics mode in the bot DM (tap bot name → enable Topics).

### User-Driven Multi-Session Mode (`/topic`)

End-user types `/topic` in the DM to enable ChatGPT-style multi-session mode — no config, no pre-declared names:

- `/topic` — enable mode, create pinned System topic
- `/topic <session-id>` — restore a previous Telegram session into a topic
- `/topic off` — disable mode, clear bindings

Each topic created via Telegram's "All Messages → send any message" becomes a standalone session with full isolation (history, context window, model state). Topics are auto-renamed to match the session title unless `disable_topic_auto_rename: true` is set.

Prerequisite: @BotFather → Bot Settings → Threads Settings → enable Threaded Mode, keep "users can create topics" on.

### When to Use Each

| Feature | Who activates | Topic names | Best for |
|---------|-------------|-------------|----------|
| `dm_topics` | Operator (config) | Fixed, chosen by operator | Permanent workspaces with skill binding |
| `/topic` | End user | Free, user-chosen | Ad-hoc parallel conversations |

Both can coexist: `dm_topics` manages operator-declared workspaces, `/topic` lets the user create ad-hoc sessions.

## WhatsApp Bridge (Baileys)

The bridge runs as a Node.js process on port 3000. For full bridge internals (endpoints, self-chat mode, sender-key group discovery, media sending, message editing), see `references/whatsapp-baileys-bridge.md` (absorbed from the former `whatsapp-bridge-baileys` skill).

### Quick Reference

```bash
# Health check
curl -s http://localhost:3000/health

# Send text
curl -s -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363XXXXX@g.us","message":"Your message"}'

# Send media
curl -s -X POST http://localhost:3000/send-media \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363XXXXX@g.us","filePath":"/path/file.html","mediaType":"document"}'
```

The `send_message` tool accepts WhatsApp targets in several formats, but the bridge (Baileys) **requires JID format**: `number@s.whatsapp.net`.

| Input Format | Result |
|---|---|
| `whatsapp:5511999999999` | ❌ Bridge error: `jidDecode failed` |
| `whatsapp:+5511999999999` | ❌ Bridge error: `jidDecode failed` |
| `whatsapp:5511999999999@s.whatsapp.net` | ❌ Channel directory can't resolve it |
| Direct curl to bridge API | ✅ Works |

### Workaround: Sending to a New Contact

The `send_message` tool only sends to contacts already in the channel directory. For new/unregistered numbers, bypass the tool and call the bridge API directly:

```bash
curl -s -X POST http://127.0.0.1:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"5511999999999@s.whatsapp.net","message":"Your message here"}'
```

The bridge runs on `127.0.0.1` (loopback), port configured via `config.extra.bridge_port` (default: 3000).

### Self-Chat Mode

The bridge logs `mode: self-chat` — only the user's own number can send/receive. Outbound messages to new contacts work fine via the bridge API. Inbound messages from non-self numbers are silently ignored (`self_chat_mode_rejects_non_self`).

**⚠️ Groups are invisible in self-chat mode.** The bridge explicitly skips both:
- `fromMe` messages in groups (`if (isGroup || chatId.includes('status')) continue;`)
- Group messages from other participants (`self_chat_mode_rejects_non_self`)

This means `send_message(action='list')` will NEVER show WhatsApp groups. The `send_message` tool also can't resolve group JIDs (`@g.us`) through the channel directory — it returns `"Could not resolve '...' on whatsapp"`.

### Discovering Group IDs

The bridge has no built-in endpoint to list groups. Add one:

1. **Add `GET /groups` to `bridge.js`** (after the `/chat/:id` route):

```javascript
app.get('/groups', async (req, res) => {
  if (!sock || connectionState !== 'connected') {
    return res.status(503).json({ error: 'Not connected' });
  }
  try {
    const groups = await sock.groupFetchAllParticipating();
    const result = Object.entries(groups).map(([id, meta]) => ({
      id,
      subject: meta.subject,
      size: meta.participants?.length || 0,
    }));
    res.json({ groups: result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
```

2. **Restart the bridge**: `kill $(cat [whatsapp-session-dir]/bridge.pid)` — gateway auto-restarts ~30s.
3. **Query**: `curl -s http://127.0.0.1:3000/groups`

### Sending to Groups

Once you have the group JID, bypass `send_message` and hit the bridge directly:

```bash
curl -s -X POST http://127.0.0.1:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363XXXXX@g.us","message":"Your message here"}'
```

On success: `{"success":true,"messageId":"..."}`

### Group Messages in Self-Chat Mode

In self-chat mode the bridge **ignores ALL group messages** — both your own (`fromMe` in groups) and others':

| Message type | Behaviour | Bridge code |
|---|---|---|
| `fromMe` + `@g.us` | Silently skipped | `if (isGroup ...) continue;` (line 269) |
| `!fromMe` + `@g.us` | Silently ignored | `self_chat_mode_rejects_non_self` (line 296) |

**Result**: the gateway never receives group messages, so `send_message(action='list')` never shows groups — only DMs.

## WhatsApp Groups

### JID Format

| Entity | JID Format | Example |
|---|---|---|
| Individual contact (standard) | `number@s.whatsapp.net` | `5511999999999@s.whatsapp.net` |
| Individual contact (alternate) | `number@c.us` | `5516981959112@c.us` |
| Group | `group_id@g.us` | `120363XXXXX@g.us` |

> Both `@s.whatsapp.net` and `@c.us` work for individual contacts on the Baileys bridge. `@c.us` was confirmed working 2026-07-16 with file send via `/send-media` to a Brazilian number (+55).

Note: `send_message` cannot resolve group JIDs through the channel directory. Group delivery must go through the bridge API directly.

### 📌 Contact Reference — Verified Group IDs & Contacts

⚠️ **Durable reference — setor é deletado por consolidação de skills.** O skills-repo-curator evolve phase pode remover JIDs das skills (ocorreu em 15/06/2026). Salvar em 3 lugares: esta skill, whatsapp-bridge-baileys Contatos Salvos, e memória.

| Nome | JID | Notas |
|-------|-----|-------|
| ID [Núcleo] | `120363170662612284@g.us` | ID Consultoria interno |
| IA que Funciona | `120363419131378682@g.us` | Comunidade IAF |
| Tácio Brito | `557991441720@s.whatsapp.net` | Sócio ID Consultoria |

Verificar nome: `curl -s http://localhost:3000/chat/JID | python3 -c "import sys,json; print(json.load(sys.stdin).get('name'))"`

### Cron Jobs → Group Delivery (Two-Tier Pattern)

When a **cron job** needs to send a message to a WhatsApp group while keeping status/confirmation private:

| Config | Correct value | Why |
|--------|---------------|-----|
| `deliver` | `"origin"` (or omit for auto) | Final response goes to user's DM, NOT the group |
| `prompt` | Uses `send_message()` internally | Agent delivers the actual message to the group |
| Final response | Brief confirmation only | e.g. `"✅ Lembrete enviado ao grupo ID Núcleo."` |

**Wrong** (what causes the leak):
```
deliver: "whatsapp:120363xxxxxx@g.us"
```
The cron's entire final response (including technical status, message IDs, "Mensagem enviada com sucesso") gets auto-delivered to the group alongside the intended message.

**Correct — cron prompt template:**
```
Você é um cron job que roda automaticamente. Use send_message para entregar a MENSAGEM ao grupo WhatsApp (120363xxxxxx@g.us).
[rest of the message instructions]

REGRAS:
1. Use send_message(target="whatsapp:120363xxxxxx@g.us", message="...")
2. Sua resposta final deve ser APENAS: "✅ [resumo simples]"
3. NÃO inclua o conteúdo da mensagem, confirmação técnica, ou IDs na resposta final
4. A resposta final não vai para o grupo — vai só para o usuário
```

**Flow when it runs:**
1. Cron fires → agent calls `send_message()` → group receives ONLY the intended text
2. Agent returns `"✅ Lembrete enviado."` → auto-delivery sends to user's origin chat
3. Group never sees status messages, message IDs, or execution confirmation

Used for: reminder crons, automated broadcasts, scheduled notifications to external groups where the user wants confirmation without contaminating the group feed.

### Sending Media (Groups & Individuals)

The bridge has a `/send-media` endpoint for native file delivery (image, video, document, audio). Works for both group JIDs (`@g.us`) and individual JIDs (`@s.whatsapp.net` or `@c.us`):

```bash
curl -s -X POST http://127.0.0.1:3000/send-media \
  -H "Content-Type: application/json" \
  -d '{
    "chatId":"120363XXXXX@g.us",
    "filePath":"/opt/data/report.html",
    "caption":"Optional caption text",
    "mediaType":"document",
    "fileName":"Report.html"
  }'
```

Parameters:
- `chatId` (required) — group JID or individual JID
- `filePath` (required) — absolute path to file on disk
- `caption` (optional) — text caption for image/video/document
- `mediaType` (optional) — auto-detected from extension if omitted. One of: `image`, `video`, `audio`, `document`
- `fileName` (optional) — display filename for documents

### Self-Chat Mode Outgoing Prefix

In self-chat mode, `formatOutgoingMessage()` prepends `⚕ *Hermes Agent*\n────────────\n` to EVERY outgoing message before sending. This is defined as `DEFAULT_REPLY_PREFIX`. When sending to groups, this prefix appears as part of the message text from the user's own number. The prefix is controlled by `WHATSAPP_REPLY_PREFIX` env var — set to empty string to disable.

### Bridging Restart Pattern

After editing `bridge.js`:
1. Kill the process: `kill $(cat [whatsapp-session-dir]/bridge.pid)`
2. Wait for the gateway's reconnection watcher (~30s, check with `curl http://localhost:3000/health`)
3. The bridge starts with the modified code, session auth persists from saved creds

### link-preview-js Missing Dependency

The WhatsApp bridge depends on `link-preview-js` for generating link previews. If missing, every message with a URL logs `ERR_MODULE_NOT_FOUND: Cannot find package 'link-preview-js'` in `bridge.log` and link previews fail silently. Messages still deliver without previews.

**Fix:**
```bash
cd /opt/data/scripts/whatsapp-bridge && npm install link-preview-js
```

Verify with `ls node_modules/link-preview-js/package.json`.

### Troubleshooting

- **"Cannot destructure property 'user' of 'jidDecode(...)'"** — JID is malformed. Use `number@s.whatsapp.net`, not E.164.
- **"Could not resolve '...' on whatsapp"** — Contact not in channel directory. Use direct bridge API.
- **Bridge log** at `[bridge-log-path]` for connection status and errors.
- **Check status**: `curl -s http://127.0.0.1:3000/health`

#### Bridge fails to start after cleanup (node_modules deleted)

System cleanups (Docker prune, disk reclaim) often remove `node_modules/` from the WhatsApp bridge directory. When the directory and its files are read-only (`0555`/`-r--r--r--`), the gateway adapter's `npm install` fails with `EACCES: permission denied` on `package-lock.json`.

**Symptoms in gateway.log:**
```
Bridge found at /opt/data/scripts/whatsapp-bridge/bridge.js
(no "Dependencies installed" message)
~500ms later -> Reconnect whatsapp failed, next retry in 300s
```

**Fix:**
```bash
# 1. Make bridge files writable
chmod u+w /opt/data/scripts/whatsapp-bridge/*.json
chmod u+w /opt/data/scripts/whatsapp-bridge/*.js /opt/data/scripts/whatsapp-bridge/*.mjs

# 2. Install dependencies
cd /opt/data/scripts/whatsapp-bridge && npm ci

# 3. Create the .hermes-pkg-hash stamp so the adapter skips npm install next time
python3 -c "
import hashlib
h = hashlib.sha256(open('package.json','rb').read()).hexdigest()[:16]
open('node_modules/.hermes-pkg-hash','w').write(h)
"
```

**How the adapter decides to run npm install (deps_fresh check):**
The adapter checks for `node_modules/.hermes-pkg-hash` and compares it against a SHA-256 of `package.json` (first 16 hex chars). If the file is missing or the hash does not match, it runs `npm install --silent` with a 300s timeout. After a clean install from scratch (no existing `node_modules`), the stamp file does not exist -- the adapter will trigger a fresh `npm install` on each reconnect, which may fail if files are read-only. Always create the stamp manually after `npm ci` to short-circuit this check.

#### Session path resolution

The adapter resolves the session path via `get_hermes_dir("platforms/whatsapp/session", "whatsapp/session")`:
- Checks for legacy path `$HERMES_HOME/whatsapp/session` first (e.g. `/opt/data/whatsapp/session/`)
- Falls back to `$HERMES_HOME/platforms/whatsapp/session`

Two paths may coexist after cleanup or profile changes. The active session is the one with `creds.json`. If an empty session directory is created by a manual bridge test (e.g. at `/opt/data/home/.hermes/whatsapp/session/`), it is not the one the adapter uses -- it will be ignored as long as the legacy path exists with valid creds.

To verify which session path the adapter is using:
```bash
curl -s http://localhost:3000/health | python3 -c "import sys,json; print(json.load(sys.stdin))"
```

## Platform Latency Diagnostics

When the user reports inconsistent response speed between platforms (e.g., Telegram slow but WhatsApp fast), the cause may be network geography, but it can also be **session context size** or a **shared provider bottleneck**.

### Quick Differential Diagnosis

Run this before diving into tools:

1. **Are ALL platforms slow?** Check gateway logs for both platforms:
   ```
   grep "response ready" /opt/data/logs/gateway.log | tail -10
   ```
   If both Telegram AND WhatsApp show high response times (e.g., `time=60.0s api_calls=14`), the bottleneck is in the **shared LLM provider/model path**, not in platform latency.

2. **What's the pattern within a single turn?** If the first response per user message is slow but subsequent tool calls in the same turn are fast, it's **prompt cache invalidation** between turns — each user message forces the provider to reprocess the full session context from scratch (30-70s for a 291K-token session), while cached responses within a turn are fast (2-5s).

3. **Is one platform consistently slower?** Then measure raw API latency from the host (see below) — likely network geography.

### Measuring Raw API Latency

```bash
# Telegram
curl -s -o /dev/null -w "connect=%{time_connect}s total=%{time_total}s\n" \
  --max-time 10 "https://api.telegram.org/bot${TOKEN}/getMe"

# WhatsApp (Graph API)
curl -s -o /dev/null -w "connect=%{time_connect}s total=%{time_total}s\n" \
  --max-time 10 https://graph.facebook.com/v22.0/
```

### Session Context Size — Prompt Cache Pattern

**Signal:** First response per user turn takes 30-120s, but subsequent calls in the same turn are 2-10s.

**Cause:** Each user message triggers a new API call that processes the ENTIRE session context. Prompt caching only helps within a single turn. A 291K-token session means every user question pays 291K tokens of reprocessing.

**Fix:**
1. Enable `compression.in_place: true` in `config.yaml` (the real config path, see `get_config_path()`)
2. Restart the gateway
3. Run `/compress` on the slow platform — this compacts the session in-place, dropping token count without rotating the session ID

**Verify:** After compression, check `response ready` times drop to normal levels.

Full methodology, per-platform baselines, and interpretation guide: `references/platform-latency-diagnostics.md`.

## Related Files

| File | Purpose |
|------|---------|
| `references/whatsapp-baileys-bridge.md` | WhatsApp bridge API reference (absorbed from former `whatsapp-bridge-baileys` skill) |
| `references/baileys-standalone-zapi-replacement.md` | Standalone Baileys REST bridge as Z-API replacement for external projects |
| `references/telegram-bot-api-file-delivery.md` | Direct Bot API file delivery from TUI (when MEDIA: can't route to Telegram) |
| `references/json-payload-newlines.md` | JSON newline handling for multi-line text |
| `references/platform-latency-diagnostics.md` | Per-platform API latency measurement and troubleshooting |
