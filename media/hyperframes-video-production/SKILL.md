---
name: hyperframes-video-production
description: >-
  Produce deterministic MP4 videos using HyperFrames (HTML→video engine).
  Generates HTML compositions with GSAP animations, renders locally via
  npx hyperframes. Hermes Style Guide is the default visual aesthetic
  for explainer/demo videos.
category: media
---

# HyperFrames Video Production

> **Engine:** HyperFrames v0.6.79 (HTML → deterministic MP4)
> **Deps:** Node.js 22+, FFmpeg, `npx hyperframes`
> **Style default:** Hermes Style Guide (Amber, Blue & Dither) adapted for video

## Prerequisites Check

```bash
node --version          # needs 22+
ffmpeg -version         # needs ffmpeg
npx hyperframes --version  # should print version
```

## Project Structure

```
<project>/
├── index.html          # main composition
├── hyperframes.json    # project config
├── meta.json           # metadata
├── package.json        # scripts (dev, check, render)
├── AGENTS.md           # agent instructions
├── CLAUDE.md           # rules for Claude/agents
├── assets/             # media (images, fonts, audio)
└── compositions/       # sub-compositions (optional)
```

## Quick Start

```bash
# 1. Scaffold a new project
npx hyperframes init my-video
cd my-video

# 2. Preview (runs a dev server — keep in background)
npm run dev &
sleep 3

# 3. After editing index.html, validate
npm run check

# 4. Render to MP4
npm run render
```

## Composition Rules (Critical)

Every timed element in `index.html` MUST follow these rules:

1. **Root div** with `data-composition-id`, `data-start="0"`, `data-duration="N"`, `data-width="1920"`, `data-height="1080"`
2. **Visible timed elements** have `class="clip"` plus `data-start`, `data-duration`, `data-track-index`
3. **Audio elements** have `data-start`, `data-duration`, `data-track-index`, + `data-volume`
4. **GSAP timeline** must be `paused: true` and registered on `window.__timelines[compositionId]`
5. No `Date.now()`, `Math.random()`, or network fetches inside composition
6. Videos use `muted` attribute — audio goes on separate `<audio>` element

### Example Scaffold

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1920, height=1080" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>/* styles */</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0"
       data-duration="30" data-width="1920" data-height="1080">

    <!-- Clips go here -->

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      // Animation keyframes
      window.__timelines["main"] = tl;
    </script>
  </div>
</body>
</html>
```

## Hermes Style Guide (for Video)

Default aesthetic for all videos unless user specifies otherwise.

### Color Palette (Direct — no CRT inversion)
```
  #0000f2  (royal blue)   → Primary text, borders, accents
  #ffffff  (white)         → Page/panel backgrounds
  #000000  (black)         → Body background (dark theme)
  #171717  (dark gray)     → Card backgrounds
  #e8e8e8  (light gray)    → Secondary text, muted elements
  #00d8fd  (cyan)          → Highlights, emphasis, active elements
  #ff0000  (red)           → Alerts, warnings
  #ffff0d  (amber)         → Accent glow, secondary highlights
```

### Typography for Video
```
  'Cormorant Garamond', serif  → Main titles (bold, uppercase, large)
  'Syncopate', sans-serif      → Section headers (uppercase, wide tracking)
  'VT323', monospace           → Status badges, tags (uppercase)
  'Space Mono', monospace      → Body text, captions, code
```

### Visual Elements
```
  - CRT scanline overlay: subtle animated horizontal lines (opacity 0.03-0.05)
  - CRT vignette: radial gradient darkening corners
  - Grid lines: 1px solid rgba(0,0,242,0.15) separating sections
  - Terminal blocks: 3px double border #0000f2, with dot header
  - Isometric buttons: box-shadow 4px 4px 0px rgba(0,0,242,0.2)
  - Status badges: borders with #0000f2, optional filled variant
  - 0px border-radius (sharp corners)
```

### Font Sizes for 1920×1080 (Mandatory)

At 1920×1080, text must be large. These are the minimum sizes:

```
  Giant Serif (Cormorant Garamond)  → 120–140px (titles)
  Wide Label (Syncopate)             → 20–24px   (section headers)
  Mono Body (Space Mono)             → 22–28px   (body text)
  Card Descriptions                  → 18–22px   (agent/step descriptions)
  Pixel Tag (VT323)                  → 16–20px   (status, tags, corner labels)
  Counter Numbers                    → 84–96px   (data displays)
  Output Grid Labels                 → 14–16px   (small text in grids)
  Badges                             → 20–24px   (status badges)
  Step Card Titles                   → 26–30px   (phase names)
  Terminal Lines                     → 28px      (typewriter text)
```

### Icon System

Prefer **inline SVG icons** over emojis. Emojis render inconsistently across platforms and break the Hermes aesthetic. Create simple, geometric SVGs:

- Use `stroke="#0000f2"` (royal blue) with `stroke-width="1.5"` or `2`
- Keep it minimal: 2-4 shapes per icon
- ViewBox 0-20 or 0-28 for small icons, 0-36 for larger ones
- Icons go inside a bordered square container matching the card's style

**Icon mapping for common concepts:**
```
  Idea/Concept        → diamond/polygon shape
  Research/Search     → circle + line (magnifier)
  Document/PRD        → rectangle with lines
  Software/Code       → rectangle with angle brackets
  User/Persona        → circle + path (person silhouette)
  Data/Chart          → polyline (graph line)
  Database/Storage    → stacked ellipses (cylinder)
  API/Integration     → rectangle with plug line
  Design/Visual       → circle with crosshair lines
  Process/Pipeline    → grid with dots
  Cycle/Iteration     → circular arrows
  Launch/MVP          → triangle/arrow pointing up
  Agent               → head outline or terminal icon
  Test/Check          → polyline checkmark
```

### Centering (Critical)

Every scene uses `display:flex; flex-direction:column; align-items:center; justify-content:center;` on the scene element itself. The scene must have `position:absolute; inset:0; width:1920px; height:1080px;`. Place all content inside the scene as direct flex children. Use `.corner-tag` for absolute-positioned labels that should not participate in flex centering.

### Scene Templates

#### Scene 1 — Title Card (3-5s)
Full-screen title with icon, centered. Fade-in + scale animation.
- Background: dark with subtle radial glow
- GSAP: `from(title, {opacity:0, scale:0.9, duration:1})` at start
- Tag badges at top: category + duration labels

#### Scene 2 — Definition / Explanation (5-8s)
Left: icon/visual, Right: text block with definition.
- Terminal-style header with dots on top
- Text appears line by line (stagger)
- GSAP: `staggerFrom(lines, {opacity:0, x:20, duration:0.4}, 0.15)`

#### Scene 3 — Process / Flow (8-12s)
Horizontal flow with numbered steps connected by line.
- Each step fades in sequentially (stagger)
- Connecting line draws from left to right
- GSAP: `staggerFrom(steps, {opacity:0, y:30, duration:0.5}, 0.3)`

#### Scene 4 — Comparison / Grid (5-8s)
Side-by-side cards showing contrast (e.g., before vs after).
- Cards slide in from opposite sides
- GSAP: `from(left, {x:-100, opacity:0})`, `from(right, {x:100, opacity:0})`

#### Scene 5 — Numbers / Data (4-6s)
Large numbers counting up with label below.
- GSAP: count-up effect using textContent in onUpdate

#### Scene 6 — Call to Action / End Card (3-5s)
Button or bold text centered. Pulsing glow animation.
- GSAP: infinite pulse via repeat:-1 yoyo:true

## Workflow

### 1. Plan the Video
- Define total duration (e.g., 45s for an explainer)
- Break into scenes (5-8s each)
- Write script per scene
- Map each scene to a template above

### 2. Build the Composition
```bash
cd /opt/data && npx hyperframes init product-pipeline-video
```

### 3. Edit index.html
Write all scenes in the composition. Each scene gets:
- A `<div class="scene">` container
- Proper `data-start`, `data-duration`, `data-track-index`
- GSAP animations in the `<script>` block

### 4. Validate
```bash
cd /opt/data/product-pipeline-video && npm run check
```

### 5. Render
```bash
cd /opt/data/product-pipeline-video && npm run render
```

### 6. Deliver
```bash
ls -la output/*.mp4
# Send via MEDIA:<path>
## Pitfalls

⚠️ **npm run dev is a SERVER** — it blocks. Always run in background (`&` or `background=true` with terminal tool).

⚠️ **Check BEFORE render** — `npm run check` catches missing attributes, broken timelines, and non-deterministic code. Fix all errors first.

⚠️ **No random/date** — compositions must be deterministic. `Math.random()`, `Date.now()`, and `fetch()` will produce non-reproducible videos.

⚠️ **GSAP version** — Use CDN `https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`. Other versions may have different APIs.

⚠️ **Track index** — Each timed element needs a unique `data-track-index`. Overlapping elements on the same track index may cause visual glitches.

⚠️ **Screenshot mode is slow (ARM64 without chrome-headless-shell)** — On Linux ARM64, chrome-headless-shell is unavailable, so HyperFrames falls back to screenshot capture (~2.6s/frame p95 at 1920×1080). A 46s video at 30fps takes ~6 min. See `references/chromium-render-env.md` for detailed performance model and mitigations.

⚠️ **Browser environment — use extracted Debian Chromium** — On Oracle Linux ARM64 without root, use the pre-extracted Chromium at `/tmp/chromium-extracted/usr/lib/chromium/chromium` with `LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium`. See `references/chromium-render-env.md` for full setup.

⚠️ **Linting: root composition attributes** — The linter requires the root element (first child of `<body>`) to have `data-composition-id`, `data-width`, `data-height`, `data-start`, `data-duration`. Place a wrapper `<div>` as the first child of `<body>` with these 5 attributes and `style="position:absolute;inset:0;"`. Do NOT put these on `<body>` itself — the linter won't recognize them there. Overlay divs (scanlines, vignette) should go INSIDE this wrapper, not before it.

⚠️ **GSAP selector scoping** — The linter warns about unscoped class/attribute selectors (e.g. `.step-card[data-phase='1']`). Prefix every non-ID selector with `body` or `[data-composition-id="main"]`:
  ```js
  tl.from("body .step-card[data-phase='1']", {...});  // scoped
  tl.from("#title-main", {...});                        // IDs inherently unique
  ```

⚠️ **Fonts in render** — Google Fonts `<link>` works in headless Chrome but adds latency. HyperFrames caches fetched fonts after first load. Missing `@font-face` warnings are non-blocking.

## Verification

```bash
npm run render  # Should produce renders/*.mp4
ls -la renders/
# Check file size (> 100KB for real video) and duration:
ffprobe renders/*.mp4 2>&1 | grep Duration
```
