# Layout Audit with agy (Gemini) for HyperFrames Compositions

## When to use

After writing `index.html` for a HyperFrames video but **before rendering**, run a layout audit with agy on the Oracle host. The audit catches font sizing, spacing, and hierarchy problems that are invisible in HTML source but obvious once rendered.

This is especially critical for:
- **Vertical 9:16 ads** (768×1280) — font sizes that look fine in code are illegible on a phone
- **Brand videos with many elements** — visual hierarchy collapses when everything is too small
- **First-time resolution** — anytime you're composing for a new aspect ratio

## How to run

### Prerequisites
- agy installed and authenticated on Oracle host (`ssh oracle 'which agy'`)
- HTML composition uploaded to host: `scp index.html oracle:/home/ubuntu/ilognet-video-review.html`

### Audit command
```bash
ssh oracle "timeout 300 env HOME=/home/ubuntu /home/ubuntu/.local/bin/agy --dangerously-skip-permissions --print 'You are a senior motion graphics designer and layout auditor. Review /home/ubuntu/ilognet-video-review.html — an HTML+GSAP composition for a [N]-second vertical video ad ([W]×[H], 9:16).

Focus your analysis on:
1. Font sizes — are they readable at this resolution on a smartphone screen?
2. Element positioning — centered, visible, no clipping?
3. Visual hierarchy — clear focal points in each scene?
4. Spacing and proportions — enough breathing room? Images/logos appropriately sized?
5. Layout balance — does each scene fill the canvas without large empty areas?

For each scene, identify specific problems and suggest exact CSS fixes. Be brutally honest.
Output as structured markdown in Portuguese (user speaks pt-BR).'
```

### Retrieve the report
```bash
ssh oracle 'cat /home/ubuntu/.gemini/antigravity-cli/brain/<uuid>/layout_audit_report.md'
```

agy saves the report to `~/.gemini/antigravity-cli/brain/<uuid>/layout_audit_report.md`. The UUID is in the output.

### Apply findings
agy's recommendations typically fall into two categories:
1. **Font size bumps** — 14px→22px, 20px→32px, 30px→48px. These are always valid for vertical mobile video.
2. **Position adjustments** — `top: X%` changes to redistribute elements vertically and fill empty space.

Apply changes with `patch` tool (targeted) or regenerate the HTML.

## What agy catches that linting doesn't

The HyperFrames linter checks syntax and determinism. It does NOT check:
- Whether text is readable at the target screen size
- Whether the visual hierarchy is effective
- Whether there's too much empty space
- Whether logos are recognizable at their rendered size
- Whether the URL/CTA is prominent enough for conversion

agy fills this gap as a "design QA" step between `npm run check` and `npm run render`.

## Creative Pass (After Audit — Optional but High-Impact)

Once the audit fixes are applied and rendering succeeds, give agy a **second pass with full creative freedom** to elevate the composition from "correct" to "polished motion graphics":

```bash
ssh oracle "timeout 600 env HOME=/home/ubuntu /home/ubuntu/.local/bin/agy --dangerously-skip-permissions --print 'You have complete creative freedom. The file at /home/ubuntu/ilognet-video-review.html is a video ad composition (HTML+GSAP→MP4, [W]×[H]).

Your audit already fixed font sizes and positioning. Now do a CREATIVE PASS — unrestricted. You can:

1. Restructure any scene — change layout grid, add/remove elements, reorder content
2. Enhance visual design — add gradients, overlays, particle effects, glow, animated dividers
3. Refine GSAP animations — improve timing curves, add stagger, create dynamic entrances
4. Add visual elements — progress bars, countdowns, glass panels, radar sweeps, data packets
5. Improve typography — make it look like a professional ad, not a webpage
6. Adjust colors within the brand palette creatively
7. Add anything that makes the video more polished, modern, and impactful

Rules:
- Keep duration, scene count, resolution, GSAP-based
- Keep brand colors but use them more creatively
- Keep clip/data-* attributes for HyperFrames compatibility
- No Math.random(), Date.now(), or network fetches
- Keep GSAP selectors scoped with body prefix
- The HTML must remain valid

Edit the file directly. After editing, describe what you changed and why.'"
```

### What to expect from the creative pass

agy typically adds 200-300 lines of visual complexity. Common additions:

| Scene | Typical Creative Additions |
|-------|---------------------------|
| Opening | Floating orbs, multi-color particles, staggered word animations |
| Feature | Glass panels, count-up counters, staggered icon ring reveals |
| B2B | Side-by-side glass cards, cyber data packets along grid lines |
| Partners | Individual glowing capsules for each logo, console/UI framing |
| Security | Rotating radar sweep background, laser scanner beam crossing shield |
| Closing | Glowing pill-shaped CTA button, Instagram as badge capsule |

### Creative pass results (real example: 30s Ilognet ad)

- HTML grew from 391 to 669 lines (+278 lines of visual enhancements)
- Output grew from 1.5MB to 2.5MB (3× visual density increase vs original)
- Render time increased proportionally (~2.7 min vs ~1.5 min)

**Rule of thumb:** audit first (fix blocking issues), creative second (add polish), focused-bug-fix third (user corrections). Never creative-pass before audit — you'll build beautiful invisible text. Never skip the bug-fix pass when the user gives specific feedback — direct agy to fix exactly those elements, not redesign everything.

### Focused Correction Pass (After Creative — When User Reports Specific Bugs)

After the creative pass, the user will review the rendered video and report specific issues. This is a **third pass** with tightly scoped prompts. The pattern:

1. User reports exact issues (e.g., "the aura looks amateur", "Wi-Fi icon ugly", "cards spill outside panel")
2. You inspect the HTML to identify the element IDs involved
3. You craft a prompt for agy that lists ONLY those elements and their fixes — do NOT give creative freedom again
4. agy edits the file surgically, preserving everything else
5. You verify the fixes were applied (`scp` back, `grep` key lines)

**Prompt template for focused corrections:**
```bash
ssh oracle "timeout 600 env HOME=/home/ubuntu /home/ubuntu/.local/bin/agy --dangerously-skip-permissions --print 'Focused correction pass on /home/ubuntu/ilognet-video-review.html. Fix these SPECIFIC issues — do not redesign the whole video, just fix what is listed:

BUG 1 — <description>. <element ID>. <what is wrong>. <desired fix>.

BUG 2 — ...

GENERAL IMPROVEMENTS:
<N>. <spacing/hierarchy concern across all scenes>.

Edit the file directly. Keep all existing data-* attributes, clip classes, track indices, and GSAP script intact. Only change HTML element styles and positioning.'"
```

**Verification after each pass:**
```bash
# Copy back
scp oracle:/home/ubuntu/ilognet-video-review.html /opt/data/ilognet-video/index.html

# Spot-check fixes were applied
cd /opt/data/ilognet-video
grep -n '<element-id>' index.html  # verify the changed lines
npx --yes hyperframes@0.6.88 lint 2>&1 | grep 'error\|◇'  # must be 0 errors
```

**Real example (30s Ilognet ad, third pass):**
- User reported: glow looks amateur, Wi-Fi icon ugly, streaming logos spill outside glass panel, spacing issues
- agy prompt listed 4 specific bugs + general improvements, all with element IDs
- agy applied: radial-gradient glow, redesigned Wi-Fi SVG (stroke-based, 200x200 viewBox), recalculated S4 panel to 500px height with 45px margins, adjusted title-subtitle proximity across all scenes
- Result: 2.4MB output, all bugs resolved in one pass

**Original** (written with skill's old font size table, 28-36px titles):
- Logo 260px, titles 30-32px, body 14-16px, URL 14px
- Result: all text invisible or illegible on smartphone

**agy audit findings:**
- 17 issues: 11 blocking (illegible text), 6 cosmetic (proportions)
- Logo → 380px, titles → 48-56px, subtitles → 26-32px, URL → 30px bold cyan
- Empty 35-45% vertical space at the bottom of each scene needed redistribution

**After fixes:** 986KB output (vs 407KB before — 2.4× bigger because text content adds visual complexity).
