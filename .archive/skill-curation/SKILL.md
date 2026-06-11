---
name: skill-curation
description: "Discover, evaluate, rank, and install community skills for Hermes Agent — full curation lifecycle from search to verification.\n\nLoad this skill when you need to find, evaluate, and install community skills for Hermes. Covers web search for skills, extraction from GitHub repos, cross-referencing reviews, tiered ranking with user feedback, installation via tap+hub or raw URL, and post-install verification. Does NOT cover authoring SKILL.md files (see hermes-agent-skill-authoring)."
version: 1.0.0
author: Hermes Agent
tags:
  - hermes
  - skills
  - curation
  - discovery
  - installation
  - evaluation
  - community
related_skills:
  - hermes-agent-skill-authoring
  - hermes-agent
triggers:
  - find skills for
  - discover skills about
  - best skills for
  - top skills for
  - rank skills
  - compare skills
  - install skill
  - procurar skills
  - adquirir skills
  - melhores skills
  - instalar skill
---

# Skill Curation — Discover, Evaluate & Install Hermes Skills

## Overview

Hermes Agent has a rich ecosystem of **70+ bundled skills** and **hundreds of community skills** across GitHub, HermesHub (`hermeshub.xyz`), Hermes Atlas (`hermesatlas.com`), and the `skills.sh` marketplace. The challenge is not finding skills — it's finding the **right** skill and evaluating whether it's production-grade.

This skill covers the full curation workflow:

```
User request → Web search for skills → Extract details from repos
  → Cross-reference reviews & feedback → Rank by tiers
  → Install (tap+hub or raw URL) → Verify
```

## Sources for Finding Skills

### Primary Sources (ranked by reliability)

| Source | URL | Reliability | Notes |
|--------|-----|:-----------:|-------|
| **Awesome Hermes Agent** | github.com/0xNyk/awesome-hermes-agent | ⭐⭐⭐⭐⭐ | 3.7k stars, curated list with maturity tags (production/beta/experimental) |
| **EasyClaw rankings** | easyclaw.com/blog/knowledge/best-hermes-agent-skills | ⭐⭐⭐⭐⭐ | Ranked by category with security badges, last-commit checks, weakness analysis |
| **Felo AI blog** | felo.ai/blog/best-hermes-agent-skills-2026 | ⭐⭐⭐⭐ | Reviews across 5 categories, real-world impact focus |
| **HermesHub** | hermeshub.xyz | ⭐⭐⭐⭐ | Security-scanned registry, install counts |
| **Hermes Atlas** | hermesatlas.com | ⭐⭐⭐ | Searchable project registry |
| **GitHub search** | `site:github.com hermes-agent skill <topic>` | ⭐⭐⭐ | Widest coverage, no quality filter — must evaluate manually |
| **Official docs catalog** | hermes-agent.nousresearch.com/docs/reference/skills-catalog | ⭐⭐⭐⭐⭐ | Only bundled skills (70+), zero community |

### Secondary Sources

- **Reddit/Discord** — real user feedback, but sparse for specific skills
- **Dev.to / Medium** — review articles, often timed to releases
- **GitHub issues/discussions** on the skill's repo — best signal for abandonment

## Evaluation Rubric

Use this **5-point checklist** before installing any community skill:

| # | Criterion | How to Check | Red Flag |
|---|-----------|-------------|----------|
| 1 | **Security scan** | `hermes skills inspect <id>` shows verdict | No badge = manual review |
| 2 | **Last commit** | Check GitHub repo `Insights` → `Pulse` | >60 days = possible incompatibility |
| 3 | **Install/usage count** | HermesHub shows installs | <50 installs on >3mo old skill |
| 4 | **Open issues** | GitHub Issues tab | Last 5 unresponded = abandoned |
| 5 | **Hermes version compat** | Check `requires_hermes` in skill.yml | Pre-v0.9 may not work with v0.10+ |

### Architecture Quality Signals

When reading a SKILL.md, evaluate:

- **Pipeline structure**: Does it decompose work into phases? Parallel agents? Sequential steps?
- **Error handling**: Does it have fallbacks? Retry logic? Phase-skip heuristics?
- **Tool discipline**: Does it scope toolsets per subagent? Or use full access for everything?
- **Adaptability**: Does it have modes (quick/standard/deep) or just one rigid path?
- **Output quality**: Templates for reports? Confidence indicators? Source citations?
- **Cost awareness**: Does it mention token/delegate_task budget? Worst-case estimates?

## Ranking Methodology

Tier-based ranking system used for comparing multiple skills on the same topic:

### Tier 1 — Elite (Multi-Agent Pipelines)
- Multiple specialized subagents running in parallel
- Cross-validation / verification layer (reviewers fact-check)
- Adaptable depth levels (quick / standard / deep)
- Concrete output templates with citations

### Tier 2 — Strong (Structured Protocols)
- Single-agent but multi-phase with structured methodology
- Multiple analytical lenses or frameworks
- Good output templates and quality checks
- Lower token cost than Tier 1

### Tier 3 — Utility (Focused & Bundled)
- Single-purpose skills (API wrappers, dedicated search)
- Bundled/official skills that don't need setup
- Good as components in a larger pipeline

## Pre-Install: Find the Hermes CLI

`hermes` may not be in shell PATH. Before running any install commands, locate it:

```bash
which hermes 2>/dev/null || find / -name "hermes" -type f 2>/dev/null | head -5
```

Common locations: `/opt/hermes/.venv/bin/hermes`, `~/.local/bin/hermes`, or the active venv. Use the full path in subsequent commands.

## Distinguish: Hermes Skill vs. External CLI Tool

When searching, a result may be one of two things:

| Type | What it is | Install approach |
|------|-----------|------------------|
| **Hermes skill** | A single `SKILL.md` (with optional scripts/references/templates) | `hermes skills install` — Methods 1-3 below |
| **External CLI tool** | A standalone app/engine (open-design, brand-studio-forge, etc.) with its own CLI | Source build, Docker, or npm — NOT `hermes skills install` |

**How to tell:** If the repo has `SKILL.md` at the root → it's a Hermes skill. If it mentions `od`, `docker compose`, `pnpm install`, or a desktop app → it's an external tool that needs separate setup.

For external tools found during curation, after installing the tool itself, register it as an MCP server (see "MCP Server Registration" below) so it's available from within Hermes.

## Installation Methods

### Method 1: Hub Install (preferred)
```bash
hermes skills search <topic>
hermes skills inspect <skill-id>     # Preview + security scan
hermes skills install <skill-id> -y  # -y to skip confirmation
```

### Method 2: Tap + Install (GitHub repo)
```bash
hermes skills tap add <user>/<repo>
hermes skills install <skill-name>
```

### Method 3: Raw URL (when hub is down/timeouting)
```bash
hermes skills install "https://raw.githubusercontent.com/<user>/<repo>/main/<skill-name>/SKILL.md" \
  --name <skill-name> --category <category> --yes
```

### Method 4: Vendor install scripts (use with caution)
```bash
bash <(curl -s https://...install.sh)
```

**Warning:** Vendor URLs at marketing sites (e.g. `https://toolname.com/install.sh`) often return SPA HTML (React/Next.js pages) instead of a shell script because they serve the marketing site for all routes. Always verify the Content-Type or preview the script first. Prefer GitHub raw URLs or official npm/Docker install paths.

### Method 5: Docker (for external CLI tools without native packages)
```bash
git clone --depth 1 https://github.com/<user>/<repo>.git
cd <repo>/deploy
# Set up .env with required tokens
docker compose up -d
```
The daemon listens on localhost (default :7456 for open-design). Verify with a health check:
```bash
curl -s http://127.0.0.1:<port>/api/health
```

### Method 6: From source (for tools needing specific Node/npm versions)
```bash
# Install required Node version via nvm first
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm install <required-major>   # e.g., 24 for open-design

# Clone and build
git clone --depth 1 https://github.com/<user>/<repo>.git
cd <repo>
corepack enable && pnpm install
pnpm --filter <package> build

# Create a CLI wrapper at /opt/data/bin/
cat > /opt/data/bin/<tool> << 'WRAPPER'
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
node /path/to/repo/dist/cli.js "$@"
WRAPPER
chmod +x /opt/data/bin/<tool>
```

## MCP Server Registration (after external tool install)

If the installed tool provides an MCP server, register it in Hermes config so the agent can call its tools:

```bash
# Find config path
hermes config path

# Set MCP server config
hermes config set mcp_servers.<name>.command "/path/to/node"
hermes config set mcp_servers.<name>.args '["/path/to/cli.js","mcp","--daemon-url","http://127.0.0.1:<port>"]'
hermes config set mcp_servers.<name>.env.OD_DATA_DIR "/path/to/repo/.od"
```

Config is write-protected from direct file editing — always use `hermes config set`.

**Important:** The `args` field gets stored as a JSON string in YAML. This is handled correctly by Hermes — don't try to force YAML list syntax.

## Post-Installation Verification

```bash
hermes skills list | grep <skill-name>    # Confirm installed
hermes skills inspect <skill-name>        # Confirm metadata
skill_view(name='<skill-name>')           # Load into session
```

## Pitfalls

- **Hub timeout**: The skills hub can timeout resolving skill IDs. Always have Method 3 (raw URL) as fallback.
- **Interactive prompts**: `hermes skills install` prompts for confirmation even in TUI mode. Always use `--yes` / `-y` flag when running non-interactively.
- **Category selection**: On raw URL install, the CLI asks for a category interactively. Pass `--category <name>` to avoid this.
- **Security scan findings**: MEDIUM findings for legitimate shell commands (`az`, `curl`, `gh`) are common and resolved as ALLOWED. Don't panic — review the context.
- **Quarantine directory**: Skills installed from raw URLs first go to `.hub/quarantine/` before being moved to `skills/`. This is normal.
- **GitHub rate limits**: Subagent GitHub searches can hit rate limits. Use `browser` tool with GitHub web UI as fallback.
- **Confirmation bias**: Actively search for negative reviews and open issues. Every skill has weaknesses — list them honestly in rankings.
- **Star count inflation**: High GitHub stars alone don't mean quality. Check code quality, documentation, and last commit.
- **Cross-reference**: Always check at least 2-3 sources (blog post, GitHub, official catalog) before ranking.

## Reference Files

- `references/deep-research-skills-ranking-2026-06.md` — Full tiered ranking of all known deep-research skills with community feedback, install commands, and architecture breakdowns. Generated from the 2026-06 session.
- `references/external-tools-install-notes.md` — Install notes for open-design CLI, brand-studio-forge, and pattern for building/setting up external CLI tools with MCP registration.
