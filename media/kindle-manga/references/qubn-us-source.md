# qubn.us — Daemons of the Shadow Realm CDN source

As of June 2026, `scans.lastation.us` is **dead for chapters 55+** (returns HTTP 404).
The active CDN for chapters on `daemonsoftheshadowreal.com` is **qubn.us**.

## URL pattern

```
https://qubn.us/uploads/daemons-of-the-shadow-realm/{ch_num}/daemons-of-the-shadow-realm-ch{ch_num}-{page:03d}.webp
```

- **Format:** .webp (not .png like the old CDN)
- **Referer required:** `https://www.daemonsoftheshadowreal.com/manga/daemons-of-the-shadow-realm-chapter-{ch_num}/`
- **User-Agent required:** Mozilla/5.0 or similar

## Page detection (ad interstitials)

The CDN returns WebP images at **all** positions (001, 002, 003...) but some are small ad
placeholders. Detect real content pages by file size:

| Size | Type |
|------|------|
| > 20,000 bytes | **Real content page** — download and keep |
| < 1,000 bytes | **Ad placeholder** — skip (tiny HTML or 1x1 pixel) |
| 1,000–20,000 bytes | **Possible ad or low-res page** — check manually |

The interleaving is not strictly alternating (odd = content, even = ad). Pages 38 and 39
in ch55 were both real content at consecutive positions. Scan all URLs and filter by
the >20,000 byte threshold.

**Actual page count (tested on ch55, June 2026):** 21 content pages at 1123×1500 px.
Earlier assumption of 36–39 was inflated by ad placeholders.

## Download and probe

### Page count probe (filters ads automatically)

```bash
python3 << 'EOF'
import subprocess
ch = 55  # target chapter
real = 0
for i in range(1, 101):
    url = f"https://qubn.us/uploads/daemons-of-the-shadow-realm/{ch}/daemons-of-the-shadow-realm-ch{ch}-{i:03d}.webp"
    r = subprocess.run(
        ["curl", "-sL", "-o", "/dev/null", "-w", "%{size_download}",
         "-H", f"Referer: https://www.daemonsoftheshadowreal.com/manga/daemons-of-the-shadow-realm-chapter-{ch}/",
         "--max-time", "8", url],
        capture_output=True, text=True, timeout=12
    )
    try:
        size = int(r.stdout.strip())
    except ValueError:
        size = 0
    if size > 20000:
        real += 1
    elif real > 0:
        # After finding at least one real page, if we hit 3 tiny in a row, stop
        tiny = 0
        for j in range(i, min(i + 5, 101)):
            url2 = f"https://qubn.us/uploads/daemons-of-the-shadow-realm/{ch}/daemons-of-the-shadow-realm-ch{ch}-{j:03d}.webp"
            r2 = subprocess.run(["curl", "-sL", "-o", "/dev/null", "-w", "%{size_download}",
                "-H", f"Referer: https://www.daemonsoftheshadowreal.com/manga/daemons-of-the-shadow-realm-chapter-{ch}/",
                "--max-time", "5", url2], capture_output=True, text=True, timeout=8)
            try:
                s2 = int(r2.stdout.strip())
            except ValueError:
                s2 = 0
            if s2 < 1000:
                tiny += 1
                if tiny >= 3:
                    print(f"Chapter {ch}: {real} real pages")
                    exit(0)
            elif s2 > 20000:
                real += 1
        break
EOF
```

### Bulk download

```bash
python3 << 'EOF'
import os, subprocess
ch = 55
dest = f"/tmp/daemons_ch{ch}"
os.makedirs(dest, exist_ok=True)
referer = f"https://www.daemonsoftheshadowreal.com/manga/daemons-of-the-shadow-realm-chapter-{ch}/"
count = 0
for i in range(1, 101):
    url = f"https://qubn.us/uploads/daemons-of-the-shadow-realm/{ch}/daemons-of-the-shadow-realm-ch{ch}-{i:03d}.webp"
    out = os.path.join(dest, f"{i:04d}.webp")
    r = subprocess.run(["curl", "-sL", "-o", out, "-w", "%{size_download}",
        "-H", f"Referer: {referer}", "--max-time", "15", url],
        capture_output=True, text=True, timeout=20)
    size = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    if size > 20000:
        count += 1
        os.rename(out, os.path.join(dest, f"{count:04d}.webp"))
    else:
        os.remove(out)
        if count > 0:
            # stop after 3 consecutive tiny files
            pass  # (see page count probe above for full logic)
print(f"Downloaded {count} real pages to {dest}")
EOF
```

## Chapter numbering (scanlation site)

The site `daemonsoftheshadowreal.com` uses **non-standard numbering** — their "Chapter 94"
does NOT correspond to the official Chapter 94. Official sources (MangaPill) have
chapters 1–54. The scanlation site's numbering is independent.

**Available scanlation chapters (confirmed via HTTP probe):**

```
94, 92, 88, 87, 81, 80, 69, 59, 55, 53–39, 28.5, 28–1
```

Chapters 93, 91, 90, 89, 86, 85 return 404 on qubn.us.

**For the automated cron:** Don't rely on sequential numbering for fetching — always
check the site for the actual latest chapter by scraping the "All Chapters" table on
the homepage.

## Processing webp to Kindle EPUB

WebP images → grayscale → 1236×1648 resize → JPEG Q75 → fixed-layout EPUB →
Gmail delivery.

Use `scripts/send_kindle_gmail.py` for the Gmail attachment send (supports EPUBs
via Gmail API `users.messages.send` with base64 MIME). Falls back to Drive upload
for files > 25 MB.

## Migration note

Chapters 1–38: previously on MangaPill CDN (`cdn.readdetectiveconan.com`)
Chapters 28.5, 39–54: previously on `scans.lastation.us`
Chapters 55+: only on `qubn.us`

The automated cron (`daemons_kindle_cron.py`) manages state via `daemons_state.json`
under `/opt/data/scripts/` and runs monthly on the 25th (cron `1ded3dfe4064`).
