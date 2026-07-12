---
name: vercel-deploy
description: "Deploy static sites and frontend apps to Vercel — from zero to production.

Load this skill when deploying frontend applications to Vercel. Covers CLI installation in restricted environments (no root, npm global prefix), device-flow authentication, project creation and linking, deployment with custom domains, environment variable management, and common deployment pitfalls."
version: 1.0.0
author: Hermes Agent
tags: [vercel, deploy, static-site, frontend, hosting, jamstack]
type: ToolIntegration
timestamp: 2026-07-10T02:00:00Z
---

# Vercel Deploy — Skill

Class-level guide for deploying static sites (HTML/CSS/JS, SPAs, static generators) to Vercel from a restricted Linux environment (no root, Hermes Agent).

---

## Installation

In restricted environments where `npm install -g vercel` fails with `EACCES`, use a custom npm prefix:

```bash
# Set a writable prefix (one-time)
npm config set prefix /opt/data/.npm-global

# Install Vercel CLI
npm install -g vercel

# Add to PATH for current session
export PATH="/opt/data/.npm-global/bin:$PATH"
```

**Verify:** `vercel whoami` shows `Vercel CLI <version>` and an error about missing credentials (expected — next step).

---

## Authentication (Device Flow)

Vercel uses OAuth device authorization flow — no browser on the server required. The CLI prints a URL the user visits on their own machine.

### Interactive (PTY)

```bash
vercel login --no-color
```

Output:
```
Visit https://vercel.com/oauth/device?user_code=XXXX-YYYY
Waiting for authentication...
```

The user opens that URL in any browser, logs in, and authorizes. The CLI detects the completion and stores credentials in `~/.vercel/auth.json`.

### Background (Hermes pattern)

Since the CLI blocks until the user authenticates, run it in background with `notify_on_complete`:

```bash
# In terminal(background=true, pty=true, timeout=180, notify_on_complete=true)
vercel login --no-color
```

- Capture the `user_code=XXXX-YYYY` from the log output
- Share the full URL with the user: `https://vercel.com/oauth/device?user_code=XXXX-YYYY`
- Wait for `notify_on_complete` signal
- **PITFALL:** Each invocation generates a NEW code. If you run `vercel login` multiple times (e.g., to capture the URL), only the LAST running process's code is valid. Send the correct code to the user.

### Verify Authentication

```bash
vercel whoami
```

Expected output: `<username>` (no error).

Credentials persist in `~/.vercel/auth.json` across sessions.

---

## Deploy a Static Project

### First-time deploy (creates + links a project)

```bash
cd /path/to/project
vercel deploy --prod --yes
```

This:
1. Detects framework (or defaults to static)
2. Uploads the project directory (respects `.vercelignore` if present)
3. Assigns a random subdomain under `vercel.app`
4. Returns the production URL

**Output:**
```
🔗  Linked to <team>/<project-name>
🔗  Production: https://<project-name>.vercel.app
```

### Subsequent deploys (same project)

From the same directory, Vercel remembers the linked project:

```bash
vercel deploy --prod --yes
```

The `--yes` flag skips interactive prompts (required in non-TTY environments).

**IMPORTANT — The `--prebuilt` approach (RECOMMENDED for reliability):**

The standard `vercel deploy --prod --yes` flow often fails to serve updated files. Vercel runs its own `vercel build` on their server which can override or ignore your uploaded files, silently serving stale content. This is especially common with `buildCommand: null` or `""` where the server-side build output replaces your local files.

**The reliable approach — build locally, deploy prebuilt:**

```bash
cd /path/to/project

# Step 1: Build locally (generates .vercel/output/)
vercel build --prod --yes

# Step 2: Deploy the prebuilt output directly (skips server-side build)
vercel deploy --prebuilt --prod --yes
```

The `vercel build --prod --yes` generates a `.vercel/output/` directory containing:
- `config.json` — route configuration from vercel.json
- `static/` — your deployable files

The `--prebuilt` flag tells Vercel to skip server-side build and use the local `.vercel/output/` directly as the deployment artifact. The deploy log should show:
```
Using prebuilt build artifacts from .vercel/output
```

**Verification — confirm new content is served:**

```bash
curl -s "https://<project>.vercel.app/" | grep -c "expected-new-content"
```

If the count is 0, the old content is still being served — the prebuilt approach wasn't used or failed.

### Custom output directory

For projects where the deployable files are in a subdirectory:

```bash
vercel deploy --prod --yes --public ./dist
```

Or set `vercel.json` (see Configuration section).

---

## Project Configuration (`vercel.json`)

Place in project root for framework detection overrides and routing:

```json
{
  "version": 2,
  "buildCommand": null,
  "outputDirectory": ".",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Key fields for static sites:**

| Field | Value | When to set |
|-------|-------|-------------|
| `buildCommand` | `null` | No build step (plain HTML/JS) |
| `outputDirectory` | `"."` | Serve from project root |
| `outputDirectory` | `"dist"` | Build output in subfolder |
| `rewrites` | URL rewrites | Clean URL slugs (e.g., `/page` → `/page.html`) |
| `routes` | Redirect/proxy | Legacy patterns; prefer `rewrites` for clean URLs |

### Clean URL slugs (rewrites)

For sites that need clean URLs (e.g., `/05062026` instead of `/edicoes/05062026.html`):

```json
{
  "version": 2,
  "buildCommand": null,
  "outputDirectory": ".",
  "rewrites": [
    { "source": "/05062026", "destination": "/edicoes/05062026.html" },
    { "source": "/especial-mythos", "destination": "/edicoes/especial-mythos.html" }
  ]
}
```

### SPA fallback route

```json
{
  "version": 2,
  "buildCommand": null,
  "outputDirectory": ".",
  "rewrites": [
    { "source": "/edicoes/(.*)", "destination": "/edicoes/$1" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Without this, direct URL navigation to sub-pages on SPAs breaks on refresh.

---

## Environment Variables

```bash
# Set a specific variable
vercel env add PLAIN_VARIABLE production
# Prompts for value (interactive)

# Set from file using Vercel CLI with --token
echo "my-value" | vercel env add SECRET_KEY production --token $VERCEL_TOKEN --yes
```

For non-interactive environments, use a VERCEL_TOKEN (see Authentication alternatives).

---

## Web Analytics

Vercel Web Analytics tracks page views, visitors, referrers, countries, and device types — privacy-first, zero cookies. Works on all plans including Hobby (free, up to 1M events/month, 30-day retention).

### Enable on a project

```bash
vercel project web-analytics <project-name>
```

### Static sites (plain HTML) — manual script injection

Unlike framework-based projects where the analytics script is auto-injected at the edge, **static HTML sites require a manual snippet** before `</body>`:

```html
<!-- Vercel Web Analytics -->
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
```

The insights endpoint (`/_vercel/insights/script.js`) becomes available at the project's production URL once analytics is enabled. Verify with:

```bash
curl -s -o /dev/null -w "%{http_code}" https://<project>.vercel.app/_vercel/insights/script.js
# Expected: 200
```

**Dashboard URL pattern:**

```
https://vercel.com/<team-slug>/<project-name>/analytics
```

Metrics available: Visitors, Page Views, Countries, Referrers, Devices. Events appear within minutes of the first visit. CSV export available.

---

## Custom Domains

```bash
# Add domain to project
vercel domains add mydomain.com

# List domains
vercel domains ls
```

DNS configuration (add CNAME to `cname.vercel-dns.com`) is still manual — Vercel doesn't auto-configure external DNS.

---

## Alternative Authentication (Token)

For unattended deploys (CI/CD, cron jobs), use a Vercel access token instead of device-flow login:

1. User generates token at: https://vercel.com/account/tokens
2. Use with `--token` flag:

```bash
vercel deploy --prod --token=$VERCEL_TOKEN --yes
```

Or set `VERCEL_TOKEN` env var and Vercel CLI picks it up automatically.

---

## Deploy Verification

After deploy, verify HTTP 200 from the production URL:

```bash
curl -s -o /dev/null -w "%{http_code}" https://<project>.vercel.app/
# Expected: 200
```

Also verify sub-pages and assets:

```bash
curl -s -o /dev/null -w "%{http_code}" https://<project>.vercel.app/edicoes/page.html
# Expected: 200
```

---

## Pitfalls

### Pitfall: Device code mismatch

Each `vercel login` call generates a NEW device code. If the CLI is invoked multiple times (to capture the URL after a timeout), only the LAST process's code is valid. The URL the user visits must match the currently running process.

**Fix:** Kill all previous `vercel login` processes. Start ONE fresh instance. Capture its code. Send that exact URL. Do not invoke `vercel login` again until authentication completes.

### Pitfall: PTY required for interactive prompts

`vercel deploy` with no `--yes` flag tries to read from stdin and hangs in non-TTY environments. Always use `--yes` when running from Hermes terminal.

**Fix:** `vercel deploy --prod --yes`

### Pitfall: EACCES on npm global install

**Symptom:** `npm install -g vercel` fails with `EACCES: permission denied, mkdir '/usr/local/lib/node_modules/vercel'`.

**Fix:** Set a writable custom prefix:
```bash
npm config set prefix /opt/data/.npm-global
export PATH="/opt/data/.npm-global/bin:$PATH"
```

### Pitfall: Project linking changes working directory

`vercel deploy` without `--prod` deploys a preview (random URL). `vercel deploy --prod` aliases the production domain. If the project isn't linked yet, `--prod` alone may not be enough — first deploy links it.

**Fix:** First deploy: `vercel deploy --prod --yes`. Subsequent deploys from the same directory: same command, Vercel reuses the link.

### Pitfall: .vercelignore missing

By default, Vercel uploads the ENTIRE project directory including `node_modules`, `.git`, and other large directories. This can cause slow uploads or hitting the 250MB file limit.

**Fix:** Create `.vercelignore`:
```
.git
node_modules
*.md
_test/
scripts/
```

### Pitfall: Persistent auth across sessions

Vercel stores credentials in `~/.vercel/auth.json`. This file persists across Hermes sessions. If the token expires or the user wants to switch accounts, delete it:
```bash
rm -f ~/.vercel/auth.json
```

### Pitfall: Framework detection picks the wrong settings

Vercel auto-detects frameworks (Next.js, Vite, etc.) and applies build settings. For a plain static site, it may incorrectly detect a framework and try to run a build command that doesn't exist.

**Fix:** Explicitly set `"buildCommand": null` in `vercel.json` or use `--force` flag:
```bash
vercel deploy --prod --yes --force
```

### Pitfall: SSO Deployment Protection blocks public access (401)

When a project is created under a team/org account, Vercel enables SSO Protection by default with `deploymentType: "all_except_custom_domains"`. This causes ALL `.vercel.app` URLs to return HTTP 401 for unauthenticated visitors — evenProduction URLs. The site looks completely broken to anyone outside the team.

**Symptom:** `curl` returns 401 with `_vercel_sso_nonce` cookie in response headers. Browser shows a Vercel login page instead of your site.

**Fix:** Disable SSO Protection via the Vercel API:
```bash
PROJECT_ID="prj_xxxx"
TEAM_ID="team_xxxx"
TOKEN="$(python3 -c "import json; print(json.load(open('/opt/data/home/.local/share/com.vercel.cli/auth.json'))['token'])")\"

curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ssoProtection": null}'
```

You can check the current protection setting with a GET request to the same endpoint. Look for `"ssoProtection": {"deploymentType": "all_except_custom_domains"}` in the response.

**Note:** This can also be disabled in the Vercel Dashboard under Project → Settings → Deployment Protection.

### Pitfall: `routes` vs `rewrites` in vercel.json

For clean URL slugs (e.g., `/05062026` serving `/edicoes/05062026.html`), use **`rewrites`**, not `routes`. The `routes` key is for redirect/proxy patterns with different semantics — it won't correctly serve rewritten content.

**Wrong:**
```json
{"routes": [{"src": "/05062026", "dest": "/edicoes/05062026.html"}]}
```

**Right:**
```json
{"rewrites": [{"source": "/05062026", "destination": "/edicoes/05062026.html"}]}
```

Note the different key names: `source`/`destination` (not `src`/`dest`) in rewrites.

### Pitfall: `.vercel/` deletion + re-link creates a NEW project

When you delete the `.vercel/` directory (e.g., `rm -rf .vercel`) and run `vercel link --yes`, Vercel may create a **brand new project** with a new `projectId` instead of re-linking to the existing one. This causes:
- **SSO Protection re-enables** on the new project (returns 401 on `.vercel.app` URLs)
- **All previous aliases** still point to the OLD project's deployments — the new deployments are invisible at the custom domain
- **Project settings are reset** (framework, buildCommand, etc.)

**Fix:** After re-linking, check the project ID:
```bash
cat .vercel/project.json  # Note the projectId
```

If it changed from the expected ID, either:
1. Delete `.vercel/` and explicitly link to the original: `vercel link --project <original-name> --yes`
2. Or disable SSO on the new project and re-assign all aliases:
```bash
# Disable SSO
python3 -c "
import json, urllib.request
with open('/opt/data/home/.local/share/com.vercel.cli/auth.json') as f:
    token = json.load(f)['token']
data = json.dumps({'ssoProtection': None}).encode()
req = urllib.request.Request(
    f'https://api.vercel.com/v9/projects/{NEW_PROJECT_ID}?teamId={TEAM_ID}',
    data=data, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='PATCH')
with urllib.request.urlopen(req) as resp:
    print('ssoProtection:', json.loads(resp.read()).get('ssoProtection'))
"

# Remove old aliases and re-create pointing to new deployment
vercel alias remove <old-domain>.vercel.app --yes
vercel alias remove <custom-domain>.vercel.app --yes
vercel alias https://<new-deploy-url> <old-domain>.vercel.app
vercel alias https://<old-domain>.vercel.app <custom-domain>.vercel.app
```

### Pitfall: Aliases don't auto-migrate when switching projects

When you run `vercel link --project <different-name> --yes` to switch a local directory to a different Vercel project, the production aliases (custom domains) on the **original** project continue pointing to the **original** project's deployments — they won't follow your new deploys. The new project gets its own auto-generated alias, but the domain users visit (e.g., `mysite.vercel.app`) still shows stale content from the old project.

**Symptom:** After linking to `<new-project>` and running `vercel deploy --prod --yes`, `curl` on the custom domain returns old content even though the new deploy URL has the correct content. The `vercel alias ls` output shows the custom domain still pointed at the old project's deployment.

**Fix:** After deploying to the new project, reassign the alias manually:

```bash
# Get the new deployment URL (shown in deploy output as ▲ Production)
DEPLOY_URL="<new-project>-<hash>-<team>.vercel.app"

# Reassign the custom domain alias
vercel alias set "$DEPLOY_URL" mysite.vercel.app

# Verify
vercel alias ls | grep mysite.vercel.app
```

Alias management commands:

```bash
vercel alias ls                          # List all aliases
vercel alias set <deploy-url> <alias>    # Assign (or reassign) alias to deployment
vercel alias remove <alias> --yes        # Remove an alias
```

---

### Pitfall: Project rename doesn't change the `.vercel.app` subdomain

`vercel project rename <old> <new>` changes the display name but the original `<old>.vercel.app` subdomain remains active. To get a new `.vercel.app` subdomain matching the new name, use `vercel alias`:

```bash
vercel alias https://<old-subdomain>.vercel.app <new-name>.vercel.app
```

However, `.vercel.app` subdomain availability depends on global uniqueness — if the name is taken by another account, the alias will return 401 until resolved.

### Pitfall: Deploy serves stale content (server-side build overrides files)

**Symptom:** After `vercel deploy --prod --yes`, `curl` still returns old content even though the files are correct locally. The deploy log shows only `vercel.json` being uploaded (small byte count like 532 bytes) while the HTML files (which should be 30KB+) are not in the upload. The server-side `vercel build` step generates its own output from cached files, ignoring your local changes.

**Root cause:** Vercel's build pipeline runs `vercel build` on their servers. Even with `buildCommand: null` or `""`, the default build detects the previous deployment's file list and regenerates output from that cache, not from your locally changed files.

**Fix:** Use the `--prebuilt` approach documented in Deploy a Static Project → Subsequent deploys section. Build locally first, then deploy prebuilt:
```bash
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

### Pitfall: `name` property in vercel.json is deprecated

Deploying with `"name"` in `vercel.json` produces a deprecation warning:
```
The `name` property in vercel.json is deprecated
```

**Fix:** Remove the `"name"` key from `vercel.json`. Project name is managed via `vercel project rename` or at initial deploy time.

### Pitfall: Deploy stays BLOCKED with no error — wrong login account

**Symptom:** `vercel deploy --prod --yes` succeeds with "Building..." but the deployment never becomes READY. API shows `state=BLOCKED`, `readyState=BLOCKED`, `errorCode=null`, `aliasAssigned=false`. No error message in CLI output. The project's SSO protection shows `null` when checked via API.

**Root cause:** The Vercel CLI is authenticated with an email that is NOT a member of the team the project belongs to. When the user logs in with email A (e.g., personal account), but the project/team belongs to email B (e.g., work account), the deploy API accepts the request but the Vercel platform blocks the deployment from ever becoming READY — silently. There's no CLI error, no email notification to the wrong-email user (the notification goes to the team owner), and the only symptom is `state=BLOCKED` in the API response.

**Diagnosis:**

```bash
# Check deployment state
curl -s "https://api.vercel.com/v13/deployments/$DEPLOYMENT_UID?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys, json; d=json.load(sys.stdin); print('state:', d.get('state'), 'readyState:', d.get('readyState'), 'errorCode:', d.get('errorCode'))"
```

If `state=BLOCKED` with no error code, suspect account mismatch.

**Fix:** Switch to the correct Vercel account:

```bash
# 1. Find where Vercel stored credentials
ls -la ~/.vercel/auth.json   # Common location
ls -la ~/.local/share/com.vercel.cli/auth.json  # Alternative location

# 2. Check which account is logged in
vercel whoami

# 3. Remove credentials
rm -f ~/.vercel/auth.json ~/.local/share/com.vercel.cli/auth.json

# 4. Re-login with the CORRECT email
vercel login --no-color
# -> Send user the device URL: https://vercel.com/oauth/device?user_code=XXXX-XXXX
# -> User MUST log in with the email that is a member of the target team

# 5. Redeploy
vercel deploy --prod --yes
```

**Prevention:** Before starting a deploy, verify auth:
```bash
vercel whoami  # Shows current email
```

If the email doesn't match the expected team member, clean and re-login.

**Tip — locate auth token for API calls:**

The Vercel CLI stores credentials in `~/.local/share/com.vercel.cli/auth.json` on some Linux setups, not `~/.vercel/auth.json`. Always check both:

```bash
cat ~/.vercel/auth.json 2>/dev/null || cat ~/.local/share/com.vercel.cli/auth.json 2>/dev/null
```

### Pitfall: Auth token location varies

The Vercel CLI stores auth credentials at `~/.local/share/com.vercel.cli/auth.json` on some Linux setups (not `~/.vercel/auth.json` as sometimes documented). When automating API calls, locate the token dynamically:

```bash
TOKEN="$(python3 -c "import json; print(json.load(open('/opt/data/home/.local/share/com.vercel.cli/auth.json'))['token'])")\"
```

### Pitfall: NPM custom config directory must exist before writing

When adding a custom `location` directive into Nginx Proxy Manager's container at `/data/nginx/custom/server_proxy.conf`, the parent directory may not exist on a fresh or restarted container.

**Symptom:** `docker exec ... sh -c 'cat > /data/nginx/custom/server_proxy.conf'` fails with: `cannot create /data/nginx/custom/server_proxy.conf: Directory nonexistent`.

**Fix:** Create the directory first:

```bash
docker exec nginx_proxy_manager mkdir -p /data/nginx/custom
```

Always write custom configs via base64 to avoid shell escaping issues with nginx `$variables`:

```bash
CONFIG_B64="$(printf '%s' 'location /delfos/ {
    proxy_pass http://backend-nginx:80/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}' | base64 -w0)"
echo "$CONFIG_B64" | base64 -d | docker exec -i nginx_proxy_manager sh -c 'cat > /data/nginx/custom/server_proxy.conf'
```

**Verify** the file after writing — shell heredocs inside `docker exec` often expand `$host`, `$remote_addr`, etc. to empty strings:

```bash
docker exec nginx_proxy_manager cat /data/nginx/custom/server_proxy.conf
# If Host: line ends with empty value, re-write using the base64 method above
```

### Pitfall: Multi-line CSP header causes 502 from openresty

**Symptom:** Proxied requests return `502 Bad Gateway` from openresty. NPM error log shows:
```
upstream sent invalid header: "\x20..." while reading response header from upstream
```

**Root cause:** The backend nginx sends a `Content-Security-Policy` header with a multi-line value (HTTP folded header). Nginx Proxy Manager uses openresty, which rejects folded headers as invalid. The `\x20` is a space at the start of a continuation line.

**Fix:** Collapse the CSP to a single line:

```nginx
# Broken - multi-line (triggers 502)
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self';
" always;

# Fixed - single-line
add_header Content-Security-Policy "default-src 'self'; script-src 'self';" always;
```

After fixing, reload or restart the affected container.

### Pitfall: Docker network isolation blocks NPM custom location upstream

When a custom `location` proxies to a container in a different Docker Compose project (different network), NPM cannot resolve the target hostname:

```
nginx: [emerg] host not found in upstream "container-name" in /data/nginx/custom/server_proxy.conf
```

**Fix:** Connect the NPM container to the target container's network:

```bash
# Find the target network
docker network ls | grep <project-name>

# Connect NPM to it (enables Docker DNS resolution)
docker network connect <project_network> nginx_proxy_manager

# Alternative: use the container's static IP
docker inspect <container-name> --format '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
```

Always restart NPM after network changes:

```bash
docker restart nginx_proxy_manager
```

### Pitfall: Vercel deploy only uploads vercel.json when project files sit in a subdirectory

**Symptom:** After deploying from within a subdirectory (e.g., `cd frontend && vercel --prod --yes`), the upload only shows a few hundred bytes even though the static files are several KB. The deployed site serves stale content or throws 404 on assets.

**Root cause:** Vercel CLI uses the current working directory as the project root. When deploying from a subdirectory that contains only `vercel.json`, only that file is uploaded. The actual source files (html, js, css) are outside the deploy root and never reach Vercel's build system.

**Fix:** Either:
1. Deploy from the project root (where all files live), not from the subdirectory:
   ```bash
   cd /project/root
   vercel build --prod --yes
   vercel deploy --prebuilt --prod --yes
   ```
2. Or set `outputDirectory` in `vercel.json` to point to the subdirectory when deploying from the root:
   ```json
   {
     "outputDirectory": "frontend",
     "rewrites": [...]
   }
   ```
   BUT verify the build output includes all files by checking `.vercel/output/static/` after running `vercel build`.

---

## Reference Files

- `references/iframe-reader-ux.md` — full pattern for static archive sites with iframe edition reader, postMessage parent-child communication, smooth close transitions, and CSS grid cards that prevent badge/title overlap. Consult this when building any "landing page + content viewer" static site on Vercel.
- `references/custom-domain-alias-pitfall.md` — explains why manually-assigned aliases survive --prod deploys and how to reassign them.
- `references/interactive-frontend-pitfalls.md` — debugging guide for Lenis smooth scroll + GSAP ScrollTrigger + Three.js integration issues. Covers `height: 100%` scroll lock, ScrollTrigger animation interference, and refresh timing. Consult when building interactive 3D/animation sites for Vercel.
- `references/threejs-invisible-scene-debugging.md` — diagnosing Three.js scenes that render correctly (triangles drawn, no errors) but appear invisible. Covers fog density masking, ShaderMaterial GLSL version mismatch in WebGL2, canvas-CSS background contrast, GLTFLoader MeshPhysicalMaterial envMap, and pixel-reading diagnostic workflow.
- `references/spa-remote-backend.md` — SPA on Vercel + backend on remote host (CORS, config.js, credentials mode, API QA via SSH).

## Quick Reference

```bash
# -- Install --
npm config set prefix /opt/data/.npm-global
npm install -g vercel
export PATH="/opt/data/.npm-global/bin:$PATH"

# -- Login (first time) --
vercel login --no-color
# -> Send user the https://vercel.com/oauth/device?user_code=XXXX-XXXX URL

# -- Deploy (reliable prebuilt flow) --
cd /path/to/project
vercel build --prod --yes          # Generate .vercel/output/
vercel deploy --prebuilt --prod --yes  # Deploy prebuilt output

# -- Verify --
curl -s -o /dev/null -w "%{http_code}" https://<project>.vercel.app/

# -- Custom domain --
vercel domains add mydomain.com

# -- Unattended deploy --
VERCEL_TOKEN=*** vercel build --prod --yes && vercel deploy --prebuilt --prod --yes

# -- Analytics (enable once per project) --
vercel project web-analytics <project-name>

# -- Analytics dashboard --
# https://vercel.com/<team>/<project-name>/analytics
# Metrics: Visitors, Page Views, Countries, Referrers, Devices
# Hobby limits: 1M events/month, 30-day retention, no custom events

# -- Static HTML analytics snippet (inject before </body>) --
# <script>window.va = window.va || function(){(window.vaq=window.vaq||[]).push(arguments)};</script>
# <script defer src="/_vercel/insights/script.js"></script>

# -- Clean up auth --
rm -f ~/.vercel/auth.json
```
