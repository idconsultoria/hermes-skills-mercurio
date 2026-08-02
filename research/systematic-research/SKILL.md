---
name: systematic-research
description: "Single-agent deep research via direct source URLs.

Load this skill when web_search is consistently unavailable (returns empty arrays for ALL queries after 2+ attempts) and you need thorough research without multi-agent dispatch. Uses domain knowledge to identify authoritative source URLs, batch parallel web_extract calls, handle blocked/404 pages, and page through large truncated encyclopedia-style articles. Produces cited, structured reports with source attribution. Complementary to deep-research (which covers multi-agent dispatch)."
category: research
type: Research
timestamp: 2026-08-02T00:00:00Z
---

# Systematic Single-Agent Research

Load this when web_search is unavailable (returns empty arrays for ALL queries after 2+ attempts) or when you need focused research on known-authority domains without multi-agent overhead.

## Pipeline

```
web_search fails × 2-4 (all empty)
        │
        ▼
  Step 1: Decompose into N sub-topics
        │
        ▼
  Step 2: Identify 2-5 known authority URLs per sub-topic
        │
        ▼
  Step 3: Parallel web_extract batches (max 5 URLs each)
        │
        ▼
  Step 4: Handle 404s/blocked — browser_navigate or alternatives
        │
        ▼
  Step 5: Read truncated full-article saves from cache
        │
        ▼
  Step 6: Deep-dive into specific sub-concepts found
        │
        ▼
  Step 7: Synthesize into structured report by sub-topic
```

## Step 1: Topic Decomposition

Split the research topic into 3-5 orthogonal sub-topics. Each sub-topic should be independently researchable from a different domain/authority.

**Example decomposition** (CFP IA financial planner research):
1. Psicologia do endividamento / vieses cognitivos
2. Mecânicas de gamificação em apps comportamentais
3. Estratégias de mudança de comportamento (Fogg, nudges)
4. UX em temas sensíveis (dívidas, dark patterns)

## Step 2: Authority URL Identification

Use known domain patterns. This is the critical step — you must know which URL patterns consistently work with `web_extract` for each topic class.

### Behavioral Economics & Cognitive Biases
```
behavioraleconomics.com/resources/mini-encyclopedia-of-be/concept-name/
  → Reliable encyclopedia entries for: loss-aversion, status-quo-bias,
    commitment, precommitment, framing-effect, choice-architecture,
    decision-fatigue, inertia, myopic-procrastination, present-bias,
    anchoring-heuristic, availability-heuristic, cognitive-dissonance,
    default-optionsetting, zero-price-effect

behavioraleconomics.com/nudge-action-overcoming-decision-inertia-in-financial-planning-tools/
  → Research article on financial decision support with data
```

### Gamification & Product Behavior
```
blog.duolingo.com/how-duolingo-streak-builds-habit/
  → Streak mechanics, loss aversion, retention data (+1.7%, 3.6× completion)
blog.duolingo.com/friend-streak/
  → Social gamification, +22% daily lesson completion
blog.duolingo.com/sticking-with-it-tips-for-staying-motivated/
  → Motivation features overview
```

### Behavior Models & Nudge Theory
```
behaviormodel.org
  → Fogg Behavior Model B=MAP (single page, no deep links)
en.wikipedia.org/wiki/Nudge_theory
  → Comprehensive nudge theory with research context
```

### Overview Concepts (Wikipedia — reliable scraping)
```
en.wikipedia.org/wiki/Gamification
en.wikipedia.org/wiki/Behavioral_economics
en.wikipedia.org/wiki/Time_preference
en.wikipedia.org/wiki/Nudge_theory
```

### UX / Design
```
nngroup.com  → Use specific article URLs. 404 common — verify first
medium.com   → Blocks scraping — do NOT rely on. Skip or use browser.
```

## Step 3: Parallel web_extract

Batch all independent URLs in a single call. The runtime executes them concurrently.

```
Call 1: URLs for sub-topic A (e.g., 3 behavioral economics articles)
Call 2: URLs for sub-topic B (e.g., 3 Duolingo blog posts)
Call 3: URLs for sub-topic C (e.g., 2 Wikipedia + behaviorModel)
```

**Limits:**
- Max 5 URLs per web_extract call
- Max ~50K chars per page before truncation
- Subsequent calls can be made immediately after (no serial dependency)

## Step 4: Handle Failures

| Failure Pattern | Handling |
|----------------|----------|
| 404 on page | Try `browser_navigate` to the same URL. If still 404, find alternative source. |
| Medium article | Skip — Medium blocks scraping. Find equivalent content elsewhere. |
| NNGroup article | Try with and without trailing slash; verify first via browser if critical |
| Anti-bot page | Skip — accept the gap and note in report |
| Empty response | Try `browser_navigate(url)` as fallback |

## Step 5: Read Full Truncated Content

`web_extract` truncates at ~15KB. Encyclopedia-style pages (Wikipedia, BehavioralEconomics.com index) are routinely 50K-280K chars. The footer of the truncated output tells you where the full file was saved:

```
Full text saved to: /opt/data/cache/web/<domain>-<hash>.md
To read the omitted middle: read_file(path="...", offset=N, limit=200)
```

**Always read the omitted middle** for:
- Behavioral economics concept pages
- Wikipedia articles
- Any page that seems to stop mid-content

## Step 6: Deep Dive on Specific Concepts

After the first pass, you'll find cross-references to specific sub-concepts:

> "Status quo bias is consistent with loss aversion"
> "Loss aversion has been used to explain the endowment effect"

Follow these cross-references with a second wave of focused URL requests:
```
First pass: concept index page
       │
       ▼
       Found: links to loss-aversion, endowment-effect
       │
       ▼
       Second wave: web_extract to those specific URLs
```

Add a third wave only if the topic demands it and time permits.

## Step 7: Synthesize Structured Report

Organize final report by sub-topic, not by source. Each section should include:
- **Concept** named and defined
- **Source** cited (URL is fine for internal docs)
- **Data/statistics** with numbers where available
- **Implication** for your current project
- **Reference list** at the end

**Format preference** (Brazilian Portuguese audience): structured markdown with tables for comparative data, bullet points for lists, section headers for clarity. Minimize prose blocks.

## When NOT to Use This Pattern

- When web_search IS working — use it as the primary tool, web_extract for known URLs
- When you need multi-domain exploration (web + GitHub + news + academic) — use `deep-research` skill with delegate_task
- When the topic has NO known authority URLs — use web_search to discover them first
- When the single known URL for a concept is Medium.com — find an alternative source

## Comparison with deep-research Skill

| Aspect | systematic-research (this) | deep-research |
|--------|---------------------------|---------------|
| Architecture | Single-agent, parallel web_extract | Multi-agent via delegate_task |
| Best when | web_search is down, known sources exist | Exploratory research, web_search works |
| Concurrency | 5 parallel URL fetches | 3 parallel subagents |
| Reliability | High (simple HTTP) | Medium (subagent timeout risk) |
| Coverage | Focused (known domains) | Broad (multiple channels) |
| Time | 10-30 min | 20-60+ min |
