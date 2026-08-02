---
name: selfhost-web-apps
description: "Deploy web apps on Oracle ARM64 — Docker Compose, NPM, SSL, and hardening.

Load this skill when deploying PHP, Python, or Node web applications on the Oracle host behind Nginx Proxy Manager. Covers the standard architecture pattern, SSL termination, PHP redirect loop fixes, and post-deploy hardening."
type: ToolIntegration
timestamp: 2026-07-26T05:05:12Z
category: infrastructure
---

# Selfhost Web Apps on Oracle ARM64

Pattern for deploying PHP/Python/Node web apps behind Nginx Proxy Manager on the Oracle ARM64 host.

## Trigger

User wants to deploy a new web application (LMS, CMS, dashboard, API) on the Oracle host under a custom domain with SSL.

## Standard Architecture

```
/home/ubuntu/selfhost/<app>/
├── docker-compose.yml    ← app + nginx + db + cache + cron
├── Dockerfile            ← if custom build needed
├── .env                  ← domain, creds, lang, tuning
├── config/
│   ├── nginx/            ← conf.d/<app>.conf
│   └── <app>/            ← app-specific config overrides
├── scripts/              ← setup.sh, cron scripts
└── data/                 ← persistent volumes (bind mounts)
    ├── html/             ← app source code
    ├── <app>data/        ← uploads, cache, sessions
    ├── postgres/         ← DB data
    └── redis/            ← cache data
```

## Docker Compose Pattern

```yaml
services:
  app:
    build: .
    container_name: <app>-app
    restart: unless-stopped
    depends_on: {postgres: {condition: service_healthy}, redis: {condition: service_healthy}}
    volumes: [./data/html:/var/www/html, ./data/<app>data:/var/<app>data, ...]
    networks: [<app>-net]

  nginx:
    image: nginx:stable
    container_name: <app>-nginx
    restart: unless-stopped
    ports: ["<CHOOSE_FREE_PORT>:80"]    # 8082, 8083, etc — check with `ss -tlnp`
    volumes: [./config/nginx/conf.d:/etc/nginx/conf.d:ro, ...]
    networks: [<app>-net, proxy_network]  # proxy_network is external for NPM

  postgres:
    image: postgres:16
    container_name: <app>-postgres
    restart: unless-stopped
    environment: {POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD}
    volumes: [./data/postgres:/var/lib/postgresql/data]
    healthcheck: {test: ["CMD-SHELL", "pg_isready -U <user>"]}
    networks: [<app>-net]

  redis:
    image: redis:7-alpine
    container_name: <app>-redis
    restart: unless-stopped
    volumes: [./data/redis:/data]
    healthcheck: {test: ["CMD", "redis-cli", "ping"]}
    networks: [<app>-net]

networks:
  <app>-net: {driver: bridge}
  proxy_network: {external: true}
```

## NPM Routing

### 1. Find a free port

```bash
ssh oracle-host 'ss -tlnp | grep -E "808[0-9]"'
# Pick next free: 8082, 8083, 8084...
```

### 2. Create proxy host via SQLite

```bash
ssh oracle-host 'docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite'
```

```python
import sqlite3, json
from datetime import datetime, timezone

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
c = sqlite3.connect("/tmp/npm.sqlite").cursor()

c.execute("""INSERT INTO proxy_host 
    (created_on, modified_on, owner_user_id, domain_names, forward_host, forward_port, 
     forward_scheme, ssl_forced, enabled, http2_support, certificate_id, caching_enabled, 
     allow_websocket_upgrade, access_list_id, advanced_config, locations, block_exploits, 
     hsts_enabled, hsts_subdomains, meta, trust_forwarded_proto)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (now, now, 1, json.dumps(["sub.domain.com"]), "<app>-nginx", 80, "http",
     0, 1, 0, 0, 0, 0, 0, "", json.dumps([]), 1, 0, 0, json.dumps({}), 0))
c.connection.commit()
```

**⚠️ IMPORTANT:** Set `certificate_id=0` and `ssl_forced=0` initially. After the proxy host is created, the user adds the Let's Encrypt certificate via NPM UI (port 81). Then update the proxy host to use the cert ID and set `ssl_forced=1`.

```bash
docker cp /tmp/npm.sqlite nginx_proxy_manager:/data/database.sqlite
docker restart nginx_proxy_manager  # required for proxy host changes to take effect
```

## SSL Redirect Loop (PHP apps behind NPM)

**Symptom:** `ERR_TOO_MANY_REDIRECTS` in browser. `curl -I` shows 303 looping to the same URL.

**Root cause:** NPM terminates SSL → internal nginx receives HTTP → PHP-FPM sees no HTTPS. The app redirects to its HTTPS wwwroot, creating a loop.

### 🧠 Debugging principle: root-cause-first

When an app shows **multiple symptoms** (redirect loops + broken CSS + broken JS + broken images + broken fonts), **do not patch symptom-by-symptom**. One root cause can explain all of them. Investigate in this order:

1. ✅ Narrow the failure to a specific layer (browser? proxy? nginx? PHP? DB?)
2. ✅ Test bypassing the proxy: access the internal port directly
3. ✅ Does a single config setting explain all symptoms?
4. ❌ Don't: apply separate workarounds for each asset type

> **Concrete example from this repo:** `$CFG->reverseproxy = true` was the single root cause breaking 4 asset-serving PHP scripts simultaneously (image.php, font.php, javascript.php, styles.php). The initial response was to warm caches for each individually — that was the wrong approach. The fix was removing one config line.

**Fix — two changes needed:**

### 1. Nginx config: pass HTTPS to PHP-FPM

```nginx
# In the location ~ \.php block:
location ~ \.php(/|$) {
    # ... other config ...
    include        fastcgi_params;
    fastcgi_param  HTTPS on;           # ← ADD THIS
    fastcgi_pass   <app>:9000;
}
```

### 2. App config: trust the SSL proxy (PHP apps)

Moodle — `sslproxy` ONLY:
```php
$CFG->sslproxy = true;
// ⚠️ Do NOT set reverseproxy=true. It triggers setup_get_remote_url() in
// lib/setuplib.php to compare $rurl host vs $wwwroot host. When they match
// (normal behind NPM/Docker), it throws 'reverseproxyabused' — killing the
// full Moodle bootstrap path needed by image.php, font.php, javascript.php,
// and styles.php on first request (before localcache exists).
// sslproxy=true + fastcgi_param HTTPS on is sufficient for HTTPS awareness.
```

WordPress (`wp-config.php`):
```php
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
```

Generic PHP:
```php
$_SERVER['HTTPS'] = 'on';
```

### 3. Purge caches after config changes

```bash
docker exec <app>-app php /var/www/html/admin/cli/purge_caches.php
```

## PHP App Config Permissions

Moodle and similar apps set config files to `root:www-data` with `640` after install. The `ubuntu` host user can't read them:

```bash
# Read protected config
sudo cat /home/ubuntu/selfhost/<app>/data/html/config.php

# Edit protected config
sudo sed -i '/pattern/a\new line' /home/ubuntu/selfhost/<app>/data/html/config.php
```

## Resource Monitoring

Check impact before/after deploy:

```bash
ssh oracle-host 'free -h && docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
```

Oracle free tier: 2 ARM vCPUs, 11.65 GiB RAM. With 20+ containers at ~5.5 GiB used, leave ~6 GiB headroom.

## References

- `references/moodle-selfhost.md` — Full Moodle 5.2 deployment on ARM64: Docker Compose, nginx HTTPS passthrough, `sslproxy` vs `reverseproxy` pitfall, diagnostic workflow for asset 500s, SCSS pipeline pitfall (fields don't compile in 5.2), `additionalhtmlhead` workaround for CSS injection, login page dark-theme polish lessons, agy CSS generation workflow, Chromium `background-clip: text` and `.visually-hidden` pitfalls, user creation and course enrolment via SQL, admin account promotion/demotion via `siteadmins`, language string customization and caching pitfalls
- `references/id-consultoria-brand-tokens.md` — ID Consultoria design system: colors, typography, shadows, Google Fonts URL, and Moodle Boost Union mapping table
- `references/npm-proxy-host-insert.md` — Complete NPM SQLite proxy host insert recipe
- `templates/post-deploy-moodle.sh` — Minimal post-deploy: just `build_theme_css.php` (no warm caches needed after the reverseproxy fix)
