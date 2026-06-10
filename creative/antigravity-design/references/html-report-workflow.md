# HTML Report Generation with agy — Hermes Style Guide

## When to Use

User requests a financial/technical report as HTML (cost analysis, breakdown, metrics dashboard). Always delegate visual design to agy — don't write the HTML directly.

## Standard Workflow

### 1. Prepare the Prompt File

Write a `.md` prompt file with ALL data inline. agy cannot read files from disk.

```bash
# SCP prompt to host (use SSH alias, not raw IP)
scp -F ~/.ssh/config /tmp/prompt.md oracle-host:/tmp/prompt.txt

# Execute agy (--print takes a string arg, NOT piped input)
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --print "$(cat /tmp/prompt.txt)"'

# Copy result back
ssh oracle-host 'sudo cp /home/ubuntu/<output>.html \
  /home/ubuntu/selfhost/hermes/data/'
```

### 2. Prompt Structure

The prompt must contain:
- **Data tables** with exact numbers — don't make agy compute
- **Section order** — executive summary first, detail after
- **Design constraints** — Hermes Style Guide specs below

### 3. Hermes Style Guide (for agy prompts)

```css
/* Core palette */
--primary: #0000FF;
--blue-bg: #F0F5FF;
--blue-border: #CCD9FF;
--blue-text: #1A237E;
--gold-accent: #E8B830;
--green-accent: #059669;
--text-dark: #1C1C1E;
--text-muted: #666680;

/* Fonts */
Headings: 'Spectral', Georgia, serif
Numbers/Code: 'Space Mono', monospace
Body: 'Inter', sans-serif
```

### 4. Executive Summary Structure (insert between Hero and Section 1)

```
<div class="executive-summary"> (position:relative; margin-top:-40px; z-index:2)
  └─ <h2>📌 Sumário Executivo</h2>
  └─ 4 KPI cards (grid 4-col)
  └─ Tabela de tokens: agente/modelo | cache hit | cache miss | output | total | hit rate | custo
  └─ Callout destacado com total geral de tokens (Space Mono, gold border)
  └─ Key insights (grid 2×2, cards com borda lateral colorida)
```

### 5. Token Breakdown — Essential Metric

Always include this table. The user considers it a first-class metric:

| Agente / Modelo | Cache Hit (input) | Cache Miss (input) | Output | Total Tokens | Hit Rate | Custo |
|---|---|---|---|---|---|---|
| Hermes — DS V4 Flash | 242.225.664 | 1.985.561 | 791.049 | 245.002.274 | 99,2% | $1,18 |

Plus a callout/callout:
```
📊 Total de Tokens: 279.866.333
  Cache Hit:  275.692.847  (98,98%)
  Cache Miss:  2.844.374  (1,02%)
  Output:      1.329.112
  → Cache economizou ~36× o custo ($75 sem cache vs $2,03 com cache)
```

### 6. DeepSeek Pricing Reference

| Modelo | Input Miss | Input Hit | Output | Cache Hit Rate |
|--------|-----------|-----------|--------|----------------|
| V4 Flash | $0,14/M | $0,0028/M | $0,28/M | 98% |
| V4 Pro | $0,435/M | $0,003625/M | $0,87/M | ~90% |

### 7. Delivery

After agy generates the HTML, zip it or rename to .txt (Telegram blocks .html):
```bash
python3 -c "import shutil; shutil.make_archive('report', 'zip', '.', 'report.html')"
```
Send with `MEDIA:/path/to/report.zip`

## Pitfalls

⚠️ **Timeout:** Always use `timeout 300` for multi-section reports. The default 120s is not enough.
⚠️ **Data accuracy:** Include ALL numbers inline in the prompt. agy may estimate/hallucinate if data is missing.
⚠️ **No file reading:** agy --print mode cannot read files — embed everything in the prompt text.
⚠️ **No follow-ups:** --print mode is one-shot. If agy gets something wrong, fix the prompt and retry.
⚠️ **--print takes a string argument:** Do NOT use `cat prompt | agy`. Use `agy --print "$(cat prompt.txt)"`.
⚠️ **Token table columns:** Must be: Cache Hit | Cache Miss | Output | Total | Hit Rate | Custo. Don't omit hit rate.
