#!/usr/bin/env python3
"""
arXiv LaTeX → Kindle EPUB pipeline.
Complete conversion: pandoc base → figure extraction → table fix → rebuild → send.

Usage:
  cd /path/to/extracted/tex  # main.tex, paper.pdf, parts_*.tex
  python3 arxiv-latex-to-kindle.py

Requires: pandoc binary at /tmp/pandoc-3.6.4/bin/pandoc (or set PANDOC env var)
Requires: pymupdf, pillow (pip install pymupdf pillow)
"""
import re, os, sys, zipfile, shutil, json, subprocess
from xml.sax.saxutils import escape as xml_escape

PANDOC = os.environ.get('PANDOC', '/tmp/pandoc-3.6.4/bin/pandoc')
OUT_EPUB = 'paper_output.epub'
TMP_DIR = '/tmp/epub_rebuild'
SRC_TEX = 'main.tex'

# ──────────────────────────────────────────────
# STEP 1: Pandoc conversion
# ──────────────────────────────────────────────
def run_pandoc():
    if not os.path.exists(SRC_TEX):
        sys.exit(f'ERROR: {SRC_TEX} not found. Run from the TeX workspace.')
    print('=== Step 1: Pandoc LaTeX → EPUB ===')
    subprocess.run([PANDOC, SRC_TEX, '-o', OUT_EPUB, '--to', 'epub3',
                    '--metadata', 'title=arXiv Paper',
                    '--metadata', 'author=Authors'], check=True)
    print(f'  → {OUT_EPUB}')

# ──────────────────────────────────────────────
# STEP 2: Figure extraction helpers
# ──────────────────────────────────────────────
def find_figure_pages(pdf_path):
    """Scan PDF for pages containing figure captions."""
    import fitz
    doc = fitz.open(pdf_path)
    fig_pages = {}
    for pnum in range(doc.page_count):
        text = doc[pnum].get_text()
        for m in re.finditer(r'Figure\s+(\d+)', text):
            fig_num = int(m.group(1))
            fig_pages.setdefault(fig_num, []).append(pnum + 1)
    doc.close()
    return fig_pages

def find_figure_bbox(page):
    """Find exact TikZ figure bounding box using vector drawings."""
    paths = page.get_drawings()
    big = [p for p in paths if p['rect'].width > 50 and p['rect'].height > 50]
    if big:
        return (min(p['rect'].x0 for p in big) - 10,
                min(p['rect'].y0 for p in big) - 10,
                max(p['rect'].x1 for p in big) + 10,
                max(p['rect'].y1 for p in big) + 10)
    return None

def extract_figures(pdf_path, figures):
    """Extract figures with precise cropping or embedded image extraction."""
    import fitz
    from PIL import Image
    doc = fitz.open(pdf_path)
    
    for fig in figures:
        page = doc[fig['page'] - 1]
        out = fig['name']
        
        # Prefer embedded image extraction
        images = page.get_images(full=True)
        if images:
            xref = images[0][0]
            base = doc.extract_image(xref)
            with open(out, 'wb') as f:
                f.write(base['image'])
            img = Image.open(out)
            if img.width > 1100:
                r = 1100 / img.width
                img = img.resize((1100, int(img.height * r)), Image.LANCZOS)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(out, optimize=True)
            print(f'  ✓ {out} (embedded, {img.width}x{img.height})')
            continue
        
        # Try vector drawing bbox
        bbox = find_figure_bbox(page)
        if not bbox:
            bbox = fig.get('crop') or (50, 50, 562, 742)
        
        clip = fitz.Rect(*bbox)
        mat = fitz.Matrix(300/72, 300/72)
        pix = page.get_pixmap(matrix=mat, clip=clip)
        pix.save(out)
        
        img = Image.open(out)
        gray = img.convert('L')
        px = gray.load()
        w, h = img.size
        left, right, top, bottom = w, 0, h, 0
        for y in range(h):
            for x in range(w):
                if px[x, y] < 240:
                    left, right = min(left, x), max(right, x)
                    top, bottom = min(top, y), max(bottom, y)
        if left < right and top < bottom:
            pad = 15
            img = img.crop((max(0,left-pad), max(0,top-pad),
                            min(w,right+pad), min(h,bottom+pad)))
        if img.width > 1100:
            r = 1100 / img.width
            img = img.resize((1100, int(img.height * r)), Image.LANCZOS)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(out, optimize=True)
        print(f'  ✓ {out} (bbox {bbox}, {img.width}x{img.height})')
    
    doc.close()

# ──────────────────────────────────────────────
# STEP 3: Table conversion (tabularx → HTML)
# ──────────────────────────────────────────────
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

def split_cells(row_text, expected_cols):
    """Split by standalone &amp; (not inside HTML tags)."""
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

def convert_tabularx_div(div_html):
    p_match = re.search(r'<p>(.*)</p>', div_html, re.DOTALL)
    if not p_match:
        return div_html
    p_content = p_match.group(1)
    rows_text, _ = strip_colspec_span(p_content)
    raw_rows = re.split(r'<br\s*/?>', rows_text)
    raw_rows = [r.strip() for r in raw_rows if r.strip()]
    if not raw_rows:
        return div_html
    col_count = max(raw_rows[0].count('&amp;') + 1, 1)
    parts = ['<table>\n<thead>\n<tr>']
    for c in split_cells(raw_rows[0], col_count):
        parts.append(f'<th scope="col">{c}</th>')
    parts.append('</tr>\n</thead>')
    if len(raw_rows) > 1:
        parts.append('<tbody>')
        for row in raw_rows[1:]:
            cells = split_cells(row, col_count)
            is_bold = any('<strong>' in c or '<b>' in c for c in cells)
            parts.append('<tr>')
            for c in cells:
                parts.append(f'<th scope="row">{c}</th>' if is_bold else f'<td>{c}</td>')
            parts.append('</tr>')
        parts.append('</tbody>')
    parts.append('</table>')
    return '\n'.join(parts)

def fix_tables(html):
    return re.sub(
        r'<div class="tabularx">.*?</div>',
        lambda m: convert_tabularx_div(m.group(0)),
        html,
        flags=re.DOTALL
    )

# ──────────────────────────────────────────────
# STEP 4: Rebuild EPUB
# ──────────────────────────────────────────────
def rebuild_epub(fig_list):
    """Fix tables, inject figures, update manifest, re-package."""
    print('\n=== Step 4: Rebuild EPUB ===')
    
    # Extract pandoc base
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    with zipfile.ZipFile(OUT_EPUB) as z:
        z.extractall(TMP_DIR)
    
    # 4a. Convert tabularx → tables
    txt_dir = os.path.join(TMP_DIR, 'EPUB', 'text')
    for fname in sorted(os.listdir(txt_dir)):
        if not fname.endswith('.xhtml'):
            continue
        path = os.path.join(txt_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        count = html.count('class="tabularx"')
        if count == 0:
            continue
        html = fix_tables(html)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  Tables: {fname} → {count} fixed')
    
    # 4b. Copy figures
    media_dir = os.path.join(TMP_DIR, 'EPUB', 'media')
    os.makedirs(media_dir, exist_ok=True)
    for fig in fig_list:
        src = fig['name']
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(media_dir, fig['name']))
    
    # 4c. Inject images into HTML
    for fig in fig_list:
        if not fig.get('fig_id'):
            continue
        for fname in sorted(os.listdir(txt_dir)):
            if not fname.endswith('.xhtml'):
                continue
            path = os.path.join(txt_dir, fname)
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
            modified = False
            
            # Replace PDF embeds
            if fig.get('is_pdf_embed'):
                pattern = r'<embed\s+src="\.\./media/' + re.escape(fig['pdf_file']) + r'"\s*/>'
                if re.search(pattern, html):
                    html = re.sub(pattern, 
                        f'<img src="../media/{fig["name"]}" alt="{fig.get("alt","Figure")}" style="max-width:100%;height:auto;" />',
                        html)
                    modified = True
            
            # Insert into empty <figure>
            pat = r'(<figure\s+id="' + re.escape(fig['fig_id']) + r'">)\s*\n(\s*)(<figcaption)'
            rep = (r'\1\n\2<img src="../media/' + fig['name'] 
                   + r'" alt="' + fig.get('alt','Figure') + r'" style="max-width:100%;height:auto;" />\n\2\3')
            new = re.sub(pat, rep, html)
            if new != html:
                html = new
                modified = True
            
            if modified:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html)
    
    # 4d. Update OPF manifest
    opf_path = os.path.join(TMP_DIR, 'EPUB', 'content.opf')
    with open(opf_path, 'r', encoding='utf-8') as f:
        opf = f.read()
    # Remove any old PDF file entries
    opf = re.sub(r'\s*<item\s+id="file0_pdf".*?/>', '', opf)
    # Add image entries
    img_entries = ''
    for fig in fig_list:
        iid = fig['name'].replace('.', '_')
        img_entries += f'\n    <item id="{iid}" href="media/{fig["name"]}" media-type="image/png" />'
    opf = opf.replace('</manifest>', img_entries + '\n  </manifest>')
    with open(opf_path, 'w', encoding='utf-8') as f:
        f.write(opf)
    
    # 4e. Re-package
    final = os.path.splitext(OUT_EPUB)[0] + '_final.epub'
    with zipfile.ZipFile(final, 'w', zipfile.ZIP_DEFLATED) as zout:
        mt = os.path.join(TMP_DIR, 'mimetype')
        if os.path.exists(mt):
            zout.write(mt, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(TMP_DIR):
            for fname in sorted(files):
                full = os.path.join(root, fname)
                arcname = os.path.relpath(full, TMP_DIR)
                if arcname == 'mimetype':
                    continue
                zout.write(full, arcname)
    
    print(f'  → {final} ({os.path.getsize(final)/1024:.0f} KB)')
    return final


if __name__ == '__main__':
    from PIL import Image
    
    run_pandoc()
    
    # You must define your figures here for each paper:
    # Each entry: {name, page (1-indexed), fig_id, alt, is_pdf_embed?, pdf_file?, crop?}
    FIGURES = [
        {'name': 'fig-01.png', 'page': 6, 'fig_id': 'fig:first',
         'alt': 'Figure'},
        # ... add more
    ]
    
    if not os.path.exists('paper.pdf'):
        sys.exit('ERROR: paper.pdf not found. Download from arxiv.org/pdf/<ID>')
    
    print('\n=== Step 2: Figure extraction ===')
    extract_figures('paper.pdf', FIGURES)
    
    final_epub = rebuild_epub(FIGURES)
    print(f'\nDone! EPUB ready: {final_epub}')
