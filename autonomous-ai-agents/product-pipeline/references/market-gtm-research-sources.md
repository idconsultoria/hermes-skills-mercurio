# Market & GTM Research: Source Recommendations & Methodology

> Reference for Fase 2 (Pesquisa) of the product-pipeline when researching go-to-market strategies, 
> online courses, edtech, or digital product markets. Created from Jul 2026 session (GTM research 
> for Brazilian AI-course portfolio).

## Quick Rules

1. **Front-load web_search:** Batch all critical queries in the first parallel `web_search` call. 
   Subsequent queries in the same session often return empty `[]` (rate-limit/quota exhaustion, 
   not backend failure). If later queries fail, fall back to `web_extract` on known URLs — don't 
   keep retrying web_search with different phrasings.

2. **Skip edtech platform blogs** (Thinkific, Kajabi, LearnWorlds, Teachfloor, Mighty Networks, 
   iSpring, CourseStorm, etc.) — they restructured blogs in 2024-2025, causing widespread 404s 
   for articles from 2022-2024. These are structurally unreliable for research.

3. **Prefer these source categories** (verified persistent in Jul 2026):
   - **CRO/marketing research firms:** acceleroi.com, firstpagesage.com, digitalapplied.com, 
     prooflytics.io, grow-conversions.com — excellent for conversion benchmarks, funnel metrics, 
     and industry-specific data.
   - **Market research firms:** gminsights.com, Grand View Research, Statista — for market size, 
     CAGR projections, industry segmentation.
   - **General business/media:** entrepreneur.com, Forbes, HBR.org — for case studies and 
     strategy articles (but HBR often paywalled).
   - **Wikipedia:** Reliable for market definitions and historical context (not blocked by bot detection).

4. **When web sources are exhausted**, augment with domain knowledge but clearly mark what was 
   externally sourced vs. internally synthesized. Cite specific source URLs for quantitative data.

## Verified Source URLs (Jul 2026)

These specific URLs returned useful data and are good starting points for similar research:

| Topic | URL | What It Provides |
|---|---|---|
| Course conversion benchmarks | `acceleroi.com/blog/unlocking-success-exploring-the-average-conversion-rate-for-online-courses` | Funnel-stage conversion rates, price-point benchmarks, traffic source breakdowns |
| Sales funnel benchmarks | `firstpagesage.com/seo-blog/sales-funnel-conversion-rate-benchmarks-2025-report/` | B2B/B2C funnel stage conversion by industry (50+ industries) |
| Industry conversion rates | `digitalapplied.com/blog/conversion-rate-benchmarks-2026-industry-channel` | Conversion by industry, channel, device, with YoY trends |
| E-learning market size | `gminsights.com/industry-analysis/elearning-market-size` | Global market size ($399B in 2022, 14% CAGR), segment breakdowns |

## Domain Knowledge Augmentation Pattern

When web_search returns empty and direct URL extraction hits 404s/blocked pages, the fallback 
approach that delivered a complete report in this session:

1. Extract everything possible from the URLs that DO work (even if only 3-4 of 15+ attempts succeed)
2. Use `browser_navigate` to read full page content for the working sources (deeper extraction)
3. Supplement with domain knowledge in clearly marked sections
4. Use industry-standard frameworks and widely-known practices (e.g., Jeff Walker's Product Launch 
   Formula, cohort-based course models, B2B per-seat licensing) as structure
5. Add numerical estimates with clear caveats ("estimated", "typically", "industry standard")
6. Cite every external data point with its source URL

## Tips for This Research Class

- **Portuguese-language market research:** Brazilian edtech data is harder to find via English queries. 
  Search for "mercado cursos online Brasil", "ABTD" (Associação Brasileira de Treinamento), "Alura", 
  "EBAC", "Escola Conquer" — these Brazilian companies publish some public data.
- **AI/tech course GTM:** Look for "DeepLearning.AI", "Coursera", "DataCamp", "Udacity" case studies.
- **Corporate training B2B:** Mercer Global Talent Trends, LinkedIn Workplace Learning Report, 
  ABTD research are the most cited sources for enterprise L&D budgets.
- **Launch strategies:** Jeff Walker's "Product Launch Formula", Amy Porterfield, and Russell Brunson's 
  books are the reference frameworks — most blog articles on the topic are derivative and short-lived.
