# Deploy Flow — IAF Newsletter

## Regra absoluta: deploy via _deploy_new_edition.py

NUNCA copie manualmente o HTML para `edicoes/` e faça vercel deploy direto. O script `_deploy_new_edition.py` é o único caminho correto porque ele:

1. Adiciona o slug no `_transform.py` EDITIONS array
2. Roda `_transform.py` — que adiciona:
   - Barra de navegação entre edições (anterior/próxima)
   - Botões "Close" e "Menu" (voltam ao index)
   - Analytics snippet da Vercel
   - CSS responsivo (converte @page print layout para web)
3. Atualiza `index.html` com a nova edição na lista
4. Atualiza `vercel.json` com o rewrite do slug
5. Roda vercel build + deploy

## Fallback quando slug já existe

Se o script disser "No new editions to deploy" (slug já registrado de deploy anterior), re-transform manualmente:

```bash
cd /opt/data/iaf-edicoes-archive
python3 -c "
from _transform import transform, EDITIONS
from pathlib import Path
HISTORY = Path('/opt/data/cron/history')
EDITIONS_DIR = Path('/opt/data/iaf-edicoes-archive/edicoes')
slug = 'DDMMYYYY'
for ed in EDITIONS:
    if ed['slug'] == slug:
        src = HISTORY / ed['source']; dst = EDITIONS_DIR / f'{slug}.html'
        idx = EDITIONS.index(ed)
        prev = EDITIONS[idx-1]['slug'] if idx > 0 else None
        nxt = EDITIONS[idx+1]['slug'] if idx < len(EDITIONS)-1 else None
        transform(str(src), str(dst), slug, ed.get('title','#?'), ed['date'], prev, nxt)
"
/opt/data/.npm-global/bin/vercel build --prod --yes
/opt/data/.npm-global/bin/vercel deploy --prebuilt --prod --yes
```

## Pitfall: regex do excerpt editorial

A função `extract_editorial_first_paragraph()` em `_deploy_new_edition.py` busca `class="hot-take"` mas o template usa `class="hot-take-box"`. Isso quebra o preview no index.html — o fallback pega CSS bruto do `<style>`. Sempre verifique o excerpt no index.html depois do deploy.

## Pitfall: verificar alias

O deploy `--prod` aliaseia automaticamente para `iaf-newsletter.vercel.app`, mas às vezes o alias não propaga. Verifique sempre:

```bash
curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/DDMMYYYY"
```

Se não for 200, re-aliasseie:
```bash
vercel alias set <deployment-url> iaf-newsletter.vercel.app
```
