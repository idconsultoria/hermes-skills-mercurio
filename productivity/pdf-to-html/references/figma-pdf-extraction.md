# Figma-export PDF → pixel-perfect HTML — working pipeline

Validated 2026-08-14 on a 8-page 1920×1080 proposal deck (Type3 fonts, Figma export). PyMuPDF 1.28.2 in a `uv venv` (no system poppler needed).

## 0. Analysis pass

```python
import pymupdf
doc = pymupdf.open('deck.pdf')
for page in doc:
    print(page.rect)                       # page size (1920x1080 here)
    page.get_text("dict")                  # spans: text, font, size, color, bbox
    page.get_drawings()                    # vector shapes: fill, stroke, rect, items
    page.get_images(full=True)             # raster images
    page.get_image_rects(xref)             # placement of each image
    page.get_svg_image()                   # full vector SVG of the page
```

## 1. The Type3 two-layer discovery (critical)

- Text extraction finds spans, but **colors are lies** (all `#000000` even when visible text is white) and some glyphs map to `€` (U+20AC) = the original was a non-breaking space.
- `apply_redactions()` on text span bboxes → `get_text()` returns 0 chars but the rendered pixmap is **byte-identical** — the visible text lives in vector paths inside Form XObjects, not in the text operators.
- Content-stream structure to expect: page stream draws black bg + `/X1 Do` (nested Form XObjects with the art) + `BT/ET` text (invisible accessibility layer, Type3 font). White/teal glyph paths live in the XObjects.

## 2. SVG structure from `page.get_svg_image()`

- `<defs>` holds masks/clips and `font_8_*` groups — the glyph defs are **EMPTY**.
- Visible text = `<path transform="matrix(1,0,0,-1,X,Y)" d="..."/>` with fill `#ffffff` / `#4ac6d3` / `#1baebe` (one path per glyph; a whole paragraph block can be ONE path with many subpaths).
- Invisible layer = `<use data-text="X" xlink:href="#font_8_N" transform="matrix(scale,0,0,-scale,X,Y)"/>` — references empty defs (renders nothing) but `data-text` carries the CLEAN characters.
- Decorative blob layers are wrapped in `<g opacity=".4">` (from `gs /ca .4`).

## 3. Removing text glyphs from the art SVG

Classify a path as TEXT when:
1. fill is text-ish (`#ffffff`, `#4ac6d3`, `#1baebe`, …), AND
2. its rendered bbox (parse `d`, compose ancestor transforms with `matrix(1,0,0,-1,X,Y)`) overlaps an accessibility line bbox.

Multi-line blocks: one path covers a whole paragraph → use **sum of intersections with ALL lines / path area > 0.35** (single-line ratio test alone misses blocks; 0.5 was too high).

Critical: this rule ALSO deletes colored art that happens to sit behind text (e.g. a teal discount chip behind a price) — keep a whitelist of non-text fills, or accept it and re-draw the element in HTML/CSS.

## 4. Rebuilding clean visible text

- Group `<use data-text>` by line: assign use to the line whose bbox contains its origin `(X, Y)` **with NO vertical padding** (padding mixes adjacent lines' uses).
- `fi`/`fl` ligatures: the invisible layer drops the `i`/`l` after `f`. Fix:

```python
import difflib
clean = ''.join(sorted chars by x)          # from data-text
access = raw_span_text.replace('\u20ac', '\xa0').replace('\r','').replace('\n','')
out = []
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, access, clean, autojunk=False).get_opcodes():
    if tag == 'equal': out.append(clean[j1:j2])
    elif tag == 'delete':
        d = access[i1:i2]
        if d in ('i','l') and (out[-1][-1] if out and out[-1] else '') == 'f':
            out.append(d)                    # ligature continuation
    elif tag == 'insert': out.append(clean[j1:j2])
    else: out.append(clean[j1:j2])
```

- Numbered markers: "1. Plano de Trabalho" — the `1.` glyphs are inside the same white path group; text extraction gives only "Plano de Trabalho" while the white path bbox starts ~32pt earlier. Crop the rendered page to confirm, then prepend manually.

## 5. Opacity of art layers

- `get_drawings()` gives fills but not opacity state.
- Sample the rendered pixmap AT the path's own item points (move/line/curve coords, page coords from `get_drawings`): dark gray `#3a3a3a` sampled as `(23,23,23)` ⇒ 40% over black (`58*0.4≈23`). Teal full-opacity samples as `(73,198,211)`; teal 40% as `(29,79,84)`. Center-point sampling fails on sparse line art — walk the path points instead.

## 6. Assembling the HTML

- Namespace every SVG id per slide (`mask_1` → `s0_mask_1`) or the browser resolves all `url(#...)` refs to the FIRST slide's defs.
- Embed fonts base64 in `@font-face`; single self-contained file.
- Verify via browser console, not vision: `document.fonts.check('700 96px "X"')`, computed colors, `getBoundingClientRect` overflow scan across all slides.
- Line-height = span bbox height; font-size = span size; color = explicit per element (never from span color).
