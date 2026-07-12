# NPM (Nginx Proxy Manager) — Database Schema Reference

Useful for adding/auditing proxy hosts when the NPM API password is unknown but you have SQLite access to `/data/database.sqlite`.

## Access

```bash
# Copy DB from container to host for inspection
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite

# Inspect with Python (sqlite3 may not be installed on host)
python3 -c "
import sqlite3
conn = sqlite3.connect('/tmp/npm.sqlite')
c = conn.cursor()
c.execute('SELECT id, domain_names, forward_host, forward_port, ssl_forced, certificate_id, forward_scheme, enabled FROM proxy_host WHERE is_deleted=0')
for row in c.fetchall():
    print(row)
"
```

## Key Tables

### `proxy_host`

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `id` | integer PK autoincrement | | |
| `domain_names` | json (TEXT) | | `'["domain.com"]'` |
| `forward_host` | varchar(255) | | Container name or IP |
| `forward_port` | integer | | 80, 8000, etc. |
| `forward_scheme` | varchar(255) | `'http'` | `'http'` or `'https'` |
| `ssl_forced` | integer | 0 | 1 = redirect HTTP→HTTPS |
| `certificate_id` | integer | 0 | 0 = no SSL cert |
| `caching_enabled` | integer | 0 | |
| `block_exploits` | integer | 0 | |
| `allow_websocket_upgrade` | integer | 0 | 1 for WS support |
| `http2_support` | integer | 0 | |
| `hsts_enabled` | integer | 0 | |
| `hsts_subdomains` | integer | 0 | |
| `advanced_config` | text | `''` | Custom nginx config |
| `locations` | json | `'[]'` | |
| `meta` | json | `'{}'` | |
| `access_list_id` | integer | 0 | |
| `owner_user_id` | integer | | Usually 1 |
| `is_deleted` | integer | 0 | Soft delete flag |
| `enabled` | integer | 1 | |

### `certificate`

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | Auto |
| `provider` | varchar(255) | `'letsencrypt'` or `'other'` |
| `nice_name` | varchar(255) | Human label |
| `domain_names` | json | `'["domain.com"]'` |
| `expires_on` | datetime | Cert expiry |
| `meta` | json | `'{}'` |

## Creating a proxy host (read-only DB approach)

When you need to add a host but only have DB read access (no API password):

1. **Read** existing configs from the DB to understand the current setup
2. **Use the NPM web UI** (port 81) if the user can log in — this allows Let's Encrypt cert issuance
3. **Direct DB insert** only works for HTTP-only hosts (`certificate_id=0`, `ssl_forced=0`). Let's Encrypt certs cannot be created via raw SQL.

## Custom nginx config (server-level include)

For complex routing rules that don't fit the location/advanced_config mold, NPM auto-includes any file matching `/data/nginx/custom/server_proxy[.]conf` at the **server block level** in each proxy host's generated config.

This allows adding arbitrary `location` blocks that NPM's UI doesn't expose:

```nginx
location /delfos/ {
    proxy_pass http://backend-nginx:80/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Write it via `docker exec` — use base64 encoding to avoid shell-escaping `$` variables:

```bash
echo 'bG9jYXRpb24gL2RlbGZvcy8gewogICAgcHJveHlfcGFzcyBodHRwOi8vZGVsZm9zLW5naW54OjgwLzsKfQo=' | base64 -d | docker exec -i nginx_proxy_manager sh -c 'cat > /data/nginx/custom/server_proxy.conf'
```

**⚠️ PITFALL: Multi-line CSP header causes 502 from openresty**

If the backend nginx adds a `Content-Security-Policy` header with a multi-line value (folded header), NPM's openresty will reject the upstream response:

```
upstream sent invalid header: "\x20..." while reading response header from upstream
```

The `\x20` is a space character at the start of the continuation line. **Fix:** Make the CSP header a single line:

```nginx
# ❌ Bad — multi-line (triggers 502 from openresty)
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self';
" always;

# ✅ Good — single-line
add_header Content-Security-Policy "default-src 'self'; script-src 'self';" always;
```

After fixing, reload nginx: `nginx -s reload` or restart the container.

## Cross-Docker-network connectivity

NPM containers are often on their own Docker networks (e.g., `proxy_network`, `ai_mesh`). If the target backend is on a different network (e.g., `delfos_default`), the container hostname won't resolve and NPM will fail to start:

```
nginx: [emerg] host not found in upstream "<backend-container>" in /data/nginx/proxy_host/1.conf
```

**Solutions:**

### A. Connect NPM to the backend's network

```bash
docker network connect <backend_network> nginx_proxy_manager
```

After connecting, use the backend container's hostname (Docker DNS) in the proxy config.

### B. Use IP address

Find the backend container's IP and use it directly:

```bash
docker inspect <backend-container> --format "{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
```

This is fragile (IPs change on container recreation) and only works until the container is rebuilt.

### C. Verify connectivity

```bash
# Check what networks NPM is on
docker inspect nginx_proxy_manager --format "{{json .NetworkSettings.Networks}}" | python3 -c "import sys,json; [print(k,v['IPAddress']) for k,v in json.load(sys.stdin).items()]"

# Test connection from inside NPM
docker exec nginx_proxy_manager curl -sS http://<target-container>:<port>/health
```

## Testing routing without DNS

```bash
# Test with Host header through internal nginx
curl -s -o /dev/null -w "%{http_code}" \
  -H "Host: <domain>" \
  http://localhost:8080/api/v1/health

# Test from inside NPM container
docker exec nginx_proxy_manager curl -sS \
  http://<upstream-container>:<port>/api/v1/health

# Verify DNS resolution
docker run --rm busybox nslookup <domain> 8.8.8.8
```
