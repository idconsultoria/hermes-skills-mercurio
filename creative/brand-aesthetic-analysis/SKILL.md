---
name: brand-aesthetic-analysis
description: Systematically analyze a product or brand's visual identity through browser inspection and produce a comprehensive style guide / design system documentation as a downloadable file.
trigger:
  - User asks to "analyze the aesthetic" of a brand, product, or website
  - User wants a "style guide" or "design system" document for a brand
  - User asks to deep-dive into visual design, color palette, typography, or component design
  - Comparative analysis of multiple brand identities
---

# Brand Aesthetic Analysis & Style Guide Creation

Systematically inspect a product/brand's visual identity using browser tools and vision analysis, then compile findings into a professional, comprehensive style guide document.

## Workflow

### Phase 1: Scout — Browse Target Pages

Navigate to the primary URLs the user provides. For a product like Hermes Agent, that means:

1. **Landing page** (`/` or `/index.html`)
2. **Feature / download page** (e.g., `/desktop`, `/download`)
3. **Documentation page** (`/docs` or similar)
4. **Parent organization / brand hub** (e.g., `nousresearch.com` for Hermes Agent)

Use `browser_navigate` for each. For pages beyond the initial viewport, scroll down to capture the full layout.

### Phase 2: See — Vision Analysis

For each page, call `browser_vision` with a detailed, structured question that asks for:

- **Color palette**: primary colors, hex codes, background color, accent colors, any gradients
- **Typography**: font families (serif, sans-serif, monospace), weights, sizes, letter-spacing, case conventions
- **Layout**: grid system, columns, max-width, spacing between sections
- **Borders & dividers**: line weights, colors, dashed/solid, border-radius
- **Components**: navigation bar, buttons (primary, ghost, copy), cards, code blocks, tables, callout boxes, terminal mockups, footers
- **Decorative elements**: illustrations (style, technique), icons, watermarks, patterns
- **Interactive states**: hover effects, transitions, animations (inferred from static analysis)
- **Overall philosophy**: brutalism, minimalism, hacker-chic, academic, corporate, etc.

```python
# Example detailed vision question (adapt per page):
browser_vision(question="Describe the full [page name] design in detail: \
  color palette (hex codes if visible), gradients, glow effects, borders, \
  typography (headings, body, code fonts), spacing, layout grid, decorative \
  elements, icons, neon/cyber aesthetic, glassmorphism, any animated elements, \
  and the overall visual philosophy.")
```

**Important**: If the vision model is unavailable (503 error), pause and retry — don't skip the visual analysis. The vision data is the core of this skill.

### Phase 3: Dive — Component-Level Inspection

After the broad visual scan, go deeper on specific elements:

- **Interactive components**: click buttons, open dropdowns ("More Details", expandable sections), toggle dark mode
- **After interaction**: call `browser_vision` again to see what changed
- **Multiple viewports**: the page may differ at different scroll positions; scroll down and re-analyze
- **Documentation pages**: toggle light/dark mode and analyze both systems

### Phase 4: Organize — Build the Style Guide Structure

Structure the guide with these sections (adapt as appropriate for the brand):

```
1. **Philosophy** — The 'why' behind the design: what aesthetic tradition, what values
2. **Color Palette** — All color systems (light, dark, accent, semantic) with exact hex codes, 
   proportion/usage rules, where each system applies
3. **Typography** — Font families per use case, scale, weights, letter-spacing, 
   case conventions (uppercase vs sentence)
4. **Layout & Grid** — Grid columns, max-widths, spacing vertical/horizontal, 
   ASCII block diagram of the page structure
5. **Navigation** — Navbar types, sidebar anatomy, responsive behavior
6. **Components** — Detailed breakdown of every reusable component:
   - Code blocks, buttons, cards, tables, callout boxes, terminal mockups, 
     collapsible sections, footers
   - Each with: visual description, dimensions, colors, typography, states
7. **Iconography & Illustrations** — Illustration style (engraving, halftone, 
   minimalist, etc.), icon set approach (SVG, emoji, custom), what's deliberately absent
8. **Interactions & Animation** — Hover states, transitions, scroll behavior, 
   loading states, error states — with duration and easing when known
9. **Voice & Tone** — Writing style: direct/technical, anti-hype, uppercase conventions, 
   language patterns, cultural references
10. **Design Principles** — Formulate 5-8 principles based on observed patterns
```

### Phase 5: Produce — Deliver the File

Create a polished markdown file at `/opt/data/<brand>-design-style-guide.md` and deliver via `MEDIA:<path>`.

```python
# Style guide conventions
- Use a table of contents at the top with anchor-linked sections
- Use ASCII diagrams for layout explanations (box-drawing chars)
- Use component tables with visual descriptions, colors, dimensions
- Include practical reference data (actual hex codes, font names)
- Add design principle formulations in the brand's language
- Include a "quality checklist" appendix for implementation reference
```

**File conventions:**
- Path: `/opt/data/<brand-slug>-design-style-guide.md`
- Target size: 25-45 KB for a thorough deep-dive
- Include a clear header with version/date and source URLs
- Use `---` thematic breaks between major sections

## Pitfalls

- **Vision model may be unavailable** (503). Retry once; if still down, use the snapshot data and your own reasoning to infer visual details. You know common design patterns — extrapolate from snapshot structure + your knowledge of the brand.
- **Don't trust vision analysis blindly**. It may misidentify colors, fonts, or effects. Cross-reference with the page source/snapshot when possible. Treat vision as "what the model sees," not ground truth.
- **Interactive dropdowns may be JS-dependent**. Click via browser_click with the ref ID from the snapshot. If it doesn't expand, try a different element (the arrow vs the text). Some dropdowns use CSS-only solutions that need specific triggers.
- **Some color values may be approximate** (vision models round hex codes). Note "~" or "likely" for uncertain values. Only use exact hexes you're confident about.
- **Avoid making claims about animations** from static screenshots unless you actually trigger and observe them. Prefer "suggested" / "likely" language for inferred states.
- **Font identification via vision is unreliable** — note "appears to be" / "resembles" / "likely". Check the page source for `@font-face` or Google Fonts CSS if possible.
- **Don't fabricate** when a page is inaccessible (e.g., login wall, 404). Note the blocker honestly and describe what you can see.
- **Different brand surfaces may use different design systems** (marketing vs docs). Document them as separate systems (e.g., System A, System B).

## User Preferences (gustavomello9600)

This user applies to the style guide output format:
- **Language**: Brazilian Portuguese — write the entire guide in PT-BR
- **Format**: Comprehensive, deep-dive structure with 10-15 sections
- **Style**: Tables, ASCII diagrams, hex codes, practical reference data
- **Delivery**: Always a downloadable file via MEDIA: path
- **Detail level**: Exhaustive — every component disassembled
- **Design principles**: Translate to Portuguese with the brand's original spirit preserved

## Example Outputs

See this session's output at `/opt/data/hermes-agent-design-style-guide.md` for a complete reference example (39 KB, 12 sections + 2 appendices).
