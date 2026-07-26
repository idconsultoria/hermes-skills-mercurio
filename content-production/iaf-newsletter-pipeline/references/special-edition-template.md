# Special Edition HTML Template

Reference for creating IAF special edition HTMLs. Based on the canonical
`especial-gpt56.html` (the first special edition whose template was reused).

## When to use

When the user requests a special edition of the IAF newsletter — a deep-dive on a
single topic (model launch, regulatory event, major industry shift). Distinct from
daily editions which aggregate 20+ items across sections.

## Research Rules — Multi-Source Mandatory

> ⚠️ **O anúncio oficial NÃO é suficiente.** Edições especiais exigem pesquisa em
> múltiplas fontes independentes (mínimo 5, ideal 8+). O blog/post oficial é o ponto
> de partida, não o ponto final.

**Fontes obrigatórias por tipo de edição:**

| Tipo de Edição | Fontes Esperadas |
|----------------|-----------------|
| Lançamento de modelo | Blog oficial + 2+ veículos de tech (9to5Google, The Verge, TechCrunch) + 1+ análise de benchmarks (OfficeChai, Artificial Analysis, BenchLM) + 1+ comunidade (Reddit, Hacker News) |
| Evento regulatório | Documento oficial + 2+ análise jurídica + 2+ reação da indústria |
| Mudança de mercado | 3+ veículos financeiros + 2+ análise de consultoria + dados primários |

**O que buscar além do anúncio oficial:**
- Comparações competitivas com modelos/produtos rivais (quem lidera em quê)
- Contexto omitido (atrasos, problemas, controvérsias)
- Dados de benchmarks independentes (não apenas os auto-reportados)
- Reação da comunidade (Reddit, HN, Twitter)
- Preços dos concorrentes para escala
- Histórico da família/linha de produto (timeline)

**⚠️ Pitfall real (21/07/2026):** Edição do Gemini 3.6 Flash começou usando apenas o Google Blog como fonte. O usuário interrompeu com "Não se baseie só no blog da Google, procure bem mais fontes sobre o tema". O anúncio oficial não mencionava: que o 3.5 Pro está atrasado (Android Headlines), comparações com GPT‑5.6 Luna e Grok 4.5 (OfficeChai), resultados reais do Flash Cyber no motor V8 (CyberSecurity News), que o Flash-Lite supera o 3 Flash original (9to5Google), ou a data de corte avançada para março/2026 (9to5Google). Sem essas fontes, a edição teria sido um release regurgitado — não uma análise.

## File naming

```
/opt/data/cron/history/iaf-especial-{slug}.html    ← working copy
/opt/data/iaf-edicoes-archive/edicoes/especial-{slug}.html   ← deployed copy
```

## CSS Architecture

The special edition uses its own self-contained `<style>` block (not the daily
newsletter template at `/opt/data/references/iaf_v3_reference.html`). The daily
classes like `.hot-take-box`, `.deep-dive-card`, `.news-grid` do NOT apply here.

### Color scheme

The accent color changes per edition to match the topic's identity:

| Edition | Accent Primary | Accent Hover | Cover Gradient |
|---------|---------------|--------------|----------------|
| GPT‑5.6 | `#0a8f88` (teal) | `#06b8a0` | Navy → red |
| Kimi K3 | `#5b3cc4` (purple) | `#7c5ce7` | Navy → purple |
| Gemini 3.6 Flash | `#1a73e8` (Google blue) | `#4285f4` | Navy → blue |

To change colors, edit the `:root` block:
```css
--accent-primary: #5b3cc4;
--accent-hover: #7c5ce7;
--accent-muted: rgba(91, 60, 196, 0.08);
--border-color: rgba(91, 60, 196, 0.18);
```

And update all `rgba(91,60,196,...)` and `rgba(10,143,136,...)` references
throughout the CSS to match the new accent.

The cover page gradient (`linear-gradient` on `.cover-page`) should evoke the
topic — use colors from the company/product's visual identity.

### Typography (fixed — do not change)

```
--font-title: 'Outfit'       → titles, stat numbers, cover
--font-body: 'Inter'         → body text, cards
--font-code: 'Fira Code'     → metadata, labels, tables, timeline dates
--font-editorial: 'Spectral' → editorial prose, pullquotes, cover subtitle
```

Google Fonts link in `<head>` must include all four families.

### CSS class inventory

| Class | Purpose | Notes |
|-------|---------|-------|
| `.cover-page` | Full-viewport cover | Gradient bg, grid overlay, glow orbs, SVG curve |
| `.cover-content` | Centered text on cover | Title, subtitle, badge, divider, meta |
| `.cover-badge` | "✦ Edição Extraordinária" pill | |
| `.cover-title` | H1 with gradient accent word | |
| `.cover-subtitle` | Italic subhead | |
| `.page` | Content page container | grid bg + ambient glow inside |
| `.bg-grid` | Subtle grid pattern overlay | |
| `.ambient-glow` / `.ambient-glow-2` | Soft radial gradients | |
| `.content` | z-index wrapper for page content | |
| `.special-banner` | Small gradient pill | Reused on section header pages |
| `.header` / `.header-left` / `.header-right` | Page header with metadata | |
| `.newsletter-title` / `.newsletter-subtitle` | "Manhã Aumentada" + tagline | |
| `.header-metadata-box` / `.meta-row` | Date, theme metadata | |
| `.iaf-logo-container` | IAF logo (acronym + tagline) | |
| `.editorial-section` / `.editorial-text` | Editorial prose | Uses `.dropcap`, `.no-indent` |
| `.editorial-pullquote` | Blockquote with left border | Has `.attribution` child |
| `.stat-row` / `.stat-item` / `.stat-number` / `.stat-label` | 4-column stat display | |
| `.section` / `.section-title` | Section headers with SVG icon | |
| `.feat-grid` / `.feat-card` / `.feat-card-title` / `.feat-card-body` | Feature cards (vertical stack) | |
| `.feat-icon` | SVG icon inside feat-card-title | |
| `.bench-table-wrap` / `.bench-table` | Comparison table | `.best` and `.delta-pos` for highlights |
| `.variant-table-wrap` / `.variant-table` | Spec comparison table | |
| `.callout-box` | Bordered info box with title | |
| `.impact-card` | Impact analysis card with tag | Uses `.impact-tag` + tag color classes |
| `.timeline` / `.timeline-item` / `.timeline-date` / `.timeline-text` | Vertical timeline | |
| `.sources-block` | Editorial sources footer | |
| `.footer` / `.footer-left` / `.footer-center` / `.footer-right` | Page footer | |

### Tag color classes

```
.tag-business  → terracotta (#c75b3e)
.tag-science   → sage (#5f7a6b)
.tag-security  → amber (#b8860b)
.tag-frontier  → accent primary
```

## Page Structure (recommended ~6 pages)

```
Page 0 — Cover (full viewport, no .page wrapper)
Page 1 — Editorial start (header + first 3-4 paragraphs + pullquote)
Page 2 — Editorial continued + stat row
Page 3 — Editorial conclusion + sources
Page 4 — Architecture / specs (variant table + feat cards)
Page 5 — Benchmarks (bench table + feat cards)
Page 6 — Impact cards + timeline + callout + footer
```

Each page uses `<div class="page">` with:
```html
<div class="page">
  <div class="bg-grid"></div>
  <div class="ambient-glow"></div>  <!-- or ambient-glow-2 on alternating pages -->
  <div class="content">
    <!-- page content -->
  </div>
</div>
```

### Cover page structure

```html
<div class="cover-page">
  <div class="cover-grid"></div>
  <div class="cover-glow-top"></div>
  <div class="cover-glow-bottom"></div>
  <svg class="cover-svg-curve" viewBox="0 0 1000 1000" preserveAspectRatio="none">
    <!-- decorative SVG paths and circles -->
  </svg>
  <div class="cover-content">
    <div class="cover-badge">✦ Edição Extraordinária</div>
    <h1 class="cover-title">Line 1<br><span class="accent-word">Line 2</span><br>Line 3</h1>
    <p class="cover-subtitle">Two-line subtitle with <br>key context</p>
    <div class="cover-divider"></div>
    <div class="cover-meta"><span>DD · Mês · AAAA</span><span>✦</span><span>IAF — IA que Funciona</span></div>
  </div>
  <div class="cover-logo">
    <span class="cover-logo-acronym">IAF</span>
    <span class="cover-logo-tagline">IA que Funciona</span>
  </div>
</div>
```

## Editorial Writing Guide

- **Research first:** Execute the Research Rules above BEFORE writing. Gather 5-8+ sources. The editorial must incorporate facts, comparisons, and context that the official announcement omits. If you can't name at least 3 things the reader wouldn't learn from reading the official blog post, you haven't researched enough.
- **Length:** ~8-12 paragraphs total, spread across 3 pages
- **Opening:** Date-stamped scene-setting with dropcap on first paragraph. Anchor the launch in the week's broader context (what else happened? what does this respond to?)
- **Tone:** Stratechery/Every style — opinionated, analytical, warm
- **Structure:** Hook → context → pullquote → competitive analysis → counterpoint → pullquote → forward-looking conclusion
- **Pullquotes:** 2-3 per editorial, sourced from different outlets (not all from the official blog). At least one should come from an independent analyst or community voice.
- **Stats:** 4-stat row after key numeric claims (use `.stat-row`)
- **Sources:** Footer with 5-8 linked sources in `.sources-block`, spanning at least 4 different domains (not 5 links to the same blog)
- **Language:** Zero anglicisms, PT-BR throughout

## WhatsApp Companion

After deploy, send via WhatsApp bridge:

```bash
cat > /tmp/iaf_whatsapp_{slug}.txt << 'HERMES_EOF'
📰 *IAF — Edição Extraordinária* · DD/MM/AAAA
🌐 https://iaf-newsletter.vercel.app/especial-{slug}

*Editorial hook sentence in bold.* Context and intrigue in normal text. 2-3 sentences max.

🔥 *Destaques*
• [emoji] *Key point* — one-line description
• [emoji] *Key point* — one-line description
• [emoji] *Key point* — one-line description
[optional 4th-5th bullet]

🎯 *Aplicação prática de hoje*
1-2 lines, imperative, actionable today, non-dev accessible.

⚠️ Optional caveat line
HERMES_EOF

curl -s -X POST http://127.0.0.1:3000/send \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'chatId':'120363419131378682@g.us','message':open('/tmp/iaf_whatsapp_{slug}.txt').read()}))")"
```

**Target:** 15-25 lines. Verify `messageId` in response.

## Existing Special Editions (reference)

| Slug | Date | Topic |
|------|------|-------|
| `especial-mythos` | 09/06/2026 | Anthropic Fable 5 / Mythos 5 launch |
| `especial-gpt56` | 26/06/2026 | OpenAI GPT‑5.6 (Sol/Terra/Luna) + gov approval |
| `especial-kimi-k3` | 16/07/2026 | Moonshot Kimi K3 (2.8T open-weight) |
| `especial-gemini-3-6-flash` | 21/07/2026 | Google Gemini 3.6 Flash + 3.5 Flash-Lite + 3.5 Flash Cyber |
