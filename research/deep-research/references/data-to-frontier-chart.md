# Data-to-Frontier-Chart Workflow

Compile numerical data from multiple web sources and generate a scatter plot with a convex upper-envelope frontier. Proven for model-benchmark analysis; generalizable to any metric-vs-scale relationship.

## When to use

- You have a **score/ranking** (y) and a **size/cost** (x) for each entity
- Data is scattered across multiple web sources (leaderboard + spec tables)
- Goal: show the "maximum achievable y at each x" — the efficient frontier

## Pipeline

### Phase 1: Extract numeric scores from a leaderboard

For SPA websites (like artificialanalysis.ai), use browser console JavaScript:

```js
// Extract model → score pairs from the visible table
const t = document.querySelector('table');
const rows = t.querySelectorAll('tbody tr, tr');
const data = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 4) {
    const name = cells[0].textContent.trim();
    const score = parseInt(cells[3].textContent.trim()); // adjust column index
    if (name && !isNaN(score)) data.push({name, score});
  }
});
JSON.stringify(data);
```

Run in browser_console(expression="..."). Get slices if the table is long (data.slice(0, 60), data.slice(60, 120) etc.).

### Phase 2: Extract parameter/size data from a catalog site

For sites like llm-evolution.com (SPA with expandable family sections):

1. Expand all families: use browser_console JS to find clickable headers (cursor:pointer + ▼) and `.click()` them
2. Extract table rows with model name + parameters:

```js
const tables = document.querySelectorAll('table');
const models = [];
tables.forEach(table => {
  const rows = table.querySelectorAll('tbody tr, tr');
  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 2) {
      const model = cells[0].textContent.trim();
      const params = cells[1].textContent.trim();
      if (model && params && params !== 'Undisclosed') {
        models.push({model, params});
      }
    }
  });
});
JSON.stringify(models);
```

### Phase 3: Cross-reference by model name

Not all model names match exactly between sources. Strategy:
- Build a CURATED list by hand: manually map leaderboard names → parameter data
- Prioritize **confirmed** params (official specs). Mark estimated params with a flag.
- For undisclosed params on closed models: use industry leaks, bandwidth analysis, or academic estimates. Annotate as `(est.)`.
- For MoE models: use **total** parameters (not active) for the x-axis, since that's the model's full footprint. Note active params in the label if helpful.

### Phase 4: Build the frontier (upper convex envelope)

```python
import numpy as np

# Dataset: (params_B, score) pairs, deduplicated
param_max = {}
for params, score in data_pairs:
    if params not in param_max or score > param_max[params]:
        param_max[params] = score

# Frontier: monotonic increasing line (params → max score)
frontier = []
for p in sorted(param_max.keys()):
    s = param_max[p]
    if not frontier or s > frontier[-1][1]:
        frontier.append((p, s))
```

### Phase 5: Generate the chart (matplotlib)

Requirements: `venv` (system python3 is PEP 668-managed), `matplotlib`, `scipy`.

```bash
python3 -m venv /opt/data/venvs/chart
/opt/data/venvs/chart/bin/pip install matplotlib scipy
```

Key chart elements:
- **Log scale** on x-axis (parameters span 3+ orders of magnitude)
- **Scatter points** colored by category (open vs closed, confirmed vs estimated)
- **Frontier line** (gold/amber, thick) connecting upper-envelope points
- **Fill under frontier** (same color, very low alpha)
- **Annotations** with leader lines for notable models
- **Legend**, **title**, **subtitle** (source + date)

Implementation notes:
- Use `facecolor='#0D1117'` for dark theme, `plt.style.use('dark_background')`
- Set `ax.set_xscale('log')` with custom ticks at powers of 3: `[0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000]`
- Labels with `ax.annotate(..., arrowprops=dict(arrowstyle='->'))` and hand-tuned offsets to avoid overlap
- Save as PNG with `dpi=200` for Telegram delivery (MEDIA: path)

### Phase 6: Deliver

- Send the PNG with a MEDIA: tag in the response
- Include structured summary: the frontier data as a table (params → score → model name), key insights, and methodology caveats

## Pitfalls

- **Model name mismatches**: The same model appears with different names across sources (e.g. "GPT-5.5 (xhigh)" vs just "GPT-5.5"). Build your mapping manually; automated fuzzy matching is unreliable.
- **SPA truncation**: Some sites only load the first N rows. Scroll or use JS to click "Show more" / pagination before extracting.
- **Closed model params**: Treat estimated parameters with an asterisk. Mark them clearly on the chart and explain the source of the estimate in the text.
- **Matplotlib venv**: Always check for PEP 668 issues. Use a dedicated venv.
- **Emoji glyphs**: matplotlb's default font (DejaVu Sans) doesn't support emoji. Avoid them in annotations, or switch to a font that does.
- **Font warnings**: Unicode glyph warnings in matplotlib are cosmetic. They don't affect the output PNG, but to suppress them, use plain ASCII in all annotations.
- **Convex hull ≠ upper envelope**: `ConvexHull` from `scipy.spatial` gives the full hull (both upper and lower). You need to extract only the upper part by sorting by x and keeping only points where y is monotonic increasing. This is simpler than a true convex hull algorithm.
