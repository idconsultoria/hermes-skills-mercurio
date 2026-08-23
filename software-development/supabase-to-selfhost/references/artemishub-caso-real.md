# Caso real: artemishub (22/08/2026)

Primeira aplicação completa da skill `supabase-to-selfhost` num produto ID.

## Topologia
- Repo: `nosterviz/artemishub` (privado, **branch default `main`**). Conta dona do
  token GITHUB é `idconsultoria`; o repo está sob o user `nosterviz` (gh summary listou
  tanto repos de `idconsultoria`/`gustavomello9600` quanto de `nosterviz` — procurar
  por nome, não pela conta).
- Stack: **React + Vite + TS** (front SPA) + **FastAPI** (`backend/main.py`, ~1775 linhas,
  lib backend offline real, banco `artemishub` Postgres, owner `app`) + **Postgres**.
- Dump do banco versionado em `db/artemishub.dump` (custom pg_dump, schema+dados:
  editais, empresas, candidaturas, analises_ia, usuários, sessoes, configuracoes).
  Restore: `pg_restore --no-owner --role=app db/artemishub.dump` sobre DB `artemishub`
  owner `app`.
- URL de produção alvo: `https://artemis.idconsultoria.ai`.
- Deploy objetivado no Oracle host via `cicd-oracle-preview` (GHCR arm64, deploy SSH,
  NPM; docker daemon NÃO acessível de dentro do container do Mercúrio).

## Arquivos tocados na remoção do Supabase
- `src/lib/supabase.ts` → stub (retorna `false`, `supabase: any = null`).
- `src/lib/supabase-db.ts` → colapsado para delegar ao `offline-api` (preservou tipos
  `Candidatura`, `StatusCandidatura`, `TagEdital`, `PortfolioHealth` e funções `buscar*`/
  `criar*`/`atualizar*`/`excluir*`/`calcularSaudePortfolio`).
- `src/lib/auth.ts`, `src/lib/user.ts`, `src/lib/app-data-context.tsx` → removidos
  branches `isSupabaseConfigured()`/`supabase.*` (login fica via `/api/auth/login`).
- `src/pages/{Auth,App,Empresas,EditalDetail,Favoritos}.tsx` → removidos branches
  supabase + imports.
- `package.json`/`package-lock.json` → removido `@supabase/supabase-js`.

## O que NÃO mexer / reparos
- `offline-api.ts` mantém `isOfflineMode = () => !isSupabaseConfigured()` (agora sempre
  true) — funciona, mas código-legado cosmético.
- As migrations `supabase/migrations/*.sql` e `render.yaml`/`vercel.json` ficaram no
  repo (histórico); a remoção de Supabase é do app runtime, não do histórico git.
- Build valida com `tsc && vite build` (Vite 6) — precisa `npm install` primeiro.

## Pitfall específico do artemishub
O `Empresas.tsx` tinha `if (!isSupabaseConfigured()) { apiDelete… } else { supabase… }` —
lógica invertida; simplificado para `apiDeleteEmpresa(id)` direto. Ver pitfall principal
da skill.