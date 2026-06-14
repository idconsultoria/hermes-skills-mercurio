# Pipeline Failure Modes — IAF Manhã Aumentada

## Chain Overview

```
Cron #1 (Coleta) ──→ Cron #2 (Newsletters) ──→ Cron #3 (Síntese/PDF) ──→ Cron #4 (Deploy Web)
```

Each step depends on the previous. When a step fails, downstream steps may behave unexpectedly.

## Failure Mode Matrix

| Step Fails | Symptom | Downstream Impact | User Visible |
|---|---|---|---|
| #1 Coleta | Missing `iaf_coleta_*.md` | #3 has no source data → generates empty/poor newsletter | No — #3 still "succeeds" with bad content |
| #2 Newsletters | Missing `iaf_newsletters_*.md` | Same as above | No |
| **#3 Síntese/PDF** | **HTTP 429, skill error, timeout** | **#4 sees FAILED output → stays [SILENT]** | **No — pipeline is silent. User only notices if they check.** |
| #4 Deploy Web | Vercel auth/alias failure | Deploy stuck, old version still live | Yes — #4 reports error in its delivery |

## Patterns Observed

### Silent Cascade (Cron #3 → Cron #4)
When Cron #3 fails:
- Cron #4 (context_from: #3) correctly reads the FAILED header
- Deploy script returns "No new editions to deploy"
- Cron #4 responds `[SILENT]`
- **User receives no alert** — the entire pipeline went dark

**Mitigation:** The pipeline should ideally produce a daily heartbeat. Without one, monitor by:
- Checking `cronjob(action='list')` — look for `last_status: 'error'` on any IAF job
- Checking `/opt/data/cron/history/` for today's HTML + PDF

### Degraded Agent Context (Missing Skills)
When a cron job's skill list includes skills that don't exist:
- The cron runtime injects a warning: `"⚠️ Skill(s) not found and skipped: X"`
- This warning sits at the TOP of the agent's prompt — pollutes context before any instruction
- The agent proceeds without the skill's knowledge, potentially producing worse output

**Mitigation:** Before running the pipeline, verify skills exist:
```
skills_list() → check if all names in the cron job's `skills` array appear
```

**⚠️ Consolidation trap:** Missing skills may have been merged into an umbrella during prior repository consolidation. Check the skills repo log:
```
grep -i "newsletter\|curation\|<skill-name>" /opt/data/skills/log.md
```
Common IAF example: `newsletter-curation` and `iaf-newsletter` were absorbed into `iaf-newsletter-pipeline` on 2026-06-10. The fix is to replace them in the cron job's skills list with the umbrella skill name, not just remove them.

### Gemini Free Tier Quota (HTTP 429)
If the Cron #3 agent uses Gemini API on a free-tier key:
- `generate_content_free_tier_input_token_count` limit: 250K tokens
- After ~1-2 weeks of daily newsletters, this quota is typically exhausted
- The job gets a non-retriable 429 mid-generation

**Mitigation:**
- Upgrade to a paid Google API key
- Or switch to a non-Google provider for Cron #3 generation
- Or add retry logic with backoff in the pipeline prompt

## Diagnosis Cheat Sheet

```bash
# Check all pipeline cron statuses
cronjob action=list

# Check if today's artifacts exist
ls /opt/data/cron/history/iaf_$(date +%Y-%m-%d).html
ls /opt/data/cron/history/iaf_$(date +%Y-%m-%d).pdf

# Check cron output (even failed jobs save partial logs)
ls /opt/data/cron/output/e418042f0c99/   # Cron #3 job output dir

# Latest collection files
ls -lt /opt/data/cron/output/b874e9037245/*.md | head -3
ls -lt /opt/data/cron/output/c03bb6e1124c/*.md | head -3

# Read last N lines of failed cron output to see the error
tail -20 /opt/data/cron/output/e418042f0c99/$(ls -t /opt/data/cron/output/e418042f0c99/ | head -1)
```
