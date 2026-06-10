---
name: messaging-platforms
description: Hermes cross-platform message sending — platform-specific quirks, JID/ID format requirements, bridge API workarounds, and channel directory resolution. Covers Telegram, WhatsApp, and other messaging adapters.
---

# Messaging Platforms

Hermes sends messages through platform-specific bridge processes (Node.js for WhatsApp, direct API for Telegram, etc.). Each platform has distinct ID format requirements for recipients.

## Telegram — MEDIA File Delivery

**Critical rule: MEDIA: must be the very first line of the message.** Any content before it (text, formatting, other MEDIA lines) prevents the file from ever arriving. The platform silently drops it.

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

## WhatsApp Bridge

### Target Format

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

2. **Restart the bridge**: `kill $(cat /opt/data/whatsapp/session/bridge.pid)` — gateway auto-restarts ~30s.
3. **Query**: `curl -s http://127.0.0.1:3000/groups`

### Sending to Groups

Once you have the group JID, bypass `send_message` and hit the bridge directly:

```bash
curl -s -X POST http://127.0.0.1:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363419131378682@g.us","message":"Your message here"}'
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
| Individual contact | `number@s.whatsapp.net` | `5511999999999@s.whatsapp.net` |
| Group | `group_id@g.us` | `120363419131378682@g.us` |

Note: `send_message` cannot resolve group JIDs through the channel directory. Group delivery must go through the bridge API directly.

### Discovering Group IDs

The bridge has no built-in endpoint to list groups. Add one:

1. **Add `GET /groups` to `bridge.js`** (after the `/chat/:id` route):

```javascript
// List all groups
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

2. **Restart the bridge**: kill the process—the gateway's reconnection watcher restarts it automatically within ~30s.

3. **Query groups**:
```bash
curl -s http://127.0.0.1:3000/groups | jq '.groups[] | select(.subject | test("IA que Funciona"; "i"))'
```

### Sending to Groups

Once you have the group JID, bypass `send_message` and hit the bridge directly:

```bash
curl -s -X POST http://127.0.0.1:3000/send \
  -H "Content-Type: application/json" \
  -d '{"chatId":"120363419131378682@g.us","message":"Your message"}'
```

The bridge returns `{"success":true,"messageId":"..."}` on success.

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

### Sending Media to Groups

The bridge has a `/send-media` endpoint for native file delivery (image, video, document, audio):

```bash
curl -s -X POST http://127.0.0.1:3000/send-media \
  -H "Content-Type: application/json" \
  -d '{
    "chatId":"120363419131378682@g.us",
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

### Discovering Group IDs Without /groups Endpoint

If the `GET /groups` endpoint hasn't been added to bridge.js yet, group IDs can still be discovered from the session filesystem:

```bash
# List all groups the bot is participating in
ls /opt/data/whatsapp/session/ | grep "sender-key-" | sed 's/.*sender-key-//' | sed 's/--.*//' | sort -u

# Find the most recently active group (likely where user just messaged)
ls -lt /opt/data/whatsapp/session/sender-key-*.json | head -5

# Check bridge log for the most frequently active group
grep -oP '"chatId":"[^"]+' /opt/data/whatsapp/bridge.log | sort | uniq -c | sort -rn | head -10
```

The bridge logs don't contain group names (only JIDs in self-chat mode), so the most recently modified sender-key file is the best heuristic for identifying the active group.

### Bridging Restart Pattern

After editing `bridge.js`:
1. Kill the process: `kill $(cat /opt/data/whatsapp/session/bridge.pid)`
2. Wait for the gateway's reconnection watcher (~30s, check with `curl http://localhost:3000/health`)
3. The bridge starts with the modified code, session auth persists from saved creds

### Troubleshooting

- **"Cannot destructure property 'user' of 'jidDecode(...)'"** — JID is malformed. Use `number@s.whatsapp.net`, not E.164.
- **"Could not resolve '...' on whatsapp"** — Contact not in channel directory. Use direct bridge API.
- **Bridge log** at `/opt/data/whatsapp/bridge.log` for connection status and errors.
- **Check status**: `curl -s http://127.0.0.1:3000/health`
