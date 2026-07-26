# Brazilian Agricultural SaaS — Competitor Landscape (July 2026)

**Source session:** Competitor research for VERO (fruticultura/viticultura SaaS)  
**Date:** 2026-07-21  
**Research method:** Direct `web_extract` on competitor URLs (web_search was non-functional; see `brazilian-market-web-blockage.md`)

## Verified Competitor URLs That Worked

These URLs returned rich content via `web_extract`:

| Company | URL That Worked | URL That Failed |
|---------|----------------|-----------------|
| Aegro | aegro.com.br | — |
| AGRO365 | **agro365.app** | agro365.com.br (blocked: private network) |
| MyFarm | myfarm.com.br | — |
| SAA Software | saasoftware.com.br | — |
| Nuvem Rural | **nuvemrural.com** | nuvemrural.com.br (522 timeout) |
| Siagri | siagri.com.br | — |
| Agrosmart | agrosmart.com.br | — |
| FieldView (Bayer) | climate.com/pt-br.html | — |
| Cropman | cropman.com.br | — |
| JetBov | jetbov.com | — |
| Embrapa (AGRO365 partner) | embrapa.br/busca-de-projetos | — |

**Key finding:** Two competitors required alternative TLDs to reach:
- AGRO365: `.com.br` blocked as private network → `.app` worked fully
- Nuvem Rural: `.com.br` timed out (522) → `.com` worked

## Unreachable Competitor

| Company | Status | Evidence |
|---------|--------|----------|
| Pomartec | 🚨 Site appears dead/abandoned | pomartec.com.br → 404 on ALL pages. Wayback Machine captcha'd. Instagram login-walled. LinkedIn company page exists ("Software para fruticultura") but no recent activity. Google Play app not found. |

## Market Patterns Discovered

### Pricing
- **100% of Brazilian agricultural SaaS use consultative/demo-based sales**
- No competitor publishes prices publicly
- Common CTAs: "Agende uma Demonstração", "Teste grátis", "Fale conosco via WhatsApp"
- `/planos/`, `/precos/`, `/pricing/` pages universally return 404
- Aegro uniquely offers: NF-e gratuita as entry hook, points exchange (Orbia, Bayer)

### Standard Features (table stakes)
Every agricultural SaaS in Brazil offers:
- Financial management (contas a pagar/receber, fluxo de caixa)
- Field operations (planejamento de safra, apontamentos)
- Stock/inventory control
- Fiscal integration (NFe, SEFAZ)
- LCDPR (Livro Caixa Digital do Produtor Rural)
- Some form of mobile app

### Differentiators by Niche
- **Aegro:** Aegro Insights (NF-e price comparison), free unlimited NF-e
- **AGRO365:** Embrapa ABC Corte partnership, fruit harvest module, multi-farm support
- **MyFarm:** Aliare ecosystem, modular structure, 7-day free trial
- **SAA Software:** Cotton-specific module (fardo GPS, HVI integration)
- **Nuvem Rural:** AgroFit database integration, extreme simplicity, small-farmer focus
- **Agrosmart:** Climate intelligence, irrigation, ESG compliance
- **FieldView:** Machine telemetry, precision ag, Bayer science integration
- **Siagri:** ERP for distributors/cooperatives (not farm management)

### Market Gaps (July 2026)
1. **MIP (Integrated Pest Management)** — no competitor offers structured MIP as a module
2. **LMR Alerts (Maximum Residue Limits)** — zero coverage; critical for fruit export
3. **Smart irrigation inside ERP** — only Agrosmart touches irrigation, but as a separate platform
4. **Harvest-to-cooperative flow** — no integrated romaneio/classification/payment flow for cooperatives
5. **Pomartec vacuum** — the only fruit-farming-focused competitor appears to have shut down

## Competitor Scale Metrics (from public claims)

| Player | Claimed Scale |
|--------|--------------|
| Aegro | +4M ha managed, +R$50B in sales, +R$10B in NF-e |
| Agrosmart | +100K producers, +90 crops, +48M ha, 9 countries |
| Siagri (Aliare) | 6,000+ establishments, 84K users, 1,100+ employees, 40% share in input resale |
| AGRO365 | Counter shows "0" — likely incomplete/new site |
| Others | No public metrics |

## Recommended Research Approach for Brazilian Ag SaaS

1. **Start with `web_extract` on known competitor URLs** — skip `web_search` entirely
2. **Try alternative TLDs** (.app, .com, .agr.br) when .com.br fails
3. **Check Embrapa partnerships** — being an Embrapa partner is a strong credibility signal
4. **LinkedIn for dead-site verification** — if the main site is down, LinkedIn confirms existence and positioning
5. **Feature comparison via site navigation** — competitor feature pages and FAQs reveal what they do/don't offer
6. **Pricing is always hidden** — don't hunt for it; note the pattern and benchmark from industry knowledge

## References

- Aegro demo page: conhecimento.aegro.com.br/contato-demonstracao-aegro (HubSpot landing page, worked)
- AGRO365 features: agro365.app/software/ (full feature list, very detailed)
- Embrapa AGRO365 project: embrapa.br/busca-de-projetos/-/projeto/220327 (government source, worked)
- Output report: /opt/data/relatorio-concorrentes-vero.md (the full competitor analysis from this session)
