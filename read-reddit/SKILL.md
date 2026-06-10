---
name: read-reddit
description: "Read Reddit subreddits reliably via RSS feeds — bypasses API rate limits and bot detection. For research, curation, or news gathering."
version: 1.1.0
author: Created for IAF pipeline
platforms: [linux, macos]
---

# Read Reddit via RSS

## Why RSS Instead of the API

Reddit's official JSON API has aggressive rate limits and often requires OAuth. RSS feeds are:
- **Free** — no API key needed
- **Stable** — same data, different format
- **Lightweight** — XML is easy to parse with stdlib

## Important: User-Agent Header

Reddit's CDN (Fastly) blocks requests without a proper browser User-Agent. **Always** set one:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

Without this header, you'll get a "blocked by network security" HTML page instead of RSS XML.

## Feed URLs

### By sorting method

| Sort | URL Pattern |
|------|-------------|
| Hot (default) | `https://www.reddit.com/r/{SUBREDDIT}/hot/.rss` |
| New | `https://www.reddit.com/r/{SUBREDDIT}/new/.rss` |
| Rising | `https://www.reddit.com/r/{SUBREDDIT}/rising/.rss` |
| Top (today) | `https://www.reddit.com/r/{SUBREDDIT}/top/.rss?t=day` |
| Top (week) | `https://www.reddit.com/r/{SUBREDDIT}/top/.rss?t=week` |
| Top (month) | `https://www.reddit.com/r/{SUBREDDIT}/top/.rss?t=month` |
| Top (year) | `https://www.reddit.com/r/{SUBREDDIT}/top/.rss?t=year` |
| Top (all) | `https://www.reddit.com/r/{SUBREDDIT}/top/.rss?t=all` |

### Limit results

Append `?limit=N` or `&limit=N` to control post count (max 100):

```
https://www.reddit.com/r/artificial/hot/.rss?limit=10
```

### Multiple subreddits

Reddit supports multi-reddit feeds:

```
https://www.reddit.com/r/artificial+LocalLLaMA+ChatGPTPro/hot/.rss?limit=10
```

## Parsing the XML

Reddit feeds use **Atom format** (`http://www.w3.org/2005/Atom`). Each post is an `<entry>` element.

### Key fields

| XML Path | Description |
|----------|-------------|
| `atom:entry/atom:title` | Post title |
| `atom:entry/atom:link[@href]` | URL to the post |
| `atom:entry/atom:author/atom:name` | Author username |
| `atom:entry/atom:published` | ISO timestamp |
| `atom:entry/atom:updated` | Last updated |
| `atom:entry/atom:content` | Post body (HTML) — strip tags for plain text |
| `atom:entry/atom:id` | Unique post ID (e.g. `t3_1twn3m7`) |
| `atom:entry/atom:category[@label]` | Subreddit name |

### Python parsing example

```python
import xml.etree.ElementTree as ET
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
subreddit = "artificial"
url = f"https://www.reddit.com/r/{subreddit}/hot/.rss?limit=10"

import subprocess
result = subprocess.run(
    ["curl", "-sL", "--max-time", "15", "-A", UA, url],
    capture_output=True, text=True
)
data = result.stdout

root = ET.fromstring(data)
ns = {'atom': 'http://www.w3.org/2005/Atom'}

posts = []
for entry in root.findall('atom:entry', ns):
    title = entry.find('atom:title', ns)
    link = entry.find('atom:link', ns)
    author = entry.find('atom:author/atom:name', ns)
    published = entry.find('atom:published', ns)
    content = entry.find('atom:content', ns)
    
    # Strip HTML tags from content
    body = ""
    if content is not None and content.text:
        body = re.sub(r'<[^>]+>', '', content.text)[:500]
    
    posts.append({
        'title': title.text if title is not None else '',
        'url': link.get('href') if link is not None else '',
        'author': author.text if author is not None else '',
        'published': published.text if published is not None else '',
        'snippet': body[:300],
    })

for p in posts:
    print(f"📌 {p['title']}")
    print(f"   👤 {p['author']} | 🕐 {p['published']}")
    print(f"   🔗 {p['url']}")
    print(f"   📝 {p['snippet']}")
    print()
```

### Parsing with shell (quick and dirty)

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
curl -sL --max-time 15 -A "$UA" \
  "https://www.reddit.com/r/artificial/hot/.rss?limit=5" | \
  python3 -c "
import sys, xml.etree.ElementTree as ET, re
data = sys.stdin.read()
root = ET.fromstring(data)
ns = {'atom': 'http://www.w3.org/2005/Atom'}
for e in root.findall('atom:entry', ns):
    t = e.find('atom:title', ns)
    l = e.find('atom:link', ns)
    a = e.find('atom:author/atom:name', ns)
    print(f\"📌 {t.text}\n   👤 {a.text}\n   🔗 {l.get('href')}\n\")
"
```

## Single-line test (for quick debugging)

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
curl -sL --max-time 10 -A "$UA" "https://www.reddit.com/r/artificial/hot/.rss?limit=3" | python3 -c "import sys, xml.etree.ElementTree as ET, re; d=sys.stdin.read(); r=ET.fromstring(d); ns={'atom':'http://www.w3.org/2005/Atom'}; [print(f\"📌 {e.find('atom:title',ns).text}\n   🔗 {e.find('atom:link',ns).get('href')}\n\") for e in r.findall('atom:entry',ns)]"
```

## Reference Files

- `references/iaf-subreddit-config.md` — Categorized subreddit list, per-subreddit sorting strategy, activity notes, and fetch limits for daily AI news curation.
- `scripts/reddit_rss_parser.py` — Standalone Python script with JSON output, argparse, and configurable subreddit groups.

## Critical: Source URL Requirement

When using this skill to collect data that will be consumed by a downstream process (newsletter generator, report, analysis pipeline), **every single entry in the saved file MUST include a clickable source URL**. No exceptions.

- Reddit RSS feeds naturally include the post URL (`atom:link`). Always extract and save it alongside each post.
- When delegating Reddit collection to a `delegate_task` subagent, include this explicit instruction in the context: *"CRITICAL: Every entry MUST include its clickable source URL. No exceptions."*
- After delegation, verify that every entry has a URL by running: `grep -c 'https\?://' output_file.md`

## Common Pitfalls

1. **Missing User-Agent** → Returns Reddit's "blocked by network security" page. Always set `-A "$UA"`.
2. **Rate limiting** → Reddit limits RSS too, but much more generously than the JSON API. Keep `limit` reasonable (≤25).
3. **Empty results** → Some subreddits or sorts may return nothing. Always handle empty results gracefully.
4. **Multi-reddit limit** → Multi-reddit feeds can be slow with many subreddits. Prefer individual requests delegated in parallel.
5. **Content with HTML** → Post bodies contain HTML. Always strip tags before using as plain text.
6. **Old Reddit format** → `old.reddit.com` uses the same block rules. Stick with `www.reddit.com/.../.rss`.
7. **Link verification** → When using this skill inside a `delegate_task` subagent, the subagent may link to wrong sources if `web_search` returns empty results. Verify key links independently: check that (a) the URL resolves, (b) the URL content matches the story, and (c) version-specific URLs (e.g. Claude Opus 4.8 → not 4.7) point to the exact right page. This is especially important when the RSS content is later used in a newsletter or report.
