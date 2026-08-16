# Upgrade major de Next.js — Zera (14 → 16, 14/08/2026) — como migrar

## Decisão R-02 (D18) — o processo, não só o resultado

`npm audit` apontava 2 high (next@14.2.35 + postcss aninhado). O usuário pediu contexto ANTES de
decidir e depois discussão de complicações (16 vs 17) — **não decidir upgrade major sem apresentar:
(1) o que o audit aponta (advisories reais), (2) por que NÃO é explorável hoje (grep do código:
Server Actions/rewrites/i18n/next-image não usados; staging interno sem TLS), (3) custo/risco por
opção com fontes oficiais.** O usuário escolheu **A2: pular direto para Next 16 (Active LTS, 16.3.1)
+ React 19.2 num lote**, aceitando o salto duplo de majors.

## Passos que funcionaram (16.3.1 + react/react-dom 19.2.8)

1. **Codemod:** `npx @next/codemod@canary upgrade latest` — TRAVA no prompt interativo (Vercel),
   mas aplica o bump de deps antes de travar. Renomeação `middleware.ts → proxy.ts` feita MANUALMENTE.
2. **`npx next typegen`** — gera os tipos `PageProps`/`LayoutProps` async corretos.
3. **Sync request APIs removidas no 16** (o shim do 15 some): `cookies()/headers()/draftMode()/
   params/searchParams` DEVEM ser awaited. `useSearchParams()` (hook client) NÃO muda.
4. **`middleware.ts` → `proxy.ts`**: renomear arquivo + `export function middleware` →
   `export function proxy` + flags de config (`skipMiddlewareUrlNormalize` →
   `skipProxyUrlNormalize`). Proxy roda em runtime nodejs (middleware antigo sem edge = rename direto).
5. **Turbopack é o bundler DEFAULT** no 16 (dev e build). Build FALHA se houver config webpack —
   o app não tinha `webpack()` no `next.config.js` (só `async headers()` CSP), então ok.
6. **React 19.2 obrigatório no App Router**: namespace JSX mudou (corrigir 2 arquivos);
   `forwardRef` está DEPRECADO mas ainda compila (deixar; conversão adiada sem ganho);
   `useRef` agora exige argumento.
7. **Não usados no app (verificar com grep antes de temer):** `next/image` (defaults mudaram no 16:
   minimumCacheTTL 4h, qualities [75], imageSizes sem 16, local-IP bloqueado, max 3 redirects),
   parallel routes (`default.js` obrigatório por slot), `next lint` (removido — usar ESLint direto),
   AMP, `serverRuntimeConfig`/`publicRuntimeConfig` (removidos).
8. **Node 20.9+ mínimo** (CI já usa Node 20; lockfile v3 compatível). TypeScript 5.1+.

## Gates de aceite (todos verdes no lote real)

- `npm audit` → **0 vulnerabilities** (o postcss aninhado do Next 14 some com o upgrade)
- vitest 119/119 · E2E Playwright 37/37 (API real Modo A) · build Turbopack (19 rotas + `ƒ Proxy`) · tsc
- CSP/security headers do `next.config.js` intactas e validadas (`curl -I` no server de produção)

## Pitfalls de ambiente do lote real

- **Porta 3000 ocupada pelo WhatsApp bridge** → E2E/next start em porta alternativa
  (`E2E_BASE_URL`/`PORT`), cenário já previsto no `playwright.config.ts`.
- **PYTHONPATH do host contamina o venv do repo** (pydantic_core quebrado, site-packages 3.13):
  `env.pop("PYTHONPATH", None)` no subprocess ou reinstalar deps em venv limpo.
- `.venv` do repo pode estar quebrado — o Pi cost criou `/tmp/zera-venv` (uv, python 3.12) como
  alternativa para rodar a suíte.
- Se um vendor/codemod travar em prompt interativo, aplicar o bump manualmente e seguir — não desistir.

## Fontes de referência para o próximo upgrade

- Guia oficial: `nextjs.org/docs/app/guides/upgrading/version-16` (e a cadeia 14→15→16)
- `versions.dev/modernize/nextjs/upgrade-to-nextjs-16` — tabela de compatibilidade 15 vs 16
- Recomendação oficial: quem está no 14 deve ir ao 15 PRIMEIRO e depois 15→16 (salto suave);
  pular 14→16 direto é possível (feito aqui) mas concentra React 18→19 + Turbopack + proxy no mesmo lote.
