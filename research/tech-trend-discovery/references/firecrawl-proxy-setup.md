# Firecrawl Residential Proxy Setup

## When to use

When `web_search` works but `web_extract` fails on anti-bot sites (Reddit, Cloudflare, WAF) with `SCRAPE_RETRY_LIMIT (document_antibot)` errors. This happens because the Oracle Cloud datacenter IP is flagged as a bot source.

## How Firecrawl proxy works

Firecrawl self-hosted supports HTTP/HTTPS proxy routing via three env variables in its `.env` file (alongside the `docker-compose.yml`):

```
PROXY_SERVER=http://proxy-host:port
PROXY_USERNAME=your-username
PROXY_PASSWORD=your-p...ese apply to ALL outbound traffic from Firecrawl workers (scrape, crawl, search indexing). There's no per-site proxy routing — it's all-or-nothing.

## Provider options

| Provider | Type | Price | Notes |
|----------|------|-------|-------|
| **BrightData** | Residential rotating | ~$15/GB | Most mature; rotating IPs per request |
| **ScrapingBee** | API-based | ~$49/mo 500k credits | Proxy included, simpler setup |
| **Hyperbrowser** | Anti-detect browser | ~$49/mo | Stealth browser, not just proxy |
| **Scrapfly** | Anti-bot + proxy | ~$59/mo 5M credits | 98% success rate claimed |

## Configuration step-by-step

### 1. Locate Firecrawl's files

The Firecrawl `docker-compose.yml` and `.env` live on the Docker host (same machine, outside the Hermes container). Find them:

```bash
find /opt /home /root /etc -maxdepth 5 -name "docker-compose*" \
  -not -path "/proc/*" -not -path "/sys/*" -not -path "*/node_modules/*" 2>/dev/null
```

### 2. Edit the .env

Add to the Firecrawl `.env`:

```
PROXY_SERVER=http://zproxy.lum-superproxy.io:22225
PROXY_USERNAME=your-brightdata-username
PROXY_PASSWORD=your-brightda...e alternative (all-in-one URL):
```
PROXY_SERVER=http://username:password@zproxy.lum-superproxy.io:22225
```

### 3. Restart Firecrawl

```bash
cd <firecrawl-dir>
docker compose down
docker compose up -d
```

### 4. Verify proxy is active

Test which IP Firecrawl is using:

```bash
curl -s -X POST "http://localhost:3002/v2/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://httpbin.org/ip","formats":["markdown"]}'
```

The response should show a residential IP, not the Oracle Cloud datacenter IP.

Then test Reddit:
```bash
curl -s -X POST "http://localhost:3002/v2/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://old.reddit.com/r/artificial/","formats":["markdown"]}' | head -100
```

And from Hermes:
```
web_extract(urls=["https://old.reddit.com/r/artificial/"])
```

## Limitations

- **Self-hosted lacks "Fire-engine"**: The cloud Firecrawl has a proprietary anti-bot engine that self-hosted instances don't get. Proxy is the best mitigation but may not match cloud performance.
- **All-or-nothing**: Proxy applies to ALL Firecrawl traffic. There's no per-domain proxy routing.
- **Latency**: Residential proxies add 50-500ms per request. Choose a proxy geographically close (US-East or South America for Oracle Cloud).
- **Cost**: $15-60/mo depending on provider and volume.
- **Proxy can still be detected**: Sophisticated anti-bot (Cloudflare Turnstile, DataDome) may still block even residential proxies. For those cases, Hyperbrowser or Scrapfly are better options.

## Alternative: Replace Firecrawl

If proxy configuration doesn't solve the problem or the user doesn't want to pay for a proxy, consider replacing the search backend in Hermes:

```yaml
# In config.yaml
web:
  backend: firecrawl
  search_backend: exa         # Exa API for search
  extract_backend: scrapingbee # ScrapingBee for scrape
```

This lets Hermes use different providers for search vs extract, each optimized for its purpose.
