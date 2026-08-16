# PDF → Branded HTML Pipeline — Technical Reference

Validated pipeline for extracting a Figma-exported PDF (Type3 fonts) into faithful HTML with original vector art. Tools: PyMuPDF (pymupdf), lxml, Python 3.13, uv venv.

## Setup
```bash
uv venv .venv && uv pip install --python .venv/bin/python pymupdf lxml
```

## 1. PDF analysis
```python
import pymupdf
doc = pymupdf.open(path)
# page sizes, spans (accessibility layer), drawings, images
d = page.get_text("dict")          # lines with bbox, size
dr = page.get_drawings()           # vector shapes: fill, color, width, rect, items
page.get_images(full=True)         # raster images (logos, photos)
page.get_xobjects()                # nested Form XObjects (art lives here)
```
- 1920×1080 slides = 1 pt = 1 px.
- Opacity layers: streams start with `q /E1 gs /X1 Do Q` where `/E1 << /ca .4 >>` — the dark blob layer renders at 0.4 opacity (verify by sampling the render: fill (58,58,58) @0.4 over black → (23,23,23)).

## 2. Type3 font reality
- `get_text("dict")` spans come from the **invisible accessibility layer** (black color, garbage chars: € for nbsp, duplicated runs like "€Wor").
- The **visible text** = white/teal vector paths inside the Form XObjects. `apply_redactions()` removes only the BT/ET operators — the rendered pixels are unchanged (0-pixel diff). Don't use redaction for text-free backgrounds.
- Per-line visible colors come from matching drawing fills (white / #4ac6d3 / #1baebe), not span colors.

## 3. SVG conversion + text stripping
```python
svg = page.get_svg_image()          # str; paths + masks + opacity preserved
```
Text appears twice in the SVG:
- `<use data-text="R" xlink:href="#font_8_12" transform="matrix(60,0,0,-60,X,Y)"/>` — invisible glyph, but carries the REAL char in `data-text` and the baseline Y.
- `<path transform="matrix(1,0,0,-1,X,Y)" d="..."/>` — the VISIBLE glyph paths (to be removed).

**Remove visible text paths:** a path is text if its rendered bbox overlaps accessibility line bboxes and:
- `inter/area > 0.15` for a single line, OR
- `sum(intersections over all lines)/area > 0.35` (multi-line blocks are one giant path — e.g. a 4-line bullet list is a single path spanning all lines; per-line ratio ≈ 0.08 fails).

**Rebuild clean text from `<use>`:** group uses by (scale, Y), sort by X, concatenate `data-text`. **Ligature drop:** 'fi'/'fl' glyphs store only 'f' — use `difflib.SequenceMatcher` against the dict text and re-insert deleted single 'i'/'l' when the previous char is 'f'. Skip deleted blocks that are multi-char (those are accessibility-layer dupes).

**Namespace ids:** each slide's SVG has `mask_1`, `clip_2`, `font_8_*` — prefix every `id="X"` and `#X` reference with `s{slide}_` or the browser resolves url(#...) to the FIRST match and masks break.

## 4. Brand asset extraction
Filter paths by rendered bbox (compose ancestor transforms + `matrix(1,0,0,-1,X,Y)`; parse `d` with a tokenizer for M/L/C/H/V):
```python
if target_x0 <= bb.x0 and bb.x1 <= target_x1 and target_y0 <= bb.y0 and bb.y1 <= target_y1:
    kept.append(path)
```
- **Always keep/copy the `fill` attribute** (or set it on the wrapper svg). A `<path>` copied without fill defaults to BLACK — invisible on dark backgrounds. This bit once: the extracted logo rendered but was invisible.
- The reference may use DIFFERENT-but-similar icons in different contexts (capa logo diamond vs standard-slide header diamond). Inspect the actual reference SVG (e.g. `page_01_clean.svg` header icon = 3 paths with internal topography, bbox ≈ 78–160 × 82–156) rather than reusing the capa mark.

## 5. Semantic HTML assembly
```html
<section class="slide">
  <svg class="bg" viewBox="0 0 1920 1080" ...>  <!-- art-only SVG, z-index 0 -->
  <div class="fg">                                <!-- semantic content, z-index 1 -->
    <h1 class="title">...</h1><p class="subtitle">...</p>
```
- Embed fonts as base64 `@font-face` data URIs (Neulis Neue Bold OTF ≈ 83 KB → 111 KB b64; Nunito Sans latin woff2 ≈ 14 KB).
- Explicit colors per element. Follow the reference exactly (e.g. bullets white, not teal).
- When a "transition" slide's teal background gets reused for a content slide, recalibrate element colors for contrast (white icons instead of teal, white border on chips/notes).

## 6. Verification (browser)
- `browser_navigate(file://...)` then `browser_console` with `getBoundingClientRect()` / `getComputedStyle()` / `document.fonts.check()`.
- The auxiliary vision model hallucinates layout: claims centered-when-right-aligned, mixes adjacent slides, misreports colors, calls icon shapes by invented names. Trust programmatic rects, not vision prose.
- Overflow probe: for each slide, every `.fg > *` rect must be within the slide rect.
- Browser session can drop to `about:blank` between calls — re-navigate before inspecting.
