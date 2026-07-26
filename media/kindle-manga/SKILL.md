---
name: kindle-manga
description: "Prepare and transfer manga to Kindle — quality-gated conversion with EPUB generation

Load this skill when putting manga or comics on a Kindle, converting CBR/CBZ/PDF to Kindle format, or using KCC (Kindle Comic Converter) and Calibre for MOBI/AZW3 conversion."

summary: "End-to-end manga pipeline: source acquisition (Archive.org JP2/CBR, Nyaa torrents, MangaDex API), quality gate (resolution + contrast checks), grayscale EPUB generation with PW11-native resize, and Drive delivery."
version: 2.0.0
author: Hermes
license: MIT
tags: [kindle, manga, comics, kcc, calibre, mobi, ereader, usb-transfer]
type: Media
timestamp: 2026-06-28T05:11:55Z
---

# Kindle Manga Transfer

Prepare manga files for Kindle e-ink devices. Covers the full workflow: finding sources (Archive.org search API, Nyaa.si BitTorrent, pre-converted MOBI collections), inspecting MOBI quality (KCC metadata, image resolution), converting CBR/CBZ/PDF → EPUB → MOBI via KCC, and delivery via USB direct copy or Google Drive.

## When to load

- User asks to put manga or comics on their Kindle
- User asks about converting CBZ/CBR to Kindle format
- User asks about KCC (Kindle Comic Converter), Calibre, or MOBI/AZW3 formats
- User wants to send manga to Kindle email but files are too large
- Any "how do I read manga on Kindle" question
- User asks to find, download, or search for manga files from Archive.org or Nyaa.si
- User asks for the latest weekly chapter of a manga (One Piece, Jujutsu Kaisen, etc.) on Kindle
- User wants to send a single manga chapter to their Kindle via email

## Format decision guide

| Transfer method | Required format | Why |
|----------------|----------------|-----|
| **USB direct copy** (drag to Documents folder) | **MOBI** or AZW | Kindle natively reads MOBI from USB. EPUB placed directly on Kindle by USB is invisible |
| **USB via Calibre** | EPUB or MOBI | Calibre converts EPUB→MOBI on send. Accepts any input format |
| **Send-to-Kindle email/cloud** | **Fixed-layout EPUB** (recommended) | Amazon accepts EPUB since 2022. Converts to KFX internally. **Use fixed-layout EPUB** with `rendition:layout=pre-paginated` for edge-to-edge display. EPUB without fixed-layout renders with margins on Kindle. |
| **Send-to-Kindle Android app** | **Fixed-layout EPUB** | Works with files up to 200 MB. Fixed-layout removes margins. |

**Critical: EPUB vs MOBI margin issue and fixed-layout metadata**

Kindle renders EPUB using a third-party renderer (RMSDK) that adds **automatic margins** around content. A reflowable EPUB with images directly linked in the spine will NOT fill the screen — it will show with blank borders.

**Solutions that work (tested on Paperwhite 11th Gen):**

| Solution | How | File size | Works with |
|----------|-----|-----------|------------|
| ✅ **Fixed-layout EPUB (CSS approach — recommended)** | Each image in its own XHTML page with `margin:0` CSS + `rendition:layout=pre-paginated`, `fixed-layout` and `zero-margin` in OPF. Uses `src=\"../Images/\"` for correct path resolution. Tested on PW11. Use `scripts/fixed-epub-builder.py`. | Same as source images | Send-to-Kindle (email + app). **Approach with proven results on Paperwhite 11.** |
| ❌ ~~Fixed-layout EPUB (SVG approach)~~ | ~~Removed — caused camera icons due to missing `../` prefix in image paths and missing `fixed-layout`/`zero-margin` metadata~~ | — | — |
| ✅ **MOBI (kindlegen replacement)** | Convert EPUB → MOBI via `scripts/kindlegen-replacement.py`. Kindle reads MOBI natively = no margins. | Similar to source images | **USB only** (Amazon deprecated MOBI for email since 2022) |

**Recommendation for Send-to-Kindle email (tested on Paperwhite 11th Gen):**

1. **Best first attempt:** CSS fixed-layout EPUB (`scripts/fixed-epub-builder.py`).
   - Each page in its own XHTML with `margin:0` CSS
   - Image paths use `src="../Images/"` for correct resolution
   - OPF includes: `rendition:layout=pre-paginated`, `fixed-layout=true`, `zero-margin=true`
   - Setup: upscale images to device resolution → run `fixed-epub-builder.py`

2. **Fallback:** Simple reflowable EPUB with images directly in spine and properly upscaled to device resolution. Amazon converts EPUB→KFX server-side, bypassing RMSDK margins. Safe fallback if CSS approach fails.

3. **Last resort:** USB delivery with MOBI format (via `scripts/kindlegen-replacement.py`). Zero margin issues since Kindle reads MOBI natively.

**Rule:** For USB, use MOBI. For email, prefer fixed-layout CSS EPUB (`fixed-epub-builder.py`) as first try.

## Kindle file size limits

| Model | Per-file limit | Notes |
|-------|---------------|-------|
| Kindle 1-4 | ~200 MB | Older models may struggle with large files |
| Kindle Paperwhite / Voyage / Oasis | ~1-2 GB | Modern models handle 200-500 MB easily |
| Kindle Scribe | ~2 GB | Largest capacity |

A typical manga volume in MOBI is **60-200 MB**. Vinland Saga volume 1 (463 pages) is ~475 MB. This fits on modern Kindles via USB but may be too large for older models.

## Single chapter workflow

For **individual weekly chapters** (not full volumes), the standard torrent + KCC pipeline is overkill. Use aggregator sites that host individual chapter scans directly:

1. Find the chapter on a manga aggregator (search patterns below)
2. Navigate the reader page in the browser; scroll down to trigger lazy image loads
3. Extract image URLs via `browser_get_images` or the Performance API (`performance.getEntriesByType('resource')`)
4. Download each page image from the CDN
5. Build a simple image-based EPUB using Python's ZipFile (see "Full workflow" section for the pattern)
6. Deliver via Gmail API attachment or Google Drive

**Aggregator sources for single chapters:**

| Source | URL pattern | Notes |
|--------|------------|-------|
| readonepiece.com | `ww{N}.readonepiece.com/chapter/one-piece-chapter-{N}/` | **Best One Piece source.** CDN at `cdn.readonepiece.com`. Domain rotates ww5-ww20. ⚠️ CDN requires `Referer: https://{domain}.readonepiece.com/` header — without it, returns 403 and a 4.8 KB HTML placeholder instead of the image. Images are PNG or JPEG depending on release. Extract URLs from raw HTML with a **generic regex** that catches both old patterns (`_NNN.png`) and new UUID-based patterns: `r"(https://cdn\\.readonepiece\\.com/file/[^\"' ]+?\\.(?:png|jpe?g))"`. Sort by the last numeric segment before the extension for correct page ordering — new format uses `/{page}.jpeg` at end of URL, old format uses `_NNN.png`. |
| MangaPlus (reference only) | `mangaplus.shueisha.co.jp/viewer/{chapter_id}` | Official. DRM blob URLs — browser + Performance API needed. Oracle Cloud IP blocked from API. |
| MangaPill | `mangapill.com/chapters/{manga_id}-{ch_id}/{slug}` | Good for series not on MangaDex. CDN: `cdn.readdetectiveconan.com`. Requires `User-Agent + Referer` headers. Image URLs embedded as `data-src` in raw HTML (no browser/JS needed — curl + grep works). URL pattern includes per-chapter UUID — extract from HTML, don't guess. See `references/mangapill-source.md`. |
| daemonsoftheshadowreal.com (qubn.us) | `daemonsoftheshadowreal.com/manga/daemons-of-the-shadow-realm-chapter-{N}/` | Historical source — CDN migrated. See `references/qubn-us-source.md` for archive. |

**One Piece schedule (confirmed):** Chapters on readonepiece.com arrive **Tuesdays** (~2 days after official Sunday WSJ). Break every 3-4 chapters.

**Cron job for automated One Piece delivery:** `one_piece_kindle_cron.py` (no_agent) — runs Sat 12:00 BRT, checks readonepiece.com, downloads→processes→sends EPUB to Kindle via Gmail. Silent if nothing new. Stored at `~/./scripts/one_piece_kindle_cron.py`, job_id=`388e767fcc7c`. **Cover fix applied 2026-06-28:** the script now includes `<meta name="cover" content="cover-image"/>` in OPF metadata and `properties="cover-image"` on the first image manifest item. URL regex updated to handle both old (`_NNN.png`) and new (`/{page}.jpeg`) CDN patterns.

**Monthly series cron pattern (e.g. Daemons of the Shadow Realm):**

For monthly manga (Yomi no Tsugai, published in Monthly Shonen Gangan on the 12th):

- **Release schedule:** ~1 chapter/month, raw in Japan on the 12th, scanlation appears within ~5–15 days
- **Cron schedule:** `0 11 25 * *` (25th of each month at 11:00 UTC / 08:00 BRT) — allows time for Japan raw + scanlation window + extra buffer for user preference
- **Cron job:** `no_agent=True` with a self-contained Python script (e.g. `daemons_kindle_cron.py`). The script handles discovery, download, processing, and delivery with zero LLM token cost. Job ID: `1ded3dfe4064`.
- **Source:** `mangapill.com` → CDN `cdn.readdetectiveconan.com` (see `references/mangapill-source.md`)
- **Workflow:**
  1. Fetch series page HTML with curl (`-H "User-Agent: ..."`) and grep for chapter links — no browser needed
  2. For new chapters, fetch chapter page HTML and extract `data-src` image URLs via regex
  3. Download each image from CDN with `User-Agent` + `Referer: https://mangapill.com/` headers
  4. Convert to grayscale + resize to Kindle (PW11: 1236×1648) → JPEG Q75
  5. Build fixed-layout EPUB with cover metadata (`<meta name="cover" content="cover-image"/>` + `properties="cover-image"` on first image item)
  6. Send to Kindle via Gmail (≤25 MB) or upload to Drive (>25 MB)
- **Scanlation vs official numbering:** MangaPill uses official chapter numbers, but always check the site's chapter list as the source of truth.
- **Gmail send:** Use `scripts/send-kindle-gmail.py` to deliver EPUB files to Kindle via Gmail API (supports attachments, unlike `gws` CLI's `gmail send` which only sends text).
- **Scanlation vs official numbering:** MangaPill uses official chapter numbers, but always check the site's chapter list as the source of truth.\n- **Gmail send:** Use `scripts/send-kindle-gmail.py` to deliver EPUB files to Kindle via Gmail API (supports attachments, unlike `gws` CLI's `gmail send` which only sends text).

**Probing a candidate URL:**
```bash
curl -sL -o /dev/null -w '%{http_code}' -H "User-Agent: Mozilla/5.0" "$url"
```

**Verifying a chapter is real:**
- Check the cover/title page via `vision_analyze` — look for Oda's official title treatment
- Cross-reference the chapter title with official sources (MangaPlus, MangaDex external URLs)
- A typical One Piece chapter has 15-19 pages. Fewer than 12 may indicate fan-made.

## Sources

### Nyaa.si (BitTorrent — manga scanlations)

[Nyaa.si](https://nyaa.si) is the primary BitTorrent tracker for anime and manga. Has full multi-volume sets in CBZ format.

Search via curl with browser User-Agent:

```bash
curl -s -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  "https://nyaa.si/?q=Vinland+Saga+manga&s=seeders&o=desc" \
  -o /tmp/nyaa.html
grep -oP 'title="[^"]*"' /tmp/nyaa.html | head -20
```

Extract magnet links and torrent download URLs:

```bash
grep -oP 'magnet:\?[^"]*' /tmp/nyaa.html | head -3
grep -oP 'href="/download/[^"]*"' /tmp/nyaa.html | head -3
```

**Torrent → CBZ → MOBI workflow:**
1. Parse torrent with `torrent_parser` (pip: `torrent-parser`) to list files
2. Download via a BT client (aria2c, transmission-cli, rtorrent)
3. Convert CBZ → MOBI via KCC

If no BT client is available on the host, share the magnet/torrent link with the user.

### MangaDex (API — aggregator)

[MangaDex](https://mangadex.org) is the largest manga aggregator. Use
the API via `curl -sv` (Python urllib/requests get blocked with HTTP 400).

Search:
```bash
curl -sv "https://api.mangadex.org/manga?title=Gin+no+Saji&limit=5" 2>&1
```

List English chapters:
```bash
UUID="<manga-id>"
curl -sv "https://api.mangadex.org/manga/$UUID/feed?limit=200&\
translatedLanguage%5B%5D=en&order%5Bchapter%5D=asc" 2>&1
```

Get at-home server data and download pages is documented in
`references/mangadex-download.md` — critical reading before attempting.

**Anti-bot quirk:** `curl -sL` triggers HTML wall. Use `-sv` instead.
Omitting `User-Agent` header (let curl default) also matters — sending
a browser-like UA triggers the block.

### Archive.org

Archive.org hosts many manga series already converted to MOBI by the community.

Search API:

```bash
QUERY="vinland saga manga"
curl -s "https://archive.org/advancedsearch.php?q=${QUERY// /+}+AND+mediatype:texts&fl[]=identifier&fl[]=title&fl[]=downloads&sort[]=downloads+desc&rows=30&output=json"
```

Check file availability for a specific item:

```bash
curl -s "https://archive.org/metadata/<identifier>" | python3 -m json.tool
```

**Download free vs borrow-only tells:**
- "Text PDF" → freely downloadable PDF
- "EPUB" (no ACS/LCP prefix) → freely downloadable EPUB
- "ACS Encrypted PDF" / "LCP Encrypted EPUB" → library-borrow only
- If download returns "401 Authorization Required" → not freely downloadable

**Known Archive.org identifiers for Vinland Saga:**
- `vinland-saga-v-01` — freely downloadable Vol 1 PDF
- `vinlandsagabook*0000yuki` — Kodansha English volumes (most are borrow-only encrypted)
- `the-gods-lie_202605` — The Gods Lie (Hiromu Arakawa). ✅ Has JP2 ZIP (70 MB, high-res). ❌ Text PDF (18.5 MB) is low-res derivative — use JP2 ZIP instead.
- `manga_Magi_no_Okurimono` — Magi no Okurimono (Kaiu Shirai). CBR format, 87 MB — good quality.

**Known Archive.org identifiers for Monster (Naoki Urasawa):**
- `manga_Monster` — Complete 18-volume set in [MS] scanlation format.
  Volume pattern: `Monster - cXXX-XXX (vNN) [MS].epub`
  ⚠️ [MS] scanlator uses text-as-separate-image-layer (see Pitfalls).
  Alternative: `monster-the-perfectedition` (incomplete, different format).
  Individual volume metadata entries also exist but are lower quality.

**Known Archive.org identifiers for Berserk (Kentaro Miura):**
- `manga_Berserk` — Multiple scanlation groups in one collection.
  - **danke-Empire HD** (quality tier): `!Berserk [danke-Empire]{HD}/Berserk vNN ... .epub`
    180–260 MB each, 1500+ px wide. Best source but needs Drive delivery.
  - **Hawks** (standard tier): `Berserk - XXX-XXX (vNN) [Hawks].epub`
    20–60 MB, 460–776 px wide. Check for `[LQ]` tag. Most email-friendly.
  - **Evil_Genius** (magazine tier): `Berserk - cXXX-cXXX (vNN) (mag) [Evil_Genius].epub`
    Later chapters (v25+), 87–145 MB.
- `berserk-volume-41_20231228` — All 41 volumes in one item (PDF format).

See `references/archive-org-search-api.md` for full search pattern catalog.

## Conversion pipeline: source → EPUB → MOBI

### Step 1: Acquire source files

- **Archive.org PDF/CBR**: Download via `curl -sL -o output.ext "https://archive.org/download/<id>/<filename>"`
- **Archive.org EPUB**: Same URL pattern, look for unencrypted EPUB in file listing
- **CBR (Comic Book RAR)**: Extract via `unrar.cffi.rarfile.RarFile` (pure Python, no system `unrar` needed)
- **CBZ (Comic Book ZIP)**: Extract via `zipfile.ZipFile`

### Step 2: Install KCC

```bash
uv pip install git+https://github.com/ciromattia/kcc.git
```

The PyPI `kcc` package is unrelated (version 0.0.9). The real KCC is only on GitHub.

### Step 3: Convert to EPUB (KCC headless)

KCC requires 7z binary and Qt (GUI library). Workarounds:

**A. Mock Qt to bypass GUI import:**

```python
import sys
sys.modules['PySide6'] = type(sys)('PySide6')
sys.modules['PySide6.QtGui'] = type(sys)('QtGui')
sys.modules['PySide6.QtCore'] = type(sys)('QtCore')
from kindlecomicconverter import comic2ebook as kcc
```

**B. Provide a 7z shim:**

Create a Python wrapper using `zipfile.ZipFile` (see `references/7z-shim-python.md`).

```bash
ln -sf /path/to/7z-shim.py /tmp/bin/7z
export PATH="/tmp/bin:$PATH"
```

**C. Convert with optimal settings:**

```python
kcc.main([
    '/path/to/source',       # PDF, CBZ, or image directory
    '-p', 'KPW5',            # Kindle Paperwhite 5 = 11th Gen (1236x1648)
    '-m',                    # Manga mode (RTL)
    '-f', 'EPUB',            # Output EPUB (kindlegen not needed)
    '-u',                    # Upscale smaller images
    '-q',                    # High quality
    '--forcecolor',          # Keep color
    '-o', '/output/dir',
    '-t', 'Title',
    '-a', 'Author',
])
```

**D. Handle nested archives:**

CBR/CBZ with subdirectories cause KCC error "No images detected, nested archives not supported." Extract flat first:

```python
from unrar.cffi.rarfile import RarFile
rf = RarFile('input.cbr')
names = sorted(n for n in rf.namelist() if n.lower().endswith(('.jpg','.jpeg','.png','.gif')))
for i, name in enumerate(names):
    with open(f'/tmp/images/{i+1:04d}.jpg', 'wb') as f:
        f.write(rf.read(name))
```

Then feed the `/tmp/images/` directory to KCC instead of the archive.

### Step 4: Convert EPUB → MOBI (kindlegen replacement)

KCC uses `kindlegen` (Amazon's tool, x86-only) for MOBI output. On non-x86 systems, use the script at `scripts/kindlegen-replacement.py` — a Python MOBI writer that creates valid PDB/MOBI files directly from KCC-produced EPUBs.

```bash
# After running KCC with -f EPUB:
python3 scripts/kindlegen-replacement.py /path/to/output.epub
# Creates output.mobi in same directory
```

The replacement creates a PDB (Palm Database) file with:
- MOBI header with EXTH metadata
- JPEG page images as sequential PalmDB records
- Proper BOOK/MOBI type identifiers

**Why this is needed for USB:** Kindle via USB requires MOBI or AZW format. EPUB copied directly to the Kindle via USB is invisible to the device. The Kindle's file system only indexes MOBI/AZW files in the Documents folder.

### Step 5: Upload and deliver

- Use Google Drive upload + share for delivery
- Files >200MB cannot be emailed (Gmail 25MB limit + Kindle 50MB limit)
- Share the folder with `--type anyone --role reader`
- For EPUBs under 25 MB, send directly to Kindle via Gmail API (see `references/gmail-kindle-delivery.md`)

## Batch processing strategy (large volume sets)

When processing many volumes (e.g. Monster 18 vols, Berserk 38 vols), **never use `delegate_task`** — it has a hard 600s timeout that kills mid-batch and leaves volumes unprocessed. Instead, use `terminal(background=true, notify_on_complete=true)` with a shell for loop:

```python
# Example: process volumes 13-18 in one background terminal
terminal(
    command="cd /opt/data && for v in 13 14 15 16 17 18; do "
            "echo '=== Monster Vol.$v ===' && "
            "python3 scripts/kindle_volume_processor.py MONSTER $v && "
            "echo 'Done Vol.$v'; done",
    background=True,
    notify_on_complete=True,
    timeout=14400  # 4h for 6 volumes
)
```

### Rules for batch dispatch

| Factor | Recommendation |
|--------|----------------|
| **Batch size** | 6 volumes max per terminal call (avoids 4h timeout wall) |
| **Timeout** | 8 min/vol × batch_size + 50% buffer |
| **Notify** | Always set `notify_on_complete=True` |
| **Parallel** | Dispatch multiple series simultaneously (e.g. Monster loop + Berserk loop in parallel) |
| **Recovery** | If a batch dies mid-way, check Drive for the last volume uploaded, then dispatch from the next missing volume. Before dispatching a new batch, Drive-search all missing volumes — an older concurrently-running batch may have already finished the work (notifications can arrive after you've already dispatched a new loop). Check for duplicate filenames in Drive and kill redundant new batches with `process(action='kill')`. |
| **Source** | Each `kindle_volume_processor.py` call reads Archive.org metadata to find the correct CBZ source |

### Sleep-cycle monitoring pattern

For very long processing runs (3h+ for Berserk 38 vols), set up a periodic watch that wakes you every N minutes to check progress:

```python
# Start a 5-minute timer
terminal(command="sleep 300", background=True, notify_on_complete=True)
# On notification:
#   1. process(action='list') — check running background processes
#   2. google_api.py drive search "<Series>" — verify new volumes in Drive
#   3. Start another sleep 300 → repeat
```

This is preferred over an automated Drive-checking monitor because it keeps the agent loop in the decision path.

**⚠️ Output buffering pitfall:** Background terminal processes (`background=true`) buffer stdout when not connected to a TTY. The `output_preview` in `process(action='poll')` often shows nothing (line count 0) even after 5+ minutes of processing — Python's print() doesn't flush in a pipe until the buffer fills or the script ends. **Never trust a blank `output_preview`.** The reliable check is to query Drive directly for newly uploaded files:

```bash
python3 /opt/data/skills/.../google_api.py drive search "Berserk_Vol16_Q85"
```

If a volume is in Drive, the background process already finished it regardless of what `output_preview` shows.

**Detecting redundant batches — before dispatching a new loop, check Drive first:**

When an old batch notification arrives late (after you've already dispatched a new overlapping batch), the new batch creates redundant uploads. Detect this by counting files per volume BEFORE assuming the new batch is needed:

```bash
# Check for duplicates across the range the new batch would cover
for v in 13 14 15 16 17 18; do
  result=$(/opt/data/venvs/google/bin/python3 \
    /opt/data/skills/productivity/google-workspace/scripts/google_api.py \
    drive search "Monster_Vol$(printf '%02d' $v)_Q85")
  count=$(echo "$result" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)
  echo "Monster v$(printf '%02d' $v): $count file(s)"
done
```

If any volumes show count > 1 (duplicates from the old batch) AND some show count ≥ 1, the old batch already delivered and the new loop is redundant. Kill it immediately:

```bash
process(action='kill', session_id='proc_...')
```

The reliable progress indicator is the Drive file count, NOT `output_preview` from `process(action='poll')` — background terminal processes buffer stdout and often show blank preview even after 5+ minutes of processing (see output buffering pitfall below).

### Post-processing: Drive folder organization and deduplication

After all volumes are processed and uploaded to Drive, they live at **My Drive root** (the `kindle_volume_processor.py` uploads without a `--parent` flag). Before declaring done:

1. **Verify folder contents** — use the Drive API to list files in the target folder:
   ```bash
   python3 -c "
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   creds = Credentials.from_authorized_user_file('/opt/data/google_token.json', ['https://www.googleapis.com/auth/drive'])
   service = build('drive', 'v3', credentials=creds)
   results = service.files().list(
       q=\"'<FOLDER_ID>' in parents and trashed=false\",
       fields='files(id, name)',
       pageSize=50).execute()
   for f in sorted(results.get('files',[]), key=lambda x: x['name']):
       print(f['name'])
   "
   ```
   The `'<FOLDER_ID>' in parents` query is the **only reliable way** to check folder membership. The `google_api.py drive search` command uses `fullText contains` and does NOT return the `parents` field, so you can't determine folder membership from search results (the `f.get('parents', [])` will always be `[]`).

2. **Move root files into the correct folder** — use `scripts/drive-move-to-folder.py` (added to this skill):
   ```bash
   /opt/data/venvs/google/bin/python3 \
     /opt/data/skills/media/kindle-manga/scripts/drive-move-to-folder.py \
     "<FOLDER_ID>" "Monster_Vol01_Q85"
   ```
   Loops through all Q85 volumes. Moves matching files to the target folder, removing from root.

3. **Deduplicate** — check for duplicate filenames in the target folder listing. Two sources of duplicates:
   - **Overlapping batch loops**: if an old batch notification arrives late after you've dispatched a new loop, both produce the same `_Q85` files. Kill the redundant loop immediately.
   - **Reprocessing old volumes**: when re-processing with Q85 quality (e.g. replacing Q20 → Q85), new files with the same name as old ones appear. The script deletes extra copies automatically.

4. **Cleanup old non-Q85 versions** — files like `Monster Vol.16.epub` (no `_Q85` suffix, old source) remain at root. Delete them:
   ```bash
   /opt/data/venvs/google/bin/python3 \
     /opt/data/skills/productivity/google-workspace/scripts/google_api.py \
     drive delete "<FILE_ID>"
   ```

**Example: Monster 18-volume cleanup**
```bash
# Move all Q85 volumes to Monster folder
for v in $(seq 1 18); do
  /opt/data/venvs/google/bin/python3 \
    /opt/data/skills/media/kindle-manga/scripts/drive-move-to-folder.py \
    "1lGbMpWC7PvP7FOQtgqV8c4nkgjDuNOrD" \
    "Monster_Vol$(printf '%02d' $v)_Q85"
done
# Delete old non-Q85 root files
for id in 16SYT2wRHRV4Zer2gjBSfEp9n0kLbJw86 1uZOw6xQtjSLdxClVLTz5Y2I88241caD3 ...; do
  GAPI drive delete "$id"
done
```

### Drive status check

To verify what volumes are in Drive after processing:

```bash
python3 /opt/data/venvs/google/bin/python3 \
  /opt/data/skills/productivity/google-workspace/scripts/google_api.py \
  drive search "Monster_Vol13_Q85"  # exact name search
  # Returns [] if missing, [file] if present

python3 /opt/data/venvs/google/bin/python3 \
  /opt/data/skills/productivity/google-workspace/scripts/google_api.py \
  drive search "Monster"  # broader search, returns Name + ID + timestamp
```

Loop through missing volumes to detect where a batch died. Timestamps help distinguish old vs reprocessed copies.

## File size optimization for Send-to-Kindle

Send-to-Kindle from Android has a **200 MB per-file limit**. Default KCC conversion with `--forcecolor` produces files well over this for most manga volumes.

**Strategy:** pre-convert pages to grayscale at KPW5 resolution before building EPUB, removing ~70-90% of file size with no visible quality loss on e-ink.

### Grayscale + resize + JPEG85 workflow (recommended)

**Before starting, ask the user which Kindle model they have.** This determines the target resolution:

| Kindle Model | Generation | Resolution | Profile |
|-------------|------------|------------|---------|
| Paperwhite 5 (2021) / 11th Gen | KPW5 | **1236×1648** | `KPW5` |
| Paperwhite 4 (2018) / 10th Gen | KPW4 | 1072×1448 | `KPW4` |
| Paperwhite 6 (2024) / 12th Gen | KPW6 | 1236×1648 | `KPW6` |
| Kindle Scribe (2022) | KS | 1860×2480 | `Scribe` |
| Unknown/default | — | **1236×1648** | `KPW5` |

For ANY source (PDF, CBR, CBZ, JP2 ZIP):

```python
from PIL import Image, ImageOps

# Determine target resolution based on user's Kindle model
# Default to PW5/PW11 (1236×1648) if unsure
TARGET_W, TARGET_H = 1236, 1648

img = Image.open(source_path)

# Convert to RGB first if needed
if img.mode not in ('RGB', 'L'):
    img = img.convert('RGB')

# GRAYSCALE — the key savings for manga on e-ink (3-5× smaller)
gray = img.convert('L')

# CONTRAST CHECK — fixes washed-out scans before resize
hist = gray.histogram()
dark_pct = sum(hist[:64]) / sum(hist) * 100
if dark_pct < 5:
    gray = ImageOps.autocontrast(gray, cutoff=1)

# ⚠️ CRITICAL: thumbnail() only DOWNSCALES. For source images smaller
# than the target (common with aggregator scans ~784×1145), choose
# between two approaches based on user preference:
#
# Option A (center-crop, fills screen, may cut ~5% of edges):
#   resize() + center-crop. Use when user wants edge-to-edge.
#
# Option B (no-crop, white margins, preserves ALL content):
#   resize to fit height + paste onto white canvas. Margins ~4% on sides.
#   Confirmed as acceptable by user Gustavo Mello ("Agora sim!").
#
# Always ask the user if they prefer full-screen or preserved content.
w, h = gray.size
src_ratio = w / h
target_ratio = TARGET_W / TARGET_H

if src_ratio > target_ratio:
    # wider: resize to match height, crop sides
    new_h = TARGET_H
    new_w = int(w * TARGET_H / h)
else:
    # taller: resize to match width, crop top/bottom
    new_w = TARGET_W
    new_h = int(h * TARGET_W / w)

resized = gray.resize((new_w, new_h), Image.LANCZOS)
left = (new_w - TARGET_W) // 2
top = (new_h - TARGET_H) // 2
final = resized.crop((left, top, left + TARGET_W, top + TARGET_H))

# Save as JPEG quality 85 — preserves gray tones for e-ink
final.save(output_path, 'JPEG', quality=85, optimize=True)

Then build the EPUB using `scripts/fixed-epub-builder.py`

### Source selection: avoid Text PDF

Archive.org has two file types for manga:

| Format | When to use | Why |
|--------|-------------|-----|
| **CBR / CBZ** | ✅ Always prefer | Native scan format, full resolution |
| **JP2 ZIP** (Single Page Processed JP2 ZIP) | ✅ Good alternative | Original high-res scans in JPEG2000 — convert JP2→JPEG with Pillow |
| **Text PDF** | ❌ **Avoid** | OCR derivative with reduced images (~72 DPI). <30 MB for a full volume = low-res. Causes "reduced pages" on Kindle |
| **Large PDF** (>100 MB) | ✅ OK | Likely proper scan PDF, usable as source |

**Rule:** If the PDF is under 30 MB for a full volume (~200 pages), it's a Text PDF — download the JP2 ZIP or CBR instead.

### Full workflow: JP2 or CBR → grayscale JPEGs → EPUB

```python
import os
from PIL import Image, ImageOps
from zipfile import ZipFile, ZIP_STORED

# 1. Download JP2 ZIP or CBR from Archive.org
# curl -sL -o source_jp2.zip "https://archive.org/download/<id>/<name>_jp2.zip"
# unzip source_jp2.zip -d pages_raw/

# Or from CBR (embedded unrar library):
# from unrar.cffi.rarfile import RarFile
# rf = RarFile('file.cbr')
# for i, name in enumerate(sorted(n for n in rf.namelist() if n.lower().endswith(('.jpg','.jpeg','.png')))):
#     with open(f'pages_raw/{i+1:04d}.jpg', 'wb') as f: f.write(rf.read(name))

TARGET_W, TARGET_H = 1236, 1648  # PW5/PW11 default
TITLE = "Manga Title"
AUTHOR = "Author Name"

SRC = "pages_raw/"
DST = "pages_opt/"
os.makedirs(DST, exist_ok=True)

files = sorted(os.listdir(SRC))
for i, fname in enumerate(files):
    if not fname.lower().endswith(('.jp2','.jpg','.jpeg','.png')):
        continue
    img = Image.open(os.path.join(SRC, fname))
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    gray = img.convert('L')
    # Contrast check
    hist = gray.histogram()
    if sum(hist[:64]) / sum(hist) * 100 < 5:
        gray = ImageOps.autocontrast(gray, cutoff=1)
    # ⚠️ Two approaches for smaller-than-target images:
    # A (center-crop, fills screen): resize() + center-crop (code below)
    # B (no-crop, preserves content): fit-height + paste on white canvas
    #   ratio = TARGET_H / h
    #   resized = gray.resize((int(w * ratio), TARGET_H), Image.LANCZOS)
    #   canvas = Image.new('L', (TARGET_W, TARGET_H), 255)  # white bg
    #   canvas.paste(resized, ((TARGET_W - resized.width) // 2, 0))
    #   final = canvas
    # Ask user preference before choosing.
    w, h = gray.size
    src_r = w / h
    tgt_r = TARGET_W / TARGET_H
    if src_r > tgt_r:
        new_h = TARGET_H
        new_w = int(w * TARGET_H / h)
    else:
        new_w = TARGET_W
        new_h = int(h * TARGET_W / w)
    resized = gray.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - TARGET_W) // 2
    top = (new_h - TARGET_H) // 2
    final = resized.crop((left, top, left + TARGET_W, top + TARGET_H))
    final.save(f'{DST}/{i+1:04d}.jpg', 'JPEG', quality=85, optimize=True)

# 3. Build fixed-layout EPUB (use `scripts/fixed-epub-builder.py` for production).
# Reflowable EPUBs show with margins on Kindle due to RMSDK.
# For the OPF, at minimum use:
#   <meta property="rendition:layout">pre-paginated</meta>
# For a quick script, at minimum use rendition:layout=pre-paginated and
# XHTML wrappers with margin:0 CSS per fixed-epub-builder.py.
OUTPUT = f'{TITLE}.epub'
with ZipFile(OUTPUT, 'w', ZIP_STORED) as zf:
    zf.writestr('mimetype', 'application/epub+zip', compress_type=ZIP_STORED)
    zf.writestr('META-INF/container.xml',
        '<?xml version="1.0"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        '  </rootfiles>\n'
        '</container>')

    manifest, spine = [], []
    jpgs = sorted([f for f in os.listdir(DST) if f.endswith('.jpg')])
    for i, fname in enumerate(jpgs):
        mid = f'img{i:04d}'
        with open(os.path.join(DST, fname), 'rb') as f:
            zf.writestr(f'OEBPS/Images/{fname}', f.read())
        manifest.append(f'<item id="{mid}" href="Images/{fname}" media-type="image/jpeg"/>')
        spine.append(f'<itemref idref="{mid}"/>')

    opf = (
        '<?xml version="1.0"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">\n'
        '  <metadata>\n'
        f'    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">{AUTHOR}</dc:creator>\n'
        '    <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>\n'
        '  </metadata>\n'
        '  <manifest>\n    ' + '\n    '.join(manifest) + '\n'
        '  </manifest>\n'
        '  <spine toc="ncx" page-progression-direction="rtl">\n    ' + '\n    '.join(spine) + '\n'
        '  </spine>\n'
        '</package>'
    )
    zf.writestr('OEBPS/content.opf', opf)

# 4. Upload to Drive and share
# Use GAPI drive upload or share folder
```

- **RTL ignored if `page-progression-direction` misspelled**: The OPF spine attribute MUST be `page-progression-direction` (with hyphens between all three words). Common misspellings like `pageprogression-direction` (missing first hyphen) or `page-progression-direction` (correct) vs `pageprogression-direction` cause Kindle to silently ignore it, defaulting to LTR reading. The correct syntax is `<spine page-progression-direction="rtl">`. Always open the generated EPUB and `grep 'spine' OEBPS/content.opf` to verify.

### Typical savings (with JPEG85 + grayscale + autocontrast)

| Source | Original (forcecolor) | Grayscale optimized | Reduction |
|--------|----------------------|---------------------|-----------|
| The Gods Lie (220p JP2 → EPUB) | 108 MB | **83 MB** | ~23% |
| Magi no Okurimono (196p CBR) | 201 MB | **~95 MB** | ~53% |
| Vinland Saga Vol 1 (464p PDF) | 475 MB | **~200 MB** | ~58% |

All fit on modern Kindles. For the 200 MB Android Send-to-Kindle limit, use quality=70 (adds ~30% more compression) versus 85.

See `references/mobi-optimization.md` for more details and the MOBI conversion variant.

## ⚠️ Quality gate: image resolution check (MANDATORY)

**Always run this check after downloading any source and BEFORE converting.** Prevents shipping a low-res file with tiny pages on Kindle.

### Thresholds

Check the **smallest dimension** (width for portrait manga pages) of a sample image:

| Image width | Verdict | Action |
|-------------|---------|--------|
| ≥ 1000 px | ✅ **Good** | Proceed with conversion |
| 700–999 px | ⚠️ **Acceptable** | OK but not ideal. Warn user. |
| < 700 px | ❌ **BLOCKED** | **STOP.** Find a better source (JP2 ZIP, CBR, or larger PDF) |

**File size heuristic:** If a full volume PDF is <30 MB, flag it as likely Text PDF immediately.

### Contrast check (prevents washed-out "gray" pages)

Before converting, check the image histogram to catch low-contrast sources:

```python
from PIL import Image, ImageOps

def check_contrast(path, apply_fix=True):
    """Check if image has enough contrast. Returns (passed, action, msg)."""
    img = Image.open(path)
    if img.mode not in ('L',):
        gray = img.convert('L')
    else:
        gray = img
    
    hist = gray.histogram()
    total = sum(hist)
    dark_pct = sum(hist[:64]) / total * 100
    light_pct = sum(hist[-64:]) / total * 100
    pixel_range = max([i for i, c in enumerate(hist) if c > 0]) - \
                  min([i for i, c in enumerate(hist) if c > 0])
    
    issues = []
    
    if dark_pct < 5:
        issues.append(f"⚠️  Very low contrast: only {dark_pct:.1f}% dark pixels. "
                       "Applying autocontrast fix.")
        if apply_fix:
            gray = ImageOps.autocontrast(gray, cutoff=1)
    
    if pixel_range < 180:
        issues.append(f"⚠️  Narrow tonal range ({pixel_range}/255). "
                       "Applying autocontrast fix.")
        if apply_fix:
            gray = ImageOps.autocontrast(gray, cutoff=1)
    
    if not issues:
        issues.append(f"✅ Contrast OK: {dark_pct:.1f}% dark, range {pixel_range}/255")
    
    return gray, issues
```

Apply `ImageOps.autocontrast(gray, cutoff=1)` before resize/save whenever contrast is flagged. This stretches the black and white extremes to use the full 0-255 range without clipping.

### JPEG quality for grayscale

- **quality=85**: Default for Drive/USB delivery (no size limit). Flawless on e-ink.
- **quality=75**: Good quality, ~80% of Q85 size. Suitable when staying under limits.
- **quality=65**: Acceptable on e-ink, ~40% smaller than Q85. Use for Gmail delivery
  (see `references/gmail-sizing-strategy.md` for grouping recommendations).
- **quality=55**: Lower bound for most manga — text stays readable but fine detail softens.
  Expects source images at least 1000 px wide. If source is smaller, upscale inflates size.
- **quality=30–25**: Heavy-upscale tier. When source images are tiny (~460–700 px) and need
  2–3× upscaling to PW11 (1236×1648), even Q55 produces 35+ MB EPUBs. Drop to Q25–Q30
  to stay under 25 MB Gmail limit. On e-ink at Q25, text is readable with minor artifacts.
  Acceptable when no better source exists (e.g. Archive.org [MS] EPUBs at 460×805 px).
- **quality=20 and below**: ❌ **BANNED for manga.** Confirmed by user feedback: Q10–Q15
  produces unacceptable artifacts on upscaled pages (lines, blockiness). JPEG artifacts at
  this level are clearly visible on 300 PPI e-ink.
- **Quality enforcement / delivery escalation**: When processing for Gmail delivery, use
  **Q65–Q75** as default. If the resulting EPUB still exceeds 25 MB after dropping to Q55,
  **stop compressing.** Upload to Google Drive at **Q85** and share the link.
  The Send-to-Kindle Android app accepts EPUBs up to 200 MB, so Q85 fits comfortably.
  Never silently go below Q50 without explicit user approval — the user prefers quality
  over forced email delivery.
- **Source-image-driven quality selection**: Before choosing a quality level, assess the
  source image resolution first. Tiny sources (~460 px wide) that need 2–3× upscale to
  PW11 (1236 px) will produce large files even at Q55 — sometimes 35+ MB for 200+ pages.
  In that case: (a) try to find a better source (higher resolution), (b) if no better
  source exists and user approves, use Q25–Q30 as absolute floor, (c) if even Q25 exceeds
  25 MB, switch to Drive delivery at Q85 and let the user download via Send-to-Kindle app.

### Quick check snippet

```python
from PIL import Image
import os

def quick_res_check(path):
    """Returns (passed, width, height, message)."""
    img = Image.open(path)
    w, h = img.size
    pw = min(w, h)  # portrait page width
    if pw < 700:
        return False, w, h, f"❌ BLOCKED: {w}x{h} — pages will appear tiny on Kindle"
    if pw < 1000:
        return True, w, h, f"⚠️  Acceptable: {w}x{h} — not ideal"
    return True, w, h, f"✅ Good: {w}x{h}"
```

For CBR/CBZ/JP2 ZIP archives, extract the first image to a temp file and check it.

### When blocked

1. Inform the user why (image dimensions + file size)
2. Suggest the **JP2 ZIP** from Archive.org (contains original high-res scans)
3. Or **CBR/CBZ** from Nyaa.si
4. If no better source exists and user explicitly okays it, override with
   `--force` flag in your processing script. 643px → upscaled to 1236px
   with LANCZOS on a 300 PPI Kindle e-ink screen is readable.
5. Only proceed if user explicitly overrides

### Real case

The Gods Lie original Text PDF (18.5 MB) → images at ~377×550 px → ❌ BLOCKED.  
The Gods Lie JP2 ZIP (70 MB) → images at ~1037×1448 px → ✅ Good.

### Image extraction: filter tiny overlay images
  
When extracting images from EPUBs, scanlation groups sometimes embed text balloons as
separate tiny JPEGs alongside the actual page art. These cause "text mixed with images"
rendering on Kindle. Filter them out during extraction:
  
```python
from PIL import Image
from io import BytesIO
  
for name in zipfile.namelist():
    if not name.lower().endswith(('.jpg','.jpeg','.png')): continue
    data = zipfile.read(name)
    if len(data) < 2000: continue  # too small to be a page
    test = Image.open(BytesIO(data))
    if min(test.size) < 300: continue  # tiny overlay, not a page
    # This is a real page — save it
```

## KCC optimal settings

**Always confirm the user's Kindle model before setting the profile.** Most common defaults:

| Kindle | Profile | Resolution |
|--------|---------|------------|
| Paperwhite 11th Gen (2021) | `KPW5` | 1236×1648 |
| Paperwhite 10th Gen (2018) | `KPW4` | 1072×1448 |
| Paperwhite 12th Gen (2024) | `KPW6` | 1236×1648 |

| Setting | Value | Why |
|---------|-------|-----|
| **Manga Mode** | ✅ ON | Right-to-left reading |
| **Device profile** | User's model (see table above) | Best PPI match — wrong profile = letterboxed or stretched pages |
| **Upscale** | ✅ ON | Prevents letterboxing on smaller source images |
| **High quality** | ✅ ON | Better JPEG encoding |
| **Force color** | ✅ ON | Preserves color pages |
| **Output format** | EPUB first, then convert to MOBI | EPUB is intermediate; MOBI is final for USB |

**If KCC is not available** (e.g. on aarch64 hosts where KCC's 7z dep fails), use `scripts/epub-builder.py` with the workflows above.

## RAR extraction without system unrar

Standard `rarfile` calls `unrar` subprocess and fails if missing. The `uv pip install unrar` package includes a compiled `_unrarlib.abi3.so` embedded in the CFFI module — use it directly:

```python
from unrar.cffi.rarfile import RarFile  # no system unrar needed
# RarFile API is similar to zipfile.ZipFile
rf = RarFile('file.cbr')
data = rf.read('image.jpg')  # reads from embedded library
```

This works on any platform where the CFFI module compiled (including aarch64). The standard `from unrar import rarfile` does NOT work because it tries to find the system library via `ctypes.util.find_library`.

## MOBI quality inspection

Use the script at `scripts/inspect-mobi.py`:

```bash
python3 scripts/inspect-mobi.py file.mobi
```

Checks:
- KCC processing (Kindle Comic Converter metadata)
- Manga mode (RTL reading direction)
- Image resolution distribution
- Page count estimate
- MOBI format validity

## Pitfalls

- **RarFile from `unrar.cffi.rarfile` doesn't support context manager**: 
  `with RarFile('file.cbr') as rf:` raises `AttributeError: 'RarFile' 
  object does not support the context manager protocol`. Always use 
  `rf = RarFile('file.cbr')` without `with`, then call `rf.read(name)` 
  directly. The CFFI wrapper is not a full drop-in for the standard 
  `rarfile.RarFile`.
- **Gmail 25 MB limit**: Always check file size before promising email delivery. Manga volumes almost always exceed this. Propose Drive + USB immediately.
- **Kindle device storage limits**: ~200 MB for older models, ~1-2 GB for modern ones. Vinland Saga Vol 1 at 475 MB fits modern Kindle but not Kindle 1-4.
- **CBR files need extraction** but not the system `unrar` command: `from unrar.cffi.rarfile import RarFile` works without system tool. The CFFI module has unrar compiled in.
- **Encrypted volumes are not downloadable**: "ACS Encrypted PDF" and "LCP Encrypted EPUB" on Archive.org return 401. Check metadata first.
- **Partial series**: Archive.org rarely has complete multi-volume sets. Nyaa.si is better for full series but requires a BT client.
- **Send-to-Kindle rejects MOBI via email since 2022**: Amazon deprecated MOBI for email delivery. Use EPUB for email. MOBI only for USB.
- **Android Send-to-Kindle app has a 200 MB file limit**: Files larger than 200 MB won't send from the Android app. Use USB or Drive for larger files. Convert to grayscale first (see `references/mobi-optimization.md`) to stay under this limit.
- **Nested archives break KCC**: CBR/CBZ with subdirs produce "No images detected" error. Extract flat first.
- **GitHub release downloads from this host return 9-byte files**: When downloading static binaries from GitHub Releases, the network may return redirect pages. Use Archive.org as alternative source for tool downloads, or use pip-based installation.
- **Answer questions before acting**: When the user asks a question mid-task, prioritize answering before continuing with tool calls.
- **Load relevant skills proactively**: When a user mentions a platform (e.g. Reddit), check if a skill exists for it and load it before responding.
- **Reddit search from this host is blocked**: Both old.reddit.com and www.reddit.com return Cloudflare blocks. Try the RSS feeds from `read-reddit` skill (rss.reddit.com) or use Nyaa.si for manga-specific searches.
- **Archive.org filenames with `()`, `[]` need full URL-encoding**: Filenames from
  Archive.org often contain parentheses and brackets, e.g.
  `Monster - c001-008 (v01) [MS].epub`. Simply replacing spaces with `%20` breaks
  curl (exit code 3 — URL malformat). Use `urllib.parse.quote(filename, safe='')`
  to encode everything:
  ```python
  from urllib.parse import quote
  filename = 'Monster - c001-008 (v01) [MS].epub'
  url = f"https://archive.org/download/{archive_id}/{quote(filename, safe='')}"
  ```
- **Archive.org Text PDF is low-res**: The "Text PDF" format on Archive.org is an
  OCR derivative with reduced image resolution — images are ~72 DPI screen-optimized, not suitable for Kindle manga. A full volume (~200 pages) should be 50-200 MB in scan quality. If the PDF is <30 MB, it's a Text PDF. Look for JP2 ZIP (Single Page Processed JP2 ZIP), CBR, or CBZ formats instead. The JP2 ZIP contains the original high-resolution page scans in JPEG2000 format (see `references/archive-org-search-api.md` for conversion steps).
- **Nyaa torrents may be fan-made content**: Not every torrent on Nyaa.si is the real chapter. Some uploads are high-quality fan-made/fan-fiction chapters that mimic the official art style but contain non-canon content. Always verify the first page with `vision_analyze` to confirm it's the real chapter before spending time on conversion. Cross-reference the title with MangaPlus. Look for red flags: wrong chapter title, non-canon character interactions, or art style inconsistencies.
- **Amazon E999 "internal error" on Send-to-Kindle**: Usually caused by invalid EPUB structure, but can also be a transient server-side error (retry often succeeds). If the EPUB is structurally valid (verified with `zipfile.ZipFile`) and retrying still fails, the error is on Amazon's side — wait 12-24h and retry. Two structural causes:

  **1. SVG wrapper pages cause E999:** Amazon's EPUB renderer rejects EPUBs that use `<svg>` wrappers with `preserveAspectRatio` for each page. The CSS+`<img>` approach (see `scripts/fixed-epub-builder.py`) consistently works. Never use SVG wrappers for Send-to-Kindle.

  **2. Cover metadata missing:** Each page needs TWO manifest items (XHTML + image). The first image MUST have `id="cover-image"` and `properties="cover-image"` on its manifest entry. The OPF metadata MUST include `<meta name="cover" content="cover-image"/>` referencing the IMAGE item ID (not the XHTML page ID). Without these, Amazon may return E999 or display the book without cover recognition.

  **⚠️ Common bug: is_cover variable defined but NOT interpolated.** In Python code that generates the manifest, the variable `is_cover = ' properties="cover-image"'` is defined for the first image but then the manifest.append() line uses `media-type="image/jpeg"/>` without interpolating the variable. The fix is to write `media-type="image/jpeg"{is_cover}/>` in the f-string. Double-check every time you add cover support to a script that was working without it.

  **3. Path mismatch (most common):** Images stored at ZIP root level while OPF is inside `OEBPS/`. Relative URLs in OPF (e.g. `href="page1.jpeg"`) resolve relative to the OPF's directory, so they look for `OEBPS/page1.jpeg` — if images are at root, they're not found and Amazon rejects. **Fix:** store images inside `OEBPS/` alongside the OPF.

  **4. Filename mismatch between OPF and actual files:** If source images have zero-padded names (`0001.jpg`) but OPF references non-padded names (`page1.jpg`), Amazon can't find them. Same if extension mismatch: OPF says `page1.jpg` but file is `page1.jpeg`. **Fix:** verify every OPF href matches an actual file in the ZIP.

  **5. `.jpeg` extension missing from image-processing filter (silent zero-page EPUB → E999):** When the CDN serves images with `.jpeg` extension (UUID-based format: `.../{page}.jpeg`), the download step saves files as `0001.jpeg`. If `process_images()` filters only for `('.jpg', '.png')`, it finds nothing → processes zero images → sends empty EPUB → Amazon E999.

  **Fix (two-part):**
  ```python
  # 1. Add `.jpeg` to the filter in process_images():
  files = sorted([f for f in os.listdir(src_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])

  # 2. Add a safety guard after process_images() to abort on zero output:
  proc_files = os.listdir(proc_dir) if os.path.exists(proc_dir) else []
  if not proc_files:
      print("ERROR: Zero images processed. Aborting to avoid sending empty EPUB.", flush=True)
      return
  ```

  **Detection:** Check raw_dir after download — if files end in `.jpeg` but process_images only looks for `.jpg`/`.png`, this is the bug. `total_kb == 0` on the "Processed:" line is the symptom.

  Verify ZIP structure before sending:
  ```python
  from zipfile import ZipFile
  with ZipFile('output.epub', 'r') as z:
      for f in z.namelist():
          print(f)
  ```
  Every image path should start with `OEBPS/`. The `mimetype` entry must be first (uncompressed).
- **Camera icons on Paperwhite 11**: Caused by one of: (a) missing `../` prefix in image path — XHTML at `OEBPS/xhtml/` references images with `src="Images/"` instead of `src="../Images/"`, or (b) missing `rendition:layout=pre-paginated`, `fixed-layout=true`, `zero-margin=true` in OPF metadata. **Fix:** always use `scripts/fixed-epub-builder.py` which has all paths and metadata correct.
- **Unicode U+2019 (smart apostrophe) in author names breaks Python string literals**: When calling `fixed-epub-builder.py` or writing inline Python scripts via heredoc or write_file, author names like "Kaiu&#x2019;s Shirai" or "Makoto Yukimura" contain the RIGHT SINGLE QUOTATION MARK (U+2019). Python interprets this as a string delimiter, producing SyntaxError: `unterminated string literal`. **Fix:** use only ASCII apostrophes (U+0027, `'`) in author names, or define the string using alternative delimiters (bytes+decode, chr() concatenation). When using write_file for Python scripts, avoid typing author names directly — use a Python wrapper that writes the script programmatically, or use execute_code which bypasses this issue.
- **Gmail delivery sizing**: EPUBs for Gmail must fit under 25 MB. Use Q65 with
  2 chapters per file (~25 MB edge) or Q75 with 1 chapter (~15 MB safe). See
  `references/gmail-sizing-strategy.md` for measured sizes and recommendations.
- **Archive.org "Temporarily Offline" on specific files**: Some CDN nodes return
  a 12 KB HTML error page instead of the file. Symptoms: downloaded CBZ/CBR is
  12 KB and starts with `<html>`. **Fix:** retry — Archive.org has multiple CDN
  backends. If a specific CBZ/CBR keeps failing, download the JP2 ZIP version
  (derivative, same content, higher resolution) instead. All JP2 ZIPs for a
  given volume are always accessible since they're generated by Archive.org's
  pipeline, not user-uploaded.
- **MangaPill CDN URL pattern changed multiple times**: As of mid-2026, images are at
  `cdn.readdetectiveconan.com/file/mangap/{year}/{week}/{manga_id}/{chapter_id}/{uuid}/{page}.jpeg`
  with a per-chapter UUID. The old simple pattern `/file/mangap/{manga_id}/{chapter_id}/{page}.jpeg`
  (no UUID, no date path) is dead. If a script that once worked now returns 403 or 0 images,
  the pattern likely changed again — extract fresh URLs from current chapter page HTML using
  `data-src` regex. See `references/mangapill-source.md`.
- **readonepiece.com CDN requires Referer header**: Since mid-2026, the CDN at `cdn.readonepiece.com` returns **403 + 4.8 KB HTML placeholder** when curl/requests download images without a `Referer: https://{domain}.readonepiece.com/` header. Without it, all pages download as 4.8 KB invalid files and PIL raises `UnidentifiedImageError`. **Fix:** always pass `Referer` and a full Chrome User-Agent when downloading images from this CDN.
- **readonepiece.com CDN path changed multiple times**: The image URL path evolved through `/file/mangap/op_{chapter}_{page:02d}.jpg` → `/file/CDN-M-A-N/op_{chapter}_nnd_{page:03d}.png` → `/file/mangap/{year}/{week}/{manga_id}/{chapter_id}/{uuid}/{page}.jpeg` (UUID-based, same pattern as MangaPill). Use a **generic regex** that catches all variants: `(https://cdn\\.readonepiece\\.com/file/[^\"' ]+?\\.(?:png|jpe?g))`. Sort by the last numeric segment before extension for correct page ordering. If extraction returns 0 results or downloads HTML placeholders, the CDN likely changed format again.
- **⚠️ `.jpeg` extension breaks image processing filter**: When the CDN migrates to `.jpeg` extension (current UUID-based format), any code that filters images by `endswith(('.jpg', '.png'))` will find ZERO files — downloads succeed (saved as `NNNN.jpeg`) but the processing loop runs zero iterations, producing an empty EPUB that Amazon rejects with **E999**. **Fix:** include `.jpeg` in the filter: `endswith(('.jpg', '.jpeg', '.png'))` with `.lower()`. Also add a guard — abort if zero images processed.
- **Cron script `one_piece_kindle_cron.py` filename**
- **Using `fixed-epub-builder.py` from Python**: Import via `importlib.util.spec_from_file_location`:
  ```python
  import importlib.util
  spec = importlib.util.spec_from_file_location("epub_builder", "/path/to/fixed-epub-builder.py")
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  mod.build(files_dir, out, title, author)
  ```
- **Monster [MS] scanlator — text as separate image layers**: Archive.org manga_Monster
  EPUBs from the [MS] group store text balloons and page backgrounds as separate JPEGs
  (e.g. 348x126 px text overlays alongside 460x805 px page art). On Kindle, these don't
  overlay properly. This is a source format limitation, not fixable by re-processing.
  Better alternative: use the **CM** Complete Edition from the monster-manga collection
  (18 complete volumes, 200-600 MB each, 1360x2044 px resolution - higher than PW11).
  Filter images under 300 px during extraction to remove small assets.
  mixing, the source EPUB is the problem. Alternative: find another scanlation group
  (e.g. ViZ official releases on Nyaa.si).
- **Berserk source quality variants on Archive.org**: `manga_Berserk` has three tiers:
  - **danke-Empire HD** (path: `!Berserk [danke-Empire]{HD}/`): 180–260 MB EPUBs,
    1571 px wide, highest quality. Too large for Gmail even after processing. Use for
    Drive delivery at Q85.
  - **Hawks** (filename: `Berserk - XXX-XXX (vNN) [Hawks].epub`): 20–60 MB EPUBs,
    460–776 px wide, variable quality. Check filename for `[LQ]` tag — some volumes
    are explicitly Low Quality source.
  - **Evil_Genius** (filename: `Berserk - cXXX-cXXX (vNN) (mag) [Evil_Genius].epub`):
    87–145 MB, mid-quality, later chapters. Check `[mag]` tag = magazine scan.
  Always inspect source image resolution before processing and warn the user about
  low-res sources.

## Known user preferences

If working for Gustavo Mello:
- **Kindle email:** gustavomelloenciv_0yDkTw@kindle.com (Send-to-Kindle delivery)
- **Sender Gmail:** gustavomelloenciv@gmail.com
- **Kindle model:** Paperwhite 11th Gen (KPW5) — 1236×1648 native resolution
- **Format preference:** EPUB for email (Send-to-Kindle), MOBI for USB
- **Language:** prefers English or Portuguese manga
- **Background:** prefers white (#fff) margins around pages, not black (#000)
- **Upscale:** prefers no-crop (fit-height + white canvas) over center-crop — hates lost content
- **Quality over compression**: prefers Q65+ for Gmail delivery. If processing doesn't fit 25 MB at Q55 or higher, upload to Drive at Q85 instead of compressing further. Q25 is the absolute floor — only for tiny source images (~460 px) with explicit user awareness. Never Q15 or below.
- **Drive cleanup before re-upload**: When replacing a previously-uploaded bad EPUB,
  delete it from Drive first (`$GAPI drive delete FILE_ID`), then upload the new version.
  This prevents confusion from stale links.

## Verification checklist

After downloading manga files AND AFTER conversion:
- [ ] Format: EPUB (for Send-to-Kindle) or MOBI (for USB) — confirmed with user
- [ ] EPUB type: check camera-icon safety — verify `fixed-layout=true`, `zero-margin=true`, and `rendition:layout=pre-paginated` in OPF
- [ ] EPUB metadata: `rendition:layout=pre-paginated` and `page-progression-direction="rtl"`
- [ ] Cover metadata: `<meta name="cover" content="cover-image"/>` in OPF + `properties="cover-image"` on first image manifest item (open EPUB zip, check content.opf manifest)
- [ ] Each page: TWO manifest items (XHTML + image), not one
- [ ] EPUB paths: if using XHTML wrappers, verify relative paths — XHTML at `xhtml/` references `Images/` and `css/` via `../` prefix
- [ ] RTL: `page-progression-direction="rtl"` in OPF spine (open EPUB zip and check content.opf)
- [ ] Upscale: if source < target, chose crop or no-crop approach based on user preference. Asked user? [ ] Yes [ ] No (default: no-crop preserves content)
- [ ] Background: user prefers white (#fff) or black (#000)? Default: white.
- [ ] Contrast: sample image has >5% dark pixels OR autocontrast was applied
- [ ] Page count: expected for the volume
- [ ] Size: under 200MB (Android app limit) or under 25MB (Gmail)
- [ ] Language: confirmed with user
- [ ] Delivery: Drive uploaded + link shared
