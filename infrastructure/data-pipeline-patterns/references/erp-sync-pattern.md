# ERP Sync Pattern — GraphQL → JSON → Supabase

Pattern observed in the ATLAS Ravello project (`scripts/sync-erp.mjs`). Applicable to any
batch pipeline that pulls large datasets from an external API and pushes to a database.

## Architecture

```
┌──────────────┐     GraphQL      ┌──────────────┐     upsert      ┌──────────┐
│  ERP / API   │ ───────────────→ │  sync script  │ ─────────────→ │ Supabase │
│  (Maxprod)   │   paginated      │  (Node.js)    │   service_role │          │
└──────────────┘                  └──────┬───────┘                └──────────┘
                                         │
                                         ▼ write JSON
                                  ┌──────────────┐
                                  │ public/data/  │
                                  │ erp/*.json    │
                                  └──────────────┘
```

## Key patterns

### 1. Dual persistence: Supabase + local JSON fallback
```javascript
// 1. Save to local JSON (always works, offline dev)
saveJson('clientes.json', empresas);

// 2. Push to Supabase if configured (production)
if (supabase) {
  await supabase.from('empresas').upsert(empresas, { onConflict: 'id' });
}
```

### 2. Paginated GraphQL collection with retry
```javascript
async function fetchAllPages(entityName, queryFn) {
  const firstPage = await graphqlQuery(queryFn(PAGE_SIZE, 0));
  const totalCount = firstPage[entityName].totalCount;
  const allItems = [...firstPage[entityName].items];

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);
  for (let page = 1; page < totalPages; page++) {
    const pageData = await graphqlQuery(queryFn(PAGE_SIZE, page * PAGE_SIZE));
    allItems.push(...pageData[entityName].items);
    await sleep(400); // Rate limiting between pages
  }
  return allItems;
}
```

### 3. Business rule enrichment in ETL (not in frontend)
Apply complex calculation rules (faturamento líquido, volume m², ajustes YTD)
during the ETL phase so the frontend receives pre-computed values:

```javascript
function processAndEnrichNFs(nfs) {
  return nfs.map(nf => ({
    ...nf,
    faturamentoLiq: calcularFaturamentoLiquido(nf),  // complex rules here
    volumeM2:       calcularVolumeComercial(nf),       // not in browser
    custoTotal:     calcularCustoMedioEstoque(nf),
  }));
}
```

### 4. Concurrent pagination for large Supabase reads
```javascript
async function fetchAllFromSupabase(table, columns) {
  const CONCURRENCY = 5;
  const limit = 1000;

  while (true) {
    const promises = Array.from({ length: CONCURRENCY }, (_, j) =>
      supabase.from(table).select(columns).range(from + j*limit, from + (j+1)*limit - 1)
    );
    const results = await Promise.all(promises);
    // Stop when any page returns empty
    if (results.some(r => !r.data || r.data.length === 0)) break;
    results.forEach(r => allData.push(...r.data));
    from += CONCURRENCY * limit;
  }
}
```

## Token Rotation & Auth Validation (ATLAS / Maxprod)

Trocar a chave de API é operação recorrente. No ATLAS a chave fica **hardcoded em 4
arquivos** — atualizar só um quebra em silêncio (sessão 2026-08-03 confirmou):

1. `scripts/sync-erp.mjs` — usado pelo cron noturno (o que importa para dados)
2. `api/sync.ts` — serverless function Vercel
3. `src/data/syncService.ts` — frontend (fallback de sync no browser)
4. `docs/fontes e apis.md` — documentação

Após trocar, `grep -rl "ANTIGO_TOKEN" .` ainda acha cópias em `.vercel/output/`
(build artifacts). **Não editar** — regeneram no próximo `vercel build`.

### Validar token sem rodar o sync completo (~25 min)

Auth Maxprod é Basic: `Authorization: Basic <TOKEN>`. Faça uma query mínima:

```bash
node -e "
const T='<TOKEN>';
fetch('https://api.maxiprod.com.br/graphql/', {
  method:'POST',
  headers:{'Content-Type':'application/json','Authorization':'Basic '+T},
  body: JSON.stringify({query:'{ empresas { totalCount } }'})
}).then(async r=>console.log('HTTP',r.status, (await r.text()).slice(0,300)));
"
```

- **HTTP 401** → token inválido/revogado
- **HTTP 400 com erro de schema GraphQL** (ex.: `field does not exist on type`) →
  **auth OK**, a query de teste é que está errada. Não confundir com falha de token.

### Cron vs Deploy: o que a troca afeta

O cron `ATLAS — Sync ERP noturno` (`/opt/data/scripts/sync-atlas-erp.sh`) roda
`node scripts/sync-erp.mjs` **localmente** → a troca de token no arquivo vale para o
próximo tick sem deploy. Deploy Vercel só é necessário se o frontend em produção
usar `api/sync.ts`/`syncService.ts` para busca ao vivo (o padrão ATLAS não usa —
frontend consome JSONs estáticos gerados pelo cron).

Para testar o sync com o token novo e acompanhar pelo Hermes, rode direto em
background com `notify_on_complete` (não use o wrapper nohup, que perde o tracking):

```bash
cd /opt/data/atlas-ravello && node scripts/sync-erp.mjs 2>&1 | tee logs/sync-teste-token-$(date +%Y%m%d-%H%M%S).log
```

## Pitfalls

- **Token in source code**: the ATLAS sync script has the Maxprod API token hardcoded.
  For production, use environment variables (`process.env.ERP_TOKEN`).

- **.vercelignore excludes data**: the local JSON fallback is dev-only. Vercel deploys
  exclude `public/data/erp/` to avoid deploying 300MB+ of static data. Production MUST
  use Supabase.

- **Supabase upsert requires `onConflict`**: when upserting, specify the primary key
  column to avoid duplicate rows: `.upsert(data, { onConflict: 'id' })`.

- **Rate limiting**: GraphQL APIs often rate-limit. 400ms between pages is safe for
  most providers. Exponential backoff on failure (5 retries, doubling delay).

- **Crash mid-execution (Node.js OOM/signal kill)**: The `nohup` background wrapper
  spawns the sync and exits — but if Node.js is killed by OOM or a signal during the
  collect or upload phase, the log simply truncates with no error line. The cron
  still reports success (the spawn exited 0). **Diagnosis:** compare log file size
  against historic successful runs (e.g. 41KB vs 2.5KB), check for missing
  `✅ Sincronização concluída!` final line. **Mitigation:** add a `timeout` + retry
  guard in the shell wrapper:
  ```bash
  timeout 3600 node scripts/sync-erp.mjs >> "$LOG" 2>&1
  if [ $? -ne 0 ]; then
    echo "⚠️ Primeira tentativa falhou, retentando..." >> "$LOG"
    sleep 60
    timeout 3600 node scripts/sync-erp.mjs >> "$LOG" 2>&1
  fi
  ```

- **Node.js stdout buffering hides progress**: When `node script.mjs >> logfile 2>&1`,
  stdout is block-buffered (not line-buffered), so upload progress lines may not
  appear in the log until the buffer fills or the process exits. Add
  `node --unhandled-rejections=strict ...` or use `script.mjs 2>&1 | while read line;
  do echo "$line" >> $LOG; done` for real-time logging. Or simply rely on file size
  growth as a liveness indicator.
