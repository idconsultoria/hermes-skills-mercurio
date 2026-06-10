# FastMCP Deployment & SSE Patterns

This reference covers four layers of making FastMCP work reliably in Docker:
1. **Event loop fix** — asyncpg + FastMCP anyio incompatibility
2. **SSE transport** — exposing MCP over HTTP instead of stdio
3. **Docker + Nginx** — deploying MCP behind a reverse proxy
4. **User identity** — making MCP operate as a configurable user
5. **Tool-call patterns** — 2-step confirmation flow

## Sintoma do event loop

FastMCP 2.x com `transport="stdio"` inicia OK (`initialize` retorna server info),
mas qualquer tool que use `async_session_factory()` (SQLAlchemy async engine +
asyncpg) falha com:

```
Task <Task pending name='mcp.server.lowlevel.server.Server._handle_message'>
  got Future <Future pending ...> attached to a different loop
```

Ou para operações subsequentes:

```
asyncpg.exceptions._base.InterfaceError:
  cannot perform operation: another operation is in progress
```

## Causa

FastMCP stdio mode usa **anyio** internamente (não `asyncio` padrão). Quando
`create_async_engine()` é chamado no módulo `database.py` no escopo global
(em tempo de import), o engine fica vinculado ao event loop **do módulo que o
importou**. Quando uma MCP tool tenta criar uma sessão via
`async_session_factory()`, o engine tenta usar o loop que estava ativo durante
a importação do módulo — mas a tool está rodando no loop do anyio.

## Soluções

### Solução A: Bypass — `asyncio.run()` direto (para testes)

Não passa pelo FastMCP, chama o mesmo código numa `asyncio.run()` limpa:

```bash
docker exec -e DATABASE_URL=... taskflow-backend-4 python3 -c "
import asyncio
async def main():
    service, session = await _get_task_service()
    task = await service.create_task(user_id='...', title='test')
    await session.commit()  # ← NECESSÁRIO! O service não faz commit
asyncio.run(main())
"
```

⚠️ `_get_task_service()` não faz commit. É preciso chamar
`await session.commit()` explicitamente — senão a task some após o `finally:
await session.close()` do script.

### Solução B: Lazy engine + NullPool no database.py (RECOMENDADO)

Diferir a criação do engine para dentro de um async context, e usar `NullPool`
para evitar que o pool retenha conexões do loop errado:

```python
from sqlalchemy.pool import NullPool

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            poolclass=NullPool,
        )
    return _engine

async_session_factory = async_sessionmaker(
    get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
)
```

A engine ainda é criada na primeira chamada, que pode ser de dentro do anyio
loop — então o loop correto é capturado.

**⚡ Importante:** qualquer arquivo que importava `engine` diretamente precisa ser
atualizado para usar `get_engine()`:
- `backend/taskflow/main.py` — lifespan usa `engine` → `get_engine()`
- `backend/taskflow/mcp/server.py` — `_ensure_database()` usa `engine`
- `tests/integration/conftest.py` — engine global

### Solução C: `transport="sse"` no server.py

Mudar o MCP para servir via HTTP SSE:

```python
# No server.py:
mcp_host = os.environ.get("MCP_HOST", "0.0.0.0")
mcp_port = int(os.environ.get("MCP_PORT", "8100"))
mcp.run(transport="sse", host=mcp_host, port=mcp_port)
```

Isso faz o FastMCP iniciar um servidor HTTP (use porta dedicada como 8100
para evitar conflito com o backend FastAPI). Cada tool call roda no próprio
loop do servidor. Perde-se compatibilidade stdio mas ganha-se estabilidade
com async engines.

**FastMCP SSE endpoints:**
- `GET /sse` — SSE stream (cliente conecta aqui)
- `POST /messages/?session_id=<id>` — envia/recebe JSON-RPC messages
- O session_id é obtido do primeiro evento do SSE stream

## Deploy do MCP em Docker + Nginx

### 1. docker-compose.preview.yml

```yaml
services:
  mcp:
    container_name: taskflow-mcp-${PR_NUMBER}
    image: ghcr.io/org/repo/backend:pr-${PR_NUMBER}
    command: taskflow-mcp
    ports:
      - "${MCP_PORT:-0}:8100"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/db_${PR_NUMBER}
      SECRET_KEY: ${SECRET_KEY}
      MCP_USER_EMAIL: "demo@taskflow.dev"     # ← ESSENCIAL: usuário correto
      MCP_USER_NAME: "Maria Silva"
      MCP_USER_PASSWORD: ${MCP_USER_PASSWORD}
      MCP_PORT: "8100"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - taskflow-net
      - proxy_network               # NPM precisa desta rede
```

### 2. Nginx location (register-preview.sh)

**CRITICAL — two locations needed, with different proxy_pass trailing-slash behavior:**

```nginx
# MCP SSE endpoint — FastMCP serves SSE at /sse
# Trailing / em proxy_pass = strip /mcp/ prefix, envia /sse pro MCP
location /mcp/ {
    proxy_pass http://taskflow-mcp-${PR_NUMBER}:8100/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400s;      # SSE é long-lived
}

# MCP messages callback — FastMCP retorna /messages/?session_id=... no SSE event
# SEM trailing / = preserva /messages/ path original
location /messages/ {
    proxy_pass http://taskflow-mcp-${PR_NUMBER}:8100;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400s;
}
```

**PITFALL — trailing slash no proxy_pass:**

- `/mcp/` **COM** trailing `/` → nginx strips the location prefix: `/mcp/sse` → `http://mcp:8100/sse` ✅
- `/messages/` **SEM** trailing `/` → nginx preserves the full URI: `/messages/?session_id=x` → `http://mcp:8100/messages/?session_id=x` ✅
- ERRADO: inverter causa 404 (path errado no upstream)

**PITFALL — nginx server_name match:**

Se o Hermes MCP client conectar via IP interno (`http://172.19.0.1/mcp/sse`), o Host header será o IP. Nginx precisa ter o IP como server_name:
```nginx
server_name 4.praxis.129.146.163.107.sslip.io 172.19.0.1;
```

O `location /mcp/` faz proxy reverso do Nginx Proxy Manager (porta 80/443)
para o container MCP na porta 8100 (rede interna `proxy_network`).

### 3. CI Workflow (preview.yml)

No step de deploy, incluir `mcp` no docker-compose up:

```yaml
PR_NUMBER=$PR_NUMBER docker compose \
  -f docker-compose.yml \
  -f docker-compose.preview.yml \
  up -d backend frontend mcp          # ← incluir 'mcp'
```

**⚠️ Pitfall:** O workflow roda `docker compose` no servidor usando os
arquivos compose que estão no servidor, não os do CI. Se a PR adicionar
um service novo (ex.: `mcp`), o servidor continua com a versão antiga.
Solução: scp o compose file pro servidor após o push.

## Configuração do MCP Client no Hermes

Para que o Hermes agent use o MCP TaskFlow como tool provider, adicionar no `config.yaml`:

```yaml
mcp_servers:
  taskflow:
    transport: sse              # ← ESSENCIAL: default é StreamableHTTP (POST), incompatível
    url: "http://172.19.0.1/mcp/sse"
    timeout: 180
    connect_timeout: 30
```

**⚠️ CRÍTICO: `transport: sse`** — O Hermes MCP client usa StreamableHTTP por padrão (somente POST), mas o FastMCP com `transport="sse"` espera SSE (GET + POST). Sem `transport: sse`, a conexão falha com `405 Method Not Allowed` porque o cliente tenta POST no endpoint `/sse` que só aceita GET.

**Se o MCP estiver atrás de um nginx com server_name específico**, pode ser necessário adicionar o IP do gateway Docker como server_name alternativo (ver seção Nginx acima).

## Create/Update com resolução contexto/projeto por nome

Tools MCP que aceitam `context` e `project` como parâmetros devem resolver nomes de string para UUIDs, já que o frontend e o MCP enviam strings, não UUIDs.

**Pattern (add to any MCP tool that accepts context/project):**

```python
import re
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

# Before calling service.create_task / service.update_task:
resolved_context_id: str | None = context
if context is not None and not _UUID_RE.match(context):
    ctx_obj = await ContextRepository(session).get_or_create_by_name(
        user_id, context.lower()
    )
    resolved_context_id = ctx_obj.id

resolved_project_id: str | None = project
if project is not None and not _UUID_RE.match(project):
    proj_obj = await ProjectRepository(session).get_or_create_by_name(
        user_id, project.lower()
    )
    resolved_project_id = proj_obj.id
```

Chamar `get_or_create_by_name` (não `get_by_name`) para que strings arbitrárias criem contextos/projetos on demand — consistente com o comportamento do `process_inbox`.

O MCP default user é controlado por `MCP_USER_EMAIL`:

```python
mcp_email = os.environ.get("MCP_USER_EMAIL", "mcp@taskflow.local")
existing = await repo.get_by_email(mcp_email)
if existing:
    return existing.id   # Usa usuário existente (Maria, admin, etc.)
```

Em preview environments, setar `MCP_USER_EMAIL=demo@taskflow.dev` e
`MCP_USER_NAME="Maria Silva"` faz o MCP operar como Maria — as tools
listam/criam tasks no mesmo dataset do frontend.

**Nunca operar como MCP User em preview** — tasks criadas ficam invisíveis
no frontend (que está logado como outro usuário).

## Tool-call patterns via MCP Python client

```bash
pip install mcp
```

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test():
    async with sse_client(url="http://localhost:8102/sse") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"{len(tools.tools)} tools registered")

            # Call a read-only tool
            r = await session.call_tool("taskflow_list_tasks", {"status": "inbox"})
            data = json.loads(r.content[0].text)
            for t in data.get("tasks", []):
                print(f"  [{t['status']}] {t['title']}")

asyncio.run(test())
```

### 2-step confirmation flow (ActionToken)

Tools destrutivas exigem confirmação em 2 passos:

```python
# Step 1: preview (retorna action_token)
r = await session.call_tool("taskflow_create_task", {"title": "..."})
data = json.loads(r.content[0].text)
# → {"requires_confirmation": true, "preview": {...}, "action_token": "<uuid>"}

# Step 2: confirmar com token
r = await session.call_tool("taskflow_create_task", {
    "title": "...",
    "confirm_token": data["action_token"]
})
data2 = json.loads(r.content[0].text)
# → {"success": true, "task": {...}}
```

### Read-only tools (sem confirmação)

`taskflow_list_tasks`, `taskflow_get_task`, `taskflow_get_next_actions`,
`taskflow_weekly_review` — executam direto, sem token.

## Pitfalls

- **Portas ocupadas:** `fuser -k <port>/tcp` pode não funcionar em containers
  minimalistas. Prefira `pkill -f taskflow-mcp` ou use portas alternativas.
- **`_get_task_service()` não faz commit** — sempre chamar `await session.commit()`.
- **CI não sincroniza compose files:** services novos precisam de scp manual.
- **seed_preview.py importa `engine` diretamente** — se database.py refatorar para lazy engine (`_engine` + `get_engine()`), o script quebra com `ImportError: cannot import name 'engine'`. Usar `get_engine()` em vez de `engine`.
- **NPM server_name precisa incluir IP do gateway** se o Hermes conectar via Docker bridge IP. Senão nginx não encontra server block e retorna 404.

## Referência

Código analisado: `taskflow-mvp` branch `sprint1-v2`

- `backend/taskflow/core/database.py` — `create_async_engine()` global
- `backend/taskflow/mcp/server.py` — `mcp.run(transport="stdio")`
- `backend/taskflow/mcp/tools/core.py` — `_get_task_service()`
- `docker-compose.preview.yml` — MCP service com proxy_network + porta 8100
- `scripts/register-preview.sh` — Nginx location /mcp/
- `.github/workflows/preview.yml` — CI com `up -d ... mcp`
