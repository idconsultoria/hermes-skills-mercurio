/**
 * Baileys WhatsApp Web Gateway — produção-ready.
 *
 * Endpoints REST (compatíveis Z-API):
 *   GET  /health, /qr, /phone-exists/:phone
 *   POST /send-text, /send-document/pdf
 *
 * Uso:
 *   PORT=3100 SESSION_DIR=./sessions node baileys_service.js
 *
 * Dependências:
 *   npm install @whiskeysockets/baileys express qrcode @hapi/boom
 */
const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const QRCode = require('qrcode');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3100;
const SESSION_DIR = process.env.SESSION_DIR || path.join(__dirname, 'baileys_sessions');
const ASSESSOR_NOME = process.env.ASSESSOR_NOME || 'Assessor';

const app = express();
app.use(express.json({ limit: '50mb' }));

let sock = null;
let isConnected = false;
let qrCodeData = null;
let qrCodeImage = null;
let reconnectAttempts = 0;
const MAX_RECONNECT = 10;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({ auth: state, version, defaultQueryTimeoutMs: 60_000 });

    sock.ev.on('creds.update', saveCreds);
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            qrCodeData = qr;
            QRCode.toDataURL(qr, { width: 400, margin: 2 })
                .then(dataUrl => { qrCodeImage = dataUrl; })
                .catch(() => {});
            QRCode.toString(qr, { type: 'terminal', small: true }, () => {});
        }

        if (connection === 'open') {
            isConnected = true;
            qrCodeData = null;
            qrCodeImage = null;
            reconnectAttempts = 0;
        }

        if (connection === 'close') {
            isConnected = false;
            const statusCode = lastDisconnect?.error instanceof Boom
                ? lastDisconnect?.error?.output?.statusCode : null;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

            if (shouldReconnect && reconnectAttempts < MAX_RECONNECT) {
                reconnectAttempts++;
                setTimeout(connectToWhatsApp, Math.min(3000 * reconnectAttempts, 30000));
            }
        }
    });
}

app.get('/health', (_req, res) => {
    res.json({
        status: isConnected ? 'connected' : (qrCodeData ? 'awaiting_qr' : 'disconnected'),
        has_qr: !!qrCodeData,
        assessor: ASSESSOR_NOME,
        reconnect_attempts: reconnectAttempts,
        timestamp: new Date().toISOString(),
    });
});

app.get('/qr', (_req, res) => {
    if (!qrCodeImage) return res.status(404).json({ error: 'QR Code não disponível' });
    res.json({ qr: qrCodeImage, type: 'image/png', encoding: 'base64' });
});

app.get('/phone-exists/:phone', async (req, res) => {
    if (!isConnected || !sock) return res.status(503).json({ exists: false, error: 'WhatsApp não conectado' });
    try {
        const [result] = await sock.onWhatsApp(req.params.phone);
        res.json({ exists: !!result?.exists, lid: result?.jid || null, phone: req.params.phone });
    } catch (err) {
        res.status(500).json({ exists: false, error: err.message });
    }
});

app.post('/send-text', async (req, res) => {
    if (!isConnected || !sock) return res.status(503).json({ error: 'WhatsApp não conectado' });
    const { phone, message } = req.body;
    if (!phone || !message) return res.status(400).json({ error: 'phone e message são obrigatórios' });
    try {
        const jid = phone.includes('@s.whatsapp.net') ? phone : `${phone}@s.whatsapp.net`;
        await sock.sendMessage(jid, { text: message });
        res.json({ success: true, phone });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/send-document/pdf', async (req, res) => {
    if (!isConnected || !sock) return res.status(503).json({ error: 'WhatsApp não conectado' });
    const { phone, document, fileName } = req.body;
    if (!phone || !document || !fileName) return res.status(400).json({ error: 'phone, document e fileName são obrigatórios' });
    try {
        const jid = phone.includes('@s.whatsapp.net') ? phone : `${phone}@s.whatsapp.net`;
        const base64Data = document.replace(/^data:application\/pdf;base64,/, '');
        const buffer = Buffer.from(base64Data, 'base64');
        await sock.sendMessage(jid, { document: buffer, fileName, mimetype: 'application/pdf' });
        res.json({ success: true, fileName, phone });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

async function start() {
    if (!fs.existsSync(SESSION_DIR)) fs.mkdirSync(SESSION_DIR, { recursive: true });
    connectToWhatsApp().catch(err => console.error('Erro fatal:', err));
    app.listen(PORT, () => console.log(`Baileys HTTP → http://localhost:${PORT}`));
}
start();
