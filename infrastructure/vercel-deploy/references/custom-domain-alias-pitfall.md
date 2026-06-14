# Custom Domain Alias Pitfall — Vercel

## Problem

After `vercel deploy --prod`, the project's default `.vercel.app` URL updates correctly, but manually-assigned custom domain aliases (set via `vercel alias set`) remain pinned to the old deployment. The custom alias returns 404.

## Root Cause

Vercel's `deploy --prod` updates the project's "production" URL and any DNS-based custom domains, but it does NOT touch aliases created via `vercel alias set <url> <alias>`. Those aliases are statically pinned to a specific deployment and must be reassigned manually after each deploy.

## Fix

```bash
# 1. Deploy as normal
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes

# 2. Verify the default URL works
curl -s -o /dev/null -w "%{http_code}" "https://project.vercel.app/"

# 3. Check the custom alias
curl -s -o /dev/null -w "%{http_code}" "https://my-brand.vercel.app/"

# 4. If not 200, reassign the alias
vercel alias set <deployment-url-from-deploy-output> my-brand.vercel.app

# 5. Verify again
curl -s -o /dev/null -w "%{http_code}" "https://my-brand.vercel.app/"
```

## Prevention

Add alias verification to every deploy checklist. Never assume `--prod` updates all domains — it only updates the default.
