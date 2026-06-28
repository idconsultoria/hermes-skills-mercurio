# scans.lastation.us Source

CDN backend for `daemonsoftheshadowreal.com` and related aggregators.
Useful when MangaPill CDN misses chapters (observed 404 on ch 39+ for
Yomi no Tsugai).

## When to use

- MangaPill CDN returns 404 for ALL pages of a chapter
- No English scanlation on MangaDex
- Need chapters beyond what MangaPill carries
- Tested with Yomi no Tsugai (Daemons of the Shadow Realm) — 54+ chapters

## URL pattern

```
https://scans.lastation.us/manga/{Series-Name}/{chapter:04d}-{page:03d}.png
```

For Yomi no Tsugai:
```
https://scans.lastation.us/manga/Yomi-no-Tsugai/0039-001.png  # Ch 39 page 1
https://scans.lastation.us/manga/Yomi-no-Tsugai/0054-037.png  # Ch 54 page 37
```

## Chapter → ID mapping

Chapter number is zero-padded to 4 digits, hyphenated to page number:
- Chapter 39 → `0039-001.png` through `0039-038.png`
- Chapter 54 → `0054-001.png` through `0054-037.png`
- Chapter 28.5 may not exist (returned 0 pages)

## Download constraints

| Issue | Fix |
|-------|-----|
| Blocks without Referer | Pass `Referer: https://www.daemonsoftheshadowreal.com/` |
| Only `.png` format observed | Don't try `.jpeg` or `.jpg` fallback |
| Sequential page numbering | Probe pages 1..N until 3 consecutive 404s, or 404 confirms end |
| Rate limiting | Light; 200ms delay between pages sufficient |

## Python download pattern

```python
import subprocess

def download_chapter(ch_num, dest_dir, base_url):
    ch_padded = f'{int(ch_num):04d}'
    ref = f'https://www.daemonsoftheshadowreal.com/manga/daemons-of-the-shadow-realm-chapter-{int(ch_num)}/'
    
    page = 1
    fails = 0
    while fails < 3:
        url = f'{base_url}/manga/Yomi-no-Tsugai/{ch_padded}-{page:03d}.png'
        out = f'{dest_dir}/{page:04d}.png'
        cmd = ['curl', '-sL', '-o', out, '-w', '%{http_code}',
               '-H', f'Referer: {ref}',
               '-H', 'User-Agent: Mozilla/5.0',
               '--max-time', '10', url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if r.stdout.strip() == '200':
            from PIL import Image
            try:
                Image.open(out).verify()
                fails = 0
                page += 1
                continue
            except:
                pass
        if os.path.exists(out):
            os.remove(out)
        fails += 1
        page += 1
    return page - 1 - fails
```

## Image quality

| Metric | Value |
|--------|-------|
| Resolution | 1200×1710 px |
| Format | PNG (lossless) |
| DPI estimate | ~300+ — good source for Kindle PW11 |
| Quality gate | ✅ 1200px ≥ 1000 (good) |
