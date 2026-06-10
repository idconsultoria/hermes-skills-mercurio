---
name: github-pr-workflow
description: "GitHub PR lifecycle: branch, commit, open, CI, merge."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    keywords: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge, PR-preview, Nginx-Proxy-Manager, ARM64, deployment]
    related_skills: [github-auth, github-code-review]
---

# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle. Each section shows the `gh` way first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

This part is pure `git` — identical either way:

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

### Pitfall: Branch checkout from detached HEAD creates the wrong name

When checking out a branch from a detached HEAD state (e.g., after a `cherry-pick` on a temp branch), `git checkout <branch-name>` creates a **local branch tracking `origin/<branch-name>`** but the local name can be `temp-fix-branch` if you were on a branch with that name.

**Check before pushing:**

```bash
# Always verify the BRANCH NAME matches what you intend to push
git branch --show-current
# If it says 'temp-fix-branch' when you wanted 'feat/my-feature':
git checkout -B feat/my-feature origin/feat/my-feature
git cherry-pick temp-fix-branch
git branch -D temp-fix-branch
git push origin feat/my-feature
```

### Recovery: committed directly to master by accident

If you committed directly to `master` (or `main`) and need to move the commit into a PR:

```bash
# 1. Create a branch from the unintended commit (keeps the commit)
git branch feat/my-feature

# 2. Reset master back to before your commit (local only)
#    Use git log to find the commit hash just before yours
git log --oneline -5
git reset --hard <hash-before-your-commit>

# 3. Push the feature branch
git push -u origin feat/my-feature

# 4. Create PR from the branch
#    gh pr create --base master --head feat/my-feature

# IMPORTANT: Do NOT force-push master after reset.
# Many CI/CD setups block force-push to master for safety.
# Instead, create the PR from the branch and merge normally.
```

## 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

## 3. Pushing and Creating a PR

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

## 4. Monitoring CI Status

### Check CI Status

**With gh:**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

**With git + curl:**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### Poll Until Complete (git + curl)

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

## 5. Auto-Fixing CI Failures

When CI fails, diagnose and fix. This loop works with either auth method.

### Step 1: Get Failure Details

**With gh:**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### Step 3: Verify

Re-check CI status using the commands from Section 4 above.

### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

## 6. Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. Preview / Deploy CI (PR Preview Environments)

When a workflow deploys a preview environment for each PR, follow these patterns.

### 7.1 Validate Locally Before Push

Before pushing to trigger CI, always validate locally first:

```bash
# Backend tests
pytest tests/ -q --tb=short

# Frontend build (catches TypeScript errors that vitest may miss)
cd frontend && npm run build

# Frontend tests
cd frontend && npm test
```

**Pitfall:** `vitest` and `npm run build` (`tsc -b`) catch different errors. Vitest transforms on-the-fly and can miss type errors in JSX files that aren't directly under test. Always run `npm run build` before push.

**Pitfall — Model/migration drift:** When a SQLAlchemy model class has columns that aren't in the database (e.g., a feature branch added `google_event_id` to the Task model but no migration was generated), the ORM crashes with `UndefinedColumnError` as soon as **any** query touches that table — even unrelated operations like registration trigger it (due to user-level eager loading). Catch this before pushing:

```bash
# Generate a migration against a fresh test DB
SECRET_KEY=x DATABASE_URL=sqlite+aiosqlite:///./check.db alembic upgrade head
SECRET_KEY=x DATABASE_URL=sqlite+aiosqlite:///./check.db alembic revision --autogenerate

# Review the generated file — remove destructive SQLite noise
# (SQLite generates DROP INDEX / CREATE FOREIGN KEY for every table on PostgreSQL)
# Strip to only ADD COLUMN / CREATE TABLE / ALTER statements
```

When the `upgrade()` function contains `DROP INDEX` and `CREATE FOREIGN KEY` for tables you didn't touch, it's autogenerate noise from SQLite naming conventions — **do NOT apply it as-is**, or it will drop real indexes on PostgreSQL.

### 7.2 SSH Deploy with appleboy/ssh-action

The `appleboy/ssh-action@v1` action runs the script as bash commands on a remote server. **Shell variables set via `VAR=value` are NOT exported to child processes.**

```yaml
# ❌ BROKEN: PR_NUMBER is a shell var, not visible to `docker compose`
script: |
  PR_NUMBER=${{ github.event.number }}
  docker compose pull              # $PR_NUMBER is empty here
  PR_NUMBER=$PR_NUMBER docker compose up -d

# ✅ FIXED: use `export` to make it available to all subsequent commands
script: |
  PR_NUMBER=${{ github.event.number }}
  export PR_NUMBER
  docker compose pull               # $PR_NUMBER is set
  docker compose up -d
```

### 7.3 Docker Compose Pull Needs Env Vars

- `docker compose pull` reads `image:` from docker-compose.yml, which may reference `${PR_NUMBER}` — needs the env var exported to the process
- `docker pull ghcr.io/...:pr-${PR_NUMBER}` works with shell variable inline (no export needed)
- When using `docker compose pull`, the env var MUST be exported (see 7.2)

### 7.4 GHCR_TOKEN vs GITHUB_TOKEN

- `secrets.GITHUB_TOKEN` is auto-generated, scoped to the current workflow run — NOT available on remote servers
- `secrets.GHCR_TOKEN` is a personal token with `packages:write` scope, required for `docker login` on the deploy server
- `docker/login-action@v3` inside the CI runner works with `GITHUB_TOKEN`; `appleboy/ssh-action` on a remote server needs `GHCR_TOKEN`

### 7.5 Diagnosing "Workflow File Issue" (Zero Jobs)

When a workflow run fails instantly with "workflow file issue" and zero jobs:

1. YAML is syntactically valid (Python `yaml.safe_load` passes) but GitHub rejected it
2. Common causes:
   - `needs:` referencing a job with incompatible `if:` condition (scheduling deadlock)
   - Escaped backticks `\`` in JS template literals inside YAML `|` blocks — use string concatenation
   - Missing `github-token:` on `actions/github-script@v7`
3. Fix: inline jobs, remove `needs`, use string concatenation, add explicit `github-token`

### 7.6 Fetching PR Run Logs

```bash
# gh run view may 404 on PR runs (?exclude_pull_requests=true)
# Workaround: list runs, find the ID, then use the ID directly
gh run list --repo $OWNER/$REPO -L 5 --json number,headSha,workflowName,conclusion
gh run view <ACTUAL_RUN_ID> --repo $OWNER/$REPO --log
```

### 7.7 Preview Database Creation

When a preview compose file has a `db-init` service, that service often uses `profiles: ["manual"]` so it doesn't auto-start with `up -d`. The backend will crash if the database doesn't exist.

**Option A — Create the database on the server after deploy:**

```yaml
script: |
  PR_NUMBER=${{ github.event.number }}
  export PR_NUMBER
  docker compose -f docker-compose.yml -f docker-compose.preview.yml up -d backend frontend
  # Create the preview database (service with profiles: ["manual"] won't auto-run)
  docker exec taskflow-db psql -U taskflow -c "CREATE DATABASE taskflow_pr_${PR_NUMBER}" 2>/dev/null || true
  docker exec taskflow-db psql -U taskflow -d taskflow_pr_${PR_NUMBER} -c "CREATE EXTENSION IF NOT EXISTS pgcrypto" 2>/dev/null || true
  docker restart taskflow-backend-${PR_NUMBER}
```

**Option B — Start the db-init service explicitly:**

```bash
docker compose -f docker-compose.yml -f docker-compose.preview.yml run --rm db-init
```

Note: `docker compose run` starts a one-shot container — it bypasses the `profiles: ["manual"]` restriction.

### 7.8 Nginx Proxy Manager — Registering a Preview Host

When using Nginx Proxy Manager (NPM) as the reverse proxy, **CRUCIAL: modifying the NPM SQLite database with `docker cp` does NOT trigger nginx config regeneration.** NPM needs to be running as a Node.js process to read the DB and write config files.

**Correct approach: write the nginx config directly into the NPM container.**

The config lives in `/data/nginx/proxy_host/N.conf` inside the NPM container. Create one per preview:

```yaml
- name: Register preview host in NPM
  uses: appleboy/ssh-action@v1
  with:
    host: <server-ip>
    username: ubuntu
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      PR_NUMBER=${{ github.event.number }}
      export PR_NUMBER
      cat > /tmp/preview-${PR_NUMBER}.conf << 'NGINX_CONF'
      server {
        listen 80;
        listen [::]:80;
        server_name ${PR_NUMBER}.praxis.129.146.163.107.sslip.io;

        # API routes -> backend
        location /api/ {
          proxy_pass http://taskflow-backend-${PR_NUMBER}:8000;
        }
        location /health {
          proxy_pass http://taskflow-backend-${PR_NUMBER}:8000;
        }
        location /auth/ {
          proxy_pass http://taskflow-backend-${PR_NUMBER}:8000;
        }

        # Everything else -> frontend (SPA)
        location / {
          include conf.d/include/proxy.conf;
        }
      }
NGINX_CONF
      docker cp /tmp/preview-${PR_NUMBER}.conf nginx_proxy_manager:/data/nginx/proxy_host/${PR_NUMBER}.conf
      docker exec nginx_proxy_manager nginx -s reload
```

**Key rules for NPM preview hosts:**
- `ssl_forced=1` with `certificate_id=0` breaks: NPM forces HTTPS with no cert → "Can't load page". Set `ssl_forced=0` (HTTP-only) or obtain a Let's Encrypt cert for the domain.
- The `proxy_host` table in NPM's SQLite has `certificate_id NOT NULL` — you cannot set it to NULL. If `ssl_forced=1`, a valid cert_id is required.
- The nginx config must split routes: `/api/`, `/health`, `/auth/` → backend; `/` → frontend (SPA)
- The NPM container's nginx config lives in `/data/nginx/` — NOT `/etc/nginx/` (which is generated from the database)
- After writing the config, always run `nginx -t` before `nginx -s reload` to catch syntax errors

**Cleanup (PR close):**

```yaml
script: |
  PR_NUMBER=${{ github.event.number }}
  export PR_NUMBER
  docker exec nginx_proxy_manager rm -f /data/nginx/proxy_host/${PR_NUMBER}.conf 2>/dev/null
  docker exec nginx_proxy_manager nginx -s reload 2>/dev/null || true
```

### 7.9 Shared Volume Permission Pitfalls

When the CI agent (Hermes) and the deploy server share a volume (e.g., Docker socket mount), files written by the agent may be owned by a different UID (e.g., 10000 inside the container) than the host user (e.g., 1001 on Ubuntu).

**Symptom:** `docker cp` fails with `Can't add file to tar: permission denied` when the file doesn't have world-read permissions.

```bash
# Fix on the agent side — set world-readable before SSH
chmod 644 /shared/path/to/file

# Fix on the server side — make the shared volume world-writable (one-time)
ssh host 'sudo chmod -R o+w /home/ubuntu/selfhost/shared/code/workstation/taskflow/'
```

**Prevention:** When creating files that will be `docker cp`'d into a container from an SSH session, always set permissions to 644 (readable by all) before the SSH command.

### 7.10 Building ARM64 Images for PR Preview

If the deploy server is ARM64 (e.g., Oracle Ampere A1) and the CI runner is AMD64, the PR preview workflow needs QEMU to build native ARM images:

```yaml
- name: Set up QEMU (multi-arch)
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push backend
  uses: docker/build-push-action@v6
  with:
    context: ./backend
    push: true
    platforms: linux/arm64     # native on the ARM server
    tags: ghcr.io/.../backend:pr-${{ github.event.number }}
```

Without this, the preview runs under QEMU emulation on the server — slower, with risk of Python C-extension deadlocks (pydantic-settings, uvloop, orjson). See `deployment-pipeline` skill for the full platform strategy (multi-arch vs single-arch trade-offs).

### 7.11 Preview Database Seeding

After deploying a preview, seed it with realistic data so the reviewer can interact with a full, working environment rather than an empty database.

**Key design decisions:**

| Decision | Recommendation | Why |
|----------|---------------|-----|
| **Script approach** | Raw SQL via SQLAlchemy `text()` (async) | Fast, no ORM overhead, works on both SQLite and PostgreSQL |
| **Idempotency** | DELETE all rows before INSERT | Preview DBs are ephemeral — no data to preserve |
| **Data scope** | 1 user + 8-15 contexts + 5-8 projects + 30-50 tasks + subtasks + reports + webhooks | Enough to test all GTD states without overwhelming the preview |
| **Realism** | Portuguese titles, 2-week timeline, mix of completed/pending/overdue tasks | Reviewer immediately understands what they're looking at |

**Seed script structure:**

```python
# backend/scripts/seed_preview.py
import asyncio, uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy import text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
NOW = datetime.now(timezone.utc)
MONDAY = NOW.replace(...) - timedelta(days=14 + NOW.weekday())

def _ts(day_offset, hour=12, minute=0):
    # ⚠️ Return datetime OBJECT, not .isoformat() string
    # PostgreSQL/asyncpg rejects ISO strings for datetime columns
    return MONDAY + timedelta(days=day_offset, hours=hour-8, minutes=minute)
```

**⚠️ PostgreSQL vs SQLite seed script pitfalls:**

| Issue | SQLite (lenient) | PostgreSQL (strict) | Fix |
|-------|-----------------|---------------------|-----|
| **Date/datetime params** | Accepts ISO strings `'2026-05-25T08:00:00+00:00'` | Requires `datetime` or `date` objects | `return d` not `return d.isoformat()` |
| **Boolean params** | Accepts `0`/`1` integers | Requires `True`/`False` | Pass Python booleans, not integers |
| **Date-only params** | Accepts string `'2026-05-25'` | Requires `date()` object | `return d.date()` not `return d.date().isoformat()` |

These three errors cause the seed script to crash on PostgreSQL at runtime. The `_ts()` helper must return `datetime` objects (not strings), and all boolean columns (`is_active`, `consumed`, `is_flagged`, `is_done`) must receive Python `True`/`False`, not `0`/`1`.

**Integration into the preview pipeline:**

Add a separate step after the deploy step that copies the seed script into the backend container and runs it:

```yaml
      - name: Seed preview database
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: ubuntu
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            set -e
            PR_NUMBER=${{ github.event.number }}
            export PR_NUMBER
            echo "[seed] Copying seed script to backend container..."
            docker cp /path/to/seed_preview.py \
              taskflow-backend-${PR_NUMBER}:/app/scripts/seed_preview.py
            echo "[seed] Running seed against taskflow_pr_${PR_NUMBER}..."
            docker exec \
              -e DATABASE_URL="postgresql+asyncpg://user:pass@db:5432/taskflow_pr_${PR_NUMBER}" \
              -e SECRET_KEY=*** \
              taskflow-backend-${PR_NUMBER} python /app/scripts/seed_preview.py
```

**PITFALL — file not found inside container:** The seed script lives in the repo's `backend/scripts/` directory. But the backend Docker image may not include it (if `.dockerignore` excludes scripts/). Always `docker cp` the file into the running container rather than relying on it being baked into the image.

**Two-path fallback for repo location:** Since the server may have the repo at different paths:
```bash
docker cp /home/ubuntu/selfhost/taskflow/backend/scripts/seed_preview.py \
  taskflow-backend-${PR_NUMBER}:/app/scripts/seed_preview.py 2>/dev/null || \
docker cp /home/ubuntu/selfhost/shared/code/workstation/taskflow/backend/scripts/seed_preview.py \
  taskflow-backend-${PR_NUMBER}:/app/scripts/seed_preview.py
```

### 7.12 Diagnosing Preview Accessibility

When a preview is deployed but you can't reach it, use the systematic reference at `references/preview-accessibility-diagnosis.md`:

1. Is the deploy workflow actually finished?
2. What services are defined in docker-compose and on which networks?
3. Does the reverse proxy (NPM/Nginx) have a route to the service?
4. Does the TLS certificate cover the preview hostname?
5. Is the container actually running on the server?

The reference covers each step with curl diagnostics, `docker inspect` checks, and a TLS error table.

### 7.13 Preview Workflow Complete Template

A complete preview workflow that covers the full lifecycle:

```yaml
name: PR Preview

on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

jobs:
  preview-deploy:
    if: github.event.action != 'closed'
    # ... build, push, deploy containers, create DB, register NPM ...
    
      - name: Seed preview database
        # ... see 7.11 above ...

      - name: Comment preview URL
        # ... see 7.10 above ...

  preview-cleanup:
    if: github.event.action == 'closed'
    # ... stop containers, drop DB, unregister NPM, remove images ...
```

The `closed` event type is included in the trigger explicitly (it is NOT in the default set of `pull_request` types). Without it, the cleanup job never fires.

## 8. Complete Workflow Example

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see Section 4)

# 8. Merge when green (see Section 6)
```

## Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` |
| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
