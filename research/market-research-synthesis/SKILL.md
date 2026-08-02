---
name: market-research-synthesis
description: "Produce market analysis reports — personas, journeys, expectations, behavior.

Load this skill when conducting market research for Brazilian/LATAM markets where web research tools face comprehensive blocking. Produces structured reports covering buyer personas, customer journeys, expectations hierarchies, purchasing behavior, and retention/fidelization. Pivots to domain-knowledge synthesis with transparent caveats when web tools fail."
category: research
type: Research
timestamp: 2026-07-12T00:00:00Z
---

# Market Research Synthesis

Produce structured market analysis reports covering buyer personas, customer journey, expectations, purchase behavior, and retention. Designed for markets where web research tools may face comprehensive blocking.

## Trigger Conditions

Load this skill when:
- User asks for market research, persona analysis, customer journey mapping, or GTM research
- User asks about "perfil do aluno", "jornada do cliente", "comportamento de compra", "expectativas", "retenção e fidelização"
- The target market is Brazilian/LATAM (expect web research tools to fail)
- User wants a comprehensive report with data and strategic implications

## Output Structure

For comprehensive market analysis reports, cover these sections:

### 1. Personas (buyer/user profiles)
- 3-5 personas with demographic profiles, motivations, objections, willingness to pay, purchase behavior
- Percentage estimates of market share per persona
- Specific to the market/industry (e.g., technology courses, SaaS, consumer goods)

### 2. Customer Journey (antes, durante, depois)
- Pre-purchase phase: triggers, research duration, channels, friction points, drop-off rates
- During product/course: critical abandonment moments with rates, factors that reduce churn
- Post-purchase: what drives referrals, what creates detractors

### 3. Expectations Hierarchy
- Ranked attributes by persona (what they value most → least)
- Weight percentages where available
- Premium willingness-to-pay drivers (what makes them pay 30-60% more)

### 4. Purchase Behavior
- When they buy (time of day, day of week, payday cycles, seasonal peaks) with percentages
- Research-to-purchase timeline by price tier
- Objections by price band
- Urgency triggers that work in the target market

### 5. Retention & Fidelization
- What drives repurchase (weighted factors with percentages)
- What causes abandonment (reasons with percentages)
- Short/medium/long-term retention strategies
- Cross-sell/upsell conversion rates between product tiers

### 6. Strategic Implications
- Pricing recommendations by tier
- Launch timing strategy
- Retention hooks between products
- Specific to the user's project/product

## Research Methodology

### Primary Approach: Web Research

1. **Start with web_search** across multiple queries covering all research areas
2. **Extract from known sources** — government databases (INEP, ABED), industry associations, edtech company blogs, news sites
3. **Cross-validate** findings across sources

### Fallback: Domain Knowledge Synthesis (CRITICAL)

When web research tools fail — watch for the **triple-blockage pattern**:

| Signal | Meaning |
|--------|---------|
| `web_search` returns `{"data": {"web": []}}` for ALL queries | Backend issue, NOT "no results exist" |
| `web_extract` returns 404s or Cloudflare pages for most URLs | Anti-bot protection on target sites |
| `browser_navigate` triggers CAPTCHA/Cloudflare challenge | Browser-based search also blocked |

**Do NOT keep retrying.** When all three signals fire:

1. **Acknowledge the limitation** to the user
2. **Compile from domain knowledge** — use what you know about the market, citing known benchmarks, industry reports, and public data points
3. **Label data provenance clearly** — distinguish verified data from benchmarks/estimates
4. **Structure the output** exactly as if web research had succeeded — same sections, same level of detail
5. **Save as a well-formatted markdown file** for the user to review and validate
6. **Note in the methodology section** which sources are public/verified vs. domain estimates

### Brazil-Specific Challenges

Brazilian websites deploy aggressive anti-bot protection:
- **Cloudflare:** Nearly all Brazilian commercial blogs, news sites, and edtech portals use Cloudflare bot protection
- **CMS migration:** Many Brazilian content sites have restructured blogs, making old URLs return 404
- **Google/Bing CAPTCHAs:** Both search engines trigger CAPTCHA for automated access from cloud IPs
- **JavaScript requirements:** Most Brazilian sites require JS execution — raw curl fails

**Verified persistent sources** (Brazilian market, as of July 2026):
- INEP/MEC (gov.br) — Censo da Educação Superior: raw data available but requires JS for navigation
- ABED (abed.org.br) — Censo EAD.BR: often blocked but is the primary source for distance education data
- Brasscom — IT workforce deficit data: available through press releases and news coverage
- Hotmart, Eduzz, Sympla — transaction data: generally blocked, use second-hand citations from news articles
- **Wikipedia (pt.wikipedia.org)** — API via terminal works reliably for baseline statistics. Passos: (a) `curl -sL "https://pt.wikipedia.org/w/api.php?action=query&titles=TITLE&format=json&prop=extracts&exintro=1&explaintext=1" -o /tmp/wiki.json`, (b) `python3 -c "import json; d=json.load(open('/tmp/wiki.json')); pages=d['query']['pages']; [print(v.get('extract','')) for v in pages.values()]"`. Use para dados econômicos, demográficos, educacionais — sempre o primeiro passo antes de perseguir portais bloqueados.
- **Banco Central do Brasil (bcb.gov.br)** — JS-heavy frontend but static HTML structure accessible via curl. Use for economic indicators, Open Finance stats, and inflation data.
- **B2C fintech pricing pages** — B2C Brazilian fintech apps DO publish prices openly (e.g., organizze.com.br/planos). The "never publishes prices" rule applies to B2B enterprise SaaS only. Always try `/planos`, `/precos`, `/pricing` on consumer-facing apps before falling back to benchmarks.

See `references/brazilian-market-web-blockage.md` for the full blockage pattern, specific blocked sites, and tested workarounds.
See `references/brazilian-agricultural-saas-landscape.md` for a worked example of competitor analysis in the Brazilian ag SaaS vertical (July 2026), including verified URLs, alternative TLD patterns, and market gaps.
See `references/brazilian-fintech-personal-finance-landscape.md` for a worked example of market research in the Brazilian personal finance app vertical (July 2026), with competitor pricing data, Open Finance context, and market sizing.

## Pitfalls

- **Don't fight the blockage.** If web_search + web_extract + browser all fail in the first 3-5 attempts, pivot to domain-knowledge synthesis immediately. Each retry costs 30-60 seconds with no ROI.
- **Don't fabricate data.** When using domain knowledge, use phrases like "benchmarks typically show", "industry data suggests", "estimated at". Never present estimates as verified facts.
- **Don't skip the strategic implications section.** The user needs actionable recommendations for their specific project/product, not just raw market data.
- **Brazilian URLs are unstable.** Blog posts from 2022-2024 on Brazilian edtech sites have a high probability of 404. Prefer .gov.br sources and industry-wide reports over individual blog posts.
- **Language matters.** Research queries for Brazilian markets MUST be in Portuguese. English queries return sparse or irrelevant results for Brazil-specific data. But web_search tool may fail regardless of language — the issue is the backend, not the query.
- **Brazilian B2B SaaS never publishes prices.** Enterprise B2B SaaS companies universally use demo-based/consultative sales. "Planos", "Preços", and "Pricing" pages return 404 or redirect to "fale conosco". **EXCEPTION:** B2C fintech/consumer apps (Mobills, Organizze, etc.) DO publish transparent pricing. Distinguish the segment before spending time hunting — check if the product serves consumers (likely published) or enterprises (likely hidden).
- **Alternative TLDs often work when .com.br fails.** Many Brazilian companies use non-obvious domains: .app, .com (without .br), .agr.br. When the obvious .com.br returns errors or blocks, try alternative TLDs. LinkedIn company pages also reliably confirm existence and positioning even when the main site is fully down.

## Direct-URL Extraction Technique (CRITICAL)

When `web_search` returns empty arrays but you have a list of target companies/URLs, **skip search entirely** and go directly to `web_extract` with the known URLs. This is consistently the most productive path:

1. Batch up to 5 competitor URLs in one `web_extract` call
2. For sites that fail in `web_extract` (anti-bot), fall back to `browser_navigate`
3. For sites that are fully down (404 on all pages), use LinkedIn company pages for positioning confirmation
4. When a site loads partially, use `read_file` with offset/limit on the cached copy to get the full content

This approach yielded rich data for 5/7 competitors in one session even when `web_search` was completely non-functional across 10+ queries.

## Competitor Analysis Workflow (Brazilian Market)

When the task is competitor/market analysis for a Brazilian vertical:

1. **Map known players** from the user's brief — they usually name the top competitors
2. **Batch-extract competitor websites** via `web_extract` (5 URLs per call)
3. **Check segment: B2C vs B2B early.** Consumer fintech/apps likely publish prices on `/planos` or `/precos`. Enterprise B2B SaaS hides them behind demo walls. Distinguish before spending time hunting.
4. **Build a comparison matrix** early: features, pricing model, target audience, differentiators, scale metrics
5. **Identify pricing patterns**: If the segment is B2B, note consultative sales as market norm (and potential differentiator if the client adopts transparent pricing). If B2C, collect all published prices and identify the market range.
6. **Hunt for gaps**: focus on features NO competitor offers (checking site menus, FAQ, feature pages)
7. **Note exit signals**: competitors with dead websites, 404s across all pages, or empty social media are market exit signals — these are opportunities for the client
8. **Save as structured markdown** with tables for features, pricing, and a dedicated "gaps and opportunities" section

See `references/brazilian-agricultural-saas-landscape.md` for the full competitor data from the agricultural SaaS session (July 2026) as a reference template.
See `references/brazilian-fintech-personal-finance-landscape.md` for the fintech/personal-finance-app vertical (July 2026) with competitor pricing data and market sizing.
