# Brand Identity Extraction from Live Website

## Use Case

When the user asks for a branded presentation/deck/visual for a company (e.g., "prepare a slide for the ID Consultoria meeting"), the workflow is TWO-PHASE:

**Phase 1 — Extract brand identity** from the company's website using browser tools
**Phase 2 — Generate** the design artifact with agy using those extracted specs

**Do NOT skip Phase 1.** agy cannot browse the website and read design spec files. YOU must extract the brand identity and embed it inline in the agy prompt.

## Phase 1: Extract Brand Identity

### Step 1 — Visit the site

```bash
browser_navigate(url="https://empresa.ai")
```

### Step 2 — Extract visual identity via browser_vision

```bash
browser_vision(question="Extraia a identidade visual completa: cores primárias, cores secundárias, logotipo, tipografia (fontes usadas nos títulos, subtítulos, botões e corpo), estilo de botões, ícones, formas (cantos arredondados ou retos), e qualquer padrão visual recorrente.")
```

If the first screenshot misses details, follow up with targeted questions:
```bash
browser_vision(question="Qual é a cor exata dos botões CTA? E dos cards de serviço? Há gradientes?")
```

You can also inspect the CSS directly via browser console:
```bash
browser_console(expression="getComputedStyle(document.querySelector('button')).backgroundColor")
```

### Step 3 — Extract text content for the prompt

Use browser_snapshot for page structure and key messaging:
```bash
browser_snapshot(full=true)
```

### Step 4 — Compile into structured specs

Organize into this format for the agy prompt:

```
## Identidade Visual da [Empresa]

Extraída do site [url]:  
- **Fundo:** [hex] — [description, e.g. "dark mode tecnológico"]  
- **Cor de destaque:** [hex] — [description]  
- **Cor secundária:** [hex]  
- **Logotipo:** [detailed description]  
- **Tipografia:** [font family, style]  
- **Botões:** [style, corners, colors]  
- **Cards:** [style]  
- **Padrão visual:** [description]  
- **Estilo geral:** [description]
```

## Phase 2: Generate with agy

Follow the standard agy SSH workflow (see `references/html-report-workflow.md` or main SKILL.md):

```bash
# 1. Write prompt with brand identity + content inline
cat > /tmp/agy-prompt-deck.txt << 'PROMPT'
[brand identity specs from Phase 1]
[slide-by-slide content]
[design constraints]
PROMPT

# 2. SCP to host
scp -F ~/.ssh/config /tmp/agy-prompt-deck.txt oracle-host:/tmp/

# 3. Generate
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --print "$(cat /tmp/agy-prompt-deck.txt)"'

# 4. Copy back
ssh oracle-host 'sudo cp /home/ubuntu/output.html /home/ubuntu/selfhost/hermes/data/'
```

## Pitfalls

⚠️ **web_extract often fails on marketing sites** — these sites use heavy JS, Canvas animations, and bot-blocking. Prefer browser_navigate + browser_vision.

⚠️ **One screenshot may not capture all brand elements** — the homepage hero section often has different typography than the rest of the site. Take 2-3 screenshots if needed (hero, service cards, footer).

⚠️ **Extracted colors may be approximate** — browser_vision describes colors in natural language ("ciano neon", "preto profundo"). Use hex approximations and let agy interpret. Do NOT spend time trying to get exact pixel colors from screenshots.

⚠️ **Logos delivered as Canvas can't be inspected** — if the logo renders on a Canvas element, describe it verbally in extreme detail for the agy prompt. Include shape, proportions, icon elements, typography pairing, and color.

⚠️ **Brand identity ≠ design output** — the extracted specs inform the visual direction but agy still needs a detailed content outline. Don't let brand extraction consume the whole budget.

## Example

For ID Consultoria (extracted from idconsultoria.ai):

```yaml
Fundo: "#050a0d" (preto profundo)
Destaque: "#00f2c3" (ciano neon)
Logotipo: "ID" em sans-serif minimalista, "I" com elemento gráfico tipo escudo acima
Tipografia: Plus Jakarta Sans (ou similar sans-serif geométrica) — Bold para títulos, Regular/Light para corpo
Botões: Cantos arredondados (pill-shape), sólido ciano neon para CTA, ghost button (borda ciano, fundo transparente) para secundários
Cards: Fundo escuro com bordas arredondadas, leve glow/brilho interno
Estilo: Tech-minimalism — contraste preto + ciano neon, espaço negativo, grid sutil de dados ao fundo
```

This was used to generate a 6-slide meeting deck at `/opt/data/reuniao_socios_id_consultoria.html`.
