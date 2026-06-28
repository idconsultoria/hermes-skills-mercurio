# Gmail Delivery Sizing Strategy

When the user asks to send manga EPUBs via Gmail (Send-to-Kindle email),
each file must fit under the **25 MB Gmail attachment limit** (effectively
~20 MB for the EPUB after base64 overhead).

## Strategy: adjust JPEG quality × chapter grouping

The tradeoff is between image quality and how many chapters fit per file.

### Measured page sizes (1236×1648 grayscale, no-crop canvas)

| Quality | KB/page | ~50p ch | ~100p (2ch) | ~150p (3ch) | Use case |
|---------|---------|---------|-------------|-------------|----------|
| Q85     | 370 KB  | 18 MB   | 37 MB ❌    | —           | Drive/USB (no size limit) |
| Q75     | 296 KB  | 15 MB ✅| 29 MB ❌    | —           | Gmail-safe for single ch |
| Q65     | 255 KB  | 13 MB ✅| 25 MB ⚠️   | —           | Gmail edge; 2ch fits |
| Q55     | 225 KB  | 11 MB ✅| 22 MB ✅    | 33 MB ❌    | Safe for 2ch; ok on e-ink |

**Recommendations:**

| Goal | Quality | Grouping | Expected size |
|------|---------|----------|---------------|
| Max quality, Drive-only | Q85 | Full volumes (4+ ch) | 60-130 MB |
| Gmail delivery | Q75 | 1 chapter per file | ~15 MB |
| Gmail, 2 chapters/file | Q65 | 2 chapters per file | ~25 MB (edge) |
| Gmail, 3 chapters/file | Q55 | 3 chapters per file | ~33 MB ❌ try Q50 |

### E-ink readability notes

- **Q85**: flawless, indistinguishable from source
- **Q75**: very good; minor JPEG artifacts only visible zoomed in
- **Q65**: good; slight softening on text but perfectly readable on 300 PPI
- **Q55**: acceptable; visible blockiness on fine details (hair, small text)
| Q50 and below | avoid for manga — text becomes noticeably blurry |

## When to escalate to Drive

If even Q55 produces an EPUB over 25 MB, **stop compressing.** Upload to Drive
at Q85 and share the link. The Send-to-Kindle app accepts EPUBs up to 200 MB.
Never go below Q50 without explicit user approval.

## When to use which

```python
# In your volume processing loop, accept a quality param:
QUALITY = 65 if gmail_delivery else 85  # user preference

# Group chapters:
if gmail_delivery:
    for i in range(0, len(chapters), 2):  # pairs
        build_volume(chapters[i:i+2], quality=65)
else:
    for i in range(0, len(chapters), 4):  # official volumes
        build_volume(chapters[i:i+4], quality=85)
| Q50 and below | avoid for manga — text becomes noticeably blurry |

## When to escalate to Drive

If even Q55 produces an EPUB over 25 MB, **stop compressing.** Upload to Drive
at Q85 and share the link. The Send-to-Kindle app accepts EPUBs up to 200 MB.
Never go below Q50 without explicit user approval.

## When to use which

| Delivery method | Quality | Max group |
|----------------|---------|-----------|
| Google Drive → user downloads → Send-to-Kindle app (200 MB limit) | Q85 | 4+ ch |
| Gmail → Kindle email (25 MB limit) | Q65-75 | 1-2 ch |
| USB direct copy | Q85 | Full volumes |
