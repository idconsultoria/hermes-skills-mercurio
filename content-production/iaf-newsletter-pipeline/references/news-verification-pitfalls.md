# News Verification Pitfalls

Lessons from repeated corrections on news accuracy — stale items, wrong dates, and dedup failures.

## The Coleta Has No Date Filter

Cron #1 (Coleta de Fontes) aggregates **everything** from its sources into flat `.md` files. It does NOT filter by date. This means:

- Reddit posts from 3+ days ago appear alongside today's
- General news searches (`web_search "AI news today"`) return a mix of recent and older articles
- The `therundown.ai` / `superhuman.ai` newsletters may reference events from earlier in the week

**Rule:** Just because an item is in the coleta does NOT mean it happened today. Every item must have its publication date verified before selection.

## How to Verify Publication Dates

### Reddit
- Old Reddit URLs show the post date in the sidebar. Check at least the day.
- If a post says "5 days ago" in your summary, it is NOT news for today.
- Cross-reference: does this post reference events that happened this week, or last month?

### Web News
- Check the URL for date patterns: `/2026/06/13/`, `?date=2026-06-13`
- Look for a dateline or byline date in the article text
- If you cannot find a date, search for the headline + "2026" + specific date terms

### Hacker News
- HN timestamps are visible in the page. Items that hit front page could be 1-24h old.
- Multiple-day-old items still appear if they got late traction.

### Newsletters (The Rundown, Superhuman)
- These aggregate the week's top stories. An item listed there may be from Monday when you're reading on Friday.
- Cross-verify the original linked article's date.

## Stale News Patterns — What to Watch For

| Pattern | Risk | Example |
|---------|------|---------|
| "Announced at I/O / WWDC / Computex" | These events happened weeks ago | Gemini 3.5, o3-pro, Apple Siri plans |
| Model launch without specific date | Model releases from days/weeks ago re-circulate | MiniMax-M3 (Jun 1), o3-pro, Nemotron |
| "Next week" or "coming soon" in the description | The source was written when this was future tense | GLM-5.2 "next week" |
| Generic roundup blog | Sites like "7 Explosive AI Updates" aggregate old news | imfounder.com, kersai.com |
| Reddit post with high reference count | Boosted by algorithm days later, not because it's new | Any post >48h old still on front page |

## The Dedup Manifest Is Not Optional — But It Can Be Fooled

Even after running `dedup_manifest.py` and reading the manifest, **check each selected item against `titles_flat` one more time before writing the HTML**. The dedup step is the **last line of defense** — if you skip it or do it hastily, duplicates WILL appear.

### How duplicates slip through
1. You read the manifest but don't cross-reference each of your 20 selected items
2. The manifest has a title, but you include it under a different headline for today
3. The topic is the same (e.g. "Google AI Overviews liability") but you frame it as "Alemanha decide" — same topic, different headline

**Fix:** Before writing the HTML, paste each of your 20 titles into a manual grep against `titles_flat`. Do not rely on memory or "close enough" similarity.

## If the User Corrects Your News

The user will correct you quickly on three things:
1. **Wrong dates** — news from last week presented as today's
2. **Wrong facts** — model capability claims that don't match reality (e.g. "Gemini 3.5 Pro shipped" when only Flash shipped)
3. **Duplicates** — items that ran in previous editions

When this happens:
- Apologize once, fix it immediately
- Do NOT argue or explain
- After fixing, audit the rest of the edition for similar issues
- The fix goes into the same HTML/PDF and gets redeployed — do not create a separate "errata" edition
