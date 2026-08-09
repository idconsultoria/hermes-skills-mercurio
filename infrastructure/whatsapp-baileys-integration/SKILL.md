---
name: whatsapp-baileys-integration
description: "Integrate WhatsApp into Python via Baileys — lifecycle, QR auth, REST bridge.

Load this skill when you need to send WhatsApp messages from Python without paid APIs. Covers full lifecycle management (spawn, QR auth, session persistence, health checks, graceful shutdown), REST bridge with Z-API compatible interface for file/media delivery, and multi-number architecture. Replaces paid Z-API with local WhatsApp Web. Absorveu messaging/whatsapp-automation (merge 08/2026): migration checklist Z-API→Baileys, rate limiting, WhatsApp Web limitations e reference files (baileys-bridge-server.js, whatsapp_client.py, multi_assessor_config.py)."
version: 1.1.0
type: ToolIntegration
tags: [whatsapp, baileys, messaging, nodejs, subprocess, automation, zapi-migration]
timestamp: 2026-08-09T05:08:04Z
---

# WhatsApp via Baileys — Python Integration

Send WhatsApp messages from Python pipelines using Baileys (WhatsApp Web) as a managed Node.js subprocess. Replaces paid APIs like Z-API with a local, free alternative.

## Architecture

```
┌─ Python pipeline ──────────────────────────────────────┐
│                                                        │
│  BaileysManager.iniciar()                              │
│    └→ subprocess: node baileys_service.js              │
│         └→ Express HTTP :3100                          │
│              └→ Baileys WebSocket ↔ WhatsApp (Meta)    │
│                                                        │
│  BaileysClient (HTTP para localhost:3100)              │
│    ├── phone_exists(telefone)                          │
│    ├── send_text(phone, message)                       │
│    ├── send_pdf_document(phone, pdf_path, file_name)   │
│    └── send_pdf_and_text(phone, pdf_path, name, msg)  │
│                                                        │
│  BaileysManager.encerrar()                             │
│    └→ SIGTERM → salva sessão → exit                   │
└────────────────────────────────────────────────────────┘
```

## Session Persistence

Sessions survive between executions via the `creds.json` file:

```
sessions/assessor1/
├── creds.json          ← TUDO que importa (autenticação)
├── pre-key-*.json      ← chaves efêmeras de criptografia
└── app-state-sync-*.json
```

- **First run**: no session → QR code generated → user scans → `creds.json` saved
- **Subsequent runs**: `creds.json` exists → connects in 2-5s without QR
- **Expired session** (>2 weeks offline): QR needed again

## BaileysManager — Python Side

```python
from src.whatsapp import BaileysManager

manager = BaileysManager(
    session_dir="./sessions/assessor1",
    porta=3100
)

# Liga → conecta → usa → desliga
if not manager.iniciar(timeout=45):
    print("WhatsApp não conectou — verifique QR ou sessão")
    sys.exit(1)

client = manager.client

# Pipeline normal
client.phone_exists("5511999999999")
client.send_pdf_and_text(
    "5511999999999",
    "/tmp/relatorio.pdf",
    "XPerformance_Cliente.pdf",
    "Olá! Segue seu relatório. 📊"
)

manager.encerrar()  # SIGTERM → salva sessão
```

## Baileys Service — Node.js Side

The `baileys_service.js` exposes a REST API compatible with Z-API's interface:

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/health` | GET | — | `{"status":"connected","has_qr":false}` |
| `/qr` | GET | — | `{"qr":"data:image/png;base64,..."}` |
| `/phone-exists/:phone` | GET | — | `{"exists":true,"lid":"55...@s.whatsapp.net"}` |
| `/send-text` | POST | `{"phone":"...","message":"..."}` | `{"success":true}` |
| `/send-document/pdf` | POST | `{"phone":"...","document":"base64...","fileName":"..."}` | `{"success":true}` |

## QR Code Handling

Baileys v6+ deprecated `printQRInTerminal`. Fix:

1. Install `qrcode` npm package
2. Listen to `connection.update` event for `qr` field
3. Generate PNG via `QRCode.toDataURL(qr)`
4. Expose via `GET /qr` endpoint
5. Python side: `BaileysManager._salvar_qr()` fetches and saves to disk

**⚠️ Ao entregar o QR ao usuário:** instrua explicitamente para escanear **DENTRO do WhatsApp** (Configurações → Aparelhos Pareados → Escanear QR Code). A câmera normal do celular NÃO funciona — se o usuário fizer isso, o QR é consumido incorretamente e você precisa matar o processo, limpar o diretório de sessão, e reiniciar para gerar um novo.

## Pairing Code (Fallback quando QR falha com 428)

Quando o QR Code é rejeitado pelo WhatsApp (erro 428), o método de **código de pareamento** é o fallback mais confiável. Em vez de escanear QR, o usuário digita um código no próprio WhatsApp.

### Fluxo

```
Baileys → WhatsApp: "pareia com 5579984233338"
WhatsApp → Baileys: código "TA65-DJMT"
Usuário: WhatsApp → Disp. Conectados → "Vincular com nº de telefone" → digita código
WhatsApp → Baileys: autenticado → creds.json salvo
```

### Implementação no baileys_service.js

```js
// NOVO endpoint: GET /pairing-code/:phone
app.get('/pairing-code/:phone', async (req, res) => {
    if (!sock || isConnected) {
        return res.json({ error: 'Socket not ready or already connected' });
    }
    try {
        const code = await sock.requestPairingCode(req.params.phone);
        res.json({ code, formatted: code?.match(/.{1,4}/g)?.join('-') });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
```

### Configuração obrigatória no `makeWASocket`

```js
const sock = makeWASocket({
    auth: state,
    version,
    browser: ["Windows", "Chrome", "114.0.5735.198"],  // ← obrigatório
    defaultQueryTimeoutMs: undefined,                     // ← obrigatório p/ cloud
    connectTimeoutMs: 60_000,
    qrTimeout: 60_000,
});
```

**Sem `browser: Windows/Chrome` e `defaultQueryTimeoutMs: undefined`, o `requestPairingCode` também falha com 428/401.**

### Uso

```bash
# Requisitar código para o número 55 79 9842-3338
curl http://localhost:3100/pairing-code/557998423338
# → {"code":"TA65-DJMT","formatted":"TA65-DJMT"}
```

O código do endpoint está em `templates/pairing-code-endpoint.js` — adicione ao `baileys_service.js` antes da seção de envio de mensagens.

O usuário então abre WhatsApp → Dispositivos Conectados → "Vincular com número de telefone" → digita o código. O `creds.json` é salvo automaticamente igual ao fluxo QR.

## Error 428 — Connection Terminated by Server

Error `428` (DisconnectReason.connectionClosed) during QR pairing means WhatsApp rejects the connection before the QR can be scanned. **Fixes that work (July 2026):**

1. **Set browser UA to Windows/Chrome** — default `["Ubuntu", "Chrome", "22.04.4"]` is blocked:
   ```js
   browser: ['Windows', 'Chrome', '114.0.5735.198'],
   ```
2. **Set `defaultQueryTimeoutMs: undefined`** — explicit `undefined` prevents cloud timeout during pairing handshake (Issue #390).

Both fixes must be in `makeWASocket()` config. See issues #1382, #2008, #390.

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Baileys morre no meio da pipeline | `subprocess.PIPE` enche o buffer de stdout | Use `stdout=subprocess.DEVNULL` no Popen |
| Conexão recusada após alguns envios | WhatsApp bane IP de datacenter | Use VM com IP residencial ou proxy |
| QR code expira rápido | Timeout padrão do Baileys é ~60s | Gere e exiba imediatamente; o QR é renovado a cada reconexão |
| Sessão expira após semanas offline | WhatsApp revoga sessões inativas | Monitore `/health` no início e alerte se `awaiting_qr` |
| `printQRInTerminal` deprecated | API do Baileys mudou na v6 | Use `qrcode` npm + endpoint REST (ver seção QR Code Handling) |
| Usuário escaneia QR com câmera normal do celular | Confusão comum — o QR do WhatsApp Web só é lido pelo scanner interno do app | **Sempre instrua:** "Escaneie DENTRO do WhatsApp → Configurações → Aparelhos Pareados → Escanear QR Code". Se escanear errado, mate o processo, limpe `sessions/<N>/` e reinicie. |
| **Erro 428 "Connection Terminated by Server"** ao escanear QR (usuário reporta "não foi possível conectar") | WhatsApp rejeita o handshake de pareamento por 3 motivos: (1) browser UA string padrão é Linux de datacenter → rejeitada, (2) IP de cloud provider sofre mais escrutínio, (3) `defaultQueryTimeoutMs` não definido como `undefined` | **Correções no `makeWASocket`:** `browser: ["Windows", "Chrome", "114.0.5735.198"]`, `defaultQueryTimeoutMs: undefined`. Se persistir, use pairing code em vez de QR (ver seção Pairing Code). Ver `references/baileys-428-error.md` para detalhes. |
| `File not found` no Google Doc/Planilha/Pasta mesmo após compartilhar | Você compartilhou com a service account ERRADA (ex: a do Drive, não a do Cloud Run) | Verificar qual SA o job usa via `gcloud run jobs describe`. A compute default é `PROJECT_NUMBER-compute@developer.gserviceaccount.com`. A service account do Drive é uma conta diferente que NÃO tem permissão de Cloud Run. |
| Job usa IDs do Drive do ambiente de teste em vez dos IDs corretos do projeto original | Múltiplos ambientes (teste vs produção) têm IDs diferentes para pastas/planilhas/documentos | Confirmar a FONTE dos IDs. O `.env.example` do projeto original contém os IDs corretos. Usar `gcloud run jobs describe <job-existente>` como referência de env vars atuais. |
| `YAML parse error` ao usar `--env-vars-file` com JSON de service account | YAML exige indentação no conteúdo de block scalar `|` | O JSON abaixo de `ASSESSOR_N_GOOGLE_CREDENTIALS_JSON: |` precisa estar indentado 2 espaços. Gerar com Python: `json.dumps(sa, indent=2)` + indentar cada linha. |

## Cloud Run Job Pattern (liga → usa → desliga)

Para execuções diárias batch: o Baileys NÃO fica 24/7. Cada job inicia o subprocesso, conecta (reusa sessão), executa o pipeline e encerra. Tempo típico: ~2s para conectar (com sessão) + pipeline.

### Session as Environment Variable (sem volume)

A sessão é armazenada como string base64 em `ASSESSOR_<N>_BAILEYS_CREDS_B64`. O entrypoint decodifica no início de cada job. As chaves de identidade no `creds.json` são de longo prazo — o mesmo arquivo funciona por meses.

```bash
# Gerar: cat sessions/1/creds.json | base64 -w0
# entrypoint.sh:
echo "${ASSESSOR_PREFIX}_BAILEYS_CREDS_B64" | base64 -d > "sessions/${ASSESSOR_PREFIX##ASSESSOR_}/creds.json"
```

Zero infra extra: sem Secret Manager, sem volume GCS, sem estado entre execuções.

### main.py — Assessor Único por Job

```python
from src.config import get_config
from src.whatsapp import BaileysManager
from src.orquestrador import executar

config = get_config()  # lê ASSESSOR_PREFIX (default: ASSESSOR_1)
prefixo = os.environ.get("ASSESSOR_PREFIX", "ASSESSOR_1")

manager = BaileysManager(
    session_dir=f"./sessions/{prefixo.split('_')[-1]}",
    porta=3100
)
manager.iniciar(timeout=45)
executar(config, whatsapp_client=manager.client)
manager.encerrar()
```

### Multi-Assessor via Cloud Run Jobs (Arquitetura Isolada)

**Cada Cloud Run Job é um ambiente isolado.** Todo job usa `ASSESSOR_PREFIX=ASSESSOR_1` — o que diferencia os assessores são OS VALORES das env vars, não o prefixo.

```bash
# ── Job 1: Assessor XP ───────────────────────────
gcloud run jobs deploy xperformance-assessor-teste \
  --image=gcr.io/.../augmentacao-assessores:latest \
  --region=us-east1 --cpu=1 --memory=2Gi --task-timeout=1200s \
  --command=./entrypoint.sh \
  --set-env-vars="ASSESSOR_PREFIX=ASSESSOR_1,ASSESSOR_1_NOME=Assessor XP,..."

# ── Job 2: Assessor Igor (job separado, mesmas envs mas outro número) ──
gcloud run jobs deploy assessor-igor \
  --image=gcr.io/.../augmentacao-assessores:latest \
  --region=us-east1 --cpu=1 --memory=2Gi --task-timeout=1200s \
  --command=./entrypoint.sh \
  --set-env-vars="ASSESSOR_PREFIX=ASSESSOR_1,ASSESSOR_1_NOME=Igor Rodrigues,..."
```

O entrypoint (`entrypoint.sh`) decodifica `${ASSESSOR_PREFIX}_BAILEYS_CREDS_B64` para `sessions/${PREFIX##ASSESSOR_}/creds.json`:
- `ASSESSOR_PREFIX=ASSESSOR_1` → `sessions/1/creds.json`
- Cada job tem seu próprio filesystem efêmero → sem conflito entre jobs.

**NUNCA use `ASSESSORES_ATIVOS=1,2` em um job só com Cloud Run.** NUNCA crie scripts avulsos. A infra é Cloud Run Jobs com env vars.

### Deploy Workflow para Novo Assessor

Sempre criar um `/plan.md` antes de executar deploys. Passos:

1. **Verificar jobs existentes** (referência de env vars):
   ```bash
   gcloud run jobs list --region=us-east1
   gcloud run jobs describe xperformance-assessor-teste --region=us-east1
   ```

2. **Criar env-vars.yaml** com os IDs de Google Drive/Sheets/Docs. **⚠️ Confirme a FONTE dos IDs:**
   - O job legado original (ex: Agemini) tem seus próprios IDs
   - O ambiente de teste pode ter IDs DIFERENTES
   - Sempre verificar no `.env.example` do projeto ORIGINAL quais IDs usar
   - `gcloud run jobs describe <job-existente>` mostra as env vars atuais como referência
   
   Alterar apenas:
   - `ASSESSOR_1_NOME` → nome do novo assessor
   - `ASSESSOR_1_BAILEYS_CREDS_B64` → base64 do creds.json do novo número

3. **Gerar creds do WhatsApp** para o novo número:
   - Rodar `baileys_service.js` com sessão limpa
   - Escanear QR (DENTRO do WhatsApp, nunca com câmera normal)
   - Extrair base64: `base64 -w0 sessions/<N>/creds.json`

4. **Deploy**:
   ```bash
   gcloud run jobs deploy assessor-igor \
     --image=gcr.io/idata-421415/augmentacao-assessores:latest \
     --region=us-east1 --cpu=1 --memory=2Gi --task-timeout=1200s \
     --max-retries=3 --command=./entrypoint.sh \
     --env-vars-file=env-vars-igor.yaml
   ```

5. **Testar:**
   ```bash
   gcloud run jobs execute assessor-igor --region=us-east1 --wait
   ```

⚠️ **gcloud token expira.** A service account do Drive NÃO tem permissão de Cloud Run. Duas formas de reautenticar:

**Via OAuth interativo (background + pty):**
```bash
terminal(command="gcloud auth login", background=true, pty=true)
process(action="log", session_id="proc_xxx")  # extrair URL
# → enviar URL ao usuário
process(action="submit", session_id="proc_xxx", data="4/0AXEQx...")
```
⚠️ Cada `gcloud auth login` gera um PKCE único. O código NÃO reusa entre chamadas.

**Via service account key (fallback sem interação):**
Se existir uma chave de service account com permissões de Cloud Run no projeto alvo, use-a diretamente:
```bash
gcloud auth activate-service-account --key-file=caminho/da/chave.json
```
Isso evita todo o fluxo browser + código de verificação.

### Variáveis de Ambiente — Job Mínimo

| Variável | Descrição |
|----------|-----------|
| `ASSESSOR_PREFIX` | Qual assessor (default: `ASSESSOR_1`) |
| `ASSESSOR_N_NOME` | Nome do assessor |
| `ASSESSOR_N_BAILEYS_CREDS_B64` | Sessão WhatsApp em base64 |
| `ASSESSOR_N_GEMINI_API_KEY` | Chave Gemini |
| `ASSESSOR_N_GEMINI_MODEL` | Modelo Gemini (default: `gemini-3.1-flash-lite`) |
| `ASSESSOR_N_GOOGLE_CREDENTIALS_JSON` | Service account (1 linha) |
| `ASSESSOR_N_ID_PASTA_PENDENTES` | Drive folder ID |
| `ASSESSOR_N_ID_PASTA_PROCESSADOS` | Drive folder ID |
| `ASSESSOR_N_ID_PLANILHA_CLIENTES` | Sheets spreadsheet ID |
| `ASSESSOR_N_ID_DOC_PERSONALIZACAO` | Docs document ID |
| `ASSESSOR_N_NOME_ABA_CLIENTES` | Sheet tab name (default: `Clientes`) |
| `ASSESSOR_N_NOME_ABA_LOGS` | Sheet tab name (default: `Registros`) |
| `ENVIOS_POR_EXECUCAO` | Limite diário de envios (default: 8) |

## Google Drive + Sheets Integration

Common pitfalls when using service accounts with Google Drive/Sheets in automation pipelines:

- **PT-BR locale**: Sheets default to `Página1`, not `Sheet1`. Rename via API: use `batchUpdate` with the sheet ID (0 for first sheet), not by name.
- **Case-sensitive PROCV**: Python `in` is case-sensitive. `"MARIA" in "XPerformance_Maria.pdf"` → False. Use lowercase IDs in planilha to match filename fragments.
- **Service account loses access after folder move**: When moving a folder you OWNED with user OAuth to a new parent, the service account sharing is inherited from the OLD parent, not the NEW one. Re-share the new parent (and all children) with the service account after any folder reorg.
- **Cloud Run deploy via gcloud**: Build without local Docker (`gcloud builds submit`), auth via PTY, `--task-timeout` (not `--timeout`), `--env-vars-file`. See `references/cloud-run-gcloud-deploy.md`.

## Google Auth on Cloud Run — ADC Fallback

When running on Cloud Run without explicit `ASSESSOR_N_GOOGLE_CREDENTIALS_JSON`, use Application Default Credentials from the job's service account. The config must return `None` instead of raising:

```python
# config.py — NEVER raise when creds not found; return None for ADC
def get_google_credentials(self) -> Optional[dict]:
    if self.google_credentials_json:
        return json.loads(self.google_credentials_json)
    cred_path = os.environ.get("GOOGLE_CREDENTIALS_PATH",
                                "conectores/credenciais/service_account.json")
    if os.path.exists(cred_path):
        with open(cred_path) as f:
            return json.load(f)
    return None  # ← allows ADC, do NOT raise

# orquestrador.py — 3-tier fallback
info = config.get_google_credentials()
if info:
    credenciais = ServiceAccountCredentials.from_service_account_info(info, ...)
else:
    import google.auth
    credenciais, _proj = google.auth.default(scopes=escopos)  # ADC
```

**Pre-requisito:** share Drive/Sheets/Docs with the Cloud Run service account email (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`) as writer. Without this, ADC auth succeeds but 403/404 on API calls.

## Gemini Free Tier — Graceful Fallback on 429

The free tier may return `limit: 0` even with a valid API key. Without handling, 429 kills the pipeline. Catch ALL exceptions in the message generator:

```python
def gerar_mensagem_assessor(...):
    try:
        resposta = chat.send_message([ficheiro, prompt])
        resultado = json.loads(resposta.text)
        return resultado["mensagem_whatsapp"], resultado["resumo_interno"]
    except Exception as e:  # ← catch ALL, not just JSONDecodeError
        print(f"[-] Erro no Gemini: {e}")
        return _gerar_mensagem_fallback(dados_cliente)  # deterministic templates
```

**Model selection via env var.** Pass `config.gemini_model` instead of hardcoding model names. Default to the latest stable flash-lite (`gemini-3.1-flash-lite` as of July 2026). Always check [Google AI docs](https://ai.google.dev/gemini-api/docs/models) for current model IDs before hardcoding.

```python
# config.py
self.gemini_model = self._env("GEMINI_MODEL", "gemini-3.1-flash-lite")

# orquestrador.py — both validation and generation use config.gemini_model
modelo = genai.GenerativeModel(
    model_name=config.gemini_model,  # ← dynamic, not hardcoded
    system_instruction=...,
    generation_config=...,
)
```

Validator and generator share the same model by default; the user can override per job.
    ...
```

Same pattern applies to `validar_relatorio_ativo()` — return `valido=True` as safe default on failure, since "cofre destrava" is better than losing an active client.

## Verified Fix — 428 Error Resolved (Jul 2026)

On Oracle Cloud ARM with Baileys 6.7.23, applying both corrections simultaneously eliminated the 428 loop. The session stabilized and remained in `awaiting_qr` state without reconnection cycles.

```diff
  const sock = makeWASocket({
      auth: state,
      version,
-     defaultQueryTimeoutMs: 60_000,
+     browser: ['Windows', 'Chrome', '114.0.5735.198'],
+     defaultQueryTimeoutMs: undefined,
      connectTimeoutMs: 60_000,
      qrTimeout: 60_000,
  });
```

After applying, verify with `watch -n2 'curl -s localhost:3100/health'` — `reconnect_attempts` should stay at 0 (or 1 for normal QR rotation) instead of climbing rapidly.

## Z-API Migration

Drop-in replacement: mesma interface REST, mesma resposta JSON. Basta trocar a URL base:

```python
# Antes (Z-API):
url = f"https://api.z-api.io/instances/{id}/token/{token}/send-text"

# Depois (Baileys):
url = "http://localhost:3100/send-text"
```

Headers adicionais como `Client-Token` não são necessários no modo local. Para segurança em produção, use firewall (bind apenas em localhost) ou autenticação básica no Express.

For extracting config from a legacy Z-API Cloud Run job and mapping to the `ASSESSOR_N_` format, see `references/legacy-job-migration.md`.

## WhatsApp Web Limitations

- **No group messaging** in basic mode — send only to individual numbers
- **QR code expires** after ~20 seconds — start the bridge with the phone ready
- **WhatsApp bans** possible with aggressive sending — respect rate limits

## Rate Limiting

- WhatsApp Web has undocumented rate limits
- Keep messages under 8 per execution batch
- PDFs over 10MB may fail — keep reports lean

## Z-API Compatibility Details

- Bridge accepts raw phone numbers but uses `@s.whatsapp.net` JIDs internally
- `phone-exists` returns `{exists, lid}` — same format as Z-API
- PDF delivery uses base64 data URIs (same as Z-API `send-document/pdf`)
- Headers adicionais como `Client-Token` não são necessários no modo local

## Migration Checklist (Z-API → Baileys)

1. Install Node.js 18+ on host
2. `npm install` bridge dependencies
3. Start bridge, scan QR code with assessor WhatsApp
4. Verify: `curl http://localhost:3100/health` → `{"status":"connected"}`
5. Test text: `curl -X POST http://localhost:3100/send-text -H "Content-Type: application/json" -d '{"phone":"55SEUNUMERO","message":"teste"}'`
6. Update `.env`: `ZAPI_URL` → `WHATSAPP_SERVICE_URL=http://localhost:3100`
7. Remove `ZAPI_CLIENT_TOKEN` (not needed by Baileys)
8. Run pipeline and verify delivery

## References (merged from whatsapp-automation)

| File | Purpose |
|------|---------|
| `references/baileys-bridge-server.js` | Full Node.js bridge server (Z-API compatible REST API) |
| `references/whatsapp_client.py` | Python client class with phone-exists, send-text, send-pdf-and-text |
| `references/multi_assessor_config.py` | Multi-instance config loader with prefixed env vars |
