---
name: selfhost-service-deploy
description: "Deploy selfhosted services on Oracle ARM64 — Docker Compose, NPM routing, SSL.

Load this skill when deploying any new selfhosted service on the Oracle VM (Docker host). Follows the established pattern: directory structure, docker-compose.yml, Nginx Proxy Manager routing, SSL termination via Let's Encrypt, and common ARM64 pitfalls."
type: ToolIntegration
timestamp: 2026-07-26T05:05:12Z
category: infrastructure
---

# Selfhost Service Deploy — Oracle ARM64

## Trigger

User wants to deploy a new selfhosted service on the Oracle VM (the Docker host where Hermes, TaskFlow, Firecrawl, Delfos, and Moodle already run). Follow this pattern for ANY new service — web app, API, LMS, CMS, monitoring tool, etc.

## Prerequisites

- SSH access to the Oracle host via `ssh oracle-host` (see `oracle-host-access` skill)
- The service must be Dockerizable (official image, community image, or custom Dockerfile)
- Domain name routing: either a subdomain on an existing domain or a new domain pointing to the Oracle VM IP (`129.146.163.107`)

## Pattern: Directory Structure

All selfhosted services live under `/home/ubuntu/selfhost/<service>/`:

```
/home/ubuntu/selfhost/<service>/
├── docker-compose.yml    ← the single source of truth
├── .env                  ← credentials, domains, tuning
├── Dockerfile            ← only if building from source (skip if using pre-built image)
├── config/               ← app-specific configs (nginx, php, app configs)
├── scripts/              ← setup/entrypoint scripts (if any)
└── data/                 ← persistent bind mounts (NOT named volumes)
    ├── <service>-db/     ← database data
    ├── <service>-data/   ← app data (uploads, cache, etc.)
    └── ...
```

**Use bind mounts, not named volumes.** Bind mounts survive `docker compose down`, are easy to backup (`tar czf`), and follow the pattern of every existing service on this host.

## Pattern: docker-compose.yml

### Minimal service (behind NPM)

```yaml
services:
  app:
    image: <image>:<tag>
    container_name: <service>-app
    restart: unless-stopped
    ports:
      - "<free-port>:<internal-port>"
    env_file:
      - .env
    volumes:
      - ./data/app-data:/var/lib/app
    networks:
      - <service>-net
      - proxy_network        # ← for NPM routing
    healthcheck:
      test: ["CMD-SHELL", "..." ]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: database (use postgres:16 or postgres:17-alpine)
  db:
    image: postgres:16
    container_name: <service>-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./data/db:/var/lib/postgresql/data
    networks:
      - <service>-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Optional: redis cache
  redis:
    image: redis:7-alpine
    container_name: <service>-redis
    restart: unless-stopped
    volumes:
      - ./data/redis:/data
    networks:
      - <service>-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

networks:
  <service>-net:
    driver: bridge
  proxy_network:
    external: true
```

### Service with custom Dockerfile (ARM64 build)

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    # NO platform: restriction — let Docker build natively on ARM64
    ...
```

**Never add `platform: linux/amd64` to a service that is built on the Oracle host.** It forces QEMU emulation. Let Docker build natively for ARM64. Official images (postgres, redis, nginx, php) are already multi-arch.

### Service with separate nginx frontend

If the app serves on a non-standard port or needs custom nginx config, add an nginx container:

```yaml
  nginx:
    image: nginx:stable
    container_name: <service>-nginx
    restart: unless-stopped
    depends_on:
      - app
    ports:
      - "<free-port>:80"
    volumes:
      - ./config/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - <service>-net
      - proxy_network
```

## Pattern: NPM Proxy Host Setup

After `docker compose up -d`, create a proxy host in Nginx Proxy Manager:

### Step 1: Find a free port

```bash
ssh oracle-host 'ss -tlnp | grep -E "<port-range>"'
```

Common free ports on this host: 8082-8089 range. Check before using.

### Step 2: Add proxy host via SQLite

```bash
ssh oracle-host 'python3 << '\''PYEOF'\''
import sqlite3, json
from datetime import datetime, timezone

db = "/tmp/npm.sqlite"
c = sqlite3.connect(db).cursor()

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
c.execute("""
    INSERT INTO proxy_host 
    (created_on, modified_on, owner_user_id, domain_names, forward_host, forward_port, 
     forward_scheme, ssl_forced, enabled, http2_support, certificate_id, caching_enabled, 
     allow_websocket_upgrade, access_list_id, advanced_config, locations, block_exploits, 
     hsts_enabled, hsts_subdomains, meta, trust_forwarded_proto)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    now, now, 1,
    json.dumps(["YOUR-DOMAIN"]),   # e.g. ["service.praxis.gotdns.ch"]
    "SERVICE-CONTAINER-NAME",       # e.g. "moodle-nginx"
    80,                              # internal port on the container
    "http",
    0,   # ssl_forced — set to 1 AFTER cert is generated
    1,   # enabled
    1,   # http2
    0,   # certificate_id — set to cert ID AFTER generating SSL
    0,   # caching
    0,   # websocket
    0,   # access_list
    "",  # advanced_config
    json.dumps([]),
    1,   # block_exploits
    1,   # hsts
    0,   # hsts_subdomains
    json.dumps({}),
    0    # trust_forwarded_proto
))
c.connection.commit()
print(f"✅ Proxy host criado (id={c.lastrowid})")
c.close()
PYEOF
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite
python3 /tmp/add_proxy.py
docker cp /tmp/npm.sqlite nginx_proxy_manager:/data/database.sqlite
docker restart nginx_proxy_manager
```

### Step 3: SSL Certificate

The user handles SSL via NPM UI (port 81) since it needs authentication:
- Access `https://<host-ip>:81` (via SSH tunnel since port 81 is blocked by Oracle firewall)
- Add Let's Encrypt certificate for the domain
- Edit the proxy host → SSL tab → select certificate → Force SSL

**⚠️ Never reset NPM passwords without explicit user permission.**

## Pitfalls

### Port already allocated

Symptom: `Bind for 0.0.0.0:<port> failed: port is already allocated`

Fix: Check `ss -tlnp` on the host and pick a free port. This host has services on 80, 443, 3002, 5173, 5432, 6379, 8000, 8080, 8081, 8090, 8100, 8642, 8882, 9119.

### Nginx upstream DNS cache

Symptom: `connect() failed (111: Connection refused) while connecting to upstream` after container restart.

Fix: See `references/nginx-docker-dns-resolution.md`. Replace `upstream` blocks with direct `fastcgi_pass $variable;` + `resolver 127.0.0.11`.

### App behind reverse proxy sees HTTP instead of HTTPS

Symptom: redirect loops, mixed content warnings, broken asset URLs.

Fix: 
1. Add `fastcgi_param HTTPS on;` (or `proxy_set_header X-Forwarded-Proto https;`) in the nginx config
2. Configure the app to trust the proxy (varies by app):
   - Moodle: `$CFG->sslproxy = true;` (⚠️ Do NOT set `reverseproxy=true` — it triggers `reverseproxyabused` in `lib/setuplib.php`, killing the full bootstrap needed by asset scripts. `sslproxy` + `fastcgi_param HTTPS on` is sufficient.)
   - WordPress: `$_SERVER['HTTPS'] = 'on';` in wp-config.php
   - Generic PHP: check `$_SERVER['HTTP_X_FORWARDED_PROTO']`

### Theme/assets 500 after fresh install (Moodle, WordPress, etc.)

**Debugging principle: root-cause-first**

When multiple assets fail simultaneously (CSS + JS + images + fonts), one root cause likely explains all. Investigate in this order, not symptom-by-symptom:

1. Narrow the failure to a specific layer (browser? proxy? nginx? PHP? DB?)
2. Test bypassing the proxy: `curl http://localhost:<port>/path` from the host
3. Does a single config setting explain all symptoms?
4. Check if `reverseproxy` is set in the app config — this is the most common multi-symptom cause on this stack

Symptom: CSS/JS/image PHP handlers return 500 after first deploy. `curl -s -o /dev/null -w "HTTP %{http_code}" https://domain/theme/styles.php/...` returns 500.

Three distinct causes, in order of probability:

**Cause A — Assets never compiled.** The app's SCSS/JS compiler hasn't run yet.
Fix: Run the app's build command:
- Moodle: `php admin/cli/build_theme_css.php`
- Generic: check the app's CLI tools for asset compilation

**Cause B — Cache revision mismatch.** Assets exist on disk and are served correctly from the host (`curl http://localhost:<port>/...` returns 200), but the HTML page references a stale revision number. The CSS files in `moodledata/localcache/theme/<rev>/` have revision `<new_rev>` but the HTML page hardcodes `<old_rev>` in its stylesheet URLs.

Debug workflow:
```bash
# 1. Find the actual CSS revision on disk
docker exec <app> find /var/<app>data -name "*.css" 2>/dev/null | head -3
# Example output: .../theme/1784691380/boost/css/all_1784691703.css
#                                                      ^^^^^^^^^^ file revision

# 2. Compare with what the HTML page requests
curl -s https://domain/ 2>&1 | grep -o 'styles.php[^"]*' | head -1
# If this shows a DIFFERENT revision → it's Cause B

# 3. Verify the correct revision works
curl -s -o /dev/null -w "HTTP %{http_code}" "https://domain/theme/styles.php/boost/<THEMEREV>_<FILEREV>/all"
# If 200 → confirmed revision mismatch

# 4. Fix: purge caches (forces page regeneration with current revisions)
docker exec <app>-app php /var/www/html/admin/cli/purge_caches.php
# The next page load regenerates HTML with current revision numbers
```

**Cause A and B can coexist** on a fresh deployment — build assets first, then purge caches to sync HTML revisions.

**⚠️ Cause C (deprecated) — JS minification failing in PHP-FPM context.** Some symptoms that look like \"ARM64 minification failures\" (JS/image/font scripts returning 500 while others work) are actually caused by `$CFG->reverseproxy = true`, which blocks the full Moodle bootstrap that asset-serving PHP scripts need. Before debugging ARM64-specific issues, first confirm `reverseproxy` is NOT set in config.php. See `selfhost-web-apps` skill → SSL Redirect Loop section for the full explanation.

### Bind mount permissions (UID mismatch)

Symptom: Container can't write to data directories.

Fix: The container's user (e.g. `www-data`, uid 33) needs write access on the host's filesystem. After the first `docker compose up`, let the app's setup script fix permissions. If it fails, manually:
```bash
ssh oracle-host 'sudo chown -R 33:33 /home/ubuntu/selfhost/<service>/data/'
```
(33 is the Debian `www-data` uid inside PHP containers)

### SSH heredoc quoting hell with Python

Symptom: Python code inside SSH heredocs breaks due to quote conflicts.

Fix: Write the script as a file locally using `write_file`, then `scp` it to the host. Never nest Python code with quotes inside SSH heredocs.

```bash
# ✅ CORRECT
write_file /tmp/script.py            # Hermes tool
scp /tmp/script.py oracle-host:/tmp/

# ❌ BROKEN
ssh oracle-host 'python3 << EOF
...
EOF'
```

## Verification

After deploy, verify from both inside and outside:

```bash
# 1. Internal: test from host
ssh oracle-host 'curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:<port>/'

# 2. External: test through NPM
curl -s -o /dev/null -w "HTTP %{http_code}" https://<domain>/

# 3. Check container health
ssh oracle-host 'docker ps --filter "name=<service>" --format "table {{.Names}}\t{{.Status}}"'

# 4. Resource usage
ssh oracle-host 'docker stats <service>-app --no-stream'
```

## Existing Services (reference)

| Service | Path | Containers | Port | Domain |
|---------|------|-----------|------|--------|
| Hermes | `/home/ubuntu/selfhost/hermes/` | 1 | 8642 | — |
| NPM | `/home/ubuntu/selfhost/nginx-proxy-manager/` | 1 | 80,443 | — |
| TaskFlow | `/home/ubuntu/selfhost/taskflow/` | 7 | 8080 | praxis.gotdns.ch |
| Firecrawl | `/home/ubuntu/selfhost/firecrawl/` | 6 | 3002 | — (ai_mesh) |
| Delfos | ? | 3 | 8090 | sslip.io |
| SearXNG | `/home/ubuntu/selfhost/searxng/` | 2 | 8080 | — (ai_mesh) |
| Fish Speech | `/home/ubuntu/selfhost/fish-speech/` | 1 | 8882 | — (ai_mesh) |
| Qwen3-TTS | `/home/ubuntu/selfhost/qwen3-tts/` | 1 | 8881 | — (ai_mesh) |
| Moodle | `/home/ubuntu/selfhost/moodle/` | 5 | 8082 | treinamentos.idconsultoria.ai |
