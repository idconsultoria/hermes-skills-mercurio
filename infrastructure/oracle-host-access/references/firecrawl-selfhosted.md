# Firecrawl Self-Hosted — Config & Diagnostics

## Service Info

| Property | Value |
|----------|-------|
| Hostname (ai_mesh) | `firecrawl_api` |
| Port | 3002 |
| Image | `ghcr.io/firecrawl/firecrawl:latest` |
| Network | `ai_mesh` (external) |
| Uptime (last check) | 3+ weeks |
| Health endpoint | NONE — test via `GET /` or `POST /v1/scrape` |

## Containers

```
firecrawl_api          ghcr.io/firecrawl/firecrawl:latest   3002/tcp, 8080/tcp
firecrawl_worker       ghcr.io/firecrawl/firecrawl:latest   8080/tcp
firecrawl_postgres     postgres:17-alpine                   5432/tcp
firecrawl_rabbitmq     rabbitmq:3-management-alpine         4369/tcp, 5671-5672/tcp, ...
firecrawl_redis        redis:alpine                         6379/tcp
firecrawl_playwright   ghcr.io/firecrawl/playwright-service:latest
```

## Quick Tests

```bash
# Root health (only connectivity check available)
curl -s http://firecrawl_api:3002/
# → {"message":"Firecrawl API","documentation_url":"https://docs.firecrawl.dev"}

# Scrape test
curl -s http://firecrawl_api:3002/v1/scrape -X POST \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
# → {"success":true,"data":{"markdown":"Example Domain\n..."}}

# Search test (WILL be empty — no search engine configured)
curl -s http://firecrawl_api:3002/v1/search -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":1}'
# → {"success":true,"data":[]} — self-hosted needs Google/Bing API key
```

## Hermes Integration

### Env vars (in `/opt/data/.env`)
```
FIRECRAWL_API_URL=http://firecrawl_api:3002
FIRECRAWL_API_KEY=local
```

### SDK install (venv is root-owned, use --target)
```bash
mkdir -p /opt/data/home/.local/lib/python3.13/site-packages
uv pip install --target /opt/data/home/.local/lib/python3.13/site-packages 'firecrawl-py==4.17.0'
echo 'PYTHONPATH=/opt/data/home/.local/lib/python3.13/site-packages:$PYTHONPATH' >> /opt/data/.env
```

### SDK usage test
```bash
export FIRECRAWL_API_URL=http://firecrawl_api:3002
export FIRECRAWL_API_KEY=local
python3 -c "
from firecrawl import Firecrawl
c = Firecrawl(api_url='$FIRECRAWL_API_URL', api_key='$FIRECRAWL_API_KEY')
r = c.scrape(url='https://example.com')
print('scrape OK:', r.metadata.title if r.metadata else '?')
s = c.search(query='test', limit=1)
print('search results:', len(s.data) if s.data else 0)
"
```

## Search Engine Architecture

Firecrawl's internal search (`apps/api/src/search/index.ts`) uses this priority chain:

```
1. FIRE_ENGINE_BETA_URL set?  →  Fire Engine (closed beta, not available)
2. SEARXNG_ENDPOINT set?      →  SearXNG (self-hosted, open source)
3. Neither?                   →  DuckDuckGo (scrape HTML — default fallback)
```

**DuckDuckGo fallback** (`apps/api/src/search/v2/ddgsearch.ts`): Scrapes DuckDuckGo HTML search results with rotating User-Agents. Has anti-bot detection with 3 retries. Can be silently blocked by DDG, returning empty results. This is why `web_search` returns nothing despite no explicit config issue.

**SearXNG** (`apps/api/src/search/searxng.ts`): Self-hosted metasearch engine. Requires `SEARXNG_ENDPOINT`. Supports `SEARXNG_ENGINES` (comma-separated, e.g. "google,bing") and `SEARXNG_CATEGORIES`. Queries via JSON format.

**SearchApi** (searchapi.com): Listed in `.env.example` as `SEARCHAPI_API_KEY`/`SEARCHAPI_ENGINE` — this is used by the **public API endpoint** (`/v1/search`), NOT the internal search used by scrape/extract. Gives 100 free searches/month, then $40/mo.

**Firecrawl does NOT directly support Google Custom Search or Bing API.** Those are accessed through SearchApi.

## Search Engine Options Comparison

| Approach | Cost | Config Effort | Reliability | Notes |
|----------|------|---------------|-------------|-------|
| DuckDuckGo (fallback) | Free | Zero | Low (anti-bot) | Fallback padrão, scraping HTML frágil |
| SearXNG (self-hosted) 🟢 | Free | 1 compose + 1 env var | High (proven) | Já implantado. Agrega Google, Bing, DDG via `ai_mesh`. Container `searxng-core` porta 8080. |
| SearchApi | 100/mo free, $40+ | 1 env var | High | Wrapper p/ Google, Bing, Baidu etc. |

### To enable SearXNG — Deployed & Proven

SearXNG should run as a **separate compose file** (not embedded in Firecrawl's), on the shared `ai_mesh` network. It needs a Valkey (Redis-compatible) cache alongside it.

#### docker-compose.yml (`/home/ubuntu/selfhost/searxng/docker-compose.yml`)

```yaml
services:
  core:
    container_name: searxng-core
    image: docker.io/searxng/searxng:latest
    restart: unless-stopped
    networks:
      - ai_mesh
    expose:
      - "8080"
    environment:
      SEARXNG_BIND_ADDRESS: "0.0.0.0"
      SEARXNG_PORT: 8080
      SEARXNG_SECRET: "<random-24-char-min>"
      SEARXNG_LIMITER: "false"
      SEARXNG_IMAGE_PROXY: "true"
    volumes:
      - ./core-config:/etc/searxng:Z
      - core-data:/var/cache/searxng/

  valkey:
    container_name: searxng-valkey
    image: docker.io/valkey/valkey:9-alpine
    command: valkey-server --save 30 1 --loglevel warning
    restart: unless-stopped
    networks:
      - ai_mesh
    volumes:
      - valkey-data:/data/

volumes:
  core-data:
  valkey-data:

networks:
  ai_mesh:
    external: true
```

#### settings.yml (`core-config/settings.yml`)

**Critical:** use `use_default_settings: true` to deep-merge with built-in defaults. Without this, SearXNG uses ONLY your minimal file and crashes (e.g. `KeyError: 'default_doi_resolver'`).

```yaml
use_default_settings: true

general:
  instance_name: "SearXNG (Firecrawl)"
  enable_metrics: false

search:
  formats:
    - html
    - json

server:
  bind_address: "0.0.0.0"
  port: 8080
  limiter: false
  image_proxy: true

outgoing:
  request_timeout: 10.0
  max_request_timeout: 15.0
  enable_http2: true
```

#### Connect to Firecrawl

Add to Firecrawl API's environment in its docker-compose:

```yaml
SEARXNG_ENDPOINT: http://searxng-core:8080
```

No `SEARXNG_ENGINES` needed — SearXNG's default engine list already includes Google, Bing, DuckDuckGo, etc. Firecrawl's search code (`apps/api/src/search/searxng.ts`) passes `format=json` and respects the engine list if provided.

After adding, recreate Firecrawl API:
```bash
cd /home/ubuntu/selfhost/firecrawl && docker compose up -d --force-recreate api
```

Verify connectivity:
```bash
# From any container on ai_mesh:
curl "http://searxng-core:8080/search?q=test&format=json"

# Firecrawl logs should confirm SearXNG is active:
docker logs firecrawl_api 2>&1 | grep "Using searxng"
# → "Using searxng search"

# Firecrawl search API returns real results:
curl -s -X POST http://firecrawl_api:3002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":3}'
# → success:true with populated data[]
```

#### SearXNG Config Pitfalls

- **`use_default_settings: true` is mandatory** for a minimal overrides file. Without it, SearXNG uses ONLY your settings.yml and crashes on missing keys (`default_doi_resolver`, `brand.*`, all 180+ engines, etc.).
- **File ownership:** The entrypoint expects `/etc/searxng/` owned by `searxng:searxng` (UID 10000 inside container). On the host use `sudo chown 10000:10000`.
- **No host port needed:** Only expose internally on `ai_mesh` (`expose:` not `ports:`). Firecrawl resolves via Docker DNS.
- **Env vars vs settings.yml:** Most config works via `SEARXNG_*` env vars, but `search.formats` (to add `json`) can ONLY be set in settings.yml — always mount one with `use_default_settings: true`.
- **502 from nginx:** If you test via localhost, Nginx Proxy Manager on port 8080 intercepts. Always test via Docker DNS (`searxng-core:8080`) from another ai_mesh container.

### To enable SearchApi

```yaml
SEARCHAPI_API_KEY: "your-key-here"
SEARCHAPI_ENGINE: "google"  # or bing, baidu, google_news, etc.
```

## Env Var Override

The Docker image sets `ENV HERMES_DISABLE_LAZY_INSTALLS=1`, which **overrides** `config.yaml`'s `security.allow_lazy_installs: true`. The `_allow_lazy_installs()` function in `tools/lazy_deps.py` checks the env var before reading config. So `ensure("search.firecrawl", prompt=False)` fails even when the config file allows lazy installs. Workaround: install firecrawl-py manually via `--target`.

## Why web_search Stopped Working After Container Update

Firecrawl's Python SDK (`firecrawl-py`) is part of the `[firecrawl]` extra in `pyproject.toml`, not the base `dependencies`:

```toml
# pyproject.toml (line 147)
firecrawl = ["firecrawl-py==4.17.0"]
```

Until **2026-05-12**, `firecrawl` was in `[all]` — so `uv sync --extra all` (used in the Dockerfile) installed it in the venv at build time. On 2026-05-12 it was moved to lazy-install only (policy: `[all]` should only contain packages that CAN'T be lazy-installed):

```toml
# Removed from [all] on 2026-05-12 (covered by lazy-install):
#   anthropic, exa, firecrawl, parallel-web, fal, edge-tts, ...
```

But the Dockerfile also sets:

```dockerfile
ENV HERMES_DISABLE_LAZY_INSTALLS=1
```

This env var is checked FIRST by `_allow_lazy_installs()` in `tools/lazy_deps.py` (line 244), **before** reading `config.yaml`'s `security.allow_lazy_installs`. So even if `config.yaml` says `true`, lazy installs are blocked.

**Result:** When the container is rebuilt with a newer image, firecrawl-py is wiped from the venv. The lazy install path can't reinstall it (env var blocks). `web_search` and `web_extract` fail with:

```
Feature 'search.firecrawl' unavailable: lazy installs disabled (security.allow_lazy_installs=false)
```

### Fix Flow (Works Across Rebuilds)

The fix survives `docker compose pull + up -d` because `/opt/data/` is a **bind mount** — preserved across container rebuilds.

```bash
# 1. Install firecrawl-py in user site-packages (persistent)
mkdir -p /opt/data/home/.local/lib/python3.13/site-packages
uv pip install --target /opt/data/home/.local/lib/python3.13/site-packages 'firecrawl-py==4.17.0'

# 2. Add PYTHONPATH so Hermes finds it
grep -q 'PYTHONPATH=' /opt/data/.env || \
  echo 'PYTHONPATH=/opt/data/home/.local/lib/python3.13/site-packages:$PYTHONPATH' >> /opt/data/.env

# 3. Restart Hermes to pick up env vars
ssh oracle-host 'docker restart hermes_agent'
```

After restart, `ensure("search.firecrawl")` finds the package already installed and never hits the lazy-install gate. `HERMES_DISABLE_LAZY_INSTALLS=1` stays active for everything else — no conflict.

### Other Packages Affected by This Pattern

Any lazy-installed backend that was removed from `[all]` on 2026-05-12 has the same vulnerability: `exa`, `parallel-web`, `fal`, `edge-tts`, `modal`, `daytona`, `telegram`, `discord`, `slack`, `matrix`, `honcho`, `faster-whisper`, `elevenlabs`, `dingtalk`, `feishu`, `bedrock`. If they fail after a container update, apply the same `--target` fix.

## Known Limitations

- **Search requires configuration**: DuckDuckGo fallback is unreliable (anti-bot blocks). You must configure SearXNG or SearchApi for reliable search.
- **No health endpoint**: The API responds on `GET /` but there's no `/health`, `/isAlive`, or `/ready`. Test by scraping a known URL.
- **Port 8080 is internal**: Inside the container port 8080 serves the API too, but from the ai_mesh network only port 3002 is reachable. Using 8080 from Hermes gives "Connection refused".
