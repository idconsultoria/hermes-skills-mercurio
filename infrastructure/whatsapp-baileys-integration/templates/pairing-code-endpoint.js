// ── Pairing Code (fallback quando QR falha com 428) ────────
// Adicione este bloco ANTES do `// ── Envio de mensagens ──` no baileys_service.js
//
// Uso: curl http://localhost:3100/pairing-code/557998423338
// O usuário digita o código retornado no WhatsApp:
//   Dispositivos Conectados → "Vincular com número de telefone"

app.get('/pairing-code/:phone', async (req, res) => {
    if (!sock) {
        return res.status(503).json({ error: 'Socket não inicializado' });
    }
    if (isConnected) {
        return res.json({ error: 'WhatsApp já está conectado', hint: 'Use /health para verificar' });
    }
    try {
        const code = await sock.requestPairingCode(req.params.phone);
        console.log(`[${ASSESSOR_NOME}] 📱 Código de pareamento: ${code}`);
        res.json({ 
            code, 
            formatted: code?.match(/.{1,4}/g)?.join('-'),
            phone: req.params.phone,
        });
    } catch (err) {
        console.error(`[${ASSESSOR_NOME}] Erro no pairing code:`, err.message);
        res.status(500).json({ 
            error: err.message,
            hint: 'Verifique se browser está como ["Windows", "Chrome", "114.0.5735.198"] e defaultQueryTimeoutMs: undefined'
        });
    }
});
