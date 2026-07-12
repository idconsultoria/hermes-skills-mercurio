# Deploy Diagnostics Cheatsheet — TaskFlow Session

Actual commands and error patterns from the 2026-07-09 session that uncovered these patterns.

## Dockerfile COPY dist failure

**Error:**
```
#8 [builder 3/7] COPY dist /build/dist
#8 ERROR: failed to calculate checksum of ref ... /dist: not found
```

**Fix:** Remove the COPY line; the multi-stage build generates dist via `npm run build`.

## Alembic migration ordering failure

**Error during migration:**
```python
asyncpg.exceptions.CheckViolationError: new row for relation "tasks" violates
check constraint "ck_tasks_status"
Failing row: ... next_action, 2, null, null, f, 0, null, ...
```

**Recovery commands:**
```bash
# Drop constraint manually
docker exec taskflow-db psql -U taskflow -d taskflow \
  -c "ALTER TABLE tasks DROP CONSTRAINT IF EXISTS ck_tasks_status;"
# Reset alembic version
docker exec taskflow-db psql -U taskflow -d taskflow \
  -c "DELETE FROM alembic_version;"
# Restart to re-run all migrations
docker compose restart backend
```

## Alembic migration gap (manually set version too far ahead)

**Error during user registration:**
```python
asyncpg.exceptions.UndefinedColumnError: column tasks.due_date_has_time does not exist
```

**Root cause:** `alembic_version` was set to '015' (HEAD) manually, skipping 014 and 015.

**Columns that were missing:**
- `gcal_event_id VARCHAR(255) NULL` (migration 014)
- `google_sync_version INTEGER NULL` (migration 014)
- `push_failed BOOLEAN NOT NULL DEFAULT false` (migration 014)
- `due_date_has_time BOOLEAN NOT NULL DEFAULT true` (migration 015)
- Index: `idx_tasks_gcal_event ON tasks(gcal_event_id)` (migration 014)

**Fix commands:**
```bash
docker exec taskflow-db psql -U taskflow -d taskflow -c "
  ALTER TABLE tasks ADD COLUMN gcal_event_id VARCHAR(255);
  ALTER TABLE tasks ADD COLUMN google_sync_version INTEGER;
  ALTER TABLE tasks ADD COLUMN push_failed BOOLEAN NOT NULL DEFAULT false;
  ALTER TABLE tasks ADD COLUMN due_date_has_time BOOLEAN NOT NULL DEFAULT true;
  CREATE INDEX idx_tasks_gcal_event ON tasks(gcal_event_id);
"
# Restart is MANDATORY — asyncpg caches prepared statements
docker compose restart backend
```

## Registration API verification

```bash
curl -sS -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@debug.com","name":"Test Debug","password":"Test123!"}'
```

Expected response: `{"access_token":"eyJ...","user":{"id":"...",...}}`

## Google OAuth credentials missing

**Symptom:** Google Calendar auth redirect shows "Missing required parameter: client_id"

**Root cause:** Production `.env` lacks Google OAuth vars (exists in a backup copy).

**Recovery commands:**
```bash
# Find backup env files with Google vars
sudo find /home /opt -name ".env*" 2>/dev/null | xargs grep -l "GOOGLE_CLIENT" 2>/dev/null

# From the session: backup was at
# /home/ubuntu/selfhost/hermes/data/taskflow-pr/.env
sudo cat /home/ubuntu/selfhost/hermes/data/taskflow-pr/.env

# Required vars to add to production .env:
# GOOGLE_CLIENT_ID=589578583981-xxxxx.apps.googleusercontent.com
# GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx
# GOOGLE_REDIRECT_URI=<public-domain>/api/v1/integrations/google/callback/
# GCAL_ENCRYPTION_KEY=<32-char-hex>
```

## NPM proxy routing verification

```bash
# Check NPM proxy host config
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite
python3 << 'PYEOF'
import sqlite3, json
c = sqlite3.connect("/tmp/npm.sqlite").cursor()
c.execute("SELECT id, domain_names, forward_host, forward_port, ssl_forced, certificate_id FROM proxy_host WHERE is_deleted=0")
for r in c.fetchall():
    print(f"ID:{r[0]} DOMAINS:{r[1]} FORWARD:{r[2]}:{r[3]} SSL:{r[4]} CERT:{r[5]}")
c.close()
PYEOF

# Test routing from nginx_proxy_manager to taskflow-nginx
docker exec nginx_proxy_manager curl -sS http://taskflow-nginx:80/api/v1/health

# Test from external host with Host header
curl -s -H "Host: praxis.gotdns.ch" http://localhost:8080/api/v1/health

# DNS resolution
docker run --rm busybox nslookup praxis.129.146.163.107.sslip.io 8.8.8.8

# Check ACME cert expiry
ssh oracle-host 'docker exec nginx_proxy_manager cat /data/nginx/proxy_host/1.conf'
```

## NPM DB schema for proxy_host insert

When the NPM API password is unknown, insert proxy hosts directly:

```sql
-- minimal proxy_host insert
INSERT INTO proxy_host (
  created_on, modified_on, owner_user_id, is_deleted,
  domain_names, forward_host, forward_port, access_list_id,
  certificate_id, ssl_forced, caching_enabled, block_exploits,
  advanced_config, meta, allow_websocket_upgrade, http2_support,
  forward_scheme, enabled, locations, hsts_enabled, hsts_subdomains
) VALUES (
  datetime('now'), datetime('now'), 1, 0,
  '["praxis.129.146.163.107.nip.io"]',
  'taskflow-nginx', 80, 0,
  0, 1, 0, 0, '', '{}', 0, 0,
  'http', 1, NULL, 0, 0
);
```

Then `docker cp /tmp/npm.sqlite nginx_proxy_manager:/data/database.sqlite`.

**⚠️ `certificate_id=0` means no SSL cert.** For Let's Encrypt, use the API or web UI.
