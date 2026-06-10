# Web Access Blocklist (from this Oracle Cloud environment)

Sources confirmed blocked as of June 2026:

## Fully blocked for DIRECT access
- **Reddit** (all forms: www, old.reddit, API with User-Agent, /hot/.json) — login wall + bot detection
- **Google Search** (web_extract returns "please click here" message)
- **DuckDuckGo** (CAPTCHA challenge — "select squares containing a duck")

**IMPORTANT:** Even though Reddit blocks direct access, `web_search` (Firecrawl search API) CAN still find Reddit content. Firecrawl's index has Reddit pages cached, so searching returns links, titles, and descriptions. Reddit is only blocked for `web_extract` (direct scrape) and the browser tool. Always try `web_search` with Reddit queries before giving up on Reddit content.

## Intermittent / fragile
- **Bing** (web_extract works sometimes, but hits Cloudflare challenge under load)
- **Web search tool** (`web_search`) — when Firecrawl backend (PostgreSQL) is healthy, it works well. When backend is down (ECONNREFUSED 5432), returns empty. See Firecrawl Self-Hosted Diagnostics in the main skill for troubleshooting.

## Known working
- **HN Algolia API** (hn.algolia.com) — always works, no auth, structured JSON
- **Firecrawl API v2 endpoints** (firecrawl_api:3002/v2/search, /v2/scrape) — direct curl tests bypass Hermes SDK
- **The Reddit Gazette** (theredditgazette.com/en) — third-party Reddit content aggregator, daily/weekly/monthly editions for major subreddits
- **General websites via web_extract** (company blogs, news articles, GitHub READMEs)
- **JSON API endpoints** (anything returning JSON via web_extract parses well)
- **Tech press** (Ars Technica, XDA, DEV Community, Lushbinary, BuildFastWithAI, LocalClaw, The Decoder)

## Strategy
When web_search returns empty and the destination is blocked, pivot to:
1. Check Firecrawl health first (see diagnostics in main skill — might be a backend outage, not a content issue)
2. HN Algolia API (tech topics)
3. The Reddit Gazette (Reddit topics via third-party aggregator)
4. Direct web_extract on known article URLs
5. Browser tool (works for some sites, fails on Reddit/Google)

Do NOT retry Reddit `web_extract` or browser more than once — they all fail the same way. But DO try `web_search` for Reddit first — it uses Firecrawl's index, not a live scrape.
