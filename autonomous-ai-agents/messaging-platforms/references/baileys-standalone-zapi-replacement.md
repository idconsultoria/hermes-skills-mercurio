# Baileys Standalone — Z-API Replacement Pattern

Building a **standalone** Baileys REST bridge that mimics the Z-API interface, enabling cost-free migration of Python projects away from paid WhatsApp APIs.

## When to use this pattern

- You have a Python project that currently uses Z-API (or similar paid WhatsApp REST API)
- You want to eliminate per-instance costs by connecting directly to WhatsApp Web
- You need multi-assessor/multi-tenant isolation (each WhatsApp number gets its own bridge instance)
- You're NOT using the Hermes-internal WhatsApp bridge (port 3000, self-chat mode) — this is for **external** projects

## Architecture

```
Python Project (src/whatsapp.py)
    │
    │  HTTP (localhost:3100)
    ▼
Baileys REST Bridge (Node.js + Express)
    │
    │  WebSocket (WhatsApp Web protocol)
    ▼
WhatsApp Web Servers
```

The bridge exposes **Z-API-compatible** REST endpoints so the migration is a URL change, not a code rewrite.

## Bridge Implementation

### Node.js Service (`baileys_service.js`)

Key dependencies: `@whiskeysockets/baileys`, `express`, `qrcode`

```javascript
const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const QRCode = require('qrcode');

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
        auth: state,
        version,
        defaultQueryTimeoutMs: 60_000,
        // printQRInTerminal: true  ← DEPRECATED in v6!
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, qr } = update;

        if (qr) {
            // Generate QR as PNG data URL and ASCII for terminal
            QRCode.toDataURL(qr, { width: 400 })
                .then(dataUrl => { /* serve via GET /qr */ });
            QRCode.toString(qr, { type: 'terminal', small: true })
                .then(ascii => console.log(ascii));
        }

        if (connection === 'open') {
            isConnected = true;
        }
    });
}
```

### REST Endpoints (Z-API compatible)

| Endpoint | Method | Z-API Equivalent | Description |
|----------|--------|-----------------|-------------|
| `/health` | GET | — | Connection status (`connected`/`awaiting_qr`/`disconnected`) |
| `/qr` | GET | — | QR code as base64 PNG (for headless auth) |
| `/phone-exists/:phone` | GET | `phone-exists/{phone}` | Check if number has WhatsApp, returns `{exists, lid}` |
| `/send-text` | POST | `send-text` | Send text message `{phone, message}` |
| `/send-document/pdf` | POST | `send-document/pdf` | Send PDF `{phone, document: "base64...", fileName}` |

### Multi-Assessor / Multi-Tenant Setup

Each WhatsApp number runs its own bridge instance with isolated:

- **Port** — `PORT=3100`, `PORT=3101`, etc.
- **Session directory** — `SESSION_DIR=./sessions/assessor1`
- **Environment** — `ASSESSOR_NOME="Joao Silva"`

```bash
# Assessor 1
PORT=3100 ASSESSOR_NOME="Joao Silva" SESSION_DIR="./sessions/assessor1" node baileys_service.js &

# Assessor 2
PORT=3101 ASSESSOR_NOME="Maria Oliveira" SESSION_DIR="./sessions/assessor2" node baileys_service.js &
```

### Python Client (`src/whatsapp.py`)

```python
class BaileysClient:
    def __init__(self, base_url="http://localhost:3100"):
        self.base_url = base_url

    def phone_exists(self, telefone: str) -> str | None:
        """Returns @lid or None"""
        ...

    def send_text(self, phone: str, message: str) -> bool:
        """Sends WhatsApp text message"""
        ...

    def send_pdf_document(self, phone: str, pdf_path: str, file_name: str) -> bool:
        """Sends PDF as WhatsApp document"""
        ...

    def send_pdf_and_text(self, telefone, pdf_path, pdf_name, message) -> bool:
        """Full flow: validate → send PDF → send text"""
        ...
```

## Pitfalls

### QR Deprecation in Baileys v6

`printQRInTerminal: true` is silently ignored. Must handle QR via `connection.update` event:

```javascript
sock.ev.on('connection.update', ({ qr }) => {
    if (qr) {
        // Manual QR rendering required
        QRCode.toDataURL(qr).then(dataUrl => { ... });
    }
});
```

### Datacenter IP Blocking

**WhatsApp Web blocks connections from hosting provider IPs** (Oracle Cloud, AWS, GCP, etc.). The bridge may:
- ✅ Generate QR codes (auth handshake succeeds)
- ❌ Fail WebSocket connection with `Connection Failure`

**Oracle Cloud ARM VM (Ampere) — confirmed blocked.** The bridge starts, HTTP server responds, QR code generates, but every WebSocket attempt fails with:
```
Error: Connection Failure
    at WebSocketClient.<anonymous> (socket.js:515)
```
Followed by a reconnect loop every 3s, incrementing delay up to 30s. This is network-level blocking by WhatsApp — not a code issue. Testing connectivity from the target host before committing is essential. Residential IP or mobile hotspot tethering may work.

### QR Timeout

Baileys v6 QR codes expire fast (~60s). Set `qrTimeout` in `makeWASocket()` options. In headless deployments, always expose `GET /qr` to fetch a fresh QR remotely.

### Session Persistence

Sessions are stored in `SESSION_DIR` as multiple files (`creds.json`). After first QR scan, subsequent restarts reuse the session — no QR needed unless logged out. Never commit session files to git.

## Deployment

### Quick Install

```bash
npm install @whiskeysockets/baileys express @hapi/boom qrcode
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY baileys_service.js .
RUN mkdir -p /app/baileys_sessions
EXPOSE 3100
ENV PORT=3100 SESSION_DIR=/app/baileys_sessions ASSESSOR_NOME="Assessor"
CMD ["node", "baileys_service.js"]
```

Volume-mount sessions for persistence across container rebuilds: `-v $(pwd)/sessions:/app/baileys_sessions`.

## Migrating from Z-API

The bridge endpoints mirror Z-API's interface:

| Z-API Call | Baileys Equivalent |
|---|---|
| `GET .../phone-exists/{phone}` | `GET /phone-exists/{phone}` |
| `POST .../send-text` with `{phone, message}` | `POST /send-text` with `{phone, message}` |
| `POST .../send-document/pdf` with `{phone, document, fileName}` | `POST /send-document/pdf` with `{phone, document, fileName}` |

**Migration steps:**
1. Start the Baileys bridge on a residential-IP host
2. Scan QR code to authenticate the assessor's WhatsApp
3. Change `WHATSAPP_SERVICE_URL` from `https://api.z-api.io/instances/...` to `http://localhost:3100`
4. Remove `ZAPI_CLIENT_TOKEN` — no longer needed
5. The Python client code stays identical (same payload format)
