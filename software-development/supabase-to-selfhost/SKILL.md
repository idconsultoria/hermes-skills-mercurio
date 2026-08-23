---
name: supabase-to-selfhost
description: "Use ao abandonar Supabase: backend próprio offline único."
version: 1.0.0
author: "ID Consultoria (Mercúrio), Hermes Agent"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [supabase, migration, self-host, react, fastapi, offline, baas]
---

# Remover Supabase → backend próprio (migração de self-host)

Padrão ID: quando um produto React usa Supabase mas tem um **fallback offline**
(backend próprio, ex.: FastAPI + PostgreSQL) espelhando a mesma superfície de dados,
"abandonar o Supabase" = tornar o fallback o **caminho único** e remover a dependência
`@supabase/supabase-js` do bundle. Caso real: artemishub (React + FastAPI + dump PG,
deploy no Oracle host). Origem: migração 22/08/2026.

## Quando usar
- Usuário pede para **abandonar/remover o Supabase** de um projeto.
- Forçar o modo offline como único caminho (não mais dual-persistence).
- Antes de mover a stack para um host próprio (Oracle) — o front remanescente de
  Supabase ficaria sem alvo.

**Arquitetura típica (já existente em apps ID):**
- `src/lib/supabase.ts` — obtém `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY` e cria o
  client via `createClient`.
- `src/lib/<baas>-db.ts` — facade com `if (isSupabaseConfigured()) { …supabase… } else { …offline… }`.
- `src/lib/offline-api.ts` — cliente do backend próprio (FastAPI), espelha a superfície.
- `src/pages/*.tsx` — branches per-page checando `isSupabaseConfigured()`.

Se o fallback offline NÃO espelha toda a superfície usada pelas telas, o primeiro passo é
completá-lo antes de remover o BaaS (senão quebra features).

## Passos

1. **Stub o módulo `supabase.ts`** para sempre offline:
   ```ts
   export function isSupabaseConfigured(): boolean { return false; }
   export const supabase: any = null; // any só p/ compilar branches-legado mortos
   ```
   `null` com tipo `any` faz o TS aceitar referências-mortas `supabase.*`; `any` NÃO é
   desculpa para manter o código morto — é etapa intermediária, remove depois (§6).

2. **Colapse a facade** (`supabase-db.ts`) para delegar 100% ao offline, **preservando as
   exportações** que as telas importam (tipos `Candidatura`, `StatusCandidatura`,
   `TagEdital` e funções `buscar*`/`criar*`/`atualizar*`/`excluir*`). Telas fazem
   `import { x } from '@/lib/supabase-db'` — se você apagar o módulo, quebra N páginas.
   Mantenha como fina camada de passagem sobre `offline-api`.

3. **Remova a dependência** `@supabase/supabase-js` do `package.json` e rode
   `npm install` (atualiza o lock). Confira que sumiu do bundle:
   ```bash
   grep -c '@supabase/supabase-js' package-lock.json   # → 0
   grep -rl "sb-nowardzbsjzzpuhxvrgb\|auth.getSession\|createClient" dist/assets/*.js  # → vazio
   npm ls @supabase/supabase-js                          # → (empty)
   ```

4. **Remova branches por página** que chamam `supabase.*` (ex.: sessão no `App.tsx`,
   login no `Auth.tsx`, favorito em `EditalDetail.tsx`/`Favoritos.tsx`, CRUD no
   `Empresas.tsx`). Mantenha só o caminho offline (`offline.api*` / `updateEdital` / etc).

5. **Remova imports** de `@/lib/supabase` que sobraram em cada página.

6. **Rode `npm run build`** (no Dockerfile ID é `tsc && vite build`). O `tsc` flagra
   branches mortos que ficaram: `Binding element 'session' implicitly has an 'any' type`.
   Remova o próprio branch morto (não "corrija" — é código que nunca executa).

7. **Verifique o bundle** (grep acima) e o `git status` (esperar alterações só nos
   arquivos tocados + lock).

## Pitfalls (mordidos de verdade)

| Sintoma | Causa | Correção |
|---|---|---|
| Build quebra com `Binding element 'X' implicitly has an 'any' type` | Branch morto com destructuring de `supabase` (agora `null`/`any`) | Remover o branch, não digitar o `any` explícito |
| CRUD de empresa/edital falha em runtime | Telas com lógica INVERTIDA: `if (!isSupabaseConfigured()) { supabase.* }` — como `isSupabaseConfigured()` é sempre `false`, o branch "offline" era o `else` e o guard mandava pra supabase | Inverter: manter `offline.api*` no branch que executa, apagar o `supabase.*` |
| `supabase` ainda no bundle | Dependência não removida do `package.json`/lock | `npm install` pós-remoção + grep de verificação |

## Pitfall do editor: `!isSupabaseConfigured()` de cabeça pra baixo
No `Empresas.tsx` o código original era `if (!isSupabaseConfigured()) { apiDelete… } else { supabase… }`.
Com o stub `isSupabaseConfigured() === false`, `!false === true` → já executava o offline.
Mas a leitura parece errada e arrisca: candidatos a reescrever o `else` errado. Ao migrar,
simplifique para `await apiDeleteEmpresa(id)` direto (sem o guard) — o offline é o único
caminho agora.

## Verificação
1. `npm run build` verde (sem `@supabase`, sem erros TS).
2. `grep -rl "supabase" dist/assets/*.js` retorna **só arquivos que citam o helper
   `isSupabaseConfigured`** (exportação legada retornando `false`) — NUNCA tokens do SDK
   (`createClient`, `sb-*` storage, `auth.getSession`).
3. Login real contra `POST /api/auth/login` do backend FastAPI funciona (não mais
   `supabase.auth.signInWithPassword`).
4. `git diff` mostra só frontend tocado + `package-lock.json`.