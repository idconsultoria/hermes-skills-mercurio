# Type3 / Figma-export PDF → SVG text extraction (working code)

Validated 14/ago/2026 on the Minuzzo proposal deck (1920×1080, 8 pages, Type3 fonts).

## Why redaction fails on Type3 text

`page.add_redact_annot(bbox)` + `apply_redactions(...)` removes the BT/ET text operators,
but the VISIBLE glyphs are vector paths inside nested Form XObjects (`/X1 Do` chains).
Result: `get_text()` returns 0 chars after redaction, but the render is **pixel-identical**
(0 diff across the whole page). Do not go down this path.

## The reliable pipeline (PyMuPDF 1.28)

```python
import pymupdf, re, json
from lxml import etree

doc = pymupdf.open('deck.pdf')
page = doc[1]
svg = page.get_svg_image()          # str; ~1MB/page; images as base64 data URIs
root = etree.fromstring(svg.encode('utf-8'))
SVG = 'http://www.w3.org/2000/svg'
```

### Transform/bbox helpers (SVG uses matrix(1,0,0,-1,X,Y) — y-flip)

```python
def parse_transform(tr):
    if not tr: return None
    m = re.match(r'matrix\(([^)]+)\)', tr.strip())
    return [float(x) for x in m.group(1).replace(',', ' ').split()] if m else None

def compose(t1, t2):  # t1 then t2
    if t1 is None: return t2
    if t2 is None: return t1
    a1,b1,c1,d1,e1,f1=t1; a2,b2,c2,d2,e2,f2=t2
    return [a1*a2+c1*b2, b1*a2+d1*b2, a1*c2+c1*d2, b1*c2+d1*d2, a1*e2+c1*f2+e1, b1*e2+d1*f2+f1]

def apply(m, x, y): return (m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5])

def path_bbox(d):
    toks = re.findall(r'[MmLlCcHhVvZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)
    xs, ys = [], []; x = y = 0.0; cmd = None; i = 0
    while i < len(toks):
        t = toks[i]
        if t.isalpha(): cmd = t; i += 1; continue
        if cmd in ('M','L','m','l'): x = float(t); y = float(toks[i+1]); i += 2
        elif cmd in ('C','c'):
            for k in range(3): x = float(toks[i]); y = float(toks[i+1]); i += 2
        elif cmd in ('H','h'): x = float(t); i += 1
        elif cmd in ('V','v'): y = float(t); i += 1
        else: i += 1; continue
        xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0,0,0,0)

def tr_bbox(m, bb):
    x0,y0,x1,y1 = bb
    pts = [apply(m,x0,y0), apply(m,x1,y0), apply(m,x0,y1), apply(m,x1,y1)]
    return (min(p[0] for p in pts), min(p[1] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts))

def abs_bbox(el):
    m = None; anc = el.getparent(); chain = []
    while anc is not None and etree.QName(anc).localname != 'svg':
        chain.append(anc); anc = anc.getparent()
    for g in reversed(chain): m = compose(m, parse_transform(g.get('transform')))
    m = compose(m, parse_transform(el.get('transform')))
    return tr_bbox(m, path_bbox(el.get('d'))) if m else None
```

### Text-line bboxes from the accessibility layer

```python
d = page.get_text("dict")
lines = []
for block in d["blocks"]:
    if block["type"] != 0: continue
    for line in block["lines"]:
        text = ''.join(s["text"] for s in line["spans"])
        if text.strip():
            lines.append({'bbox': line["bbox"], 'text': text,
                          'size': max(s["size"] for s in line["spans"])})
```

### Remove text glyph paths (white/teal fills overlapping lines)

```python
TEXT_FILLS = {'#ffffff', '#4ac6d3', '#1baebe', '#679da3'}
def inter_area(b1, b2):
    ix = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
    iy = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
    return ix * iy

for el in list(root.iter(f'{{{SVG}}}path')):
    fill = el.get('fill')
    if fill is None or fill.lower() not in TEXT_FILLS: continue
    bb = abs_bbox(el); area = (bb[2]-bb[0]) * (bb[3]-bb[1])
    hit = False; s = 0
    for lb in [l['bbox'] for l in lines]:
        i = inter_area(bb, lb); s += i
        if i and area and i/area > 0.15: hit = True; break
    if not hit and area and s/area > 0.35:   # multi-line block paths
        hit = True
    if hit:
        p = el.getparent()
        if p is not None: p.remove(el)
```

### Reconstruct clean text — ligature fix (difflib)

The invisible `<use data-text="...">` layer has clean chars but drops the second char
of `fi`/`fl` ligatures. The accessibility text has all chars but maps nbsp→`€` and can
duplicate fragments (e.g. `"Duração:€Wor Workshop"` vs correct `"Duração: Workshop"`).

```python
import difflib
def fix_ligatures(data_text, access_text):
    access = access_text.replace('\u20ac', '\xa0')   # € == nbsp
    sm = difflib.SequenceMatcher(None, access, data_text, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            out.append(data_text[j1:j2])
        elif tag == 'delete':
            d = access[i1:i2]
            prev = out[-1][-1] if out and out[-1] else ''
            if d in ('i', 'l') and prev == 'f':      # ligature continuation
                out.append(d)
        else:
            out.append(data_text[j1:j2])
    return ''.join(out)
```

### Extracting a brand logo component

Select white paths whose bbox falls in the logo region, emit a standalone SVG
carrying the ORIGINAL per-path transforms and an explicit `fill`:

```python
vb = f"{min(xs)-10} {min(ys)-10} {max(xs)-min(xs)+20} {max(ys)-min(ys)+20}"
parts = [f'<path fill="#ffffff" transform="{p["transform"]}" d="{p["d"]}"/>' for p in logo_paths]
svg = f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
```

⚠️ **SVG default `fill` is black.** Without `fill="#ffffff"` the logo renders
invisible on a black slide — symptom is "logo not visible" in browser while the
element is present in the DOM with 57 paths. Always copy the fill.

## Repeated verification checklist

- `browser_console`: `document.fonts.check('700 96px "Neulis Neue"')` — fonts loaded?
- Overflow check per slide: every `.fg > *` rect must stay inside the slide rect.
- Side-by-side crop vs the PDF render when the user reports a color/position issue.
- The vision model misreads zoomed pages; trust programmatic rects over its spatial claims.
