---
name: cost-comparison-chart
description: Generate cost comparison bar charts as self-contained HTML — CSS-only bars, honest linear scale, mobile-first layout, storytelling structure. For comparing AI model costs per task, deliverable via Telegram (screenshot + file).
---

# Cost Comparison Bar Chart

Generate clean consulting-style bar charts comparing costs across categories (typically AI model pricing by task type). Self-contained HTML, no JS charting libraries, renders in any browser.

## When to use

- User asks to compare costs of AI models per task
- User has a table of model × task × cost data and wants a visual
- User needs a chart deliverable via Telegram (screenshot + HTML file)
- Values span a wide range (10× to 100×+ between cheapest and most expensive)

## Technique: CSS-only horizontal bars

Chart.js often fails in headless Chrome with `logarithmic` + `bar` types. Use **pure CSS horizontal bars** instead.

Each bar fill gets inline style `width: <pct>%; background: <color>;` where pct = (cost / maxCost) × 100.

**Rules:**
- Do NOT set `min-width` on `.fill` — let the bar be tiny if the data says so. Honest representation.
- Sort by cost ascending (cheapest on top). Builds narrative tension from "nearly free" → "premium."
- Use `flex: 0 0 360px` on desktop bar track, `flex: 1` (full-width) on mobile.

## Data structure

Each row uses stacked layout (label above bar) for mobile-readability:

```html
<div class="item">
  <div class="item-top">
    <span class="group">
      <span class="ico">💻</span>
      <span class="task">CÓDIGO</span>
      <span class="model">DeepSeek V4 Pro</span>
    </span>
    <span class="cost">R$ 0,11/M</span>
  </div>
  <div class="item-bar">
    <div class="track"><div class="fill" style="width:0.76%;background:#1D4ED8;"></div></div>
  </div>
</div>
```

## Color coding by model family

```css
DeepSeek:  #1D4ED8 (dark blue), #2563EB (blue)
MiniMax:   #0D9488 (teal), #0F766E (dark teal)
Gemini:    #D97706 (amber), #EA580C (orange)
Claude:    #7C3AED (purple)
/* For other families, pick distinct hues */
```

Include a compact color legend (<5 items) below the bars.

## Storytelling structure

1. **Title:** Provocative, narrative hook — "💰 O custo certo para cada tarefa"
2. **Subtitle:** State metric explicitly + key insight: `"Custo por milhão de tokens (R$) — o modelo que atinge a qualidade necessária pelo menor custo. De {cheapest} (R$ X) a {priciest} (N×)"`
3. **Column header:** Subtle `"Tarefa · Modelo / R$ / M tok"` row 
4. **Bars:** Linear scale, sorted ascending, one per item
5. **Legend:** Color dots per family at bottom
6. **Annotation box:** Explains the choice logic per model. Highlight the cost gap (e.g. "132× difference"). Add scale-honesty note: "Barras em escala linear — o comprimento reflete exatamente o custo relativo."

## Mobile-first layout

- Card max-width: 420px (fits phone screen in Telegram)
- Stacked per-item: label row (icon + TASK · model | cost) + bar row (full-width 18px)
- Font sizes: 14px labels, 16px cost (Space Mono), 21px title
- Padding: 28px 20px card, 9px per item

## Pitfalls

- **Chart.js logarithmic bug:** Don't use Chart.js with `type: 'bar'` + `logarithmic` scale in headless — renders empty. CSS bars always work.
- **min-width ruins honesty:** Do not add min-width to fills. Tiny bars ARE the story of cost efficiency.
- **Tables below charts:** User rejects tables under the chart. Data lives in the bars + labels.
- **Unit ambiguity:** Always label /M (per million) in subtitle AND every cost value.
- **Model names in title:** Bad. Title is the narrative hook. Models go in the rows.
- **Equal visual weight:** Task name + model name should have similar prominence. Use uppercase bold for tasks, regular gray for models.

## Verification

- Open HTML in browser, take screenshot via `browser_vision`
- Confirm: all bars visible (including tiny ones), colors match legend, metric unit present, text readable at phone-screen size
- Test: send MEDIA:screenshot_path + MEDIA:html_path in response
