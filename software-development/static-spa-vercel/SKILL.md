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

## Entregar a URL pública (o deploy não termina no `Ready`)

O `Ready in Ns` só diz que o build subiu. Antes de mandar o link ao usuário:

1. **Descobrir a URL real.** `vercel project ls` traz a coluna `Latest Production URL`;
   `vercel inspect <deployment>` lista os aliases daquele deploy. Nome de projeto já usado por
   outra conta ganha **sufixo aleatório** (`<projeto>-<palavra>.vercel.app`) — nunca deduza a URL
   do nome do projeto. Ao capturar a URL do output do deploy por regex, aceite **hífens**
   (`https://[a-z0-9-]+\.vercel\.app`): com `[a-z0-9]+` o match para no primeiro hífen, o padrão
   falha em silêncio e o `vercel alias set` simplesmente não roda — o alias continua no deploy antigo.
3. **Criar alias limpo e estável:** `vercel alias set <deployment>.vercel.app nome-limpo.vercel.app`.
   Alias manual **não acompanha** o próximo deploy: reaponte depois de cada `vercel --prod` (o
   alias automático pode ficar preso a um deployment órfão e responder `x-vercel-error: NOT_FOUND`).
3b. **Correção depois de entregar: NÃO repontar a URL já enviada.** Se o link já foi para o
   usuário (ou o cliente já o viu), publique a correção em **projeto/deploy novo** e deixe o
   endereço antigo congelado — é o que o usuário pede quando a entrega está em uso ("deixe a url
   atual intacta e suba o deploy de correções em outra"). Receita: copie a pasta do site para um
   diretório limpo (`rm -rf .vercel .env.local`), `vercel link --yes --project <novo-nome>`,
   `vercel --prod --yes`, desligue a proteção do projeto novo e **prove que o antigo não mudou**
   (baixe o mesmo JS/CSS das duas URLs e mostre a string-marcador da correção ausente na antiga e
   presente na nova). Substituir por cima o link em uso tira do cliente a referência que ele já
   validou.
3. **Desligar a Deployment Protection quando o destino é o cliente navegar:**
   `vercel project protection <projeto>` mostra `ssoProtection`; desligue com
   `vercel project protection disable <projeto> --sso` (o CLI **rejeita `--yes`** nesse
   subcomando — sem ele roda não interativo). Com SSO ligado, todo acesso anônimo a
   `*.vercel.app` cai em login do Vercel ou em **404 `NOT_FOUND`**, indistinguível de deploy
   quebrado — é a primeira coisa a checar quando o usuário relata 404 num link que abriu para você.
   Domínio customizado fica fora da proteção, então o sintoma só aparece em `*.vercel.app`.
4. **Verificar como o usuário vai acessar:** requisição anônima
   (`curl -sS -D h.txt -o b.html <url>` e ler `x-vercel-error`; ou `vercel curl /`, que denuncia
   proteção ativa ao gerar bypass), conferindo **título + um asset conhecido**, não só o status.
   Repita 2× antes de mandar o link — alias e proteção mudam entre o deploy e a entrega.

## Export/impressão do que você publicou

Entrega web que o cliente vai imprimir ou baixar em PDF precisa ser verificada como funcionalidade,
não como estilo — o botão de PDF é a feature que mais falha em silêncio:

- **Prove o artefato:** capture o blob/arquivo gerado (ou clique real + `Browser.setDownloadBehavior`);
  "sem erro no console" não é evidência.
- **Evite `color-mix()`/`oklch()` em CSS imprimível** — o html2canvas não parseia e aborta a captura.
- **Verifique o PDF página a página** (`pdfinfo` + `pdftoppm` + contagem de tinta escura): 0% de
tinta é página em branco.
- Detalhes e receitas: `references/print-and-pdf-export-web.md`.

## Verificação e2e obrigatória
Com Playwright headless contra a URL pública:
- Carregar `https://<proj>.vercel.app/#/<rota>` e ler `body.innerText` (confere conteúdo renderizado,
  badges como "DOCUMENTO VENCIDO"/"CREDENCIAL INATIVA", dashboard pós-login).
- Reproduzir fluxos reais (ex.: `fill` + `click` no `#login-form`; assertar que re-renderizou).
- Registrar `console` errors e `pageerror` no listener — erro de console aponta handler quebrado.
- Atestar cada rota (raiz, `/c/<token>`, `/admin`) num único script.

## Auditoria de contraste e visibilidade (script, não olho)

Um site de entrega se audita por script re-executável, em desktop **e** mobile, antes e depois de
cada correção — e de novo **na URL publicada**:

- Para cada nó de texto, componha o fundo efetivo subindo os ancestrais (rgba sobre rgba, base =
fundo do body) e multiplique a **opacidade de todos os ancestrais**. Sem isso o audit acusa falha
no texto de telas inativas (`opacity: 0` por design) e ignora que o conteúdo está invisível.
- Conte só o que tem opacidade efetiva ≥ 0,9 e compare com 4,5:1 (ou 3:1 para ≥ 24px / ≥ 18,66px
bold). Rode também com o painel/modal ABERTO — o conteúdo atrás de um overlay costuma ser o que
reprova.
- **Confirme que a URL publicada serve o SEU build** (título + um asset conhecido) antes de auditar:
tela de login do host, página de erro e deploy antigo também renderizam texto e passam no contraste.
- **Visibilidade condicionada é parte do teste:** verifique que o conteúdo aparece na carga e
**depois de cada navegação programática** (clique de menu, troca de rota). Reveal por progresso de
scroll pode deixar a tela em branco até o próximo evento — bug de primeira ordem, não animação.
- **Relato visual é hipótese; medição é fato.** Quando uma análise de imagem apontar colisão,
overflow ou elemento cortado, meça `getBoundingClientRect` + computed styles antes de "corrigir":
só entre no código o que a medição confirma.
- Feche o ciclo re-rodando o mesmo audit + console + download/PDF afetado e registre os números
  (textos checados, falhas, páginas do PDF) no relatório — é o que autoriza dizer "pronto".
- **Texto sobre canvas/3D não é coberto por este audit:** a composição de fundo lê só o DOM, então
  texto apoiado num fundo WebGL claro passa aqui e falha na tela do cliente. Faça o teste de cena
  clara — camada clara injetada atrás do conteúdo (`position:fixed; inset:0;` entre canvas e
  conteúdo) + contraste medido no pixel do screenshot, percentis 2%/98% por caixa. Receita e script
  re-rodável em `revisao-entrega-cliente` (`scripts/contraste-cena-clara.py`).
- **Correção que "não pegou": separe cache de cascata.** Leia o valor computado
  (`getComputedStyle`) antes de repetir o teste: se ainda é o original, a regra perdeu a cascata
  (media query em arquivo carregado ANTES do CSS da tela) — não é cache. E rode o CDP/Playwright
  com cache desligado (`Network.setCacheDisabled`) ou perfil novo, senão você audita o build antigo
  e conclui errado nos dois sentidos.

## References
- `references/static-spa-vercel-deploy.md` — receita completa detalhada (auth device flow, vercel.json, pitfall do hash, organização do deploy).

## Browser policy — Mercúrio proot

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e decks): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.
- **Runtime Playwright:** `/data/data/com.termux/files/home/capitolium/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
