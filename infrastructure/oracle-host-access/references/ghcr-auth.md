# GHCR Authentication — Oracle Host

**Context:** The Oracle Ampere (ARM64) server pulls Docker images from `ghcr.io/gustavomello9600/taskflow-mvp/` for automated deployment.

## Token Setup

| Property | Value |
|----------|-------|
| Token type | Classic PAT (personal access token) |
| Required scopes | `write:packages` (includes `read:packages`) |
| GitHub user | `gustavomello9600` |
| Registry | `ghcr.io` |
| Secret name (GitHub Actions) | `GHCR_TOKEN` |

### Creating the token

1. https://github.com/settings/tokens/new?description=ghcr-reader&scopes=write:packages
2. Or manually: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Name: `ghcr-reader-token`
   - Scopes: `write:packages` (auto-includes `read:packages`, `delete:packages`)
3. Copy the generated token (starts with `ghp_`)

### Adding to GitHub repo secrets

```bash
# Via gh CLI (simplest)
echo "<the-token>" | gh secret set GHCR_TOKEN --repo gustavomello9600/taskflow-mvp -a actions

# Verify
gh secret list -R gustavomello9600/taskflow-mvp
```

## Docker Login on the Oracle Host

### Manual (one-time, persists in ~/.docker/config.json)

```bash
echo "<PAT>" | docker login ghcr.io -u gustavomello9600 --password-stdin
```

The credential is stored in `/home/ubuntu/.docker/config.json` unencrypted (Docker's default). This persists across container restarts.

### Via CI deploy step (re-login every deploy)

```yaml
# In .github/workflows/ci.yml (deploy job)
- name: Deploy via SSH
  uses: appleboy/ssh-action@v1
  with:
    script: |
      cd /home/ubuntu/selfhost/taskflow
      echo "${{ secrets.GHCR_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      docker compose pull
      docker compose up -d
```

## Images

| Image | Registry URL |
|-------|-------------|
| backend | `ghcr.io/gustavomello9600/taskflow-mvp/backend` |
| frontend | `ghcr.io/gustavomello9600/taskflow-mvp/frontend` |

Tags: `latest` (mutável), `sha-<commit>` (imutável).

## Pitfalls

- **GITHUB_TOKEN doesn't work for external pulls:** The auto-generated `secrets.GITHUB_TOKEN` only has `packages: write` within the Actions context. It cannot be used for `docker login` from external hosts. Always use a dedicated PAT stored as `GHCR_TOKEN`.
- **Token scope must include `write:packages`:** `repo` scope alone is NOT sufficient for GHCR package access. The `read:packages` scope (or its superset `write:packages`) is required explicitly.
