---
name: manga-anime-data
description: "Research manga and anime data via AniList GraphQL API — rankings, scores, metadata, completion status, and genre filtering.

Load this skill instead of web search when you need authoritative community ratings, detailed metadata, or status verification for anime/manga. Returns structured JSON data via direct GraphQL queries."
category: media
---

# Manga & Anime Data Research via AniList API

Query AniList's public GraphQL API directly with `curl` + `python3` parsing. Faster and more reliable than scraping ranking sites, and returns structured JSON.

## Quick Start — Top Finished Manga

```bash
curl -s -X POST "https://graphql.anilist.co" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"query":"{Page(page:1,perPage:20){media(type:MANGA,status:FINISHED,sort:SCORE_DESC,isAdult:false){title{romaji english}averageScore genres format chapters startDate{year}}}}"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, m in enumerate(data['data']['Page']['media'], 1):
    t = m['title']['english'] or m['title']['romaji']
    s = m.get('averageScore', 0) or 0
    g = ', '.join(m['genres'][:2])
    f = m['format']
    ch = m.get('chapters', '?') or '?'
    yr = m['startDate']['year'] or '?'
    print(f'{i:2d}. Score:{s:3d}  {str(t):45s} {str(ch):>4s}ch  {yr}  {f:10s} [{g}]')
"
```

## Query Patterns

### Top N by Score (Filtered)
Use `SCORE_DESC` sort. Combine with `status:FINISHED` for completed works only.

| Parameter | Values | Notes |
|-----------|--------|-------|
| `type` | `MANGA`, `ANIME` | |
| `status` | `FINISHED`, `RELEASING`, `NOT_YET_RELEASED`, `CANCELLED`, `HIATUS` | |
| `sort` | `SCORE_DESC`, `POPULARITY_DESC`, `TRENDING_DESC` | |
| `isAdult` | `false` (omit for all) | Defaults to true — set false to filter adult content |
| `genre` | `"Action"`, `"Romance"` etc. | Add to `media` filter object |

### Search Specific Title

```bash
curl -s -X POST "https://graphql.anilist.co" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"query":"{Media(search:\\"Monster\\",type:MANGA){title{romaji english} status averageScore chapters volumes startDate{year} endDate{year} description}}"}' | python3 -m json.tool
```

### Fetch More Data (Pagination)
Use `page` parameter (1-indexed, 50 items/page):
```json
{"query":"{Page(page:2,perPage:50){media(...){...}}}"}
```

### Genre + Status Combined
```json
{"query":"{Page(page:1,perPage:20){media(type:MANGA,status:FINISHED,genre:\"Psychological\",sort:SCORE_DESC){title{romaji english} averageScore chapters startDate{year}}}}"}
```

## Available Scores

| Field | Range | Meaning |
|-------|-------|---------|
| `averageScore` | 0–100 | Mean community score (what most rankings use) |
| `meanScore` | 0–100 | Alternative scoring, often slightly different |

## Output Formatting Tips

- **Pretty-print entire response**: pipe to `python3 -m json.tool`
- **Custom table**: pipe to python3 inline script (as in Quick Start)
- **Filter adult content** with `isAdult:false` — without this, H-content skews results
- **Filter by format** `MANGA` to exclude light novels (which have `NOVEL` format) — they're different mediums with different scoring dynamics

## Pitfalls

- **⚠️ Complete status vs. actual completion**: Some titles marked `FINISHED` on AniList may still have epilogue chapters, spin-offs, or post-publication extras releasing. For strict "truly finished" lists, verify end date is in the past and no active sequel series exists.
- **⚠️ Berserk**: Marked as `RELEASING` (post-Miura continuation). NOT finished — do not include in "completed" lists.
- **⚠️ Rate limiting**: ~30 requests/min before 403. Batch into single queries with `Page` pagination instead of multiple sequential calls. If hit 403, wait ~1min.
- **⚠️ Score bias**: Older classics (Akira, Nausicaä, Death Note, Dragon Ball) score lower on AniList than modern works — their voters skew younger. The raw score is ordinal within an era, not absolute across eras. Factor this in when ranking across decades.
- **⚠️ Manhwa / Webtoon mixing**: Korean and Chinese works (`MANGA` format tag) also appear in results. The GraphQL `Format` enum includes MANGA and NOVEL but doesn't distinguish Japanese manga from Korean manhwa. Check `startDate.country` or description if you need to filter by origin.
- **⚠️ One-shots & doujinshi**: `chapters: 1` entries may be one-shots, specials, or mis-tagged doujinshi. Filter with `chapters_greater: 5` or similar if they pollute results.

## GraphiQL Explorer

For building and testing queries interactively: https://anilist.co/graphiql

## References

None yet.
