# Archive.org Search API — Manga Discovery Patterns

Find manga on Archive.org using the advanced search API. These queries work with `curl` or browser — no API key needed.

## Base URL

```
https://archive.org/advancedsearch.php?output=json&rows=50&q=...
```

## Common Search Patterns

### By subject + mediatype

```
q=subject:"Vinland Saga" AND mediatype:texts
```

### By format (MOBI/CBZ/PDF)

```
q=subject:"Vinland Saga" AND format:(MOBI OR PDF OR CBZ)
```

### By publisher (e.g. Kodansha English release)

```
q=publisher:kodansha AND vinland saga AND mediatype:texts
```

### By identifier prefix

Useful when you know the naming convention:
```
q=identifier:vinlandsagabook* AND mediatype:texts
```

## Returned Fields

Use `fl[]` to request specific fields (repeat for multiple):

```
&fl[]=identifier&fl[]=title&fl[]=downloads&fl[]=format&sort[]=downloads+desc
```

| Field | Description |
|-------|-------------|
| `identifier` | Unique item ID (used in download URL) |
| `title` | Display title |
| `downloads` | All-time download count |
| `format` | Array of available formats |
| `creator` | Uploader/author |
| `description` | Item description text |
| `subject` | Tags/subjects |
| `language` | Language code |
| `mediatype` | texts, audio, video, etc. |

## Checking Available Files

```bash
curl -s "https://archive.org/metadata/<identifier>"
```

Look at the `files` array for format indicators:

| Format indicator in metadata | Meaning | Manga quality |
|------------------------------|---------|---------------|
| `Text PDF` | Freely downloadable PDF | ⚠️ **LOW RES — OCR derivative.** Archive.org generates this by running OCR on scans and reducing image resolution. Not suitable for Kindle manga. |
| `Single Page Processed JP2 ZIP` | Original high-res page scans in JPEG2000 | ✅ **BEST quality.** Extract JP2 → convert to JPEG → feed to KCC. Full scan resolution preserved. |
| `EPUB` | Freely downloadable EPUB | ✅ Good if it's a proper image-based EPUB |
| `Comic Book RAR` | CBR format, freely downloadable | ✅ **Native scan format.** Best quality. |
| `Comic Book ZIP` | CBZ format, freely downloadable | ✅ Native scan format. Best quality. |
| `ACS Encrypted PDF` | Library-borrow only (requires Open Library account) | ❌ Cannot download |
| `LCP Encrypted PDF` | Protected, not freely downloadable | ❌ Cannot download |
| `LCP Encrypted EPUB` | Protected, not freely downloadable | ❌ Cannot download |
| `DjVu` | Freely downloadable (scanned) | ✅ Good quality, but needs conversion to JPEG |

**How to tell a Text PDF from a proper scan:** Check file size. A full manga volume (~200 pages) in scan quality is **50-200 MB**. If the PDF is under 30 MB, it's a Text PDF derivative with reduced images. Look for JP2 ZIP, CBR, or CBZ instead.

**How to use JP2 ZIP:**
```bash
# Download the JP2 ZIP
curl -sL -o "file_jp2.zip" "https://archive.org/download/<id>/<name>_jp2.zip"

# Extract JP2 files
unzip file_jp2.zip -d /tmp/pages/

# Convert JP2 to JPEG (pillow handles JP2)
for f in /tmp/pages/*.jp2; do
    python3 -c "from PIL import Image; Image.open('$f').save('${f%.jp2}.jpg')"
done

# Feed directory to KCC
kcc.main(['/tmp/pages/', '-p', 'KPW5', '-m', '-f', 'EPUB', ...])
```

## Download URLs

Once you have the identifier and filename:

```
https://archive.org/download/<identifier>/<filename>
```

The server redirects to a CDN (dn*.ca.archive.org). Use `curl -sL` to follow redirects automatically.

## Common Manga Identifier Patterns

| Pattern | Example | Notes |
|---------|---------|-------|
| `<series>-v-<N>` | `vinland-saga-v-01` | Community scan, often PDF |
| `<series>book<word><year><initials>` | `vinlandsagabooko0000yuki` | Kodansha release, may be encrypted |
| `<series>_<author>` | `the-gods-lie_202605` | Community upload |
| `manga_<title>` | `manga_Magi_no_Okurimono` | Community upload, often CBR |

## Pitfalls

- **Encrypted != downloadable**: Kodansha/Viz releases on Archive.org are often library-borrow-only. Check file list for "ACS Encrypted" or "LCP Encrypted" before attempting download.
- **Partial series**: Most long series (27+ volumes) have only 1-4 volumes freely downloadable. The rest are typically encrypted or missing.
- **Wrong language**: Archive.org MOBI/PDF may be English, Japanese, Spanish, or other languages. Check `language` field.
- **Rate limiting**: The API is generous but avoid hammering it with rapid-fire queries. Add brief pauses between multiple sequential calls.
- **File mismatch**: The identifier found in search may not match what you expect. Always check metadata to confirm the right series/volume.
- **Search results include non-manga**: The same keyword may match novels, video reviews, fan podcasts. Filter by `mediatype:texts` and look for subject tags like "manga" or "comics".

## Full Example: Check Freely Downloadable Volumes

```bash
# 1. Search for Vinland Saga
curl -s "https://archive.org/advancedsearch.php?q=vinland+saga+manga+AND+mediatype:texts&fl[]=identifier&fl[]=title&fl[]=downloads&sort[]=downloads+desc&rows=30&output=json"

# 2. Check a specific item's files
curl -s "https://archive.org/metadata/vinland-saga-v-01" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for f in data.get('files',[]):
    name = f.get('name','')
    fmt = f.get('format','')
    size = f.get('size',0)
    if 'pdf' in name.lower() or 'epub' in name.lower() or 'cbr' in name.lower() or 'cbz' in name.lower():
        encrypted = '🔒' if 'encrypted' in fmt.lower() or 'lc' in fmt.lower() else '✅'
        print(f'{encrypted} {name} | {fmt} | {int(size)//1024//1024} MB')
"

# 3. Download a freely available PDF
curl -sL -o "Vinland_Saga_v01.pdf" "https://archive.org/download/vinland-saga-v-01/VinlandSaga_v01.pdf"
```
