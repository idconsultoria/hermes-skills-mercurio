# Brazilian Market Web Blockage Pattern

**Last verified:** 10 July 2026  
**Session reference:** Market research for technology courses in Brazil (ID Consultoria — Jornada de IA)

## The Triple-Blockage Pattern

When researching Brazilian-market topics, ALL web research channels fail simultaneously:

### Signal 1: web_search returns empty arrays
```
web_search(query="any query about Brazilian market") → {"data": {"web": []}}
```
- Happens regardless of query quality, language (PT or EN), or specificity
- NOT a "no results exist" signal — the backend search provider itself returns empty
- Retrying with different phrasing does NOT help

### Signal 2: web_extract hits 404s or Cloudflare
```
web_extract(urls=["brazilian-blog.com/article"]) → 404 or Cloudflare challenge page
```
- Brazilian commercial sites overwhelmingly use Cloudflare bot protection
- Even major platforms (Hotmart, Alura, EBAC, Trybe, Rocketseat) block automated extraction
- CMS migrations on Brazilian sites make old blog URLs return 404

### Signal 3: browser_navigate triggers CAPTCHA
```
browser_navigate(url="google.com/search?q=...") → "Sorry" / Cloudflare challenge
browser_navigate(url="bing.com/search?q=...") → Cloudflare challenge
```
- Google and Bing both detect cloud IP ranges and require verification
- DuckDuckGo times out or also triggers challenges

## Blocked Sites (Tested July 2026)

| Site | web_extract | browser | curl | Notes |
|------|-------------|---------|------|-------|
| Google Search | N/A | CAPTCHA | JS required | Cloud IP blocked |
| Bing Search | N/A | Cloudflare | JS required | Cloudflare challenge |
| DuckDuckGo | N/A | Timeout | N/A | CDP timeout |
| hotmart.com/blog | 404 on old URLs | N/A | JS required | Blog restructured, old posts gone |
| alura.com.br/artigos | 404 | N/A | N/A | Blog restructured |
| trybe.com (US) | Loads | N/A | N/A | Wrong site — not betrybe.com.br |
| rocketseat.com.br/blog | Loads but JS | N/A | N/A | Categories show, articles don't load |
| rockcontent.com.br | 404 | N/A | N/A | Redirected to analoghq.ai |
| resultadosdigitais.com.br | 404 | N/A | N/A | Blog restructured |
| mundodomarketing.com.br | 404 | N/A | N/A | Blog restructured |
| forbes.com.br | 404 | N/A | N/A | Article not found |
| exame.com | Empty | N/A | N/A | Redirect |
| cnnbrasil.com.br | Empty | N/A | N/A | JS required |
| terra.com.br | Empty | N/A | N/A | JS required |
| sympla.com.br/blog | N/A | N/A | Cloudflare | JS challenge |
| abed.org.br | Blocked | N/A | N/A | Scraping blocked |
| gov.br/inep | Partial | N/A | N/A | Content loads but JS-rendered tabs |
| ead.com.br/blog | 404 | N/A | N/A | Page not found |
| suno.com.br | 404 | N/A | N/A | Article not found |
| neilpatel.com/br | Blocked | N/A | N/A | Anti-bot |
| capterra.com.br | Anti-bot | N/A | N/A | Scrape aborted (document_antibot) |
| g2.com | Anti-bot | N/A | N/A | Scrape aborted (document_antibot) |
| crunchbase.com | Anti-bot | N/A | N/A | Scrape aborted (document_antibot) |
| instagram.com | Anti-bot | Empty page | N/A | Login wall / empty snapshot |
| pitchbook.com | Anti-bot | N/A | N/A | Scrape aborted |
| distrito.me | N/A | N/A | N/A | 404 on startup profiles |
| startups.com.br | N/A | N/A | N/A | 404 on company profiles |
| web.archive.org | N/A | Cloudflare CAPTCHA | N/A | Wayback Machine also captcha'd |

## What DOES Work (Brazilian Market)

### Government sources
- **INEP/MEC (gov.br):** Content loads via web_extract but is sparse (mostly navigation). Raw data downloads may be available via direct PDF/Excel links.
- **IBGE:** Statistical data, generally accessible.

### International sources covering Brazil
- English-language news sites covering Brazilian market (Reuters, Bloomberg)
- International research firms (Statista, Gartner — paywalled but snippets available)
- Academic papers on Brazilian edtech (Google Scholar, SciELO)

### Second-hand citations
- Press releases from Brazilian edtechs picked up by international tech news
- Industry reports summarized by consulting firms (McKinsey, BCG, Bain — Brazil practice)
- Conference talks and slide decks (SlideShare, YouTube)

## The Right Response: Domain Knowledge Synthesis

When the triple-blockage pattern fires:

1. **Stop retrying immediately.** Each attempt costs 30-60 seconds with zero ROI.
2. **Tell the user what's happening.** "Ferramentas de busca web estão enfrentando bloqueios generalizados em sites brasileiros. Vou compilar a análise com base em conhecimento de domínio e benchmarks públicos do setor."
3. **Compile from domain knowledge.** Structure the report exactly as if research had succeeded.
4. **Label data provenance.** Use clear language:
   - "Segundo o Censo EAD.BR 2022-2023 (ABED)..." → verified public data
   - "Dados de mercado indicam que..." → industry benchmark
   - "Estima-se que..." → domain estimate
5. **Save as markdown** with a methodology section that transparently notes the tooling limitations.
6. **Offer to refine** if the user has specific sources they want incorporated.

## Why This Pattern Matters

Without this reference, an agent will waste 5-10 minutes trying different URLs, search engines, and extraction methods — all failing — before giving up. The pattern recognition shortcut saves tokens and produces a useful deliverable instead of an apology.

## Related Patterns

- `deep-research` skill pitfall about web_search returning empty arrays (general case)
- `product-pipeline` skill pitfall about edtech blog restructurings and web_search rate limits
- General Cloudflare bot protection on commercial sites (global pattern, especially aggressive in LATAM)
