# BPMN 2.0 Rendering with bpmn-js + Chromium Headless

Uses the same Chromium setup from the html-to-pdf-chromium skill to render
BPMN 2.0 XML diagrams as PNG images via bpmn-js (the same engine that powers
Camunda Modeler).

## Project Integration (Dédalo Squad)

Found in `/opt/data/dedalo_squad/render/`:

```
render/
  package.json        # deps: bpmn-js + puppeteer
  render_bpmn.js      # node render_bpmn.js <input.bpmn> [output.png]
  setup.sh            # cd render && bash setup.sh
```

After `git clone`, run:
```bash
cd render && bash setup.sh    # installs bpmn-js + puppeteer, detects Chromium
```

## Chromium Detection Order

The render script auto-detects Chromium in this order:
1. `$PUPPETEER_EXECUTABLE_PATH` or `$CHROMIUM_PATH` env var
2. `/tmp/chromium-extracted/usr/lib/chromium/chromium` (Debian-extracted, aarch64 compatible)
3. Puppeteer's built-in Chromium (downloaded during `npm install`)

On aarch64 (Oracle ARM, Raspberry Pi): the Debian-extracted Chromium is required
because Puppeteer's default is x86_64. The script sets `LD_LIBRARY_PATH` to include
the extracted libs automatically in the `puppeteer.launch({ env: ... })` call.

## Python Wrapper

```python
from agemini.conectores.render_bpmn import renderizar_bpmn, renderizar_e_salvar_no_drive

# Render to bytes
png_bytes = renderizar_bpmn(bpmn_xml_string)

# Render + upload to Google Drive, returns shareable URL
url = renderizar_e_salvar_no_drive(bpmn_xml_string, drive_folder_id, "Estrategico")
```

## Architecture

Puppeteer launches Chromium, loads an HTML page with bpmn-js inlined (~180KB minified),
imports the BPMN XML, waits for `window.__BPMN_READY__`, and takes a fullPage screenshot
at 2x retina. The SVG is also extractable but currently only PNG is saved.

## Output Quality

Indistinguishable from Camunda Modeler — same bpmn-js library, same font rendering,
same shape primitives (rounded rects for tasks, circles for events, diamonds for gateways),
correct arrowhead markers, dashed message flows, pool/lane partitions.

## Pitfalls

### Google Drive `trashed=false` required with `supportsAllDrives`

When listing files in a Drive folder with `supportsAllDrives=True`, the API returns
**trashed files** unless you explicitly add `and trashed=false` to the query.
This caused the audio downloader to pick up 7 deleted files alongside the 1 active file,
resulting in 8× the expected API calls and corrupted transcriptions.

**Fix:** always include `and trashed=false` in Drive `files().list()` queries:
```python
q=f"'{folder_id}' in parents and trashed=false"
```

### bpmn-js UMD bundle must be inlined

ES module imports (`import BpmnJS from '...'`) don't work from `file://` pages.
Use `bpmn-viewer.production.min.js` from the dist/ folder inlined as a `<script>` tag.

### Chromium on aarch64

Puppeteer downloads x86_64 Chrome by default. On ARM machines, use the Debian-extracted
Chromium from this skill's setup. The render script sets `LD_LIBRARY_PATH` automatically
in `puppeteer.launch({ env: { LD_LIBRARY_PATH: ... } })` to include
`/tmp/chromium-extracted/usr/lib/chromium` and `/tmp/chromium-extracted/usr/lib/aarch64-linux-gnu`.

## Exponential Backoff for Gemini API (Dédalo Squad)

The Dédalo Squad pipeline uses a **monkey-patch** in `agemini/modelos/gemini.py` that wraps
all `genai.GenerativeModel.generate_content()` and `genai.ChatSession.send_message()` calls
with exponential backoff from `agemini/backoff.py`.

**Why:** `gemini-3.1-flash-lite` free tier has 15 RPM limit. Running 4+ concurrent processes
triggers 429 errors. The backoff extracts the `retry_delay` from the error message and waits
before retrying (5 attempts, 2s→4s→8s→16s→32s base, with ±25% jitter, capped at 120s).

**How it works:**
```python
# gemini.py — at module load time
from agemini.backoff import retry_call

_original_generate_content = genai.GenerativeModel.generate_content
_original_send_message = genai.ChatSession.send_message

def _generate_content_with_backoff(self, *args, **kwargs):
    return retry_call(
        lambda: _original_generate_content(self, *args, **kwargs),
        max_attempts=5, base_delay=2.0, max_delay=120.0
    )

genai.GenerativeModel.generate_content = _generate_content_with_backoff
genai.ChatSession.send_message = _send_message_with_backoff
```

This means **zero changes to agent code** — every agent that imports `genai` gets backoff
automatically.

**Parallel strategy:** 5 concurrent processes with backoff safely processes 30 items.
Without backoff, 4 concurrent processes all fail with 429 within the first 60 seconds.

### Progress reporting during batch jobs

When running long batch jobs (30+ processes, 10+ minutes), poll the process periodically
and report incremental progress to the user. The user expects updates every ~2 minutes
with counts of completed vs remaining.
