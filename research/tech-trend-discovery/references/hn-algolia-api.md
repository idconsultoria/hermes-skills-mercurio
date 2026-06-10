# HN Algolia API Reference

Public Algolia-powered search for Hacker News. No auth required. Returns JSON. Best consumed via `web_extract()` which auto-parses into readable markdown with summaries.

## Endpoints

### Front page (currently trending)
```
https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=20
```
Returns stories currently on the HN front page sorted by points.

### Topic search
```
https://hn.algolia.com/api/v1/search?query=<URL_ENCODED_QUERY>&tags=story&hitsPerPage=10
```
Returns stories matching the query. Tags: `story` (all stories), `front_page` (front page only).

### By date (recent)
```
https://hn.algolia.com/api/v1/search?query=AI&tags=story&hitsPerPage=10&numericFilters=created_at_i>1749052800
```
Unix timestamp for date filtering.

## Key Parameters

| Param | Description |
|-------|-------------|
| `query` | URL-encoded search terms |
| `tags` | `story`, `front_page`, `comment`, `show_hn`, `ask_hn` |
| `hitsPerPage` | Max results (1-20) |
| `numericFilters` | `created_at_i>TIMESTAMP`, `points>N` |
| `page` | Pagination (0-indexed) |

## What the response includes

Each hit has: `title`, `url`, `author`, `points`, `num_comments`, `objectID`, `created_at`, `story_text` (if available).

## Proven working examples

```
# Top AI stories this week
web_extract(urls=["https://hn.algolia.com/api/v1/search?query=artificial+intelligence&tags=story&hitsPerPage=10"])

# Any tech front page (best for "what's trending")
web_extract(urls=["https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=15"])
```
