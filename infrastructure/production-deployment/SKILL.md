---
name: production-deployment
description: "Post-CI deploy operations — Docker rollout, DB schema, ingress routing, DNS fallback.

Load this skill when deploying a built application to production: verifying DB migrations ran, diagnosing container startup failures, checking Nginx/NPM routing, or handling a domain that stopped resolving. Covers the gray zone between CI completing and the site being live — the step most pipelines leave unscripted."
version: 1.5.0
author: Hermes Agent
license: MIT
type: ToolIntegration
timestamp: 2026-07-12T00:00:00Z
metadata:
  hermes:
    keywords: [Deploy, Production, Docker, PostgreSQL, Alembic, asyncpg, Nginx-Proxy-Manager, DNS, Migration, Rollout, OAuth, nip.io, LetEncrypt]
    related_skills: [github-pr-workflow, oracle-host-access]
---

# Production Deployment

Covers the deploy operations between CI completion and a live, healthy site: DB schema verification, container health diagnosis, ingress routing checks, and domain/DNS fallbacks.

## Docker Build Antipatterns

### Pre-built artifact COPY fails in CI

COPY references a directory that doesn't exist in the CI build context (e.g., `dist/` is gitignored). Docker's COPY fails immediately — even if a later RUN step generates the directory.

Fix: remove the COPY, let the multi-stage build handle it entirely via RUN commands.

## Post-Deploy Database Verification

### Alembic migration gap

Symptom: `asyncpg.exceptions.UndefinedColumnError: column tasks.<name> does not exist`.

Root cause: alembic_version was manually set to HEAD to unblock a failing migration, skipping actual migrations (014, 015, etc.).

Fix:
1. Find which migrations were skipped — compare `ls alembic/versions/` with the old `alembic_version` value
2. Read each skipped migration to list the exact columns/indexes it creates
3. Add missing columns via psql ALTER TABLE directly:
   ```sql
   ALTER TABLE tasks ADD COLUMN gcal_event_id VARCHAR(255);
   ALTER TABLE tasks ADD COLUMN due_date_has_time BOOLEAN NOT NULL DEFAULT true;
   CREATE INDEX idx_tasks_gcal_event ON tasks(gcal_event_id);
   ```
4. RESTART the backend container — **asyncpg caches prepared statements**, restart is mandatory, not optional

### Migration ordering: constraint before backfill

Symptom: `CheckViolationError` during migration.

Root cause: Migration A (constraint) runs before Migration B (backfill legacy data). Legacy rows violate the new constraint.

Design rule: Data-repair must have a LOWER revision number than constraint-creation. Or merge both into one migration.

### ⚠️ Setting alembic_version to HEAD skips intermediate migrations

When the backend won't start and you bypass the problematic migration by doing:
```sql
INSERT INTO alembic_version (version_num) VALUES ('015');
```
you tell Alembic "015 and everything before it is applied" — even if 014 and 015 never actually ran. The schema ends up missing columns those migrations create.

**Better approach** when a single migration is broken:
1. Drop the problematic object (constraint, column) manually from the DB
2. Fix the migration source code in the repo
3. Delete the alembic_version row for that revision so Alembic re-runs it on next restart
4. Never set the version ahead of what was actually executed

**If you already made the mistake and have a version gap:**
1. Read each skipped migration to list its exact DDL
2. Apply the DDL manually via psql
3. **Restart the backend container** — asyncpg caches prepared statements against the old schema. Without restart, you'll keep getting `UndefinedColumnError` even with the columns present in the DB.

## Nginx Proxy Manager Routing

After deploy: verify DNS resolves, NPM config points to correct upstream, containers share the same Docker network, SSL certs exist.

### Adding a new proxy host when NPM API password is unknown

You need an NPM proxy host for a fallback domain (e.g., nip.io after DDNS died) but don't have the NPM admin password.

**Option A — Direct SQLite insert** (skip API):
```bash
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite
```
Inspect current hosts via Python, then insert, then copy back to container.

**⚠️ Limitations:** No Let's Encrypt cert possible from raw DB insert — `certificate_id=0` gives proxy host without SSL.

> 📘 **NPM SQLite schema reference:** `skill_view(name='production-deployment', file_path='references/npm-database-schema.md')` — columns, defaults, and testing commands for proxy_host and certificate tables.

**Option B — API login** (if password is known):
```bash
TOKEN=$(curl -s -X POST http://localhost:81/api/tokens \
  -H "Content-Type: application/json" \
  -d '{"identity":"admin@example.com","secret":"password"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
```
Then POST to `/api/nginx/proxy-hosts` with `"certificate_id":"new"` and `letsencrypt_agree:true`.

**Option C — Browser tool** on NPM web UI (port 81): ask the user to log in, then add the proxy host manually through the interface.

### Testing NPM routing locally

After adding a proxy host, verify the routing chain before relying on external DNS:

```bash
# Test with correct Host header through internal nginx
ssh oracle-host 'curl -s -o /dev/null -w "%{http_code}" \
  -H "Host: praxis.129.146.163.107.nip.io" \
  http://localhost:8080/api/v1/health'

# Test from inside NPM itself (internal Docker network)
ssh oracle-host 'docker exec nginx_proxy_manager curl -sS \
  http://taskflow-nginx:80/api/v1/health'

# Verify DNS resolution of the new domain
ssh oracle-host 'docker run --rm busybox nslookup \
  praxis.129.146.163.107.nip.io 8.8.8.8'
```

### nip.io (or sslip.io) with Google OAuth

If using nip.io/sslip.io as a DDNS-free domain, the redirect URI will be **HTTP**, not HTTPS — because no SSL certificate exists for the wildcard domain (nip.io doesn't do certs). Google OAuth does not accept HTTP redirect URIs for non-localhost domains.

To make this work, you need:
1. Add the nip.io domain as a proxy host in NPM
2. Request a Let's Encrypt cert for it via the NPM API or web UI
3. Register `https://<your>.nip.io/api/v1/.../callback/` in Google Cloud Console
4. Set `GOOGLE_REDIRECT_URI` in .env to match exactly

Let's Encrypt HTTP-01 validation works because nip.io resolves to the server IP on port 80, which NPM handles.

## Environment Variable Validation

### Symptom: Google OAuth returns `Missing required parameter: client_id`

This means `GOOGLE_CLIENT_ID` (or the secret/redirect URI) is missing from the environment the backend actually reads.

### ⚠️ Pitfall: `docker compose restart` ignores ALL `.env` changes — always use `up -d`

`docker compose restart` **never** re-reads the compose file or any `.env` reference — it just restarts the existing container with its original configuration. Both `env_file:` and `${VARIABLE}` substitutions are resolved **at container creation time only**.

```bash
# ❌ Never loads new .env variables
docker compose restart backend

# ✅ Recreates container, re-evaluates env_file + variable substitution
docker compose up -d backend
```

**Always verify** the vars reached the container:

```bash
docker exec <container> env | grep -E "^GOOGLE_|^CORS_|^SOME_KEY"
```

If the expected env vars are missing even after `up -d`, check the `.env` file format: trailing whitespace, unclosed quotes, or misplaced comments (e.g., a comment between the last env line and the new section) can silently break parsing past that point. Run `grep -n 'GOOGLE\|^#' .env` on the host to verify the new lines are present and in the right position.

### Recovery: find backup env files

The production `.env` may be outdated or incomplete. Search for backup copies across the host:

```bash
sudo find /home /root /etc -name ".env*" -o -name "*.env" 2>/dev/null
```

Check common locations:
- The project's original config in a dev/backup clone (`/home/ubuntu/selfhost/hermes/data/taskflow-pr/.env`)
- Docker volume backups
- `.env.example` files as a reference for which vars are expected

Once found, update the production `.env` and restart the relevant container.

### Google Calendar OAuth redirect URI mismatch

Even with the correct `GOOGLE_CLIENT_ID`, the redirect URI must match **exactly** what's registered in Google Cloud Console. If the production domain changed (e.g., DDNS went down and you switched to sslip.io), update BOTH:

1. `GOOGLE_REDIRECT_URI` in the production `.env`
2. The "Authorized redirect URIs" in Google Cloud Console

**Validation flow after configuring:**

```bash
# 1. Verify env vars are in the container
docker exec <backend> env | grep -E "^GOOGLE_|^GCAL_|^CORS_"

# 2. Hit the auth-url endpoint (requires an auth token)
TOKEN=$(curl -s -X POST "https://your.domain/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@domain.dev","name":"Test","password":"Test123!"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X GET "https://your.domain/api/v1/integrations/google/auth-url/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
# Expected: {"url":"https://accounts.google.com/o/oauth2/v2/auth?client_id=..."}
# The redirect_uri in the returned URL must match what's registered in GCloud.
```

**Cannot configure OAuth client via CLI** — the authorized redirect URIs in Google Cloud Console can only be set through the web UI at `https://console.cloud.google.com/apis/credentials`. Even `gcloud` CLI doesn't expose this configuration.

## Deployment Verification — What Code Is Actually Running

> 📘 **Pre-merge branch analysis:** `skill_view(name='production-deployment', file_path='references/pre-merge-branch-analysis.md')` — commands to assess how far branches have diverged, anticipate conflict risk, and recover from an aborted merge. Use BEFORE any merge attempt on diverged branches.

After a CI/CD push completes, verify that the **intended commit** is what's actually running in production — CI can report success while the deploy step silently fails (wrong tag, stale image, pull error).

### 1. Check Running Images and Their Ages

```bash
ssh deploy-host 'docker compose images'
```

Sample output:
```
CONTAINER           REPOSITORY                                       TAG       CREATED
taskflow-backend    ghcr.io/org/repo/backend                         latest    2 weeks ago
```

Note the **CREATED** column — it tells you when the image was built. Compare with git commit timestamps.

### 2. Cross-Reference Image Build Time with Git Commits

```bash
# Get image creation timestamp (UTC)
ssh deploy-host 'docker inspect <repo>/backend:latest \
  --format "{{.Created}}"'

# Get latest master commit timestamp (author date)
git log origin/master --format="%H %ai %s" -1
#                SHA ^      ^ author date (with TZ)
```

The image `Created` timestamp should be **within minutes** of the git commit's author date (or committer date, whichever is later). A gap of hours or days means CI pushed a stale image or the deploy job didn't run.

### 3. Check the Image Digest (SHA256)

The image SHA is a content-addressable hash of the actual layers:

```bash
ssh deploy-host 'docker inspect <repo>/backend:latest \
  --format "{{.Id}}"'
# Returns: sha256:a6cc79224c92...
```

Useful when comparing across hosts or correlating with CI build logs.

### 4. Verify Container Config Matches Expectations

```bash
# Check which image tag a running container was started from
ssh deploy-host 'docker inspect $(docker compose ps -q backend) \
  --format "{{.Config.Image}}"'
# e.g. ghcr.io/org/repo/backend:latest

# Verify expected env vars reached the container
ssh deploy-host 'docker exec <container> env | grep -E "^MY_VAR"'
```

### 5. Full Verification Sequence (Single SSH Call)

```bash
ssh deploy-host ' \
  echo "=== IMAGES ===" && \
  docker compose images && \
  echo "=== BACKEND IMAGE ===" && \
  docker inspect $(docker compose ps -q backend 2>/dev/null) \
    --format "{{.Config.Image}} — Created: {{.Created}}" && \
  echo "=== HEALTH CHECK ===" && \
  curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health'
```

### 6. Pitfall: Images Tagged `latest` Can Stay Stale

If CI builds and pushes but the deploy host never runs `docker compose pull`, `:latest` still points to the old image. **Always check the `Created` date, not just the tag name.**

If the image is old, force a pull and recreate:

```bash
ssh deploy-host 'docker compose pull && docker compose up -d --remove-orphans'
```

## Domain / DDNS Fallback

When gotdns.ch (or similar free DDNS) goes offline, fall back to sslip.io or nip.io wildcard DNS — they resolve `<name>.<ip>.sslip.io` automatically with zero registration.

### Investigating a dead DDNS domain

When a domain stops resolving:

```bash
# Check current DNS servers
nslookup -type=NS broken-domain.ch 8.8.8.8

# Check RDAP/whois for registrar info
# (gotdns.ch domains are typically registered via easyname GmbH
#  and use no-ip.com DNS: nf1-4.no-ip.com)

# Verify server itself is reachable
curl -s -o /dev/null -w "%{http_code}" http://<server-ip>:<port>/health

# Test routing via internal nginx with correct Host header
curl -s -H "Host: <domain>" http://localhost:<npm-internal-port>/health
```