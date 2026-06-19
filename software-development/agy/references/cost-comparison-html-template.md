# HTML Template Reference — Cost Comparison Bar Chart

Complete working template for a mobile-first cost comparison bar chart. This is the production version delivered in the session — copy, adapt data, and use as-is.

## File structure

A single `.html` file with embedded `<style>` and all data in the body. No JS, no external dependencies (except Google Fonts CDN — works fine in offline mode too).

## Key CSS variables to adjust

| Token | Default | What it controls |
|-------|---------|-----------------|
| `max-width: 420px` on `.card` | 420px | Mobile narrow card. Increase to 600–800px for desktop. |
| `font-size: 21px` on `h1` | 21px | Title size. Desktop: 24-27px. |
| `.item { padding: 9px 0 }` | 9px | Row spacing. Desktop: 12-14px. |
| `.track { height: 18px }` | 18px | Bar thickness. Desktop: 20-22px. |

## Data adaptation

The 7-row pattern repeats. To add/remove rows:

1. Copy a `<div class="item">...</div>` block
2. Update: icon, task name, model name, cost value, bar width%, bar color
3. Bar width = (cost / maxCost) × 100, where maxCost is the largest cost value
4. Legend below bars: add/remove `.legend-item` blocks to match model families

## Color mapping (model families)

```
DeepSeek:  #1D4ED8, #2563EB  →  blue
MiniMax:   #0D9488, #0F766E  →  teal
Gemini:    #D97706, #EA580C  →  amber/orange
Claude:    #7C3AED           →  purple
```

## Complete template (abridged)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>Custo por tarefa × modelo ideal</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#F2F3F6; display:flex; justify-content:center; align-items:center; min-height:100vh; padding:16px; }
.card { max-width:420px; width:100%; background:#FFF; border-radius:20px; padding:28px 20px 24px; box-shadow:0 1px 2px rgba(0,0,0,.04),0 8px 24px rgba(0,0,0,.06); }
/* See full working file at /opt/data/kimi-k2.7-vs-claude-gpt.html */
</style>
</head>
<body>...</body>
</html>
```

## Reference file

The production file from this session: `/opt/data/kimi-k2.7-vs-claude-gpt.html`

Use `read_file()` + `patch()` to adapt its data for new comparisons.
