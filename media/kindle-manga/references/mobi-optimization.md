# MOBI File Size Optimization for Send-to-Kindle

Send-to-Kindle from Android has a **200 MB per-file limit**. Manga volumes often exceed this when processed with default KCC settings (`--forcecolor` + full quality).

## Root cause

- `--forcecolor` keeps all pages as color JPEG — adds **3-5× overhead** for black-and-white manga
- Default JPEG quality (85) is overkill for e-ink (no color, lower contrast range)
- KCC does NOT auto-convert to grayscale unless `--forcecolor` is omitted. Without it, KCC's *default* is grayscale — but the `-q` flag keeps JPEG quality high

## Optimization workflow

### 1. Extract source pages

**From PDF (PyMuPDF/fitz, included in KCC deps):**

```python
import fitz
from PIL import Image

doc = fitz.open('/path/to/file.pdf')
for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(dpi=120)  # 120 DPI = good for KPW5
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    gray = img.convert('L')              # GRAYSCALE — the key savings
    gray.thumbnail((1072, 1448), Image.LANCZOS)  # KPW5 resolution cap
    gray.save(f'/tmp/pages/{i+1:04d}.jpg', 'JPEG', quality=70, optimize=True)
```

**From CBR (embedded CFFI unrar):**

```python
from unrar.cffi.rarfile import RarFile
from PIL import Image
from io import BytesIO

rf = RarFile('/path/to/file.cbr')
names = sorted(n for n in rf.namelist() if n.lower().endswith(('.jpg','.jpeg','.png','.gif')))
for i, name in enumerate(names):
    raw = rf.read(name)
    img = Image.open(BytesIO(raw))
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    gray = img.convert('L')
    gray.thumbnail((1072, 1448), Image.LANCZOS)
    gray.save(f'/tmp/pages/{i+1:04d}.jpg', 'JPEG', quality=70, optimize=True)
```

### 2. Feed flat image directory to KCC with --noprocessing

```python
kcc.main([
    '/tmp/pages',           # flat image directory
    '-p', 'KPW5',           # Paperwhite 5 profile
    '-m',                   # manga mode (RTL)
    '-f', 'EPUB',           # intermediate EPUB
    '-u',                   # upscale if needed
    '--noprocessing',       # DON'T re-process (already optimized)
    '-o', '/tmp/',
    '-t', 'Title',
    '-a', 'Author',
])
```

`--noprocessing` is critical: without it KCC re-converts the grayscale JPEGs back through its own pipeline, which re-adds color profiling and degrades compression gains.

### 3. Convert EPUB → MOBI

```bash
python3 /path/to/kindlegen-replacement.py /tmp/output.epub
# → /tmp/output.mobi
```

## Expected savings

| Source | Original (forcecolor) | Optimized | Reduction |
|--------|----------------------|-----------|-----------|
| The Gods Lie (220p PDF) | 107 MB | **12 MB** | ~89% |
| Magi no Okurimono (196p CBR) | 201 MB | **54 MB** | ~73% |
| Vinland Saga Vol 1 (464p PDF) | 475 MB | **137 MB** | ~71% |

All three fit comfortably under the 200 MB Android Send-to-Kindle limit.

## Quality notes

- Grayscale on e-ink is indistinguishable from color-chartreuse-to-gray for manga
- JPEG quality 70 is the sweet spot: no visible artifacts on 300 PPI e-ink, significant size savings
- Images are capped at 1072×1448 = KPW5 native resolution. For KPW6/KS1240/KS1920, adjust resolution
- Double-page spreads are a special case: if the source has true 2-page spreads, split them before optimization or let KCC's `-m` mode handle it
- Some manga have color inserts (first/last pages, chapter openings). These are rare enough that greyscale conversion is a net win
