---
name: hyperframes-video-production
description: "Produce deterministic MP4 videos via HyperFrames — HTML compositions to video.

Load this skill when creating programmatic video content. Covers HTML composition with GSAP animations, local rendering via npx hyperframes, Hermes Style Guide integration for explainer/demo videos, and deterministic output for consistent regeneration."

Load this skill when creating programmatic video content. Covers HTML composition with GSAP animations, local rendering via npx hyperframes, Hermes Style Guide integration for explainer/demo videos, and deterministic output for consistent regeneration."
category: media
type: Media
timestamp: 2026-06-12T02:23:22Z
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

### Vertical 9:16 Video

For phone-format vertical video (e.g., 768×1280 ads), see `references/vertical-video.md` for resolution setup, font sizes, particle patterns, and GSAP repeat workarounds. The 1920×1080 scene templates below adapt directly — just use vertical positioning.

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

## Advertising Video Templates (Vertical 9:16)

For 30-second product ads in vertical format (768×1280), use this 6-scene structure. Each scene = ~5 seconds, optimized for fast reading on mobile screens.

### Format Config
```html
<div id="root" data-composition-id="main" data-start="0"
     data-duration="30" data-width="768" data-height="1280">
```

### Font Sizes for 768×1280 (Vertical)

These sizes are calibrated for **smartphone screens at arm's length** — the rendered video is viewed on a 6–7" display, not a desktop monitor. What looks fine at 1920×1080 on a 27" screen is 4–5× too small at 768×1280 on a phone. **When in doubt, go bigger.** Illegible text is the #1 rejection reason for mobile video ads.

```
  Main titles     → 48–56px (bold 800)        — must dominate the scene
  Section titles  → 38–48px (bold 700)        — clear hierarchy below main
  Subtitles       → 26–32px (semi-bold 600)   — readable at a glance
  Body/descriptions → 22–26px (regular 400)   — minimum for any narrative text
  Tags/labels     → 20–24px (medium 500)      — icon labels, service names
  Footer/URL      → 22–30px (bold 700–800)    — URL and social handles are CTAs, not fine print
  Logo img        → 340–380px max-width       — brand authority in opening/closing
  Hero partner logos → 180–220px max-width    — ecosystem showcase
  Secondary partner logos → 100–140px max-width — supporting brands
  SVG icons       → 100–200px viewport        — icons must be recognizable, not decorative
```

**Verification checklist before render:**
- Can you read every text element from 2 meters away? If not, bump the size.
- Is any text below 20px? If yes, it will be a blur on most phones — increase it.
- Do any elements sit below `top: 75%`? If yes, the bottom 25% of the screen is empty — redistribute vertically.
- Are logos/images smaller than 120px in any dimension? If yes, they lose brand identity — scale up.
- Does every scene fill the vertical canvas? Empty bottom space >30% means the layout needs `top` adjustments.

### Scene 1 — Opening / Brand Reveal (0–5s)
Logo entrance with motion background (particles, gradient). Tagline below.
- Background: deep brand color gradient
- Logo: scale 0.6→1.0 + opacity 0→1, ease: power3.out at t=1s
- Glow: `box-shadow: 0 0 60px rgba(<brand-accent>,0.5)` on logo
- Particles: 12–18 small circles (2–5px) with glow, moving across screen
- Text: tagline fade-in after logo, centered below
- GSAP: timeline with pre-computed particle positions (NO Math.random)

### Scene 2 — Feature Highlight (5–10s)
Core product with pulsing icon + benefit text.
- Background: dark with speed lines (horizontal streaks sliding across)
- Icon: SVG relevant to product, pulsating scale yoyo at 0.6s period
- Title: product name in bold, subtext below
- GSAP: speed lines translateX, icon pulse with repeat:-1 yoyo:true

### Scene 3 — B2B / Enterprise (10–15s)
Corporate segment with digital grid, service icons.
- Background: grid lines (brand accent at 10–15% opacity)
- Title: segment name (bold, uppercase)
- Icons: 2–3 SVG service icons with labels, staggering in
- GSAP: grid fade-in, title slide-down, icons stagger with scale bounce

### Scene 4 — Partners / Ecosystem (15–20s)
Logo showcase of partners or integrations.
- Background: dark gradient with subtle colored particles
- Hero partner logos: large, centered, entering from bottom with spring
- Secondary logos: smaller row below, staggering after heroes
- Text: category description, fade-in after all logos
- GSAP: hero logos from({y:80, opacity:0, scale:0.8}), secondary stagger 0.2s

### Scene 5 — Trust / Security (20–25s)
Dark dramatic scene with shield/badge and protection message.
- Background: near-black (#0A0A1A) — maximum contrast
- Shield: SVG path with `stroke-dashoffset` animation (drawSVG effect)
- Fill: subtle accent color at 15% opacity after draw completes
- Title: segment name + protection message
- GSAP: drawSVG on path, title syncs with draw completion

### Scene 6 — Closing / CTA (25–30s)
Return to brand background. Logo top, bold CTA center, URL/contact footer.
- Background: brand gradient (match scene 1)
- Logo: centered in upper third
- CTA: largest text on screen (36px+), white, scale pulse infinite
- Contact: URL + social handle, small, bottom third
- GSAP: logo fade-in, CTA scale pulse repeat:-1 yoyo:true duration:0.8

### Motion Effects Library
Common reusable effects for advertising scenes:
```
  Fiber-optic particles: circles ciano 40% opacity, translateX/Y across scene
  Speed lines:        thin rects, translateX(-100% → +100%), varying durations
  Digital grid:       repeating-linear-gradient lines at 10-15% opacity
  Glow/pulse:         box-shadow + scale yoyo (0.6–0.8s period)
  drawSVG shield:     stroke-dashoffset animates from full to 0
  Logo reveal:        scale 0.6→1.0 + opacity 0→1, power3.out ease
```

## Brand Color Adaptation (Web → Video)

When a brand style guide exists with web colors, adapt them for motion graphics.
See `references/brand-to-video-color-adaptation.md` for the full recipe — derivation
rules, anti-patterns, and a verification checklist.

| Web Role | Web Color (example) | Video Adaptation |
|----------|---------------------|------------------|
| Primary blue | `#1e87f0` (UI blue) | Deepen to navy `#001B3D` for dark backgrounds; promote to neon `#00D2FF` for glow/highlights |
| Accent orange | `#ff9f00` | Use sparingly — small accents only. Reduce saturation in dark scenes |
| White | `#ffffff` | Keep pure white for text. Never tint body text |
| Dark gray | `#1D1D1B` | Use as secondary dark. Don't use pure black except for security/dramatic scenes |

**Rule:** Keep the brand's font family and logo intact. Upgrade colors for screen impact (deeper darks, brighter highlights) but stay in the same hue family. Never introduce a color that has no basis in the brand's palette — derive it by pushing saturation or lightness, not by changing hue.

## Workflow

### 1. Plan the Video
- Define total duration (e.g., 30s for an ad, 45s for an explainer)
- Break into scenes (5–8s each for horizontal; 5s each for vertical ads)
- Write script per scene
- Map each scene to the appropriate template above (Advertising or Hermes explainer)
- **Consume brand input** — if a brand style guide or asset manifest was produced by brand-studio-forge's forge_analyze, load it now. Extract the brand's color palette, typography, and logo paths. Override the Hermes default style with the brand's identity. Look at the guide's "Paleta do Vídeo" section if present — it contains pre-adapted motion-graphics colors. Place downloaded assets (`<brand>-logo.png`, partner logos, icons) into the project's `assets/` directory.
- **Extract brand from live site** — when no style guide exists, perform a brand extraction directly. See `references/brand-extraction-for-video.md` for the full CSS-scraping, font-detection, logo-download, and browser-vision workflow. This produces the same inputs (palette, typography, asset paths) as a pre-existing style guide.
- **Reconcile palettes** — if the brand guide has web colors but no video palette, derive one using the Brand Color Adaptation rules above. Document the derived palette in the plan before writing HTML.

### 2. Build the Composition
```bash
cd /opt/data && npx hyperframes init product-pipeline-video
```

### 3. Edit index.html
Write all scenes in the composition. Each scene gets:
- A `<div class="scene">` container
- Proper `data-start`, `data-duration`, `data-track-index`
- GSAP animations in the `<script>` block

### 3.5 Layout Audit + Design Review (Required for Vertical / First-Time Resolutions)

After writing the HTML but before rendering, run a design audit with agy (Gemini) on the Oracle host. The linter catches syntax — agy catches readability. See `references/layout-audit-with-agy.md` for the full 3-pass workflow:

1. **Audit pass** — catches font sizes too small for phone screens, unbalanced vertical spacing, and logo illegibility
2. **Creative pass** (after audit fixes succeed) — elevates the composition with glass panels, particle effects, radar sweeps, and motion-graphics polish
3. **Focused correction pass** (after user reviews rendered video) — surgical fixes for specific bugs the user reports, without redesigning everything

Skip the audit and you will render invisible text if you guessed font sizes wrong for the target resolution.

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

⚠️ **Browser environment — use extracted Debian Chromium** — On Oracle Linux ARM64 without root, set BOTH env vars before render: `HYPERFRAMES_BROWSER_PATH=/tmp/chromium-extracted/usr/lib/chromium/chromium` AND `LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium`. The validate step will attempt apt-get (which fails without root); the render will use the env-configured browser. See `references/chromium-render-env.md` for full setup and performance model.

⚠️ **Linting: root composition attributes** — The linter requires the root element (first child of `<body>`) to have `data-composition-id`, `data-width`, `data-height`, `data-start`, `data-duration`. Place a wrapper `<div>` as the first child of `<body>` with these 5 attributes and `style="position:absolute;inset:0;"`. Do NOT put these on `<body>` itself — the linter won't recognize them there. Overlay divs (scanlines, vignette) should go INSIDE this wrapper, not before it.

⚠️ **GSAP selector scoping** — The linter warns about unscoped class/attribute selectors (e.g. `.step-card[data-phase='1']`). Prefix every non-ID selector with `body` or `[data-composition-id="main"]`:
  ```js
  tl.from("body .step-card[data-phase='1']", {...});  // scoped
  tl.from("#title-main", {...});                        // IDs inherently unique
  ```

⚠️ **Fonts in render** — Google Fonts `<link>` works in headless Chrome but adds latency. HyperFrames caches fetched fonts after first load. Missing `@font-face` warnings are non-blocking.

⚠️ **Brand asset paths** — Downloaded brand assets (logos, partner images) must be placed inside the project's `assets/` directory. Reference them from HTML as `assets/filename.png`. Do not use absolute paths — HyperFrames resolves asset URLs relative to the project root, not to the HTML file.

⚠️ **Vertical video font sizes** — Text that looks good at 1920×1080 will be TINY at 768×1280 after scaling down. Use the `Font Sizes for 768×1280` table above — sizes are 3–4× smaller than the 1920×1080 equivalents because the viewport is smaller but the rendered output is still viewed at phone size.

⚠️ **Brand logo on dark backgrounds** — Most brand logos are designed for white/light backgrounds (positive version). On dark video backgrounds, either use a white/inverted logo variant or apply a CSS `filter: brightness(0) invert(1)` to the logo `<img>`. Check the brand's style guide for a white/negative logo file first.

⚠️ **Particle pre-computation** — Motion backgrounds with particles must NOT use `Math.random()`. Pre-compute all particle positions and durations as static arrays in a `<script>` block before the GSAP timeline. Use loops over these arrays to create animation tweens deterministically.

⚠️ **CRITICAL: `opacity:0` in inline styles + `tl.from({opacity:0})` = invisible text** — GSAP's `tl.from()` records the element's **computed/inline style value** as the animation destination. If the inline style has `opacity:0`, the target is 0, and the animation goes 0→0 (never visible). The fix: **never put `opacity:0` in inline styles on elements that use `tl.from({opacity:0})`**. Let the element's natural computed value (opacity:1) be the destination. The `class="clip"` already handles show/hide timing. If you need simultaneous opacity animation on nested children (e.g., both parent container and child text fade in), use `tl.fromTo()` with explicit `{opacity:1}` in the target object.

⚠️ **`repeat: -1` is a lint ERROR, not warning** — The HyperFrames linter rejects infinite GSAP repeats. Use a finite integer: `repeat: Math.floor(sceneDuration / cycleDuration) - 1`. For pulsing icons in a 5s scene with 0.7s cycle: `repeat: 6`. For CTA pulse in a 3.5s window with 0.8s cycle: `repeat: 3`. Never use `repeat: -1` in HyperFrames compositions.

## Verification

```bash
npm run render  # Should produce renders/*.mp4
ls -la renders/
# Check file size (> 100KB for real video) and duration:
ffprobe renders/*.mp4 2>&1 | grep Duration
```
