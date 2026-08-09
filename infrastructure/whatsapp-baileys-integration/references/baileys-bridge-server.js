/**
 * Baileys Bridge Server — WhatsApp Web Gateway
 * ============================================
 *
 * Substituto local da Z-API. Usa @whiskeysockets/baileys para conectar
 * diretamente ao WhatsApp Web, sem custos de API de terceiros.
 *
 * Endpoints REST (compatíveis com Z-API):
 *   GET  /health                  → status do servico
 *   GET  /phone-exists/:phone     → verifica se numero tem WhatsApp
 *   POST /send-text               → envia mensagem de texto
 *   POST /send-document/pdf       → envia documento PDF
 *
 * Autenticacao:
 *   Na primeira execucao, exibe QR Code no terminal.
 *   A sessao e salva em disco e reutilizada nas proximas execucoes.
 *
 * Uso:
 *   npm install @whiskeysockets/baileys express @hapi/boom
 *   PORT=3100 ASSESSOR_NOME="Assessor XP" node baileys-bridge-server.js
 *
 * Variaveis de ambiente:
 *   PORT=3100                     (padrao: 3100)
 *   SESSION_DIR=./baileys_sessions (padrao: ./baileys_sessions)
 *   ASSESSOR_NOME="Assessor XP"   (identificacao nos logs)
 */

const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3100;
const SESSION_DIR = process.env.SESSION_DIR || path.join(__dirname, 'baileys_sessions');
const ASSESSOR_NOME = process.env.ASSESSOR_NOME || 'Assessor';

const app = express();
app.use(express.json({ limit: '50mb' }));

// ── Estado global ──────────────────────────────────
let sock = null;
let isConnected = false;

// ── Conexao WhatsApp ────────────────────────────────
async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR);

    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        defaultQueryTimeoutMs: 60_000,
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect } = update;

        if (connection === 'open') {
            isConnected = true;
            console.log(`[${ASSESSOR_NOME}] WhatsApp conectado`);
        }

        if (connection === 'close') {
            isConnected = false;
            const shouldReconnect =
                lastDisconnect?.error instanceof Boom &&
                lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;

            console.log(`[${ASSESSOR_NOME}] Conexao fechada. Reconectando: ${shouldReconnect}`);

            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 3000);
            } else {
                console.log(`[${ASSESSOR_NOME}] Sessao encerrada. Delete ${SESSION_DIR} para novo QR.`);
            }
        }
    });

    // Aguarda conexao com timeout
    await new Promise((resolve) => {
        const check = setInterval(() => {
            if (isConnected) { clearInterval(check); resolve(); }
        }, 500);
        setTimeout(() => { clearInterval(check); resolve(); }, 120_000);
    });
}

// ── REST API ────────────────────────────────────────

app.get('/health', (_req, res) => {
    res.json({
        status: isConnected ? 'connected' : 'disconnected',
        assessor: ASSESSOR_NOME,
        timestamp: new Date().toISOString(),
    });
});

app.get('/phone-exists/:phone', async (req, res) => {
    if (!isConnected || !sock) {
        return res.status(503).json({ exists: false, error: 'WhatsApp nao conectado' });
    }

    const phone = req.params.phone;

    try {
        const [result] = await sock.onWhatsApp(phone);
        if (result && result.exists) {
            res.json({ exists: true, lid: result.jid, phone: phone });
        } else {
            res.json({ exists: false, phone: phone });
        }
    } catch (err) {
        res.status(500).json({ exists: false, error: err.message });
    }
});

app.post('/send-text', async (req, res) => {
    if (!isConnected || !sock) {
        return res.status(503).json({ error: 'WhatsApp nao conectado' });
    }

    const { phone, message } = req.body;
    if (!phone || !message) {
        return res.status(400).json({ error: 'phone e message sao obrigatorios' });
    }

    try {
        const jid = phone.includes('@s.whatsapp.net') ? phone : `${phone}@s.whatsapp.net`;
        await sock.sendMessage(jid, { text: message });
        res.json({ success: true, phone: phone });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/send-document/pdf', async (req, res) => {
    if (!isConnected || !sock) {
        return res.status(503).json({ error: 'WhatsApp nao conectado' });
    }

    const { phone, document, fileName } = req.body;
    if (!phone || !document || !fileName) {
        return res.status(400).json({ error: 'phone, document e fileName sao obrigatorios' });
    }

    try {
        const jid = phone.includes('@s.whatsapp.net') ? phone : `${phone}@s.whatsapp.net`;
        const base64Data = document.replace(/^data:application\/pdf;base64,/, '');
        const buffer = Buffer.from(base64Data, 'base64');

        await sock.sendMessage(jid, {
            document: buffer,
            fileName: fileName,
            mimetype: 'application/pdf',
        });

        res.json({ success: true, fileName: fileName, phone: phone });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ── Inicializacao ───────────────────────────────────

async function start() {
    console.log(`[${ASSESSOR_NOME}] Iniciando servico Baileys na porta ${PORT}...`);
    console.log(`[${ASSESSOR_NOME}] Sessao: ${SESSION_DIR}`);

    if (!fs.existsSync(SESSION_DIR)) {
        fs.mkdirSync(SESSION_DIR, { recursive: true });
    }

    connectToWhatsApp().catch((err) => {
        console.error(`[${ASSESSOR_NOME}] Erro fatal:`, err);
    });

    app.listen(PORT, () => {
        console.log(`[${ASSESSOR_NOME}] Servidor HTTP: http://localhost:${PORT}`);
    });
}

start();
