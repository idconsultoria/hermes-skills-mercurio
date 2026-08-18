# Preview Deployment Pattern (PR Preview via NPM)

> Concrete implementation from Sprint 1 TaskFlow (2026-06-08).
> Server: Oracle Cloud 129.146.163.107, NPM on port 81, Docker Compose stacks.

## Files Created

| File | Location | Purpose |
|------|----------|---------|
| `docker-compose.preview.yml` | project root | Compose override: isolated containers, DB, ports |
| `scripts/register-proxy-host.py` | project root | INSERT proxy_host in NPM SQLite |
| `scripts/register-preview.sh` | project root | Wrapper: copy DB → register → copy back |
| `scripts/unregister-preview.sh` | project root | Soft-delete proxy_host from NPM |
| `.github/workflows/preview.yml` | project root | CI: deploy on open/sync, cleanup on close |

## docker-compose.preview.yml Template

```yaml
services:
  backend:
    container_name: taskflow-backend-${PR_NUMBER}
    image: ghcr.io/[REDACTED]/taskflow-mvp/backend:pr-${PR_NUMBER}
    environment:
      DATABASE_URL: postgresql+asyncpg://taskflow:taskflow@db:5432/taskflow_pr_${PR_NUMBER}
    networks:
      - taskflow-net
      - proxy_network       # required for NPM to reach container

  frontend:
    container_name: taskflow-frontend-${PR_NUMBER}
    image: ghcr.io/[REDACTED]/taskflow-mvp/frontend:pr-${PR_NUMBER}
    environment:
      VITE_API_URL: https://${PR_NUMBER}.praxis.129.146.163.107.sslip.io
    networks:
      - taskflow-net
      - proxy_network
```

## GitHub Actions Workflow (preview.yml)

**Triggers:** `pull_request: [opened, synchronize, reopened, closed]`

**Jobs:**
- `preview-deploy` (on != closed): Build images :pr-N → push GHCR → SSH pull → docker compose up → create DB → migrate → register NPM
- `preview-cleanup` (on == closed): Unregister NPM → docker stop/rm → drop DB → rmi images
- `preview-comment` (on != closed): Post/update PR comment with preview URL

**Key constraint:** `secrets.GITHUB_TOKEN` used in `appleboy/ssh-action` for `docker login ghcr.io` **will fail** because the auto-generated token only has `packages:write` scope within Actions context, not `read:packages` from external hosts. Must use a PAT secret (`secrets.GHCR_TOKEN`) with `write:packages` scope.

## NPM Proxy Host Registration

The NPM SQLite DB has these required fields in `proxy_host`:

```sql
INSERT INTO proxy_host (
  id, created_on, modified_on, owner_user_id, is_deleted,
  domain_names, forward_host, forward_port,
  access_list_id, certificate_id, ssl_forced, caching_enabled,
  block_exploits, advanced_config, meta, allow_websocket_upgrade,
  http2_support, forward_scheme, enabled, locations,
  hsts_enabled, hsts_subdomains, trust_forwarded_proto
) VALUES (?, ?, ?, ?, 0,
          ?, ?, ?,
          0, 0, 1, 0,
          0, '', '{}', 1,
          0, 'http', 1, '[]',
          0, 0, 0);
```

**Critical NOT NULL fields** (use defaults or 0/'{}'/''):
- `access_list_id` = 0
- `certificate_id` = 0  
- `meta` = '{}'
- `locations` = '[]'
- `advanced_config` = ''

## SSH Quoting Workaround

When SSH heredocs mangle Python strings with quotes:

```bash
# BROKEN — inner quotes conflict with heredoc delimiter
ssh host 'cat > file.py << '\''EOF'\''
code = "with 'quotes'"  # ← shell breaks here
EOF'

# FIXED — write locally, scp to host
write_file /tmp/script.py  # ← from agent
scp /tmp/script.py host:/path/
```

## DNS for Wildcard Subdomains

- **sslip.io:** `{pr}.{ip}.sslip.io` — free wildcard, no setup. But test resolution first: some 4-octet IP formats get truncated by nip.io/sslip.io
- **gotdns.ch:** Add `*` A record pointing to server IP. Verify with `python3 -c "import socket; print(socket.getaddrinfo('test.{domain}', 80)[0][4][0])"`
- **Cloudflare:** Wildcard DNS (`*.domain.com`) included in free plan
