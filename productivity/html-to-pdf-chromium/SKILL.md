---
name: html-to-pdf-chromium
description: "Convert HTML to PDF via Chromium ARM64 compartilhado.

Load this skill when generating PDF from HTML with browser-quality rendering, or when weasyprint output lacks CSS features like -webkit-background-clip or gradients. Uses the shared Playwright/Chromium runtime for browser-quality PDF output; WeasyPrint is only an explicitly non-browser fallback."
trigger: User asks to generate PDF from HTML with browser-quality rendering, or when weasyprint output lacks CSS features like -webkit-background-clip or gradients.
related_skills: [html-report-hermes, iaf-newsletter-pipeline]
type: Template
timestamp: 2026-07-16T22:30:00Z
---

# HTML → PDF com Chromium Headless

## Browser único e política de uso

Este proot usa **uma única cópia funcional do Chromium ARM64**. Não instale nem baixe outro browser por perfil:

```bash
CHROMIUM=/opt/data/.playwright/chromium-1129/chrome
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright
NODE_PATH=/data/data/com.termux/files/home/capitolium/node_modules
```

- **Arquivos locais** (HTML→PDF, screenshot, DOM, SVG/PNG, Mermaid e BPMN): use o Chromium compartilhado acima, preferencialmente via Playwright ou pelo binário com `executablePath`.
- **Sites externos com acesso à internet**: prefira a ferramenta `browser_exec`; ela mantém a navegação web separada do renderer local determinístico.
- **Nunca usar** caminhos legados de browser e caches por perfil. Se qualquer comando apontar para esses caminhos, corrigir para o runtime canônico.

## Pré-requisitos e resolução

O runtime já está instalado. Para validar sem baixar nada:

```bash
/opt/data/.playwright/chromium-1129/chrome --version
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright \
NODE_PATH=/data/data/com.termux/files/home/capitolium/node_modules \
node -e "const {chromium}=require('playwright'); console.log(chromium.executablePath())"
```

O resultado esperado é Chromium 125 ARM64 no caminho `/opt/data/.playwright/chromium-1129/chrome`.

## Gerar PDF com o Chromium compartilhado

```bash
CHROMIUM=/opt/data/.playwright/chromium-1129/chrome
INPUT=/caminho/absoluto/arquivo.html
OUTPUT=/caminho/absoluto/resultado.pdf

"$CHROMIUM" \
  --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-pdf-header-footer \
  --print-to-pdf="$OUTPUT" \
  "file://$INPUT"
```

Para documentos que exigem mais controle, usar Playwright:

```js
import { chromium } from 'playwright';
process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/data/.playwright';
const browser = await chromium.launch({ headless: true, executablePath: '/opt/data/.playwright/chromium-1129/chrome' });
```

### Se o Chromium travar

1. Remover `<link href="https://fonts.googleapis.com/...">` ou usar fontes locais por `@font-face`.
2. Extrair base64 grande para arquivos locais; evitar payloads inline acima de ~500 KB.
3. Usar timeout de 90–120 s para HTML complexo.
4. Manter `--no-sandbox`, `--disable-gpu` e `--disable-dev-shm-usage` no ambiente proot.

## ⚠️ Node e Chromium — caminhos que MUDAM (verificado 08/10/2026)

Dois erros silenciosos derrubam o render local. Confira sempre antes de culpar o HTML:

1. **Node do Termux quebra o Playwright.** `/data/data/com.termux/files/usr/bin/node`
   reporta `process.platform === 'android'`, e o `playwright-core` aborta com
   `Error: Unsupported platform: android`. **Use o Node do runtime:**
   `/data/data/com.termux/files/home/capitolium/node/bin/node` (linux, v22).
2. **Import ESM falha no proot** (`import { chromium } from 'playwright'` → mesmo erro de
   platform). **Usar CommonJS:** `const { chromium } = require('/data/data/com.termux/files/home/capitolium/node_modules/playwright')`.

O Chromium compartilhado foi **atualizado de 1117 para 1129** e o layout mudou: agora é
`/opt/data/.playwright/chromium-1129/chrome` — **sem** o subdiretório `chrome-linux/`.
Apontar para o caminho antigo dá `executable doesn't exist`. Conferir com
`ls /opt/data/.playwright/` antes de renderizar; a política continua a mesma (uma única
cópia ARM64, nada instalado por perfil). Chromium verificado: **128.0.0.0**.

### Receita verificada — documento A4 com rodapé numerado

```js
const { chromium } = require('/data/data/com.termux/files/home/capitolium/node_modules/playwright');
const b = await chromium.launch({ executablePath:'/opt/data/.playwright/chromium-1129/chrome',
  args:['--no-sandbox','--disable-dev-shm-usage'] });
const p = await b.newPage();
await p.goto('file://'+INPUT, { waitUntil:'load' });
await p.evaluate(()=>document.fonts.ready);          // sem isso, fonte tardia desalinha
await p.pdf({ path:OUT, printBackground:true, preferCSSPageSize:true,
  displayHeaderFooter:true, headerTemplate:'<div></div>',
  footerTemplate:'<div style="font-size:7pt;color:#7b8c9c;padding:0 18mm;display:flex;justify-content:space-between;"><span>Título · subtítulo</span><span class="pageNumber"></span></div>',
  margin:{top:'15mm',bottom:'15mm',left:'18mm',right:'18mm'} });
```

Rodar com `/data/data/com.termux/files/home/capitolium/node/bin/node render.cjs` (script **.cjs**, não .mjs).

### Paginação de documento A4 (pitfall de layout real)

- **Capa em sangria com margens na `@page`:** `@page{size:A4;margin:15mm 18mm}` e, na capa,
  `margin:-15mm -18mm;width:210mm;height:297mm`. Assim o corpo ganha margem em **todas**
  as páginas e a capa sangra de ponta a ponta. Com `margin:0` na `@page`, o texto do miolo
  encosta na borda inferior.
- **`page-break-inside:avoid` no bloco grande desperdiça meia página.** Um cartão de seção
  indivisível força cada seção a começar em página nova e deixa metade da folha vazia
  (aconteceu: 9 páginas com 5 meias-páginas). Solução: **soltar o bloco maior** e proteger só
  as partes: `break-inside:avoid` nos blocos internos e **`break-after:avoid` no cabeçalho**
  (impede título órfão no pé da página). Resultado: 8 páginas densas, sem cabeçalho solto.
- **Verificação obrigatória por densidade de texto:** `pdftotext -f N -l N` página a página e
  olhar o que abre cada uma — bloco repetido indicando divisão feia, ou página quase vazia.
  Complementar com inspeção visual; nunca declarar "pronto" só com o `pdfinfo`.

## Verificação

```bash
CHROMIUM=/opt/data/.playwright/chromium-1129/chrome
"$CHROMIUM" --version
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright NODE_PATH=/data/data/com.termux/files/home/capitolium/node_modules \
  node -e "const {chromium}=require('playwright'); console.log(chromium.executablePath())"
```

Depois de gerar o PDF, conferir `stat`/`pdfinfo` para existência, tamanho e páginas. Para HTML→PDF de proposta, usar `scripts/render_pdf.mjs` do Mercúrio; ele já fixa o cache compartilhado.

## Pitfalls

- **Não instalar outro Chromium:** caminhos legados de browser são proibidos neste proot.
- **CSS moderno:** WeasyPrint pode perder gradientes, chips, `background-clip` e elementos com float; não substituir o renderer local sem o usuário pedir.
- **Fontes remotas:** remover `@import`/links do Google Fonts ou usar `@font-face` local; não trocar silenciosamente por DejaVu.
- **Backgrounds de impressão:** aplicar `-webkit-print-color-adjust: exact` e `print-color-adjust: exact`.
- **Timeout:** iniciar em 90 s para HTML complexo e capturar o stderr real; não afirmar sucesso sem arquivo PDF válido.
- **Múltiplos processos:** usar o mesmo Chromium, mas diretórios `--user-data-dir` temporários distintos quando necessário.

## Casos de uso relacionados

- **BPMN 2.0 → PNG:** usar `bpmn-diagram-renderer`; ele aponta para o mesmo Chromium compartilhado.
- **Mermaid → PNG:** usar `google-docs-formatting/references/mermaid-rendering.md` e o `puppeteer-config.json` compartilhado.
- **Sites externos:** usar `browser_exec`; não transformar o renderer local em navegador de navegação remota.

## Browser policy — Mercúrio proot

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e visual local): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1129/chrome`.
- **Runtime Playwright:** `/data/data/com.termux/files/home/capitolium/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
