# Preview MCP User Configuration

How to change which user the MCP server operates as in a PR preview environment.

## The MCP User Identity Flow

```
Hermes MCP client
  config.yaml → mcp_servers.taskflow.url → http://172.19.0.1/mcp/sse
       |
       v
NPM proxy (Host header → PR number)
  ˥ praxis.129.146.163.107.sslip.io → taskflow-mcp-˥:8100
       |
       v
MCP server container
  server.py → _ensure_default_user():
    mcp_email = os.environ["MCP_USER_EMAIL"]   # ← THIS is the key
    existing = await repo.get_by_email(mcp_email)
    if existing: return existing.id             # Usa user existente
    # else: cria novo user com este email
```

The MCP server's `_ensure_default_user()` in `server.py`:
1. Reads `MCP_USER_EMAIL` from env (default: `mcp@taskflow.local`)
2. Tries `get_by_email()` on the database
3. If found → operates as that existing user
4. If not found → creates a new user with `MCP_USER_NAME` and `MCP_USER_PASSWORD`

**Important:** If the user was already created via the frontend signup, step (3) will find them. No password check is performed — the MCP server just needs the email to match.

## Where to Change It

### docker-compose.preview.yml (the deploy copy)

```yaml
services:
  mcp:
    environment:
      MCP_USER_EMAIL: "gustavomelloenciv@gmail.com"   # ← email do user desejado
      MCP_USER_NAME: "Gustavo Mello"                   # ← usado só se criar novo user
      MCP_USER_PASSWORD: ${MCP_USER_PASSWORD}          # ← usado só se criar novo user
```

### ⚠️ Two Copies of the File

There are TWO copies of `docker-compose.preview.yml` on the host:

| Location | Use | Owned by |
|----------|-----|----------|
| `/home/ubuntu/selfhost/taskflow/docker-compose.preview.yml` | **Deploy** — docker compose reads this | `ubuntu:ubuntu` |
| `/home/ubuntu/selfhost/shared/code/workstation/taskflow/docker-compose.preview.yml` | **Shared volume** — Hermes edits via `/opt/data/code/...` | `uid 10000` (container) |

**Changing the shared volume copy does NOT update the deploy copy.** You must sync manually:

```bash
ssh oracle 'cp /home/ubuntu/selfhost/shared/code/workstation/taskflow/docker-compose.preview.yml \
            /home/ubuntu/selfhost/taskflow/docker-compose.preview.yml'
```

This dual-path exists because the shared volume (`shared/`) is bind-mounted into the Hermes/Pi containers for code editing, but the actual docker-compose deployment runs from `selfhost/taskflow/` — a separate directory.

## Complete Workflow: Change MCP User

```bash
# 1. Edit the compose file (via write_file on the shared volume path)
#    Path: /opt/data/code/workstation/taskflow/docker-compose.preview.yml

# 2. Sync to deploy dir
ssh oracle 'cp /home/ubuntu/selfhost/shared/code/workstation/taskflow/docker-compose.preview.yml \
            /home/ubuntu/selfhost/taskflow/docker-compose.preview.yml'

# 3. Restart only the MCP service (recreates container with new env)
ssh oracle 'cd /home/ubuntu/selfhost/taskflow && \
  PR_NUMBER=<N> docker compose -f docker-compose.yml -f docker-compose.preview.yml up -d mcp'

# 4. Verify the new user
ssh oracle 'docker logs taskflow-mcp-<N> 2>&1 | grep "Operating as"'
# Expected: [TaskFlow MCP] Operating as: Gustavo Mello <gustavomelloenciv@gmail.com> (...)

# 5. Reload MCP connection in Hermes session
#    Use /reload-mcp or restart Hermes
```

## Verification

```bash
# Check MCP logs for user identity
ssh oracle 'docker logs taskflow-mcp-<N> 2>&1 | grep -i "operating\|user"'

# Check env vars on the running container
ssh oracle 'docker inspect taskflow-mcp-<N> --format "{{json .Config.Env}}" | python3 -c "import sys,json; [print(e) for e in json.load(sys.stdin) if \"MCP_USER\" in e]"'
```

## Pitfalls

- **Two copies of compose files:** always sync after editing the shared volume copy
- **User must already exist in the database** if you want the MCP to use an existing account. If the email doesn't match any user, the MCP creates a new one with `MCP_USER_NAME` — which won't have that user's existing tasks
- **Frontend vs MCP user mismatch:** if MCP uses a different user than the frontend is logged into, tasks created via MCP tools are invisible in the frontend and vice versa
- **MCP_USER_PASSWORD is only used on user creation** — if the user already exists, password is ignored. No authentication check happens at MCP startup beyond email lookup
- **Container restart in preview resets in-memory state** but preserves the database (Postgres is a separate container). The `_ensure_default_user()` only does a DB lookup + optional create — no data loss
