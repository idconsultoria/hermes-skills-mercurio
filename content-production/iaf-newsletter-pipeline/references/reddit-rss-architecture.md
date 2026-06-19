# Reddit RSS Parser — Architecture & Multi-Strategy

**Script:** `/opt/data/scripts/reddit_rss_parser.py`

## Why Multi-Strategy?

The Oracle Cloud host IP is flagged as a datacenter by Reddit's Cloudflare. Direct RSS from `www.reddit.com` returns HTTP 403. The fix uses three fallback strategies:

## Strategy Order

1. **`old.reddit.com/r/{sub}/{sort}/.rss`** (primary — works with browser UA)
2. **`old.reddit.com/r/{sub}/.rss`** (fallback sort endpoint)
3. **`www.reddit.com/r/{sub}/{sort}/.rss`** (last resort, likely 403)

## Key Design Decisions

### old.reddit.com
- Returns Atom XML (not RSS 2.0). The parser has dedicated `parse_atom_to_markdown()`.
- Rate limit is strict: ~1 request per 60s per endpoint.
- Headers `x-ratelimit-remaining`, `x-ratelimit-reset` in responses.

### File-based caching
- Cache dir: `/opt/data/cache/reddit_rss/`
- TTL: 120 seconds (configurable via `--cache-ttl`)
- Key: SHA256 hash of the URL
- Solves the parallel-cron problem: the agent calls 14+ RSS URLs in a single message. Without caching, all 14 hit the same rate limit simultaneously.

### Domain-level locking
- Lock file per domain (e.g., `.lock_old_reddit_com`)
- Acquire with timeout (30s) before making HTTP request
- Stale lock detection at 30s (handles killed processes)
- Ensures sequential requests to the same domain

### Rate limit handling
- On HTTP 429: read `Retry-After` or `x-ratelimit-reset` header
- Wait that many seconds before retrying (up to 2 retries)
- If all retries exhausted, return `<!-- RATE LIMITED -->` comment

### Description cleaning
- HTML entity decoding via `html.unescape()`
- Strips Reddit boilerplate: `submitted by /u/... [link] [comments]`
- Truncates to 300 chars

## CLI Usage

```bash
# Fetch Hot posts
python3 /opt/data/scripts/reddit_rss_parser.py artificial --sort hot --label "r/artificial"

# Fetch Top of the week
python3 /opt/data/scripts/reddit_rss_parser.py artificial --sort top --label "r/artificial — Top semana"

# Fetch New posts
python3 /opt/data/scripts/reddit_rss_parser.py artificial --sort new --label "r/artificial — New"
```

## Testing

```bash
# Clear cache for clean test
rm -rf /opt/data/cache/reddit_rss

# Sequential calls (respects rate limits)
python3 /opt/data/scripts/reddit_rss_parser.py artificial --label "Test"
python3 /opt/data/scripts/reddit_rss_parser.py OpenAI --label "Test 2"

# Second call to same sub = cache hit (~0.07s)
python3 /opt/data/scripts/reddit_rss_parser.py artificial --label "Cached"
```

## Known Limitations

- Rate limit is 1 request per ~60s per endpoint even on old.reddit
- Cache collision risk: same hash for different URLs with identical query params
- No proxy rotation — if old.reddit also blocks datacenter IPs in the future, need residential proxy
- Firecrawl bypasses Cloudflare but adding it as a 4th strategy would add ~2-3s latency per page
