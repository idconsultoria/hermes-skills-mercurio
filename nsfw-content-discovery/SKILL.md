---
name: nsfw-content-discovery
description: "Find adult/NSFW content across platforms — creators, performers, search engines.

Load this skill when searching for explicit content from a specific creator or performer. Covers the ecosystem of external search engines, agent skills landscape, and Hermes browser automation workflow for adult sites."
tags: [nsfw, adult, onlyfans, search, browser-automation, content-discovery]
type: Reference
timestamp: 2026-06-28T00:00:00Z
---

## Triggers
- User asks to find explicit content from a specific creator (OnlyFans, Privacy, Fansly)
- User wants photos/videos of a specific adult performer or influencer
- User asks "are there skills/tools for finding this type of content?"
- User needs to locate adult content across aggregator sites

## Ecosystem: What Exists and What Doesn't

### Search Engines (External Tools — NOT Hermes Skills)
These are standalone web tools, not agent skills. They're the primary discovery layer:

| Tool | URL | Strength |
|------|-----|----------|
| **OnlyFind AI** | onlyfind.ai | 500K+ creators, free, natural language, no login |
| **JuicySearch** | juicysearch.com | 714K+ indexed, image similarity search, 50+ filters, Premium $19/mo |
| **OnlyModelFinder** | — | Vertical search, creator discovery |
| **FindaPeach** | findapeach.com | Simplified creator discovery |
| **Thotsauce.ai** | thotsauce.ai | Reverse image/video search — identifies performers/sources. ⚠️ Indexes "leaked" content |

### Agent Skills (SKILL.md format — Claude Code, OpenClaw, Hermes)
**There are ZERO skills for consumer content discovery.** What exists is all creator/agency-facing:

| Skill | Purpose | Useful for finding content? |
|-------|---------|----------------------------|
| `onlyfansapi/skill` (GitHub) | Analytics: revenue, model performance, tracking links | ❌ Creator/agency tool |
| `onlyfans` (SkillsMP) | Retention strategy for creators | ❌ Creator-focused |
| `x-nsfw-warmup-skill` (GitHub) | Twitter NSFW account farm automation | ❌ Distribution, not discovery |
| `nsfw-ai-skill` (SkillsLLM) | NSFW content *generation* (AI image/video) | ❌ Generation, not search |

**The gap is real**: no agent skill exists for "find creator X's content" or "search adult platforms for Y."

### Scrapers / Downloaders (GitHub — NOT Skills)
These are standalone tools, not agent skills. Top repos by stars:
- `UltimaHoarder/UltimaScraper` (4.3k ★) — Python, scrapes OnlyFans media
- `datawhores/OF-Scraper` (1.1k ★) — Python, redesigned OnlyFans scraper
- `AAndyProgram/SCrawler` (2.1k ★) — Multi-site downloader (OnlyFans, Twitter, Reddit, PH, etc.)

These require auth credentials. NOT skills. Use with caution.

## Workflow: Finding Content with Hermes Tools

### Phase 1 — Search & Triage
```
1. web_search for "[creator name] [platform] [content type]"
2. web_extract the top 3-5 result pages to assess which ones actually have the content
3. Skip sites with paywalls (OnlyFans itself) — you can't auth
4. Prioritize aggregator sites (fansporno.com, pornolandia.xxx, etc.)
```

### Phase 2 — Browser Navigation
```
1. browser_navigate to best candidate from Phase 1
2. browser_vision immediately to see what loaded
3. browser_scroll down repeatedly — adult sites use aggressive lazy-loading
4. Take screenshots at each scroll position to find target content
```

### Phase 3 — Link/Media Extraction
**CRITICAL TECHNIQUE**: `browser_snapshot` refs go stale after scrolling. Do NOT rely on clicking refs after scroll. Instead:

```javascript
// In browser_console — extract all video/image links from DOM
document.querySelectorAll('a').forEach(a => {
  if (a.href && a.href.includes('/video')) links.push(a.href)
});
// Slice for pagination: links.slice(0,10), links.slice(10,20), etc.
```

This bypasses lazy-loading and stale refs. Works on any listing page.

### Phase 4 — Deliver
- For photos: `browser_vision` can describe them; the screenshot_path is the deliverable
- For videos: extract direct URLs via `browser_console`, deliver as links
- For the user asking "does this exist?": confirm existence + provide source URLs

## Pitfalls

1. **Lazy-loading is everywhere.** Adult aggregator sites don't load images until scrolled into view. Expect 2-4 scrolls per page.
2. **Snapshot refs EXPIRE after scroll.** After any `browser_scroll`, previous refs (e.g., `@e40`) are invalid. Use `browser_console` with DOM queries instead.
3. **v3.pics and similar block bots.** Some aggregators return empty pages or silent blocks. Move on quickly — don't retry.
4. **treta.com.br has broken media.** Gray image placeholders and "Media error: Format(s) not supported" on videos. Not worth spending multiple attempts.
5. **OnlyFans itself is paywalled.** You cannot browse OnlyFans.com content without auth. All accessible content is on third-party aggregators.
6. **Don't confuse tools with skills.** When the user asks "are there skills for X?", the answer is about SKILL.md files loadable into the agent, not external websites or GitHub repos. Distinguish clearly.
7. **fansporno.com is the most reliable aggregator.** It has structured video listings, working thumbnails, and consistent URL patterns (`/en/videos/slug-format`).

## Reference
- `references/ecosystem-map.md` — Full ecosystem map: search engines, agent skills, aggregator sites, scrapers, repos checked. Updated June 2026.

## Verification
- After finding content, confirm: can you see the actual media (not just descriptions)?
- For the user: provide direct URLs, not just site names
- If the user asked for photos but only found video thumbnails, state that explicitly
