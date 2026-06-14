# Preview Architecture — TaskFlow MCP

## Estrutura

Cada PR ganha **3 containers isolados** via `docker-compose.preview.yml`:

| Serviço | Container | Imagem | Porta |
|---------|-----------|--------|-------|
| Backend | `taskflow-backend-{PR_NUMBER}` | `ghcr.io/.../backend:pr-{PR_NUMBER}` | 8000 |
| Frontend | `taskflow-frontend-{PR_NUMBER}` | `ghcr.io/.../frontend:pr-{PR_NUMBER}` | (NPM proxy) |
| MCP | `taskflow-mcp-{PR_NUMBER}` | `ghcr.io/.../backend:pr-{PR_NUMBER}` (cmd: taskflow-mcp) | 8100 |

## Banco de dados

- Database isolada: `taskflow_pr_{PR_NUMBER}`
- Criada automaticamente via service `db-init` (profiles: [manual])
- Schema idêntico ao de produção (via `Base.metadata.create_all` no startup do MCP)

## Rede

```
                 Internet
                    │
            ┌───────┴───────┐
            │  NPM (Nginx)  │
            │  129.146.163.107│
            └───────┬───────┘
                    │
        ┌───────────┴───────────┐
        │   proxy_network       │
        │                       │
        │   taskflow-net        │
        │   ┌───────────────┐   │
        │   │   db (PG 16)  │   │
        │   └───────────────┘   │
        └───────────────────────┘
```

- NPM roteia `{PR_NUMBER}.praxis.129.146.163.107.sslip.io` para o container correto
- Hermes conecta no MCP via Docker bridge (`172.19.0.1` → host → NPM → container)
- Header `Host: {PR_NUMBER}.praxis...` é o seletor de preview no NPM

## MCP User

O container MCP recebe:

```yaml
MCP_USER_EMAIL: demo@taskflow.dev
MCP_USER_NAME: Maria Silva
```

O server faz `get_by_email()` no startup. Se o user não existe, cria com senha default (`MCP_USER_PASSWORD`).

## Fluxo de Deploy

1. Build de imagem via GitHub Actions (`ghcr.io/.../backend:pr-{N}` e `frontend:pr-{N}`)
2. `docker compose -f docker-compose.yml -f docker-compose.preview.yml up -d` com `PR_NUMBER=N`
3. NPM aponta automaticamente (configurado manualmente na primeira vez)

## Comandos úteis

```bash
# Subir preview
PR_NUMBER=42 docker compose -f docker-compose.yml -f docker-compose.preview.yml up -d

# Criar database (primeira vez)
docker compose -f docker-compose.yml -f docker-compose.preview.yml run --rm db-init

# Ver logs do MCP
docker logs taskflow-mcp-42

# Testar conexão SSE
curl -v -H "Host: 42.praxis.129.146.163.107.sslip.io" http://172.19.0.1/mcp/sse
```
