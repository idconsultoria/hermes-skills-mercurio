---
name: documento-a4-marca-id
description: "Documento A4 com identidade ID (HTML→PDF)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pdf, a4, marca, id, onboarding, manual, html, chromium]
    related_skills: [elaboracao-proposta-comercial, html-pdf-fidelity, html-to-pdf-chromium, md-to-timbrado-id]
type: Orchestrator
timestamp: 2026-10-16T00:00:00Z
---

# Documento A4 com identidade ID

## Quando usar

Cliente ou sócio pede um **documento de mão** (manual de onboarding, guia do participante, handout de treinamento, one-pager operacional) em **PDF A4** com a cara da ID — não um deck de slides.

**Não usar para:** proposta comercial (use `elaboracao-proposta-comercial`) nem documento timbrado em Google Docs (use `md-to-timbrado-id`).

## Fonte da marca (não reinventar)

Extrair do template da proposta: `skills/business/elaboracao-proposta-comercial/templates/modelo_proposta.html`.

- **Fontes embutidas em base64**: há 2 blocos `@font-face` (Neulis Neue 700 OTF + Nunito Sans 400 WOFF2). Copiá-los **verbatim** para um `fonts.css` no diretório de trabalho e inlinar no `<style>`. Não usar Google Fonts (quebra a fidelidade e exige rede).
- **Logo ID**: extrair o `<svg class="logo-id" viewBox="1324...">…</svg>` (branco, ~88 KB) e inlinar.
- **Diamante teal** de header: extrair `<svg class="page-icon" …>…</svg>` (~31 KB) e inlinar.
- **Tokens**: `--bg:#000000`, `--fg:#FFFFFF`, `--teal:#4AC6D3`, `--line:#1B5A63`, `--muted:rgba(255,255,255,.74)`, títulos Neulis Neue, corpo Nunito Sans.

## Receita

1. `mkdir -p <HERMES_HOME>/work/<peça>`; extrair `fonts.css`, `logo.svg`, `icon.svg` do template com um script Python (regex nos blocos `@font-face` e nas duas `<svg>`).
2. Gerar o HTML por **script Python** (um `build_manual.py`), montando `<section class="page">` de A4 e inlinando fontes/SVGs. Assim o ajuste fino é uma edição de string e o build é reprodutível.
3. CSS: `@page{size:A4;margin:0}`, `.page{width:210mm;height:297mm;padding:14mm 15mm 16mm;background:var(--bg);overflow:hidden;page-break-after:always}`. Corpo 10-10,5 pt, títulos 17-23 pt, títulos de seção 11 pt teal. Para celular: alto contraste, no máximo 2 colunas, linhas curtas.
4. Renderizar com `scripts/render_a4.mjs` (mesmo Chromium/Playwright da proposta).
5. Conferir **duas coisas** antes de entregar: (a) o script avisa `ATENCAO pagina N: overflow Xpx` — conteúdo é cortado silenciosamente por `overflow:hidden`, então zero avisos; (b) contagem de páginas do PDF bate com o pedido.
6. Verificação visual: `scripts/preview.mjs` gera PNG por página e ler com `vision_analyze` (logo renderizado, texto cortado, equilíbrio de espaço no fim da última página).

## Marca do cliente (logo)

- **Não inventar**: procurar no disco primeiro (`find <HERMES_HOME> -iname '*<cliente>*'`, pastas `entregas/`, `profiles/<rama>/entregas/`, `deliverables/`). Não achou no disco → **baixar do site do próprio cliente** (ex.: WordPress guarda em `/wp-content/uploads/.../logo*.png`; `curl -sL <site> | grep -oiE '(src|href)="[^"]*logo[^"]*"'`).
- **Escolher a variante certa**: medir o logo com PIL (média RGB dos pixels opacos) — versão escura de fundo claro não serve sobre fundo preto. Footer/rodapé de sites costuma ser a versão **branca/negativa**, feita para fundo escuro.
- **Recortar o padding** (`img.crop(img.getbbox())`) antes de usar, para o logo não parecer menor por causa da margem transparente.
- **Um único lockup**: logo do cliente + divisor + logo da ID **só na primeira página**. Não repetir a marca da ID (logo ou diamante) em cada página — vira ruído; a assinatura recorrente fica no rodapé em texto.

## Pitfalls

1. **`render_pdf.mjs` da proposta é 1920×1080 por slide** — não serve para A4. Usar `render_a4.mjs` (mesmo motor, `format:'A4'`, `preferCSSPageSize:true`, `printBackground:true`).
2. **`process.platform === 'android'` neste proot**: `require('playwright')` explode com *Unsupported platform: android* **se** `PLAYWRIGHT_BROWSERS_PATH` não estiver definido **antes** do require (é o caminho que evita o cálculo de cache do registry). Definir os env vars na primeira linha do `.mjs`.
3. **Binário do Chromium muda de versão**: resolver por candidatos (`/opt/data/.playwright/chromium-1129/chrome`, depois `chromium-1117/chrome-linux/chrome`) e falhar com mensagem clara. Não instalar outro Chromium.
4. **`overflow:hidden` esconde o excesso**: uma página que “parece” pronta pode ter 100 px cortados. Sempre checar o aviso de overflow e reduzir margens/paddings antes de declarar pronto.
5. **Não inventar dado logístico**: data, horário, endereço, carga horária e ementa vêm do contrato/proposta/conversa do ponto focal. Roteiro de horários internos é "previsão" e deve estar rotulado.
6. **Zero emoji e zero nota interna** no documento do cliente; sem citar ferramentas internas.

## Checklist

- [ ] 3 páginas ou menos, sem overflow
- [ ] Fontes Neulis/Nunito aplicadas (verificar no PNG)
- [ ] Logo ID + cliente renderizados
- [ ] Dados logísticos conferidos contra contrato/conversa
- [ ] PNG das páginas revisado com visão

## Browser policy — Mercúrio proot

- Renderer local: `/opt/data/.playwright/chromium-1129/chrome` (fallback `chromium-1117/chrome-linux/chrome`); runtime Playwright em `/data/data/com.termux/files/home/capitolium/node_modules/playwright`; `PLAYWRIGHT_BROWSERS_PATH=/opt/data/.playwright`.
- Arquivos de entrega em `<HERMES_HOME>/work/<peça>/`.
