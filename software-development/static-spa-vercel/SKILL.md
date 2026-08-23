---
name: static-spa-vercel
description: "Build static SPA prototypes and deploy to Vercel."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [prototype, spa, vercel, deploy, static, playwright, qr]
    related_skills: [dogfood, html-pdf-fidelity, google-workspace]
type: Orchestrator
timestamp: 2026-08-20T00:00:00Z
---

# Static Hash-SPA → Vercel (protótipo rápido + deploy + verificação)

Padrão para construir um protótipo funcional de baixo esforço (SPA estática em HTML+CSS+JS
vanilla, com dados MOCKADOS no front) e publicá-lo no **Vercel** a partir de um ambiente
headless/sem GUI, validando depois de ponta a ponta na URL pública. Validado num protótipo de
"credenciais digitais" com página pública via QR + painel admin (20/08/2026).

## Quando usar
- Precisa demonstrar funcionalidades (página pública, painel admin, QR, listas) sem backend,
  com dados de mentira, e o usuário quer uma URL pública compartilhável.
- Deploy rápido em Vercel de um app estático, com fluxo de autenticação headless.
- Não usar para: produto com backend real, build/SSR Next (aí é pipeline de produto).

## Estrutura (estática, sem build)
```
app/  → index.html, styles.css, app.js, data/mock.js, assets/... , vercel.json
```
`vercel.json` (SPA catch-all):
```json
{ "$schema":"https://openapi.vercel.sh/vercel.json","cleanUrls":true,"trailingSlash":false,
  "rewrites":[{"source":"/(.*)","destination":"/index.html"}] }
```

## Fluxo
1. **Construir** o app estático (separar dados mock em `data/mock.js`; QR com lib vendida
   localmente, ex. qrcodejs, para funcionar offline).
2. **Autenticar no Vercel** (device flow, headless):
   - `vercel login` (rodar em pty) imprime `Visit https://vercel.com/oauth/device?user_code=XXXX-XXXX`.
   - Repassar a URL ao usuário; ele autoriza à parte; o CLI termina. Confirmar com `vercel whoami`.
3. **Deploy** (produção, não interativo): `cd app && vercel deploy --prod --yes`.
   Retorna `Production https://<x>-xxx.vercel.app` + `Aliased https://<proj>.vercel.app` (URL estável).
4. **Verificar e2e na URL pública** com Playwright headless (não confiar só no build local).

## Pitfalls (lições reais)
- **SPA por hash: setar o MESMO hash não re-renderiza.** `location.hash='#/admin'` quando o hash
  já é `#/admin` NÃO dispara `hashchange` → a view fica parada. Sintoma típico: tela de login que
  "não passa" (o submit seta a sessão mas não avança). Correção: em handlers de mudança de estado
  que não trocam a rota (login/logout), chamar a função de render `route()` DIRETAMENTE após setar
  o hash (é idempotente): `location.hash='#/admin'; route();`.
- **Rotas `/c/<token>` dão 404 — inofensivo p/ hash-SPA.** O fragmento `#/...` nunca vai ao
  servidor; o navegador só pede `/` e o JS lê o hash. Montar URLs canônicas de QR como
  `location.origin + pathname + '#/c/<token>'` — não `/c/<token>` puro.
- **`vercel login` exige pty** para imprimir a URL e completar o device flow. `npm install -g vercel`
  pode falhar por permissão → instalar LOCAL: `npm init -y && npm install vercel`, chamar via
  `./node_modules/.bin/vercel` (ou `export PATH="$PWD/node_modules/.bin:$PATH"`).
- **Não publiques pasta com `package.json`/`node_modules`**: se você rodou `npm install vercel`
  no projeto, o Vercel pode tratar como projeto Node em vez de estático. Deploie de um diretório
  LIMPO com só o site estático + `vercel.json`.
- **Playwright resolve `node_modules` a partir da pasta DO SCRIPT, não do cwd** → rode o script de
  verificação na pasta onde o playwright foi instalado, senão `ERR_MODULE_NOT_FOUND`.

## Verificação e2e obrigatória
Com Playwright headless contra a URL pública:
- Carregar `https://<proj>.vercel.app/#/<rota>` e ler `body.innerText` (confere conteúdo renderizado,
  badges como "DOCUMENTO VENCIDO"/"CREDENCIAL INATIVA", dashboard pós-login).
- Reproduzir fluxos reais (ex.: `fill` + `click` no `#login-form`; assertar que re-renderizou).
- Registrar `console` errors e `pageerror` no listener — erro de console aponta handler quebrado.
- Atestar cada rota (raiz, `/c/<token>`, `/admin`) num único script.

## References
- `references/static-spa-vercel-deploy.md` — receita completa detalhada (auth device flow, vercel.json, pitfall do hash, organização do deploy).
