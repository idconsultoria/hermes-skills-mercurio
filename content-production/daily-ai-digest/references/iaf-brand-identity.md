# IAF Brand Identity — "O Sintetizador Orgânico"

Full design system reference. The canonical source is `/opt/data/references/iaf-manual-identidade.md`.

## Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#080d0f` | Page background (chumbo profundo) |
| `--bg-secondary` | `#0d1519` | Cards, containers |
| `--accent-primary` | `#0da69e` | Teal — section titles, borders, tags |
| `--accent-hover` | `#00ffd5` | Neon — highlights, CTAs, emphasis |
| `--accent-terracotta` | `#e07a5f` | Analysis tags, biz tags |
| `--accent-sage` | `#8f9e8b` | Product tags, creative tags |
| `--accent-amber` | `#ffb700` | Alert tags, community tags |
| `--text-primary` | `#f3f6f6` | Body text (off-white) |
| `--text-secondary` | `#8a9d9f` | Secondary text, metadata |

## Typography

| Role | Font | Weight |
|------|------|--------|
| Logo / giant title | Outfit | 900 |
| Section titles | Outfit | 700 |
| Body / paragraphs | Inter | 300-500 |
| Code, tags, metadata | Fira Code | 400-700 |

## Visual Atmosphere

- **Grid background**: 30px repeating grid at `rgba(13,166,158,0.02)` opacity
- **Ambient glow**: Radial gradient teal glow in top-right corner
- **Ambient curve**: SVG Bézier path crossing the page at `opacity: 0.08`
- **Section dividers**: Linear gradient line that fades out `rgba(13,166,158,0.3) → transparent`
- **Cards**: `border-radius: 10-14px`, `border: 1px solid var(--border-color)`, hover glow effect
- **Hot take box**: Left accent border (3px neon teal), gradient background

## Component Order

1. Header (brand + metadata right-aligned)
2. Editorial / Hot Take (bordered box, left accent)
3. Análise (deep-dive cards, stacked)
4. Radar (compact news grid)
5. Pulso da Comunidade (expanded cards + compact grid)
6. Aplicação Prática (recipe card with benefit box)
7. Footer (left: name, center: sources, right: "Gerado por Hermes Agent")

## PDF-Specific

- Use `@page { size: A4; margin: 1.5cm 1.8cm; }` — not `margin: 0` + padding, which breaks weasyprint
- Title uses `color: var(--accent-primary)` (solid) — weasyprint does not support `-webkit-background-clip: text`
- Add `page-break-inside: avoid` to `.hot-take-box`, `.deep-dive-card`, `.app-card`
- Use pt or mm units, not px, for reliable print output
