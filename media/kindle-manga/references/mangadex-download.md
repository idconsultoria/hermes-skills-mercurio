# MangaDex Download Workflow

Batch-download manga chapters from MangaDex for Kindle conversion.

## Why this exists

MangaDex has no official download button. The API serves images via an
at-home CDN, but Python's `urllib` and `requests` get blocked with
HTTP 400 (anti-bot protection). The fix: `curl` via subprocess.

## Key findings (reverse-engineered)

1. **curl with `-sv` works, `-sL` gets blocked.** Use `curl -sv` and
   parse JSON from stdout. The `-sL` flags (silent + follow redirects)
   somehow trigger the HTML response instead of JSON.

2. **No browser-like User-Agent.** The API returns HTML (not JSON) when
   you send a `User-Agent: Mozilla/5.0 ...` header. Use curl's default
   UA or omit custom headers entirely.

3. **`requests` and `urllib` always fail** with 400 HTML from this host.

## Workflow

### 1. Find the manga ID

```bash
curl -sv "https://api.mangadex.org/manga?title=Gin+no+Saji&limit=5" \
  2>&1 | grep -oP '(?<="id":")[^"]+'
```

Extract UUID from the JSON response.

### 2. List chapters (English)

```bash
curl -sv "https://api.mangadex.org/manga/<UUID>/feed?\
limit=200&translatedLanguage%5B%5D=en&order%5Bchapter%5D=asc" 2>&1
```

Each chapter has a UUID, chapter number, volume number, page count.

### 3. Get at-home server data

```bash
curl -sv "https://api.mangadex.org/at-home/server/<chapter-uuid>" 2>&1
```

Returns JSON with:
- `baseUrl` — CDN host (e.g. `https://cmdxd98sb0x3yprd.mangadex.network`)
- `chapter.hash` — content hash
- `chapter.data` — array of page filenames (use `data`, not `dataSaver`)

### 4. Download pages

```bash
curl -sL -o page.jpg \
  "https://<baseUrl>/data/<hash>/<filename>"
```

Image URLs don't need custom headers and work with `-sL`.

## Python pattern (subprocess + curl)

```python
import subprocess, json

def mangadex_fetch(url):
    """Fetch MangaDex API JSON using curl -sv (Python libs blocked)."""
    result = subprocess.run(
        ['curl', '-sv', url],
        capture_output=True, text=True, timeout=30
    )
    if result.stdout.strip().startswith('{"'):
        return json.loads(result.stdout)
    return None

def mangadex_chapter_pages(chapter_id):
    """Get (base_url, hash, [filenames]) for a chapter."""
    data = mangadex_fetch(
        f'https://api.mangadex.org/at-home/server/{chapter_id}'
    )
    if not data or data.get('result') != 'ok':
        return None
    ch = data['chapter']
    return data['baseUrl'], ch['hash'], ch['data']  # full quality

def download_page(base_url, hash, filename, output_path):
    """Download one chapter page."""
    url = f'{base_url}/data/{hash}/{filename}'
    subprocess.run(
        ['curl', '-sL', '-o', output_path, url],
        capture_output=True, timeout=30
    )
```

## Pitfalls

- **No browser UA on API calls**: Setting `User-Agent: Mozilla/5.0`
  triggers the bot wall. Let curl use its default UA.
- **Rate limiting**: The at-home CDN accepts concurrent connections
  but may throttle. Add 50-100ms delay between pages to be safe.
- **No English chapters**: Check `translatedLanguage[]=en` in the
  feed query. If total=0, try other languages or find an alternative
  source — no English scanlation exists yet.
- **Chapter data in PNG**: Some chapters have `.png` files instead of
  `.jpg`. Pillow handles both. The fixed-layout SVG builder needs
  JPEG input — convert with Pillow during the grayscale pipeline.
