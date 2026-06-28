# Special Edition Deploy — Vercel Archive Site

## Overview

When a special edition is published, it needs to appear in the IAF newsletter archive site
(`iaf-newsletter.vercel.app`) alongside daily editions. The archive is a static site at
`/opt/data/iaf-edicoes-archive/` deployed to Vercel project `iaf-newsletter`.

This process differs from the daily pipeline's `_deploy_new_edition.py` script, which is designed
for daily editions. Special editions require three manual file edits before deploy.

## Pre-requisites

- Vercel CLI installed and authenticated (`vercel whoami` shows user)
- Project directory: `/opt/data/iaf-edicoes-archive/`
- Special edition HTML saved and ready (from the special edition workflow)

## Step-by-step

### 1. Copy HTML to edicoes/

```bash
cp /opt/data/cron/history/iaf-especial-YYYY-MM-DD-SLUG.html \
   /opt/data/iaf-edicoes-archive/edicoes/especial-{slug}.html
```

### 2. Update sidebar — index.html editions array

The sidebar is driven by a JS array `editions` in `/opt/data/iaf-edicoes-archive/index.html`.
Add a new entry after the last special edition entry (special editions are grouped at the
bottom of the array, ordered by date). Use `patch` tool with `mode='replace'` to add the entry.

Entry format:
```javascript
{
  date: 'DD/MM/YYYY',
  weekday: '✦',
  slug: 'especial-{slug}',
  file: 'edicoes/especial-{slug}.html',
  number: 'Extra',
  title: 'Title of the Special Edition',
  label: 'Extraordinária',
  labelClass: 'extra',
  excerpt: '<strong>First sentence bold.</strong> Rest of excerpt...',
  tags: ['Tag1', 'Tag2', 'Tag3'],
  isSpecial: true
}
```

**Ordering rule:** Special editions must be ordered by date (oldest first). When adding a new
one, insert it after any earlier-dated specials and before any later-dated ones. Currently the
two special editions are: Mythos (09/06/2026) → GPT‑5.6 (26/06/2026).

### 3. Update vercel.json — add rewrite rule

Add a rewrite entry for the new slug in `/opt/data/iaf-edicoes-archive/vercel.json`:

```json
{ "source": "/especial-{slug}", "destination": "/edicoes/especial-{slug}.html" }
```

The special edition rewrites are at the end of the rewrites array, after all daily edition
rewrites (which use date-based slugs like `/26062026`).

### 4. Build and deploy

```bash
export PATH="/opt/data/.npm-global/bin:$PATH"
cd /opt/data/iaf-edicoes-archive
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

The `--prebuilt` flag is critical — without it, Vercel's server-side build may serve stale
files. See `vercel-deploy` skill for pitfalls.

### 5. Verify

```bash
# Check new special edition
curl -s -o /dev/null -w "%{http_code}" "https://iaf-newsletter.vercel.app/especial-{slug}"
# Expected: 200

# Check index page has sidebar entries for ALL special editions
curl -s "https://iaf-newsletter.vercel.app/" | grep -c "especial-{slug}"
# Expected: 2 (one in editions array, one in sidebar rendering)
```

### 6. Verify sidebar ordering

The prod URL should show special editions ordered by date at the bottom of the sidebar.
Open `https://iaf-newsletter.vercel.app/` in a browser and click "Ler edições" to verify.

## Pitch pitfalls

- **The `_deploy_new_edition.py` script does NOT handle special editions.** It's designed for
  daily editions only. Special editions require manual deployment as described above.
- **Don't forget the vercel.json rewrite.** Without it, the clean URL `/especial-{slug}`
  returns 404. The rewrite maps it to the actual file in `edicoes/`.
- **The editions array order matters.** Special editions use `isSpecial: true` for visual
  differentiation (different card styling). They should be grouped at the bottom of the array,
  ordered by date (oldest first).
