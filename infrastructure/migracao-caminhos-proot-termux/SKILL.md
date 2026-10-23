---
name: migracao-caminhos-proot-termux
description: "Corrigir caminhos da casa proot para o Termux nativo."
category: infrastructure
type: ToolIntegration
timestamp: 2026-10-19T02:45:00Z
---

# Migração de caminhos: casa proot → Termux nativo

Use quando um arquivo de perfil/agente citar `/opt/mercurio-data`, `/opt/data`,
`/opt/hermes/bin` ou `.playwright` e o caminho não existir mais (comando quebrado, skill
com runtime morto).

O panteão migrou do proot para um Termux nativo; arquivos antigos (skills, SOUL/AGENTS,
config.yaml, scripts, memories) ainda citam a casa antiga.

## Mapeamento confirmado por existência no disco

- `/opt/mercurio-data` → `/data/data/com.termux/files/home/capitolium`
- `/opt/data/.playwright/chromium-1117` → `$HOME/.hermes/.cache/ms-playwright/chromium-1117`
- `/opt/data/.playwright` → `$HOME/.hermes/.cache/ms-playwright`
- `/opt/data/.hermes` → `$HOME/.hermes/.hermes` (aninhado de propósito: os scripts de
  TTS/STT — gemini-stt, omnivoice-tts, qwen3-tts, hermes-tts — só existem ali)
- `/opt/data` → `$HOME/.hermes`
- `/opt/hermes/bin` → `/data/data/com.termux/files/usr/bin` (o wrapper `hermes` chama
  `$HOME/.hermes/hermes-agent/venv/bin/python`)

Casas: **Capitólio** (romana, ID) = `~/capitolium`; **Olimpo** (grega) = `~/.hermes`.
Perfis do Capitólio: fama, fortuna, jupiter, luperco, netuno, providentia, terminus, vitruvio.

## Classes que NÃO se toca (sem alvo nativo — só reportar)

- `/opt/opendesign-mcp/**` — diretório do host remoto (Oracle) / caminho de contêiner.
- `/opt/data/code/workstation/**` — vive no host (`ssh oracle-host …/shared/code/`).
- `/opt/data/pi-global/**` — o `pi` nativo está em `usr/bin/pi`; o prefixo npm global é
  `usr/lib/node_modules`, sem `@earendil-works` — não inventar alvo.
- `chromium-1129` — build inexistente no nativo (só `chromium-1117`).

## Regra de escrita

Substituição é mecânica, mas **mascarar os protegidos antes** de trocar (token temporário)
e restaurar depois; senão o `/opt/data` genérico engole `code/workstation` e
`opendesign-mcp`. Script: `~/capitolium/scripts/migra-casa-antiga.py` (`--dry-run` / `--apply`).

Fora de escopo sempre: `.git`, `.curator_backups`, `*.bak*`, `arquivo/`, `backups/`,
`cron/jobs.json` (escrito pelo gateway do perfil), `*.db`, `state.db-wal`,
`.state.db-litestream/**` (6k das ocorrências "live" estão ali — é litestream, não texto),
caches (`.hub/index-cache`), logs.

## Verificação antes de declarar pronto

1. Rodar `--dry-run` de novo: **0 substituições** restantes.
2. Listar remanescentes: só as classes protegidas.
3. Conferir cada alvo novo com `os.path.exists` (não confiar no mapeamento).
4. Validar YAML dos `config.yaml` (perfis + raiz) com o python do venv do Hermes
   (`$HOME/.hermes/hermes-agent/venv/bin/python`) — o python do sistema não tem `pyyaml`.
5. Integridade: empacotar os originais em tar antes de aplicar e conferir
   `migra(antes) == depois` byte a byte. Divergência = achado, não ruído.
6. Commitar **só os arquivos tocados** (`git add -- <lista>`) em cada repo de skills; há
   repos com sujeira pré-existente (sync de skills bundled) que não é sua.

## Camada da prosa: a palavra "proot"

Depois dos caminhos, sobra a palavra em prosa. Separar **casa antiga** de **mecanismo**:

- **Mecanismo (manter):** `pi-proot.sh`, sandbox de proot aninhado, `proot-distro`,
  `proot` puro/`exec proot`, `npm install` dentro/fora do proot, `PRoot/L2S` e `/.l2s`
  nos guardas de `.git`. Verificado vivo: `proot` e `proot-distro` existem em `usr/bin` e
  `bash scripts/pi-proot.sh -c 'echo ok'` responde `ok`. Não reescrever.
- **Casa antiga (reescrever):** "Browser policy — Mercúrio proot" (assinatura repetida em
  centenas de skills), "Browser único do proot", "runtime único do proot", "Chromium
  compartilhado do proot", "ambiente proot", "host é PRoot Linux", "Capitólio (proot
  Ubuntu …)", "proot/Android", "Mercúrio em proot".

Script: `~/capitolium/scripts/revisa-proot.py` (`--dry-run`/`--apply`, deixa `.prootbak`).

### Pitfall que custa uma segunda passada

Filtro de KEEP largo demais engole casa: `do proot` casava "Chromium compartilhado do
proot". **Nunca use `do proot` como padrão de mecanismo.** Ordem correta no loop: aplicar
as regras primeiro; só se nenhuma regra disparar é que KEEP decide manter. Depois de
aplicar, **auditar o que sobrou** — listar linha a linha e conferir que cada uma é
mecanismo de verdade. E rodar duas vezes deixa sufixo duplicado se a regra acrescenta
texto ("… extinta) (… extinta)"): conferir idempotência.

Falsos positivos a proteger: `TooltipRoot`, `TooltipPrimitive.Root` (contêm "proot").
