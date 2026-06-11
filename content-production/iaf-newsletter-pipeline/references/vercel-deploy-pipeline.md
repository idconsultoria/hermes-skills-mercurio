# Vercel Deploy Pipeline — IAF Newsletter

## Overview

The IAF Newsletter web archive lives at `https://iaf-newsletter.vercel.app/`.  
New editions are deployed automatically via CRON #4 (Deploy Web, 07:50 BRT).

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
```

## Verification

```bash
curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/{SLUG}"
# → 200 means live
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

This is expected — it means today's slug is already registered in `_transform.py` EDITIONS.  
If you've regenerated the HTML since the last deploy (e.g., after content corrections), skip the script and do a manual redeploy:

```bash
python3 _transform.py
vercel build --prod --yes
vercel deploy --prebuilt --prod --yes
```

## URL Format

- `https://iaf-newsletter.vercel.app/` — archive index
- `https://iaf-newsletter.vercel.app/{SLUG}` — specific edition (e.g. `10062026`)
- `https://iaf-newsletter.vercel.app/especial-{slug}` — special editions (e.g. `especial-mythos`)
