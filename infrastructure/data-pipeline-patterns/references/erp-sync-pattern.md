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
