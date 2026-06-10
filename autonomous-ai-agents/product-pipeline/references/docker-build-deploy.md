# Docker Build & Deploy — Padrões e Pitfalls

> Válido para: stacks multi-container (Vite+React + FastAPI + PostgreSQL + nginx + Redis)
> Oracle VM, Docker Compose, self-hosted

## Padrão de Dockerfiles

### Frontend (Vite + React + TypeScript + Tailwind)

```dockerfile
# Stage 1: Builder
FROM node:22-alpine AS builder
WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm install            # ← npm ci se package-lock.json existir
COPY . .
RUN npm run build

# Stage 2: Static server (nginx)
FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/*
RUN printf "server {\n    listen 5173;\n    location / {\n        root /usr/share/nginx/html;\n        try_files \$uri \$uri/ /index.html;\n    }\n}\n" > /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist /usr/share/nginx/html
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
```

### Backend (FastAPI + SQLAlchemy)

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Se ghcr.io for inacessível (Oracle VM comum), use pip install uv
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]"

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Catálogo de Bloqueios em Build

| # | Sintoma | Causa Raiz | Fix |
|---|---------|------------|-----|
| 1 | `failed to read dockerfile: open Dockerfile: no such file or directory` | Frontend Dockerfile nunca foi criado (ou 0 bytes) | Criar Dockerfile multi-stage: node:22 → nginx:alpine (ver padrão acima) |
| 2 | `failed to solve: ghcr.io/astral-sh/uv:latest` | Registry ghcr.io bloqueado na Oracle VM (DNS/network) | Substituir `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv` por `RUN pip install uv` |
| 3 | `npm error A complete log of this run is in: /root/.npm/_logs/` | `npm ci` exige `package-lock.json` — se não existir ou for incompleto, falha | Trocar para `npm install` (mais tolerante) |
| 4 | `Failed to load PostCSS config — Cannot find module '@tailwindcss/postcss'` | `postcss.config.js` referencia plugin que não está no `package.json` | Adicionar `"@tailwindcss/postcss": "^4.0.0"` ao `devDependencies` — ou remover `postcss.config.js` se `@tailwindcss/vite` já estiver no `vite.config.ts` |
| 5 | `Bind for 0.0.0.0:80 failed: port is already allocated` | Porta 80 ocupada (ex: Nginx Proxy Manager, outro nginx) | Remapear: `"8080:80"` no docker-compose.yml |
| 6 | `ModuleNotFoundError: No module named 'asyncpg'` | `asyncpg` não listado em `pyproject.toml` (ou só em optional-dependencies) | Adicionar `"asyncpg"` e `"psycopg2-binary"` ao array `dependencies` em pyproject.toml, rebuildar |
| 7 | Container roda mas `/health` retorna 401 | Rota de health check requer autenticação — o framework aplica middleware global | Verificar se a rota `/health` está no `exempt_routes` do middleware de auth, ou criar middleware condicional |
| **8** | **Migration PostgreSQL: Boolean default `0`** | Migração escrita para SQLite usa `sa.text("0")` em coluna BOOLEAN; PostgreSQL rejeita integer como default booleano | Trocar `server_default=sa.text("0")` por `sa.text("false")` e `sa.text("1")` por `sa.text("true")` em TODAS as colunas Boolean. Verificar também o model ORM (`server_default="0"` → `"false"`) |
| **9** | **Migration PostgreSQL: import path errado** | Alembic `env.py` importa de `taskflow.db.base` mas módulo está em `taskflow.models.base` | Corrigir import no `alembic/env.py` |
| **10** | **Docker HEALTHCHECK caminho errado** | HEALTHCHECK no Dockerfile bate em `/health` mas rota real é `/api/v1/health` (prefixo do router) | Alinhar o caminho no `CMD curl -f` do HEALTHCHECK com a rota real do health endpoint |
| **11** | **bcrypt 5.0.0 + passlib 1.7.4 incompatível** | bcrypt 5.0.0 quebra o `detect_wrap_bug` do passlib. Docker baixa a última versão se não estiver pinado | Pinar `bcrypt==4.0.1` no `pyproject.toml` como dependência direta. Hotfix sem rebuild: `docker exec pip install bcrypt==4.0.1` |
| **12** | **Model UUID vs PostgreSQL UUID type mismatch** | Model usa `String(36)` como PK (funciona SQLite), migration cria `uuid` no PostgreSQL. INSERT gera `$1::VARCHAR` → rejeitado | Trocar para `from sqlalchemy.dialects.postgresql import UUID`. PK: `id: Mapped[str] = mapped_column(UUID, primary_key=True, default=lambda: str(uuid4()))` |
| **13** | **Pydantic rejeita UUID object em response model** | Após corrigir models para UUID, ORM retorna `uuid.UUID`. Pydantic v2 `from_attributes=True` rejeita UUID como str | Criar type alias global: `IdStr = Annotated[str, BeforeValidator(str)]` em `schemas/common.py`. Usar em TODOS os schemas de resposta |
| **14** | **Subtask migration com coluna faltando** | Model de subtask tem `completed_at` mas migration não criou a coluna | `ALTER TABLE subtasks ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE;`. Verificar TODAS as colunas do model vs schema real |
| **15** | **Rota /search capturada por /{task_id}** | FastAPI casa rotas em ordem. `/tasks/search` vira `task_id = "search"` se router detail vem antes de search | Declarar router de actions/search ANTES do detail no `__init__.py`: `include_router(actions)` antes de `include_router(detail)` |

## Entrypoint Pattern (alembic migrations no startup)

Para garantir que migrations rodem automaticamente ao subir o container:

```dockerfile
# Crie backend/docker-entrypoint.sh:
#   #!/bin/sh
#   set -e
#   echo "Running migrations..."
#   alembic upgrade head
#   echo "Starting application..."
#   exec "$@"

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
```

⚠️ **Se as migrations falharem, o container restartará em loop.** Sempre testar localmente antes de buildar. Em caso de erro, resetar o banco com `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` e rebuildar.

## Double-nginx Architecture Note

O padrão atual tem **2 camadas de nginx**:
1. **Frontend container** — nginx interno servindo static files (porta 5173)
2. **Proxy nginx** — nginx separado (:8080) roteando / → frontend, /api/ → backend

Isso funciona mas adiciona complexidade desnecessária. Simplificação possível: servir os static files do frontend diretamente do proxy nginx, eliminando o container `frontend` e sua camada de nginx.

## .env Patterns

**Mínimo funcional** para PostgreSQL local:
```env
APP_NAME=TaskFlow
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/dbname
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=["http://localhost:80","http://localhost:5173","http://localhost:8080"]
```

**⚠️ SECRET_KEY é obrigatória** — se o `.env` não tiver, o backend falha ao importar (pydantic-settings valida campo sem default).

## Verification Checklist

Após `docker compose up -d`:

```bash
# 1. Todos os containers rodando?
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Backend responde na URL REAL da rota?
# (Verificar o prefixo do router: /health ou /api/v1/health)
curl -sf http://localhost:8000/api/v1/health || curl -sf http://localhost:8000/health
# Esperado: 200 com JSON {"status":"healthy",...}

# 3. Backend está healthy no Docker?
docker inspect --format='{{.State.Health.Status}}' taskflow-backend
# Esperado: healthy (se "unhealthy" ou "starting", checar logs)

# 4. Frontend servindo?
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/
# Esperado: 200

# 4. nginx proxy funcional?
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/
# Esperado: 200

# 5. Logs sem erro?
docker logs taskflow-backend --tail 20 2>&1 | grep -i error

# 6. db e redis saudáveis?
docker inspect --format='{{.State.Health.Status}}' taskflow-db
docker inspect --format='{{.State.Health.Status}}' taskflow-redis
```

## Notas por Ambiente

### Oracle VM (ARM64)
- ghcr.io frequentemente inacessível → preferir `pip install` sobre `COPY --from=ghcr.io`
- Docker Compose v2: atributo `version` obsoleto → remover do docker-compose.yml
- Porta 80 geralmente ocupada por Nginx Proxy Manager → remapear para 8080
- Downloads de imagem: arm64 tem boa cobertura (node, python, nginx, postgres, redis)
