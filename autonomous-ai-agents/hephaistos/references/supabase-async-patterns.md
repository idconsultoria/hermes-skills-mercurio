# Supabase Async Patterns — Pitfalls & Fixes

> O cliente Supabase JS v2 retorna `PostgrestResponse` via `PromiseLike`, não `Promise`. Isso causa erros de TypeScript ao usar `.then().catch()`.

## O Problema

```typescript
// ❌ FALHA — .catch() não existe em PromiseLike<void>
db.from("leads").insert([payload]).then(({ error }) => {
  if (error) console.warn("Insert failed:", error.message);
}).catch((err) => {
  console.warn("Network error:", err);
});
// TS error: Property 'catch' does not exist on type 'PromiseLike<void>'
```

## Fix 1: async/await (preferido)

```typescript
// ✅ CORRETO — usar async/await com try/catch
const db = getSupabase();
if (db) {
  try {
    const { error } = await db.from("leads").insert([payload]);
    if (error) console.warn("Insert skipped:", error.message);
  } catch (err: unknown) {
    console.warn("Network error:", err instanceof Error ? err.message : err);
  }
}
```

**Requisito:** a função que chama deve ser `async`. Para handlers de evento:
```typescript
// ❌ handler não-async
<form onSubmit={(e) => { ... await ... }}>

// ✅ handler async
<form onSubmit={async (e) => { ... await ... }}>
```

## Fix 2: .then(onFulfilled, onRejected) com dois argumentos

```typescript
// ✅ CORRETO — usar os dois argumentos de .then()
db.from("leads").insert([payload]).then(
  ({ error }) => {
    if (error) console.warn("Insert skipped:", error.message);
  },
  (err) => {
    console.warn("Network error:", err);
  }
);
```

## Fix 3: Wrapping em Promise<void> (para variáveis tipadas)

Quando o resultado precisa ser atribuído a uma variável `Promise<void>`:

```typescript
// ❌ FALHA — PromiseLike não assignable a Promise
let supabasePromise: Promise<void> = Promise.resolve();
supabasePromise = db.from("leads").insert([...]).then(...);
// TS error: Type 'PromiseLike<void>' is not assignable to type 'Promise<void>'

// ✅ CORRETO — envolver em new Promise
const insertResult = db.from("leads").insert([payload]);
let supabasePromise: Promise<void> = new Promise<void>((resolve) => {
  insertResult.then(
    ({ error }) => {
      if (error) console.warn("Insert skipped:", error.message);
      resolve();
    },
    () => {
      console.warn("Network error — saved to localStorage only");
      resolve();
    }
  );
});

// Agora pode usar:
await supabasePromise;
```

## Contexto

- **Onde aparece:** `page.tsx`, `DiagnosticWizard.tsx`, `CaptureGate.tsx` — qualquer componente que faz insert/update no Supabase
- **Versão afetada:** Supabase JS v2.x (testado com v2.108.0)
- **Validado em:** Desconsultor, 2026-06-16
