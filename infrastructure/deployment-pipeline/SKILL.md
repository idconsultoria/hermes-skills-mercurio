---
name: deployment-pipeline
description: "CI/CD for Docker apps — GitHub Actions, ghcr.io registry, SSH deploy to bare metal.

Load this skill for automated Docker deployment pipelines. Covers GitHub Actions workflow design, ghcr.io registry authentication, Docker tag strategy, SSH deploy key setup for bare metal hosts, database migration management, and common CI/CD pitfalls with recovery patterns."

Load this skill for automated Docker deployment pipelines. Covers GitHub Actions workflow design, ghcr.io registry authentication, Docker tag strategy, SSH deploy key setup for bare metal hosts, database migration management, and common CI/CD pitfalls with recovery patterns."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [CI/CD, GitHub-Actions, Docker, ghcr.io, Deploy, SSH, Infrastructure]
    related_skills: [github-pr-workflow, github-auth, oracle-host-access]
type: Reference
timestamp: 2026-06-12T02:23:22Z
---

# Deployment Pipeline — Docker + GitHub Actions + SSH Deploy

Class-level guide for setting up a CI/CD pipeline for containerized applications.
Covers the full lifecycle: PR merge → tests → Docker build → push to registry → SSH deploy.

---

## Architecture Overview

```
PR merge → master
     │
     ├── Test suite (lint, unit, integration)
     │
     ├── Build & Push (ON PUSH to master, not PR)
     │   ├── ghcr.io/<owner>/<repo>/backend:sha-<commit>
     │   ├── ghcr.io/<owner>/<repo>/backend:latest
     │   ├── ghcr.io/<owner>/<repo>/frontend:sha-<commit>
     │   └── ghcr.io/<owner>/<repo>/frontend:latest
     │
     └── Deploy (SSH → server)
         ├── cd /home/ubuntu/selfhost/<app>/
         ├── docker compose pull
         ├── docker compose up -d --remove-orphans
         └── docker image prune -f --filter "until=24h"
```

### Key decisions

| Decision | Recommended | Why |
|----------|-------------|-----|
| **Registry** | ghcr.io (GitHub Container Registry) | Same auth as GitHub via GITHUB_TOKEN. No extra account. No rate limits for private images. |
| **Tag strategy** | `sha-<commit>` + `latest` | sha-* is immutable (rollback target). latest is a convenience pointer for the compose file. |
| **Pipeline shape** | Single pipeline, atomic deploy | For monorepo MVP. Split when >1 dev or different release cadence. |
| **Pipeline naming** | Match scope: `CI` = only tests/lint; `CI/CD` = tests + build + deploy | A pipeline named `TaskFlow CI` that also builds and deploys is misleading. Rename to `CI/CD` when CD jobs are present. |
| **Auth (push)** | GITHUB_TOKEN (auto-generated) | Scoped by workflow `permissions:` block — set `packages: write`. |
| **Auth (pull on server)** | GHCR_TOKEN (fine-grained PAT) | GITHUB_TOKEN is ephemeral per-run and not available on the remote server. See auth section below. |
| **Architecture** | Single-arch arm64 (server-aligned) | If the server is ARM-only (Oracle Ampere), build only `linux/arm64` — faster CI, no unnecessary amd64 layer. Use multi-arch (`amd64+arm64`) only if deploying to both archs. See "Platform Strategy" below. |

---

## Workflow Structure (GitHub Actions)

### Job dependency graph

```
lint ──→ test-unit ──→ build-and-push ──→ deploy
         test-integration ─┘      (only on push to master)
```

- `test-unit` and `test-integration` run on EVERY push/PR
- `build-and-push` and `deploy` run ONLY on push to the default branch (not PRs)
- `build-and-push` needs: `[lint, test-unit, test-integration]`
- `deploy` needs: `build-and-push`

### Branch trigger alignment

**PITFALL:** The CI trigger branch must match the repo's actual default branch.
The YAML says `branches: [master]` but if the repo default is `main`, the CI never fires.

```yaml
on:
  push:
    branches: [master]      # ← must match repo default
  pull_request:
    branches: [master]      # ← must match repo default
```

To find the actual default branch:
```bash
git remote show origin | grep "HEAD branch"
# or
gh repo view --json defaultBranch
```

### Env vars pattern

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/<owner>/<repo>/backend
  IMAGE_FRONTEND: ghcr.io/<owner>/<repo>/frontend
```

These are reused in the build step. Avoid hardcoding image names per step.

---

## Platform Strategy — build for the server, not for all

**Why:** Many VPS providers use ARM CPUs (Oracle Ampere A1, AWS Graviton, Azure Ampere). A single-arch amd64 image won't run natively on these servers — it falls back to QEMU emulation, which is slow and can BREAK certain workloads.

### Preferred: single-arch arm64 (ARM-only server)

If your deploy target is ARM-only, build **only** `linux/arm64`. Faster CI (one arch), same native performance:

```yaml
- name: Set up QEMU for arm64
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push backend image
  uses: docker/build-push-action@v6
  with:
    push: true
    platforms: linux/arm64                    # single arch — ~3min vs ~8min multi-arch
    tags: |
      ${{ env.IMAGE }}:sha-${{ steps.sha.outputs.sha }}
      ${{ env.IMAGE }}:latest
```

### Multi-arch (both architectures)

Only needed when deploying to both x86_64 AND ARM targets (e.g., dev on x86, prod on ARM):

```yaml
platforms: linux/amd64,linux/arm64
```

Buildx creates a manifest list — `docker pull` auto-selects the correct arch on each target.

**🐛 QEMU emulation kills Python extensions:** pydantic-settings (Python 3.12) hangs indefinitely when imported under `qemu-x86_64`. The `pydantic.plugin._loader` module calls `importlib.metadata.distributions()` which deadlocks inside QEMU's threading model. Symptom: the container logs "Running migrations..." and freezes — `alembic upgrade head` never completes, the healthcheck fails, and the container stays in `(health: starting)` forever.

**Fix:** Build for BOTH architectures so the server runs natively without emulation.

### docker/setup-qemu-action (for emulated arm64 build)

GitHub Actions runners are amd64. To build arm64 images from an amd64 runner, you need QEMU binfmt support:

```yaml
- name: Set up QEMU for multi-arch
  uses: docker/setup-qemu-action@v3
```

This step goes BEFORE `docker/setup-buildx-action@v3`.

### platforms parameter

Add `platforms: linux/amd64,linux/arm64` to both `docker/build-push-action@v6` steps:

```yaml
- name: Build and push backend image
  uses: docker/build-push-action@v6
  with:
    context: ./backend
    file: ./backend/Dockerfile
    push: true
    platforms: linux/amd64,linux/arm64      # ← multi-arch
    tags: |
      ${{ env.IMAGE_BACKEND }}:sha-${{ steps.sha.outputs.sha }}
      ${{ env.IMAGE_BACKEND }}:latest
```

**Trade-off:** Arm64 builds under QEMU are ~2-3x slower than native amd64. The backend took ~3min single-arch vs ~8min multi-arch in practice. The trade-off is worth it for native ARM performance on the server.

### docker-compose.yml — NO platform pin

With multi-arch images in the registry, `docker pull` auto-selects the correct architecture for the host. Do NOT add `platform: linux/amd64` — that would force amd64 on ARM and reintroduce the QEMU problem.

### Fallback: single-arch amd64 + QEMU on server

If multi-arch is not viable (CI time constraints, complex build matrix), you can run amd64 images on ARM servers via QEMU:

1. Install QEMU binfmt on the server (one-time):
   ```bash
   docker run --rm --privileged tonistiigi/binfmt --install all
   ```

2. Add `platform: linux/amd64` to docker-compose services:
   ```yaml
   services:
     backend:
       image: ghcr.io/.../backend:latest
       platform: linux/amd64           # ← force amd64 under QEMU
   ```

**⚠️ Fallback risks:** Python C/Rust extensions may randomly deadlock under QEMU (pydantic-settings, orjson, uvloop, numpy, etc.). Only use this for light workloads where stability isn't critical.

### Workflow permissions

**REQUIRED:** The default GITHUB_TOKEN does NOT have `packages:write` scope.
Add this at workflow root level (under `env:`):

```yaml
permissions:
  contents: read
  packages: write
```

Without this, `docker/build-push-action@v6` fails with `denied: installation not allowed to Create organization package`.

### ghcr.io auth (push — in CI)

Uses the auto-generated `GITHUB_TOKEN` — no extra secrets needed:

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ${{ env.REGISTRY }}
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### ghcr.io auth (pull — on deploy server)

**CRITICAL PITFALL:** ghcr.io images are PRIVATE by default (even if the repo is public).
The deploy server needs to authenticate to pull them.

**🐛 GITHUB_TOKEN won't work on the remote server:** The `${{ secrets.GITHUB_TOKEN }}` is substituted
by the GitHub Actions runner BEFORE the SSH command is sent. In the `appleboy/ssh-action` script block,
the substitution happens in the CI runner, so it SHOULD work in theory. But in practice, GITHUB_TOKEN
is short-lived (per-run) and may not have the right scopes for pulling private packages.

**🐛 PAT scope trap:** A classic personal PAT with `repo` scope does NOT grant `read:packages`.
Even though `repo` covers private repos, GHCR packages are a separate permission domain:
```json
Scopes needed: repo, read:packages    ✓
Scopes insufficient: repo             ✗ → 403: "need read:packages scope"
```

| Token | Scope | Can push? | Can pull on server? |
|-------|-------|-----------|---------------------|
| `GITHUB_TOKEN` | Per-workflow, includes `packages:write` if permissions set | ✅ Always | ❌ Not available on server |
| Classic PAT with `repo` | `repo` | ✅ | ❌ Missing `read:packages` |
| Classic PAT with `repo, write:packages` | `repo, write:packages` | ✅ | ✅ (write implies read) |
| Fine-grained PAT | `Read: packages` on specific repo | ❌ | ✅ |

**Recommended approach — dedicated GHCR_TOKEN secret:**

1. Create a classic PAT with scopes `repo, write:packages` (or fine-grained with `Read: packages`)
2. Add it as a GitHub Actions secret: `GHCR_TOKEN`
3. Use it in the deploy step:

```yaml
- name: Deploy via SSH
  uses: appleboy/ssh-action@v1
  with:
    host: <server-ip>
    username: ubuntu
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /home/ubuntu/selfhost/<app>
      echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      docker compose pull
      docker compose up -d --remove-orphans
```

The `echo "${{ secrets.GHCR_TOKEN }}"` is substituted by the Actions runner before the SSH command
is dispatched — the server never sees the raw token, only the authenticated `docker login` result.

**Adding the secret via CLI:**
```bash
# Using gh
echo "<pat-value>" | gh secret set GHCR_TOKEN --repo <owner>/<repo> -a actions

# Verify
gh secret list -R <owner>/<repo>
```

**Alternative — Option A (GITHUB_TOKEN in deploy script):**

```yaml
- name: Deploy via SSH
  uses: appleboy/ssh-action@v1
  with:
    host: <server-ip>
    username: ubuntu
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /home/ubuntu/selfhost/<app>
      echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      docker compose pull
      docker compose up -d --remove-orphans
```

**Alternative — Option B (public packages):**
GitHub UI → repo → Packages → (click package) → Package settings → Change visibility → Public

| Approach | Pro | Con |
|----------|-----|-----|
| GHCR_TOKEN secret | Explicit, long-lived, scoped to packages | Requires creating and managing a PAT |
| GITHUB_TOKEN inline | No extra secrets | Token is ephemeral, unstable across Action versions |
| Public packages | Zero config on deploy | Anyone can pull your images |

### Tag generation

Two tags per image: immutable `sha-<commit>` + mutable `latest`:

```yaml
- name: Generate short SHA
  id: sha
  run: echo "sha=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"

- name: Build and push backend
  uses: docker/build-push-action@v6
  with:
    context: ./backend
    file: ./backend/Dockerfile
    push: true
    tags: |
      ${{ env.IMAGE_BACKEND }}:sha-${{ steps.sha.outputs.sha }}
      ${{ env.IMAGE_BACKEND }}:latest
```

**Rollback:** On the server, edit `docker-compose.yml` to point `image:` at a specific `sha-` tag, then `docker compose up -d`.

---

## Deploy Job (SSH)

### Inline commands, not remote scripts

**PITFALL:** After switching to image-based deployment, the deploy script DOES NOT exist on the server (the repo is no longer cloned there). The SSH action must contain the deploy commands inline:

```yaml
- name: Deploy via SSH
  uses: appleboy/ssh-action@v1
  with:
    host: <server-ip>
    username: ubuntu
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    fingerprint: ${{ secrets.SSH_KNOWN_HOSTS }}
    script: |
      cd /home/ubuntu/selfhost/<app>
      echo "[deploy] Pulling new images..."
      docker compose pull
      echo "[deploy] Recreating containers..."
      docker compose up -d --remove-orphans
      echo "[deploy] Pruning old images..."
      docker image prune -f --filter "until=24h" 2>/dev/null || true
```

### GitHub secrets needed

| Secret | Source |
|--------|--------|
| `SSH_PRIVATE_KEY` | Deploy key (ed25519, no passphrase) generated on the server |
| `SSH_KNOWN_HOSTS` | `ssh-keyscan <server-ip>` output |

## Rollback Workflow — Manual Deploy to Specific SHA

A workflow_dispatch pipeline that allows rolling back to a previously-deployed SHA. This is a **safety net** — not a replacement for proper CI/CD, but essential when a deploy breaks production and you need to revert fast.

**When to use:** Production deploy fails (migration error, runtime crash, data corruption) and you need the previous version running in <5 min.

**Key design decisions:**

| Decision | Why |
|----------|-----|
| **Separate workflow file** (`rollback.yml`) | Keeps the main CI/CD clean. Rollback is an emergency action, not part of normal flow. |
| **workflow_dispatch only** (no automatic trigger) | Rollback should be a conscious manual decision, never automated. |
| **Required input: SHA** | The immutable `sha-<commit>` tag from the CI build step. Never `latest` (mutable, can drift). |
| **Optional input: service** | `backend`, `frontend`, or `both`. Allows partial rollback if only one service is broken. |
| **Re-tags `:latest`** | After verifying the SHA exists in the registry, re-tags it as `latest` so the server's compose file (which points to `:latest`) picks it up. |
| **Redeploy via SSH** | Same `docker compose pull && up -d` as normal deploy. Zero config changes needed on the server. |

### Workflow template

```yaml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      sha:
        description: 'SHA do commit para rollback (ex: abc1234)'
        required: true
        type: string
      service:
        description: 'Serviço (backend, frontend, both)'
        required: true
        default: both
        type: choice
        options: [both, backend, frontend]

jobs:
  rollback:
    name: Rollback to sha-${{ inputs.sha }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Verify SHA exists and retag as latest
        run: |
          SHA="${{ inputs.sha }}"
          if [ "${{ inputs.service }}" = "backend" ] || [ "${{ inputs.service }}" = "both" ]; then
            docker pull ghcr.io/<owner>/<repo>/backend:sha-${SHA}
            docker tag ghcr.io/<owner>/<repo>/backend:sha-${SHA} ghcr.io/<owner>/<repo>/backend:latest
            docker push ghcr.io/<owner>/<repo>/backend:latest
          fi
          # same for frontend

      - name: Deploy rollback via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: <server-ip>
          username: ubuntu
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/ubuntu/selfhost/<app>
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f --filter "until=24h" 2>/dev/null || true
```

### Pre-requisites for rollback to work

- [ ] CI builds produce `sha-<commit>` tags (not just `latest`)
- [ ] GHCR_TOKEN or GITHUB_TOKEN has `packages:write` scope (to push the re-tagged `:latest`)
- [ ] Server has `GHCR_TOKEN` configured (see ghcr.io auth section)
- [ ] Team knows the workflow exists — document it in the project README

### Rollback vs revert

| Action | What it does | When to use |
|--------|-------------|-------------|
| **Rollback** (this workflow) | Re-deploys `:latest` to a previous SHA | Emergency: fix production first, investigate second |
| **Revert PR** | Creates a new commit that undoes the changes | After stabilization: clean up the codebase, not just the deployment |

### Deploy key setup (one-time on server)

```bash
# Generate key
ssh-keygen -t ed25519 -f ~/.ssh/deploy-<app> -N ""

# Add public key to authorized_keys
cat ~/.ssh/deploy-<app>.pub >> ~/.ssh/authorized_keys

# Add private key to GitHub:
#   Settings → Secrets → Actions → SSH_PRIVATE_KEY
#   Settings → Deploy keys → Add deploy key (paste public key)
```

### If Hermes runs in Docker ON the same server

When the CI/CD agent (Hermes) runs inside a Docker container on the SAME Oracle server, SSH via public IP fails (hairpin NAT). Use the Docker bridge gateway:

```bash
# Discover gateway
ip route | grep default

# Typical: 172.17.0.1 (default bridge) or 172.19.0.1 (custom compose network)

# SSH config at /opt/data/.ssh/config:
cat > /opt/data/.ssh/config << 'EOF'
Host oracle
  HostName 172.19.0.1
  User ubuntu
  IdentityFile /opt/data/home/.ssh/id_rsa_oracle
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
EOF
```

Then SSH as `ssh oracle 'command'` instead of the public IP.

---

## docker-compose with Image References

### Before (local build)

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
```

### After (pre-built image)

```yaml
services:
  backend:
    image: ghcr.io/<owner>/<repo>/backend:latest
```

**Impact:** The server no longer needs the repo checked out — only needs:
- `docker-compose.yml`
- `.env`
- `nginx/nginx.conf` (or other static config files that bind-mount)
- Persistent volumes (`./data/`, `pgdata`, `redisdata`)

### First deploy on the server

```bash
# One-time setup
mkdir -p /home/ubuntu/selfhost/<app>/data
# Copy compose, .env, nginx.conf from repo

# Enable GitHub Actions runner to access
# Add deploy SSH key (see above)

# First manual deploy
docker compose pull
docker compose up -d
```

---

## Database Migrations in CI/CD

### Strategy: auto-migrate on startup

The backend Docker entrypoint runs migrations before the app starts:

```bash
#!/bin/sh
set -e
alembic upgrade head    # ← runs before uvicorn
exec "$@"
```

This means:
- Migrations always run before new code serves requests
- Healthcheck catches failures (container marked unhealthy if migration fails)
- Rollback: deploy old image → old code + old schema (downgrade manually for schema reversions)

### CI validation

Add a migration validation step that runs against a real PostgreSQL (not SQLite):

```yaml
- name: Validate migrations
  run: |
    # Assumes postgres service container is running
    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/testdb" \
    alembic upgrade head
```

**Why separate from tests:** SQLite doesn't support `ALTER COLUMN`, `DROP COLUMN`, or `CREATE INDEX CONCURRENTLY`. A migration that works on SQLite can break on PostgreSQL.

### Migration safety rules

1. **Every migration must be reversible** — always implement `downgrade()`
2. **Breaking changes in 3 phases:**
   - Phase 1: `ALTER TABLE ADD COLUMN` (compatible with old code) → deploy
   - Phase 2: new code uses the column → deploy
   - Phase 3: `DROP COLUMN` (if removing) → deploy
3. **Rollback script** on the server for manual intervention:

```bash
#!/bin/bash
case "${1:-}" in
    up)      docker compose exec -T backend alembic upgrade head ;;
    down)    docker compose exec -T backend alembic downgrade -1 ;;
    history) docker compose exec -T backend alembic history ;;
    current) docker compose exec -T backend alembic current ;;
esac
```

---

## Server Setup Checklist (one-time)

| Step | Command / Action |
|------|-----------------|
| Create app dir | `mkdir -p /home/ubuntu/selfhost/<app>/data` |
| Install Docker | `curl -fsSL https://get.docker.com | sh` |
| Verify Compose | `docker compose version` |
| Create Docker network | `docker network create proxy_network` (if needed by nginx) |
| Generate deploy key | `ssh-keygen -t ed25519 -f ~/.ssh/deploy-<app> -N ""` |
| Authorize key | `cat ~/.ssh/deploy-<app>.pub >> ~/.ssh/authorized_keys` |
| Copy config files | `docker-compose.yml`, `.env`, `nginx/nginx.conf` |
| First deploy | `docker compose pull && docker compose up -d` |

---

## Common Pitfalls

### CI never triggers
**Cause:** Trigger branch (`main`) doesn't match repo default (`master`).
**Fix:** Align `branches:` in `on:` with `git remote show origin | grep HEAD`.

### Deploy job references script that doesn't exist on server
**Cause:** CI calls `bash scripts/deploy.sh` via SSH, but the repo isn't cloned on the server.
**Fix:** Inline the deploy commands in the SSH action (see "Deploy Job" above).

### ghcr.io push fails
**Cause:** GITHUB_TOKEN scope missing `packages:write` or first push to a new package.
**Fix:** Add `permissions: { contents: read, packages: write }` at workflow root level.
**Check:** `gh repo view --json name` shows the repo exists.

### ghcr.io pull fails on deploy server ("unauthorized")
**Cause:** ghcr.io images are private by default. The server needs auth to pull.
**Fix:** Add `docker login ghcr.io` in the deploy script (see "ghcr.io auth" section above).

### SSH host key fingerprint mismatch
**Cause:** appleboy/ssh-action `fingerprint` param receives wrong format or the key rotates.
**Fix:** Remove the `fingerprint` parameter entirely — the action defaults to `StrictHostKeyChecking=accept-new`, which adds the host key on first connection. Or get the correct SHA256 fingerprint:
```bash
ssh-keyscan <server-ip> 2>/dev/null | ssh-keygen -lf -
# Use the ED25519 key: SHA256:xxx
```

### Test files not found by CI
**Cause:** CI runs `working-directory: ./backend` but `pytest tests/unit` expects `backend/tests/unit/`. If the tests are at the repo root (`./tests/`), pytest can't find them from `backend/`.
**Fix:** Use relative paths: `pytest ../tests/unit` instead of `pytest tests/unit`. Or don't set `working-directory` for test steps and use absolute or `cd` commands.

### Pre-existing lint blocks build-and-push
**Cause:** The codebase has existing ruff/pylint errors. Since `build-and-push needs: [lint]`, a broken lint job blocks the entire pipeline — even if lint failures are pre-existing and unrelated to the PR.
**Fix:** Either:
- Remove `lint` from `needs:` list for `build-and-push` (tests become the deploy gate)
- Set `continue-on-error: true` on the lint job so it runs but doesn't block

```yaml
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    continue-on-error: true   # ← lint is advisory, not a gate
```

**Reasoning:** Pre-existing lint debt shouldn't block production deploys. Fix lint issues separately and promote to gate once clean.

### Docker compose up -d doesn't recreate containers
**Cause:** `docker compose up -d` only recreates containers if the compose configuration changed or the image was updated. If the `latest` tag points to the same image reference (e.g., both point to the same SHA), nothing happens.
**Fix:** Always run `docker compose pull` BEFORE `docker compose up -d`. The pull fetches the new `latest` image digest, and `up -d` detects the change and recreates.

### Docker compose fails after deploy
**Cause:** Old volumes or container state conflicts.
**Fix:** `docker compose down -v` (DATA LOSS — only if volumes are disposable), then `docker compose up -d`.

### Migration fails, container unhealthy
**Cause:** Migration takes longer than Docker healthcheck `start_period`.
**Fix:** Increase `HEALTHCHECK --start-period=60s` in the Dockerfile.

### npm install crashes under QEMU during Docker build (frontend arm64)

**Symptom:** The GitHub Actions build log shows:
```
#14 [builder 4/6] RUN npm install
#14 14.44 qemu: uncaught target signal 4 (Illegal instruction) - core dumped
```

The build hangs indefinitely or exits with signal 4. This is NOT a timeout — it's a native-code crash inside QEMU emulation. Node.js native modules (esbuild, sharp, node-gyp compiled addons, etc.) use CPU instructions that QEMU cannot correctly emulate under npm's worker-thread spawning pattern.

**Root cause:** When building `linux/arm64` images on an amd64 GitHub Actions runner, Docker uses QEMU user-mode emulation (`qemu-aarch64`). `npm install` spawns child processes for native module compilation and pre-built binary extraction. Under QEMU, some of these processes hit illegal instruction traps and crash.

**Fix — three options:**

| Option | Complexity | Reliability |
|--------|-----------|-------------|
| **Split build (recommended)** | Medium | ✅ No QEMU involved in frontend build |
| **Switch to node:22-slim** | Low | ⚠️ May still fail with native modules |
| **Use buildx --cache-from** | Medium | ⚠️ QEMU still runs, just faster |

**Option A (recommended) — Build frontend natively, Docker copies dist:**

Separate the frontend build into two CI steps: (1) native amd64 npm install + build, (2) Docker image build that skips npm and just copies pre-built artifacts.

Workflow change:
```yaml
# Step 1: Build frontend natively on the runner (amd64, no QEMU)
- name: Build frontend assets (native, no QEMU)
  run: |
    cd frontend
    npm ci
    npm run build
  shell: bash

# Step 2: Build arm64 Docker image (npm install SKIPPED because dist/ exists)
- name: Build and push frontend image (arm64)
  uses: docker/build-push-action@v6
  with:
    context: ./frontend
    file: ./frontend/Dockerfile
    push: true
    platforms: linux/arm64
    tags: ghcr.io/org/repo/frontend:pr-${{ github.event.number }}
```

Dockerfile change — detect pre-built dist/ and skip npm:
```dockerfile
FROM node:22-slim AS builder
WORKDIR /build

# Copy pre-built dist first (avoids QEMU npm install when built natively)
COPY dist /build/dist

# Copy source and package files
COPY package.json package-lock.json* tsconfig.json vite.config.ts index.html ./
COPY src ./src
COPY public ./public

# Install + build only if dist doesn't already exist
RUN if [ ! -f /build/dist/index.html ]; then \
      npm install && npm run build; \
    fi
```

**Option B (quick attempt) — Switch to node:22-slim:**

Change the base image from Alpine to Debian-slim. The glibc-based container handles QEMU slightly better than musl-based Alpine:
```dockerfile
FROM node:22-slim AS builder    # ← instead of node:22-alpine
```

This may fix some native modules but esbuild/sharp/etc can still crash.

**Option C (not recommended) — Cache mount for npm:**

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

The cache reduces download time but doesn't fix the QEMU crash issue.

**PITFALL:** When `npm install` crashes under QEMU, retrying the same build rarely helps — the crash is deterministic for the same package combination. The split-build approach (Option A) is the only reliable fix.

### PyTorch CUDA bloat on ARM64 — Dockerfile install order matters

**Symptom:** `docker compose build` on ARM64 (Oracle Ampere) takes 10+ minutes and installs gigabytes of `nvidia-cublas`, `nvidia-cudnn`, `cuda-toolkit`, `nvidia-cusparse`, etc. The image balloons to 8-12GB even though there's no GPU. The server has no NVIDIA hardware — these packages are dead weight.

**Root cause:** `pip install` of any library that depends on `torch>=2.4` (e.g., `omnivoice`, `whisper`, `transformers`-adjacent audio models) pulls the default PyTorch wheel, which includes CUDA runtime. On Linux, PyTorch's PyPI index defaults to the `cu128` (CUDA 12.8) build. The `--index-url https://download.pytorch.org/whl/cpu` flag must be used to get the CPU-only wheel.

But the real trap: if you install torch CPU first and then `pip install` the app lib, pip sees `torch>=X.Y` as unsatisfied (because the CPU wheel version may differ slightly or pip's resolver re-evaluates) and reinstalls the CUDA version from the default index **overwriting the CPU install**.

**Fix — three-layer Dockerfile pattern:**

```dockerfile
# LAYER 1: PyTorch CPU (ARM64, from CPU-only index)
RUN pip install --no-cache-dir \
    torch==2.4.0 \
    torchaudio==2.4.0 \
    --index-url https://download.pytorch.org/whl/cpu

# LAYER 2: Other dependencies (no torch to avoid CUDA pull)
RUN pip install --no-cache-dir \
    transformers \
    accelerate \
    pydub \
    numpy \
    soundfile \
    librosa \
    fastapi \
    "uvicorn[standard]" \
    python-multipart

# LAYER 3: App lib WITHOUT deps (torch already pinned from layer 1)
RUN pip install --no-cache-dir --no-deps omnivoice
```

**Layer 3 is critical.** `--no-deps` prevents pip from re-resolving `torch>=2.4` and pulling the CUDA wheel. The torch from Layer 1 is already on disk and satisfies the runtime import.

**Verification:**
```bash
# After build, check image size
docker images omnivoice-omnivoice-api --format "{{.Size}}"
# Expected: ~2-3GB (CPU-only torch + app deps)
# Without fix: ~8-12GB (torch + CUDA bloat)

# Check what torch packages are installed
docker run --rm omnivoice-omnivoice-api python3 -c "import torch; print(torch.__version__); print('CUDA available:', torch.cuda.is_available())"
# Expected: CUDA available: False

# Check for NVIDIA packages
docker run --rm omnivoice-omnivoice-api pip list 2>/dev/null | grep -i nvidia
# Expected: empty (no nvidia-* packages)
```

**Applicability:** This pattern applies to ANY Python ML image built for ARM64 servers — whisper, stable-diffusion, TTS models, speaker diarization, etc. If the image is CPU-only (no GPU on the server), always use `--index-url .../whl/cpu` for torch and `--no-deps` for the lib that declares torch as a dependency.

### Python app freezes on ARM server (no migrations, no HTTP)
**Cause:** The Docker image was built for `linux/amd64` and the server is `linux/arm64` (e.g., Oracle Ampere, AWS Graviton). The container runs under QEMU emulation. Python extensions compiled for amd64 (pydantic_core, orjson, uvloop, etc.) can deadlock under `qemu-x86_64`.

**Symptom:** `docker logs` shows "Running migrations..." and nothing else. `alembic upgrade head` never completes. `docker exec` with a simple Python import of `pydantic_settings` also hangs. `docker top` shows `/usr/bin/qemu-x86_64 /usr/local/bin/python` as the parent process.

**Root cause:** `pydantic.plugin._loader` calls `importlib.metadata.distributions()`, which triggers a deadlock inside QEMU's threading model. The fix is NOT about the Python code — it's about the architecture mismatch.

**Fix:** Build multi-arch images (see "Multi-Architecture Builds" section above). Then the server pulls a native arm64 image and runs without emulation.

**Diagnostic commands:**
```bash
# Check if running under QEMU
docker top <container> | grep qemu
# → /usr/bin/qemu-x86_64 ... = CONFIRMED emulation

# Check host architecture
uname -m
# → aarch64 = ARM

# Check container architecture
docker exec <container> uname -m
# → x86_64 (if under QEMU, reports the emulated arch)
```

**Workaround (not a fix):** Install QEMU binfmt on the host and add `platform: linux/amd64` to compose. This gets past the initial import but is unreliable for production use (random hangs under load).

### Coverage threshold blocks deploy after adding large features

**Cause:** A Sprint added significant new code (services, MCP tools, UI pages) but tests for the new code are sparse. The `coverage-report` job fails with e.g. `total of 74 is less than fail-under=80` — even though all test suites passed.

**Diagnosis:** Pipeline blockers after test success = coverage issue. Check the coverage report line in the workflow log. The tests themselves (283 passed, 1 xpassed) are green.

**Options:**

| Approach | When to use | Trade-off |
|----------|-------------|-----------|
| **Lower threshold** temporarily | Right after a Sprint with substantial untested code | Technical debt — record the threshold change reason in the commit message |
| **Add tests for gap areas** | When uncovered code is mission-critical (auth, payments, data integrity) | Better coverage, longer CI. Prioritize by risk |
| **Make coverage advisory** | When team prioritizes velocity over gates | Remove `--cov-fail-under`, keep `--cov-report=term` for visibility |

**PITFALL:** First reaction is often to lower the threshold. Check *why* coverage dropped — is it genuinely untestable code (CLI entrypoints, async event loops) or testable logic that was simply not covered?

### Preview comment URL — `actions/github-script` must include `script:` input

**PITFALL:** The `actions/github-script@v7` step that comments the preview URL on the PR can silently stop working. The build and deploy succeed, but the step fails with `Error: Input required and not supplied: script` because the `script:` field was accidentally removed during workflow edits.

**Symptom:** Preview works (hit the URL directly), but there's no comment on the PR. In the Actions log: `Error: Input required and not supplied: script`.

**Fix:** After any edit to the preview workflow, verify the `actions/github-script` step has its `script:` block intact. The complete pattern:

```yaml
      - name: Comment preview URL
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const number = context.payload.pull_request.number;
            const url = 'https://' + number + '.praxis.129.146.163.107.sslip.io';
            const body = '## Preview Deployed\n\n| URL | ' + url + ' |\n| Health | ' + url + '/health |\n\nAuto-destroi quando o PR for mergeado.';
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: number,
            });
            const existing = comments.find(c => c.body && c.body.includes('Preview Deployed'));
            if (existing) {
              await github.rest.issues.updateComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: existing.id,
                body: body,
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: number,
                body: body,
              });
            }
```

---

## Nginx Proxy Manager — Proxy Host Registration

When deploying PR previews (or any ephemeral environment behind NPM), you need to register a new proxy host in NPM's SQLite database **and** write the nginx config file. Updating only the SQLite DB is insufficient.

### Architecture

```
GitHub Actions runner
    │
    └── SSH into server
        │
        ├── docker compose pull + up -d (preview containers)
        │
        ├── 1. Copy NPM database from container
        ├── 2. Insert row in proxy_host table
        ├── 3. Copy database back to NPM container
        ├── 4. Write nginx config -> /data/nginx/proxy_host/{id}.conf
        └── 5. docker exec nginx -t && nginx -s reload
```

### PITFALL: SQLite DB update alone is NOT enough

NPM reads its SQLite database at startup and **writes nginx config files** to /data/nginx/proxy_host/{id}.conf. Simply `docker cp`'ing a modified database back does NOT trigger config regeneration — NPM's Node.js daemon only regenerates configs when changes come through its web API or internal event loop.

**Fix:** After inserting the DB row, write the nginx conf directly and reload:

```bash
# 1. Copy DB from NPM container
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm-edit.sqlite

# 2. Insert proxy host row via Python script (see references/npm-sqlite-schema.md)
python3 scripts/register-proxy-host.py \
  --db /tmp/npm-edit.sqlite \
  --domain "${DOMAIN}" \
  --forward-host "${BACKEND_HOST}" \
  --forward-port 8000

# 3. Copy DB back
docker cp /tmp/npm-edit.sqlite nginx_proxy_manager:/data/database.sqlite

# 4. Write nginx config with dynamic routing
#    /api/, /health, /auth/ -> backend:8000
#    / (SPA)              -> frontend:5173

# 5. Validate and reload
docker exec nginx_proxy_manager nginx -t
docker exec nginx_proxy_manager nginx -s reload
```

**The nginx conf must route API calls to the backend and the SPA to the frontend.** A naive conf that points only to the backend will return 401 on every path (including the root /). See `scripts/npm-proxy-2.conf` for the TaskFlow reference.

### PITFALL: ssl_forced=1 with certificate_id=0 blocks HTTP

When ssl_forced=1 but certificate_id=0 (no Let's Encrypt cert), NPM redirects HTTP -> HTTPS and HTTPS fails with TLS `unrecognized name` error because no matching certificate exists.

**Fix:** Set ssl_forced=0 for ephemeral preview hosts:

```python
# In the SQLite INSERT:
ssl_forced=0   # not 1!
certificate_id=0
```

### PITFALL: stale nginx config from a closed PR blocks ALL new previews

When a PR preview was deployed *before* a cleanup job existed (or the cleanup job failed), the NPM proxy host `.conf` file remains on disk inside the NPM container. On the next PR, NPM may show the new proxy host as registered with `is_deleted=0`, but `nginx -t` fails because the old `.conf` references a container (`taskflow-backend-{OLD_PR}`) that no longer exists.

**Symptom:** Preview containers spin up, database is created, register-preview script runs successfully, but the preview URL shows the NPM "Congratulations" default page (host not set up yet). The workflow log shows no error — the register script failed silently because `nginx -s reload` was never reached after `nginx -t` failed.

**Diagnosis:**
```bash
# Inside NPM container — look for configs with stale container references
docker exec nginx_proxy_manager nginx -t 2>&1
# → "host not found in upstream \"taskflow-backend-3\"" means old PR #3's config is still present

# List all configs — compare to currently running containers
docker exec nginx_proxy_manager ls /data/nginx/proxy_host/
# → 2.conf, 1.conf  (2.conf is from a closed PR)
```

**Fix:** Remove stale configs whose hostnames reference non-existent containers, then reload:
```bash
# Find and remove stale configs manually
docker exec nginx_proxy_manager rm -f /data/nginx/proxy_host/2.conf  # PR #3 config
docker exec nginx_proxy_manager nginx -t && docker exec nginx_proxy_manager nginx -s reload

# Alternatively, clean ALL proxy host configs and regenerate from NPM DB:
# (See scripts/register-npm-proxy-host.sh for regeneration)
docker exec nginx_proxy_manager rm -f /data/nginx/proxy_host/*.conf
# Then restart NPM to regenerate from its SQLite database:
docker restart nginx_proxy_manager
```

**Prevention:** The preview cleanup job (see "Preview Cleanup" section) must remove the `.conf` file from NPM's nginx directory in addition to marking `is_deleted=1` in the SQLite database. Without removing the file, `nginx -t` fails on every future reload.

### PITFALL: preview databases must exist before backend starts

If your preview architecture uses a shared PostgreSQL with per-PR databases, create the database **BEFORE** starting the backend container. The backend's entrypoint runs `alembic upgrade head` immediately on startup, which fails if the database doesn't exist.

```bash
# Add this BEFORE `docker compose up -d backend`:
docker exec taskflow-db psql -U taskflow \
  -c "CREATE DATABASE taskflow_pr_${PR_NUMBER}" 2>/dev/null || echo "DB already exists"
docker exec taskflow-db psql -U taskflow -d taskflow_pr_${PR_NUMBER} \
  -c "CREATE EXTENSION IF NOT EXISTS pgcrypto" 2>/dev/null
```

### Preview Cleanup — Auto-Destroy on PR Close

Every preview environment (containers, database, NPM entry, images) must be cleaned up when the PR closes. Otherwise orphaned resources accumulate.

**Trigger:** The workflow must listen for `closed` events. The recommended event types for preview workflows are:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, closed]
```

- `opened` — first deploy when PR is created
- `synchronize` — redeploy when the branch gets new commits
- `reopened` — redeploy if a closed PR is reopened
- `closed` — trigger cleanup (see cleanup job below)

Without the full types list, the default is only `opened` + `synchronize`, which misses cleanup on close.

**Cleanup job template:**

```yaml
  preview-cleanup:
    name: Cleanup Preview
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GHCR_TOKEN }}

      - name: Remove preview containers, DB and NPM entry
        uses: appleboy/ssh-action@v1
        with:
          host: <server-ip>
          username: ubuntu
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            set -e
            PR_NUMBER=${{ github.event.number }}
            export PR_NUMBER

            # 1. Stop and remove containers
            cd /home/ubuntu/selfhost/<app>
            docker compose -f docker-compose.yml -f docker-compose.preview.yml down --remove-orphans || true

            # 2. Drop per-PR database
            docker exec taskflow-db psql -U taskflow \
              -c "DROP DATABASE IF EXISTS taskflow_pr_${PR_NUMBER}" 2>/dev/null || true

            # 3. Unregister from Nginx Proxy Manager
            bash scripts/unregister-preview.sh || true

            # 4. Remove preview images from the server
            docker rmi ghcr.io/<owner>/<repo>/backend:pr-${PR_NUMBER} 2>/dev/null || true
            docker rmi ghcr.io/<owner>/<repo>/frontend:pr-${PR_NUMBER} 2>/dev/null || true
``````

**Cleanup checklist:**

| Resource | Cleanup | 
|----------|---------|
| Containers | `docker compose ... down --remove-orphans` |
| Database | `DROP DATABASE IF EXISTS taskflow_pr_{NUM}` |
| NPM proxy host | Script que marca `is_deleted=1` no SQLite + remove nginx conf |
| Docker images | `docker rmi :pr-{NUM}` (opcional — prune automático pode bastar) |
| GHCR images | Manual — deixar no registry, prune periódico

---

## Alembic Migration — Auto-Generation Pitfalls

### SQLite vs PostgreSQL naming differences

Alembic's `--autogenerate` compares the current database state to your SQLAlchemy models. When run against SQLite (common in dev), the autogenerated migration includes operations that make no sense for PostgreSQL:

- Drop + recreate all foreign keys (naming convention mismatch)
- Drop + recreate all indexes (naming convention mismatch)
- Drop + recreate unique constraints (SQLite uses unique=1 index, PostgreSQL uses CONSTRAINT)

**Result:** The generated upgrade() would **DROP all your PostgreSQL indexes and foreign keys**, then recreate them with different names. The downgrade() adds them back — a fragile, unnecessary operation that could corrupt production data.

**Fix:** After `--autogenerate`, review the generated file and strip out ALL operations that are not actual column/table additions. Keep only the essential DDL:

```python
def upgrade() -> None:
    op.add_column('tasks', sa.Column('google_event_id', sa.String(length=255), nullable=True))
    op.add_column('mcp_action_tokens',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))

def downgrade() -> None:
    op.drop_column('tasks', 'google_event_id')
    op.drop_column('mcp_action_tokens', 'updated_at')
```

**Signal:** If the autogenerated migration has 40+ lines of `op.drop_index` + `op.drop_constraint` + `op.create_foreign_key` and only 2 `op.add_column` lines, you're looking at SQLite noise.

### When to autogenerate vs manual

| Situation | Approach |
|-----------|----------|
| New column on existing table | Manual (simple DDL, no noise risk) |
| New table with FK relationships | Autogenerate, then strip noise |
| Rename/drop column | Manual (autogenerate can't detect) |
| Data migration (backfill) | Manual (SQL-level UPDATE) |
| Index-only change | Autogenerate (safe, dialect-portable) |
| Column type change | Manual (different syntax per dialect) |

### Migration validation in CI

Always run migrations against a real PostgreSQL (not SQLite) in CI to catch dialect-specific issues:

```yaml
- name: Validate migrations on PostgreSQL
  env:
    DATABASE_URL: postgresql+asyncpg://user:pass@localhost:5432/test
  run: alembic upgrade head
```

---

## References

See `references/` for implementation examples:
- OmniVoice selfhost on ARM64: `references/omnivoice-selfhost.md`
  (Dockerfile pattern, API endpoints, voice management, Hermes TTS config)
- Selfhost initial setup workflow: `references/selfhost-initial-setup.md`
  (pre-CI/CD: research ARM64, directory structure, Dockerfile template, SSH tunnel)
- TaskFlow real implementation: `references/taskflow-cicd-example.md`
- Full CI workflow with multi-arch: `references/multi-arch-ci-workflow.yml`
- NPM SQLite schema (proxy_host table columns): `references/npm-sqlite-schema.md`
