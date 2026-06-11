# Brand Color Adaptation — Web to Motion Graphics

> When a brand style guide contains web-optimized colors, this reference provides
> a repeatable recipe for deriving a motion-graphics palette that is more impactful
> on screen while staying in the same hue family.

## Principle

**Push saturation and lightness; never change hue.** The brand's colors represent
its identity. Motion graphics need deeper darks for contrast, brighter highlights
for glow/particles, and higher saturation for impact at 30fps. Derive, don't invent.

## Recipe

### Step 1 — Extract the brand's base colors
From the style guide, identify:
- Primary color (the brand's "anchor" — usually the logo color)
- Accent color (the contrast — buttons, highlights)
- Neutral dark (background or heading color)
- Neutral light (card backgrounds, body)

### Step 2 — Derive the video palette

| Base (Web) | Operation | Video Result | Usage |
|-----------|-----------|-------------|-------|
| Primary (#1e87f0) | Lightness -40, saturate +10% | Deep navy (#001B3D) | Scene backgrounds |
| Primary (#1e87f0) | Lightness +25, saturate +20% | Neon cyan (#00D2FF) | Highlights, glow, particles, icons |
| Accent (#ff9f00) | Keep as-is, reduce usage | Same orange | Small accents only (logo mark, dividers) |
| Dark neutral (#1D1D1B) | Lightness -15 | Near-black (#0A0A1A) | Dramatic scenes (security) |
| Light neutral (#f8f8f8) | Keep pure white | #FFFFFF | All body text |
| Primary (#1e87f0) | Opacity 0.1–0.2 | rgba(0,210,255,0.15) | Grid lines, secondary elements |

### Step 3 — Define 2 additional derived colors

| Name | Derivation | Hex |
|------|-----------|-----|
| Mid-tone | Halfway between navy and neon | #003366 |
| Dark glow | Neon at 30% opacity | rgba(0,210,255,0.3) |

### Step 4 — Document the mapping

Add a `### Paleta do Vídeo` subsection to the style guide so future agents
(and cron jobs recreating the video) have the exact mapping. This is the
artifact the session produced at `/opt/data/ilognet-style-guide.md` §3.

## Anti-patterns

- **Do NOT copy the web primary color directly as a background.** `#1e87f0` as a
  full-screen background burns the eyes. Deepen it.
- **Do NOT introduce new hue families.** If the brand is blue+orange, don't add
  green or purple particles just because they "look cool."
- **Do NOT use gray for body text on dark backgrounds.** Dark backgrounds need
  white text. Gray is for web forms, not video overlays.
- **Do NOT tint body text.** White stays white. Tinting body text (e.g. cyan
  body text) reduces readability at 30fps.

## Verification checklist

- [ ] Video palette has exactly the same hue angles as the web palette
- [ ] Darkest color is deep enough for full-screen backgrounds (L < 15)
- [ ] Brightest accent is bright enough for glow/particles (L > 60, S > 80)
- [ ] White text is `#ffffff`, not `#f8f8f8` or gray
- [ ] At most 5 colors in the final video palette (including white)
