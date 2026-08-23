---
name: baas-offline-migration
description: "Migrar SPA que usa Supabase p/ backend próprio offline."
version: 1.0.0
author: "ID Consultoria (Mercúrio), Hermes Agent"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [supabase, firebase, baas, offline, migration, react, vite, fastapi, self-host]
    related_skills: [cicd-oracle-preview]
---

# Migrar SPA de BaaS (Supabase) para backend próprio — Skill

Use quando um SPA (React/Vite) tem **dupla persistência** — usa um Backend-as-a-Service
(ex.: Supabase) *se* configurado, senão cai num **backend local/offline** (ex.: FastAPI +
Postgres) — e você quer **abandonar o BaaS por completo** e mandar tudo para um deploy
próprio (ex.: host Oracle via `cicd-oracle-preview`).

Origem: migração do **ArtemisHub** (`nosterviz/artemishub`) — React + Vite, front usava
`@supabase/supabase-js` com espelho completo offline em `offline-api.ts`. Detalhe da sessão
no padrão em `references/artemis-migration.md`.

## 1. Quando usar

- O SPA tem `if (isSupabaseConfigured())` (ou `!isSupabaseConfigured()`) espalhado, com um
  fallback offline que espelha a mesma superfície de dados.
- Você quer tirar o BaaS do bundle/build (remover a dep, matar código morto) e viver só do
  backend próprio.
- Container/pipeline vai rodar 100% sem o BaaS (deploy no Oracle).

**Não usar para:** apps 100% BaaS (sem fallback offline) — aí é reescrita de dados, não
migração de modo. E **não** edite o deploy/CI daqui (isso é `cicd-oracle-preview`).

## 2. Padrão de dupla persistência (o que você vai derrubar)

Antes, todo acesso passa por uma camada `supabase-db.ts` que faz:
`if (!isSupabaseConfigured()) { usar offline } else { usar supabase }`. O `offline-api.ts`
já implementa TUDO contra o backend local. Sua meta: **forçar a perna offline** e remover a
dependência — sem reescrever as telas (elas já importam as mesmas funções).

## 3. Passos (ordem segura; build verde a cada parada)

1. **Stub do `supabase.ts`** — devolve `configured=false` e um client nulo tipado `any`:
   ```ts
   export function isSupabaseConfigured(): boolean { return false; }
   export const supabase: any = null;   // any p/ o TS aceitar código-legado morto
   ```
   > `any` é pragmático: branches mortos que referenciam `supabase.*` compilam sem a lib.

2. **Colapse `supabase-db.ts`** para delegar 100% ao offline, mantendo a **mesma superfície
   de exportação** (tipos `Candidatura`, `StatusCandidatura`, `TagEdital` + funções
   `buscarCandidaturas`, `criarCandidatura`, ...). Isso evita tocar nas telas.

3. **Remova a dep**: apague `@supabase/supabase-js` do `package.json` E do
   `package-lock.json` (rodar `npm install` atualiza o lock). Confirme:
   - `grep -c '@supabase/supabase-js' package-lock.json` → `0`
   - `npm ls @supabase/supabase-js` → `(empty)`

4. **Varra e limpe os branches Supabase mortos** em `App.tsx`, `Auth.tsx`, `Empresas.tsx`,
   `Favoritos.tsx`, `EditalDetail.tsx`, `user.ts`, `app-data-context.tsx` — remover o
   import e o bloco, mantendo o caminho offline.

5. **`npm run build`** — o erro de compilação é o mapa do que sobrou. No ArtemisHub,
   `tsc` acusou só `Binding element 'session' implicitly has an 'any'` no código morto do
   supabase (antes de limpar o blob inteiro).

## 4. Pitfalls

| Sintoma | Causa | Correção |
|---|---|---|
| `!isSupabaseConfigured()` ao redor de chamada `supabase.*` quebra em runtime | Após forçar `configured=false`, `!isSupabaseConfigured()` vira `true` SEMPRE → um bloco `if (!isSupabaseConfigured()) { supabase.from(...) }` com lógica invertida chama o client `null` | Re-escrever cada blob: manter só o caminho offline; remover o import `supabase` |
| `supabase` tipado `null` quebra `tsc` em branches mortos | strict null checks | Tipar como `any` (§3.1) até limpar os blobs |
| Bundle ainda carrega SDK | Dep removida mas `package-lock` não atualizado, ou import restante | Conferir flag de lock + `grep` por tokens internos no `dist/assets/*.js` |

## 5. Verificação

1. `npm run build` verde.
2. `npm ls @supabase/supabase-js` → vazio; `grep -c` no lock → 0.
3. `grep -rl "createClient\|auth.getSession\|sb-nowardzbszjjpuhxvrgb" dist/assets/*.js`
   → nenhum match (tokens internos do SDK sumiram).
4. Determinação manual de 1-2 telas que usavam `isSupabaseConfigured()` para garantir que
   caíram no caminho offline.

## 6. Companion: deploy próprio

Depois do SPA 100% offline, o deploy no host Oracle segue `cicd-oracle-preview`
(frontend nginx estático SPA + proxy `/api` → backend FastAPI). Nota do ArtemisHub: o
**frontend chama `/api` no mesmo origin** — o nginx do front precisa do
`location /api/ { proxy_pass http://backend:8000; }` (DNS do compose), e `proxy_buffering
off` + `proxy_read_timeout 300s` porque o "chat streaming" devolve resposta única após LLM.

Para seed do **banco de produção na 1ª subida**: monte no container postgres
`db/init/01-restore.sh` + `db/artemishub.dump` em `/docker-entrypoint-initdb.d/` — o entry
point só roda quando o volume está vazio. Restaure com `pg_restore --no-owner --role=app`.