---
name: arxiv-latex-to-kindle
description: "Convert arXiv LaTeX to Kindle EPUB — tables, figures, Gmail delivery.

Load this skill when the user wants to download an arXiv paper, convert its LaTeX source to EPUB, and deliver it to a Kindle device. Handles the full pipeline: arXiv source download, Pandoc conversion, post-processing for tabularx→HTML table conversion, precise figure extraction from the PDF, EPUB rebuild, and Gmail API delivery."
summary: "End-to-end arXiv LaTeX→EPUB pipeline: download source, Pandoc conversion, tabularx→HTML table fix, PyMuPDF figure extraction with precise crop, EPUB rebuild, Kindle delivery via Gmail API."
version: 1.1.0
author: Hermes
license: MIT
tags: [arxiv, latex, epub, kindle, pandoc, tables, pymupdf, academic-papers]
type: Media
timestamp: 2026-07-08T10:30:00Z
---

# arXiv LaTeX → Kindle EPUB Pipeline

Convert academic papers from arXiv LaTeX source to Kindle EPUB with proper HTML tables and precisely cropped figures. Pandoc converts `tabularx` to `<div>` elements instead of `<table>`, and embedded PDF figures (TikZ, vector graphics) don't survive the conversion — this pipeline fixes both.

## When to load

- User asks to download an arXiv paper for their Kindle
- User wants to convert `main.tex` to EPUB
- Pandoc output has `<div class="tabularx">` instead of `<table>`
- Figures in the EPUB are blank, missing, or rendered as full PDF pages
- User reports tables not rendering correctly on Kindle
- Any "arXiv paper → Kindle" request

## Prerequisites

- **Pandoc 3.x** (arm64 binary at `/tmp/pandoc-3.6.4/bin/pandoc`)
- **Python venv** with packages: `pymupdf` (fitz), `Pillow`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`
- **Gmail OAuth2 token** at `/opt/data/google_token.json` (scopes: `gmail.send`, `gmail.readonly`, `gmail.modify`)
- **Kindle email** (user-specific, stored in memory)

## Full pipeline

### Phase 1: Download arXiv source

```bash
# Get paper URL from user (e.g. "2606.30306")
PAPER_ID="2606.30306"
SRC_DIR="/opt/data/arxiv-${PAPER_ID}"
# Download source
curl -sL "https://arxiv.org/src/${PAPER_ID}" -o "/tmp/arxiv-${PAPER_ID}.tar.gz"
mkdir -p "$SRC_DIR"
tar xzf "/tmp/arxiv-${PAPER_ID}.tar.gz" -C "$SRC_DIR/"
# Download PDF for figure extraction
PDF_URL="https://arxiv.org/pdf/${PAPER_ID}.pdf"
curl -sL -o "${SRC_DIR}/paper.pdf" "$PDF_URL"
```

### Phase 2: Base Pandoc conversion

```bash
/tmp/pandoc-3.6.4/bin/pandoc "$SRC_DIR/main.tex" -o /tmp/test-output.epub --to epub3
```

Key option: `--to epub3` — produces EPUB3 with proper XHTML structure, figure IDs, and tabularx divs.

### Phase 3: Diagnose table structure

Check how many `<table>` tags Pandoc generated vs how many `\begin{table}` / `\begin{tabular}` are in the LaTeX:

```bash
# After extracting EPUB to /tmp/epub_rebuild/
cd /tmp/epub_rebuild/EPUB/text
grep -c '<table' *.xhtml          # actual HTML tables
grep -c 'tab:' *.xhtml            # tab reference anchors
```

Pandoc converts `tabularx` to `<div class="tabularx">` with this structure:
```html
<div class="tabularx">
<p><span>p<span>0.045</span>p<span>0.20</span>Yc</span> Header1 &amp; Header2 &amp; Header3<br />
Cell1 &amp; Cell2 &amp; Cell3<br />
</p></div>
```

Note: the colspec `<span>` has **nested `<span>` tags** for width specifications — a simple regex like `<span>(.*?)</span>` will match the wrong closing tag.

### Phase 4: Precise figure identification

Use PyMuPDF to find exact figure bounding boxes on each page:

```python
import fitz
doc = fitz.open(f'{SRC_DIR}/paper.pdf')

for page_num in range(len(doc)):
    page = doc[page_num]
    # Find text blocks to identify figure areas
    blocks = page.get_text('blocks')
    images = page.get_images(full=True)
    
    # Check for embedded images (external PDF figures)
    if images:
        for img_info in images:
            bbox = page.get_image_bbox(img_info)
            print(f"  Image at {bbox}")
    
    # Find tables to distinguish from figures
    tables = page.find_tables()
    
    # Look for captions (blocks starting with 'Fig.' or 'Table')
    for b in blocks:
        text = b[4][:50]
        if text.startswith('Fig.') or text.startswith('Table'):
            print(f"  Page {page_num+1}: {text[:60]}")

doc.close()
```

Key method: `page.get_text('blocks')` returns all content blocks with their bounding boxes — use this to identify figure regions, caption locations, and distinguish vector-drawn figures (no embedded images) from table blocks.

### Phase 5: Figure crop definitions

Build a `FIGURES` list with per-figure crop bounds:

```python
FIGURES = [
    {
        'name': 'fig-example.png',
        'page': 5,                          # 1-indexed page number
        'crop': (60, 60, 555, 400),         # (x0, y0, x1, y1) in PDF points
        'embedded': False,                  # True = extract from embedded image stream
        'alt': 'Descriptive alt text',
        'fig_id': 'fig:example-id',         # Pandoc figure ID from LaTeX \label
    },
]
```

**For embedded images** (`'embedded': True`): Extract from the image stream instead of rendering. Use `page.get_images(full=True)` to find the xref, then `doc.extract_image(xref)` to get the raw bytes. This preserves original resolution.

**For rendered figures** (`'embedded': False`): Use `fitz.Rect()` + `page.get_pixmap(clip=rect, matrix=Matrix(300/72, 300/72))` to render just the crop region at 300 DPI. Apply smart-crop (remove white margins by scanning pixel values < 240) and resize to max 1100px wide.

**Two figures on the same page:** Define separate `FIGURES` entries with different `crop` values. PyMuPDF handles them independently.

### Phase 6: tabularx → HTML table conversion

#### The problem

Pandoc converts `tabularx` LaTeX environments to:
```html
<div class="tabularx">
<p><span>p<span>0.045</span>p<span>0.20</span>Yc</span> Header1 &amp; Header2 &amp; Header3<br />
Cell1 &amp; Cell2 &amp; Cell3<br />
</p></div>
```

No `<table>`, no `<thead>`, no `<th>` — just `<div>` with `<br>`-separated rows and `&amp;`-separated cells. Kindle renders this as plain inline text.

#### The fix — strip_colspec_span()

The colspec wrapper `<span>` has **nested span tags** for width values. Removing it requires depth-aware parsing:

```python
def strip_colspec_span(text):
    """Remove outermost <span>...</span> (with nested spans) from text start."""
    if not text.startswith('<span'):
        return text, ''
    depth = 0
    i = 0
    while i < len(text):
        if text[i:i+6] == '<span>' or text[i:i+7] == '<span ':
            j = text.find('>', i)
            if j > i and text[j-1] != '/':
                depth += 1
                i = j + 1
                continue
        elif text[i:i+7] == '</span>':
            depth -= 1
            i += 7
            if depth == 0:
                while i < len(text) and text[i] in ' \t\n\r':
                    i += 1
                return text[i:], text[:i]
            continue
        i += 1
    return text, ''
```

**Why this is needed:** A simple `r'^.*?</span>'` regex matches only the first `</span>` (the innermost one inside the colspec), leaving the colspec text and outer `</span>` in the rows. This corrupts the first cell.

#### Column count

**ALWAYS** count from the first row's `&amp;` occurrences, never from the colspec string. Pandoc's colspec representation is unreliable when nested spans are stripped:

```python
col_count = raw_rows[0].count('&amp;') + 1
```

#### Cell splitting

Split by `&amp;` that appears **outside** HTML tags. Use placeholder substitution to protect `&amp;` inside tag attributes or content:

```python
def split_cells(row_text, expected_cols):
    # Protect &amp; inside HTML tags
    protected = re.sub(r'<[^>]*>', lambda m: m.group(0).replace('&amp;','\x00AMP\x00'), row_text)
    cells = protected.split('&amp;')
    cells = [c.replace('\x00AMP\x00','&amp;').strip() for c in cells]
    while len(cells) < expected_cols:
        cells.append('')
    return cells[:expected_cols]
```

#### Table structure

Build a proper `<table>` with:
- First row → `<thead>` with `<th scope="col">`
- Subsequent rows → `<tbody>` with `<td>` (or `<th scope="row">` for **bold/Total rows**)
- Rows containing `<strong>` or `<b>` in any cell should use `<th scope="row">`

### Phase 7: Inject figures and rebuild EPUB

1. **Copy figures** into `EPUB/media/`
2. **Replace PDF embed tags**: Pandoc generates `<embed src="../media/file0.pdf"/>` for external PDF figures — replace with `<img>` pointing to the extracted PNG
3. **Inject `<img>` before `<figcaption>`**: For each `<figure id="fig:...">`, insert `<img src="../media/fig-name.png" />` right after the `<figure>` opening tag and before `<figcaption>`
4. **Update OPF manifest**: Remove `file0.pdf` entry, add PNG image entries
5. **Replace CSS** with Kindle-optimized table styling:
   - `table { border-collapse: collapse; width: 100%; font-size: 0.85em; }`
   - `th, td { padding: 0.3em 0.5em; border: 1px solid #999; }`
   - `thead { border-bottom: 2px solid #666; }`
   - `tbody tr:last-child { border-bottom: 2px solid #666; }`
6. **Re-package** via Python `zipfile.ZipFile` with `ZIP_DEFLATED` compression (keep `mimetype` first, uncompressed)

### Phase 8: Send to Kindle

Use Gmail API with `MIMEBase('application', 'epub+zip')`:

```python
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

msg = MIMEMultipart()
msg['To'] = KINDLE_EMAIL
msg['Subject'] = "Paper Title"
msg.attach(MIMEText("Body text", 'plain'))

with open(epub_path, 'rb') as f:
    part = MIMEBase('application', 'epub+zip')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
        'attachment; filename="paper_title.epub"')
    msg.attach(part)

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
result = service.users().messages().send(
    userId='me', body={'raw': raw}
).execute()
```

## Validation checklist

Run these checks before declaring success:

- [ ] **Tables**: Count `<table>` tags across all XHTML — should match or exceed `\begin{table}` count in LaTeX (minus any tabular in the source that aren't table floats)
- [ ] **Table columns**: Verify complex tables (benchmarks, comparisons) have correct column counts — check `ch007`, `ch008` (governance, evaluation)
- [ ] **Figure images**: Each PNG in the manifest has a corresponding file in `EPUB/media/`
- [ ] **file0.pdf residue**: Verify no `file0.pdf` in the EPUB ZIP (remove from OPF manifest and media directory)
- [ ] **Evolution tree / embedded figures**: Pandoc embeds external PDF figures as `<embed>` tags — verify they're replaced with `<img>`
- [ ] **Two figures on same page**: Verify both lifecycle and invariants figures (page 43) are present and don't overlap
- [ ] **CSS table styling**: Verify `border-collapse`, `thead`, and `tbody tr:last-child` borders are in the CSS
- [ ] **EPUB size**: Should be reasonable (~1-3 MB for typical paper with figures)
- [ ] **Duplicate IDs**: Scan all XHTML for intra-page duplicate `id` attributes — Kindle renderer can skip content when encountering them. Run: `python3 -c \"import re, zipfile; z = zipfile.ZipFile('output.epub'); [print(f'  INTRA-PAGE dup \"{i}\" in {n}') for n in sorted(z.namelist()) if n.endswith('.xhtml') and 'cover' not in n for (i, seen) in [({}, []) for _ in [1]] for c in [z.read(n).decode()] for id_ in re.findall(r'id=\\"([^\\\"]+)\\"', c) if (seen.append(id_) or True) if seen.count(id_) > 1]; z.close()\"`
- [ ] **Image rendering in browser**: Before sending to Kindle, spot-check an XHTML page with images by extracting it and opening locally: `python3 -c \"from zipfile import ZipFile; import os; z = ZipFile('output.epub'); [os.makedirs(f'/tmp/epub_test/images', exist_ok=True) or open(f'/tmp/epub_test/{n}', 'wb').write(z.read(n)) for n in z.namelist() if 'images/' in n]; c = z.read('OEBPS/xhtml/ch0038.xhtml').decode().replace('src=\"../images/', 'src=\"images/'); open('/tmp/epub_test/ch0038.html','w').write(c); css = z.read('OEBPS/css/style.css'); open('/tmp/epub_test/style.css','wb').write(css); print('Open file:///tmp/epub_test/ch0038.html in browser to verify'); z.close()\"`

## Known pitfalls

- **Nested `<span>` in colspec**: Pandoc wraps tabularx column specifications as `<span>p<span>0.045</span>p<span>0.20</span>Yc</span>` with nested spans. Do NOT use simple regex to extract colspec — use depth-aware `strip_colspec_span()`.
- **Column count from colspec is unreliable**: Pandoc sometimes merges or drops column width info. Always count from `raw_rows[0].count('&amp;') + 1`.
- **Figures in PDF as embedded images**: Some figures (evolution trees, diagrams) exist as embedded PNG/JPEG images within the PDF. Extract with `doc.extract_image(xref)` rather than rendering the page area — preserves original quality.
- **Multiple figures per page**: Define separate `FIGURES` dict entries with distinct crop rectangles. PyMuPDF handles independent clip regions.
- **Pandoc figure IDs**: Pandoc generates `<figure id="fig:xyz">` from LaTeX `\label{fig:xyz}`. Match figure injection to these IDs.
- **Smart crop white margins**: After rendering a clip region, the actual figure may not fill the full crop box. Scan pixel values and trim to content (threshold: < 240/255).
- **OPF manifest must list all PNGs**: Missing manifest entries cause EPUB validation warnings. Each figure needs `<item id="..." href="media/..." media-type="image/png" />`.
- **Gmail token scopes**: Must include `gmail.send`, `gmail.readonly`, `gmail.modify` for the refresh token flow.
- **token.json path**: `/opt/data/google_token.json` for this environment.
- **Kindle email**: Stored in memory; always reference from there.
- **EPUB envelope**: Use `files=.../always_on_agents.epub`, subject and body text inside script, send via Gmail API (not `gws` CLI which only sends text).
- **`&amp;` inside HTML tags**: Cell content may contain `<span class="citation" data-cites="...">` where `&amp;` inside data attributes should NOT be treated as column separators. Protect them by substituting during split.
- **"Total" rows with multicolumn**: LaTeX `\\multicolumn` rows produce fewer cells than the column count. The split fills missing cells with `''` — the resulting HTML may have an empty-looking cell. Acceptable on Kindle, but verify visually.

**Kindle image rendering debugging**

When the user reports images not rendering on their Kindle (only some images appear, or none at all), follow this systematic approach. The issue is almost always in the EPUB structure or HTML, not the PNG file itself.

**Diagnosis sequence:**

1. **Rule out file corruption**: Extract images from the EPUB ZIP and compare MD5 hashes with source files. If they match, the images are correctly stored — move on.

2. **Verify images render in a browser**: Extract an XHTML page with a broken image and open it locally (see the browser-check script in the Validation checklist above). If images render in Chrome but not on Kindle, the issue is Kindle-specific (converter pipeline or firmware limitations).

3. **Check for MathML presence on the image page** ⚠️ — Strong empirical correlation: every XHTML page that renders images correctly on Kindle also contains inline `<math>` elements on the same page; pages without any MathML fail to show images. Before deeper debugging, check whether all image-bearing pages have MathML:
   ```python
   import re
   from zipfile import ZipFile
   z = ZipFile('output.epub')
   for n in sorted(z.namelist()):
       if not n.endswith('.xhtml') or 'cover' in n: continue
       c = z.read(n).decode()
       if re.search(r'figure-img', c):
           print(f'{n}: MathML={bool(re.search(r"<math[ >]", c))}')
   z.close()
   ```
   **Working hypothesis**: Kindle's renderer uses a different layout engine for XHTML pages containing MathML (full-web pipeline that handles `<img>` correctly) vs plain pages (a simpler book pipeline with image-rendering bugs). If confirmed, possible workarounds (try in order):
   - Change image CSS to `display:inline-block !important` (avoids a `display:block` + `width:100%` bug in the simple pipeline)
   - Convert images from PNG to JPEG (Q95+) — the AZW3 converter handles JPEG more reliably
   - Inject a tiny hidden `<math>` element on image-bearing pages to trigger the web pipeline

4. **Check for duplicate HTML IDs**: Kindle's EPUB→KF8 converter uses strict XML parsing. Intra-page duplicate `id` attributes (e.g. `<span id="fig-X"/>` then `<p id="fig-X">` on the same page) can cause the Kindle renderer to skip content on that page. Fix by ensuring each `id` is unique within its XHTML file.

5. **Add explicit width/height to `<img>` tags**: Kindle's layout engine performs better when images have explicit pixel dimensions. Read PNG dimensions from the IHDR chunk (pure Python, no Pillow needed):
   ```python
   import struct
   with open(path, 'rb') as f:
       f.read(8)  # signature
       length = struct.unpack('>I', f.read(4))[0]
       chunk_type = f.read(4)
       assert chunk_type == b'IHDR'
       w = struct.unpack('>I', f.read(4))[0]
       h = struct.unpack('>I', f.read(4))[0]
   ```
   Emit: `<img src="..." width="W" height="H" alt=""/>` alongside CSS `max-width:100%;height:auto`.

6. **Strip optional PNG metadata chunks**: Some Kindle firmware versions choke on optional chunks (sRGB, gAMA, cHRM). Rewrite PNGs keeping only IHDR, IDAT, IEND:
   ```python
   KEEP = {b'IHDR', b'IDAT', b'IEND', b'PLTE', b'tRNS'}
   ```
   If the images are already minimal (common with web-scraped PNGs), this step is a no-op.

7. **Convert PNG to JPEG** (last resort): If all else fails, convert images to JPEG (Q95+). Amazon's EPUB→AZW3 converter handles JPEG more reliably than PNG. Use `ffmpeg` if ImageMagick/Pillow aren't available:
   ```bash
   ffmpeg -y -i input.png -q:v 95 -frames:v 1 -update 1 output.jpg
   ```
   Update the builder to use `.jpg` extensions and the JPEG media type in the OPF manifest.

**CSS that works on Kindle:**
```css
.figure-img{text-align:center;margin:1em 0;page-break-inside:avoid}
.figure-img img{max-width:100% !important;height:auto !important;display:inline-block !important;margin:0;vertical-align:middle}
```
- `display:block` can cause invisible images on some Kindle firmware (especially without MathML on the page). Prefer `display:inline-block` with `!important`.
- `width:100%` + `display:block` interacts poorly with Kindle's reading-position tracking. Drop `width:100%`, use `max-width:100%` only.
- Always use `!important` on image CSS rules — the converter may inject its own stylesheet that overrides yours.
