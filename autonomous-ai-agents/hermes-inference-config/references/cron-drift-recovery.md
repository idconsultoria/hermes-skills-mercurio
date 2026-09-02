# Cron drift recovery — 2026-09-01 session (Mercúrio)

Despining cures `HTTP 401` and `drift_skip` after model renames. Session verified on
`8a7f5f65ed76` (Ciclo de Consolidação) and `3dfe43219f1b` (Alíquota ISS).

## Symptoms observed

- `cronjob list` → `last_status: error`, `last_error: RuntimeError: HTTP 401: Model hy3-free is not supported`
  Output files in `$HERMES_HOME/cron/output/<job_id>/2026-09-01_02-01-07.md` contain `## Error` with the same 401.
- Earlier history same jobs showed `[drift_skip]` for unpinned jobs when `model.default` drifted
  (`deepseek-v4-flash` → `deepseek-v4-flash-vision-exp`, `opencode-free` → `opencode-go`).
  Output: `RuntimeError: [drift_skip] Skipped to prevent unintended spend ... model_snapshot differs`.
- `cronjob list` also showed `gateway_running: false` → `These jobs are saved but will NOT fire`.

## Diagnosis steps that worked

```bash
# 1. List jobs + last errors
hermes cron list
cat $HERMES_HOME/cron/jobs.json | python3 -c "import json; [print(j['id'], j['model'], j['provider'], j['last_error']) for j in json.load(open('jobs.json'))['jobs']]"

# 2. Inspect last cron output
ls -lt $HERMES_HOME/cron/output/8a7f5f65ed76/
grep -a "## Error" -A5 $HERMES_HOME/cron/output/8a7f5f65ed76/*.md | grep -E "RuntimeError|HTTP|drift"

# 3. Check current inference config (one key at a time)
hermes config get model
hermes config get providers
hermes config get fallback_providers
cat $HERMES_HOME/config.yaml | grep -A20 "model:\|fallback"
```

Config on 2026-09-01:

```yaml
model:
  default: muse-spark-1.2-contributor-free
  provider: opencode-free   # alias → opencode-zen @ https://opencode.ai/zen/v1
fallback_providers:
  - { model: muse-spark-1.2-contributor, provider: opencode-go, base_url: https://opencode.ai/zen/go/v1 }
  - { model: hy3, provider: opencode-go }
# hy3-free (opencode-free) no longer exists → pin to it gives 401
```

## Fix — despin to follow global (user preference 2026-09-01)

User said "Despine e deixe usar o global" → "Sim, despine todos". Preference is
inheritance, not pinning, for all crons.

```bash
hermes cron edit 8a7f5f65ed76 --model "" --provider ""  # Ciclo Consolidação
hermes cron edit 3dfe43219f1b --model "" --provider ""  # Alíquota ISS
# Both now show model: None / provider: None → inherit model.default + fallback chain
# Verify:
hermes cron list
cat $HERMES_HOME/cron/jobs.json | python3 -c "import json; print([(j['id'], j['model'], j['provider']) for j in json.load(open('jobs.json'))['jobs']])"
```

- Unpinning recalculates `model_snapshot`/`provider_snapshot` → drift guard (#44585) clears.
- Gateway must be running: `hermes cron status` / `hermes gateway start`. Without it, unpinned jobs still won't tick.

## When to re-pin instead

Only if cron must stay on a specific model regardless of global (e.g., heavy reasoning needs `hy3` on `opencode-go`). Then:

```bash
hermes cron edit <id> --model hy3 --provider opencode-go
# successor of hy3-free; verify it exists in providers/fallback_providers first
```

## References in this repo

- This recovery pattern extends `hermes-inference-config` SKILL.md section "CRITICAL — cron jobs follow the chain only when UNPINNED" and "Diagnosing model errors from logs".
- For consolidation cycle recovery after partial failure, see `skills-repo-curator` pitfalls ("Ciclo pode morrer no meio e deixar working directory sujo").
