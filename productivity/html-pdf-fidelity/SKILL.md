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

## Renderer: Chromium headless no HOST (não WeasyPrint)

WeasyPrint **degrada CSS moderno** (drop caps com float, chips, ornamentos, gradientes). O padrão fiel é Chromium headless via SSH no host Oracle (padrão da IAF newsletter):

```bash
ssh oracle-host 'chromium-browser --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=/home/ubuntu/out.pdf "file:///home/ubuntu/in.html" 2>/dev/null'
```

Pitfalls do renderer:
- **Snap do Chromium tem fontconfig ISOLADO** — instalar fontes em `~/.local/share/fonts` ou `/usr/share/fonts` NÃO funciona (confinamento). A solução é injetar `@font-face` com `src: url("file:///home/ubuntu/fonts/X.ttf")` — o snap lê `/home/ubuntu`. Verificar se as fontes foram usadas extraindo o PDF: `pymupdf` mostra fontes embutidas como `Type3 (N 0 R)` (nome vazio) — se aparecer `DejaVuSerif`, caiu em fallback.
- **Chromium não imprime backgrounds sem `print-color-adjust: exact`** — o fix de impressão mínimo é: `* { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }`. Sem isso, fundo creme e chips ficam brancos no PDF.
- **NÃO remapear `font-family` para DejaVu no caminho Chromium** — só remover links/@import do Google Fonts. Remapear muda as métricas das fontes e infla o layout (pode estourar a página).
- **WeasyPrint 69 crasha com `::first-letter { float }`** (AssertionError em float_layout) — usar Chromium, ou converter o drop cap para inline (`float: none`).
- **Snap pode sumir do host**: reinstalar com `sudo snap install chromium`. O snap tem `/tmp` privado — HTML de entrada deve ficar em `/home/ubuntu/`, não `/tmp`.
- **Divisores grossos no PDF**: `border-top+bottom 1px` com `height: 3px` vira barra de 5px — reduzir `height` para 1px.

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

### Fallback de preview quando pymupdf/pdftoppm não existem no container

Se `pymupdf` e `pdftoppm` não estão instalados localmente, o Chromium do host renderiza um screenshot direto do HTML (mesmo renderer do PDF — é o que valida o visual de verdade):

```bash
ssh oracle-host 'timeout 90 chromium-browser --headless --no-sandbox --disable-gpu \
  --screenshot=/home/ubuntu/preview.png --window-size=1240,1750 "file:///home/ubuntu/in.html" 2>&1 | tail -1'
ssh oracle-host 'cat /home/ubuntu/preview.png' > /opt/data/reports/preview.png
# depois: vision_analyze no PNG local
```

- `--window-size=1240,1750` ≈ 1 página A4 em ~70 DPI — suficiente para conferir hero, cards e tabelas.
- Para seções abaixo do fold, subir o height (ex.: `1240,3500`) e inspecionar o screenshot inteiro com `vision_analyze`.
- Erros de DBus/UPower no stderr do snap são normais em servidor sem desktop — ignorar; conferir o arquivo PNG gerado.
