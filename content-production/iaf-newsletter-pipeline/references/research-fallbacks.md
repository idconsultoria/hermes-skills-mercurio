# Research Fallbacks — When web_search / web_extract Are Unavailable

## Problem

The `web_search` and `web_extract` tools depend on Firecrawl backend, which may be unavailable
due to `security.allow_lazy_installs=false` (the package `firecrawl-py` must be pre-installed).

When these tools fail with `"Feature 'search.firecrawl' unavailable: lazy installs disabled"`,
use the alternatives below. These patterns were proven during the GPT‑5.6 special edition
research (26/06/2026) and earlier research sessions.

## Alternative 1: Hacker News Algolia API (best source for AI news discovery)

The HN Search API is free, fast, and returns structured JSON. No auth needed.

### Search for stories (discovery)
```
curl -sL "https://hn.algolia.com/api/v1/search?query=GPT+5.6&tags=story&hitsPerPage=10"
```

Parse with Python to extract titles, URLs, points, and comment counts:
```python
import sys, json
d = json.load(sys.stdin)
for h in d.get('hits', []):
    print(f"Title: {h.get('title')}")
    print(f"URL: {h.get('url')}")
    print(f"Points: {h.get('points')} | Comments: {h.get('num_comments')}")
    print(f"Author: {h.get('author')}")
```

### Read comments from a story (deep dive)
```
curl -sL "https://hn.algolia.com/api/v1/items/{story_id}"
```

Story IDs come from the search results. Comments are in `children`, ordered by relevance.
Each comment has `author`, `points`, `text` (HTML). Strip HTML tags with `re.sub(r'<[^>]+>', '', text)`.

### Search within comments
```
curl -sL "https://hn.algolia.com/api/v1/search?query=GPT+5.6+benchmark&tags=comment&hitsPerPage=10"
```

## Alternative 2: Direct curl to known news sites

When you already know the URL, fetch directly with curl + Python HTML-to-text extraction:

```bash
curl -sL -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  "https://example.com/article" 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:5000])
"
```

### News sites that worked (not behind aggressive paywalls/Cloudflare)
- `metr.org` — METR evaluation posts, full text accessible
- `deploymentsafety.openai.com` — OpenAI system cards, full text accessible
- `theverge.com` — works with proper User-Agent, main article text extractable
- `velo.xyz` — works, though content may be thin
- `hn.algolia.com` — API always works (no Cloudflare)

### Broken / blocked sites
- `openai.com` — Cloudflare challenge page, blocks both curl and browser_navigate
- `washingtonpost.com` — paywall
- `bloomberg.com` — paywall
- `techcrunch.com` — article body may not be in static HTML
- `reddit.com` — API blocks without OAuth; use `old.reddit.com` RSS feeds instead (see `reddit-rss-architecture.md`)

## Alternative 3: Browser tools (last resort for dynamic content)

When curl fails (Cloudflare, JS-rendered content), try `browser_navigate`. But note:
- `openai.com` blocks browser too (Cloudflare challenge)
- Browser is slower and more expensive per page
- Only use when curl + API approaches are exhausted

## Alternative 4: Pre-install firecrawl-py

If research volume justifies it and the user approves:
```bash
uv pip install firecrawl-py==4.17.0
```
Then retry `web_search`/`web_extract`. This may require setting `security.allow_lazy_installs=true` in Hermes config.

## Priority order
1. HN Algolia API (fastest, free, covers tech news)
2. Direct curl to known URLs (when URL is known)
3. Browser (last resort, for JS-rendered pages)
4. Pre-install firecrawl (if repeated use expected)
