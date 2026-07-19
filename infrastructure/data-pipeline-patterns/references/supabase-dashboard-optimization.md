# Supabase Dashboard Optimization — Materialized Views + Edge Functions

Pattern from ATLAS Ravello (`perf/data-loading` branch). Reduces dashboard load from 300 MB / 30-90s
to ~50 KB / <3s by moving aggregation from browser to database.

## Problem

Dashboard loads 380K+ rows (62K NFs, 288K contas a receber, 26K pedidos) into the browser
before rendering anything. All business-rule processing happens client-side in `erpProcessor.ts`.

## Solution: 3-layer architecture

```
┌──────────────────────────────────────────────┐
│ BROWSER                                       │
│  useKPIs() — fetches ~50 KB JSON, caches     │
│  useSWR with IndexedDB fallback              │
└──────────────────┬───────────────────────────┘
                   │ HTTPS (anon key)
┌──────────────────▼───────────────────────────┐
│ SUPABASE EDGE FUNCTION (Deno)                 │
│  /functions/v1/dashboard-kpis                │
│  Queries materialized views in parallel      │
│  Returns pre-aggregated JSON                 │
│  Cold start: ~200ms, warm: ~50ms             │
└──────────────────┬───────────────────────────┘
                   │ SQL
┌──────────────────▼───────────────────────────┐
│ POSTGRESQL MATERIALIZED VIEWS                 │
│  mv_faturamento_mensal (24 months)           │
│  mv_inadimplencia_atual (1 row)              │
│  mv_ranking_reps_ytd (16 rows)              │
│  Refresh: manual or pg_cron every 6h         │
└──────────────────────────────────────────────┘
```

## Step-by-step implementation

### 1. Create materialized views via Management API

```bash
curl -s -X POST 'https://api.supabase.com/v1/projects/{REF}/database/query' \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE MATERIALIZED VIEW mv_faturamento_mensal AS SELECT ..."}'
```

**Key columns to include:** pre-computed fields from ETL (`faturamentoLiq`, `volumeM2`,
`representanteOuVendedor1Nome`) — do NOT include raw item-level data (stripped during ETL
to keep rows lightweight).

### 2. Deploy Edge Function

```bash
npx supabase functions deploy dashboard-kpis \
  --project-ref {REF} \
  --no-verify-jwt
```

Edge Function code pattern:
```typescript
Deno.serve(async (req) => {
  const supabase = createClient(url, anonKey);
  const [fat, inad, ranking] = await Promise.all([
    supabase.from("mv_faturamento_mensal").select("*").limit(24),
    supabase.from("mv_inadimplencia_atual").select("*").single(),
    supabase.from("mv_ranking_reps_ytd").select("*"),
  ]);
  return new Response(JSON.stringify({ faturamento: fat.data, ... }));
});
```

### 3. Frontend hook with caching

```typescript
function useKPIs() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch('https://{REF}.supabase.co/functions/v1/dashboard-kpis', {
      headers: { Authorization: `Bearer ${ANON_KEY}` }
    }).then(r => r.json()).then(setData);
  }, []);
  return data;
}
```

## Pitfalls

- **Materialized views need explicit refresh**. They don't auto-update. Use:
  ```sql
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_faturamento_mensal;
  ```
  `CONCURRENTLY` requires a UNIQUE index on the view.

- **Edge Function cold starts**: first request after deploy or inactivity takes ~200ms.
  Subsequent requests are ~50ms. For production, set up a cron ping every 5 minutes.

- **anon key has limited permissions**: the Edge Function uses the anon key, so the
  materialized views must be in the `public` schema and have appropriate RLS policies
  (or the function must use the service_role key).

- **Don't include raw item details** in the materialized views — the ETL strips
  `itensDaNotaFiscalEmitidaOuRecebida` before saving to Supabase. If you need
  format segmentation (45x45 vs 37x59), compute it from `detailed_sales` JSON
  or add a pre-computed column during ETL.

## Results (ATLAS Ravello)

| Metric | Before | After |
|---|---|---|
| Data transferred | ~300 MB | ~50 KB |
| Time to first interaction | 30-90s | <2s |
| Browser memory | ~500 MB | ~20 MB |
| Supabase rows scanned | 380K+ | 40 (aggregated) |
