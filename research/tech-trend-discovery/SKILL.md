---
name: tech-trend-discovery
description: "Discover what tech and AI communities discuss — trending topics and hot discussions.

Load this skill when you need to find current tech conversations. Covers Reddit sources and Hacker News Algolia API as primary feeds when traditional search tools fail. Returns trending topics, emerging discussions, and breaking conversations with source attribution and context."

Load this skill when you need to find current tech conversations. Covers Reddit sources and Hacker News Algolia API as primary feeds when traditional search tools fail. Returns trending topics, emerging discussions, and breaking conversations with source attribution and context."
trigger:
  - User asks "what's trending in AI/tech"
  - User wants to check subreddits, HN, or community discussions
  - User asks for "o que estão discutindo" (Portuguese: what they're discussing)
  - Need to find hot topics without using web_search (which may return empty)
  - Need to bypass blocked social media (Reddit) via alternative data sources
metadata:
  hermes:
    tags: [trends, tech, ai, reddit, hacker-news, firecrawl, discovery]
    related_skills: [blogwatcher, deep-research]
type: Research
timestamp: 2026-06-12T02:23:22Z
---

# Tech Trend Discovery

When the user wants to know what the tech or AI community is discussing right now, follow this workflow. Reddit blocks direct access (`web_extract`, browser) — but `web_search` (Firecrawl search API) can still find Reddit content from Firecrawl's index when the backend is healthy.

## Primary Path: Firecrawl web_search (Reddit + general)

Try `web_search` first — it queries Firecrawl's own web index, which includes cached Reddit pages. This works even when direct Reddit access is blocked.

```
web_search(query="reddit r/artificial trending AI discussions", limit=5)
```

**Important nuance:** `web_search` returns results from the Firecrawl search index, not from live scraping. It CAN find Reddit links, titles, and descriptions. It CANNOT return the full page content of Reddit posts (that requires `web_extract`, which is blocked).

If `web_search` returns empty for ALL queries (not just niche ones), check if Firecrawl's backend is healthy (see "Firecrawl Self-Hosted Diagnostics" section below).

If `web_search` returns empty ONLY for your specific query (but works for broad queries), pivot to HN Algolia (next section).

## Secondary Path: Hacker News Front Page (always reliable)

HN Algolia's public API returns structured JSON that `web_extract` parses cleanly. Use this as a fallback when `web_search` doesn't find what you need, or as a cross-reference.

```
web_extract(urls=["https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=20"])
```

The response includes: title, points, comments, author, URL, and AI-generated summary with key excerpts. Filter mentally for AI/tech relevance — not everything on the front page is about the user's topic.

For topic-specific search on HN:
```
web_extract(urls=["https://hn.algolia.com/api/v1/search?query=<topic>&tags=story&hitsPerPage=10"])
```

Query parameter: `query=<search terms>` (URL-encoded), `tags=story` (front page stories), or `tags=front_page` (currently trending). Supports `hitsPerPage` up to 20.

## Preferred Reddit Path: The Reddit Gazette (works)

**The Reddit Gazette** at [https://theredditgazette.com/en](https://theredditgazette.com/en) is a reliable third-party aggregator that summarizes content from major subreddits (r/gaming, r/artificial, r/worldnews, r/CryptoCurrency, etc.) into structured daily, weekly, and monthly gazettes. Extract cleanly with `web_extract`.

```
web_extract(urls=["https://theredditgazette.com/en"])
```

The response includes:
- Daily gazettes by subreddit category (r/artificialdaily, r/gamingdaily, r/worldnewsdaily, etc.)
- Weekly gazettes by major subreddit (r/artificialweekly, r/gamingweekly, etc.)
- Each entry has: title, key points (3-5 bullet summary), author, read time, tags
- Monthly analyses for long-term trends

**Categories available:** artificial, gaming, worldnews, CryptoCurrency, and more. Each has separate daily, weekly, and monthly editions.

Use the daily or weekly editions for "what's trending right now." Switch to monthly for strategic/synthesis-level answers.

## Secondary Path: Cross-Reference with Tech Press

Once you identify a trending topic from The Reddit Gazette, validate and deepen it by cross-referencing with tech press articles. This gives the community sentiment + technical depth combo.

Use `web_search` with the topic name + "review" or "benchmark" or "discussion":

```
web_search(query="<topic> review benchmark comparison 2026")
web_search(query="<topic> OR <alternative> OR <rival> local model comparison")
```

**Reliable tech press sources** (extractable with `web_extract`):
- **Ars Technica** — good technical depth, hardware/performance focus
- **XDA Developers** — practical "hands-on" developer perspective
- **DEV Community** (dev.to) — developer tutorials, community benchmarks, code snippets
- **Lushbinary** — structured developer guides with tables, specs, FAQs
- **BuildFastWithAI** — practical guides with comparison tables and contrarian takes
- **LocalClaw** — local AI / model-specific sizing guidance
- **The Decoder** — AI news roundup with broader industry context

Combine multiple sources to form a complete picture: specs + benchmarks + community reaction + practical deployment advice.

## Deep-Dive Workflow: From Trend to Comprehensive Report

When the user wants to go deep on a specific trending topic:

1. **General scan** — Use The Reddit Gazette or HN Algolia to identify what's hot
2. **Topic selection** — User picks one to explore, or you recommend the most impactful
3. **Deep research** — Cross-reference 3-5 tech press sources (see above)
4. **Layer in community sentiment** — Pull quotes from Reddit, Dev.to comments, XDA takes
5. **Compile deliverables** — See "Deliverable Formats" below

Use the `todo` tool to track deep-dive progress for complex research tasks.

## Deliverable Formats

For delivering research results to the user:

### Quick Summary (inline in chat)
- Emoji indicators (🔥 for hottest)
- Numbered list with 1-2 sentence summaries
- "Resumão" (tl;dr) at the end
- Offer to deep-dive

### Deep-Dive Markdown File (.md)
For comprehensive topic research, create a `.md` file and deliver via `MEDIA:<path>`:

- **Structure**: Start with a Key Facts table, then deep sections with quotes, benchmarks, comparisons
- **Sections to include**: Specs, architecture deep-dive, benchmarks (with caveats), comparison table, community reaction, risks/limitations, practical how-to (code snippets), verdict
- **Source linking**: Link to every article referenced
- **Portuguese titles**: Use emoji section headers (📊, 🔬, ⚠️, etc.)
- Save to a sensible path (e.g., `/opt/data/<topic>-<slant>.<ext>`) and include `MEDIA:/path/to/file` in response
- **Length target**: 10-15 sections, 10-20 KB is appropriate for a thorough deep-dive

### HTML Conversion (Beautiful Deliverable)
When the user asks for a "beautiful" or "well-formatted" version after receiving the .md, convert to HTML:

- **Theme**: dark mode with `#0b0d11` background, `#13161c` surface, `#6c8cff` accent, `#e4e8f0` text
- **Typography**: `Inter` for text, `JetBrains Mono` for code (load via Google Fonts)
- **Styling**: CSS-only (no JS), responsive (`@media` queries), embedded `<style>` block
- **Components to style**: cards with hover effects, tables with alternating rows, callout boxes with colored borders, code blocks with `#1a1f2a` background, blockquotes with left accent border, tags/badges for categorization
- **Delivery**: Save as `/opt/data/<topic>.html` (30-45 KB typical) and deliver via `MEDIA:`
- **Color scheme reference for the dark theme**: `--bg: #0b0d11; --surface: #13161c; --surface2: #1a1f2a; --border: #262d3a; --text: #e4e8f0; --text-dim: #8a93a8; --accent: #6c8cff; --accent2: #a78bfa; --green: #34d399; --orange: #fb923c; --red: #f87171; --cyan: #22d3ee`
- **Example output**: See `/opt/data/gemma-4-12b-reddit-trends.html` from this session (32 KB, 13 sections, CSS-only dark theme)

## Fallback Path: Reddit (direct access)

Reddit blocks direct access:
  - Browser access (login wall with bot detection)
  - JSON API (returns HTML with "blocked" message)
  - old.reddit.com (same)
  - Even with proper User-Agent headers
  - Firecrawl scrape (`web_extract`) — returns `SCRAPE_RETRY_LIMIT (document_antibot)`
  - `curl` with any User-Agent to `reddit.com/r/*/.json`
  - Browser to old.reddit.com or www.reddit.com
  - Third-party front-ends (teddit, libreddit, redlib) — mostly dead

**BUT** note the crucial distinction. See "Firecrawl: search vs scrape distinction" above — `web_search` CAN return Reddit results from the Firecrawl index even though `web_extract` is blocked. Always try `web_search` for Reddit first.

### Making Reddit scrape work: Residential Proxy

Reddit blocks full content access (scrape) because this environment's IP range (Oracle Cloud datacenter) is identified as a bot source. The fix is a residential proxy. Firecrawl self-hosted supports this natively via env vars:

```
PROXY_SERVER=http://residential-proxy-host:port
PROXY_USERNAME=your-username
PROXY_PASSWORD=your-password
```

These go in the Firecrawl `.env` file (alongside the docker-compose.yml). After adding them, rebuild and restart the Firecrawl containers. See `references/firecrawl-proxy-setup.md` for full details.

If Reddit content is critical and the user hasn't set up a proxy yet:
1. Inform them Reddit direct scrape is blocked (datacenter IP)
2. Offer to set up a residential proxy via Firecrawl's `PROXY_SERVER` vars
3. In the meantime, pivot to HN Algolia or The Reddit Gazette

## Firecrawl Self-Hosted Diagnostics

When `web_search` returns empty results, **it may be a Firecrawl backend outage, not a content gap**. This environment runs self-hosted Firecrawl at `firecrawl_api:3002` (Docker container). The architecture has:

- **Firecrawl API server** (port 3002) — the HTTP endpoint Hermes talks to
- **Backend PostgreSQL** (port 5432) — search index and queue state
- **Redis** (port 6379) — job queue and caching

When PostgreSQL is down, Firecrawl's v0/v1 endpoints redirect to v2 but fail with `ECONNREFUSED 127.0.0.1:5432`, causing all searches to return empty results even though the API responds OK. The search eventually works when the database restarts.

### Quick health check from terminal

```bash
# Test Firecrawl search directly (bypasses Hermes SDK)
curl -s -m 10 -X POST "http://firecrawl_api:3002/v2/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"test query","limit":3}'
```

- **Success**: returns `{"success": true, "data": {"web": [...]}}` with actual results
- **Backend down (PostgreSQL)**: returns `{"error": "connect ECONNREFUSED 127.0.0.1:5432"}` with warnings about v0/v1 being deprecated
- **v0/v1 endpoints**: redirect to v2 with deprecation warnings but FAIL when backend is down

The v2 endpoints (`/v2/search`, `/v2/scrape`) are the current version. Always use v2 for direct API testing — v0/v1 redirect and the redirect path doesn't handle backend failures gracefully.

### Firecrawl proxy escalation path

If `web_search` works (search index has data) but `web_extract` fails specifically on anti-bot sites (Reddit, Cloudflare, etc.), and the user needs full scrape access:

1. **Current state**: Firecrawl uses direct outbound connection from Oracle Cloud IP (datacenter range). Anti-bot systems block datacenter IPs.
2. **Fix**: Add residential proxy to Firecrawl's `.env`:
   - `PROXY_SERVER=http://residential-proxy:port`
   - `PROXY_USERNAME=username`
   - `PROXY_PASSWORD=password`
3. **After config**: Restart Firecrawl containers, verify with `httpbin.org/ip` scrape
4. **Reference**: See `references/firecrawl-proxy-setup.md` for provider options and step-by-step

### Firecrawl backend diagnostic summary

When `web_search` returns empty for ALL queries:
1. Run the curl health check (v2/search)
2. If `ECONNREFUSED 127.0.0.1:5432` → PostgreSQL is down, retry later, pivot to HN
3. If it returns results → your query is the issue, not Firecrawl. Broaden/change query
4. If `web_search` works but `web_extract` fails on specific sites → anti-bot, needs proxy (see `references/firecrawl-proxy-setup.md`)

### When to suspect a Firecrawl outage

- Multiple different `web_search` queries all return empty results (not just niche queries — everything)
- `web_extract` works on general sites but fails on specific ones in ways inconsistent with prior behavior
- The same Reddit/HN query that worked before now returns nothing

In this case:
1. Run the curl health check above
2. If you see `ECONNREFUSED 127.0.0.1:5432`, the backend is down — retry later
3. Pivot to HN Algolia API (always works independently)
4. Inform the user the search backend is temporarily unavailable

### Firecrawl: search vs scrape distinction

This is the most important nuance:

- **`web_search` (Firecrawl search API)** — queries Firecrawl's own web index/cache. CAN return Reddit results (links, titles, descriptions) when the backend is healthy, even though Reddit blocks direct access. The search engine has already indexed the content.
- **`web_extract` (Firecrawl scrape API)** — directly accesses the target URL. Reddit blocks this with `document_antibot` (returns `SCRAPE_RETRY_LIMIT`).
- **Browser tool** — also blocked by Reddit (login wall + bot detection).

So: **`web_search` CAN find Reddit content** even when `web_extract` and browser fail. Always try `web_search` first for Reddit — don't skip it because "Reddit is blocked."


## Fallback Path: Web Search (unreliable)

`web_search` often returns empty results for niche or time-sensitive queries — but check if it's a Firecrawl backend outage first (see diagnostics above). `web_extract` is more reliable but runs into CAPTCHAs on:
  - Google (blocked)
  - DuckDuckGo (CAPTCHA challenge)
  - Bing (intermittent — may work, may hit Cloudflare)
  - Yahoo (not tested)

## Presenting Results

When delivering findings in Portuguese (common for this user), structure as:

1. **Numbered list** of 5 top discussions with:
   - Emoji indicator (🔥 for most active)
   - Points/comment count for signal
   - 1-2 sentence summary
2. **"Resumão"** (tl;dr paragraph) at the end tying themes together
3. Offer to deep-dive into any specific topic

## Pitfalls

- **web_search returning empty**: This is a known limitation. Do not retry with different queries more than 2-3 times. Pivot to web_extract on known API endpoints immediately.
- **HN Algolia can return zero hits** for very specific queries — broaden the search or remove query param to get front page.
- **JSON API endpoints work best with web_extract** (not browser, not curl). web_extract automatically parses JSON into readable markdown with summaries.
- **Do not fabricate results** when sources are blocked. Report the blocker honestly and offer alternatives.
- **The Reddit Gazette** does not cover every subreddit — it's curated, not comprehensive. If you need deep Reddit-only data, it may not exist outside the gazette's selection.
- **Cross-referencing depth trap**: It's easy to over-collect sources. Stop at 3-5 quality sources for a deep-dive — more gives diminishing returns for the token cost.
- **MEDIA: delivery requires absolute paths** — always use `/opt/data/<filename>` not `~/<filename>`.
- **Reddit is blocked; don't insist.** Multiple approaches all fail the same way.
