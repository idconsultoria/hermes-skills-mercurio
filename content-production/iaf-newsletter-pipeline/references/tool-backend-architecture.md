# Tool Backend Architecture — IAF Pipeline

This reference documents HOW each tool works under the hood when Hermes executes the IAF cron pipeline. Essential for diagnosing failures, estimating costs, and understanding network dependencies.

## 1. `web_extract` — Firecrawl (Docker, port 3002)

**Backend:** Local Firecrawl instance running in a Docker container on the same Oracle host.

**How it works:**
1. Hermes sends an HTTP POST to `http://localhost:3002/v1/extract` (or similar Firecrawl API endpoint)
2. Firecrawl spins up a headless Chromium instance
3. Chromium navigates to the target URL, executes JavaScript
4. Firecrawl extracts the page content and converts to Markdown
5. For pages over ~5KB, Firecrawl also generates an LLM summary
6. Result is returned to Hermes as structured markdown

**Used in IAF pipeline:**
- Cron #1: extracts Hacker News frontpage (`news.ycombinator.com`)
- Cron #1: would extract Reddit (if RSS fails, fallback to web_extract)

**Dependencies:**
- Docker container running Firecrawl on port 3002
- Chromium inside the container
- Internet access from Docker host
- RAM: ~1-2GB per extraction (Chromium is heavy)

**Failure modes:**
- Firecrawl container stopped → `web_extract` returns timeout/error
- Target site behind Cloudflare/bot detection → returns error or captcha page
- Memory pressure → Chromium OOM kill → stale extraction

**Expected cost:** 0 tokens (local), but time cost of ~2-8s per URL.

---

## 2. `web_search` — Provider Search API

**Backend:** The configured LLM provider's search API (OpenCode Go / OpenRouter / custom).

**NOT** Firecrawl. It does NOT pass through the local Docker instance.

**How it works:**
1. Hermes sends the search query to the configured provider's API endpoint
2. The provider proxies to a search backend (Tavily, Similarweb, or self-hosted)
3. Returns structured results: `{url, title, description, category}[]`
4. Hermes renders the results into the context

**Used in IAF pipeline:**
- Cron #1: 8+ search queries for news sources (TechCrunch, WIRED, Reuters, The Verge, Ars Technica)
- Cron #1: supplementary searches for social/discussion topics

**Dependencies:**
- Provider API key configured (OpenCode Go / OpenRouter)
- Search backend availability
- Internet access

**Failure modes:**
- Empty results (returned `[]`) → happened on 16/06 for some queries
- Rate limiting by provider
- Search backend down

**Cost:** Counted in token usage (results are rendered as content in the context).

---

## 3. `terminal` — Docker Host Shell

**Backend:** Shell execution inside the Hermes Docker container on the Oracle host.

**How it works:**
1. Hermes receives the command string
2. Executes via `subprocess` inside the container (`/bin/bash -c`)
3. Stdout + stderr captured and returned
4. Working directory persists between calls (same container session)

**Used in IAF pipeline:**
- Cron #1: `mkdir -p` for output directory
- Cron #1: runs `reddit_rss_parser.py` (Python) for each subreddit RSS feed
- Cron #3: runs `dedup_manifest.py`, Chromium for PDF, file ops
- Cron #4: runs `vercel` CLI, deploy scripts, `curl` for verification

**Python environment:** Python 3.13 (no pip module), PEP 668 active. Use `uv` or venvs.

**Network access:** Full outbound internet from the Docker container.

**Failure modes:**
- Command timeout
- Python script crashes (import error, HTTP error)
- Chromium/vercel not found in PATH

**Cost:** 0 tokens (terminal output is tool result, not LLM-generated). But the output is read by the LLM, so large outputs consume context.

---

## 4. `read_file` / `write_file` — Filesystem

**Backend:** Direct filesystem access from the Docker container (bind-mounted volume).

**Path:** All IAF files live under `/opt/data/` which is mounted into the container.

**Cron-specific paths:**
- Output dir: `/opt/data/cron/output/{job_id}/`
- History: `/opt/data/cron/history/`
- Scripts: `/opt/data/cron/scripts/`

**Dependencies:** None (always available, cheap).

---

## 5. `send_message` — Telegram Bot API

**Backend:** HTTP POST to `https://api.telegram.org/bot{TOKEN}/{method}`.

**How it works:**
1. Hermes formats the message + optional MEDIA file path
2. POSTs to Telegram Bot API
3. If MEDIA path present, uploads file via multipart/form-data

**MEDIA file delivery:** Files are read from the container's filesystem and uploaded to Telegram servers. The file must exist at the specified path.

**Cost:** 0 tokens. Network transfer cost only.

---

## Tool Call Cost Summary

| Tool | Token Cost | Time Cost | Network | Backend |
|---|---|---|---|---|
| `web_search` | Context (results read by LLM) | 0.5-2s | Yes | Provider search API |
| `web_extract` | 0 (local) | 2-8s | Yes | Firecrawl Docker :3002 |
| `terminal` | 0 (execution) | Varies | Per command | Docker shell |
| `read_file` | 0 | <0.1s | No | Filesystem |
| `write_file` | 0 | <0.1s | No | Filesystem |
| `send_message` | 0 | 1-3s | Yes | Telegram API |

## Where Firecrawl IS and ISN'T Used

| Tool / Component | Uses Firecrawl? | Backend |
|---|---|---|
| `web_extract` | ✅ YES | Firecrawl Docker :3002 |
| `web_search` | ❌ NO | Provider search API |
| `terminal` (Python HTTP) | ❌ NO | Direct urllib.request |
| HTML-to-PDF rendering | ❌ NO | Chromium headless (not Firecrawl) |
| Newsletter dedup script | ❌ NO | Local Python |

> **Key insight:** Firecrawl is only used for `web_extract` — converting a specific URL to markdown. It is NOT used for search, API calls, or PDF generation. Each has a separate backend.
