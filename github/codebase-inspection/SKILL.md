---
name: codebase-inspection
description: "Multi-layered codebase diagnostics: structural mapping, dependency audit, git history, metrics, and health reports."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository, Architecture, Diagnostic]
    related_skills: [github-repo-management, github-code-review]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection & Architecture Diagnostic

Analyze repositories in layers — from surface structure through deep architecture — producing a comprehensive diagnostic report with severity ratings and actionable recommendations.

## When to Use

- User asks for a full architecture review or codebase audit
- User wants to understand a repo they just cloned
- User asks "how healthy is this project?"
- User asks for LOC, language breakdown, or codebase composition
- Pre-PR cleanup: scan for structural issues before proposing changes
- Pre-refactor assessment: understand coupling, duplication, and debt

## Prerequisites

```bash
# pygount for quantitative metrics
pip install pygount

# git for history analysis
git --version
```

---

# The Multi-Layered Diagnostic Method

Work through these layers sequentially. Each builds on the previous one.

## Layer 1: Surface Scan

Get the file tree. Understand the top-level structure.

```bash
cd /path/to/repo
find . -not -path './.git/*' -not -path './__pycache__/*' -not -path '*/node_modules/*' \
  -not -path '*.egg-info*' | head -200
```

**Look for**: monorepo patterns (multiple apps/domains), missing README, stray binaries, config files.

### Key red flags
- Credential files (`.json` service accounts, `.pem` keys, `.env` with secrets)
- Binary artifacts committed (`.pyc`, `.exe`, `.dmg`, images > 500KB)
- IDE configs (`.vscode/`, `.idea/`) committed
- Requirements files in multiple directories (fragmented deps)

## Layer 2: Core Module Analysis

Read the actual implementation files. Pick the most important ones based on structure:
1. `__init__.py` files — tell you what's exported
2. Entry points — `main.py`, `app.py`, CLI entrypoints
3. Core wrappers — model abstractions, client configs
4. The longest files — they hold the most logic

Always read enough to understand the **module's responsibility, dependencies, and patterns**.

### Key red flags
- Hardcoded IDs, URLs, API keys in source code
- Two different versions of the same SDK/library
- System prompts > 5KB embedded in Python files
- Module coupling to N other modules (fan-out > 5)

## Layer 3: Subsystem Identification

Map out how many independent domains exist in the repo. Classify each:

```python
# mental model for each subsystem
{
  "name": "POP Generation Pipeline",
  "entrypoint": "elaboracao_de_pops_e_diagramas.py",
  "lines": 764,
  "dependencies": ["modelos/", "agentes/", "conectores/"],
  "external_services": ["Gemini", "Google Drive", "Notion", "Imgur"],
  "autonomy": "standalone"
}
```

For each subsystem note: entry point, core files, external services, and whether it shares state with other subsystems.

## Layer 4: Dependency & Configuration Audit

Check all config mechanisms:

```bash
# Env files
cat .env.example 2>/dev/null || echo "No .env.example"
cat .env 2>/dev/null || echo "No .env"

# Config files
find . -name '*.json' -not -path './.git/*' -not -path '*/node_modules/*'
find . -name '*.yaml' -not -path './.git/*' -not -path '*/node_modules/*'
find . -name '*.toml' -not -path './.git/*' -not -path '*/node_modules/*'

# Secrets committed?
find . -name 'service_account*.json' -not -path './.git/*'
find . -name '*.pem' -not -path './.git/*'
grep -rn 'api_key\|API_KEY\|secret\|password' --include='*.py' \
  --exclude-dir='.git' --exclude-dir='__pycache__' 2>/dev/null | head -20
```

### Key red flags
- Multiple service account files
- Credentials in committed JSON/YAML config files
- API keys in source code (even as default parameter values)
- Multiple `requirements.txt` files
- Fallback hardcoded IDs in code (e.g., `ID_PASTA = os.environ.get("X", "hardcoded_fallback")`)

## Layer 5: Git History Analysis

```bash
# Team composition
cd /path/to/repo
git shortlog -sne --all

# Branch topology
git branch -a
git log --oneline --all --graph | head -30

# Recency
git log --oneline -20

# Commit message quality
git log --format="%s" --all | head -30
```

### Key red flags
- Single contributor (bus factor = 1)
- Messages like "att", "fix", "update", "nova versao" (no semantic info)
- Unmerged branches with significant work
- No tags / releases
- Merge commits from bots mixed with manual work

## Layer 6: Quantitative Metrics

Run pygount (see full pygount reference below):

```bash
pygount --format=summary \
  --folders-to-skip=".git,__pycache__,node_modules,venv,.venv,.cache,dist,build,.tox,.eggs,vendor,third_party" \
  .
```

Key metrics to extract:
- **Code/comment ratio** — < 20% comments suggests under-documented
- **Language diversity** — > 3 active languages suggests complexity
- **File count** — > 100 files per subsystem suggests it needs splitting
- **Binary/unknown files** — indicates committed build artifacts

---

# The Diagnostic Report Format

Synthesize all layers into a structured report. Required sections:

```
## 📊 Ficha Técnica
Table with repo name, created date, last push, language, size, LOC, file count, commits, contributors, license status, test status.

## 🧩 O Que Esse Repositório FAZ (Mapeamento de Subsistemas)
For each subsystem: one-line purpose, pipeline diagram, client/target audience.

## 🔴 PROBLEMAS CRÍTICOS (Prioridade Máxima)
Issues labeled 🔴. Include: location in code, impact, severity. Examples:
- Credentials committed
- Zero tests
- Hardcoded configuration
- SDK version conflicts
- API key naming inconsistency

## 🟡 PROBLEMAS ESTRUTURAIS (Média Prioridade)
Issues labeled 🟡. Structural/code quality issues.

## ⚠️ PROBLEMAS OPERACIONAIS
Issues labeled ⚠️. CI/CD, error handling, gitignore deficits.

## 📈 Métricas de Saúde
Rating table with emoji scores:

| Indicador | Nota | Justificativa |
|---|---|---|
| **Segurança** | 🟤 X/10 | ... |
| **Testabilidade** | 🟤 X/10 | ... |
| **Modularidade** | 🟡 X/10 | ... |
| **Manutenibilidade** | 🟡 X/10 | ... |
| **Documentação** | 🟢 X/10 | ... |
| **Configuração** | 🟤 X/10 | ... |
| **Infraestrutura** | 🟡 X/10 | ... |

**Nota geral: 🟤 X.X/10 — classification**

## 🎯 Recomendações Imediatas (Top 5)
Numbered, actionable, prioritized.
```

---

# pygount Reference (Original)

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```
On ARM64/uv environments:
```bash
uv pip install pygount
uv run pygount --format=summary --folders-to-skip=".git,__pycache__" .
```

## 1. Basic Summary

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories.

## 2. Common Folder Exclusions

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
5. **uv-managed environments** — pygount installed via `uv pip install` won't be on PATH. Always use `uv run pygount ...` or the full venv path.
