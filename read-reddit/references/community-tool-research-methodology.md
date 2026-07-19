# Community Tool Research Methodology

Proven multi-source pipeline for researching AI tool recommendations from online communities. Developed and validated during tool comparison research sessions.

## When to Use

When the task is "find the best [type of tool] recommended by real users in [communities]" — tool comparisons, market landscaping, competitive analysis through the lens of actual user sentiment rather than vendor marketing.

## The Pipeline (5 Steps)

### Step 1: Reddit RSS — Surface-Level Discovery

Pull hot/top posts from relevant subreddits to understand what the community is currently discussing.

**Subreddits to target by topic:**
| Topic | Primary Subreddits | Secondary |
|---|---|---|
| AI Chat/Assistants | r/ChatGPT, r/ClaudeAI, r/artificial | r/LocalLLaMA, r/singularity |
| AI Images | r/Midjourney, r/StableDiffusion | r/StableDiffusion, r/aiArt |
| No-Code/App Building | r/nocode, r/webdev, r/learnprogramming | r/SaaS, r/startups |
| AI Video/Avatars | r/artificial, r/aivideo | r/runwayml |
| Productivity | r/productivity, r/ChatGPT | r/Notion, r/ObsidianMD |

**Feed strategy:**
- Start with `top/.rss?t=year&limit=10` — most reliable, least rate-limited
- Fall back to `hot/.rss?limit=10` if you need recency over relevance
- Expect 429s from some subreddits (see Pitfall #12 in SKILL.md)

### Step 2: HN Algolia API — Developer/Technical Perspective

Complement Reddit's general-user sentiment with HN's developer-heavy viewpoint.

```bash
curl -sL --max-time 15 \
  "https://hn.algolia.com/api/v1/search?query={keyword1}+OR+{keyword2}+{year}&tags=story&hitsPerPage=15"
```

**Key patterns:**
- Use `+OR+` between alternative tool names to catch comparisons
- Add `+2025+2026` to filter for recent discussions
- The `tags=story` filter excludes comments — for thread discussions, also query with `tags=comment`
- API returns JSON with `points` (upvotes), `num_comments`, `created_at` — these proxy community signal strength
- **Do NOT use the browser-based hn.algolia.com interface** — the JS search often returns 0 results; use the API directly via curl

### Step 3: web_search — Discover Independent Comparisons

Once you know the key players from Steps 1-2, search for comparison articles.

**Query template:**
```
"{Tool A} vs {Tool B} {year} comparison {Reddit | review}"
```

**Why this works:** Independent bloggers and review sites produce detailed head-to-head comparisons that synthesize community sentiment. They're not rate-limited and often cite Reddit/HN threads directly.

**Signals to look for in search results:**
- URLs from `.dev`, `.ai`, `.co` domains (tool-focused blogs)
- Titles containing "vs", "comparison", "tested", "ranked"
- Descriptions mentioning specific model versions or pricing

### Step 4: web_extract — Deep Content Retrieval

Extract the full content of the best comparison articles found in Step 3.

**Selection criteria for which URLs to extract:**
- Articles that mention multiple tools (comparisons, not single-tool reviews)
- Posts with version/date specificity (e.g., "2026", specific model numbers)
- Content that includes pricing, feature tables, or "best for" recommendations
- Articles citing community sources (Reddit, HN, G2 reviews)

**Extract in parallel** — up to 5 URLs per web_extract call to save rounds.

### Step 5: Synthesize with Consensus Classification

Classify community sentiment for each tool into one of three tiers:

| Tier | Portuguese Label | Meaning |
|---|---|---|
| **CONSENSUS** | CONSENSO | Clear winner — recommended by multiple independent sources with minimal dissent |
| **DIVIDED** | DIVIDIDO | Strong proponents and detractors — tool is polarizing or use-case-dependent |
| **NICHE** | NICHO | Recommended only for specific use cases — not a general recommendation |

**Classification rules:**
- CONSENSO requires at least 2 independent sources (one can be a blog citing communities)
- DIVIDED if Reddit threads show mixed upvote ratios (<70% positive) or HN comments are split
- NICHE if consistently qualified with "only if you need X" or "not for beginners"

## Output Format

Reports should use this structure:

1. **Sumário Executivo** — One-line recommendation per category
2. **Per-category breakdown** — Each tool gets:
   - 🏆 emoji + name + consensus label
   - "O que a comunidade diz" — verbatim or paraphrased community quote with source link
   - Prós/Contras in bullet form
   - Preço, versão gratuita, nível de consenso
3. **Tabela comparativa** — Side-by-side at end of each category
4. **Stack recomendado** — Free and paid tier recommendations
5. **Fontes Principais** — Numbered list of all source URLs used

## Fallback Order

When a source fails, pivot in this order:
1. Reddit RSS 429 → `top/.rss?t=year` variant → `web_search site:reddit.com` → skip subreddit
2. HN Algolia empty → broader search terms → search comments instead of stories → skip HN
3. web_search empty → retry with different keyword combination → use browser_navigate directly → skip
4. web_extract anti-bot → try browser_navigate to the same URL → skip the source

## Real Session Example

Session from 2026-07-15: Researched "melhores ferramentas de IA para não-programadores" across 5 topics. Encountered rate limiting on r/ClaudeAI, r/Midjourney, r/StableDiffusion (HTTP 429). Pivoted to web_search for blog comparisons, extracted 12 articles via web_extract. Produced a 407-line Portuguese report with 15+ source citations. Full pipeline took ~20 tool calls across Reddit RSS, HN API, web_search, and web_extract.
