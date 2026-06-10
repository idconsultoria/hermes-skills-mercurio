# Preview Accessibility Diagnosis

Systematic approach to verifying whether a service deployed in a PR preview is actually publicly reachable.

## 1. Is the Deploy Workflow Actually Running?

```bash
# List open PRs
gh pr list --repo owner/repo --state open --json number,title,headRefName,url

# View status checks on a PR — look for "Deploy Preview" check
gh pr view N --repo owner/repo --json statusCheckRollup
```

Check for:
- `❌ FAILURE` — deploy broke, read logs
- `🟡 IN_PROGRESS` / `"" conclusion` — still building, wait
- `✅ SUCCESS` — deploy finished, proceed to verify

To read deploy logs while IN_PROGRESS is not possible via API. Check the workflow run directly:

```bash
gh run list --repo owner/repo --limit 10 --json databaseId,conclusion,status,displayTitle,headBranch,url
gh run view <RUN_ID> --repo owner/repo --log --job <JOB_ID>  # fails if IN_PROGRESS
```

## 2. What Gets Deployed? (docker-compose Topology)

Read the compose files to understand **which services exist** and **which networks they're on**:

```bash
# Read from GitHub (no local clone needed)
gh api repos/owner/repo/contents/docker-compose.preview.yml?ref=branch-name --jq '.content' | base64 -d
gh api repos/owner/repo/contents/docker-compose.yml?ref=branch-name --jq '.content' | base64 -d
```

**Key questions per service:**

| Question | How to Check | What it Means |
|----------|-------------|---------------|
| Has `ports:`? | Look for `"8000:8000"` or similar | Exposed on host network — reachable via server IP:port |
| Has `proxy_network`? | Check `networks:` list | Reachable via reverse proxy (Nginx/NPM/Traefik) |
| Has `taskflow-net` only? | Only internal network | Not publicly accessible — only reachable by other containers on same network |
| Has `profiles: [manual]`? | Check service block | Won't start with `docker compose up -d`, must be started separately |

**Common pattern:** The main app (backend + frontend) goes on `proxy_network`; auxiliary services (MCP, workers, migrations) go on internal networks only.

## 3. What Does the Reverse Proxy Route?

Read the proxy registration script:

```bash
gh api repos/owner/repo/contents/scripts/register-preview.sh?ref=branch-name --jq '.content' | base64 -d
```

Look for `location` blocks:

```nginx
location /api/    { proxy_pass http://backend:8000; }   # ✅ Proxied
location /mcp/    { ... }                                 # ❌ Missing = MCP not exposed
location /health  { proxy_pass http://backend:8000; }   # ✅ Health endpoint
```

**MCP-specific:** For an MCP server to be publicly accessible, it needs:
1. A `location` block in nginx for the MCP endpoint (e.g., `/mcp/`)
2. The MCP container on `proxy_network` (so nginx can reach it)
3. Either SSE transport (HTTP-streaming) or a WebSocket upgrade path

## 4. Test the Preview URL

After confirming the proxy should route, test:

```bash
# Step 1: Check DNS resolution
dig +short <PR_NUMBER>.preview.domain.com

# Step 2: Try health endpoint
curl -sk --connect-timeout 10 "https://<PR_NUMBER>.preview.domain.com/health"

# Step 3: Diagnose TLS issues
curl -skv --connect-timeout 15 "https://<PR_NUMBER>.preview.domain.com/health" 2>&1 | grep -E "SSL|TLS|certificate|error|alert"
```

### TLS Error Reference

| curl Error | Likely Cause | 
|------------|-------------|
| `SSL routines::tlsv1 unrecognized name` | Certificate doesn't cover this hostname. NPM/Traefik has no matching cert. |
| `SSL certificate problem: self-signed` | Using self-signed cert, use `-k` or update CA bundle |
| `Connection refused` (port 443) | Nginx/NPM not running, or no listener on 443 |
| `Connection timeout` (port 443) | Firewall blocking, or server unreachable |
| `Empty response` (200 with 0 bytes) | Proxy is forwarding but upstream is not responding |
| **Exit code 35** (SSL connect error) | TLS handshake failed — cert mismatch or expired |
| **Exit code 28** (timeout) | Server not reachable at all — check firewall or deploy status |

## 5. Debugging: Is the Container Running on the Server?

If you have SSH access:

```bash
# Check if the specific preview container is running
ssh ubuntu@server "docker ps --filter name=taskflow-mcp-${PR_NUMBER}"

# Check logs
ssh ubuntu@server "docker logs taskflow-mcp-${PR_NUMBER} --tail 20"

# Check if it's on the right network
ssh ubuntu@server "docker inspect taskflow-mcp-${PR_NUMBER} --format '{{json .NetworkSettings.Networks}}' | jq ."

# Direct test: can nginx reach it?
ssh ubuntu@server "docker exec nginx_proxy_manager curl -s http://taskflow-mcp-${PR_NUMBER}:<PORT>/health"
```

## 6. Full Verification Checklist

- [ ] PR deploy check exists and is ✅ SUCCESS
- [ ] Service is defined in docker-compose.preview.yml
- [ ] Service is on `proxy_network` OR has exposed `ports:`
- [ ] Reverse proxy config has a `location` block routing to this service
- [ ] No `profiles: [manual]` (or it was started explicitly)
- [ ] DNS resolves preview URL to server IP
- [ ] Health endpoint returns 200 with valid JSON
- [ ] TLS cert is valid for the preview domain

## 7. Common Pitfalls

- **"Deploy ran successfully but URL doesn't work"** — check if the container got on `proxy_network`. Missing `networks:` in the override file is invisible to deploy scripts.
- **"Previous preview was working, now it's broken"** — new push re-deploys and replaces containers. If the new deployment crashed, the old one is gone too.
- **"Only some routes work"** — compare what `register-preview.sh` routes vs what the service needs. MCP often uses different paths or protocols than the REST API.
- **"HTTPS fails but HTTP works"** — NPM auto-TLS may not have a cert for the preview hostname. Use HTTP-only previews or add a wildcard cert for `*.praxis.domain.com`.
