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

## Pattern: Build on the host (native ARM64) — NO GHCR/QEMU

**User preference (Gustavo, 14/08/2026):** for app projects (Zera, TaskFlow, VERO), the build
happens ON the Oracle host, natively for ARM64 — NOT in CI with QEMU emulation. The CI runs
lint/tests/E2E only; it never builds images. Rationale: the host IS ARM64, so `docker compose build`
compiles natively and fast; QEMU emulation of `npm install`/`npm run build` is slow and fragile (the
TaskFlow preview.yml had to add a "Build frontend assets (native, no QEMU)" step to work around it).

The full deploy flow for an app:

```
push to main → GitHub Actions (CI: lint+tests only)
                     │
                     ▼
        SSH → host → git pull --ff-only → docker compose build (native) → up -d → smoke
```

Key points:
- **Never build images in CI for ARM64 apps** — build on the host with `docker compose build`.
- **Never `git reset --hard` on the host** — the user has blocked this twice. Use
  `git pull --ff-only` (or `git fetch -f origin pull/N/head:pr-N && git checkout pr-N` for PRs).
  The shared volume / repo is the single source of truth; a hard reset can destroy uncommitted work.
- If the repo directory doesn't exist yet, `git clone` it; if it does, `pull --ff-only`.
- Deploy script shape (see Zera `infra/scripts/deploy_alfa.sh`): validate env → `docker compose build`
  → `up -d` → smoke test (health + ready + register→login through the reverse proxy).

### GitHub Secrets + Deploy Keys for the CD (headless, from Zera alfa setup 14/08)

To let GitHub Actions SSH into the host and clone the repo, set up ONCE per app:

1. **Deploy key for repo access (host → github):** generate on the host, add pub to the repo,
   configure `~/.ssh/config` so plain `git fetch` uses it:
   ```bash
   ssh oracle-host 'ssh-keygen -t ed25519 -f ~/.ssh/<app>_deploy_key -N "" -C "<app>-deploy-key"'
   ssh oracle-host 'cat ~/.ssh/<app>_deploy_key.pub' 2>/dev/null > /tmp/k.pub   # 2>/dev/null CRITICAL
   wc -l /tmp/k.pub                # must be 1 line — the ssh stderr warning pollutes otherwise
   gh repo deploy-key add /tmp/k.pub --title "<app>-host-oracle" --allow-write=false
   gh repo deploy-key list         # verify read-only
   ```
   Pitfall: `gh repo deploy-key add` takes a FILE PATH (not stdin); a 2-line pub file (warning + key)
   fails HTTP 422 "key is invalid".
2. **STAGING_SSH_KEY secret (actions → host):** generate a SEPARATE dedicated key per app
   (`~/.ssh/deploy-<app>-cicd`, authorized_keys += its pub) — do NOT reuse another project's key
   (individually revocable). Set the secret:
   ```bash
   gh secret set STAGING_SSH_KEY --body "$(cat /tmp/deploy-key)"   # ✅ --body-file missing on older gh
   gh secret list                                                   # ✅ ALWAYS verify — a failed
   #                                                               #   set silently skips the secret
   ```
   Pitfall: `--body-file` does not exist in some gh versions (`unknown flag`); `--body "$(cat file)"`
   works for multi-line private keys. Always confirm with `gh secret list` (shows name + timestamp)
   before moving on — a bad flag exits 1 but the earlier secrets in the same batch already landed.
3. **Test the key** before wiring the workflow: `ssh -i /tmp/deploy-key ubuntu@<host> "echo OK"`.

### Next.js frontend as a container (standalone)

Next.js apps (16.x) need `output: 'standalone'` in `next.config.js` and a multi-stage Dockerfile:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL=/api/v1        # ⚠️ NEXT_PUBLIC_* is inlined at BUILD time
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN mkdir -p public && npm run build   # mkdir public — repo may have no public/ dir
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public/
USER nextjs
CMD ["node", "server.js"]
```

**⚠️ NEXT_PUBLIC_* pitfall (caught by agy review, Zera infra):** `NEXT_PUBLIC_*` variables are inlined
into the client bundle at `npm run build` time — setting them as `environment:` in compose is
USELESS for the client bundle. They must be passed as **build args**:
```yaml
frontend:
  build:
    context: ../frontend
    dockerfile: Dockerfile
    args:
      NEXT_PUBLIC_API_URL: /api/v1
```
The compose `build.context` must be the **frontend dir** (`../frontend`), not the repo root, or
`COPY package.json` fails.

Reverse proxy routing for Next standalone: `location /api/` → API backend, `location /` → frontend
(port 3000). The Next app injects its own CSP/security headers in HTML — do NOT duplicate basic
headers in nginx for `/` (duplicated headers break browsers); nginx keeps headers for `/api/*` and
docs routes only.

## Pattern: Preview per Pull Request (compose override + NPM + per-PR DB)

TaskFlow/Zera pattern for ephemeral PR previews, all build-on-host:

1. **Base compose** is the production stack; **`docker-compose.preview.yml`** is an override that
   renames containers (`<svc>-pr-${PR_NUMBER}`), points the DB at a per-PR database
   (`<app>_pr_${PR_NUMBER}`), and joins an external `proxy_network` so NPM can reach it.
2. **DB per PR:** one Postgres container serves all previews; the workflow creates the DB on demand:
   `docker exec <db> psql -d postgres -U $USER -c "CREATE DATABASE <app>_pr_${PR_NUMBER}"`
   (idempotent `2>/dev/null || echo exists`). ⚠️ **`-d postgres` é OBRIGATÓRIO** (correção
   15/08): o banco default do PG é o nome do usuário (`cfp`) que não existe →
   `FATAL: database "cfp" does not exist`. Conectar no banco de sistema `postgres` para
   criar/drop. Pass `--env-file .env.staging` to compose so `DATABASE_URL`
   interpolates real credentials — never hardcode them in the override.
3. **URL via sslip.io + NPM:** `{PR}.<app>.<host-ip>.sslip.io` → register a proxy host in NPM's
   SQLite (`register-proxy-host.py` clones the TaskFlow one), write the generated nginx conf,
   reload. HTTP only by default (D17 — no TLS on ephemeral previews): keep `CORS_ORIGINS` and
   `NEXT_PUBLIC_API_URL` as `http://`.
4. **Cleanup on PR closed:** `docker compose ... down` → `DROP DATABASE` → unregister NPM → rmi.
5. **Workflow caveats learned:**
   - **A porta externa do compose é o STAGING, não o preview.** Depois de deployar um
     preview, NÃO teste o login demo na porta 8081 do compose — essa é a stack de staging
     (banco `cfp_ia`, sem a seed do Rafael A) → `credenciais_invalidas` falso. O preview é
     alcançado pela URL sslip.io via NPM. Sempre validar o preview na URL do NPM, não no
     localhost do host.
   - `git fetch -f origin pull/N/head:pr-N` — the `-f` is REQUIRED on `synchronize` events (ref
     already exists locally), else the deploy silently runs stale code.
   - Wait for API `/health` (poll) BEFORE running the seed — migrations run async at container
     startup; the seed will fail on missing tables if it runs too early.
   - `docker exec` the seed WITHOUT overriding `DATABASE_URL` — compose already injected the
     interpolated URL into the container env.
   - Separate deploy dirs for staging vs previews to avoid branch checkout races
     (`$DEPLOY_DIR/previews/pr-N`; cleanup must `rm -rf` the dir too).
   - Copy `.env.staging` into the preview dir after checkout — a fresh clone has no
     gitignored env file, and every compose call needs `--env-file .env.staging`.

6. **Preview isolation from staging (agy turns 4–7, Zera infra):**
   - **Explicit compose project name** (`name: zera_staging` in base, `name: zera_preview_${PR_NUMBER}`
     in the override). Without it, both default to the folder name (`infra`) and `docker compose down`
     of a preview kills the staging stack.
   - **`--no-deps` no `up`, NÃO `depends_on: []`** (correção 15/08 — o `depends_on: []`
     no override é IGNORADO no merge do compose: o api ainda herda `db/redis` do base e o
     preview tenta criar `zera-db`/`zera-redis` → `Conflict. The container name "/zera-db"
     is already in use`. O fix real: `docker compose ... up -d --no-deps api agente bot
     frontend` — o staging já roda db/redis, o preview só cria o banco próprio via psql).
   - **DNS via `container_name`, not service alias:** in a shared external network the alias
     `db`/`api` is ambiguous (staging + every preview). Point preview services at the staging
     containers' names: `DATABASE_URL=...@zera-db:5432/...`, `RATE_LIMIT_REDIS_URL=redis://zera-redis:6379/0`,
     agente/bot `API_BASE_URL`/`ZERA_API_URL=http://zera-api-pr-${PR_NUMBER}:8100`.
   - **Shared networks external:** `zera_net: {external: true}` + `proxy_network: {external: true}`
     in the preview override — compose must not try to recreate/delete the staging network on `down`.
   - **`DROP DATABASE ... WITH (FORCE)`** (PG 16) in cleanup — kills residual pooled connections.
   - **`always()` in the deploy job's `if:`** — `if: always() && (needs.ci.result == 'success' ||
     (github.event_name == 'workflow_dispatch' && inputs.force))`; a plain `needs.ci.result` check
     cancels the deploy when the CI job is skipped by `force=true`.
   - **New-repo checkout — três bugs reais (correções 15/08):**
     a) NÃO use `git rev-parse --git-dir` para testar se o dir é repo: ele SOBE ao repo pai
        (`/home/ubuntu/cfp-ia/.git`) e o checkout roda no diretório errado, deixando
        `previews/pr-N` vazio. Use `[ -d .git ]` (repo local).
     b) `git fetch -f origin pull/N/head:pr-N` cria a branch local `pr-N`; em seguida
        `git checkout -f -b pr-N FETCH_HEAD` falha `fatal: A branch named 'pr-N' already
        exists`. Use `checkout -f -B pr-N origin/pr-N` nos DOIS ramos.
     c) `git fetch ... :pr-N` direto recusa `refusing to fetch into branch 'refs/heads/pr-N'
        checked out` quando a branch está ativa (synchronize). Fetch para ref REMOTA:
        `git fetch -f origin +refs/pull/N/head:refs/remotes/origin/pr-N` e depois
        `git checkout -f -B pr-N origin/pr-N`. Padrão que funciona em repo novo e existente:
        ```bash
        if [ -d .git ]; then
          git fetch -f origin +refs/pull/N/head:refs/remotes/origin/pr-N && git checkout -f -B pr-N origin/pr-N
        else
          git init && git remote add origin git@github.com:<repo>.git \
            && git fetch -f origin +refs/pull/N/head:refs/remotes/origin/pr-N && git checkout -f -B pr-N origin/pr-N
        fi
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
ssh oracle-host 'python3 << '\\''PYEOF'\\''
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

**⚠️ CRÍTICO (correção 15/08/2026): `docker restart` NÃO regenera o `.conf` para
hosts inseridos via banco direto.** O NPM só gera `proxy_host/{ID}.conf` quando o host é
salvo pela UI/API. Após o insert no banco, você DEVE escrever o `.conf` manualmente e
recarregar — senão o domínio responde 404 (config ausente) mesmo com o host `enabled=1`:

```bash
# 1. Gerar /tmp/proxy-{ID}.conf (template completo: server{listen 80; server_name DOMAIN;
#    location / { include conf.d/include/proxy.conf; } } — ver scripts/register-preview.sh do
#    TaskFlow para o shape exato, com locations /api/, /health, /auth/ por serviço)
docker cp /tmp/proxy-{ID}.conf nginx_proxy_manager:/data/nginx/proxy_host/{ID}.conf
docker exec nginx_proxy_manager nginx -t          # syntax ok
docker exec nginx_proxy_manager nginx -s reload    # NÃO restart — reload basta
```

3. **Conectar o container à `proxy_network`** (uma vez, se ainda não estiver):
```bash
docker network connect proxy_network <container-name>
docker exec nginx_proxy_manager sh -c "getent hosts <container-name>"   # deve resolver
```

**Sintoma típico:** proxy host `enabled=1` no banco, root responde 200, mas um path
(`/health`) devolve `404 Not Found` HTML do nginx — enquanto o mesmo path direto no
container retorna 200. Checar se o `.conf` do host existe em `/data/nginx/proxy_host/`.

### Step 3: SSL Certificate

The user handles SSL via NPM UI (port 81) since it needs authentication:
- Access `https://<host-ip>:81` (via SSH tunnel since port 81 is blocked by Oracle firewall)
- Add Let's Encrypt certificate for the domain
- Edit the proxy host → SSL tab → select certificate → Force SSL

**⚠️ Never reset NPM passwords without explicit user permission.**

## Pitfalls

### Never `git reset --hard` on the host repo

**User blocked this twice (14/08/2026).** The host repo is the single source of truth (shared
volume). `git reset --hard origin/main` can destroy uncommitted work (e.g. files another agent
wrote) and is unnecessary — use `git pull --ff-only origin main`. For PR previews:
`git fetch -f origin pull/N/head:pr-N && git checkout pr-N`.

When the agy reviewer suggests `git reset --hard` to guard against local modifications in the
deploy sync, **reject it** and use the safe equivalent:
```bash
git checkout -- . && git fetch origin main && git checkout main && git pull --ff-only origin main
```
(`git checkout -- .` discards tracked-file modifications without touching untracked files like
`.env.staging` — same protection, zero destruction.)

### Docker compose: build context vs dockerfile path

`build.context` is the directory the Dockerfile's relative `COPY`s resolve against. For a repo with
services in subdirs: `context: ../frontend` + `dockerfile: Dockerfile` (not `context: ..` +
`dockerfile: frontend/Dockerfile`) unless the Dockerfile is written for the repo root.

### Seed scripts: SQLite/Postgres portability

When a seed script must run against BOTH SQLite (dev/test) and Postgres (preview/prod), raw
`text()` inserts hit dialect differences. See `references/seed-script-portability.md`.

### QA de preview alfa (dogfood completo)

Para o checklist concreto de um dogfood de preview por PR (o que testar, bugs de classe
cookie-Secure/header-ASCII/requirements faltante, técnicas de token e rate limit):
`references/dogfood-zera-alfa-2026-08-15.md`.

### Auth cookie `Secure` flag breaks login on HTTP previews/staging (15/08)

**Symptom:** login via browser "does nothing" — the button disables forever, the page never
navigates, no visible error. Direct API login via curl returns 200 with tokens. Console is clean.

**Root cause:** the app sets the refresh cookie with `Secure` (FastAPI `set_cookie(secure=True)`,
default in `api/config.py`). Browsers REFUSE to store `Secure` cookies on plain HTTP (no TLS).
The frontend calls `/auth/login`, gets 200, saves the access token in memory, then
`router.replace('/dashboard')` — but the middleware re-checks the httpOnly refresh cookie,
doesn't find it, and bounces back to `/login?next=%2Fdashboard`. The submit button never gets
re-enabled because the success path skips `setSubmitting(false)` before navigating.

**Diagnosis checklist:**
1. `fetch('/api/v1/auth/login', {method:'POST', ...})` from the browser console → 200 with tokens
   (API is fine).
2. `document.cookie` → empty (httpOnly cookies are invisible to JS — expected), but the
   middleware still can't see the cookie → check `Set-Cookie` headers: `secure` flag present?
3. Nav to `/dashboard` directly → bounced to `/login?next=%2Fdashboard` (middleware, no session).

**Fix:** set `AUTH_COOKIE_SECURE=false` in the staging/preview env while there is no TLS
(D17 — HTTP interno/sslip.io). Document it in `.env.staging.example` with the note "produção
HTTPS = True". The backend setting is usually a pydantic-settings bool (`auth_cookie_secure`),
so the env var name is the field name uppercased.

**Broader lesson:** API 200 ≠ browser session works. Any auth flow that sets an httpOnly cookie
must be tested IN A BROWSER on the actual external URL (NPM/sslip.io), not just via curl — curl
never validates cookie flags against the transport scheme.

### Healthcheck frequency vs CPU spikes (15/08)

**Symptom:** host CPU at ~60% with NOBODY using the app; `docker stats` shows individual Zera
containers oscillating 0% → 27% → 0% in ~10s cycles. The API uvicorn had accumulated only ~47s
CPU over 7h (avg ~0.2%), so the app was idle — the spikes were **healthcheck executions**.

**Root cause:** every `CMD python -c "...urlopen..."` / `CMD node -e "fetch(...)"` healthcheck
**spawns a brand-new interpreter process** (docker exec → python/node startup + import). With
`interval: 10s` across 8 containers (api/agente/bot/frontend × staging+preview) = ~48
process-spawns/minute, each coinciding with the docker-stats sample window shows up as a 26%+ CPU
peak. Healthcheck interval must match the environment's real need.

**Fix:** `interval: 30s` for app-level HTTP healthchecks in staging/preview (`sed -i
's/interval: 10s/interval: 30s/g' docker-compose.staging.yml`); keep 5s only for infra
(redis-cli ping, pg_isready — those are ~1ms native binaries, not interpreter spawns). After
changing compose healthcheck, containers must be recreated (`docker compose up -d` recreates
when config changed). Verify with repeated `docker stats --no-stream` samples — the CPU should
drop from ~57% total to <3%.

**Ainda mais leve (15/08): troque o comando do healthcheck por `bash -c /dev/tcp`.**
O custo de `python -c "...urlopen..."` / `node -e "fetch(...)"` é quase TODO o spawn do
interpretador (medido: `docker exec python -S -c pass` ≈ 0.122s vs urlopen ≈ 0.130s — o Python
mal aparece). `/dev/tcp` é builtin do bash: **0.016s, ~8x mais leve**, e ainda valida HTTP de
verdade:
```yaml
test: ["CMD", "bash", "-c", "exec 3<>/dev/tcp/127.0.0.1/8100; printf 'GET /health HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n' >&3; head -1 <&3 | grep -q '200 OK'"]
```
**⚠️ Pegadinha alpine:** imagens `node:*-alpine` / `python:*-alpine` **não têm bash** (`bash:
executable file not found`) — use o `wget` do busybox (presente, ~leve) no lugar:
```yaml
test: ["CMD", "wget", "-q", "-O", "/dev/null", "http://127.0.0.1:3000/"]
```
Sempre confirme qual shell/binário a imagem tem antes: `docker exec <svc> sh -c "which bash wget"`.

**Debug workflow for "containers eating CPU with no users":**
1. `docker stats --no-stream` sorted by CPU → identify the offenders.
2. `docker top <svc>` → process TIME accumulated: low TIME over hours = idle process (the CPU
   is external to it, e.g. healthcheck spawns or another container's polling).
3. Sample repeatedly (`for i in $(seq 1 10); do docker stats ...; sleep 2; done`) — a periodic
   ~10s spike aligns with `Interval: 10s`.
4. Also `ps aux | grep` for leftover long-running watchers (pi_follow_tui.mjs, --replay, etc.)
   that accumulate across sessions — kill via `sudo pkill -9 -f "<pattern>"` when they're no
   longer needed (they run as root in another namespace; plain `pkill` gets EPERM).

### NEVER overwrite a live `.env` with the example — recovery from running containers (15/08)

**Mistake that happened:** validating a compose with
`cp .env.staging.example .env.staging` **silently destroyed the real env** (generated secrets:
POSTGRES_PASSWORD, JWT_SECRET, channel tokens, DATABASE_URL, etc.) because the example has empty
placeholders. The containers kept running (env loaded at create time), but any recreate/deploy
would have come up with empty credentials → auth fails, DB refuses connections.

**Recovery (works as long as the containers are still running):** extract the original env from
`docker inspect` and rebuild the file:
```bash
get_env() { docker inspect "$1" --format "{{range .Config.Env}}{{println .}}{{end}}" 2>/dev/null \
  | grep "^$2=" | cut -d= -f2- | head -1 || true; }
PG_PASS="$(get_env <db-container> POSTGRES_PASSWORD)"      # e.g. zera-db
JWT="$(get_env <api-container> JWT_SECRET)"                 # e.g. zera_staging-api-1
OR="$(get_env <api-container> OPENROUTER_API_KEY)"
TG="$(get_env <bot-container> TELEGRAM_BOT_TOKEN)"
TOKENS="$(get_env <api-container> CHANNEL_TOKENS)"          # per-channel tokens (D14)
# DATABASE_URL must mirror POSTGRES_PASSWORD (the env validator checks this):
NEW_URL="postgresql+asyncpg://${PG_USER}:${PG_PASS}@db:5432/${PG_DB}"
```
Then `sed -i "s|^VAR=.*|VAR=${value}|" .env.staging` for each recovered var and run the
project's `validar_env_staging.sh` until "0 avisos". Note: `DATABASE_URL` espelhamento da senha
é checado pelo validador — rebuild it explicitly.

**Prevention (user preference — see also "Secrets nuance"):**
- NEVER `cp .env.example .env` on a live host — validate with a throwaway copy in `/tmp` and
  `--env-file /tmp/validate.env` instead.
- Back up the real `.env` before touching it: `cp .env.staging .env.staging.bak`.
- The compose `env_file:` paths resolve relative to the compose dir, so a temp env file must be
  copied INTO the dir (e.g. `infra/.env.staging`) to satisfy `config --quiet` — do that with a
  `cp ... && validate && rm` one-liner that never leaves the placeholder file in place.

### "Otimizar" ≠ "derrubar" — never tear down a preview the user is actively using (15/08)

**User correction (explicit):** told to "encerre as instâncias de Pi follow" while investigating
60% CPU, I tore down the PR preview too (compose down + NPM unregister + DROP DATABASE + rm -rf).
User reply: *"Não é para derrubar o preview. Eu estou usando para testes. É para otimizar."*

**Rule:** scope destructive actions to EXACTLY what was named. "Encerre as instâncias de X" =
kill process group X only. When the goal is resource optimization, prefer non-destructive fixes
(healthcheck interval, killing watcher processes) over stopping stacks; if a stack teardown is
truly needed, ASK first. If you already tore something down by mistake, recreate it immediately
via the same workflow that created it (push an empty commit to the PR branch re-triggers the
preview deploy: `git commit --allow-empty -m "re-deploy" && git push`), then re-verify health.

### HTTP client headers must be ASCII-only (httpx breaks on non-ASCII) (15/08)

**Symptom:** the LLM/agent client silently fails before reaching the provider — the app returns
a graceful fallback ("dificuldade técnica") and the log shows:
`LLM falhou ('ascii' codec can't encode character '\u2014' in position 7: ordinal not in range(128))`.

**Root cause:** an HTTP header value contained a non-ASCII char (e.g. `X-Title: "CFP IA — Núcleo
Agêntico"` with em-dash U+2014). httpx serializes headers as ASCII per HTTP spec; the encode
error throws BEFORE the request leaves, so the LLM was never called and the app fell back.

**Fix:** keep every header value ASCII-only — strip accented chars/em-dashes from custom headers
(`X-Title: "CFP IA Nucleo Agentico"`). Also a good habit: log the raw exception, not just the
fallback, so the real cause isn't hidden behind the graceful message.

**Broader lesson:** graceful degradation can mask the true error. When a service "works" but
returns a canned fallback, grep the backend logs for the real exception (here: a 1-line
`ModuleNotFoundError: No module named 'mcp'` earlier in the same flow — a dependency declared in
`agente/requirements.txt` but missing from `api/requirements.txt`; a service image must install
every requirements file its imported packages depend on, not just the service's own).

### First deploy on the host — real bugs found (Zera alfa 14/08)

The CI passed but the stack failed in production-like staging. These four bit us in order;
check them before anything else on a first `docker compose up -d --build`:

1. **Service Dockerfile missing a package the router imports.** The API's `chat.py` imports
   `agente.api_client`, but `api/Dockerfile` only copied `api/ src/ migrations/`. Result:
   `ModuleNotFoundError: No module named 'agente'` → container crashes → compose healthcheck
   fails (`dependency api failed to start: container is unhealthy`). Fix: the service image
   must `COPY` **every top-level package its imports chain touches** — grep `import <pkg>` in
   the service's routers before writing the Dockerfile.

2. **Reverse proxy missing health-endpoint locations.** The deploy smoke script tests
   `GET /health` (and `/health/ready`) on the EXTERNAL port, but nginx only had
   `location /api/` (→ backend) and `location /` (→ frontend), so `/health` returned 404 from
   Next. Fix: add exact-match locations for root-level health endpoints:
   ```nginx
   location = /health { proxy_pass http://cfpia_api; ... }
   location = /health/ready { proxy_pass http://cfpia_api; ... }
   ```
   Any smoke route must have a matching nginx location — the smoke runs through the proxy,
   not at the container.

3. **Host's system nginx (systemd) holding the port.** `address already in use` on 8081 was a
   **host nginx**, not a container: `sudo ss -tlnp | grep ":8081 "` showed `users:(("nginx",...))`
   and `systemctl status nginx` was active since weeks — serving a legacy orphan site whose
   upstream no longer exists (TaskFlow moved to containers). Fix after confirming nothing live
   depends on it: `sudo systemctl stop nginx && sudo systemctl disable nginx`. Always check
   `systemctl` when a port is taken by an unlabeled process — it may be an orphaned system service.

4. **Orphan container with NO networks after a failed partial deploy.** After `down` + `up`,
   the nginx container was `Up` but `docker inspect <svc> --format '{{json .NetworkSettings.Networks}}'`
   showed `{}` → nginx couldn't resolve `api:8100` (`host not found in upstream`, crash loop).
   Cause: the container was created during the attempt that failed on the port bind, and
   `up -d` didn't recreate it. Fix: `docker compose up -d --force-recreate <svc>`.

5. **CI lint gate catches NEW scripts too.** The deploy's first gate is `ruff check` on the
   whole repo; a freshly-written seed script failed it (F401 unused imports, E731 `lambda`
   assigned to a name). Run `ruff check` locally on any new `scripts/*.py` before pushing,
   or the deploy workflow dies at the gate with exit 1 before reaching the host. Convert
   assigned lambdas to `def`, drop unused imports.

### Port already allocated

Symptom: `Bind for 0.0.0.0:<port> failed: port is already allocated`

Fix: Check `ss -tlnp` on the host and pick a free port. This host has services on 80, 443, 3002, 5173, 5432, 6379, 8000, 8080, 8081, 8090, 8100, 8642, 8882, 9119.

### Custom ports are NOT reachable from outside (Oracle firewall)

**The host firewall (iptables) only opens 80/443/22/2222** (plus a few service-specific
ports like 9119/8642). A compose stack exposed on a custom port (e.g. `8081`) answers
`curl localhost:8081` = 200 on the host but **times out from the internet** — verified
15/08/2026 on the Zera staging. Do NOT rely on opening custom ports; the established
pattern is: **everything external goes through NPM (80/443)** — register a proxy host
(domain or `*.sslip.io`) → internal nginx/container port, exactly like TaskFlow
(`praxis.gotdns.ch` → `taskflow-nginx:80`) and Moodle (`treinamentos...` → `moodle-nginx:80`).

Quick check that a custom port is NOT firewalled-open:
```bash
ssh oracle-host 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health'
# 200 local, mas de fora (mesmo host via IP público) timeout → firewall bloqueia
```

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

**Secrets nuance (14/08/2026):** when filling secret values (API keys, bot tokens) into a host
`.env`, do NOT pipe the secret through redirection/`$(cat ...)` chains that echo it around — the
user blocked a command that extracted an OpenRouter key to `/tmp` mid-pipeline. Clean pattern:
1. write a small local script with `write_file` (or fetch the value into a local file with a
   dedicated script), 2. `scp` it, 3. run it on the host so the secret is only touched by the
   host's own shell. Better: ask the user to paste values they hold (bot tokens from BotFather,
   etc.) directly rather than deriving them from other stores. Always `rm -f` temp copies of
   private keys/tokens after use (local AND host).

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
