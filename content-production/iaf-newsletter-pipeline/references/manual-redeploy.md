# Manual Redeploy — Forçar Atualização de Edição Já Publicada

Quando uma edição da newsletter já foi publicada (Cron #4 executou com sucesso) mas você precisa **substituir o conteúdo** (correção de erros, remoção de notícias repetidas, ajustes editoriais), o script `_deploy_new_edition.py` **não funciona** — ele detecta que o slug já existe no registro e retorna "No new editions to deploy".

## Workaround

O slug é gerado a partir da data: `15062026` para `iaf_2026-06-15.html`.

Passos para forçar o redeploy de uma edição já registrada:

### 1. Sobrescreva o HTML fonte

```bash
cp /tmp/manha_aumentada_DDMMYYYY.html /opt/data/cron/history/iaf_YYYY-MM-DD.html
```

### 2. Re-transforme a edição

Rode o `_transform.py` importado diretamente para transformar **apenas** o slug desejado:

```python
cd /opt/data/iaf-edicoes-archive && python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('transform', '_transform.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# mod.transform() já foi chamado pelo loop do script ao importar
# Apenas verifique se o slug foi transformado corretamente
"
```

> **Nota:** Ao importar `_transform.py`, o loop no final do script executa e transforma **todas as edições** — incluindo a atualizada. O erro final `missing 1 required positional argument` é esperado e **inofensivo**; a transformação já ocorreu.

### 3. Faça o deploy Vercel

```bash
cd /opt/data/iaf-edicoes-archive
/opt/data/.npm-global/bin/vercel build --prod --yes
/opt/data/.npm-global/bin/vercel deploy --prebuilt --prod --yes
```

### 4. Verifique e corrija o alias personalizado

O deploy `--prod` aliaseia para o domínio original (`iaf-edicoes-archive.vercel.app`) mas **pode não atualizar** o alias personalizado (`iaf-newsletter.vercel.app`). Verifique:

```bash
curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/SLUG"
```

Se retornar 404, re-aliasseie apontando o deployment URL mais recente para o domínio personalizado:

```bash
# Liste os deployments para pegar a URL mais recente
/opt/data/.npm-global/bin/vercel list

# Aliasseie o deployment específico para o domínio personalizado
/opt/data/.npm-global/bin/vercel alias set <deployment-url> iaf-newsletter.vercel.app
```

### 5. Confirme o resultado

```bash
curl -o /dev/null -s -w "%{http_code}" "https://iaf-newsletter.vercel.app/SLUG"
# Deve retornar 200
```

## Quando usar

- Correção editorial de conteúdo já publicado (erros factuais, remoção de notícias repetidas)
- Atualização de links quebrados
- Ajustes de formatação ou layout no HTML da edição

## Quando NÃO usar

- Para adicionar uma edição nova (use o script normal `_deploy_new_edition.py`)
- Para correções cosméticas no site que não envolvem conteúdo da edição (edite direto no index.html)
