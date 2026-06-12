---
name: autonomous-ai-agents
description: "Delegate coding tasks to AI coding agent CLIs via Hermes: one-shot, review

Load this skill when you need to delegate coding tasks to autonomous AI coding agent CLIs. Covers one-shot queries to Claude Code, Codex, or OpenCode; PR review workflows with structured prompts; and session orchestration patterns for complex multi-step tasks across agents."

Load this skill when you need to delegate coding tasks to autonomous AI coding agent CLIs. Covers one-shot queries to Claude Code, Codex, or OpenCode; PR review workflows with structured prompts; and session orchestration patterns for complex multi-step tasks across agents."
category: autonomous-ai-agents
---

# Autonomous AI Coding Agents

Delegate coding tasks to external AI coding agent CLIs through Hermes. Choose the right agent for the job, then use common orchestration patterns.

## Decision Guide

| Agent | Best for | CLI command |
|-------|----------|-------------|
| **Claude Code** | Complex features, large codebases, PRs | `claude` (npm) |
| **Codex CLI** | OpenAI-native projects, quick tasks | `codex` (npm) |
| **OpenCode CLI** | Go-based projects, PR review | `opencode` (go) |

## Common Orchestration Patterns

All three agents share the same Hermes integration patterns:

### One-shot task
```bash
# Via terminal
terminal("cd /path/to/project && claude -p 'fix the auth bug in src/auth.ts'")
terminal("cd /path/to/project && codex exec 'add rate limiting to the API'")
terminal("cd /path/to/project && opencode run 'review PR #42'")
```

### Interactive session (pty mode)
```bash
terminal("tmux new-session -d -s agent-session 'claude'", pty=true)
```

### Parallel worktrees
```bash
git worktree add ../feature-branch feature-branch
terminal("cd ../feature-branch && claude -p 'implement feature X'", background=True, notify_on_complete=True)
```

### Monitoring
```bash
process(action='poll', session_id='...')
process(action='log', session_id='...')
```

## Claude Code CLI

**Install:** `npm install -g @anthropic-ai/claude-code`
**Key flags:** `-p` (one-shot print), `--dangerously-skip-permissions`
**Auth:** Anthropic API key in env or `claude login`
**Hermes pattern:** Same one-shot/background/pty patterns as below.

### One-shot task
```bash
terminal("claude -p 'task description'", timeout=300)
```

### Interactive session
```bash
terminal("claude", pty=true, background=True)
process(action='submit', session_id='...', data='/goal implement feature X')
```

### PR review
```bash
terminal("git diff main | claude -p 'review this diff for bugs and style issues'")
```

## Codex CLI

**Install:** `npm install -g @openai/codex`
**Key flags:** `exec` (one-shot)
**Auth:** OpenAI API key
**Smaller binary** (5.4KB SKILL.md vs Claude's 34KB)

```bash
terminal("codex exec 'generate unit tests for src/auth.ts'")
terminal("codex exec 'review this PR' < git diff main")
```

## OpenCode CLI

**Install:** Go binary from opencode.ai/zen/go
**Key flags:** `run` (one-shot)
**Auth:** API key in env
**Lightweight** (7.3KB SKILL.md)

```bash
terminal("opencode run 'add TypeScript types to the API module'")
terminal("opencode run --model deepseek-v4-flash 'quick bug fix in parser'")
```

## Common Pitfalls

- **Timeout:** Use generous timeouts (300s+) for complex tasks
- **Background monitoring:** Always use `notify_on_complete=true` for long tasks
- **Worktree cleanup:** Remove worktrees after merge
- **Auth expiry:** Check agent auth before delegating — expired tokens cause silent failures
- **Context size:** Large codebases may hit context limits — narrow the task scope
