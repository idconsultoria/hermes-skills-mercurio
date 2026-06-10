# Source Categorization by Cron

This is the specific source layout for the IAF pipeline. Each cron handles one category with staggered timing.

## Cron #1 — General AI News (04:00)
**Type**: Broad web search for AI developments
**Tools**: web_search
**Queries examples**:
- "artificial intelligence news today" site:techcrunch.com OR site:venturebeat.com OR site:theverge.com OR site:theregister.com
- "generative AI" "latest developments" "today"
- "AI" "machine learning" "breakthrough" site:reuters.com OR site:bloomberg.com OR site:arstechnica.com
- "large language model" "release" OR "launch" OR "announcement"
- "AI agents" "latest" "update"

**Output**: Structured markdown with title, source, 1-2 sentence summary per item. Prioritize: announcements, product launches, research breakthroughs, funding news.

## Cron #2 — Specialized AI Newsletters (04:15)
**Type**: Direct content extraction from curated newsletters
**Tools**: web_extract
**Sources**:
- https://www.therundown.ai/ — daily AI news roundup (extract latest post)
- https://www.superhuman.ai/ — AI productivity news
- https://importai.substack.com/ (if applicable)
- https://lastweekin.ai/ (if applicable)

**Output**: Extract full content, filter for items that are:
(a) Relevant to practitioners, not just consumers
(b) Practical applications, not just hype
(c) Underserved by the general news cron above

## Cron #3 — Reddit Discussions (04:30)
**Type**: Forum scraping
**Tools**: web_extract with targeted Reddit URLs + web_search with site:reddit.com
**Subreddits** (in priority order):
1. r/artificial — broad AI discussion
2. r/LocalLLaMa — open-source LLM community
3. r/ChatGPTPro — professional ChatGPT users
4. r/AIAssisted — AI-assisted workflows
5. r/LLMDevs — LLM developers
6. r/SaaS — SaaS builders using AI
7. r/Singularity — AI futurism
8. r/datascience — data science + AI
9. r/MachineLearning — ML research
10. r/AIethics — ethics discussions

**How to scrape**:
- Hot posts (past 24h) via old.reddit.com/r/[sub]/hot/.json
- Top posts (past 24h) via old.reddit.com/r/[sub]/top/?sort=top&t=day
- Search: `site:reddit.com/r/[sub] "AI" OR "LLM" OR "generative"`

**Output**: Per subreddit: title, upvotes, link to discussion, 2-3 sentence summary of the thread's value. Flag threads about practical tips, tool comparisons, and real usage stories.

## Cron #4 — Hacker News (04:45)
**Type**: Community discussion scraping
**Tools**: web_extract (textise dot iitty) + web_search
**Sources**:
- https://news.ycombinator.com/front (front page)
- https://hn.algolia.com/api/v1/search?tags=front_page (API)
- https://news.ycombinator.com/newest (recent)

**Focus**: AI-related posts only
- Filter by keywords: AI, LLM, GPT, Claude, Gemini, generative, agent, transformer
- Pay attention to discussion threads — HN comments often have high-signal critiques

**Output**: Post title, points, link, 1-2 sentence summary of both the article AND the top comments' sentiment.

## Cron #5 — X / Social / Other (05:00)
**Type**: Social media and discussion forum search
**Tools**: web_search
**Sources**:
- X/Twitter discussions: `site:x.com OR site:twitter.com "generative AI" OR "AI" filter:follows`
- LinkedIn: `site:linkedin.com "AI" "practical" OR "workflow" OR "tool"`
- Medium/Towards Data Science: `site:medium.com/towards-data-science AI`
- Dev.to: `site:dev.to AI`

**Output**: Notable threads, practitioner tips, tool recommendations, with links.

## Output Format for ALL Collectors

Each collector must save its output to a structured markdown file following this format:

```markdown
# [Source Name] — [Date]

## Metadata
- Cron: [Name]
- Run at: [timestamp]
- Items found: [N]
- Source status: ✅ / ⚠️ / ❌

## [Section Header]

### [Item Title]
🔗 [URL]
- Summary: [1-2 sentences]
- Why it matters: [1 sentence]
- Tags: #tag1 #tag2

---
```

This format ensures the synthesis cron can parse all collector outputs uniformly.
