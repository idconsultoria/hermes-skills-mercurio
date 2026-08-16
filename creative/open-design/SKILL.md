---
name: open-design
description: "Open Design daemon :7456, CLI od e MCP — gera protótipos e artes de marca.

Carregue esta skill quando o usuário mencionar open-design, pedir para gerar artes/designs/protótipos, ou precisar diagnosticar o daemon :7456, o CLI od ou as tools MCP mcp_open_design_*. Workspace local-first (nexu-io/open-design, Apache-2.0) com daemon Express+SQLite e 460 plugins bundled (AirBnb, Apple, Ant, Linear). Layout persistente em /opt/data/open-design-repo — nunca /tmp."
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [design, mcp, daemon, cli, open-design, brand]
    related_skills: [agy, style-guide-consultation, ai-creative-assets, brand-studio-forge]
type: ToolIntegration
timestamp: 2026-08-14T06:00:15Z
---

# Open Design — daemon, CLI, MCP

## When to Use
- Usuário menciona "open-design" ou pede para gerar artes/designs/protótipos via Open Design.
- Precisa diagnosticar ou restaurar o daemon :7456, o CLI `od` ou as tools MCP `mcp_open_design_*`.
- Precisa configurar o bloco MCP do Open Design no config.yaml, ou testar o MCP sem reload do Hermes.

Workspace de design local-first (repo `nexu-io/open-design`, Apache-2.0): daemon Express+SQLite + CLI `od` + MCP server. Gera protótipos, artes de marca, design systems; spawna agentes de design via `start_run`. v0.18.2 (2026-08): 460 plugins bundled (design systems AirBnb/Apple/Ant/Linear...), `od tools directions`, `od automation`, `od research search` (Tavily).

## Layout persistente (NUNCA /tmp)
- Repo: `/opt/data/open-design-repo` (2.3G, node_modules + dist buildado)
- Daemon: `node apps/daemon/dist/cli.js --port 7456 --host 127.0.0.1 --no-open`
- Start script: `/opt/data/bin/start-open-design-daemon.sh`
- CLI wrapper: `/opt/data/bin/od` (exporta `OD_DAEMON_URL=http://127.0.0.1:7456`; o CLI exige essa env)
- Health: `curl http://127.0.0.1:7456/api/health` → `{"ok":true,"version":"0.18.2"}` — endpoint `/health` NÃO existe (404), `/api/version` também responde

## MCP (config.yaml)
- Bloco `open-design` em `/opt/data/config.yaml`: command = node ABSOLUTO `/opt/data/home/.nvm/versions/node/v24.16.0/bin/node`, env `OD_DAEMON_URL` + `OD_DATA_DIR=/opt/data/open-design-repo/.od`.
- ⚠️⚠️ CRÍTICO DUPLO no bloco MCP:
  1. **`args` DEVE ser lista YAML** (`args:\n  - /opt/.../cli.js\n  - mcp\n  ...`). Como **string JSON** multi-line o client pega `args[0]` da string (= `[`) e monta `os.path.join(cwd,'[')` → `Cannot find module '/opt/data/['` → `McpError: Connection closed` → server **parked**. Transcript completo em `references/mcp-connection-debug.md`.
  2. **NUNCA sourcear `nvm.sh`** no command — o aviso do `~/.npmrc` sai no STDOUT e corrompe o JSON-RPC stdio. Node absoluto sempre. O wrapper `od` pode sourcear (stdout não é protocolo lá).
- Validar SEM reload: `hermes mcp test open-design` — roda com o config atual e lista as 22 tools; se passar, o reload vai funcionar (server fica parked até reconexão ser pedida).
- 22 tools: `start_run`/`get_run`/`cancel_run` (geração), `create_artifact`/`write_file`/`delete_file`, `list_projects`/`get_file`/`search_files`/`list_files`, `list_skills`/`list_plugins`/`list_agents`, `collect_brief`/`confirm_brief`, `get_active_context`, `start_vela_login`/`get_vela_login_status`.
- Tools `mcp_open_design_*` só aparecem após RELOAD do MCP no Hermes — o daemon precisa estar de pé quando o Hermes inicializa/reloada.

## Runtime agy (quem gera os designs no start_run)

O OD spawna `agy -p -` (contrato escrito para agy **v1.0.3**, prompt via stdin). No agy **1.1.12+** isso quebrou: `-p -` não lê mais stdin e responde *"request was empty or just a hyphen"* → run termina `succeeded` com **0 artifacts**. Fix instalado: shim em `/opt/data/home/.local/bin/agy` (binário real renomeado `agy-real`) que converte `-p -` → `--dangerously-skip-permissions --print "$(cat)"`. Se o shim sumir, recriar; ver skill `agy` (seção "Open Design integration").

### ⚠️ agy 1.1.13 (autoupdate 2026-08-14) — ORDEM DOS FLAGS no shim

O agy-real **1.1.13** (autoupdate) mudou o parse de flags: `--dangerously-skip-permissions` **DEVE vir ANTES** de `-p`/`--print`, senão o print mode NÃO auto-aprova tools → *"jetski: no output produced — a tool required the read_file/command permission that headless mode cannot prompt for"* → daemon classifica como `auth_required` (empty output guard) e o run falha mesmo com token OK.

Sintoma clássico: `agy -p -` manual responde `AUTH_OK`, mas `start_run` falha com `AGENT_AUTH_REQUIRED`. O watcher de processos (`tr '\0' '\n' < /proc/<pid>/cmdline`) prova que o shim está rodando e o token está OK — o problema é só a ordem.

Fix (shim atual): `exec "$REAL" --dangerously-skip-permissions "${ARGS[@]}" --print "$PROMPT"` — flag PRIMEIRO, e remover `-p`/`--print` originais dos ARGS (o `--print` adicionado cumpre o papel; `-p --print` duplicado quebra no 1.1.13). Verificar com: `echo 'Leia o arquivo X e responda OK' | agy --log-file /tmp/t.log -p -` → deve responder OK e log mostrar `Print mode: --dangerously-skip-permissions set, auto-approving all tool permissions` + `Always-proceed: auto-approving tool confirmation "ReadFile"`.

⚠️ settings.json 1.1.13: entries tipo `read_file`, `write_file`, `edit`, `glob`, `grep`, `ls`, `bash` (sem `command(...)`) são **rejeitadas** com *"ignoring invalid allow entry ...: invalid grant string"* — o 1.1.13 só aceita `command(<target>)`. Com o shim corrigido (skip-permissions antes), as allow-rules nem são necessárias para tools.

Pré-requisitos do agy no container:
1. **Token OAuth**: copiar `/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token` do host Oracle → `/opt/data/home/.gemini/antigravity-cli/` (o container não tem keyring; o arquivo basta).
2. **settings.json** com `permissions.allow` (sem allow-rules o modo headless auto-deny tools → *"no output produced… auto-denied"*). trustedWorkspaces: `/opt/data`, `/opt/data/open-design-repo`.

## CLI od (v0.18.2)
```
od tools directions                    # direções de design (editorial-monocle, modern-minimal, human-approachable...)
od plugin list                         # 460 plugins bundled (design-system-* ...)
od automation <list|get|create|run>    # automações headless (mesma store da UI)
od research search --query "..."       # pesquisa Tavily via daemon
od tools design-systems read/resolve   # ler design systems ativos
od artifacts create --name --input     # criar artefato de projeto
od mcp [--daemon-url <url>]            # MCP server stdio
```
`od --version` NÃO existe (unknown option) — use `GET /api/version`.

## Fluxo típico
1. Health check: `curl -s http://127.0.0.1:7456/api/health` — se ok, daemon vivo.
2. Usar CLI via `/opt/data/bin/od` (com `OD_DAEMON_URL`) ou tools MCP (após reload).
3. Gerar design via MCP: `list_skills` → `create_project(name, skill)` → **`write_file` do DESIGN.md no projeto** (o agente do OD lê do projeto, não do repo local) → `start_run(project, skill, prompt autossuficiente com tokens inline, agent="antigravity", model="Gemini 3.5 Flash (High)", requestId=<UUID estável>)` → `get_run` a cada 30–60s (5–30 min; running com mtimes estáticos = agente pensando, NÃO cancelar).
4. Validação: `previewUrl` (`http://127.0.0.1:7456/api/projects/<id>/raw/<file>`) no browser + `browser_vision`; hex exatos via grep no arquivo.
5. Daemon morto ou repo sumido → seguir `references/restore.md`.

### Assinaturas de falha do run (events.jsonl em `.od/runs/<runId>/`)
- `errorCode: AGENT_AUTH_REQUIRED` → agy sem token (copiar do host) ou settings sem permissões.
- `status: succeeded` com 0 artifacts + stdout *"request was empty"* → shim do agy quebrado/removido (`/opt/data/home/.local/bin/agy`).
- stdout *"no output produced — tool required command permission"* → settings.json sem allow-rules.

### Editar artefato gerado
Patch no arquivo local, depois **sincronizar em 3 lugares**: pasta de entrega, repo do projeto (`cfp-ia/product/design/`), e `.od/projects/<id>/` (o previewUrl serve deste último). Screenshots: `browser_vision` retorna `screenshot_path` → copiar para a pasta de entrega, nomear com versão (v1, v2…).

⚠️ **Corrigir direção de símbolo SVG = redesenhar os paths, NUNCA `transform="rotate(...)"`.** A rotação CSS/SVG quebra o centering/enquadramento do símbolo dentro do viewBox (ficou "desastroso" — o usuário rejeitou). Redesenhar os paths na orientação correta, preservando as proporções do original. Exemplo (chevrons p/ cima, viewBox 32, mesmo desenho do z-icon do Igor): inferior `M7 22L16 16L25 22`, superior `M9 15L16 9L23 15`. Sempre validar com `browser_vision` após o patch (orientação + enquadramento + cores) antes de entregar.

**Preferência do usuário (Gustavo):** verificação visual de marca = SEMPRE prints de TODAS as seções em **modo claro E escuro** (ex.: brand-kit, design-system, app-mockup × light/dark = 6 prints). Validar o dark mode em cada seção, não só na primeira.

### Posts sociais / carrossel com copy aprovada
- **Copy exata aprovada pelo usuário → renderizar em HTML/CSS, NUNCA `imagegen`/`imagen`** — geração de imagem alucina texto (pior em PT-BR); a copy de post é contrato. Skills corretas: `canvas-design` (PNG/PDF), `poster-hero` (vertical), `card-xiaohongshu` (carrossel multi-card swipeable).
- Formato Instagram 4:5 = 1080×1350 — validar CADA slide com `browser_vision` antes de entregar (não só o primeiro).
- Specs de posts da Zera ficam na pasta "Posts" do Drive (ID `1R88p_5x4j7BBm8my3LiUpMT9byR-tMnl`) — docs com copy completa + links de preview; detalhe do Post 1 em `references/zera-brand-posts.md`.

## Protocolo de marca e fluxo de identidade (não é toolbox pura)

O OD tem um protocolo formal + skills de orquestração, mas o "fluxo" é dirigido pelo agente (não há roadmap fixo tipo brand-studio-forge):

- **DESIGN.md é o contrato de marca** — prosa canônica de tokens consumível por agentes. Spec de design system: `manifest.json` + `DESIGN.md` + `tokens.css` (`docs/design-systems.md` no repo).
- **Craft rules** — regras universais (typography, color, anti-ai-slop) injetadas entre DESIGN.md e a skill; marca vence no conflito.
- **5 design directions**: editorial-monocle, modern-minimal, human-approachable, tech-utility, brutalist-experimental (`od tools directions`).
- **154 design systems embutidos** em `design-systems/` (Linear, Stripe, Vercel, Apple, Notion...).
- **Fluxo recomendado para identidade**: `creative-director` orquestra (5 fases, lanes: critique → style-direction → visual asset generation → motion/data → polish → accessibility → verification). Compor skills por peça via `start_run` (`skill` + `skills[]` + `plugin` + `agent` + `model`): `brandkit` (logo system/identity boards via imagem), `imagegen`/`imagen` (ícones, social cards), `minimax-pdf`/`minimax-docx`/`slides` (brand guidelines formais), `frontend-design`/`gpt-taste` (landing), `frame-logo-outro`/`remotion` (vídeo de marca), `design-review`/`web-design-guidelines` (auditoria).
- Mapa completo: `references/brand-identity-spectrum.md`.

## Referências
- `references/brand-identity-spectrum.md` — mapa das skills de marca (46/162), plugins, design systems e direções do open-design.
- `references/restore.md` — playbook completo de restauração pós-reboot, teste MCP via JSON-RPC, edição do config.yaml e pitfalls confirmados.
- `references/mcp-connection-debug.md` — transcript do bug args-string vs lista YAML (Cannot find module '/opt/data/['), `.npmrc`/stdout, `hermes mcp test`, edição cirúrgica vs safe_dump.
