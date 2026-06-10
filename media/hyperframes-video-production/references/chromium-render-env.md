# Chromium Render Environment (Oracle Linux ARM64)

## Context

The Hermes container runs on Oracle Linux ARM64 without root/sudo. The system Chromium snap is on the host (accessible via `ssh oracle-host` but not from inside the container). A Debian-extracted Chromium build lives at `/tmp/chromium-extracted/usr/lib/chromium/chromium` for HTML-to-PDF tasks (see `html-to-pdf-chromium` skill).

HyperFrames uses this same Chromium for video rendering.

## Required Env Vars

```bash
export HYPERFRAMES_BROWSER_PATH=/tmp/chromium-extracted/usr/lib/chromium/chromium
export LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium
```

## Performance

- **Mode:** Screenshot capture (HeadlessExperimental.beginFrame unavailable in standard Chrome builds)
- **Speed:** ~2.6s per frame at 1920×1080 (p95)
- **Formula:** `frames × 2.6s` total render time
- **Example:** 46s video @ 30fps = 1380 frames = ~3588s ≈ 6 minutes

### Mitigations

| Strategy | Change | Effect |
|----------|--------|--------|
| Shorter video | 15s @ 30fps = 450 frames | ~20 min → ~20 min (450 × 2.6s) |
| Lower FPS | 46s @ 15fps = 690 frames | ~60 min → ~30 min |
| Lower resolution | 1280×720 (half pixels) | ~2.6s → ~1.3s per frame (estimated) |
| Combine all | 15s @ 15fps @ 720p | ~6 min total |

## Verification

```bash
export HYPERFRAMES_BROWSER_PATH=/tmp/chromium-extracted/usr/lib/chromium/chromium
export LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium
npx hyperframes doctor | grep -i browser
# Expected: "Browser: env" (not "Browser: not found")
```
