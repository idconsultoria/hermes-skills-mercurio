---
name: newsletter-curation
description: "Newsletter curation with content sourcing, editorial structure, and subscriber growth strategies. Covers issue formatting, link roundups, commentary style, and sending cadence. Use for: email newsletters, link roundups, weekly digests, curated content, creator newsletters."
version: 2.0.0
author: inference-sh/skills
---

# Newsletter Curation

Create and curate high-quality newsletters with proven editorial frameworks.

## Newsletter Formats

### 1. Link Roundup
5-15 curated links with 1-3 sentence commentary per link.

```markdown
## This Week's Top Picks

### [Article Title](url)
One to three sentences explaining why this matters and what the reader will get from it. Add your take — don't just describe.
```

### 2. Deep Dive + Links
One in-depth analysis (300-500 words) + 5-8 curated links.

### 3. Original Essay
One focused piece (500-1,000 words) with a clear thesis.

### 4. Q&A / Interview
Feature conversation with an expert or practitioner.

### 5. Data/Trends
Numbers, charts, and analysis of trends in your space.

## The Template

```markdown
# [Newsletter Name] — Issue #[N]

## 👋 Hello
[2-3 sentences of personal intro]

## 🔥 The Big Story
[Featured content with your deepest analysis]

## 📚 Worth Reading
### [Title 1](url)
[2-3 sentence commentary with your take]

## 💡 Quick Hits
- [One-liner + link](url)

## 📊 Stat of the Week
[One compelling data point with context]

## 💬 From the Community
[Reader reply, question, or discussion point]
```

## Content Sourcing

### Source Categories

| Source Type | Examples | Best For |
|------------|---------|----------|
| **News** | TechCrunch, The Verge, industry press | Breaking developments |
| **Research** | Papers, reports, surveys | Data-backed insights |
| **Blogs** | Engineering blogs, personal blogs | Practitioner perspectives |
| **Social** | Twitter threads, LinkedIn posts | Hot takes, discussions |
| **Tools** | Product launches, updates | Practical recommendations |
| **Community** | Reddit, HN, forums | Ground-level sentiment |

### Curation Quality Filter

For each piece, ask:
- **Would I send this to a colleague 1-on-1?** If no → don't include.
- **Does it teach something actionable?** If no → consider skipping.
- **Is the source credible?** If no → find better source.
- **Is it timely/relevant?** If no → save for later.
- **Can I add commentary that adds value?** If no → just linking isn't enough.

### Ranking-Driven Editorial Triage

Before placing any item in the newsletter, **score it first** on three criteria (1–10 each):

| Criterion | What it measures |
|-----------|-----------------|
| **Impact** | How much does this move the needle for the reader's industry? |
| **Utility** | Can the reader act on this today? |
| **Intrigue** | Is this novel, surprising, or thought-provoking? |

**Total = Impact + Utility + Intrigue** (max 30). Use the total to:
- **Top 3** → Deep Dive / expanded treatment
- **Remaining news** → Radar / compact format
- **Remaining discussions** → Community section

Also tag each item as **notícia** (news) or **discussão** (discussion/opinion) to route it to the correct section. The scores and tags are **internal editorial tools** — never publish them in the newsletter itself.

**Deduplication rule**: if a discussion covers the same topic as an expanded news item, drop it from the community section or move it to compact format. No topic should appear twice in the same issue.

## Writing Commentary

### What Makes Good Commentary

```
❌ Just describing: "This article talks about X."
❌ Restating the headline: "X is here."
✅ Adding context: "...this is the first production teardown I've seen."
✅ Giving your take: "I'm skeptical about the migration path here."
✅ Connecting dots: "This pairs well with Y's announcement last month."
```

### Commentary Formula

```
[What happened] + [Why it matters to the reader] + [Your take or prediction]
```

## Zero Anglicisms Rule

When writing in Portuguese, **zero anglicisms**. Replace English jargon with Portuguese equivalents. When a foreign term is unavoidable (e.g. "IPO", "GPT"), explain it clearly and didactically the first time it appears.

| Avoid | Use instead |
|-------|-------------|
| keynote | grandes palcos, palestra principal |
| shipar, ship | entregar, lançar |
| brainstorm | chuva de ideias |
| deadline | prazo final |
| feedback | retorno, devolutiva |
| pitch | apresentação, argumento |
| roadmap | roteiro, plano |
| benchmark | referência, comparativo |
| stakeholder | parte interessada |
| hands-on | na prática, mão na massa |

## Critical: Every Item Must Have a Link

Every single item in the newsletter — whether expanded or compact, news or discussion — **MUST include a clickable source URL**. No exceptions.

- Expanded items get a dedicated link line at the bottom.
- Compact items include the link inline (e.g. `— [Leia mais](url)`).
- When collecting source data via delegate_task subagents, the collection prompt MUST include: *"CRITICAL: Every entry MUST include its clickable source URL. No exceptions."*
- After collection, verify: `grep -c 'https\?://' output_file.md` — if zero, the collection failed to preserve links.

## IAF Newsletter Structure

When producing the "IAF — Manhã Aumentada" daily newsletter, use this **exact section order**:

1. **Editorial / Hot Take** — 1–4 paragraphs, opinionated, data-driven, one core argument. First paragraph: bold hook. Following paragraphs: unpack the argument.
2. **Análise (Deep Dive)** — Top 3 items from the ranking, expanded. Each gets: title, 2–4 paragraph analysis, source link. Order by rank score (highest first).
3. **Radar de Notícias** — Remaining news items (not discussions). Compact format: 1–2 lines each, inline link.
4. **Pulso da Comunidade** — Remaining discussions. First 2 expanded (like Deep Dive cards), rest compact. **Must not duplicate topics already covered in Análise**.
5. **Aplicação Prática** — 1 item only. Extensive tutorial-style: step-by-step instructions, tools needed, expected benefit ("O que você ganha" box).
6. **Footer** — Sources line + "Gerado por Hermes Agent".

### WhatsApp Companion Message

After delivering the PDF, send a WhatsApp-friendly text message with this **exact format**:

```
*IAF — Manhã Aumentada* · [DATA]

[Editorial hook — 1-2 sentences that summarize the hot take's core argument]

• [Best material bullet 1]
• [Best material bullet 2]
• [Best material bullet 3]

🎯 [Spoiler of today's practical application]
```

No additional text, sign-offs, or metadata.

### Deduplication (14-Day Context)

Before synthesizing a new issue, **scan the last 14 days of published HTML files** in the history directory. Compare story titles and topics against the current ranking. Drop or relegate to compact any item whose core topic already appeared in a Deep Dive in the last 14 days.

## PDF Rendering (weasyprint)

When converting HTML to PDF on this ARM64 Linux system, Chromium/Puppeteer is not available.
See `references/weasyprint-pdf-tips.md` for weasyprint CSS compatibility notes and the
exact substitution checklist.

Key rule: **Never modify the canonical HTML.** Create a PDF-optimized copy with only
the CSS substitutions that weasyprint can't handle (gradient text, page margins,
box-shadow on wrapper, @keyframes). The original stays intact for browser viewing.

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No consistent schedule | Readers forget you | Same day, same time, every week |
| Links without commentary | You're a bookmark | Add your take on every piece |
| Links missing from items | Reader has no source to verify | Every item gets a link, always |
| Too many links (15+) | Nothing stands out | 5-10 curated picks max |
| Generic subject lines | Low open rates | Tease the best content |
| No personal voice | Reads like an RSS feed | Opinions, personality |
| Anglicisms in Portuguese text | Sounds unnatural, alienating | Use the zero-anglicisms table above |
| Repeating topics across sections | Reader sees the same story twice | Deduplicate Deep Dive vs Community |
