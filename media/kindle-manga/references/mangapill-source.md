# MangaPill Source

Download manga chapters from MangaPill for Kindle conversion.

## When to use

- Series available on MangaPill (mangapill.com) — good for series not on MangaDex
- CDN image URLs embedded in raw HTML as `data-src` attributes (no JS rendering needed)
- Works with curl + browser headers (User-Agent + Referer)
- Tested with Yomi no Tsugai (Daemons of the Shadow Realm) — 54 chapters

## URL patterns (current, as of 2026-06)

Series page:     `https://mangapill.com/manga/{manga_id}/{slug}`
Chapter reader:  `https://mangapill.com/chapters/{manga_id}-{chapter_id}/{slug}`
CDN base:        `https://cdn.readdetectiveconan.com/file/mangap/{year}/{week}/{manga_id}/{chapter_id}/{uuid}/`
CDN image:       `{CDN base}/{page}.jpeg`

The CDN URL includes:
- **year/week**: upload date path (e.g. `2026/25`)
- **manga_id**: series identifier (5887 for Yomi no Tsugai)
- **chapter_id**: internal chapter number (see formula below)
- **uuid**: per-chapter UUID (changes each chapter — must be extracted from HTML)
- **page**: sequential page number starting from 1

The UUID is **NOT guessable** — each chapter gets a different one when uploaded.
The URL path (year/week) also changes with each batch upload.

## Getting chapter IDs

For Yomi no Tsugai (manga_id=5887), the chapter ID formula is:
```
chapter_id = 10000000 + chapter_number * 1000
```

Examples:
- Chapter 1  → 10001000
- Chapter 2  → 10002000
- Chapter 54 → 10054000

## Extracting image URLs from a chapter page (no browser needed)

The chapter page HTML contains all image URLs in `data-src` attributes on `<img>` tags.
Fetch the HTML with proper browser headers, then regex-extract:

```bash
# Fetch chapter page HTML
CHAPTER_URL="https://mangapill.com/chapters/5887-10054000/yomi-no-tsugai-chapter-54"

curl -sL --max-time 30 \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml" \
  -H "Accept-Language: en-US,en;q=0.9" \
  "$CHAPTER_URL" | \
  grep -oP 'data-src="\K[^"]+(?=")'
```

This returns one URL per page, sequentially numbered:
```
https://cdn.readdetectiveconan.com/file/mangap/2026/25/5887/10054000/019ed26f-2e93-7c8a-b8f9-dcf4fa9353ea/1.jpeg
https://cdn.readdetectiveconan.com/file/mangap/2026/25/5887/10054000/019ed26f-2e93-7c8a-b8f9-dcf4fa9353ea/2.jpeg
...
```

## Download workflow

```bash
# 1. Fetch chapter HTML
CHAPTER_URL="https://mangapill.com/chapters/5887-10054000/yomi-no-tsugai-chapter-54"
mkdir -p chapter_54
cd chapter_54

# 2. Extract all data-src URLs into a list
HTML=$(curl -sL --max-time 30 \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -H "Accept: text/html,application/xhtml+xml" \
  -H "Accept-Language: en-US,en;q=0.9" \
  "$CHAPTER_URL")
URLS=($(echo "$HTML" | grep -oP 'data-src="\K[^"]+(?=")'))

echo "Found ${#URLS[@]} pages"

# 3. Download each with proper headers
CURL_HEADERS=(
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
  -H "Referer: https://mangapill.com/"
  -H "Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
)
for i in "${!URLS[@]}"; do
  page=$((i + 1))
  ext="${URLS[$i]##*.}"
  curl -sL -o "$(printf '%04d' $page).${ext}" \
    --max-time 20 --retry 2 --retry-delay 2 \
    "${CURL_HEADERS[@]}" "${URLS[$i]}"
done
```

## Python pattern (curl subprocess + regex)

```python
import subprocess, re

BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"

def get_image_urls(chapter_url):
    """Fetch chapter HTML and extract all data-src image URLs."""
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "30", "--retry", "2",
         "-H", f"User-Agent: {BROWSER_UA}",
         "-H", "Accept: text/html,application/xhtml+xml",
         "-H", "Accept-Language: en-US,en;q=0.9",
         chapter_url],
        capture_output=True, text=True, timeout=40
    )
    return re.findall(r'data-src="(https://cdn\.readdetectiveconan\.com/[^"]+)"', r.stdout)

def download_page(url, out_path):
    """Download single CDN image with browser headers."""
    subprocess.run(
        ["curl", "-sL", "-o", out_path, "-w", "%{size_download}",
         "--max-time", "20", "--retry", "2",
         "-H", f"User-Agent: {BROWSER_UA}",
         "-H", "Referer: https://mangapill.com/",
         "-H", "Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
         url],
        capture_output=True, text=True, timeout=30
    )

# Example
chapter_url = "https://mangapill.com/chapters/5887-10054000/yomi-no-tsugai-chapter-54"
urls = get_image_urls(chapter_url)
print(f"Found {len(urls)} pages")
```

## Checking for new chapters on a series page

Fetch the series page HTML and regex for chapter links:

```python
import subprocess, re

def get_chapters(manga_url):
    """Extract chapter numbers from MangaPill series page."""
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "30",
         "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
         "-H", "Accept: text/html,application/xhtml+xml",
         manga_url],
        capture_output=True, text=True, timeout=40
    )
    chapters = set()
    for m in re.finditer(r'/chapters/\d+-(\d+)/[^"\']*chapter-(\d+)', r.stdout):
        chapters.add(int(m.group(2)))
    return sorted(chapters, reverse=True)

# Example for Yomi no Tsugai (5887)
chs = get_chapters("https://mangapill.com/manga/5887/yomi-no-tsugai")
print(f"Newest: {chs[0]}, Oldest: {chs[-1]}")
```

## Pitfalls

- **CDN requires both User-Agent AND Referer**: Without a proper Chrome User-Agent
  string, curl gets a 403. Without a `Referer: https://mangapill.com/` header,
  same 403. Both are required for successful downloads.
- **UUID changes per chapter**: The UUID in the CDN path is unique per chapter.
  You MUST extract it from the chapter page HTML — there's no way to guess it
  or construct it from other data.
- **Image format is .jpeg**: Downloaded images are `.jpeg` format. If the format
  changes (e.g. to `.webp` or `.png`), the URL extension in `data-src` reflects
  it automatically.
- **Page count = number of data-src img tags**: No need to probe sequentially\n  or use the browser — the count is the number of `data-src` URLs found in the\n  HTML.\n- **Last page threshold (~12KB)**: The final page is often a credit/end page\n  (~12 KB). Use a download filter of `>15000 bytes` to drop non-content pages.\n  36-44 real content pages is typical for a manga chapter; the last page is\n  frequently the credits/to-be-continued splash.
- **Old simple URL pattern (no UUID) is dead**: The previous pattern
  `/file/mangap/{manga_id}/{chapter_id}/{page}.jpeg` no longer works — chapters
  are now stored under `/{year}/{week}/` with a UUID.
- **Rate limiting**: Add 200-300ms delay between every 10 pages to avoid CDN
  throttling.
- **Chapter ID formula varies by series**: Yomi no Tsugai uses `10000000 + ch * 1000`.
  Other series on MangaPill may use a different scheme — extract from the chapter
  page URL pattern.
