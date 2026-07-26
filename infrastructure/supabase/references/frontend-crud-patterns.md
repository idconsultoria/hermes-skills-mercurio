# Frontend Supabase CRUD Patterns

Patterns for building a React + Supabase data layer — covering upsert with unique constraints, batch operations, CSV import with Brazilian format, and localStorage fallback.

---

## 1. Upsert with ON CONFLICT

When a table has a UNIQUE constraint spanning multiple columns (e.g., `representanteId, mes, ano`), use `upsert` with `onConflict` to avoid duplicate-key errors:

```ts
const { error } = await supabase
  .from('metas')
  .upsert(row, {
    onConflict: 'representanteId, mes, ano',
    ignoreDuplicates: false,  // false = REPLACE on conflict
  });
```

**Types:**
```ts
interface MetaRow {
  id?: number;           // serial PK — omit on insert, present on update
  representanteId: number | null;
  representanteNome: string;
  mes: number;
  ano: number;
  metaFaturamento: number;
}
```

---

## 2. Batch Upsert (chunked)

Supabase REST API has a ~100-row limit per upsert call (payload size). Chunk for reliability:

```ts
const chunkSize = 100;
let allOk = true;

for (let i = 0; i < rows.length; i += chunkSize) {
  const chunk = rows.slice(i, i + chunkSize);
  const { error } = await supabase
    .from(TABLE)
    .upsert(chunk, {
      onConflict: 'representanteId, mes, ano',
      ignoreDuplicates: false,
    });
  if (error) {
    console.error(`Chunk ${i / chunkSize} failed:`, error);
    allOk = false;
  }
}
```

---

## 3. Delete by PK

```ts
await supabase.from(TABLE).delete().eq('id', dbId);
```

Track the DB `id` (`_dbId` field) alongside your local state so deletes propagate correctly.

---

## 4. LocalStorage Fallback Pattern

Keep a write-through cache in localStorage for offline resilience:

```ts
// On load: try Supabase first, fall back to localStorage
const rows = await fetchMetas(ano);
if (rows.length > 0) {
  setMetas(rows.map(r => /* map to local shape */));
} else {
  const cached = localStorage.getItem(STORAGE_KEY);
  if (cached) setMetas(JSON.parse(cached));
}

// On save: write both
const ok = await upsertMetas(rows);
if (ok) localStorage.setItem(STORAGE_KEY, JSON.stringify(localMetas));
```

---

## 5. CSV Import (Brazilian Format)

Parser that handles:
- Comma as decimal separator (`150000,50`)
- Quoted fields (`"Nome do Rep"`)
- Auto-resolve `representanteNome` → `representanteId` via ERP data map

**Expected CSV format:**
```csv
Representante,Mês,Ano,Meta Faturamento (R$)
"João Silva",1,2026,150000
"Maria Souza",2,2026,200000,50
```

**Key implementation notes:**
- Parse header case-insensitively
- Strip `R$`, `.` (thousands separator), replace `,` with `.` for JS parseFloat
- Reject lines where representative name doesn't match any ERP rep
- Merge results with existing state (overwrite by composite key `repId+mes+ano`)
- Provide a downloadable model CSV for the user
- Reference: `src/data/metasService.ts` in `idconsultoria/atlas-ravello`
