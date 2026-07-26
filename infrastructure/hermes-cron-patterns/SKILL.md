---
name: hermes-cron-patterns
description: "Hermes cron job patterns — timeout limits and background execution.

Load this skill when a cron job exceeds the 3-minute hard limit or needs to run long scripts. Covers the nohup background spawn pattern, script delivery, and timeout workarounds for the Hermes cron scheduler."
version: 1.0.0
author: Hermes Agent
tags: [hermes, cron, background, nohup, timeout]
type: Reference
timestamp: 2026-07-26T05:05:12Z
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
