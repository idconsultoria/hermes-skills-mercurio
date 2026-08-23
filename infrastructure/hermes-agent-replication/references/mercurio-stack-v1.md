# Inventário do ambiente Mercúrio (22/08/2026)

Fonte: recon do ambiente vivo durante a replicação v1. Use como BOM para cópia 1:1.

## Container / rede
- Container `hermes_mercurio`, rede Docker `ai_mesh`, `HERMES_HOME=/opt/data`.
- Compose no host: `/home/ubuntu/selfhost/mercurio/`.
- Gateway Telegram conectado — bot `mercurio_id_bot`.
- `restart: unless-stopped` + `HERMES_GATEWAY_BOOTSTRAP_STATE=running` (sobe sozinho).
- Daemon Docker NÃO acessível de dentro do container (builds de imagem de SO: no host).

## Runtime
- Oracle Cloud ARM64 (kernel 6.17), Ubuntu.
- Python 3.13.5, Node v26.5.1, npm 11.17.0.
- Hermes em `/opt/hermes` (binário `/opt/hermes/bin/hermes`); state em `/opt/data`.
- tirith: `/opt/data/bin/tirith`.

## Modelo / provider
- default `deepseek-v4-flash` via `opencode-go`. Fallbacks (ordem):
  `deepseek-v4-flash-free`(opencode-zen) → `mimo-v2.5`(opencode-go) → `mimo-v2.5-free`(opencode-zen).
- Auxiliares (visão/compressão): `gemini-flash-lite-latest` via `gemini`.

## Chaves do .env (nomes — valores a rotacionar)
TELEGRAM_BOT_TOKEN, TELEGRAM_HOME_CHANNEL, TELEGRAM_ALLOWED_USERS, OPENCODE_GO_API_KEY,
OPENCODE_ZEN_API_KEY, GOOGLE_API_KEY, GITHUB_TOKEN, API_SERVER_KEY, FIRECRAWL_API_KEY,
FIRECRAWL_API_URL.

Allow-list DM Telegram: Gustavo(6171996969), Cleverton(8600141184), Maxwell(8888381551),
Tacio(609921578).

## Config key
web.backend=firecrawl · web.search_backend=ddgs · browser.cdp_url=http://chrome-cdp:9223 ·
terminal.backend=local · approvals.mode=smart · security.redact_secrets=true ·
memory.memory_enabled=true · tts.provider=hermes-tts (script Gemini, voz Fenrir) ·
stt.provider=local · plugins.enabled=[context-kb] · timezone='' (display BRT).

## Repositorios
- Skills: clone git de `gustavomello9600/hermes-skills-mercurio` (branch master, 138 skills).
- KB: `gustavomello9600/hermes-context-kb` (dir `context-kb/` é consumer passivo, sem .git no volume).
- Spec/install da rama: `gustavomello9600/hermes-mercurio` (`install-mercurio.sh`) — 404 via
  desautenticado; provável privado. Fonte de verdade = recon do ambiente vivo.

## Skills-core do Mercúrio
hermes-agent · id-design-guide · pi-agent-coordination · product-pipeline · opencode ·
merge-reconciler · elaboracao-proposta-comercial · planejamento-estrategico-2h · emissao-nfse ·
inter-api-id-consultoria · gestao-financeira-id · augmentacao-query · augmentation-process-design ·
valuation-consultivo · md-to-timbrado-id · id-papel-timbrado · html-report-hermes ·
html-to-pdf-chromium · xlsx · docx.

## Plugins
- `plugins/context-kb` (único habilitado): engine.py / tools.py / schemas.py / plugin.yaml.
  Ferramentas kb_search/kb_read/kb_status/kb_map, filtro `scope:id` no load, consumo passivo.

## Venvs / scripts
- `/opt/data/venvs/google` — Google (google-api-python-client 2.198.0, google-auth 2.56.3,
  google-auth-oauthlib 1.4.0, httplib2, protobuf, requests, cryptography, Pillow).
- `/opt/data/scripts/` — hermes-tts-mercurio.py (TTS), buscar_aliquota_iss.sh/.py (ISS),
  check_inter_api.py, inter_api_detail.py, runner/watchdog-idata-diario.sh (Banco Inter→planilha),
  whatsapp-bridge/ (Baileys, node).

## Motor NFS-e
- `/opt/data/id-nfse-motor` — Aracaju (2800308) = protocolo NFS-e NACIONAL → DPS via nfelib.
- Multi-stage Docker (ARM64), runtime não-root `idmotor`, TPAMB=2. Imagem: `id-nfse-motor`.
- requirements: nfelib==2.5.2, pynfse-nacional==0.9.5, erpbrasil.edoc==3.1.1,
  erpbrasil.transmissao==1.1.0, erpbrasil.assinatura==1.8.0, erpbrasil.base==2.4.2,
  xsdata==26.2, signxml==5.1.0, zeep==4.3.3, lxml==6.1.1, requests==2.34.2, pydantic==2.13.4.

## Cron (jobs.json)
- `Alíquota ISS mensal (ID)` — `0 10 5 * *` (dia 5, 10h), agente + fallback manual,
  script buscar_aliquota_iss.sh, grava `id-nfse-motor/dados/aliquota_iss.json`.
- `iData diário (Banco Inter → planilha de Gestão)` — `0 7 * * *`, no_agent,
  watchdog-idata-diario.sh (última run com erro de auth no Inter).

## Pendencias conhecidas
- Certificado A1 e-CNPJ expirado (renovação conduzida pela contabilidade AAD).
- iData/Inter: falha de autenticação — validar credencial ao reimplementar.