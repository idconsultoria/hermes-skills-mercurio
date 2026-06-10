---
name: daily-briefing-pipeline
description: Design and implement recurring multi-source daily briefing / newsletter pipelines using Hermes cron jobs. Covers the full lifecycle — collector fan-out, cron chaining via context_from, multi-platform sourcing (web, Reddit, HN, X, specialized sites), report structure design, copywriting + humanizer quality pipeline, and HTML-to-PDF delivery via Chromium headless (weasyprint fallback). Trigger on any request for 'daily briefing', 'daily newsletter', 'daily report', 'morning digest', 'curated news', or 'automated briefing'.
metadata:
  version: 1.0.0
  tags: [cron, pipeline, newsletter, briefing, curation, copywriting, reporting]
  related_skills: [humanizer, html-report-hermes, tech-trend-discovery, deep-research, plan]
---

# Daily Briefing Pipeline

Design and implement recurring multi-source daily briefing/newsletter pipelines using Hermes cron. This skill covers the full architecture, from collector cron design through synthesis, quality polish, and delivery.

## When to Load

Load this skill when the user asks to:
- Create a daily news briefing / newsletter / digest
- Automate morning delivery of curated content
- Set up multi-source content aggregation on a schedule
- Build a cron pipeline that collects from several places and synthesizes into one report
- Generate a recurring PDF report from HTML

## Architecture Pattern

The canonical pattern uses **asymmetric fan-out**: multiple lightweight collector crons that each focus on one source type, chained via `context_from` into a single heavyweight synthesis cron.

```
04:00 ── Cron #1: [Source Type A]        \
04:15 ── Cron #2: [Source Type B]         │
04:30 ── Cron #3: [Source Type C]         ├── context_from ──→ 07:00 ── Cron #N: Synthesis
04:45 ── Cron #4: [Source Type D]         │                      Loads: copywriting + humanizer
05:00 ── Cron #5: [Source Type E]        /                      Produces: HTML → PDF → MEDIA: delivery
```

### Why This Architecture

| Approach | Pros | Cons |
|----------|------|------|
| **Single monolithic cron** | Simple to create | Token-heavy; hard to debug; single point of failure |
| **Chained pipeline** (this) | Each cron has clear focus; parallel collection; if one collector fails, others still produce data | More crons to manage; slightly more complex setup |
| **Delegate_task inside one cron** | Parallel collection in one session | Not durable — parent interruption kills children |

### When context_from isn't enough (data too large)

If the combined collector output exceeds ~50KB, don't rely on `context_from` injection alone. Instead:
1. Each collector cron writes its curated output to a file (e.g. `/cron/output/iaf_fonte_tipo.md`)
2. The synthesis cron reads those files with `read_file` and `web_extract` for the raw links
3. `context_from` is used only for lightweight metadata (file paths, success/failure flags, dates)

## Implementation Steps

### Step 1: Define Sources

Categorize sources by trust level and content type:

| Source Type | Examples | Best For | Cron Cadence |
|-------------|----------|----------|-------------|
| **General AI news** | web_search for trending AI news | Breaking stories | ~15 min gap |
| **Specialized newsletters** | therundown.ai, superhuman.ai, importai | Curated deep reads | ~15 min gap |
| **Community forums (Reddit)** | r/artificial, r/LocalLLaMa, r/MachineLearning | Ground-level sentiment, practical tips | ~15 min gap |
| **Community forums (HN)** | news.ycombinator.com | Tech discussion, critical takes | ~15 min gap |
| **Social / X** | web_search for X discussions, trends | Hot takes, practitioner voices | ~15 min gap |

### Step 2: Design Report Structure

The canonical structure (refined through user feedback — see `references/iaf-report-structure.md`):

```
┌─ HEADER ──────────────────────────────┐
│  [NAME] — [SUBTITLE]                  │
│  [DATE]                               │
├─ 🔥 HOT TAKE DO DIA ──────────────────┤
│  1-2 paragraphs. The most important    │
│  story or insight, with voice/opinion. │
├─ 📰 RADAR DE NOTÍCIAS ────────────────┤
│  5-7+ quick items (1-2 lines each)     │
├─ 🎯 DEEP DIVE (2-3) ──────────────────┤
│  Context + analysis + links for        │
│  the most significant stories.         │
├─ 💡 APLICAÇÃO PRÁTICA ────────────────┤
│  Real user cases from forums, with     │
│  links to original discussions.        │
├─ ⚡ PULSO DA COMUNIDADE ──────────────┤
│  Reddit/HN/X sentiment, quotes,        │
│  interesting threads.                  │
├─ 📚 FONTES ───────────────────────────┤
│  Links to all sources cited.           │
└────────────────────────────────────────┘
```

**Key rule from user feedback**: DO NOT include bullet-point highlights at the top. The Hot Take paragraph IS the highlight. The hot take length should vary naturally based on content quality (1-2 paragraphs).

### Step 3: Configure Collector Crons

Each collector uses `cronjob(action='create')` with:
- `schedule`: staggered to avoid overlap (e.g., 15 min apart)
- `prompt`: self-contained instructions for that source type
- `enabled_toolsets`: `["web", "file"]` (lightweight — no browser/delegation needed)
- `skills`: if the collector needs specific extraction patterns, load relevant skills
- No `deliver` set (output goes to context_from, not to user)
- `script` (optional): a data-collection script for deterministic extraction

Each collector should:
1. Search/extract from its source
2. Curate — filter out noise, keep only high-quality items
3. Format output as structured markdown (headings, links, brief summaries)
4. NOT try to write final prose — just collect and lightly curate

**IMPORTANT**: Collector crons run autonomously — no user present. The prompt must be fully self-contained. Include:
- Exact URLs or search queries
- Quality threshold (e.g., "skip anything that would not interest a daily AI professional")
- Output format specification

### Step 4: Configure Synthesis Cron

The synthesis cron uses:
- `schedule`: after all collectors finish (e.g., 07:00)
- `context_from`: list of collector job IDs
- `skills`: `["copywriting", "humanizer"]` (or custom IAF copy skill)
- `enabled_toolsets`: `["file", "web", "terminal"]` (needs weasyprint for PDF)
- `deliver`: auto (delivers to the current chat)
- `model`: override to a stronger model if the briefing needs high-quality synthesis

The prompt should instruct:
1. Read all context_from output (the 5 curated collections)
2. Select the most important 2-3 stories for deep dive
3. Write the Hot Take (1-2 paragraphs, opinionated, with voice)
4. Compile the News Radar (brief items)
5. Extract practical application stories from forum sources
6. Format as the IAF report structure
7. Apply copywriting principles (clarity, specificity, benefits over features, active voice)
8. Apply humanizer pass (strip AI-isms, inject personality, vary rhythm)
9. Render as HTML with visual care (proper typography, spacing, colors)
10. Convert to PDF with Chromium headless (see Step 5; fallback: weasyprint)

### Step 5: HTML to PDF

**Primary: Chromium Headless** (preserves gradients, `-webkit-background-clip: text`, `@page` rules, and all CSS features — use whenever possible)

On ARM64 / no-root environments, download and extract the Debian chromium + chromium-common packages:

```bash
# Setup (one-time)
cd /tmp
apt-get download chromium chromium-common libdouble-conversion3 libharfbuzz-subset0 libminizip1t64 libopenh264-8 libicu76
mkdir -p /tmp/chromium-extracted
for pkg in chromium_*.deb chromium-common_*.deb; do dpkg -x "$pkg" /tmp/chromium-extracted/; done
for pkg in lib*.deb; do dpkg -x "$pkg" /tmp/chromium-extracted/; done
cp /tmp/chromium-extracted/usr/lib/aarch64-linux-gnu/*.so* /tmp/chromium-extracted/usr/lib/chromium/
```bash
# Generate PDF
CHROMIUM=/tmp/chromium-extracted/usr/lib/chromium/chromium
LD_LIBRARY_PATH=/tmp/chromium-extracted/usr/lib/chromium \
  $CHROMIUM --headless --no-sandbox --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="$OUTPUT" "file://$INPUT"
```

**Gradient artifact fix:** When applying `-webkit-background-clip: text` on an `<h1>`, Chromium may render a 1px gradient line above the heading text in PDF output. Wrap the heading text in a `<span>` and apply the gradient to that `<span>` instead of the `<h1>`. See the `html-to-pdf-chromium` skill's Pitfalls section for exact CSS/HTML.

See the `html-to-pdf-chromium` skill for full setup instructions and troubleshooting.

**Fallback: WeasyPrint** (use when Chromium binary is unavailable)

Note: `-webkit-background-clip: text` is NOT supported — gradient titles render as solid color.

### Step 6: Delivery

The synthesis cron's final message should include:
```
MEDIA:/tmp/iaf_20260605.pdf
```

This delivers the PDF as a native file attachment on Telegram.

## Correction Principle

When the user requests a correction to newsletter output, **change ONLY the specific item they mentioned**. Do not:
- Reword other sections or items
- Reformate sections that weren't flagged
- Add/remove/reorder content beyond the explicit request
- "Improve" adjacent parts as a courtesy

If a secondary issue matters, suggest it separately after delivering the correction. Extra changes risk breaking approved content and frustrate the user.

## Copywriting + Humanizer Quality Pipeline

Apply these passes in order during synthesis:

### Pass 1: Copywriting (coreyhaines31/marketingskills)
- Clarity over cleverness
- Benefits over features
- Specificity (numbers, concrete claims)
- Active voice
- One idea per section
- Customer language (not jargon)

### Pass 2: Humanizer (blader/humanizer)
- Strip AI-isms: "delve", "pivotal", "landscape", "testament", "underscore"
- Remove -ing signposting: "highlighting", "underscoring", "showcasing"
- Remove chatbot artifacts: "Let's dive in", "Here's what you need to know"
- Vary sentence rhythm
- Inject personality and opinion
- Avoid em dashes overuse
- Remove soulless hedging
- Final audit: "What makes the below so obviously AI generated?"

### Pass 3: IAF Voice Calibration
- Mix of copywriting (persuasive, clear) + journalistic (informative, structured)
- Portuguese with English technical terms where appropriate
- Beautiful visual facilitation (layout, spacing, typography)
- "Gostosa e impecável" — delightful and impeccable to read

## Verification

Before declaring done:
1. Run the synthesis cron manually: `cronjob(action='run', job_id='...')`
2. Verify the PDF was generated: check file size > 0
3. Verify delivery: check the chat received the MEDIA: file
4. For the first few days, review output quality and adjust source lists or report structure

## Pitfalls

- **context_from data limits**: If collector output > 50KB, the data won't fully inject. Use file-based handoff instead (collectors write to files, synthesis reads them).
- **weasyprint font issues**: System fonts may not have Cyrillic/Japanese glyphs. Use web-safe fonts or Google Fonts via `@import url(...)`.
- **Collector cron silence**: If a collector finds nothing (no trends, no content), it should still output "Nenhum conteúdo relevante encontrado em [fonte]" rather than failing silently — this prevents context_from from injecting empty data.
- **Time zone**: The cron scheduler uses the server's timezone. If the server is UTC and the user wants 07:00 BRT, set schedule to `10:00` UTC (BRT = UTC-3).
- **Model quality**: Synthesis demands a strong model. Use `model` override on the synthesis cron to ensure high-quality output (e.g., Claude Sonnet or GPT-4 class).
- **Watermark/header**: If the PDF is delivered via MEDIA: it arrives as a file. Include metadata (date, issue number) in the HTML so the PDF is self-contained even if downloaded.

## Reference Files

- `references/iaf-report-structure.md`: Exact report structure refined by user
- `references/example-sources.md`: Source categorization by cron
- `references/copywriting-humanizer-workflow.md`: Three-pass quality pipeline (copywriting → humanizer → IAF voice calibration)
- `references/companion-message-format.md`: WhatsApp/Telegram companion message template with emoji rules, scoring-based selection, and bold formatting
