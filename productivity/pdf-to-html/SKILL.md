---
name: pdf-to-html
description: "PDF→HTML: Type3/Figma extraction gotchas + clean semantic rebuild.

Load this skill when replicating a PDF design as HTML (slide deck, proposal, one-pager) or extracting vector art/text for the web. Especially relevant for Figma-exported PDFs (Type3 fonts) — full of silent traps. Default for this user: clean semantic rebuild with foreground/background separated, not pixel-perfect SVG. Absorveu pdf-deck-to-html, pdf-slides-to-html, pdf-to-html-replication e branded-html-replication (merge 16/08/2026): estrutura de proposta comercial aprovada, extração de assets, pipeline completo."
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [pdf, html, figma, typ3, extraction, slides, conversion]
    related_skills: [html-pdf-fidelity, pdf, html-to-pdf-chromium, html-report-hermes]
type: ToolIntegration
timestamp: 2026-08-14T05:00:00Z
---

# PDF → HTML

## When to Use

Load this skill when the user asks to replicate a PDF design as HTML (slide deck, proposal, one-pager, brand piece), or to extract a PDF's vector art/text for the web. Especially relevant when the PDF was exported from Figma (Type3 fonts) — the extraction path is full of silent traps.

Two ways to turn a PDF design into HTML. **For this user (Gustavo/ID Consultoria), the clean semantic rebuild is the default for slide decks and proposals** — he explicitly rejected pixel-perfect SVG extraction in favor of "HTML nascido HTML" (syntax that looks like it was written as HTML from the start) with foreground and background clearly separated.

## Decision: which approach

| Situation | Approach |
|---|---|
| Deck/proposta/one-pager for a client or brand | **Clean rebuild** (Approach A) — semantic HTML, fg/bg split, palette + type scale from the PDF |
| Document where EXACT visual fidelity is required and rebuild is infeasible | **Extraction** (Approach B) — vector SVG art + absolute-positioned text |
| User says "pixel perfect" explicitly | Extraction, but expect the user to follow up with color/typography corrections and then ask for the clean version |

## Approach A — Clean semantic rebuild (user's preferred default)

Build the HTML as if it came first: `section` per slide/page, `h1/h2/h3`, `p`, `ul/li`, CSS grid/flex. Never absolute-position text from PDF coordinates.

1. **Extract the content truth** from the PDF with PyMuPDF: text spans/lines (`page.get_text("dict")` gives bbox + size per line), drawings (fills/colors), images (`page.get_images` + `page.get_image_rects`).
2. **Reconstruct visible text carefully** — see "Text truth" below; the extractable text layer lies about characters and colors.
3. **Map sizes to the type scale** the user provides (e.g. Neulis Neue Bold 96/60/48/36, Nunito Sans Regular 36/30/24/20). Same size (36) can be Bold for headers and Regular for subtitles — decide per line by cropping the rendered page and eyeballing stroke weight.
4. **Explicit colors per element** — do not infer colors from the PDF text layer (it lies — see below). Ask the user or sample the rendered PNG.
5. **Layering**: `.bg` (decorative SVG art: contour lines, shields, photos with dark overlay) absolutely positioned behind; `.fg` (content) on top. User demand: "Separe bem elementos de foreground de elementos de background."
6. **Assets**: reuse real raster assets from the PDF (logos, photos) as `<img>`/background base64 — that's legitimate and keeps brand fidelity; only re-*drawing* decorative art in SVG is expected.
7. **Embed fonts** base64 in `@font-face` (OTF/woff2). Self-contained single HTML file.
8. **Verify in a real browser**, not just by eye: fonts loaded (`document.fonts.check`), computed colors, `getBoundingClientRect` overflow scan (any child outside slide bounds). The vision model is unreliable for precise position/color claims on long stacked pages — trust programmatic checks.

## Approach B — Pixel-perfect extraction (when required)

Full pipeline with working code: `references/figma-pdf-extraction.md`.

Key gotchas that will otherwise eat hours:

- **Figma-exported PDFs use Type3 fonts with TWO text layers**: (1) an invisible accessibility layer (`BT/ET` operators — extractable text, but colors are wrong/black and some glyphs map to `€`), and (2) the VISIBLE text drawn as vector paths inside Form XObjects. Consequence: `apply_redactions()` removes the text logically but the render stays byte-identical; span colors are useless.
- **`page.get_svg_image()`** (PyMuPDF) converts a page to SVG preserving draw order and opacity — the foundation of extraction.
- In that SVG: `<use data-text="X">` elements reference **empty** glyph defs (invisible, but carry the clean characters); `<path d=...>` elements are the visible glyphs.
- **Ligatures**: `fi`/`fl` — the invisible layer drops the `i`/`l` after `f`. Fix with difflib alignment against the accessibility text, inserting deleted `i`/`l` only when preceded by `f`.
- **Numbered list markers** ("1." in "1. Plano de Trabalho") can be drawn inside the same white text path group — text extraction misses them; check the path bbox's leading gap vs the text bbox.
- **Opacity**: decorative blob layers often render at 40% (`gs /ca .4`). Determine per-layer opacity by sampling the rendered page along the path's own points, or from the content stream.
- Namespace all SVG ids per slide (`mask_1`, `clip_2`, `font_8_*` collide across slides in one document).
- Removing text paths from the SVG: fill in text-ish colors AND bbox overlap with accessibility line bboxes; multi-line blocks need a sum-of-intersections/area > 0.35 rule (one path can hold a whole paragraph block).

## Text truth (both approaches)

The visible text = `<use data-text>` chars (clean) + ligature insertions (see above). The accessibility layer has all chars but nbsp maps to `€` (U+20AC) and it can duplicate syllables ("€Wor Workshop"). Never ship the raw accessibility text.

## User preferences — ID Consultoria deck/proposal design

Iterated and validated with the user across multiple rounds (2026-08-14). When building decks/proposals for this user, follow these — each was an explicit correction:

- **Use the ORIGINAL brand assets** — extracted SVG art (backgrounds/contours), vector logos, icons from the source PDF. Hand-drawn replacements were rejected: *"péssimo sem os fundos e a logo originais"*, *"removeu os ícones"*, *"errou o tom"*.
- **Capa (cover)**: foreground in ONE centered block placed in the free portion of the background — logo cliente + vertical divider + logo da marca at top; título 96 (Title) + subtítulo 36 below; meta (Cliente, Preparada por, Data, Válida até) as a 4-column grid at the bottom. Measure the background graphic's extent (parse path bboxes) and start the block after it — the user rejects overlap ("não se sobrepõe ao diamante em background").
- **Slides padrão**: the brand **mark/symbol** (diamond + name letters, WITHOUT tagline) in the top-left corner — the "logo correta" for slide corners is the compact mark, not the full logo with tagline (full logo is for cover/final only). Title + subtitle on every standard slide (e.g. 60 H1 + 24 Body3), content flows below.
- **Type scale** (style guide): Title 96 · H1 60 · H2 48 · H3 36 · Body1 36 · Body2 30 · Body3 24 · Note 20 (Neulis Neue Bold for headings, Nunito Sans Regular for body).
- **Icons**: high-quality thin-stroke icons (Lucide-style) in column titles and cards where it makes sense — "sem exageros" (no icons on every element).
- **List bullets WHITE** (like the source deck), not teal. Leads WHITE, not muted/greyed.
- **Iterate "um slide de cada vez"** — fix and validate one slide at a time, get user sign-off before moving on.
- Explicit colors per element; never auto-infer from the PDF text layer.

## Delivery

Single self-contained `.html` → send via Telegram Bot API `sendDocument` (works directly for `.html`, do NOT zip — see messaging-platforms skill).

## Pitfalls

- Don't put HTML text over an SVG that still contains the original text glyphs — double text when misaligned. Remove glyph paths from the art layer first.
- Don't trust span colors for visible text color — sample the rendered PNG or the drawing fills (white/teal paths).
- Don't promise "identical" without browser verification; expect the user to catch color slips — enumerate colors explicitly per element.
- **Extracted logo components must carry `fill="#ffffff"`** — SVG default fill is black; a white logo over a dark background becomes invisible (exact failure seen: logo rendered but not visible).
- **`{{` in Python f-strings is a LITERAL** `{`; only `{fn()}` executes. Writing `{{col_h3(...)}}` emits literal `{col_h3(...)}` text into the HTML.
- **Browser zoom (e.g. 0.66) distorts the vision model's reading of alignment/centering** — always confirm positions with `getBoundingClientRect`/computed styles, not by eye.
- **List bullets/dots are part of the text path group** — when removing text paths they disappear too. Recreate as `li::before` white circles at a FIXED column per list (compute per-item `left: var(--bx)` since item x0 varies).

## References

- `references/figma-pdf-extraction.md` — pixel-perfect extraction pipeline (working code, opacity sampling, XObject structure).
- `references/consulting-proposal-guide.md` — os 12 princípios de propostas comerciais (deep-research ID Consultoria) + localização do guia e do template HTML com marca ID.
- `references/type3-svg-extraction.md` — extração de logo/shields como componentes SVG (absorvido de pdf-to-html-replication, merge 16/08/2026).
- `references/figma-pdf-pymupdf-pipeline.md` — code patterns: SVG parsing, path bbox, transform composition, text reconstruction (absorvido de pdf-slides-to-html, merge 16/08/2026).
- `references/pdf-to-html-pipeline.md` — technical pipeline completo com thresholds (absorvido de branded-html-replication, merge 16/08/2026).

## Templates de proposta comercial — estrutura aprovada (marca ID)

Depois do deck, o usuário pediu um template HTML adaptável de proposta comercial com a marca ID (merge 16/08/2026 — absorvido de pdf-deck-to-html). Iteração de validação: **"um slide de cada vez"**; quando ele pedir comparação, **listar diferenças sem editar**; validar cada slide antes de seguir.

### Estrutura aprovada (do Guia de Princípios)
Capa → Resumo Executivo (com preço) → Entendimento do Desafio (com "custo de não agir") → Escopo & Entregáveis (com "fora do escopo") → Prova social → Metodologia & Cronograma → **ROI antes do preço** → transição teal → Investimento (3 opções Good-Better-Best, médio "Recomendado") → Garantia → Condições Comerciais → Responsabilidades → Sobre a empresa → Próximos Passos + assinatura → Final.

### Estilo (seguir o deck aprovado, NÃO inventar)
- Capa: logo do cliente (`{{CLIENTE_LOGO_URL}}`, box tracejado "LOGO DO CLIENTE") + divisor + logo ID no topo; título (96) e subtítulo (36) abaixo; meta em grid — tudo num **bloco centralizado na porção direita, NUNCA sobrepondo o diamante/escudo do fundo** (medir a extensão real do escudo no SVG de fundo antes de posicionar).
- Transições: título gigante alinhado à **ESQUERDA** (como o deck original), fundo teal claro (contornos `#679DA3`).
- Slide final: logo + "Proposta válida até {{VALIDADE}}" (teal `#1AAEBD`) + disclaimer.

### Pitfall — usar o EXATO ícone da referência
O header icon dos slides padrão era um diamante teal facetado (3 paths com topografia interna), NÃO o diamante da logo da capa — parecem similares mas diferem; o usuário rejeitou a aproximação. Inspecionar o HTML/SVG de referência (computed styles, paths) — nunca aproximar de memória.
