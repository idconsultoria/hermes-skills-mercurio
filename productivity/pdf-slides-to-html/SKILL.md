---
name: pdf-slides-to-html
description: "Convert PDF slide decks to HTML — original art preserved, real text.

Load this skill when the user hands over a PDF slide deck / proposal / presentation and wants it as HTML: pixel-perfect clone, strongly inspired rebuild, or semantic HTML. Also applies when the PDF came out of Figma or contains unselectable text. Covers analysis, vector art extraction, and semantic HTML output."
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [pdf, html, slides, pymupdf, figma, svg, presentation]
    related_skills: [html-pdf-fidelity, html-to-pdf-chromium, pdf]
type: ToolIntegration
timestamp: 2026-08-14T05:00:55Z
---

# PDF Slides → HTML

## When to Use

Use when the user hands over a PDF slide deck / proposal / presentation and wants it as HTML:
pixel-perfect clone, "strongly inspired" rebuild, or semantic HTML. Also applies when the PDF
came out of Figma or contains text you cannot select/edit reliably.

Convert presentation decks (PDF) into HTML. Covers the full pipeline: analyze the PDF, extract
vector art + clean text, and produce a semantic HTML file that looks like the original.

## User expectations (ID Consultoria decks) — READ FIRST

Learned from the Minuzzo proposal job (3 iterations, user rejected 2). This is the contract:

1. **Semantic HTML wins over pixel-perfect.** Structure with real tags: `section` per slide,
   `h1/h2/h3`, `p`, `ul/li`. No div-per-coordinate soup if avoidable.
2. **BUT keep the ORIGINAL visual assets.** Backgrounds, logos, icons, contour art, photos,
   exact tone — extract them from the source PDF and use them. NEVER hand-recreate brand art
   (hand-drawn contour SVGs, HTML-rebuilt logos, guessed colors). The user rejected a
   fully hand-made "inspired" version: *"Ficou péssimo sem os fundos e a logo originais.
   Parece que errou o tom... e removeu os ícones."*
3. **Separate foreground from background.** Art layer (`.slide > svg`, z-index 0) vs content
   layer (`.fg`, z-index 1). Each editable independently.
4. **Working formula** (v3, accepted): original art SVG extracted from the PDF as background +
   semantic HTML content positioned at the PDF's layout coordinates (left/top per block or line).
5. **Colors on this deck style:** default text WHITE; section headers teal `#4AC6D3`; footer /
   discount chip `#1AAEBD`; background black. When in doubt, ask which colors are wrong instead
   of guessing.
6. **Style guide:** Neulis Neue Bold = Title 96 / H1 60 / H2 48 / H3 36 (headers only);
   Nunito Sans Regular = Body1 36 / Body2 30 / Body3 24 / Note 20. 36px is Bold ONLY for
   section headers (e.g. "Plano de Trabalho"), Regular otherwise (subtitles/footers).

## Figma-export PDF anatomy (the key insight)

Decks exported from Figma look like ordinary PDFs but have a hidden structure:

- **Visible text is drawn as VECTOR PATHS** inside Form XObjects (often white/teal fills).
- The BT/ET text layer (`get_text`) is an invisible **accessibility layer** — same glyphs in
  black, with corrupted character mapping (e.g. `€` = non-breaking space, duplicated runs like
  `€Wor Workshop`).
- `get_drawings()` / `get_svg_image()` return the REAL rendering (paths, fills, opacity).
- Background art uses `gs /ca .4` (40% opacity) groups — sample rendered pixels along path
  points to confirm effective opacity per fill color.
- `page.apply_redactions()` removes ONLY the invisible text layer; the visible vector text
  survives → renders identical. Do not rely on redaction to strip text.

## Pipeline

1. **Analyze** with PyMuPDF (`uv venv` + `uv pip install pymupdf`): page count/size (deck = 1920×1080),
   dump spans per line, `get_drawings()` fills/rects, `get_images()` placements.
2. **Extract art:** `page.get_svg_image()` per page → full vector SVG with correct order,
   opacity, embedded raster images (logos, photos) as data URIs.
3. **Separate text from art in the SVG:** `<use data-text="X">` = invisible accessibility glyphs
   (clean characters!); visible glyphs = `<path fill="#fff|#4ac6d3|#1baebe">` whose rendered bbox
   overlaps text line bboxes. Remove those paths. Multi-line blocks need a sum-intersection ratio
   (> 0.35 of path bbox area) — a per-line ratio misses one path covering many lines.
4. **Rebuild clean text** from `data-text` uses (sort by x within each line bbox; no vertical
   bbox padding — adjacent line bboxes overlap and scramble uses). Fix `fi`/`fl` ligature drops
   (glyph carries `data-text='f'` only) by difflib-alignment against the accessibility text.
5. **Namespace SVG ids per slide** (`mask_1` → `s0_mask_1`, `url(#...)` too) — ids collide across
   slides and browsers resolve to the first match.
6. **Build HTML:** `.slide > svg` (art, absolute inset 0) + `.fg` with semantic tags positioned at
   the PDF line bboxes (left/top, line-height = vertical advance between lines: 41px for 30px
   text, 32px for 24px, etc.). Use `<br>` inside li/p to force the PDF's line breaks.
7. **Recreate what the art layer lost:** bullets (small white circles, fixed column x, offset via
   `--bx` custom property), discount chips (rect that the text-removal filter wrongly ate because
   it overlapped a price line), numbered-title prefixes ("1."/"2." — they're part of the title
   path, ~32px left of the extracted text bbox).
8. **Verify in a real browser** (`browser_navigate` file:// + `browser_console`): fonts loaded
   (`document.fonts.check`), computed colors, zero overflow, chip/label geometry. `browser_vision`
   misreads long stacked pages — prefer programmatic checks for position/color truth.

## Pitfalls

- Never trust `get_text()` output for final text — ligatures, nbsp (`\xa0`), and duplicated
  runs corrupt it. `data-text` is clean but drops ligature parts; merge both.
- Text removal threshold: path bbox vs single line ratio fails for multi-line blocks; use
  sum-of-intersections / path-area.
- Redaction ≠ text removal for Figma PDFs (vector text survives).
- SVG `getBBox()` ignores transforms — apply `getCTM()` before comparing positions.
- A "missing" number in a title ("1. Plano de Trabalho") is usually inside the title's white
  path — check the path bbox left edge vs the text bbox.
- Test fonts in the actual browser; data-URI fonts can silently fall back.

## Support files

- `references/figma-pdf-pymupdf-pipeline.md` — working code patterns: SVG parsing, path bbox,
  transform composition, text reconstruction, classification.
