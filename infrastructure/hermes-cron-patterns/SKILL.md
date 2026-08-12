---
name: hermes-cron-patterns
description: "Hermes cron job patterns — timeout limits and background execution.

Load this skill when a cron job exceeds the 3-minute hard limit or needs to run long scripts. Covers the nohup background spawn pattern, script delivery, and timeout workarounds for the Hermes cron scheduler."
version: 1.0.0
author: Hermes Agent
tags: [hermes, cron, background, nohup, timeout]
type: Reference
timestamp: 2026-08-09T05:08:04Z
---

# Hermes Cron Patterns

Patterns for working with the Hermes cron scheduler, especially long-running scripts
that exceed the built-in 3-minute hard timeout.

---

## The 3-Minute Hard Limit

Hermes cron jobs have a **hard 3-minute interrupt per tick**. Scripts that run longer
than 3 minutes are killed and reported as failed. This limit cannot be changed — it's
enforced by the scheduler, not configurable per-job.

---

## Pattern: `nohup` Background Spawn

For scripts that take longer than 3 minutes (e.g., full ERP syncs, large batch
operations), wrap the real work in a `nohup` background process. The cron script
itself exits in < 1s, staying within the limit, while the actual work runs
independently.

### Template

```bash
#!/usr/bin/env bash
# Wrapper: spawns long-running task in background, exits immediately.
# Cron tick completes in < 1s; actual work runs to completion.
set -euo pipefail

LOG_DIR="/path/to/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/task-$(date +%Y%m%d-%H%M%S).log"

nohup bash -c "
  echo '=== \$(date) — Starting ===' > '$LOG_FILE'
  cd /path/to/project
  ./long-running-command.sh >> '$LOG_FILE' 2>&1
  EXIT_CODE=\$?
  if [ \$EXIT_CODE -eq 0 ]; then
    echo '✅ \$(date) — Done' >> '$LOG_FILE'
  else
    echo '❌ \$(date) — Failed (exit \$EXIT_CODE)' >> '$LOG_FILE'
  fi
" > /dev/null 2>&1 &

echo "🚀 Task spawned in background — $(date)"
echo "📋 Log: $LOG_FILE"
```

### Key points

- `nohup` prevents the process from being killed when the parent exits
- `> /dev/null 2>&1 &` detaches completely from the cron tick
- All output goes to a timestamped log file — cron tick output only shows the spawn message
- `EXIT_CODE=\$?` — the escaped `\$` prevents bash from expanding the variable in the
  parent. The inner bash process expands `$?` at runtime.
- The cron job reports as **successful** as long as the spawn succeeds (exit 0).

### When to use

| Scenario | Approach |
|---|---|
| Script takes < 3 min | Direct `script` attribute, no wrapper needed |
| Script takes > 3 min | `nohup` wrapper pattern |
| Need delivery of results | Script writes summary to stdout; cron `no_agent=True` delivers stdout |
| LLM-driven cron (> 3 min) | Not possible — agent loops also have time limits. Use `delegate_task` or `terminal(background=True)` instead |

### Pitfalls

- **Stale PID files**: The cron process dies quickly but the nohup child lives on.
  If the script writes PID files, they may point to the dead cron process.
- **No delivery of results**: The cron tick output is minimal (spawn confirmation).
  To get results, have the script write to a log that another system monitors,
  or use a second cron job with `context_from` to read the log.
- **Orphaned processes**: If the nohup script hangs, there's no automatic cleanup.
  Add a `timeout` to the inner bash invocation for safety:
  ```bash
  timeout 1800 ./long-running-command.sh >> '$LOG_FILE' 2>&1
  ```
- **Cron output caching**: If you update the script and immediately `cronjob run`,
  the old version may be cached. Remove and recreate the cron job to force a fresh
  read of the script file.
- **Silent mid-execution death**: A `nohup` background script can be killed by OOM
  or signal mid-execution with no error output — the log simply stops mid-page and
  the completion marker line never gets written. The cron reports success (the spawn
  exited 0), so you only notice when data is stale. **Diagnosis:** log file truncated
  compared to historic runs, no final `✅ Done` or `❌ Failed` line. **Mitigation:**
  wrap the inner command with `timeout` + retry loop:
  ```bash
  timeout 1800 ./long-command.sh >> "$LOG" 2>&1
  if [ $? -ne 0 ]; then
    echo "⚠️ Retrying after failure..." >> "$LOG"
    sleep 60
    timeout 1800 ./long-command.sh >> "$LOG" 2>&1
  fi
  ```

---

## Pattern: Retrieving Cron Outputs on Request

When the user asks "os relatórios/documentos que o cron produziu" (or similar):

1. `cronjob(action='list')` → achar o `job_id`, `last_run_at`, `last_status` (ok/error), `deliver` e `schedule`.
2. Output bruto da sessão: `/opt/data/cron/output/<job_id>/<timestamp>.md` — começa com o prompt completo; a resposta final do agente fica no FIM do arquivo (crons LLM costumam terminar com marcadores tipo `REPORT:/GRAPH:/SUMMARY:`).
3. Artefatos do job vivem no `workdir` do job (ex: ciclo de consolidação → `/opt/data/skills/reports/`, `skills_graph.html`, `log.md`, `index.md`).
4. Entregar os artefatos como arquivos reais via `MEDIA:<path>` (sempre dentro de `/opt/data`) + legenda curta do que cada um é — não resumir tudo no texto. Oferecer output bruto e artefatos antigos por demanda.

Pitfalls:
- Sessões cron com `deliver: origin` entregam no chat E salvam em `cron/output/`; jobs `no_agent` com `deliver: local` só salvam no diretório.
- `cron/output/` pode reter só as runs recentes — para histórico completo usar o git log do workdir (ex: `/opt/data/skills` tem `log.md` + `git log` dos ciclos).
- Não confundir o arquivo de output (sessão inteira, prompt incluso) com os artefatos do job (relatórios/gráficos) — o usuário normalmente quer os artefatos.

## Model Pinning & Drift Protection

> 📖 **Leia também:** `references/cron-provider-outage-triage.md` — triage de vários
> crons agent-driven falhando na mesma janela (`idle for 600s — waiting for
> non-streaming API response` = provider outage) + rerun em ordem de dependência +
> verificação por artefatos.

Hermes cron jobs that use an LLM (agent-driven, not `no_agent`) must match the
currently configured model/provider — or be explicitly pinned — to avoid a
**model drift safety block**.

### The problem (#44585)

When the global default model changes (e.g. `deepseek-v4-pro` → `deepseek-v4-flash`
after a Hermes update), **unpinned** cron jobs are blocked from executing with:

```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted
since this job was created (model 'X' -> 'Y'), and this job is unpinned.
```

This is a safety feature: without it, the job would silently run on a potentially
much more expensive or different-behaving model.

### Who is affected

| Job type | Affected? | Fix needed? |
|----------|-----------|-------------|
| `no_agent: true` (scripts only) | ❌ No LLM, no drift risk | No |
| Agent-driven with explicit model | ❌ Already pinned | No |
| Agent-driven, unpinned (model=null) | ✅ Yes, will fail on next drift | Pin explicitly |

### How to fix

**At creation time:**
```python
cronjob(action='create', ..., model={'provider': 'opencode-go', 'model': 'deepseek-v4-flash'})
```

**On an existing job (detected via `last_status: error` + the drift error in the output log):**
```python
# 1. List to find the job_id
cronjob(action='list')

# 2. Pin the current model
cronjob(action='update', job_id='<id>', model={'provider': '<provider>', 'model': '<model>'})
```

### Best practice

Always pin the model on any agent-driven cron. This makes the job explicit about
what it runs on, avoids surprise cost changes, and makes drift-failure diagnosis
trivial (the model field is visible in `cronjob list`).

Unpinned is acceptable only when you intentionally want the job to follow whatever
the global default is — but be prepared for it to block on the next update cycle.
