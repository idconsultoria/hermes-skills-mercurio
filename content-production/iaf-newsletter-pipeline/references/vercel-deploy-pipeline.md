# Vercel Deploy Pipeline — IAF Newsletter

## Overview

The IAF Newsletter web archive lives at `https://iaf-newsletter.vercel.app/`.  
New editions are deployed automatically via CRON #4 (Deploy Web, 07:50 BRT).

## Domain Architecture

The Vercel project is named **`iaf-edicoes-archive`**. It has two URLs:

| Type | URL | Purpose |
|------|-----|---------|
| **Original/production domain** | `https://iaf-edicoes-archive.vercel.app` | Set by Vercel at project creation; `vercel deploy --prod` aliases here by default |
| **Custom alias** | `https://iaf-newsletter.vercel.app` | User-facing domain; must be set explicitly after deploy |

**Key insight:** `vercel deploy --prod --yes` aliases the deploy to the project's original domain, NOT necessarily to the custom alias. After every deploy, verify the alias and re-set it if needed:

```bash
vercel alias set <deployment-url> iaf-newsletter.vercel.app
```

Where `<deployment-url>` is the URL shown in the deploy output (e.g., `https://iaf-newsletter-ob9n4z9uh-gustavos-projects-9b1060a6.vercel.app`). The alias only takes effect once explicitly assigned.

## Project Structure

```
/opt/data/iaf-edicoes-archive/
├── _deploy_new_edition.py   ← Entry point script (called by CRON #4)
├── _transform.py            ← Transforms history HTML → responsive web HTML
├── index.html               ← Archive landing page (JS array of editions)
├── vercel.json              ← Rewrites for slug → /edicoes/{slug}.html
├── edicoes/                 ← Generated responsive HTML files (1 per edition)
└── .vercel/                 ← Vercel project config (do not touch)
```

## Deploy Flow (CRON #4)

1. **Detect:** `_deploy_new_edition.py` scans `/opt/data/cron/history/iaf_*.html` for files not yet in the archive (by slug in `_transform.py` EDITIONS array)
2. **Register:** Appends new entry to `_transform.py` EDITIONS + `index.html` editions array + `vercel.json` rewrites
3. **Transform:** Runs `_transform.py` to generate responsive mobile-friendly HTML in `edicoes/{slug}.html`
4. **Build:** `vercel build --prod --yes` — outputs to `.vercel/output/`
5. **Deploy:** `vercel deploy --prebuilt --prod --yes` — uploads to Vercel
6. **Verify alias:** Check the deploy output for "Aliased" URL. If it's not `iaf-newsletter.vercel.app`, set it explicitly

## Manual Deploy (when CRON #4 missed or needs redo)

```bash
export PATH="/opt/data/.npm-global/bin:$PATH"
cd /opt/data/iaf-edicoes-archive

# 1. Transform the new HTML
python3 _transform.py

# 2. Build
vercel build --prod --yes

# 3. Deploy
vercel deploy --prebuilt --prod --yes

# 4. Ensure the custom alias is set
# Extract deployment URL from deploy output and set alias
vercel alias ls | grep iaf-newsletter
vercel alias set $(vercel ls iaf-edicoes-archive --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['url'])" 2>/dev/null) iaf-newsletter.vercel.app
```

## Verification

```bash
# Check both URLs point to the same content
curl -s -o /dev/null -w "archive: HTTP %{http_code}\n" "https://iaf-edicoes-archive.vercel.app/{SLUG}"
curl -s -o /dev/null -w "alias:   HTTP %{http_code}\n" "https://iaf-newsletter.vercel.app/{SLUG}"
# Both must return 200
```

## When deploy script says "No new editions to deploy"

This is expected — it means today's slug is already registered in `_transform.py` EDITIONS.  
If you've regenerated the HTML since the last deploy (e.g., after content corrections like dedup), skip the script and do a manual redeploy:

```bash
# 1. Copy the corrected HTML to the edicoes directory
cp /opt/data/cron/history/iaf_YYYY-MM-DD.html /opt/data/iaf-edicoes-archive/edicoes/{SLUG}.html

# 2. Transform, build, deploy
cd /opt/data/iaf-edicoes-archive
python3 _transform.py
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

## Key Paths

| Item | Path |
|------|------|
| Vercel CLI | `/opt/data/.npm-global/bin/vercel` |
| Deploy script | `/opt/data/iaf-edicoes-archive/_deploy_new_edition.py` |
| Transform script | `/opt/data/iaf-edicoes-archive/_transform.py` |
| History HTMLs (source) | `/opt/data/cron/history/iaf_YYYY-MM-DD.html` |
| Generated web HTMLs | `/opt/data/iaf-edicoes-archive/edicoes/{slug}.html` |

## Alias Divergence (Important Pitfall)

O comando `vercel deploy --prebuilt --prod --yes` pode ALIASAR o deploy
para um domínio DIFERENTE de `iaf-newsletter.vercel.app` (ex: o projeto
pode ter um alias secundário configurado como `iaf-edicoes-archive.vercel.app`).
Isso faz com que o site principal NÃO receba as atualizações.

**Sempre verifique o alias depois do deploy:**
```bash
# A saída do deploy mostra "Aliased https://..." — confira se é o domínio certo
# Se não for, corrija explicitamente:
vercel alias set <deployment-url> iaf-newsletter.vercel.app
```

## Quando o Index Mostra CSS no Lugar do Editorial

Se o preview da edição no index.html mostra CSS bruto no lugar do texto
editorial, o problema é na função `extract_editorial_first_paragraph()`
em `_deploy_new_edition.py`. A regex usada para extrair o editorial do
HTML fonte precisa casar com `class="hot-take-box"` — veja o reference
file `extract-editorial-excerpt-regex.md` para o diagnóstico e fix.

## URL Format

- `https://iaf-newsletter.vercel.app/` — archive index
- `https://iaf-newsletter.vercel.app/{SLUG}` — specific edition (e.g. `10062026`)
- `https://iaf-newsletter.vercel.app/especial-{slug}` — special editions (e.g. `especial-mythos`)
