---
name: whatsapp-automation
description: "Automate WhatsApp messaging from Python projects — Baileys bridge, Z-API migration, multi-assessor patterns.

Load this skill when your Python project needs to send WhatsApp messages (text, PDFs, documents) without paying for third-party APIs. Covers Baileys Node.js bridge setup, Z-API compatible REST interface, QR authentication workflow, and multi-number multi-assessor patterns."
version: "1.0.0"
author: Hermes Agent
type: ToolIntegration
timestamp: 2026-07-16T00:00:00Z
metadata:
  hermes:
    tags: [whatsapp, baileys, zapi, automation, python, nodejs, rest]
  dependencies:
    python: [requests]
    nodejs: ["@whiskeysockets/baileys", "express", "@hapi/boom"]
---

# WhatsApp Automation (Baileys)

Automate WhatsApp messaging from Python without paying for third-party APIs. Uses a local Node.js bridge that wraps [@whiskeysockets/baileys](https://github.com/WhiskeySockets/Baileys) (WhatsApp Web protocol) behind a REST API compatible with Z-API interface — drop-in replacement.

## When to Use

- Python project needs to send WhatsApp messages (text, PDFs, documents)
- Migrating from Z-API (paid) to Baileys (free, self-hosted)
- Multiple WhatsApp numbers needed (multi-assessor, multi-agent)
- Need full control over the messaging pipeline (no third-party dependency)

## Architecture

```
Python App                  Node.js Bridge              WhatsApp
+--------------+    HTTP     +------------------+    WebSocket    +----------+
| whatsapp.py  | ----------> | baileys_service  | --------------> | WhatsApp |
| (cliente     | <---------- | (Express +       | <-------------- | Web      |
|  REST)       |    JSON     |  Baileys socket)  |               +----------+
+--------------+             +------------------+
                                    |
                              sessions/
                              assessor1/
                                creds.json
```

## Quickstart

### 1. Baileys Bridge (Node.js)

The bridge exposes a Z-API-compatible REST API. Full reference at `references/baileys-bridge-server.js`.

```bash
npm install @whiskeysockets/baileys express @hapi/boom

# Start (first run: scan QR code with WhatsApp)
PORT=3100 ASSESSOR_NOME="Joao" node baileys_service.js
```

Endpoints:

| Method | Path | Z-API Equivalent | Description |
|--------|------|------------------|-------------|
| GET | `/health` | — | Connection status |
| GET | `/phone-exists/:phone` | `phone-exists/{phone}` | Check if number has WhatsApp |
| POST | `/send-text` | `send-text` | Send text message `{phone, message}` |
| POST | `/send-document/pdf` | `send-document/pdf` | Send PDF `{phone, document, fileName}` |

### 2. Python Client

Full reference at `references/whatsapp_client.py`. Core class:

```python
from whatsapp import BaileysClient

client = BaileysClient(base_url="http://localhost:3100")

# Check number
lid = client.phone_exists("5511999999999")

# Send text
client.send_text(lid, "Ola! Segue seu relatorio")

# Send PDF + text (full flow)
client.send_pdf_and_text(
    telefone="5511999999999",
    pdf_path="/tmp/relatorio.pdf",
    pdf_name="XPerformance_Marco.pdf",
    message="Bom dia! Sua carteira rendeu *122% do CDI*."
)
```

## Multi-Assessor / Multi-Instance Pattern

When multiple WhatsApp numbers are needed (one per assessor), use prefixed environment variables and isolated service instances:

```bash
# .env
ASSESSORES_ATIVOS=1,2

ASSESSOR_1_NOME="Joao Silva"
ASSESSOR_1_WHATSAPP_SERVICE_URL="http://localhost:3100"
ASSESSOR_1_ID_PASTA_PENDENTES="..."

ASSESSOR_2_NOME="Maria Oliveira"
ASSESSOR_2_WHATSAPP_SERVICE_URL="http://localhost:3101"
ASSESSOR_2_ID_PASTA_PENDENTES="..."
```

Each instance gets:
- **Own port** (3100, 3101, ...)
- **Own session directory** (sessions/assessor1/, sessions/assessor2/)
- **Own QR code** (scan each WhatsApp account once)
- **Independent lifecycle** (restart one without affecting others)

Reference config loader at `references/multi_assessor_config.py`.

## Pitfalls

### WhatsApp Web Limitations
- **No group messaging** in basic mode
- **QR code expires** after ~20 seconds — start the bridge with phone ready
- **WhatsApp bans** possible with aggressive sending — respect rate limits

### Session Persistence
- Session stored in `baileys_sessions/creds.json`
- If deleted, new QR code required — back up `creds.json`
- Different assessors MUST use different session directories

### Rate Limiting
- WhatsApp Web has undocumented rate limits
- Keep messages under 8 per execution batch
- PDFs over 10MB may fail — keep reports lean

### Z-API Compatibility
- Bridge accepts raw phone numbers but uses `@s.whatsapp.net` JIDs internally
- `phone-exists` returns `{exists, lid}` — same format as Z-API
- PDF delivery uses base64 data URIs (same as Z-API `send-document/pdf`)

## Migration Checklist (Z-API to Baileys)

1. Install Node.js 18+ on host
2. `npm install` bridge dependencies
3. Start bridge, scan QR code with assessor WhatsApp
4. Verify: `curl http://localhost:3100/health` -> `{"status":"connected"}`
5. Test text: `curl -X POST http://localhost:3100/send-text -H "Content-Type: application/json" -d '{"phone":"55SEUNUMERO","message":"teste"}'`
6. Update `.env`: `ZAPI_URL` -> `WHATSAPP_SERVICE_URL=http://localhost:3100`
7. Remove `ZAPI_CLIENT_TOKEN` (not needed by Baileys)
8. Run pipeline and verify delivery

## References

| File | Purpose |
|------|---------|
| `references/baileys-bridge-server.js` | Full Node.js bridge server (Z-API compatible REST API) |
| `references/whatsapp_client.py` | Python client class with phone-exists, send-text, send-pdf-and-text |
| `references/multi_assessor_config.py` | Multi-instance config loader with prefixed env vars |
