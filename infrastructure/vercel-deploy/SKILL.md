---
name: vercel-deploy
description: "Deploy static sites and frontend apps to Vercel — from zero to production, CLI install, auth, deploy, custom domains, env vars.\n\nLoad this skill when deploying a static site or frontend app to Vercel. Covers CLI installation in restricted environments (no root, npm global prefix), device-flow OAuth authentication, project creation, deployment commands, custom domain setup, environment variable configuration, and common pitfalls like alias mismatches."
version: 1.0.0
author: Hermes Agent
tags: [vercel, deploy, static-site, frontend, hosting, jamstack]
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
TOKEN="$(python3 -c "import json; print(json.load(open('/opt/data/home/.local/share/com.vercel.cli/auth.json'))['token'])")"

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

### Pitfall: Auth token location varies

The Vercel CLI stores auth credentials at `~/.local/share/com.vercel.cli/auth.json` on some Linux setups (not `~/.vercel/auth.json` as sometimes documented). When automating API calls, locate the token dynamically:

```bash
TOKEN="$(python3 -c "import json; print(json.load(open('/opt/data/home/.local/share/com.vercel.cli/auth.json'))['token'])")"
```

---

## Reference Files

- `references/iframe-reader-ux.md` — full pattern for static archive sites with iframe edition reader, postMessage parent-child communication, smooth close transitions, and CSS grid cards that prevent badge/title overlap. Consult this when building any "landing page + content viewer" static site on Vercel.

## Quick Reference

```bash
# ── Install ──
npm config set prefix /opt/data/.npm-global
npm install -g vercel
export PATH="/opt/data/.npm-global/bin:$PATH"

# ── Login (first time) ──
vercel login --no-color
# → Send user the https://vercel.com/oauth/device?user_code=XXXX-XXXX URL

# ── Deploy (reliable prebuilt flow) ──
cd /path/to/project
vercel build --prod --yes          # Generate .vercel/output/
vercel deploy --prebuilt --prod --yes  # Deploy prebuilt output

# ── Verify ──
curl -s -o /dev/null -w "%{http_code}" https://<project>.vercel.app/

# ── Custom domain ──
vercel domains add mydomain.com

# ── Unattended deploy ──
VERCEL_TOKEN=*** vercel build --prod --yes && vercel deploy --prebuilt --prod --yes

# ── Analytics (enable once per project) ──
vercel project web-analytics <project-name>

# ── Analytics dashboard ──
# https://vercel.com/<team>/<project-name>/analytics
# Metrics: Visitors, Page Views, Countries, Referrers, Devices
# Hobby limits: 1M events/month, 30-day retention, no custom events

# ── Static HTML analytics snippet (inject before </body>) ──
# <script>window.va = window.va || function(){(window.vaq=window.vaq||[]).push(arguments)};</script>
# <script defer src="/_vercel/insights/script.js"></script>

# ── Clean up auth ──
rm -f ~/.vercel/auth.json
```
