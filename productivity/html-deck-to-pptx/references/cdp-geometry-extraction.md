# Extração de geometria do deck HTML (Chromium/CDP)

Objetivo: `deck_geo.json` com, por slide (`<section class="slide">`, 1920x1080 px em CSS de print), tudo que o emissor precisa: fundo, caixas, textos, imagens, svgs, tabelas, pseudos.

## Subir e conectar no navegador

- Use o Chromium já presente na imagem (Playwright): `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`, flags `--headless=new --no-sandbox --disable-gpu --hide-scrollbars --remote-debugging-port=N --window-size=1920,1080`.
- Conecte no alvo de **página**: `GET http://127.0.0.1:N/json/list` e pegue o `webSocketDebuggerUrl` do item `type == "page"`. O `/json/version` devolve o alvo do *browser*, que responde `-32601 '<dominio>' wasn't found` para `Page.*`/`Runtime.*` — sintoma clássico de ter conectado no alvo errado.
- Com `aiohttp`: `await ws.receive_str()` e só então `json.loads` (o `receive()` cru devolve `WSMessage`, não str). Casamento de resposta por `id`; logue `msg["error"]` quando existir.
- `Runtime.evaluate` → valor em `resp["result"]["result"]["value"]`.
- Espere ~3,5 s após `Page.navigate` — o deck carrega **webfonts de CDN** (Clash Display via Fontshare, Hanken Grotesk via Google) e medir antes disso dá métrica errada.
- Retângulos relativos ao slide: `getBoundingClientRect()` + `window.scrollX/scrollY`, subtraindo o rect da própria `<section>`.

## Texto — o algoritmo que evita duplicação

Para cada elemento *blockish* (display em block/flex/grid/list-item/table/inline-block/inline-flex) que **não** tenha descendente blockish: percorra os filhos e monte runs.

- Nó de texto → run com o estilo herdado; elemento inline → run com *o próprio* `fontWeight`/`fontSize`/`color`/`fontFamily`/`letterSpacing` (preserva negrito, `<i>` e cor de destaque).
- Filho blockish → **pule a subárvore** (o texto dele pertence ao run dele).
- `<br>` → marcador de quebra; o emissor transforma em novo parágrafo.
- A caixa do bloco = união dos `getClientRects()` via `Range` por nó de texto (a *line box*, não a tinta) — é o que alinha com o topo da linha no PowerPoint.
- `text-transform: uppercase` não existe no PowerPoint: guarde o valor e aplique no próprio texto.

## Caixas

Colete quando houver `background-color` com alpha > 0.05, `background-image != none` ou borda visível; e **não** colete quando `backgroundClip/webkitBackgroundClip == 'text'`, quando for `SECTION` ou `svg`. Cada caixa guarda: rect, fill+alpha, raio (`borderTopLeftRadius`), o `background-image` cru (string do gradiente) e sombra.

**Bordas por lado** — monte `{t,r,b,l}` com `border<Lado>Width/Style/Color` e só considere os lados com width > 0 e style != none.

**Sombra** — do primeiro `box-shadow` (separe por vírgula fora de parênteses): `{x, y, blur, color, alpha}`.

## Pseudo-elementos com `content`

Rode para `::before` e `::after` de cada elemento, ignorando `content: none|normal|''|url(...)`. Como não há API de layout para pseudo, meça: `canvas.getContext('2d').measureText(texto)` com o `font` do pseudo (`fontWeight + fontSize + fontFamily`) mais `padding` e bordas. Posição: se `position: absolute|fixed`, use como bloco de contenção a *padding box* do elemento (`rect + paddingLeft/Top`) mais `left`/`top` computados (o Chrome já resolve percentuais para px) e some `tx`/`ty` da `matrix()` de `transform` (é assim que `translateX(-50%)` centraliza o selo). Capture também bg, cor, raio, bordas, letter-spacing e alinhamento.

## Tabelas

Por `<table>` → linhas → células com texto normalizado (`\s+` → espaço), tag, font-size, weight, cor, `textAlign` e fundo. **O fundo da célula herda**: próprio `<td>` → `<tr>` → `<table>`, sempre carregando o **alpha** (sem ele, tints de 0.05/0.16 viram cor sólida e a tabela fica ilegível). Alturas por linha e larguras pela linha de cabeçalho.

## SVGs

`outerHTML` + rect + `getComputedStyle(el).color` (os ícones usam `currentColor`).

**Rasterizar para PNG transparente:** monte uma página com cada SVG numa célula do tamanho do rect original e `color` do elemento; antes de capturar chame `Emulation.setDefaultBackgroundColorOverride` com `{r:0,g:0,b:0,a:0}` (só `omitBackground` não basta se `html`/`body` pintam fundo — sete ambos para transparente) e capture com `Page.captureScreenshot` {format png, `captureBeyondViewport: true`, `clip` = rect da célula, `scale: 2}`. Confira o resultado: PNGs de mesmo tamanho são suspeitos de crop errado.

## Fundo de cada slide

Para o slide `i`: em todas as sections, deixe `visibility` `hidden` em todos os filhos, exceto o filho `.bg` do slide `i`; capture o `clip` do rect da section (scale ~1.25). O `.bg` do deck é só gradiente + orbs com `filter: blur()`, então o resultado traz o fundo exato (inclusive os brilhos) sem texto. Depois disso, **não** emita caixas de classe `orb` no PPTX (dualidade).
