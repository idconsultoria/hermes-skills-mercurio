---
name: pdf-to-html-replication
description: "Convert PDF decks/documents to faithful HTML — pixel-perfect or semantic.

Load this skill when converting a PDF deck or document to faithful HTML, whether the user wants pixel-perfect positioning or clean semantic structure. Covers brand asset extraction (logos, icons, backgrounds) and the pitfalls of Type3/Figma exports. Complements html-pdf-fidelity for the reverse direction."
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [pdf, html, svg, type3, figma, presentation, replication]
    related_skills: [pdf, html-pdf-fidelity, messaging-platforms]
type: ToolIntegration
timestamp: 2026-08-14T05:35:18Z
---

# PDF → HTML Replication

## When to Use

- User asks to convert a PDF deck/slide/proposal to HTML: "replique esses slides em HTML", "faz um html inspirado nesse", "converte essa apresentação para web".
- Rebuilding a branded document (proposal, deck) as an editable web page where the original vector art must be preserved.
- Any Figma-exported PDF where text extraction looks wrong (missing letters, `€` artifacts, invisible text).

Converts a PDF (especially Figma-exported decks) into an HTML file that looks like the original. Validated end-to-end 14/ago/2026 with user Gustavo Mello (ID Consultoria) on the Minuzzo proposal deck: three iterations, the third was approved as "perfeito".

## The winning formula (user-validated — do not skip)

**Semantic HTML structure + ORIGINAL vector art as a background layer + explicit foreground text.**

- `.bg` = original SVG art extracted from the PDF (contour lines, shields, logos, icons, photos). **NEVER redraw the art by hand.**
- `.fg` = semantic HTML (`h1/h2/h3/p/ul/li`) with explicit color/font per element.
- User REJECTED a fully hand-drawn-background version: *"péssimo sem os fundos e a logo originais... errou o tom e as fontes... removeu os ícones"*. Accepted the hybrid (original art + semantic text): *"Parabéns, agora ficou perfeito"*.

## Pipeline

1. **Analyze** each page: `page.get_text("dict")` (lines/spans), `page.get_drawings()` (fills/strokes), `page.get_images(full=True)`, `page.get_xobjects()`.
2. **Detect Type3 fonts** (Figma export signature): the *visible* text is drawn as **vector paths inside Form XObjects**; the BT/ET text operators are an invisible accessibility layer (span color often `#000000` on a black slide — the real text is white/teal paths). Consequence: PyMuPDF redaction (`add_redact_annot` + `apply_redactions`) does **NOT** remove the visible text — the render stays pixel-identical.
3. **Convert each page to SVG** with `page.get_svg_image()` — preserves Z-order, group opacity (e.g. blob layers at `opacity=".4"`), and raster images as base64 data URIs. ~1MB/page typical.
4. **Strip text glyphs from the SVG**: remove `<path>` elements whose fill is a text color (white/teal) AND whose rendered bbox overlaps a text-line bbox. Keep logo art (white paths in brand regions don't overlap lines → kept).
5. **Extract reusable brand components** (logo, shields) from the cleaned SVG into standalone `<svg viewBox=...>` components — see `references/type3-svg-extraction.md` for the working code (including the classic bug: SVG default `fill` is black; the extracted logo must carry `fill="#ffffff"` or it's invisible on a black slide).
6. **Build the HTML**: inline SVG as `.bg` (absolute, z-index 0), semantic elements positioned in the PDF's regions (absolute coordinates from the line bboxes are fine — the user wants "nascido HTML" syntax, not necessarily pure flow layout). Embed fonts as base64 `@font-face`.

## Pitfalls

- **Text removal rule**: single-line overlap `inter/area > 0.15` is not enough — big text-block paths span many lines, so also remove when `sum(intersections with all lines)/path_area > 0.35`. Art paths sit near 0.02–0.05, so the threshold is safe.
- **Bullets/dots are usually part of the SAME white path as the text** and get removed together. Recreate as `li::before` circles, positioned at the fixed bullet column (extract column x from a crop; items often have different text x but a shared bullet x).
- **`<use data-text>` layer**: carries clean characters BUT ligature glyphs (`fi`, `fl`) drop the second char (`Artificial` → `Artifcial`). The accessibility layer has the full text but maps nbsp to `€` and can duplicate fragments. Fix: difflib alignment — base = data-text, reinsert deleted `i`/`l` only when preceded by `f`. See references.
- **`€` in extracted text = `\xa0` (nbsp)**, not the euro sign.
- **Transition/title slides may draw the section number inside the title's white path bbox** (e.g. `"1. Plano de Trabalho"` — the accessibility layer misses the `1.`). Crop-render the left edge of the title to check for drawn numbers.
- **The chip/rounded rect behind a price** can be removed as "text" if its bbox overlaps a price line (the price sits inside it). Re-add it as a CSS element with explicit width.
- **Colors**: never infer text color from span colors (that's the invisible layer). Sample the rendered page pixels or match drawing fills by bbox overlap; then set colors EXPLICITLY per element — the user will point out each wrong color otherwise.
- **Verify in a real browser** (browser_navigate to `file://` + browser_vision + `document.fonts.check('700 96px "Neulis Neue"')`), and run an overflow check on every slide (`.fg > *` rect vs slide rect).

## User preferences (Gustavo / ID Consultoria)

- Keep original brand assets (logos, icons, background art, tone) — copy them from the source, never redraw.
- Semantic tags: `section/h1/h2/h3/p/ul/li`; foreground/background as clearly separated layers.
- Slides at native 1920×1080, no navigation UI, "slides crus".
- Deliver via Telegram Bot API `sendDocument` from TUI (`.html` arrives directly; do NOT zip — see messaging-platforms skill).
