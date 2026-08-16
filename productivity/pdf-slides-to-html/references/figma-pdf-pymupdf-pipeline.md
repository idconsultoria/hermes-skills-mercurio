# Figma-export PDF → PyMuPDF pipeline (working code patterns)

Validated on a 1920×1080 proposal deck (8 pages, Type3 fonts, Form XObjects). Python venv:
`uv venv .venv && uv pip install --python .venv/bin/python pymupdf lxml`.

## Anatomy recap

- Page stream: `q /E1 gs /X1 Do Q` (blob art at 40% opacity via `/ca .4`) then BT/ET text with a
  Type3 font — INVISIBLE (black on black), used only for copy/paste (`get_text`).
- The REAL glyphs live in the Form XObjects as white/teal filled paths.
- `page.get_svg_image()` returns a complete SVG: `<use data-text="R" xlink:href="#font_8_12"
  transform="matrix(60,0,0,-60,X,Y)"/>` (invisible accessibility glyph, empty def) followed by
  `<path transform="matrix(1,0,0,-1,X,Y)" d="..."/>` (the visible glyph outline).

## Path bbox with transforms (SVG coords = PDF coords, y-down)

```python
def parse_transform(tr):
    m = re.match(r'matrix\(([^)]+)\)', tr.strip() or '')
    return [float(x) for x in m.group(1).replace(',', ' ').split()] if m else None

def compose(t1, t2):  # t1 then t2
    if t1 is None: return t2
    if t2 is None: return t1
    a1,b1,c1,d1,e1,f1 = t1; a2,b2,c2,d2,e2,f2 = t2
    return [a1*a2+c1*b2, b1*a2+d1*b2, a1*c2+c1*d2, b1*c2+d1*d2, a1*e2+c1*f2+e1, b1*e2+d1*f2+f1]

def apply_matrix(m, x, y):
    return (m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5])
```

Compose ALL ancestor `<g>` transforms + own transform, then transform the local path bbox
(parse `d` with a mini M/L/C/H/V tokenizer).

## Classifying text paths for removal

A path is TEXT (remove) when its fill ∈ `{white, #4ac6d3, #1baebe}` AND:

```python
# per-line: intersection/area > 0.15, OR
# multi-line blocks: sum(intersections with all lines) / path_area > 0.35
```

Why 0.35: one path may contain an entire multi-line paragraph block (its bbox covers lines +
gaps); per-line ratio lands ~0.44 and fails the old 0.5 bar. Art paths score ~0.02–0.05.

## Clean text reconstruction

```python
# group <use data-text> glyphs to lines by: line bbox contains (X, Y) origin,
# NO vertical padding (b[1] <= y <= b[3]+1) — padding merges adjacent lines.
# sort by X, join chars -> clean text
# then fix ligatures: 'fi'/'fl' glyphs carry only 'f' in data-text.
import difflib
sm = difflib.SequenceMatcher(None, access_text, clean_text, autojunk=False)
# for 'delete' opcodes: if deleted in ('i','l') and previous output char == 'f': re-insert
# access_text = get_text line, with '\u20ac' -> '\xa0' (nbsp mapping)
```

## Opacity detection (0.4 blob layer)

Sample the rendered page (1x pixmap) at the drawing group's path points; dark `#3a3a3a` fills
blend to `(23,23,23)` over black at 0.4. Teal `#4ac6d3` at 1.0 samples `(73,198,211)`; at 0.4
samples `(29,79,84)`. Don't sample rect centers — contour art is sparse; walk the path points.

## SVG id namespacing

```python
ids = set(re.findall(r'id="([^"]+)"', svg))
for i in ids:
    svg = re.sub(r'(?<![A-Za-z0-9_])#' + re.escape(i) + r'\b', '#' + prefix + i, svg)
    svg = re.sub(r'id="' + re.escape(i) + r'"', 'id="' + prefix + i + '"', svg)
```

## Recreated-in-HTML items the art layer loses

- **Bullets**: white 10px circles at a fixed column x (e.g. 78 left col, 958 right col); offset
  per li via `style="--bx:{bullet_x - li_left}px"` + `li::before{left:var(--bx)}`.
- **Numbered titles**: "1. Plano de Trabalho" — the "1." is part of the title path (path bbox
  starts ~32px left of `get_text` bbox); add it back manually in the HTML text.
- **Discount chip**: a `#1AAEBD` rounded rect behind a price gets classified as TEXT (it overlaps
  the price line) and removed; recreate as a div with fixed width + radius, label ABOVE it.
- **Line heights**: vertical advance between PDF lines (30px text → 41px, 24px → 32px,
  96px two-line titles → 115px). `<br>` inside `p/li` forces the PDF's exact line breaks.
