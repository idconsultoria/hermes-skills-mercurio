---
name: html-pdf-fidelity
description: "HTML→PDF identical to the browser — fonts, layout, 1 page.

Load this skill when a PDF export differs from the browser rendering (fonts, layout, pagination) or the user demands fidelidade máxima HTML→PDF. Chromium headless print pipeline with exact font embedding and one-page control."
version: 1.0.0
author: Hermes (curadoria autônoma, sessão 11/08/2026)
license: MIT
trigger: User compares PDF vs browser and finds font/layout/background differences; or asks for 'fidelidade máxima' PDF export.
metadata:
  hermes:
    tags: [pdf, chromium, html, fidelity, fonts, print]
    category: productivity
    related_skills: [html-to-pdf-chromium, resume-ats-engine, iaf-newsletter-pipeline]
type: Orchestrator
timestamp: 2026-08-12T02:54:45Z
---

# HTML → PDF com FIDELIDADE MÁXIMA

Garantir que um PDF exportado de HTML seja **idêntico ao que o usuário vê no navegador** — tipografia, cores, layout, contagem de páginas. Validado em 11/08/2026 (carta de apresentação: usuário rejeitou compactação de impressão: *"Que parte de fidelidade máxima você não tinha entendido ainda?"*).

## When to Use

- Usuário compara o PDF com o que vê no navegador e aponta diferenças (fontes, fundo, layout, número de páginas)
- Qualquer HTML→PDF que precise sair fiel à tela (cartas, relatórios, certificados)
- Usuário pede "fidelidade máxima" ou reclama que "não está idêntico ao HTML"
- **Relatórios analíticos multi-página** (hero, KPI cards, tabelas, callouts): ver `references/multipage-reports.md` — fluxo completo cat→host→chromium→cat back + verificação via screenshot do renderer

## Princípio central (preferência forte do usuário)

- **O que se vê na tela é o que sai no PDF.** PROIBIDO `@media print` que altere font-size, line-height, margin ou padding.
- **1 página é alcançada no DESIGN** (texto conciso + escala tipográfica equilibrada, preenchimento ~90-99% da altura A4), nunca por compactação no print.
- Se sobrar espaço: aumente fontes/espaçamentos (ex.: corpo 15.5→17.5px, nome 30→34px, labels ~11px, line-height 1.55). Se estourar: encurte o texto.

## Renderer: Chromium compartilhado do proot (não WeasyPrint)

WeasyPrint degrada CSS moderno (drop caps com float, chips, ornamentos e gradientes). Para fidelidade máxima, usar a única cópia ARM64 do Chromium:

```bash
CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright
NODE_PATH=/opt/mercurio-data/node_modules
```

Renderização local via Playwright:

```js
import { chromium } from 'playwright';
process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.playwright';
const browser = await chromium.launch({ headless: true, executablePath: '/opt/data/.playwright/chromium-1117/chrome-linux/chrome' });
```

Renderização local direta:

```bash
"$CHROMIUM" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-pdf-header-footer --print-to-pdf=/caminho/out.pdf "file:///caminho/in.html"
```

- Para arquivos, PDFs, screenshots e diagramas locais, use sempre o Chromium compartilhado acima.
- Para sites externos com internet, prefira `browser_exec`.
- Não usar caminhos legados de browser, caches por perfil ou Chromium remoto.

Pitfalls do renderer:
- **Chromium não imprime backgrounds sem `print-color-adjust: exact`** — usar `* { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }`.
- **Não remapear `font-family` para DejaVu** — remover apenas links/@import remotos ou usar `@font-face` local; remapear altera métricas e paginação.
- **WeasyPrint pode falhar com `::first-letter { float }`** — manter Chromium nesse caso.
- **Divisores grossos no PDF**: `border-top+bottom 1px` com `height: 3px` vira barra de 5 px; reduzir para 1 px.

## Fontes: embutir para fidelidade em qualquer máquina

O fallback de fontes varia por SO (Windows→Georgia/Times, Mac→Garamond/Didot, Android→Noto Serif). Para o PDF e o HTML do usuário mostrarem as MESMAS fontes:

1. **No host (render):** `@font-face { font-family: "EB Garamond"; src: url("file:///home/ubuntu/fonts/EBGaramond.ttf"); }` — copiar os .ttf para `/home/ubuntu/fonts/`.
2. **No zip entregue ao usuário:** HTML + pasta `fonts/` + `@font-face` relativo (`url('fonts/X.ttf')`) — abre igual em qualquer navegador (inclusive Chrome Android).
3. Fontes úteis do Google Fonts (licença livre): EB Garamond (corpo), Playfair Display (nome/drop cap), Cinzel (título display). Variantes variable TTF (~2.3MB total) ou WOFF2 (~107KB) — WOFF2 para base64, TTF para file:///fontconfig.
4. **Base64 `@font-face` dentro de `<style>` grande é instável** (funciona em HTML mínimo, falha em stylesheet grande) — preferir file:// (host) ou pasta `fonts/` (zip). Se precisar de base64, usar `<style>` separado.

## Export pelo navegador do usuário (Chrome Android)

Se o usuário exportar do telefone, configurar no diálogo de impressão:
- **Papel: A4** · **Margens: Nenhuma** (crítico — sem isso o Chrome soma margens por cima do `@page`) · **Escala: 100%** · **Gráficos em segundo plano (Background graphics): ATIVADO**.
- Se o export sair em 2 páginas: o HTML que ele abriu não tinha o fix de 1 página (ou o design não cabe) — embutir o ajuste no HTML ou redesenhar para caber naturalmente.

## Entregas

- **SEMPRE versionar nomes de arquivo** (`carta_v7.pdf`, `carta_v8.zip`...) — o usuário exige nome único por versão para identificar a mais recente; nunca reutilizar o mesmo nome entre entregas (WhatsApp mostra o arquivo antigo como "igual").
- Se o usuário disser que a versão está "igual à anterior": conferir se o arquivo entregue é o renderizado por último (erro comum: gerar em `X_final.pdf` e entregar `X.pdf` antigo).

## Verificação

1. `pymupdf`: páginas == esperado; fontes usadas por span (`get_text('dict')`) — corpo/nome devem ser as fontes embutidas, não DejaVu.
2. Preenchimento: `ymax` do conteúdo ≈ 90-99% da área útil (A4 842pt − 2×margem).
3. Render de preview (dpi 140) + `vision_analyze` para conferir visual antes de entregar.

### Preview local com o mesmo renderer do PDF

Se `pymupdf`/`pdftoppm` não estiverem disponíveis, gerar o preview diretamente do HTML com o mesmo Chromium compartilhado:

```bash
CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
"$CHROMIUM" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --hide-scrollbars --window-size=1240,1750 \
  --screenshot=/caminho/preview.png "file:///caminho/in.html"
```

Depois inspecionar o PNG com `vision_analyze`. Para seções abaixo do fold, aumentar o height (ex.: `1240,3500`). DBus/UPower no stderr são normais em modo headless; o PNG gerado é a evidência.

## PDF → HTML (fluxo inverso): replicar um deck/PDF como HTML com assets originais

Validado 14/08/2026 (proposta Minuzzo → HTML v3). O usuário NÃO quer clone pixel-perfect de PDF — quer **HTML "que pareça nascido como HTML"**: sintaxe semântica (section/h1/h2/h3/p/ul/li, CSS grid/flex), **foreground (conteúdo) separado do background (arte decorativa)**, e **assets ORIGINAIS** (fundos, logos, ícones, cores exatas) extraídos do PDF — nunca recriados à mão. A v1 (SVG extraído + texto posicionado por coordenadas) foi aceita como base visual; a v2 (HTML limpo com arte recriada) foi rejeitada ("ficou péssimo sem os fundos e a logo originais"); a v3 (SVG original como `.bg` + HTML semântico no `.fg`) foi aprovada.

Pipeline: `pymupdf` `page.get_svg_image()` → remover paths de texto (filtro por fill branco/teal + overlap com spans) → SVG limpo vira camada `.bg` → texto em HTML semântico sobreposto. Detalhe completo da técnica (anatomia Type3/XObjects, fix de ligaduras 'fi'/'fl', extração de logo por bbox, opacidade 0.4 da arte, extração de componentes de marca): `references/pdf-to-html-replication.md`.

Pitfalls de processo que o usuário corrigiu:
- **Verificar layout programaticamente, não pela vision model.** `browser_vision`/`vision_analyze` é impreciso com posicionamento (lê "centralizado" o que está à direita, vê "duplicado" slides separados, alucina descrições de ícones) e o zoom 0.66 distorce a leitura. A fonte da verdade é `getBoundingClientRect` + computed styles via `browser_console`; a vision serve só para sanidade visual.
- **Ajustar um slide de cada vez com validação do usuário** — nunca refazer o deck inteiro numa tacada; cada slide aprovado vira referência.
- **"Qual a logo/asset correto?" → olhar o arquivo de referência (deck v3) e extrair dele** (ex.: slides padrão usam o símbolo diamond teal, não a logo completa com tagline; a tagline fica só na capa/final).
- Cores/posições: seguir o deck de referência por inspeção programática das posições reais (left/top/size), não por achismo.

## Browser policy — Mercúrio proot

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e visual local): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.
- **Runtime Playwright:** `/opt/mercurio-data/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
