# SPA on Vercel + Backend on Remote Host (Oracle / VPS)

Pattern for deploying a frontend SPA to Vercel while the backend API runs on a remote host (e.g., Oracle Cloud VM, dedicated server).

## Architecture

```
User Browser → Vercel CDN (SPA) → API calls → Remote Host (Backend)
                                                          ↕
                                                     Docker/PostgreSQL
```

CORS is required since the frontend origin (vercel.app) differs from the backend origin (remote host IP).

## Required Changes

### 1. Frontend: `config.js` with API_BASE

Create `frontend/js/config.js`:

```js
const API_BASE = 'http://<PUBLIC_IP>:<PORT>/api/v1';
```

Include it **before** all other JS in `index.html`:

```html
<script src="js/config.js"></script>
<script src="js/api.js"></script>
<script src="js/auth.js"></script>
<script src="js/app.js"></script>
```

### 2. Frontend: `api.js` — relative → absolute URL

Change `API_PREFIX` to use the external `API_BASE`:

```js
// Before: const API_PREFIX = '/api/v1';
// After: API_BASE is defined in config.js, imported globally

const url = `${API_BASE}${path}`;
```

Change `credentials` mode:

```js
// Before: credentials: 'same-origin'
// After:  credentials: 'include'
```

### 3. Frontend: `auth.js` — absolute login URL

The login endpoint is hardcoded in many Pi-generated SPAs:

```js
// Before: const response = await fetch('/api/v1/auth/login', ...)
// After:  const response = await fetch(`${API_BASE}/auth/login`, ...)
```

### 4. Backend: CORS configuration

Add the Vercel domain to the backend's CORS origins list:

```python
CORS_ORIGINS: list[str] = [
    # ... local origins ...
    "https://<project>.vercel.app",
    # Optional: allow public IP for testing
    "http://<PUBLIC_IP>:<PORT>",
]
```

> **Important:** The actual Vercel auto-generated subdomain often contains a random suffix (e.g., `delfos-mvp-orpin.vercel.app`), not just `<project>.vercel.app`. Check the deploy output's `Production` URL and add that exact origin. Rebuild and restart the backend after changing CORS origins.

> `allow_credentials=True` + `allow_origins=["*"]` is invalid. Use explicit origins.

### 5. Vercel: SPA fallback routing

`vercel.json` in project root:

```json
{
  "version": 2,
  "buildCommand": null,
  "outputDirectory": ".",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### 6. Deploy (prebuilt flow)

```bash
cd /path/to/project
vercel build --prod --yes          # generates .vercel/output/
vercel deploy --prebuilt --prod --yes  # skip server-side build
```

## Mixed Content Problem (HTTPS Frontend → HTTP Backend)

**Problem:** Vercel serves the SPA over HTTPS. If the backend API is on `http://<public-ip>:<port>`, modern browsers block the mixed-content request. The API calls silently fail.

### Solution A: Proxy through an existing HTTPS domain

If there's already an HTTPS domain on your backend host (e.g., `praxis.gotdns.ch` with Let's Encrypt via Nginx Proxy Manager), add the API as a sub-path:

1. **NPM custom config** — add a `location /api-proxy/` block that forwards to the backend nginx.

   **The directory must exist first:**

   ```bash
   docker exec nginx_proxy_manager mkdir -p /data/nginx/custom
   ```

   Write the config using base64 encoding to avoid shell-escaping `$` variables:

   ```bash
   CONFIG_B64="$(printf '%s' 'location /delfos/ {
       proxy_pass http://backend-nginx:80/;
       proxy_http_version 1.1;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }' | base64 -w0)"
   echo "$CONFIG_B64" | base64 -d | docker exec -i nginx_proxy_manager sh -c 'cat > /data/nginx/custom/server_proxy.conf'
   ```

   **Verify** the file content — shell may expand `$host` etc. to empty strings:

   ```bash
   docker exec nginx_proxy_manager cat /data/nginx/custom/server_proxy.conf
   # Confirm proxy_set_header Host $host (not blank)
   ```

2. **Docker network connectivity** — if the proxy container can't resolve the backend nginx hostname (different Docker networks), connect it:

   ```bash
   docker network connect <backend_network> <proxy_container>
   docker restart nginx_proxy_manager
   ```

3. **Backend nginx path rewrite** — strip the prefix so the backend sees clean paths:

   ```nginx
   location /delfos/ {
       rewrite ^/delfos(/.*)$ $1 break;
       proxy_pass http://backend:8000;
   }
   ```

4. **Update frontend config.js** — point to the HTTPS URL:

   ```js
   const API_BASE = "https://existing-domain.com/delfos/api/v1";
   ```

### Solution B: Direct API URL (HTTP, with browser warning)

If you accept mixed-content warnings during development, the frontend must explicitly allow it. No config change in the SPA — the browser console shows the blocked requests. User must click "Load unsafe scripts" or disable mixed-content blocking in browser settings.

**This is not a production solution.**

### Solution C: Self-signed cert on the backend host

Use a self-signed certificate for the backend nginx. Browsers will show a warning but will still allow the connection after the user accepts the risk.

---

## Pitfalls

### CSP with multi-line value causes 502 from openresty (Nginx Proxy Manager)

**Symptom:** Proxied requests return 502 (`502 Bad Gateway` from openresty). The nginx error log shows:
```
upstream sent invalid header: "\x20..." while reading response header from upstream
```

**Root cause:** The backend nginx sends a `Content-Security-Policy` header with a multi-line value (folded header). Nginx Proxy Manager / openresty does not accept folded headers and rejects the upstream response as invalid.

**Fix:** Make the CSP header a single line:

```nginx
# Broken - multi-line (triggers 502)
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self';
" always;

# Fixed - single-line
add_header Content-Security-Policy "default-src 'self'; script-src 'self';" always;
```

After fixing, reload nginx: `nginx -s reload` or restart the container.

### API QA via Hermes doesn't reach Docker containers on the host

For API testing from Hermes, use SSH or the Docker gateway IP:

```bash
ssh oracle-host 'curl -s http://localhost:<PORT>/api/v1/health'
curl -s http://172.19.0.1:<PORT>/api/v1/health
```

### CORS preflight (OPTIONS) may fail

If the backend doesn't handle OPTIONS requests, browsers will block the real request. Verify:

```bash
ssh oracle-host "curl -s -X OPTIONS -H 'Origin: https://<project>.vercel.app' -H 'Access-Control-Request-Method: POST' http://localhost:8090/api/v1/auth/login"
```

Expected: 200 with `access-control-allow-origin` header matching the Vercel domain.

### Vercel SSO Protection blocks public access

Disable via API:

```bash
curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ssoProtection": null}'
```

## Verification

```bash
# Frontend
curl -s -o /dev/null -w "%{http_code}" https://<project>.vercel.app/

# Backend health
ssh oracle-host 'curl -s http://localhost:<PORT>/api/v1/health'

# CORS works from Vercel domain
ssh oracle-host "curl -s -X OPTIONS -H 'Origin: https://<project>.vercel.app' -H 'Access-Control-Request-Method: GET' http://localhost:8090/api/v1/health" | grep -i access-control

# Login (full flow)
ssh oracle-host "curl -s -X POST http://localhost:<PORT>/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
```
