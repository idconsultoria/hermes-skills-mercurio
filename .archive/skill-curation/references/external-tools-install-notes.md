# External CLI Tools — Install Notes (2026-06)

## Open Design (open-design.ai)

**Repo:** nexu-io/open-design · 60.9k ★ · Apache-2.0
**Type:** External CLI + daemon + web UI (NOT a Hermes skill)
**CLI:** `od` at `/opt/data/bin/od` (wrapper script)
**Daemon:** http://127.0.0.1:7456
**Location:** `/tmp/open-design-repo/`
**Node:** v24.16.0 via nvm (`/opt/data/home/.nvm/versions/node/v24.16.0/bin/node`)
**Build:** pnpm install + pnpm --filter @open-design/daemon build
**Plugins:** 405 bundled · Skills: 259+ · Design systems: 142+
**MCP:** Registered in Hermes config as `mcp_servers.open-design`

**Start daemon:**
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
cd /tmp/open-design-repo
nohup node apps/daemon/dist/cli.js --port 7456 --host 127.0.0.1 --no-open > /tmp/open-design-daemon.log 2>&1 &
```

**Health check:** `curl -s http://127.0.0.1:7456/api/health`

**Install from source reminder:**
- Requires Node 24+ (install via nvm)
- Requires pnpm 10.33.x (via corepack)
- git clone --depth 1, pnpm install, then build daemon
- `od mcp install hermes` outputs manual config block (auto-install unsupported for Hermes)

## Brand Studio Forge

**Repo:** levi-lvjp/brand-studio-forge · MIT
**Type:** Hermes skill (creative/brand-studio-forge)
**Install:** `hermes skills install "https://raw.githubusercontent.com/levi-lvjp/brand-studio-forge/main/SKILL.md" --name brand-studio-forge --category creative --yes`
**Commands:** forge_interview, forge_forge, forge_name, forge_evolve, forge_critique, forge_audit, forge_polish, forge_content, forge_author, forge_schedule
**Logo strategies:** 22 design strategies matched to brand personality
**Anti-slop:** Reflex-reject font list (20 banned), industry anti-cliche rules, two-tier slop test
**Image gen:** Gemini 2.0 Flash or GPT Image 2 (API key in ~/.forge/keys.json)
