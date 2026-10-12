# Render e verificação — documento A4 para ente público

## Geometria

```css
@page{size:A4;margin:11mm 12mm}                     /* margens estreitas: densidade sem apertar */
.cover{margin:-11mm -12mm;width:210mm;height:297mm} /* capa em sangria, igual às margens da @page */
body{font-size:10.4pt;line-height:1.58}             /* Nunito Sans */
h1,h2,h3,h4{font-family:'Neulis Neue'}              /* títulos */
```

Fontes embutidas em base64 no próprio HTML (`@font-face` OTF da Neulis Neue e woff2 da Nunito
Sans). O arquivo fica com ~440 KB — normal, e é o que garante o mesmo desenho em qualquer render.
Não trocar por link do Google Fonts: o Chromium headless trava em fonte remota.

## Render (rodapé numerado pelo Chromium)

```bash
/opt/mercurio-data/node/bin/node \
  skills/business/proposta-ente-publico/scripts/render_doc.cjs \
  /caminho/ID-Solucoes-<Orgao>-<UF>-vX.Y.html \
  /caminho/ID-Solucoes-<Orgao>-<UF>-vX.Y.pdf \
  "ID Consultoria · Documento de soluções — <órgão>"
```

O script usa o Chromium compartilhado (`/opt/data/.playwright/chromium-1129/chrome`) com
`displayHeaderFooter: true` e `footerTemplate` — a numeração de página sai do Chromium. **Nunca
digitar "página N" no HTML.**

Node errado derruba o render: usar `/opt/mercurio-data/node/bin/node` (o node do Termux reporta
`platform: android` e o Playwright aborta). CommonJS (`.cjs`), não ESM.

## Verificação de densidade

```bash
skills/business/proposta-ente-publico/scripts/checar_paginas.sh <arquivo.pdf>
```

O script imprime caracteres por página e sinaliza páginas abaixo do piso e texto que não deveria
existir (preço, placeholder). Ordem de leitura do resultado:

1. **Contagem total** compatível com o padrão (referência de 8 páginas: 592 na capa e
   1.400–3.000 no miolo).
2. **Página órfã** (< ~1.400 caracteres no miolo) = bloco grande com `break-inside:avoid`, quebra
   forçada sobrando ou bloco de assinatura que não coube. Corrigir antes de olhar o desenho.
3. **Cabeçalho órfão**: o que abre cada página deve ser conteúdo, nunca um `sec-head` sozinho.

## Conferência visual obrigatória

```bash
pdftoppm -png -r 110 <arquivo.pdf> /tmp/prev
```

E olhar, no mínimo: **capa**, página da **matriz** (a barra e os marcadores), **uma frente**
(duas colunas + "não incluído") e o **fecho** (pontos + próximo passo + rodapé). A contagem de
caracteres não pega rodapé solto, assinatura flutuando, coluna desbalanceada nem marcador fora
de centro.

## Ordem de correção quando não fecha

1. Densidade (corpo 10,4→11pt, `line-height` 1,58→1,62, margens) — resolve a maior parte.
2. Quebras forçadas (`section.closing` e pouco mais) — cada uma custa 0,3–1 página.
3. Conteúdo — sempre por último e sempre com o órgão sabendo.
