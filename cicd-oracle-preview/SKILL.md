---
name: cicd-oracle-preview
description: "Replicar CI/CD: GHCR arm64, deploy SSH, preview por PR."
version: 1.0.0
author: "ID Consultoria (gustavomello9600), Hermes Agent"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [cicd, github-actions, ghcr, arm64, oracle-cloud, preview-pr, nginx-proxy-manager, deploy-ssh, docker]
    related_skills: [github-pr-workflow, github-repo-management]
---

# CI/CD Oracle com Preview por PR — Skill (padrão ID Consultoria)

> **FORÇA-TAREFA (12 — PADRÃO ATUAL da ID):** desde 22/08/2026 (Artemis),
> o padrão canônico é **build nativo no Oracle host** — **SEM GHCR, SEM QEMU**.
> O `ci.yml` do TaskFlow (QEMU→GHCR→pull) virou **legado**. Ver §14.

Padrão de pipeline da ID para **qualquer** projeto de código: qualidade automatizada no
runner do GitHub, build nativo `linux/arm64` com push para GHCR, deploy automático por SSH
no host Oracle ARM64 e URL de preview efêmera por Pull Request registrada no Nginx Proxy
Manager (NPM). Origem: engenharia reversa do pipeline real de
`gustavomello9600/taskflow-mvp` (workflows, scripts e estado vivo do host Oracle em
22/08/2026). A skill é autocontida — todos os comandos e arquivos prontos para copiar,
com `<placeholders>` marcados para substituição.

## 1. Quando usar

- Replicar este padrão de CI/CD em um projeto de código novo ou existente da ID.
- Diagnosticar falhas do pipeline (build, deploy, preview, rollback) já implantado.
- Auditar um host Oracle antes de conectar um pipeline (pré-requisitos).
- Responder perguntas sobre secrets, isolamento de preview, rollback por SHA ou NPM.

**Não usar para:** deploys em plataformas gerenciadas (Vercel, GH Pages, Fly.io) — o
padrão assume servidor próprio; CI de projetos sem servidor não precisam de `preview.yml`
nem `rollback.yml`.

## 2. Arquitetura

```
                        GITHUB (repo privado)
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
   push/PR → master       PR aberto/atualizado     PR fechado
        │                     │                      │
  ┌─────▼──────┐      ┌───────▼────────┐      ┌──────▼───────┐
  │  ci.yml    │      │  preview.yml   │      │ preview.yml  │
  │ lint+tests │      │ build arm64    │      │ (job cleanup)│
  │ coverage   │      │ push :pr-N     │      │ derruba tudo │
  └─────┬──────┘      │ sobe stack     │      └──────────────┘
        │ só em push  │ registra NPM   │
        ▼             │ comenta URL    │
  ┌──────────┐        └───────┬────────┘
  │ build &  │                │ SSH (appleboy/ssh-action)
  │ push GHCR│                ▼
  │ :sha-X   │        ORACLE HOST (ARM64, ex.: 129.146.163.107)
  │ :latest  │        ├── docker compose pull + up -d
  └────┬─────┘        ├── Nginx Proxy Manager (80/443)
       ▼              ├── Postgres/Redis compartilhados
  deploy.yml          └── URL: https://<N>.praxis.<IP>.sslip.io
  (deploy automático)
       ▼
  rollback.yml (manual, workflow_dispatch): re-tag sha antiga → latest
```

**Princípios do padrão:**

1. **CI roda 100% no GitHub-hosted runner** (`ubuntu-latest`). O servidor nunca compila —
   só puxa imagens prontas do GHCR. Servidor de 2 vCPU fica livre.
2. **Build para `linux/arm64`** (plataforma real do host). Zero QEMU em runtime — evita o
   bug conhecido de `pydantic-settings` travando sob emulação.
3. **Imagens versionadas por SHA curto + `latest`.** Deploy consome `latest`; rollback =
   reapontar `latest`.
4. **Preview por PR é efêmero e isolado:** containers com sufixo `-pr-<N>`, database
   separada por PR (`<app>_pr_<N>`) no Postgres de produção, proxy registrado
   dinamicamente no NPM, tudo destruído no fechamento do PR.
5. **Zero segredo em código.** Acesso ao host = `SSH_PRIVATE_KEY`; acesso ao registry =
   `GHCR_TOKEN`; o resto é o `GITHUB_TOKEN` efêmero do próprio Actions.

## 3. Pré-requisitos de infraestrutura (configuração única)

| # | Item | Detalhe |
|---|------|---------|
| 1 | Servidor com Docker + Compose v2 | Oracle Cloud ARM64 (Ampere A1). Verificar: `terminal(command="ssh host 'docker compose version'")` |
| 2 | **NPM** ocupando 80/443 | Único caminho de entrada (Security List da Oracle normalmente só abre 80/443). Container `nginx_proxy_manager`, rede externa compartilhada (`proxy_network` no TaskFlow) |
| 3 | Rede Docker externa NPM ⇄ apps | `docker network create proxy_network`. Todo serviço com URL pública entra nessa rede; o NPM resolve containers **pelo `container_name`** (DNS interno) |
| 4 | DNS wildcard grátis via **sslip.io** | `{algo}.praxis.129.146.163.107.sslip.io` resolve para o IP automaticamente — sem comprar domínio nem configurar DNS. Substitua pelo seu IP |
| 5 | Certificado TLS no NPM | Request Let's Encrypt para `*.praxis.<IP>.sslip.io` (ou domínio próprio). Proxy hosts de preview herdam `ssl_forced=1` |
| 6 | Repositório de imagens **GHCR** | Imagens privadas em `ghcr.io/<org>/<repo>/<serviço>`. Repo precisa de `packages: write` habilitado |
| 7 | Chave SSH dedicada ao deploy | `ssh-keygen -t ed25519 -f deploy_key`, pública no `authorized_keys` do usuário de deploy do host, privada no secret `SSH_PRIVATE_KEY` |

> ⚠️ Portas altas (8000, 3000...) **não** são acessíveis externamente na Oracle
> (Security List). Nunca exponha preview por porta — sempre atrás do NPM em 443.

## 4. Layout do repositório

```
projeto/
├── .github/workflows/
│   ├── ci.yml            # lint + testes + coverage + build/deploy (push master)
│   ├── preview.yml       # ciclo de vida do preview por PR
│   └── rollback.yml      # rollback manual por SHA
├── backend/
│   ├── Dockerfile
│   └── pyproject.toml    # extras [dev,test,mcp] instalados no CI
├── frontend/
│   └── Dockerfile        # multi-stage: node builder → nginx servindo dist
├── docker-compose.yml        # stack de produção (imagens :latest do GHCR)
├── docker-compose.preview.yml# overlay: mesma stack, sufixada por PR
└── scripts/
    ├── register-preview.sh    # registra proxy host no NPM + nginx conf
    ├── register-proxy-host.py # INSERT idempotente no SQLite do NPM
    ├── unregister-preview.sh  # soft-delete no NPM
    └── seed_preview.py        # popula o banco do preview (opcional)
```

**Dockerfile frontend (referência):**

```dockerfile
FROM node:22-slim AS builder
WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/* && printf "server {\n    listen 5173;\n    location / {\n        root /usr/share/nginx/html;\n        try_files \$uri \$uri/ /index.html;\n    }\n}\n" > /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist /usr/share/nginx/html
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
```

**Substituições mecânicas (sed-like) ao adaptar para outro projeto:**

| No TaskFlow | Trocar por |
|---|---|
| `taskflow-mvp` | `<repo>` |
| `gustavomello9600` | `<org>` |
| `129.146.163.107` | `<IP>` |
| `praxis` | `<subdomínio-base>` |
| `taskflow_pr_` | `<app>_pr_` |
| portas (8000/8100/5173) | conforme o projeto |

## 5. Secrets necessários no GitHub

`Settings → Secrets and variables → Actions` (ou `gh secret set NOME --body "valor"`):

| Secret | Escopo | Como criar | Usado por |
|--------|--------|-----------|-----------|
| `SSH_PRIVATE_KEY` | conteúdo da chave privada ED25519 de deploy (colar o arquivo inteiro, com header `-----BEGIN`) | `ssh-keygen -t ed25519 -f deploy_key` no host + pública no `authorized_keys` | todos os steps SSH (deploy, preview, cleanup, rollback) |
| `GHCR_TOKEN` | classic PAT com escopo **`write:packages`** (inclui `read:packages`) | GitHub → Settings → Developer settings → PAT (classic) | `docker login ghcr.io` **dentro do host**, para puxar imagens privadas |

**Por que o PAT é obrigatório:** o `GITHUB_TOKEN` efêmero do Actions serve para *push*
das imagens (via `packages: write`), mas **não funciona para pull a partir de máquina
externa** — o host recebe `denied: requested access to the resource is refused`. Problema
real resolvido com PAT clássico no TaskFlow.

**O que NÃO precisa de secret:** login do runner no GHCR usa
`${{ secrets.GITHUB_TOKEN }}` com bloco `permissions:` mínimo por workflow
(`contents: read`, `packages: write`, `pull-requests: write` só onde comenta no PR).

> 🐛 **Dívida observada no TaskFlow:** o `preview.yml` referencia
> `secrets.SECRET_KEY` no step de seed, mas esse secret **não está cadastrado** (só
> existem `GHCR_TOKEN` e `SSH_PRIVATE_KEY`). O step executa com valor vazio. Ao replicar:
> ou cadastre o secret, ou remova a referência.

## 6. Workflow 1 — CI de qualidade (`ci.yml`)

Gatilhos: `push` e `pull_request` contra a branch padrão (**confira qual é a sua** — no
TaskFlow é `master`, não `main`; errar isso silencia o pipeline inteiro). Criar o arquivo
com `write_file` em `.github/workflows/ci.yml`:

```yaml
name: Projeto CI/CD
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/<org>/<repo>/backend

permissions:
  contents: read
  packages: write

jobs:
  lint:                          # avisa, não bloqueia (política atual)
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
        working-directory: ./backend
      - run: ruff check .
        working-directory: ./backend
      - run: mypy pkg --ignore-missing-imports || true
        working-directory: ./backend

  test-unit:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python-version }}" }
      - run: pip install -e ".[test,dev]"
        working-directory: ./backend
      - run: pytest tests/unit -v --cov=pkg --cov-report=xml --timeout=30 -m "unit"
        working-directory: ./backend
      - uses: codecov/codecov-action@v4   # opcional; fail_ci_if_error: false

  test-integration:
    services:                    # Postgres/Redis efêmeros no job
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_USER: t, POSTGRES_PASSWORD: t, POSTGRES_DB: t }
        options: >-
          --health-cmd pg_isready --health-interval 10s
          --health-timeout 5s --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping" --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[test,dev]" && pip install asyncpg aiosqlite
        working-directory: ./backend
      - run: DATABASE_URL="sqlite+aiosqlite:///./it.db" pytest tests/integration -m "integration" --timeout=60
        working-directory: ./backend

  coverage-report:
    needs: [test-unit, test-integration]
    steps:
      - run: pytest tests/ --cov=pkg --cov-fail-under=70   # ← gate duro
      - uses: actions/upload-artifact@v4                   # relatório HTML 7 dias
        with: { name: coverage-report, path: htmlcov/ }

  build-and-push:               # SÓ em push para a branch padrão
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    needs: [test-unit, test-integration]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/setup-buildx-action@v3
      - id: sha
        run: echo "sha=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"
      - uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          platforms: linux/arm64            # ← plataforma REAL do host
          tags: |
            ${{ env.IMAGE_BACKEND }}:sha-${{ steps.sha.outputs.sha }}
            ${{ env.IMAGE_BACKEND }}:latest

  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    needs: [build-and-push]
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: <IP_DO_HOST>
          username: <usuario>
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /caminho/do/compose/no/host
            echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f --filter "until=24h"
```

**Pontos de atenção:**

- **`platforms: linux/arm64`** no build. Se o host fosse x86, seria `linux/amd64`. Build
  cross-arch no runner é emulação controlada só durante build (aguenta); runtime nunca.
- **Tags duplas** `sha-X` + `latest`: o SHA habilita rollback; `latest` simplifica o
  compose.
- Coverage com `--cov-fail-under` é o único gate de qualidade duro além dos testes (lint
  e mypy são informativos — decisão consciente para não travar entregas).
- Testes marcados com `-m "unit"`/`-m "integration"` (pytest.ini: `markers`).

## 7. Workflow 2 — Preview por PR (`preview.yml`)

Gatilho: `pull_request` com `types: [opened, synchronize, reopened, closed]`. Um único
arquivo cobre **deploy** (`action != closed`), **comentário** e **cleanup**
(`action == closed`).

### 7.1 Fluxo do job de deploy

1. Login no GHCR (runner) → build/push `backend:pr-<N>` e `frontend:pr-<N>` (arm64).
2. SSH no host (`appleboy/ssh-action`):
   ```bash
   export PR_NUMBER=<N>
   echo "<GHCR_TOKEN>" | docker login ghcr.io -u <actor> --password-stdin
   cd /caminho/do/compose
   docker compose -f docker-compose.yml -f docker-compose.preview.yml pull
   docker exec <db-container> psql -U <user> -c "CREATE DATABASE app_pr_${PR_NUMBER}" 2>/dev/null || echo "DB already exists"
   docker exec <db-container> psql -U <user> -d app_pr_${PR_NUMBER} -c "CREATE EXTENSION IF NOT EXISTS pgcrypto"
   PR_NUMBER=$PR_NUMBER docker compose -f docker-compose.yml -f docker-compose.preview.yml up -d backend frontend mcp
   bash scripts/register-preview.sh
   ```
3. (Opcional) seed do banco do preview rodando script dentro do container novo.
4. Comentário idempotente no PR com as URLs — procura comentário anterior com marcador
   `"Preview Deployed"` e **edita** em vez de duplicar.

`preview.yml` completo (modelo — substituir placeholders):

```yaml
name: Preview PR
on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/<org>/<repo>/backend
  IMAGE_FRONTEND: ghcr.io/<org>/<repo>/frontend

permissions:
  contents: read
  packages: write
  pull-requests: write        # só este workflow comenta no PR

jobs:
  deploy-preview:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          platforms: linux/arm64
          tags: ${{ env.IMAGE_BACKEND }}:pr-${{ github.event.pull_request.number }}
      - uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: true
          platforms: linux/arm64
          tags: ${{ env.IMAGE_FRONTEND }}:pr-${{ github.event.pull_request.number }}
      - uses: appleboy/ssh-action@v1
        with:
          host: <IP_DO_HOST>
          username: <usuario>
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            export PR_NUMBER=${{ github.event.pull_request.number }}
            echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            cd /caminho/do/compose
            docker compose -f docker-compose.yml -f docker-compose.preview.yml pull
            docker exec <db-container> psql -U <user> -c "CREATE DATABASE app_pr_${PR_NUMBER}" 2>/dev/null || echo "DB already exists"
            docker exec <db-container> psql -U <user> -d app_pr_${PR_NUMBER} -c "CREATE EXTENSION IF NOT EXISTS pgcrypto"
            # Endurecimento recomendado: isolar o projeto compose do preview
            #   docker compose -p preview_${PR_NUMBER} -f docker-compose.yml -f docker-compose.preview.yml up -d backend frontend mcp
            PR_NUMBER=$PR_NUMBER docker compose -f docker-compose.yml -f docker-compose.preview.yml up -d backend frontend mcp
            bash scripts/register-preview.sh
      - uses: actions/github-script@v7
        with:
          script: |
            const marker = "Preview Deployed";
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner, repo: context.repo.repo,
              issue_number: context.issue.number
            });
            const existing = comments.find(c => c.body.includes(marker));
            const body = marker + "\n\nBackend: https://" + context.issue.number + ".praxis.<IP>.sslip.io/api\nFrontend: https://" + context.issue.number + ".praxis.<IP>.sslip.io\nMCP: https://" + context.issue.number + ".praxis.<IP>.sslip.io/mcp";
            if (existing) {
              await github.rest.issues.updateComment({
                owner: context.repo.owner, repo: context.repo.repo,
                comment_id: existing.id, body
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner, repo: context.repo.repo,
                issue_number: context.issue.number, body
              });
            }

  cleanup-preview:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: appleboy/ssh-action@v1
        with:
          host: <IP_DO_HOST>
          username: <usuario>
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            export PR_NUMBER=${{ github.event.pull_request.number }}
            cd /caminho/do/compose
            bash scripts/unregister-preview.sh
            PR_NUMBER=$PR_NUMBER docker compose -f docker-compose.yml -f docker-compose.preview.yml down --remove-orphans
            docker exec <db-container> psql -U <user> -c "DROP DATABASE IF EXISTS app_pr_${PR_NUMBER}"
            docker rmi ghcr.io/<org>/<repo>/backend:pr-$PR_NUMBER ghcr.io/<org>/<repo>/frontend:pr-$PR_NUMBER || true
```

> ⚠️ **Isolamento do projeto compose:** no padrão TaskFlow os containers entram no mesmo
> projeto/rede de produção e a identidade vem do `container_name` sufixado. Risco real:
> `up -d` sem overlay (ou no diretório errado) **recria o container de produção** (ver
> pitfall 12). Para garantia total, use `-p preview_${PR_NUMBER}` (projeto compose
> próprio, como o Zera) ou diretório separado — redes externas (`app-net`,
> `proxy_network`) continuam funcionando por nome.

### 7.2 Overlay de preview (`docker-compose.preview.yml`)

O overlay **sobrescreve** os serviços de produção — é aqui que mora o isolamento:

```yaml
services:
  backend:
    container_name: app-backend-${PR_NUMBER}         # sufixo = identidade
    image: ghcr.io/<org>/<repo>/backend:pr-${PR_NUMBER}
    ports: ["${BACKEND_PORT:-0}:8000"]               # porta host aleatória
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/app_pr_${PR_NUMBER}
    networks: [app-net, proxy_network]               # NPM alcança pelo nome

  frontend:
    container_name: app-frontend-${PR_NUMBER}
    image: ghcr.io/<org>/<repo>/frontend:pr-${PR_NUMBER}
    networks: [app-net, proxy_network]
```

**Regras de ouro do overlay:**

- **Mesmo Postgres de produção, databases separadas** (`app_pr_<N>`): simples e barato; o
  DROP no cleanup devolve o espaço. (Alternativa mais dura: compose inteiro isolado — ver
  §10.)
- **`container_name` explícito e sufixado** — é o DNS que o NPM usa como `forward_host`.
- **Entrar na `proxy_network`** — sem isso o proxy não resolve o container.
- Healthchecks herdadas da imagem podem mentir (ex.: checam 8000 num processo que roda na
  8100). Desabilite (`healthcheck: {disable: true}`) ou defina a correta — universal:
  `bash -c "echo > /dev/tcp/localhost/<porta>"`.

### 7.3 Registro no Nginx Proxy Manager (`scripts/register-preview.sh`)

O NPM guarda proxy hosts em SQLite (`/data/database.sqlite`). O script (rodando **no
host**):

1. `docker cp nginx_proxy_manager:/data/database.sqlite /tmp/database.sqlite`
2. Python faz **INSERT idempotente** (se o domínio já existe, retorna o ID):
   ```sql
   INSERT INTO proxy_host (id, created_on, modified_on, owner_user_id, is_deleted,
     domain_names, forward_host, forward_port, ..., ssl_forced, ..., forward_scheme, enabled, ...)
   VALUES (max_id+1, now, now, 1, 0, '["<N>.praxis.<IP>.sslip.io"]',
           '<container-backend>', 8000, ..., 1, ..., 'http', 1, ...);
   ```
3. `docker cp /tmp/database.sqlite nginx_proxy_manager:/data/database.sqlite`
4. Escreve o conf nginx do proxy host (`/data/nginx/proxy_host/<ID>.conf`) com roteamento
   por path:

   ```nginx
   server {
     server_name <N>.praxis.<IP>.sslip.io;
     listen 80;
     include conf.d/include/block-exploits.conf;

     location /api/    { proxy_pass http://app-backend-${PR}:8000; proxy_set_header Host $host; ... }
     location /health  { proxy_pass http://app-backend-${PR}:8000; }
     location /        { include conf.d/include/proxy.conf; }   # SPA → frontend

     # MCP/SSE (se o projeto expõe MCP):
     location /mcp/ {
       proxy_pass http://app-mcp-${PR}:8100/;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_read_timeout 86400s;          # SSE não pode ter timeout curto
     }
     location /messages/ { ... }           # callback POST do FastMCP
   }
   ```

5. Validar e recarregar: `docker exec nginx_proxy_manager nginx -t && docker exec nginx_proxy_manager nginx -s reload`

**Cleanup** (`unregister-preview.sh` + job do PR fechado): soft-delete no NPM
(`is_deleted=1`), `docker compose ... down --remove-orphans`, `DROP DATABASE IF EXISTS
app_pr_<N>`, `docker rmi` das imagens `:pr-<N>`.

## 8. Workflow 3 — Rollback (`rollback.yml`)

`workflow_dispatch` com inputs `sha` e `service` (`both`/`backend`/`frontend`). Criar com
`write_file` em `.github/workflows/rollback.yml`:

```yaml
name: Rollback
on:
  workflow_dispatch:
    inputs:
      sha:
        description: 'SHA curto da imagem (ex.: abc1234)'
        required: true
      service:
        description: 'both | backend | frontend'
        required: true
        default: 'both'

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/<org>/<repo>/backend
  IMAGE_FRONTEND: ghcr.io/<org>/<repo>/frontend

permissions:
  contents: read
  packages: write

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # 1. verifica se a tag sha-X existe no registry
      - run: docker pull ${{ env.IMAGE_BACKEND }}:sha-${{ github.event.inputs.sha }}
        if: github.event.inputs.service != 'frontend'
      - run: docker pull ${{ env.IMAGE_FRONTEND }}:sha-${{ github.event.inputs.sha }}
        if: github.event.inputs.service != 'backend'
      # 2. re-aponta latest (rollback = reapontar a tag)
      - run: docker tag ${{ env.IMAGE_BACKEND }}:sha-${{ github.event.inputs.sha }} ${{ env.IMAGE_BACKEND }}:latest && docker push ${{ env.IMAGE_BACKEND }}:latest
        if: github.event.inputs.service != 'frontend'
      - run: docker tag ${{ env.IMAGE_FRONTEND }}:sha-${{ github.event.inputs.sha }} ${{ env.IMAGE_FRONTEND }}:latest && docker push ${{ env.IMAGE_FRONTEND }}:latest
        if: github.event.inputs.service != 'backend'
      # 3. deploy
      - uses: appleboy/ssh-action@v1
        with:
          host: <IP_DO_HOST>
          username: <usuario>
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /caminho/do/compose/no/host
            echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker compose pull
            docker compose up -d --remove-orphans
```

Como produção sempre puxa `latest`, re-apontar a tag **é** o rollback. Requer disciplina:
toda build de push gera tag `sha-<curto>`.

## 9. Checklist de replicação para um novo projeto

Em ordem; itens 1–5 são únicos (infra), 6–11 por projeto. Cada item tem critério de
verificação executável:

1. [ ] Host acessível por SSH e com Docker Compose v2 — `terminal(command="ssh host 'docker compose version'")` retorna v2.x.
2. [ ] NPM rodando em 80/443 + rede externa criada (`docker network create proxy_network`) e referenciada no compose do projeto.
3. [ ] Certificado TLS válido no NPM para o domínio wildcard (sslip.io ou próprio) — `curl -sI https://<N>.praxis.<IP>.sslip.io | head -1` responde `HTTP/2 200` ou `301`.
4. [ ] PAT classic `write:packages` criado → secret `GHCR_TOKEN` cadastrado — `gh secret list` mostra `GHCR_TOKEN` e `SSH_PRIVATE_KEY`.
5. [ ] Par ED25519 de deploy gerado → pública no `authorized_keys` → privada no secret `SSH_PRIVATE_KEY` — `ssh -i deploy_key <usuario>@<IP> 'echo ok'` responde `ok`.
6. [ ] Dockerfiles por serviço (multi-stage; frontend servindo dist estático).
7. [ ] `docker-compose.yml` de produção: imagens `ghcr.io/<org>/<repo>/<svc>:latest`, healthchecks explícitos, redes `app-net` + `proxy_network`.
8. [ ] `docker-compose.preview.yml`: container_name/image/DATABASE_URL sufixados por `${PR_NUMBER}`, healthcheck herdado desabilitado se mentir.
9. [ ] Adaptar `scripts/register-preview.sh` / `register-proxy-host.py` / `unregister-preview.sh`: trocar domínio base, nomes de container e porta frontal.
10. [ ] Workflows `ci.yml`, `preview.yml`, `rollback.yml`: trocar `<org>/<repo>`, IP do host, branch padrão (`main` vs `master`!), plataformas, caminhos de contexto dos Dockerfiles.
11. [ ] Primeiro merge na branch padrão valida o ciclo completo; abrir um PR de teste valida preview + cleanup.

## 10. Variação conhecida: preview com projeto Compose totalmente isolado (padrão Zera)

O TaskFlow injeta containers sufixados **dentro do mesmo projeto/rede** de produção
(§7.2). O Zera usa abordagem alternativa, mais isolada:

- Cada PR ganha **diretório próprio** (`/home/ubuntu/cfp-ia/previews/pr-<N>/infra/`) e
  **projeto compose próprio** (`zera_preview_<N>` — label visível em `docker inspect`).
- Redes e volumes namespaced pelo projeto → colisão zero com produção, inclusive de banco
  (Postgres próprio do preview).
- Custo: mais RAM/disco por PR (stack completa duplicada) e cleanup precisa `down -v` no
  diretório certo.

**Quando usar cada um:** banco compartilhado + sufixo (TaskFlow) para stacks leves e
muitos PRs; projeto isolado (Zera) quando o preview pode ter migrações destrutivas ou
state incompatível com produção.

## 11. Segurança

**Já embutido no padrão:**

- Bloco `permissions:` mínimo em todo workflow (menor privilégio); `pull-requests: write`
  só onde comenta.
- Segredos só via Secrets; token efêmero para push de pacotes; PAT único e escopo estreito.
- Nginx do NPM com `block-exploits.conf`, SSL forçado, logs por proxy host.
- Cleanup automático remove containers, banco e imagens de preview (superfície encolhe
  sozinha).
- Scripts do host nunca ecoam tokens (`--password-stdin`, não `-p`).

**Para endurecer em novos projetos:**

- Branch protection + required checks (indisponível no plano free para repos privados —
  alternativa: regra de time "não mergear vermelho"; ou tornar repo público).
- Ambiente `production` com reviewers aprovando o job de deploy.
- Restringir o trigger de preview a membros da org:
  `if: github.event.pull_request.head.repo.owner.id == github.repository_owner_id` —
  evita fork externo disparar deploy no seu host.
- Rotação periódica do `GHCR_TOKEN` e da chave de deploy.
- Não embutir PAT na URL do remote git
  (`https://user:token@github.com/...` — encontrado no checkout do TaskFlow no host; vaza
  para `git remote -v` e logs). Preferir credential helper.
- Endurecer o projeto compose do preview (`-p preview_<N>`) para nunca tocar containers
  de produção (ver §7.1).

## 12. Pitfalls (todos já mordidos — soluções testadas)

| Sintoma | Causa | Correção |
|---|---|---|
| Host não puxa imagem do GHCR (`denied`) | `GITHUB_TOKEN` efêmero não vale fora do Actions | PAT classic `write:packages` no secret `GHCR_TOKEN`, usado no `docker login` do host |
| Backend trava na importação (`pydantic_settings`) em container amd64 no ARM | QEMU emulation deadlock | Build com `platforms: linux/arm64`; validar com `docker exec <c> uname -m` → `aarch64` |
| Container sempre `unhealthy` mas funciona | Healthcheck da imagem aponta porta errada, ou `/sse` prende curl | Definir healthcheck no compose; teste universal `/dev/tcp/localhost:<porta>`; desabilitar o herdado |
| Preview não sobe após mudança de compose | `up -d` sem os dois `-f` | Sempre `docker compose -f docker-compose.yml -f docker-compose.preview.yml ...` |
| Preview antigo continua respondendo | Proxy host órfão no NPM | Cleanup chama `unregister-preview.sh` (soft delete) + `down --remove-orphans` |
| Porta nova inalcançável de fora | Duas camadas de firewall (nftables + Security List) | `sudo nft **insert** rule` (ordem importa!) + ingress rule no Console Oracle; ou nem abrir porta — usar NPM |
| SSE/MCP cai após ~60s | Timeout padrão de proxy | `proxy_read_timeout 86400s` + headers Upgrade/Connection no location |
| Pipeline silencioso, nada roda | Trigger na branch errada (`main` vs `master`) | Conferir `default_branch` do repo e casar nos `branches:` |
| Deploy recria container de produção errado | Rodar compose de preview no diretório de prod sem `-f` do overlay (ou vice-versa) | Padronizar comandos completos nos scripts; nunca digitar à mão; usar `-p preview_<N>` |
| Preview fica na rede certa mas 502 | Container fora da `proxy_network` ou `container_name` divergente do `forward_host` | Conferir `docker inspect <c> --format '{{json .NetworkSettings.Networks}}'` e casar nome/porta no NPM |
| Secret referenciado no workflow não existe | Secret nunca foi cadastrado (ex.: `SECRET_KEY`) | `gh secret list` e comparar com `secrets.*` usados nos workflows; cadastrar ou remover a referência |
| Deploy usa imagem amd64 legada | Script antigo ainda faz `pull --platform linux/amd64` | Remover scripts legados; build sempre `linux/arm64`; confirmar `uname -m` no container |
| Postgres sobe healthy mas banco VAZIO (dump não restaura) | **Dump em formato mais novo que o `pg_restore` do container** — ex.: dump feito com PG17 = formato `1.16`; `postgres:16` só lê até `1.15` → `pg_restore: unsupported version (1.16)`. O initdb falha silenciosamente e o container fica healthy. | Verificar formato: `head -c 9 db/*.dump` → `PGDMP 01 10` = versão `1.16`. Alinhar `postgres:17-alpine` (ou 18) EXATAMENTE à versão do dump. Recriar o volume (`docker volume rm` — só se vazio) e subir de novo |
| GHCR `403 Forbidden` no pull do host | `GHCR_TOKEN` sem `read:packages`/`write:packages` (token só com `repo`) | No padrão atual (build nativo no host) **não usa GHCR p/ pull**; se usar GHCR, PAT precisa de `write:packages` |
| Login no NPM (API) falha ou payload rejeitado | Versão NPM v2.15 tem schema estrito (`additionalProperties:false`) | Confirmar senha correta; payload exato do cert: `{provider, nice_name, domain_names, meta:{dns_challenge:false}}` — SEM `letsencrypt_agree` |
| HTTPS dá 000 / TLS falha testando via `localhost` | O cert cobre só o domínio, não `localhost` | Testar contra o domínio real resolvido (e não localhost) p/ validar TLS |
| Importante: NPM NÃO emite wildcard | Let's Encrypt no NPM é só HTTP-01 | Cada subdomínio de preview precisa do próprio cert (HTTP-01 automático) |

**Dívidas observadas ao auditar o TaskFlow (evitar ao replicar):**

- Checkout no host stale vs GitHub (workflows locais triggam branch errada) — consolidar
  num único checkout canônico + `git pull` no deploy.
- `scripts/deploy.sh` legado ainda puxa `--platform linux/amd64` (obsoleto desde a
  migração para arm64).
- Senha do Postgres de preview = senha de produção; defaults fracos no MCP preview
  (`mcp-preview-secret-key`) — aceitável em ambiente efêmero, ruim se o preview viver
  dias.
- Passo `npm ci && npm run build` nativo no preview.yml antes do build Docker é
  redundante hoje (o Dockerfile reconstrói no stage builder) — manter só como smoke test
  de build.

## 14. PADRÃO ATUAL: Build nativo no host (sem GHCR/QEMU) — validado no Artemis (22/08/2026)

**Motivação.** Build no GitHub runner com QEMU (`setup-qemu-action` + `build-push` arm64)
é lento, pode travar (ex.: `pydantic-settings` em emulação) e obriga todo host a puxar
imagem privada do GHCR (exige PAT com `read:packages`/`write:packages` — sem isso o host
recebe `403 Forbidden`). Como o **host Oracle é nativo ARM64**, buildar ali é o caminho
mais robusto: **o host compila nativamente, SEM QEMU e SEM registry do meio**.

**Arquitetura do padrão (novo):**

```
GITHUB (qualidade apenas)                  ORACLE HOST (ARM64, ex.: 129.146.163.107)
  ci.yml (push main)            ──SCP──►   /home/ubuntu/selfhost/<repo>/
    lint (informativo)                     └─ docker compose build   ← NATIVO, sem QEMU
    build frontend (valida)                       │                 ──┴──
    deploy:                                                   docker compose up -d
      scp-action (envia compose+scripts+src)                    (postgres restaura DUP na 1ª subida)
      ssh-action: build && up -d                                NPM: <sub>.idconsultoria.ai → frontend:80

  preview.yml (PR)                 ──SCP–SSH──►  seed banco de TESTE (app_pr_<N>)
    build+up stack autônoma por PR                              register-preview (NPM, HTTP-01)
    comentário com URL https://<N>.dominio
    fechou → cleanup: down + DROP DB + unregister NPM

  rollback.yml (workflow_dispatch, input sha)
    checkout@v4 ref:sha ──SCP──► rebuild local no host
```

**Princípios do padrão atual:**

1. **GitHub faz SÓ qualidade.** Lint + build de teste do frontend (`npm run build`).
   Zero imagem construída no runner.
2. **Deploy = SCP + SSH.** `appleboy/scp-action@v0.1.7` envia os arquivos do compose
   (`docker-compose*.yml`, `docker/`, `scripts/`, `db/`, `src/`, `backend/`, arquivos de build),
   depois `appleboy/ssh-action@v1` roda `docker compose build` **nativo** + `up -d`.
3. **Sem GHCR_TOKEN.** Como o host compila local, não precisa pagar pull de imagem privada.
   O único secret obrigatório é **`SSH_PRIVATE_KEY`**. (Se o repo for privado e o host precisar
   clonar, use SCP, nunca embutir PAT na URL do git.)
4. **`docker-compose.yml` usa `build:` em vez de `image: ghcr.io/...`** — tag local
   (`image: <app>-backend:${IMAGE_TAG:-latest}`). O mesmo vale pro preview com `IMAGE_TAG=pr-<N>`.
5. **`.env` do host** (POSTGRES_PASSWORD, API keys) criado na 1ª subida pelo workflow com
   `openssl rand -hex 24`, **não** é secret do Actions. Modelo em `.env.example` (commitá-lo
   exige `!.env.example` no `.gitignore`, que tem `*.env*`).
6. **Versionamento/rollback sem GHCR:** rollback = `checkout@v4 ref:sha` + SCP + rebuild local.

**Docker compose (produção) — pontos-chave:**

```yaml
services:
  db:
    image: postgres:17-alpine          # ⚠ versão precisa ser EXATAMENTE a do dump — ver pitfall
    container_name: <app>-db
    volumes:
      - ./db/init/01-restore.sh:/docker-entrypoint-initdb.d/01-restore.sh:ro
      - ./db/<app>.dump:/docker-entrypoint-initdb.d/<app>.dump:ro
      - pgdata:/var/lib/postgresql/data
    healthcheck: pg_isready
  backend:
    build: { context: ., dockerfile: docker/backend.Dockerfile }
    image: <app>-backend:${IMAGE_TAG:-latest}
    depends_on: { db: { condition: service_healthy } }
  frontend:
    build: { context: ., dockerfile: docker/frontend.Dockerfile }
    image: <app>-frontend:${IMAGE_TAG:-latest}
    environment: { BACKEND_HOST: backend }   # nginx proxy /api → backend
    networks: [app-net, proxy_network]
networks:
  app-net: { driver: bridge }
  proxy_network: { external: true }          # rede compartilhada do NPM — NÃO criar
```

**Frontend nginx que proxeia `/api` ao backend — configurável p/ preview (envsubst nativo):**
Use `/etc/nginx/templates/default.conf.template` (imagem `nginx:1.27-alpine` renderiza com
envsubst **apenas das envvars setadas** — `$host`, `$uri` etc. ficam intactos). Assim o MESMO
Dockerfile serve produção (`BACKEND_HOST=backend`) e preview (`BACKEND_HOST=<app>-backend-<N>`).

**Dockerfile frontend (multi-stage):**
```dockerfile
FROM node:22-alpine AS builder
COPY package*.json ./; RUN npm ci; COPY . .; RUN npm run build
FROM nginx:1.27-alpine AS runner
RUN rm -f /etc/nginx/conf.d/default.conf && mkdir -p /etc/nginx/templates
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /build/dist /usr/share/nginx/html
```
`nginx.conf.template`:
```nginx
location /api/ { proxy_pass http://${BACKEND_HOST}:8000; proxy_buffering off; proxy_read_timeout 300s; }
location = /health { proxy_pass http://${BACKEND_HOST}:8000/api/health; }
location / { try_files $uri $uri/ /index.html; }
```

**Preview (stack AUTÔNOMA por PR, não overlay):** ⚠ não fazer `-f docker-compose.yml -f docker-compose.preview.yml`
como overlay, porque sob outro projeto isso **recria o `db` de produção**. A stack de preview usa
o **postgres de produção** (container `<app>-db`, rede externa `<app>_app-net`) mas com database
dedicada `<app>_pr_<N>` e containers sufixados `-<N>`:
```yaml
services:
  backend:
    build: { context: ., dockerfile: docker/backend.Dockerfile }
    image: <app>-backend:${IMAGE_TAG:-pr-${PR_NUMBER}}
    container_name: <app>-backend-${PR_NUMBER}
    environment: { ARTEMISHUB_DB_URL: postgresql://...@<app>-db:5432/<app>_pr_${PR_NUMBER} }
    networks: [<app>_app-net, proxy_network]   # externas
  frontend:
    image: <app>-frontend:pr-${PR_NUMBER}
    container_name: <app>-frontend-${PR_NUMBER}
    environment: { BACKEND_HOST: <app>-backend-${PR_NUMBER} }
    networks: [<app>_app-net, proxy_network]
networks:
  <app>_app-net: { external: true }
  proxy_network: { external: true }
```

**Seeds no banco (dump):** `seed_preview.sh` cria `<app>_pr_<N>` no postgres de produção e
`pg_restore` do dump (via `docker cp` p/ dentro do container). Rotina de cleanup: `down`,
`DROP DATABASE IF EXISTS <app>_pr_<N> WITH (FORCE)`, `unregister-preview`.

**Registrar preview no NPM via API (novo — mais confiável que INSERT no SQLite):**
Autentica `POST /api/tokens` (identity/secret), depois:
- **cert por PR:** HTTP-01 (Let's Encrypt NÃO emite wildcard) — `POST /api/nginx/certificates`
  payload EXATO: `{"provider":"letsencrypt","nice_name":"<sub>.dominio","domain_names":["<sub>.dominio"],"meta":{"dns_challenge":false}}`
  (schema do NPM **não aceita** `letsencrypt_agree` nem campos extras — `additionalProperties:false`).
- **proxy host:** `POST /api/nginx/proxy-hosts` com `certificate_id`, `ssl_forced:true`,
  `forward_host: <app>-frontend-<N>`, `http2_support:true`, `block_exploits:true`.
- Cleanup: `DELETE /api/nginx/proxy-hosts/<id>` (e opcional rmi local).

**Certificado de produção no NPM:** mesmo fluxo API. `POST /api/tokens` com as credenciais do
admin (`user` table no `/data/database.sqlite`); emitir cert apontando p/ domínio que **já**
resolve pro host (HTTP-01 valida pela porta 80). Depois `PUT /api/nginx/proxy-hosts/<id>` com
`certificate_id` + `ssl_forced:1`, ou criar de novo por POST.

## 13. Verificação (provar que o padrão funcionou)

1. **CI:** merge de teste na branch padrão → `ci.yml` verde até o job `deploy` (conferir
   em Actions → run mais recente).
2. **Arquitetura nativa:** `terminal(command="ssh <usuario>@<IP> 'docker exec <container-backend> uname -m'")` → `aarch64`.
3. **Produção no ar:** `terminal(command="curl -sI https://<sub>.praxis.<IP>.sslip.io | head -1")` responde sem erro TLS.
4. **Preview:** abrir um PR de teste (mudança qualquer) → comentário `Preview Deployed`
   com URL responde; abrir a URL e exercitar `/api` e `/health`.
5. **Cleanup:** fechar o PR → `docker ps` não mostra `*-pr-<N>`; `docker exec <db> psql -U <user> -c "\l"` não lista `app_pr_<N>`; NPM sem proxy host órfão.
6. **Rollback:** disparar `rollback.yml` com um SHA anterior → produção volta a servir a
   versão antiga (validar por um healthcheck/versão exposta).