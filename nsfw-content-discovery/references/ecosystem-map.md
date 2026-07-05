# Adult Content Discovery Ecosystem — June 2026

## Search Engines (Standalone Web Tools)

### OnlyFind AI
- URL: https://onlyfind.ai
- Database: 500,000+ verified creators (OnlyFans, Fansly, Fanvue, Patreon)
- Cost: Free, no login required
- Features: Natural language search, AI-powered intent understanding, 3 modes (Natural/Creator/Tag)
- Privacy: Anonymous, no personal data stored
- Best for: Quick discovery of creators by description

### JuicySearch
- URL: https://juicysearch.com
- Database: 714,000+ creators indexed
- Cost: Free basic / Premium $19/mo
- Features: Natural language, image similarity search (upload photo → find similar creators), 50+ filters, Visual Match (AI sees photo content), Discovery Mode (personalized feed), Managed Account Detection
- Accuracy: 9/10 claimed
- Best for: Power users, image-based search, filtered discovery

### OnlyModelFinder
- Vertical search engine for OnlyFans creator discovery
- Acts as discovery bridge since OnlyFans has no built-in search

### FindaPeach
- URL: https://findapeach.com
- Simplified OnlyFans creator discovery

### Thotsauce.ai
- URL: https://thotsauce.ai
- Type: Reverse image/video search for adult content
- Features: Upload screenshot/video → find source, identify performers, find similar content
- Coverage: Millions of indexed adult video frames
- ⚠️ Warning: Results include "leaked" tagged content

### NSFWBase
- URL: https://nsfwbase.com
- Indexes videos from: Pornhub, Xvideos, xHamster, VK
- NOT OnlyFans-specific

## Agent Skills (SKILL.md Format)

### onlyfansapi/skill
- GitHub: https://github.com/onlyfansapi/skill
- Stars: 11
- Type: Agent skill for Claude Code, OpenClaw, Hermes, etc.
- Purpose: OnlyFans *analytics* — revenue summaries, model performance, tracking link analytics
- Requires: onlyfansapi.com account + API key
- For: Creators/agencies managing accounts
- NOT for: Consumer content discovery

### x-nsfw-warmup-skill
- GitHub: https://github.com/huangji6693-max/x-nsfw-warmup-skill
- Type: Claude Code / OpenClaw skill
- Purpose: X (Twitter) NSFW account farm automation
- For: Automating adult content distribution on Twitter
- NOT for: Content discovery

### nsfw-ai-skill
- Platform: skillsllm.com
- Purpose: NSFW AI content *generation* (image, video, text)
- NOT for: Finding existing content

### onlyfans (SkillsMP)
- Platform: skillsmp.com
- Purpose: Creator retention strategy
- For: OnlyFans creators
- NOT for: Consumer content search

## Aggregator Sites (Where Content Actually Lives)

### Fans Porno
- URL: https://fansporno.com
- Profile: /en/models/mc-mirella (example)
- Video URL pattern: /en/videos/slug-format
- Features: Structured listings, working thumbnails, video duration, ratings, category tags (Anal, Big Ass, etc.)
- Reliable: Yes — best aggregator tested
- Extracted 30 videos from MC Mirella profile

### Pornolandia
- URL: https://www.pornolandia.xxx
- Album URL pattern: /album/{id}/slug
- Features: Photo galleries, lazy-loaded images, related albums section
- Photos per album: 55 (MC Mirella example)
- Content type: Mostly sensual/teasing, less explicit than fansporno

### Treta
- URL: https://www.treta.com.br
- Article example: /vazou-mc-mirella-nua-pelada-e-sem-calcinha-no-onlyfans/
- Content: Blog-style articles with embedded media
- Issues: Broken images (gray placeholders), broken videos ("Media error: Format(s) not supported")

### v3.pics
- URL: https://v3.pics
- Pattern: /fotos+da+{name}+pelada
- Content: Aggregated images from multiple sources (pornolandia, treta, vazounudes, etc.)
- Issues: Bot blocks, returns empty pages

## Scrapers / Downloaders (GitHub Tools — NOT Skills)

| Repo | Stars | Language | Purpose |
|------|-------|----------|---------|
| UltimaHoarder/UltimaScraper | 4.3k | Python | Scrape OnlyFans media |
| AAndyProgram/SCrawler | 2.1k | VB.NET | Multi-site media downloader (OF, Twitter, Reddit, IG, TikTok, PH, etc.) |
| datawhores/OF-Scraper | 1.1k | Python | Redesigned OnlyFans scraper |
| DIGITALCRIMINAL/ArchivedUltimaScraper | 965 | Python | Scrape OF + Fansly |
| yaroslaff/nudecrawler | 372 | Python | Crawl telegra.ph for nudes |
| sim0n00ps/OF-DRM | 253 | C# | Download DRM-protected OF videos |

These require OnlyFans auth credentials. Not agent skills.

## Hermes Skills Repositories Checked

- Runtime skills (54): Zero adult/NSFW skills
- Undermybelt/hermes-skills (1,422 SKILL.md files): Zero adult/NSFW skills
- awesome-hermes-agent (0xNyk): Zero adult/NSFW skills listed

**Conclusion**: No Hermes skill exists for adult content discovery as of June 2026. This skill (`nsfw-content-discovery`) is the first.
