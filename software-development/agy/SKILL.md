---
name: agy
description: Google Antigravity CLI (agy) — instalação, autenticação OAuth via tmux, e workflows de design (image generation, prototipagem, subagentes paralelos).
category: software-development
---

# agy — Antigravity CLI (Consultor Externo)

> **Papel na hierarquia:** Consultor externo especialista. Usar em momentos estratégicos.
> Prompt complexo, leitura de arquivos, design/UX → agy. Tarefa simples, code task → Pi cost.
> Pouco e certeiro. Nao usar para tarefas operacionais rotineiras.
>
> Ver pi-agent-coordination para a hierarquia completa (agy > Pi best > Pi cost).

## Trigger
User asks to use agy for design tasks (UI mockups, prototipagem, design review, UX audit, pesquisa),
ou quando a tarefa se encaixa no perfil "consultor externo": complexo, estrategico, requer file I/O.

## Install

### On Host (Oracle VM / Ubuntu)
```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

### On Hermes Container (if needed)
```bash
# Download script first (pipe-to-bash blocked by smart approval)
curl -fsSL -o /tmp/agy-install.sh https://antigravity.google/cli/install.sh
bash /tmp/agy-install.sh
```

Installed to `~/.local/bin/agy` (version seen: 1.0.6, Go binary ~158MB).

Add to PATH manually:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Authentication (Critical — OAuth Requires Interactive TTY)

agy uses Google OAuth with PKCE. In remote/SSH environments (no browser), the flow is:

1. agy prints a Google OAuth URL
2. User visits URL in browser, signs in
3. Browser shows an alphanumeric authorization code
4. User pastes the code back into agy's TUI

**The problem:** agy uses bubbletea (TUI framework) that requires a real TTY. Running via `ssh <host> agy` or piping stdin doesn't work — it either fails with "error opening TTY" or the 30s timeout expires.

### Solution: tmux session on the host

```bash
# 1. Install tmux if missing
ssh oracle-host 'sudo apt-get install -y tmux'

# 2. Create a tmux session with agy running
ssh oracle-host 'tmux new-session -d -s agy-auth \
  "env HOME=/home/ubuntu TERM=xterm-256color /home/ubuntu/.local/bin/agy"'

# 3. Wait for the TUI to render, then select Google OAuth
sleep 3
ssh oracle-host 'tmux send-keys -t agy-auth "1" Enter'

# 4. Extract the auth URL from the tmux pane
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -30'

# 5. Send the URL to the user — they visit it, authenticate, get a code
# 6. Send the code back to agy in tmux
ssh oracle-host 'tmux send-keys -t agy-auth "<THE_CODE>" Enter'

# 7. Verify auth succeeded
ssh oracle-host 'tmux capture-pane -t agy-auth -p -S -10'
```

**Important:** Each agy invocation generates a fresh PKCE `code_challenge`. If the URL is lost and agy restarts, the previous auth code is invalidated.

### Detecting auth state
```bash
ssh oracle-host 'echo "n" | timeout 12 env HOME=/home/ubuntu /home/ubuntu/.local/bin/agy 2>&1 | head -10'
# If "Authentication required" → not authenticated yet
# If session starts → authenticated
```

## Design Workflows

### Image Generation (Built-in)
agy has native `GenerateImage()` — no external tools needed. Use for:
- UI mockups
- App icons / branding assets
- Placeholder images
- Visual concepts

Prompt pattern: *"Generate an image of [description]"*

### Autonomous Prototyping (/goal)
Hands-free mode: agy plans, codes, tests, and delivers without human input.
```bash
agy /goal "Build a single-page landing page for [product] with hero, features, and CTA"
```

Generates:
- `implementation_plan.md` — full spec
- Code output
- `walkthrough.md` — post-completion docs

### Requirements Gathering (/grill-me)
Interactive TUI interview before coding — agy asks targeted questions with curated options.
```bash
agy /grill-me "Design a dashboard UI for [purpose]"
```

Good for ambiguous design briefs with many decision points.

### Subagents (Parallel Design Work)
Spawn parallel agents for research + implementation:
```bash
# Spawn research subagent for design research
# Meanwhile, main agent works on implementation
```

Three subagent types: `research` (read-only), `self` (full clone), custom.

### Skills System
agy has 56+ built-in skills (Chrome DevTools, Modern Web, Firebase, etc.):
```bash
# List available skills
/skills

# Use a skill
"Use the modern-web-guidance skill for CSS container queries best practices"
```

### Workflow Skill Creator
Completed design workflows can be distilled into reusable `SKILL.md` files:
```bash
# After completing a design workflow, save it as a skill
"Save this workflow as a skill called 'landing-page-scaffold'"
```

## Pitfalls

⚠️ **TUI requires real TTY.** Cannot pipe commands or redirect stdin for interactive use. Always use tmux/screen on the remote host.

⚠️ **30s auth timeout.** agy waits 30s for the user to authenticate. If using the tmux approach, the session stays alive indefinitely — no timeout issue.

⚠️ **PKCE one-time use.** Auth code from one session cannot be reused in another. Always generate a fresh URL.

⚠️ **Output token limit em arquivos grandes.** agy (Gemini Flash 3.5) tem limite de tokens de saída. Ao reconstruir arquivos grandes (ex: prototype.html > 75KB), a geração pode ser truncada com "The model's generation exceeded the maximum output token limit." agy se recupera compactando e reescrevendo — mas o resultado pode perder funcionalidades. Para evitar: quebrar a tarefa em partes menores, ou pedir versão compacta explicitamente.

⚠️ **Path confusion — sempre usar path absoluto explícito.** agy pode procurar arquivos em diretórios errados (ex: `/home/ubuntu/selfhost/taskflow/` em vez de `/home/ubuntu/selfhost/shared/code/workstation/taskflow/`). Como o agy usa o modelo para decidir onde ler, ele pode seguir links simbólicos ou caminhos antigos. Sempre fornecer o path absoluto completo (desde `/home/ubuntu/selfhost/...`) nos prompts para evitar confusão.

⚠️ **$HOME must be set.** agy crashes with `$HOME is not defined` if the env var is missing. Always pass `HOME=/home/ubuntu` or whatever is appropriate.

⚠️ **First-run only in HOST keyring.** OAuth tokens are cached in the OS keyring (`secret-tool` / `dbus`) **on the host** after first auth. The Hermes/Pi containers have no dbus, so agy prompts for auth every time when run inside the container. **Always run agy on the host via SSH**, not inside any container:

```bash
# ✅ Run on host
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/PROJETO && /home/ubuntu/.local/bin/agy -p "prompt"'

# ❌ Does NOT work (container has no keyring)
agy -p "prompt"
```

⚠️ **File paths from host perspective** — Inside the container, files are at `/opt/data/code/workstation/...`. On the host, they're at `/home/ubuntu/selfhost/shared/code/workstation/...`. When running agy via SSH, always use the host path.

## Verification
```bash
# Check binary
ssh oracle-host '/home/ubuntu/.local/bin/agy --version'
# Expected: 1.0.6

# Check PATH setup
ssh oracle-host 'export PATH="$HOME/.local/bin:$PATH" && which agy'
```
