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
CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright
NODE_PATH=/opt/mercurio-data/node_modules
```

- **Arquivos locais** (HTML→PDF, screenshot, DOM, SVG/PNG, Mermaid e BPMN): use o Chromium compartilhado acima, preferencialmente via Playwright ou pelo binário com `executablePath`.
- **Sites externos com acesso à internet**: prefira a ferramenta `browser_exec`; ela mantém a navegação web separada do renderer local determinístico.
- **Nunca usar** caminhos legados de browser e caches por perfil. Se qualquer comando apontar para esses caminhos, corrigir para o runtime canônico.

## Pré-requisitos e resolução

O runtime já está instalado. Para validar sem baixar nada:

```bash
/opt/data/.playwright/chromium-1117/chrome-linux/chrome --version
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright \
NODE_PATH=/opt/mercurio-data/node_modules \
node -e "const {chromium}=require('playwright'); console.log(chromium.executablePath())"
```

O resultado esperado é Chromium 125 ARM64 no caminho `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.

## Gerar PDF com o Chromium compartilhado

```bash
CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
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
const browser = await chromium.launch({ headless: true, executablePath: '/opt/data/.playwright/chromium-1117/chrome-linux/chrome' });
```

### Se o Chromium travar

1. Remover `<link href="https://fonts.googleapis.com/...">` ou usar fontes locais por `@font-face`.
2. Extrair base64 grande para arquivos locais; evitar payloads inline acima de ~500 KB.
3. Usar timeout de 90–120 s para HTML complexo.
4. Manter `--no-sandbox`, `--disable-gpu` e `--disable-dev-shm-usage` no ambiente proot.

## Verificação

```bash
CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
"$CHROMIUM" --version
PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright NODE_PATH=/opt/mercurio-data/node_modules \
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

- **Renderer local** (HTML→PDF, screenshots, Mermaid, BPMN, p5.js e visual local): usar a única cópia ARM64 do Chromium em `/opt/data/.playwright/chromium-1117/chrome-linux/chrome`.
- **Runtime Playwright:** `/opt/mercurio-data/node_modules/playwright`; cache: `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Não instalar outro Chromium/Puppeteer por perfil; não usar caches antigos ou browsers remotos.
- **Sites externos com internet:** usar a ferramenta `browser_exec` para navegação, interação, extração e verificação visual.
