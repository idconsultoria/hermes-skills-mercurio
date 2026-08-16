---
name: branded-html-replication
description: "Replicate designed PDFs/decks as faithful branded HTML — assets, fonts, SVG.

Load this skill when recreating a designed document (PDF slides, deck, proposal) as HTML that carries the brand faithfully: backgrounds, logos, icons, fonts, colors — optionally as clean semantic HTML instead of pixel-perfect positioning. Validated with the ID Consultoria deck + proposal template (Aug 2026). Extracts brand assets from PDF for HTML use."
metadata:
  hermes:
    tags: [html, pdf, replication, brand, svg, template, deck]
version: 1.0.0
author: hermes
license: MIT
type: Creative
timestamp: 2026-08-14T00:00:00Z
---

# Branded HTML Replication

Recreate a designed document (PDF slides, deck, proposal) as HTML that carries the brand faithfully: same backgrounds, logos, icons, fonts, colors — optionally with clean semantic structure ("nascido HTML") instead of pixel-perfect positioning. Validated with the ID Consultoria deck + proposal template (Aug 2026).

## When to use
- User asks to replicate a PDF/deck as HTML: "pixel-perfect", "fortemente inspirado", or "nascido HTML"
- User wants a reusable brand template (proposal, deck) built from a reference document
- Extracting brand assets (logo, icons) from a PDF for HTML use

## Core workflow

### Phase 1 — Analyze the PDF (PyMuPDF)
1. Page sizes + text spans: `page.get_text("dict")` → per-line bbox, size, text
2. Drawings: `page.get_drawings()` → vector shapes with fill/stroke + rect
3. Images: `page.get_images()` + `get_image_rects()`; XObjects: nested Form XObjects wrap the art; `/E1 gs` sets opacity (e.g. `ca .4` → 0.4 layer)

**Key insight — Type3 fonts:** text extracted by PyMuPDF (the BT/ET layer) is usually an *invisible accessibility layer* (black, garbled chars like €). The VISIBLE text is drawn as vector paths (white/teal) inside the XObjects. Consequences:
- Redaction does NOT remove the visible text — redaction is useless for text-free backgrounds here
- The visible text color comes from the path fills, NOT the span color

### Phase 2 — Convert to SVG and strip text
1. `page.get_svg_image()` → full vector SVG (draw order, opacity, masks preserved; images embedded as data URIs)
2. Identify text paths: filled paths (white/teal/#1baebe) whose rendered bbox overlaps accessibility line bboxes. **Multi-line blocks are ONE path spanning several lines** — per-line intersection ratio fails; use `sum(intersections)/path_area > 0.35`
3. Remove them → clean art-only SVG (the `.bg` layer)
4. Reconstruct clean visible text from `<use data-text="X">` elements (the SVG accessibility layer): group by (scale, Y), sort by X. **Ligature bug:** 'fi'/'fl' glyphs lose the 'i'/'l' in data-text — re-insert via difflib alignment against the dict text
5. Namespace all SVG ids per slide (`s0_mask_1`, `s1_mask_1`...) — ids collide across slides and break masks/clips

### Phase 3 — Brand asset extraction
- Extract logo/icon components from the clean SVG by filtering paths whose rendered bbox falls in the target region (parse `d` + compose `matrix(1,0,0,-1,X,Y)` transforms)
- **Pitfall: preserve fill** — copying `<path transform=... d=...>` without `fill="#fff"` renders BLACK (invisible on dark bg). Copy the fill attribute or set it on the wrapper
- **Use the EXACT icon the reference uses.** Inspect the reference HTML/SVG. E.g. the standard-slide header icon was a faceted teal diamond (3 paths with internal topography), NOT the capa logo diamond — they look similar but differ; the user rejected the approximation

### Phase 4 — Semantic HTML
- `.slide > svg` (art layer, z-index 0) + `.fg` (semantic content h1/h2/h3/p/ul/li, z-index 1)
- Explicit colors per element; follow the reference deck's choices (e.g. white bullets, not teal)
- When the user says "copy the v3 / the reference" — OPEN the reference HTML and inspect the actual source (computed styles, SVG paths), don't approximate from memory

### Verification
- `browser_navigate(file://...)` + `browser_console` computed styles — **the vision model HALLUCINATES positioning** (claims centered when right-aligned, mixes adjacent slides, misreports colors). Verify coordinates programmatically: `getBoundingClientRect()`, `getComputedStyle()`
- Overflow check: every `.fg > *` rect must stay inside its slide rect
- Fonts loaded: `document.fonts.check('700 96px "Neulis Neue"')`
- The browser session resets to `about:blank` between tool calls — re-navigate before inspecting

## User preferences (Gustavo / ID Consultoria)
- Brand assets must be EXACT copies from the original — never recreated approximations
- Style guide: Neulis Neue Bold (Title 96 / H1 60 / H2 48 / H3 36), Nunito Sans Regular (Body1 36 / Body2 30 / Body3 24 / Note 20)
- Palette: black bg, white text, teal #4AC6D3, teal-deep #1AAEBD
- Slide layouts: capa = centered foreground block on the right of the background diamond; standard slides = header icon (faceted teal diamond) + title 60 + subtitle 24 stacked below
- Semantic HTML structure; foreground/background separation (.fg / .bg) kept editable
- Iterate one slide at a time; wait for explicit approval before the next
- Telegram from TUI: `sendDocument` with .html works directly (no zip needed); `MEDIA:` only routes from gateway sessions

## References
- `references/pdf-to-html-pipeline.md` — full technical pipeline with code patterns and thresholds
