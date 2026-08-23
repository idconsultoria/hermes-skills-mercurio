# Deploy de protótipo estático (SPA por hash) no Vercel — modo headless

Receita validada para construir um protótipo rápido (HTML+CSS+JS vanilla, dados mockados,
roteamento por hash) e publicá-lo no Vercel a partir de um ambiente headless/segundo container.

## Estrutura recomendada (estática, sem build)
```
app/  (index.html, styles.css, app.js, data/mock.js, assets/...)
app/vercel.json        → SPA catch-all
```
`vercel.json`:
```json
{ "$schema":"https://openapi.vercel.sh/vercel.json","cleanUrls":true,"trailingSlash":false,
  "rewrites":[{"source":"/(.*)","destination":"/index.html"}] }
```

## Autenticação headless (device flow)
- `vercel login` (rodar em pty) imprime `Visit https://vercel.com/oauth/device?user_code=XXXX-XXXX`.
  Repasse a URL ao usuário; ele autoriza à parte; o CLI completa sozinho. Confirmar com `vercel whoami`.

## Instalação do CLI (permissão de escrita global costuma faltar)
- `npm install -g vercel` pode falhar (permições). Instale LOCAL no projeto:
  `npm init -y && npm install vercel`, e chame via `./node_modules/.bin/vercel`
  (ou `export PATH="$PWD/node_modules/.bin:$PATH"`).

## Publicar (produção, não-interativo)
- `cd <dir-do-projeto> && vercel deploy --prod --yes`
- Retorna duas URLs: `Production  https://<x>-<hash>.vercel.app` e `Aliased https://<proj>.vercel.app`
  (esta é a URL estável para compartilhar/colocar no QR).

## ⚠️ Pitfall crítico — SPA por hash: setar o MESMO hash não re-renderiza
Num router por hash, `location.hash = '#/admin'` quando o hash já é `#/admin` NÃO dispara
`hashchange`, então a view não re-renderiza. Sintoma típico: tela de login que "não passa" — o
submit faz `setLoggedIn(true)` (a sessão existe) mas continua na mesma tela.
Correção: em handlers de mudança de estado que não trocam a rota (login, logout), chamar a função
de render `route()` DIRETAMENTE (é idempotente): `location.hash='#/admin'; route();`.

## Rotas /c/<token> dão 404 — inofensivo para hash-SPA
O fragmento `#/...` nunca vai ao servidor; o navegador só pede `/` (HTTP 200) e o JS lê o hash.
Monte URLs canônicas de QR como `location.origin + location.pathname + '#/c/<token>'` — não
`/c/<token>` puro (esse caminho retorna 404, mas não é usado).

## Verificação end-to-end (não confiar só no build local)
Validar a URL PÚBLICA com Playwright headless contra a versão no ar:
- Carregar `https://<proj>.vercel.app/#/<rota>` e ler `body.innerText` (confere colaborador renderizado,
  badges como "DOCUMENTO VENCIDO"/"CREDENCIAL INATIVA", dashboard pós-login).
- Reproduzir fluxos reais (ex.: `fill` + `click` no `#login-form`, assertar que re-renderizou).
- Registrar `console` errors e `pageerror` num listener — erro de console aponta handler quebrado
  (clientes: `p.on('console', m=>m.type()==='error'&&errs.push(m.text()))`).
- Atestar cada rota (raiz, `/c/<token>`, `/admin`) num único script.
Nota: o Node resolve `node_modules` a partir da pasta DO SCRIPT, não do cwd — rode o script na pasta
onde o playwright foi instalado, senão `ERR_MODULE_NOT_FOUND`.

## Organização do deploy
- Nunca publique a pasta com `package.json`/`node_modules`: se você rodou `npm install vercel` no
  projeto, o Vercel pode tratar como projeto Node em vez de estático. Deploie de um diretório LIMPO
  copiando só o site estático + `vercel.json` (sem artefatos npm).
