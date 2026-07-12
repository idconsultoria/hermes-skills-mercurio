# Kindle EPUB Image Debugging — Diagnostic Scripts

Reference for the systematic diagnostic approach when images don't render on Kindle.
These scripts are session-specific tools — adapt paths and filenames as needed.

## 1. Map XHTML pages to figure captions

Identify which XHTML file contains each image and its figure number:

```python
import re, os
from zipfile import ZipFile

z = ZipFile('Workspace_Transformer_Circuits_2026.epub')
for n in sorted(z.namelist()):
    if not n.endswith('.xhtml') or 'cover' in n: continue
    c = z.read(n).decode()
    # Find figure captions
    for m in re.finditer(r'<p class="figure-caption"[^>]*>(Figure \d+[^<]*)</p>', c):
        caption = re.sub(r'<[^>]+>', '', m.group(1))[:80]
        # Find preceding image
        before = c[:m.start()]
        img_m = re.search(r'<img[^>]*src="[^"]*images/([^"]+)"', before[::-1])
        if img_m:
            print(f"  {os.path.basename(n)}: {caption} → {img_m.group(1)[::-1]}")
z.close()
```

## 2. Check for intra-page duplicate IDs

```python
import re
from zipfile import ZipFile
from collections import Counter

z = ZipFile('Workspace_Transformer_Circuits_2026.epub')
for n in sorted(z.namelist()):
    if not n.endswith('.xhtml') or 'cover' in n: continue
    c = z.read(n).decode()
    ids = re.findall(r'id="([^"]+)"', c)
    for id_, count in Counter(ids).items():
        if count > 1:
            print(f'DUPLICATE "{id_}" in {n} ({count}x)')
z.close()
```

## 3. Check MathML presence on image pages

Critical diagnostic: Kindle may use a different rendering pipeline for pages
with inline `<math>` vs plain XHTML. Check if broken image pages lack MathML:

```python
import re
from zipfile import ZipFile

z = ZipFile('Workspace_Transformer_Circuits_2026.epub')
print("Page | MathML on page? | Has images?")
print("-" * 55)
for n in sorted(z.namelist()):
    if not n.endswith('.xhtml') or 'cover' in n: continue
    c = z.read(n).decode()
    has_math = bool(re.search(r'<math[ >]', c))
    has_img = bool(re.search(r'figure-img', c))
    if has_img:
        print(f"{os.path.basename(n):25s} | {'YES' if has_math else 'NO ':4s} | YES")
z.close()
```

## 4. Compare XHTML structure — working vs broken image pages

```python
import re
from zipfile import ZipFile

z = ZipFile('Workspace_Transformer_Circuits_2026.epub')

def analyze_page(n):
    c = z.read(n).decode()
    lines = c.split('\n')
    print(f"\n{'='*60}")
    print(f"  {n} ({len(lines)} lines, {len(c)} chars)")
    print(f"{'='*60}")
    img_tags = re.findall(r'<img[^>]+/>', c)
    print(f"  Images: {len(img_tags)}")
    for img in img_tags:
        print(f"    {img[:200]}")
    ids = re.findall(r'id="([^"]+)"', c)
    dup_ids = {i for i in ids if ids.count(i) > 1}
    if dup_ids:
        print(f"  Duplicate IDs: {dup_ids}")
    # Check for spans before captions (source of most duplicate IDs)
    spans = re.findall(r'<span id="([^"]+)"/>', c)
    caption_ids = re.findall(r'id="([^"]+)"', c[2000:])  # captions are typically later
    overlap = set(spans) & set(caption_ids)
    if overlap:
        print(f"  Span-caption ID overlap: {overlap}")

analyze_page('OEBPS/xhtml/ch0008.xhtml')   # works (has MathML)
analyze_page('OEBPS/xhtml/ch0038.xhtml')   # broken (no MathML)
analyze_page('OEBPS/xhtml/ch0051.xhtml')   # broken (no MathML)
z.close()
```

## 5. Render test in browser

```bash
# Extract a suspect page and its images for local browser viewing
python3 -c "
from zipfile import ZipFile
import os

z = ZipFile('input.epub')
os.makedirs('/tmp/epub_test/images', exist_ok=True)

# Extract all images
for n in z.namelist():
    if 'images/' in n:
        open(f'/tmp/epub_test/{n}', 'wb').write(z.read(n))

# Extract a specific page (ch0038 = where Figure 47 lives)
c = z.read('OEBPS/xhtml/ch0038.xhtml').decode()
c = c.replace('src=\"../images/', 'src=\"images/')  # fix relative paths
open('/tmp/epub_test/ch0038.html', 'w').write(c)

# Extract CSS
css = z.read('OEBPS/css/style.css')
open('/tmp/epub_test/style.css', 'wb').write(css)

print('Open file:///tmp/epub_test/ch0038.html in browser')
z.close()
"
```

## 6. Verify all images have manifest entries

```python
import re
from zipfile import ZipFile

z = ZipFile('input.epub')
opf = z.read('OEBPS/content.opf').decode()

# Collect image refs from XHTML
image_refs = set()
for n in z.namelist():
    if not n.endswith('.xhtml'): continue
    c = z.read(n).decode()
    for m in re.finditer(r'src="(?:\.\./)?images/([^"]+)"', c):
        image_refs.add(m.group(1))

# Collect manifest entries
manifest = set()
for m in re.finditer(r'href="images/([^"]+)"', opf):
    manifest.add(m.group(1))

missing = image_refs - manifest
if missing:
    print(f"MISSING FROM MANIFEST: {missing}")
else:
    print(f"All {len(image_refs)} images have manifest entries ✓")

# Extra in manifest but not referenced
extra = manifest - image_refs
if extra:
    print(f"UNREFERENCED IN MANIFEST: {extra}")
z.close()
```

## 7. PNG metadata analysis (chunks)

```python
import struct, os

def analyze_png(path):
    with open(path, 'rb') as f:
        sig = f.read(8)
        assert sig == b'\x89PNG\r\n\x1a\n'
        chunks = []
        while True:
            length = struct.unpack('>I', f.read(4))[0]
            ctype = f.read(4).decode()
            data = f.read(length)
            f.read(4)  # CRC
            chunks.append((ctype, length))
            if ctype == 'IEND': break
    return chunks

for fn in sorted(os.listdir('images/')):
    if not fn.endswith('.png'): continue
    ch = analyze_png(f'images/{fn}')
    types = [t for t,l in ch]
    print(f"{fn}: {' '.join(types)} ({len(ch)} chunks)")
```

## 8. Strip optional PNG chunks (sRGB, gAMA, cHRM)

```python
import struct, os, shutil

SRC_DIR = '/opt/data/workspace-figures'
KEEP = {b'IHDR', b'IDAT', b'IEND', b'PLTE', b'tRNS'}

for fn in sorted(os.listdir(SRC_DIR)):
    if not fn.endswith('.png'): continue
    path = os.path.join(SRC_DIR, fn)
    with open(path, 'rb') as f:
        raw = f.read()
    
    # Read all chunks, keep only KEEP
    pos = 8  # skip signature
    output = raw[:pos]
    changed = False
    while pos < len(raw):
        length = struct.unpack('>I', raw[pos:pos+4])[0]
        ctype = raw[pos+4:pos+8]
        chunk_data = raw[pos+8:pos+8+length]
        crc = raw[pos+8+length:pos+12+length]
        if ctype in KEEP:
            output += raw[pos:pos+12+length]
        else:
            changed = True
        pos += 12 + length
    
    if not changed:
        print(f'{fn}: UNCHANGED (already minimal)')
    else:
        with open(path, 'wb') as f:
            f.write(output)
        print(f'{fn}: STRIPPED {len(raw)-len(output)} bytes')
```

## 9. Convert all PNGs to JPEG

```bash
mkdir -p workspace-figures-jpg
for f in workspace-figures/*.png; do
    base=$(basename "$f" .png)
    ffmpeg -y -i "$f" -q:v 95 -frames:v 1 -update 1 "workspace-figures-jpg/${base}.jpg"
done
```
