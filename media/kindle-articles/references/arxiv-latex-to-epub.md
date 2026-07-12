# arXiv LaTeX → Kindle EPUB Pipeline

Full pipeline for converting an arXiv paper's TeX source to a figure-rich EPUB for Kindle, using pandoc for text/tables and PyMuPDF for rendered figure extraction.

## Complete workflow

```bash
# 1. Create workspace
mkdir -p /tmp/arxiv-paper && cd /tmp/arxiv-paper

# 2. Download sources
curl -sL "https://arxiv.org/src/2606.30306" -o source.tar.gz
curl -sL "https://arxiv.org/pdf/2606.30306" -o paper.pdf

# 3. Extract TeX source
tar xzf source.tar.gz
# → main.tex + parts_*.tex + figures + .bbl + references.bib

# 4. Install pandoc (ARM64 — adjust arch for your platform)
curl -sL "https://github.com/jgm/pandoc/releases/download/3.6.4/pandoc-3.6.4-linux-arm64.tar.gz" -o /tmp/pandoc.tar.gz
tar xzf /tmp/pandoc.tar.gz -C /tmp/
PANDOC=/tmp/pandoc-3.6.4/bin/pandoc

# 5. Install Python deps for figure extraction
uv pip install pymupdf pillow

# 6. Convert TeX → base EPUB
$PANDOC main.tex -o output.epub \
  --to epub3 \
  --metadata title="Paper Title" \
  --metadata author="Authors"
```

## Figure extraction strategy

arXiv papers typically have two kinds of figures that pandoc mishandles:

| Figure type | Pandoc output | Fix |
|---|---|---|
| **External PDF figures** (`\includegraphics{file.pdf}`) | `<embed src="media/file0.pdf">` | Render as PNG and replace with `<img>` |
| **TikZ diagrams** (inline LaTeX drawings) | Empty `<figure>` with only `<figcaption>` | Render the compiled PDF page as PNG and inject before `<figcaption>` |

### Finding figure locations in the compiled PDF

Search the PDF text for figure captions:
```python
import fitz
doc = fitz.open('paper.pdf')
keywords = ['Figure 1', 'Figure 2', 'Evolutionary tree', 'Coverage heatmap',
            'persistent-state lifecycle', 'Always-On Evaluation Protocol']
for page_num in range(doc.page_count):
    text = doc[page_num].get_text()
    if any(kw.lower() in text.lower() for kw in keywords):
        print(f"Figure on page {page_num + 1}")
```

### Finding exact figure bounding boxes

Full-page renders capture text above/below the figure. Use `get_text('blocks')` and `get_drawings()` to find the precise figure region:

```python
def find_figure_bbox(page):
    """Find the bounding box of a TikZ figure on a PDF page.
    Returns (x0, y0, x1, y1) in PDF points, or None."""
    blocks = page.get_text('blocks')
    paths = page.get_drawings()
    
    # Strategy 1: use vector drawing bounds for TikZ figures
    big_paths = [p for p in paths 
                 if p['rect'].width > 50 and p['rect'].height > 50]
    if big_paths:
        min_x = min(p['rect'].x0 for p in big_paths)
        min_y = min(p['rect'].y0 for p in big_paths)
        max_x = max(p['rect'].x1 for p in big_paths)
        max_y = max(p['rect'].y1 for p in big_paths)
        return (min_x - 10, min_y - 10, max_x + 10, max_y + 10)
    
    # Strategy 2: find gaps in text block positions
    # Find the paragraph just before the figure and the caption
    caption_block = None
    for block in blocks:
        text = block[4].strip().lower()
        if text.startswith('figure '):
            caption_block = block
            break
    
    if caption_block:
        above_caption_y = caption_block[1]  # y0 of caption
        # Content above caption minus last paragraph text = figure area
        text_end_y = 50  # rough top margin
        for block in blocks:
            if block[5] == 0 and block[3] < caption_block[1] - 20:
                text_end_y = max(text_end_y, block[3])
        
        return (50, text_end_y + 5, 562, above_caption_y - 5)
    
    return None  # fallback — will use full-page smart crop
```

For multi-figure pages (figure + table side by side, or two figures stacked), analyze the text blocks to find vertical gaps that separate figure regions:

```python
def split_multi_figure_page(page):
    """Detect multiple figures on one page and return separate bboxes."""
    blocks = page.get_text('blocks')
    captions = [(i, b) for i, b in enumerate(blocks) 
                if b[4].strip().lower().startswith('figure ')]
    
    if len(captions) <= 1:
        return []
    
    figures = []
    for idx, (cap_idx, caption) in enumerate(captions):
        cap_y0 = caption[1]
        cap_y1 = caption[3]
        
        if idx == 0:
            # First figure: from just after text above to caption bottom
            upper_bound = 50
            for b in blocks[:cap_idx]:
                if b[5] == 0 and b[3] < cap_y0 - 20:
                    upper_bound = max(upper_bound, b[3])
            figures.append((50, upper_bound + 5, 562, cap_y1 + 10))
        else:
            # Nth figure: from previous caption bottom to this caption bottom
            prev_cap = captions[idx - 1][1]
            figures.append((50, prev_cap[3] + 5, 562, cap_y1 + 10))
    
    return figures
```

Then use these precise bboxes when rendering:

```python
clip = fitz.Rect(x0, y0, x1, y1)
mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
pix = page.get_pixmap(matrix=mat, clip=clip)
pix.save(f'{label}.png')
```

### Rendering and cropping figure pages

```python
import fitz, os
from PIL import Image

doc = fitz.open('paper.pdf')
figures = [
    ('fig-evolution', 6),   # External PDF figure
    ('fig-overview', 8),    # TikZ
    ('fig-timeline', 15),   # TikZ
    ('fig-heatmap', 33),    # TikZ
    ('fig-lifecycle', 43),  # TikZ
    ('fig-invariants', 35), # TikZ
    ('fig-aoep', 88),       # TikZ
]

for label, page_num in figures:
    page = doc[page_num - 1]
    pix = page.get_pixmap(dpi=300)
    pix.save(f'{label}.png')
    
    # Smart crop: remove white margins
    img = Image.open(f'{label}.png')
    gray = img.convert('L')
    px = gray.load()
    w, h = img.size
    # Find content bounds
    left, right, top, bottom = w, 0, h, 0
    for y in range(h):
        for x in range(w):
            if px[x, y] < 240:  # non-white pixel
                left, right = min(left, x), max(right, x)
                top, bottom = min(top, y), max(bottom, y)
    cropped = img.crop((max(0,left-20), max(0,top-20),
                        min(w,right+20), min(h,bottom+20)))
    # Resize to Kindle width
    if cropped.width > 1100:
        ratio = 1100 / cropped.width
        cropped = cropped.resize((1100, int(cropped.height * ratio)),
                                  Image.LANCZOS)
    cropped.save(f'{label}.png', optimize=True)
```

For external PDF figures, the embedded image can often be extracted directly:
```python
page = doc[5]  # page 6
images = page.get_images(full=True)
for img_ref in images:
    xref = img_ref[0]
    base_image = doc.extract_image(xref)
    with open('fig-evolution.png', 'wb') as f:
        f.write(base_image["image"])
```

## Table conversion: tabularx → HTML `<table>`

Pandoc handles simple `{tabular}` environments (no X-columns) correctly, producing proper HTML `<table>` tags. But **`tabularx` environments** (and any table using `X` or `Y` column types) produce `<div class="tabularx">` with plain text — rows separated by `<br />`, cells by `&amp;`, column spec in a nested `<span>`. This is unreadable on Kindle.

### The colspec nest problem

Pandoc outputs the column spec as nested `<span>` tags, e.g.:
```html
<span>p<span>0.045</span>p<span>0.20</span>p<span>0.115</span>Yc</span>
```

A naive `re.sub(r'^.*?</span>', ...)` breaks on the first inner `</span>`. Use depth-aware stripping:

```python
def strip_colspec_span(text):
    """Remove the outermost <span>...</span> (with nested spans) from text start."""
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

### Column count from `&amp;`, not colspec

Don't parse the colspec to count columns — the colspec string pandoc emits is incomplete and unreliable. Always use the first data row:

```python
col_count = raw_rows[0].count('&amp;') + 1
```

### Building the `<table>`

Split each row by standalone `&amp;` (respecting HTML tags inside cells), then emit proper `<thead>`/`<tbody>`/`<tr>`/`<th>`/`<td>`:

```python
def split_cells(row_text, expected_cols):
    """Split a table row by standalone &amp; (not inside HTML tags)."""
    # Protect &amp; inside HTML tags
    protected = re.sub(
        r'<[^>]*>',
        lambda m: m.group(0).replace('&amp;', '\x00AMP\x00'),
        row_text
    )
    cells = protected.split('&amp;')
    cells = [c.replace('\x00AMP\x00', '&amp;').strip() for c in cells]
    while len(cells) < expected_cols:
        cells.append('')
    return cells[:expected_cols]

def tabularx_div_to_table(div_html):
    """Convert <div class='tabularx'>...</div> to proper <table>."""
    p_match = re.search(r'<p>(.*)</p>', div_html, re.DOTALL)
    if not p_match:
        return div_html
    p_content = p_match.group(1)
    
    rows_text, colspec_block = strip_colspec_span(p_content)
    raw_rows = re.split(r'<br\s*/?>', rows_text)
    raw_rows = [r.strip() for r in raw_rows if r.strip()]
    if not raw_rows:
        return div_html
    
    col_count = max(raw_rows[0].count('&amp;') + 1, 1)
    
    # Build table
    parts = ['<table>\n<thead>\n<tr>']
    header_cells = split_cells(raw_rows[0], col_count)
    for c in header_cells:
        parts.append(f'<th scope="col">{c}</th>')
    parts.append('</tr>\n</thead>')
    
    if len(raw_rows) > 1:
        parts.append('<tbody>')
        for row in raw_rows[1:]:
            cells = split_cells(row, col_count)
            is_bold = any('<strong>' in c or '<b>' in c for c in cells)
            parts.append('<tr>')
            for c in cells:
                parts.append(
                    f'<th scope="row">{c}</th>' if is_bold 
                    else f'<td>{c}</td>'
                )
            parts.append('</tr>')
        parts.append('</tbody>')
    parts.append('</table>')
    return '\n'.join(parts)
```

Apply to all HTML files in the unpacked EPUB:

```python
for fname in sorted(os.listdir('epub_dir/EPUB/text/')):
    if not fname.endswith('.xhtml'):
        continue
    path = os.path.join('epub_dir/EPUB/text', fname)
    with open(path, 'r') as f:
        html = f.read()
    start_count = html.count('class="tabularx"')
    if start_count == 0:
        continue
    
    # One replacement at a time avoids re.DOTALL cross-match issues
    new_html = re.sub(
        r'<div class="tabularx">.*?</div>',
        lambda m: tabularx_div_to_table(m.group(0)),
        html,
        flags=re.DOTALL
    )
    if new_html != html:
        with open(path, 'w') as f:
            f.write(new_html)
```

## Full pipeline script

The complete pipeline — figure extraction, table conversion, EPUB rebuild, and Kindle delivery — is available as a reusable script at `scripts/arxiv-latex-to-kindle.py`. Run it in the TeX workspace directory after downloading the arXiv source and PDF.

## Post-processing the pandoc EPUB

After extraction, unpack the pandoc EPUB and patch the HTML:

```python
import zipfile, os, re

# Extract
with zipfile.ZipFile('output.epub') as z:
    z.extractall('epub_dir')

# Patch each HTML file
for filename in os.listdir('epub_dir/EPUB/text/'):
    if not filename.endswith('.xhtml'):
        continue
    path = os.path.join('epub_dir/EPUB/text', filename)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace PDF embeds with <img>
    html = re.sub(
        r'<embed\s+src="\.\./media/file0\.pdf"\s*/>',
        '<img src="../media/fig-evolution.png" alt="..." style="max-width:100%;height:auto;" />',
        html
    )
    
    # Insert images into empty TikZ <figure> tags
    for img_name, fig_id in [
        ('fig-overview.png', 'fig:overview'),
        ('fig-timeline.png', 'fig:timeline'),
        ('fig-heatmap.png', 'fig:heatmap'),
        ('fig-lifecycle.png', 'fig:lifecycle'),
        ('fig-invariants.png', 'fig:invariants'),
        ('fig-aoep.png', 'fig:aoep'),
    ]:
        pattern = r'(<figure\s+id="' + re.escape(fig_id) + r'">)\s*\n(\s*)(<figcaption)'
        replacement = (
            r'\1\n\2<img src="../media/' + img_name + r'" alt="Figure" style="max-width:100%;height:auto;" />\n\2\3'
        )
        html = re.sub(pattern, replacement, html)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

# Update OPF manifest: add image entries, remove file0.pdf
with open('epub_dir/EPUB/content.opf', 'r') as f:
    opf = f.read()
opf = re.sub(r'\s*<item\s+id="file0_pdf".*?/>', '', opf)
# Add image manifest entries before </manifest>
img_entries = ''
for fname in ['fig-evolution.png', 'fig-overview.png', 'fig-timeline.png',
              'fig-heatmap.png', 'fig-lifecycle.png', 'fig-invariants.png',
              'fig-aoep.png']:
    img_entries += f'\n    <item id="{fname.replace(".", "_")}" href="media/{fname}" media-type="image/png" />'
opf = opf.replace('</manifest>', img_entries + '\n  </manifest>')
with open('epub_dir/EPUB/content.opf', 'w') as f:
    f.write(opf)

# Re-package EPUB3
with zipfile.ZipFile('final.epub', 'w', zipfile.ZIP_DEFLATED) as zout:
    zout.write('epub_dir/mimetype', 'mimetype', compress_type=zipfile.ZIP_STORED)
    for root, dirs, files in os.walk('epub_dir'):
        for fname in sorted(files):
            full = os.path.join(root, fname)
            arcname = os.path.relpath(full, 'epub_dir')
            if arcname == 'mimetype':
                continue
            zout.write(full, arcname)
```

## Kindle-optimized CSS for LaTeX papers

Replace the pandoc-generated CSS with Kindle-tested rules:

```css
body {
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.5;
  text-align: justify;
  hyphens: auto;
  widows: 2;
  orphans: 2;
}
p { text-indent: 1.2em; margin: 0.3em 0; }
figure { margin: 1em auto; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
figcaption { font-size: 0.85em; font-style: italic; text-indent: 0; }
table { margin: 1em 0; border-collapse: collapse; width: 100%; font-size: 0.85em; }
th, td { padding: 0.3em 0.5em; border: 1px solid #ccc; }
code { font-family: "Courier New", monospace; font-size: 0.85em; }
pre { font-family: "Courier New", monospace; font-size: 0.8em;
      background: #f8f8f8; border-left: 2px solid #ddd; padding: 0.5em 1em; }
```

## Sending to Kindle

```python
# See kindle-manga/references/gmail-kindle-delivery.md for full details
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/opt/data/google_token.json"
KINDLE_EMAIL = "gustavomelloenciv_0yDkTw@kindle.com"

creds = Credentials.from_authorized_user_file(TOKEN_PATH, [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('gmail', 'v1', credentials=creds)
msg = MIMEMultipart()
msg['To'] = KINDLE_EMAIL
msg['Subject'] = "Paper Title"
msg.attach(MIMEText("Sent via Hermes Agent.", 'plain'))

with open('final.epub', 'rb') as f:
    part = MIMEBase('application', 'epub+zip')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="paper.epub"')
    msg.attach(part)

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
print(f'Sent! Message ID: {result["id"]}')
```

## Pitfalls

- **Architecture mismatch**: Pandoc releases are per-architecture. ARM64 (aarch64) needs `linux-arm64.tar.gz`; x86_64 needs `linux-amd64.tar.gz`. Check with `uname -m`.
- **TikZ figures produce empty `<figure>`** → pandoc keeps the `<figcaption>` but the figure body is blank. You must inject images from the compiled PDF.
- **Figure page numbers change** with different LaTeX compilation settings. Always scan the PDF captions to find the right page for each figure.
- **`.bbl` files ignored** — pandoc reads the `.bbl` content during LaTeX→EPUB conversion but may not include the full bibliography. Check the reference section in the output.
- **Math**: Rendered as `<span class="math inline/display">` spans. Not rendered as proper math. Fine for reference reading.
- **Gmail 25 MB limit**: A full paper with 7 color PNGs at 1100px is ~5 MB. Fine for most papers.
