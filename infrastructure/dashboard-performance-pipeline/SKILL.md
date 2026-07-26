---
name: dashboard-performance-pipeline
description: "Optimize dashboards — move aggregation from browser to backend via materialized views

Load this skill when a SPA dashboard loads slowly or transfers too much data (300 MB to 50 KB target). Covers Supabase materialized views, progressive loading with pagination, Vercel preview branch deployment, and the full backend-aggregation pipeline pattern."
version: 1.0.0
author: Hermes Agent
tags: [dashboard, performance, supabase, vercel, materialized-views, edge-functions, progressive-loading]
type: ToolIntegration
timestamp: 2026-07-26T05:05:12Z
---

# Dashboard Performance Pipeline

Pattern for optimizing a data-heavy SPA dashboard (300 MB → 50 KB, 30-90s → < 3s) by moving aggregation from browser to backend, then deploying a preview.

---

## Phase 1: Backend Aggregation (Supabase)

### 1.1 Materialized Views

Pre-compute KPIs in PostgreSQL to avoid pulling raw tables to the browser:

```sql
CREATE MATERIALIZED VIEW mv_faturamento_mensal AS
SELECT
  DATE_TRUNC('month', "dataEmissao")::date AS mes,
  SUM("faturamentoLiq") AS faturamento,
  SUM("volumeM2") AS volume_m2,
  COUNT(DISTINCT "representanteId") AS reps_ativos
FROM notas_fiscais
WHERE estado = 'EMITIDA' AND "dataEmissao" >= '2024-01-01'
GROUP BY 1 ORDER BY 1;

CREATE UNIQUE INDEX ON mv_faturamento_mensal (mes);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_kpi_views()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_faturamento_mensal;
END;
$$ LANGUAGE plpgsql;
```

Apply via `supabase db query --linked -f migration.sql` if migration history is out of sync.

### 1.2 Edge Function

Serve pre-aggregated KPIs via a Deno Edge Function (~50 KB instead of 300 MB):

```typescript
// supabase/functions/dashboard-kpis/index.ts
Deno.serve(async (req) => {
  const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!);
  const [fatRes, inadRes, rankingRes] = await Promise.all([
    supabase.from("mv_faturamento_mensal").select("*").order("mes", { ascending: false }).limit(24),
    supabase.from("mv_inadimplencia_atual").select("*").single(),
    supabase.from("mv_ranking_reps_ytd").select("*").order("faturamento_ytd", { ascending: false }),
  ]);
  return new Response(JSON.stringify({
    faturamento_mensal: fatRes.data || [],
    inadimplencia: inadRes.data || {},
    ranking_reps: rankingRes.data || [],
    _meta: { generated_at: new Date().toISOString(), source: "materialized_views" }
  }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
});
```

Deploy: `supabase functions deploy dashboard-kpis --project-ref <ref>`

---

## Phase 2: Progressive Frontend Loading

### 2.1 KPIs Hook

Create a lightweight hook that fetches from the edge function immediately:

```typescript
// useKPIs.ts
export function useKPIs() {
  const [kpis, setKPIs] = useState<KPIData | null>(null);
  useEffect(() => {
    fetch(`${SUPABASE_URL}/functions/v1/dashboard-kpis`, {
      headers: { Authorization: `Bearer ${SUPABASE_ANON_KEY}` }
    }).then(r => r.json()).then(setKPIs);
  }, []);
  return { kpis, isLoading: !kpis };
}
```

### 2.2 Non-Blocking Dashboard

Remove the full-data loading spinner. Render immediately with KPIs; load heavy data in background:

```tsx
// AtlasDashboard.tsx — key change
// BEFORE: {!isLoaded ? <Spinner/> : <ActiveComponent/>}
// AFTER:  always render <ActiveComponent/>, show banner while loading

{!isLoaded && (
  <Banner>Carregando dados detalhados...</Banner>
)}
<ActiveComponent />
```

### 2.3 KPI Fallback in Cockpit

When full data (NFs) hasn't loaded yet, use edge function KPIs for summary cards:

```typescript
const hasFullData = nfs.length > 0;
const effectiveData = hasFullData ? dados : kpiDados;
// Use effectiveData throughout the component
```

---

## Phase 3: Data Mapping Gotchas

When loading from Supabase flat tables (not nested GraphQL), field names differ:

| GraphQL (ERP syncService) | Supabase table | Frontend code |
|---|---|---|
| `cr.cliente.apelido` | `clienteNome` (string) | Use `(cr as any).clienteNome \|\| cr.cliente?.apelido` |
| `nf.destinatarioOuRemetente.apelido` | `clienteNome` (string) | `nf.clienteNome \|\| nf.destinatarioOuRemetente?.apelido` |

Always support both shapes with a fallback chain.

---

## Phase 4: Vercel Preview Deploy

### Prebuilt flow (avoids stale content)

```bash
vercel build --yes
rm -rf .vercel/output/static/data/erp/   # strip heavy local data
vercel deploy --prebuilt --yes            # preview URL
vercel --prod --yes                       # alias to preview domain
```

### Common pitfalls

1. **SSO Protection (401):** New Vercel projects under team accounts enable SSO by default. Disable via API:
   ```python
   PATCH /v9/projects/{id}?teamId={team}  { "ssoProtection": null }
   ```

2. **Missing env vars:** `vercel build` in a new project doesn't pull from `.env`. Add via Management API:
   ```python
   POST /v9/projects/{id}/env?teamId={team}  { "key": "...", "value": "...", "target": ["preview","production","development"], "type": "encrypted" }
   ```

3. **Heavy public/ files:** `.vercelignore` doesn't prevent `vercel build` from copying `public/` to `.vercel/output/static/`. Always `rm -rf` heavy dirs between build and deploy.

4. **New project created accidentally:** `vercel build --yes` may create a new project instead of linking to existing. Check `.vercel/project.json` after build.

---

## Refresh After Data Sync

After syncing new data to Supabase, refresh materialized views:

```bash
supabase db query --linked "REFRESH MATERIALIZED VIEW mv_faturamento_mensal; REFRESH MATERIALIZED VIEW mv_inadimplencia_atual; REFRESH MATERIALIZED VIEW mv_ranking_reps_ytd;"
```

Verify edge function returns fresh data:
```bash
curl -s "https://<ref>.supabase.co/functions/v1/dashboard-kpis" \
  -H "Authorization: Bearer $ANON_KEY" | jq '.faturamento_mensal[-1]'
```
