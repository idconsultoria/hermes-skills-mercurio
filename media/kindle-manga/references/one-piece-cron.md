# One Piece Automated Kindle Delivery — Cron Job Reference

Cron job ID: `388e767fcc7c`
Schedule: Every Saturday 12:00 BRT (15:00 UTC) — `0 15 * * 6`
Script: `~/./scripts/one_piece_kindle_cron.py` (caminho absoluto: `/opt/data/scripts/one_piece_kindle_cron.py`)
Mode: `no_agent=True` (watchdog — silent when nothing new)

## How it works

1. Reads last chapter number from `/opt/data/scripts/last_op_chapter.txt` (initially 1185)
2. Probes readonepiece.com domains `ww5` through `ww20` via curl to find working domain
3. Checks if `chapter (last+1)` returns HTTP 200
4. If found: extracts CDN image URLs from HTML, downloads, processes, builds fixed-layout EPUB, sends via Gmail → Kindle
5. If not found: exits silently (no output = no delivery)

## CDN Image Extraction

The CDN at `cdn.readonepiece.com` has evolved. Two known patterns as of mid-2026:

**Old pattern (CDN-M-A-N):**
| Property | Value |
|----------|-------|
| **Base** | `https://cdn.readonepiece.com/file/CDN-M-A-N/` |
| **Filename pattern** | `op_{chapter}_nnd_{page:03d}.png` (zero-padded 3 digits) |
| **Format** | PNG |

**New pattern (UUID-based, mirrors MangaPill):**
| Property | Value |
|----------|-------|
| **Base** | `https://cdn.readonepiece.com/file/mangap/{year}/{week}/{manga_id}/{chapter_id}/{uuid}/` |
| **Filename pattern** | `{page}.jpeg` |
| **Format** | JPEG |

**For both patterns:** CDN requires `Referer: https://{domain}.readonepiece.com/` header. Without it, returns 403 with a 4.8 KB HTML placeholder instead of the image.

### Regex for HTML extraction

Use a **generic regex** that catches ALL variants (old underscore-based, new UUID-based):

```python
re.findall(r"(https://cdn\\.readonepiece\\.com/file/[^\"' ]+?\\.(?:png|jpe?g))", html)
```

Sort by the last numeric segment before extension (works for both `_NNN.png` and `/{page}.jpeg`):

```python
def page_sort_key(url):
    m = re.search(r'/(\\d+)\\.(?:png|jpe?g)$', url)  # new: /N.jpeg
    if m: return int(m.group(1))
    m = re.search(r'_(\\d+)\\.(?:png|jpe?g)', url)   # old: _NNN.png
    if m: return int(m.group(1))
    return 0
unique.sort(key=page_sort_key)
```

### Pitfalls

- **Old regex breaks silently**: The CDN path has changed from `/file/mangap/...jpg` to `/file/CDN-M-A-N/...png`. If the cron script finds a chapter but downloads 4.8 KB placeholders, the regex still needs updating.
- **Domain rotation**: `ww{N}.readonepiece.com` rotates between `ww5` and `ww20`. The cron script probes all of them. The browser may redirect to a different domain (`ww5 → ww12`, for example) — always use the actual redirect target's domain for the Referer header.
- **Chapter numbering**: Some chapters have decimal variants (e.g., `1054.5`, `1053.4`). The cron script increments by 1, so it won't catch fractional chapters automatically — they'd need manual dispatch.

## Key configuration

- Kindle email: gustavomelloenciv_0yDkTw@kindle.com
- Gmail sender: gustavomelloenciv@gmail.com
- Token: `/opt/data/google_token.json`
- Resolution: 1236×1648 (PW11/KPW5)
- Upscale: fit-height + white canvas (no crop)
- Format: fixed-layout EPUB (../Images/ path, RTL, pre-paginated, white bg)

## Troubleshooting

- **Domain not found:** readonepiece.com domains rotate. The domain probe spans `ww5-ww20`.
- **Curl fails:** The script uses `subprocess.run` with `curl` internally. If curl fails, check network.
- **Chapter not found on Saturday:** Chapters typically arrive Tuesdays. If Saturday cron finds nothing, the next run will catch it.
- **Gmail token expired:** Token auto-refreshes via `google.auth.transport.requests.Request`. If multiple failures, re-run setup.
- **Script not found:** The cron job references `one_piece_kindle_cron.py` (with `_cron` suffix). The file lives at `~/./scripts/one_piece_kindle_cron.py`. If the cron job was created without `_cron`, update with `cronjob action=update job_id=388e767fcc7c script=one_piece_kindle_cron.py`.
