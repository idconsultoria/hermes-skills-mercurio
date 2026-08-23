# Migração ArtemisHub: referência de sessão

Repo: `nosterviz/artemishub` (privado; produto interno ID, financiado por contrato
Banese). Frente: React 18 + Vite 6 + TS. Backend próprio: `backend/main.py` (FastAPI +
psycopg + PostgreSQL). Deploy alvo: host Oracle ARM64, URL `artemis.idconsultoria.ai`.

## A arquitetura "double-mode" que foi derrubada

- `src/lib/supabase.ts` — `createClient` só se `VITE_SUPABASE_URL` definido; senão client
  nulo. `isSupabaseConfigured()` = `Boolean(url && key && url.startsWith('https://'))`.
- `src/lib/supabase-db.ts` — camada central; cada função faz
  `if (!isSupabaseConfigured()) { offline.X() } else { supabase.from(...) }`.
- `src/lib/offline-api.ts` — espelho COMPLETO da superfície contra o FastAPI (editais,
  empresas-parque, candidaturas, tags, alertas, analises IA, perfil, documentos, stats).

Decisão: forçar o modo offline como caminho único (remover Supabase por completo para
viver 100% no backend próprio + Oracle).

## O que mudou (edits reais)

| Arquivo | Ação |
|---|---|
| `src/lib/supabase.ts` | Reescrito: `isSupabaseConfigured() → false`; `supabase: any = null` |
| `src/lib/supabase-db.ts` | Reescrito: delegar 100% ao `offline`, preservando exportações (tipos `Candidatura`, `StatusCandidatura`, `TagEdital` + funcs) |
| `src/lib/auth.ts` | Removido `if (isSupabaseConfigured()) await supabase.auth.signOut()` no logout; mantido reexport `isSupabaseConfigured` |
| `src/lib/user.ts` | Removido bloco do Supabase Auth (storage `sb-nowardzbszjjpuhxvrgb-auth-token`); sessão vem do backend multi-usuário |
| `src/lib/app-data-context.tsx` | Removida a perna `supabase.from(...)`; só `offline.fetch*` |
| `src/App.tsx` | `RequireAuth` só usa `isLogado()`; removido `supabase.auth.getSession()` |
| `src/pages/Auth.tsx` | Login só contra `login()` (FastAPI); removido `signInWithPassword` |
| `src/pages/Empresas.tsx` | Blobs `if (!isSupabaseConfigured()) { offline } else { supabase }` → só offline |
| `src/pages/Favoritos.tsx` | Só `updateEdital` offline |
| `src/pages/EditalDetail.tsx` | Só `updateEdital` + `criarCandidatura` offline |
| `package.json` / lock | Removida dep `@supabase/supabase-js` |

## Erro de compilação visto (mapa do que restava)

`tsc` acusou ao rodar `npm run build`:
```
src/App.tsx(...): TS7031 Binding element 'session' implicitly has an 'any' type.
src/pages/EditalDetail.tsx(...): TS7031 Binding element 'data' implicitly has an 'any' type.
```
Ambos em branches mortos do Supabase — limpar o blob inteiro resolve (não tentar satisfazer
o `any` no destructuring do código legado).

## Verificação no bundle

- `npm ls @supabase/supabase-js` → `(empty)`
- `grep -c '@supabase/supabase-js' package-lock.json` → `0`
- Props internos do SDK (ex.: `sb-nowardzbszjjpuhxvrgb`, `createClient`, `auth.getSession`)
  ausentes de `dist/assets/*.js` (só sobrou o helper `isSupabaseConfigured` retornando false).

## Deploy próprio (Oracle)

- frontend: static nginx SPA, `location /api/ { proxy_pass http://backend:8000; }`
  (mesmo origin; `proxy_buffering off`, `proxy_read_timeout 300s` p/ chat que emula streaming).
- backend: `uvicorn main:app --host 0.0.0.0 --port 8000`; env `ARTEMISHUB_DB_URL`,
  `ARTEMISHUB_API_KEY`, `ARTEMISHUB_CORS_ORIGINS`, `OPENCODE_API_KEY`.
- db: `postgres:16-alpine`; seed do dump na 1ª subida via `db/init/01-restore.sh` +
  `db/artemishub.dump` montados em `/docker-entrypoint-initdb.d/`
  (`pg_restore --no-owner --role=app`).
- preview por PR: **stack autônoma** reusa o Postgres de produção pelo `container_name`
  (`artemishub-db`) e rede interna `artemishub_app-net` `external: true`, com database de
  teste `artemishub_pr_<N>` seedada do dump — NÃO usar overlay da base (recriaria o `db`).
- NPM registra proxy `https://<N>.praxis.artemis.idconsultoria.ai` → `artemishub-frontend-<N>`.

## State do deploy (22/08/2026)

Pipeline escrito mas NÃO commitado (aguardando Gustavo): IP do host, usuário SSH,
`SSH_PRIVATE_KEY`, `GHCR_TOKEN`, `POSTGRES_PASSWORD`, rede `proxy_network`, DNS wildcard
de preview. Arquivos prontos em `/opt/data/artemishub`.