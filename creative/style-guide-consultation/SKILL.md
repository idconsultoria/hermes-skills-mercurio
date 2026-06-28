---
name: style-guide-consultation
description: "Catalog of style guides — load the correct design system for any visual task.

Load this skill when you need to apply a brand or design system to any visual output. Covers loading the correct style guide (Hermes Agent, ID Consultoria, IAF Comunidade, IAF Newsletter) for brand-consistent HTML, diagrams, and presentations."
version: 1.0.0
tags: [design, style-guide, brand, visual-identity]
---

# Style Guide Consultation

> ⚡ **Stitch MCP:** Se esta tarefa envolver design de telas, aplicação de design system ou prototipagem visual, ative o Stitch MCP primeiro: edite `/opt/data/config.yaml` mudando `stitch.enabled` para `true` e execute `/reload-mcp`.

Catálogo centralizado de todos os guias de estilo disponíveis. Use esta skill para carregar o design system correto antes de qualquer tarefa visual.

## Regra de ouro

> **Se o usuário NÃO especificar qual guia de estilo usar, carregue o Hermes Agent como padrão.**

Se o usuário especificar explicitamente uma marca (ID, IAF, etc.), carregue o guia correspondente.

## Índice de guias

| # | Guia | Caminho | Formato | Quando usar |
|---|------|---------|---------|-------------|
| 1 | **Hermes Agent** (padrão) | `/opt/data/referencias/hermes-agent/hermes-agent-style-guide.html` | HTML | 🔵 **Sempre que não especificado.** Azul royal #0000F2, branco #FFFFFF, Cormorant Garamond serif, Space Mono corpo, Syncopate headers, VT323 UI |
| 2 | **Consulting Brand** | `/opt/data/referencias/[brand]/[brand]-style-guide.html` | HTML | Quando o output for para a marca de consultoria. Teal escuro, fonte display customizada, dark mode |
| 3 | **Community Brand** | `/opt/data/referencias/[community]/[community]-identity-manual.html` | HTML | Para conteúdo da comunidade. Teal accent, dark background, fontes customizadas |
| 4 | **Newsletter Brand** | `/opt/data/referencias/[newsletter]/[newsletter]-visual-identity.html` | HTML | Para o newsletter diário. Variação com foco em legibilidade editorial |

## Como usar

### 1. Identificar o guia correto

Pergunte-se: "Este output visual é para qual marca/projeto?"

- Nenhuma menção / genérico → **Hermes Agent** (padrão)
- Marca específica mencionada → carregue o guia correspondente do catálogo
- Comunidade / grupo → guia da comunidade
- Newsletter / daily digest → guia do newsletter

### 2. Carregar o guia

```python
from hermes_tools import read_file

# Para Hermes Agent (padrão) — leia o HTML e extraia os tokens CSS do <style>:root
content = read_file('/opt/data/referencias/hermes-agent/hermes-agent-style-guide.html', limit=100)
# Extraia as variáveis CSS :root para cores, fontes, etc.

# Para HTML (outras marcas), leia as primeiras 100 linhas para os tokens CSS
content = read_file('/opt/data/referencias/[brand]/[brand]-style-guide.html', limit=100)
# Extraia as variáveis CSS :root para cores, fontes, etc.
```

### 3. Extrair design tokens

Para guias HTML, procure na tag `<style>` pelas variáveis `:root`:

```css
:root {
    --blue-royal: #0000F2;
    --white: #FFFFFF;
    --charcoal: #171717;
    --font-serif: 'Cormorant Garamond', serif;
    --font-mono: 'Space Mono', monospace;
    --font-wide: 'Syncopate', sans-serif;
    --font-pixel: 'VT323', monospace;
    ...
}
```

O Hermes Agent usa os tokens CSS acima. Para consultar um componente específico, localize a classe CSS correspondente no HTML (ex: `.hero-giant-title`, `.isometric-btn`, `.tech-table`).

### 4. Aplicar no output visual

- Use as fontes, cores e materiais **exatos** do guia
- Respeite as regras de proibição (ex: sem azuis fora do espectro teal na ID)
- Siga o tom de voz e a filosofia de design

## Design tokens resumidos (quick reference)

### Hermes Agent (PADRÃO)
```css
--blue-royal: #0000F2;
--white: #FFFFFF;
--charcoal: #171717;
--paper: #F5F5F7;
--amber: #FFBD38;
--red: #FF0000;
--font-serif: 'Cormorant Garamond', serif;
--font-wide: 'Syncopate', sans-serif;
--font-mono: 'Space Mono', monospace;
--font-pixel: 'VT323', monospace;
```

### Consulting Brand
```css
--bg-color: #050A0F;
--deep-teal: #003B46;
--electric-teal: #66E8F1;
--teal-ciano: #4AC6D3;
--deep-indigo: #1B2A6B;
--font-headline: 'Bricolage Grotesque', sans-serif;
--font-body: 'Nunito Sans', sans-serif;
--font-mono: 'IBM Plex Mono', monospace;
```

### Community Brand
```css
--bg-primary: #080d0f;
--bg-secondary: #0d1519;
--accent-primary: #0da69e;
--accent-hover: #00ffd5;
--accent-terracotta: #e07a5f;
--accent-sage: #8f9e8b;
--accent-amber: #ffb700;
--font-logo: 'Outfit', sans-serif;
--font-body: 'Inter', sans-serif;
--font-mono: 'Fira Code', monospace;
```

## Estrutura de diretórios

⚠️ **Para agy (Antigravity), carregue o guia primeiro e extraia os tokens.** Depois inclua os tokens no prompt do agy como constraints de design.

⚠️ **Light mode adaptation:** O guia escuro da marca de consultoria pode ser adaptado. Se o usuário pedir light mode, adapte: fundo #F7F9FB, texto #1C1C1E, bordas #DCE4E8. Mantenha o teal escuro e electric-teal. Veja `references/extraction-patterns.md` para a tabela completa.
```
├── STYLE_GUIDES_INDEX.md
├── hermes-agent/
│   └── hermes-agent-style-guide.html          (44KB, HTML autossuficiente com 15 componentes + console interativo)
├── consulting-brand/
│   ├── style-guide.html                     (112KB, 2798 linhas)
│   ├── guide-logo.png                       (460KB)
│   └── notion-guide.html                    (1.9MB, 3280 linhas)
├── community-brand/
│   └── identity-manual.html                 (850KB)
└── newsletter-brand/
    └── visual-identity.html                 (41KB)
```

## Pitfalls

⚠️ **Carregue o guia ANTES de escrever qualquer CSS/HTML.** Não comece a construir com design tokens genéricos e depois tentar corrigir. Quando o usuário menciona uma marca (ID, IAF, etc.), esta skill deve ser a PRIMEIRA coisa carregada — antes de agy, antes de escrever style.css, antes de qualquer output visual. O usuário teve que corrigir o agente duas vezes em uma sessão porque o CSS foi escrito com tokens inventados em vez do guia real da marca.

⚠️ **Gold (#C9A227 / --kintsugi-gold) foi REMOVIDO da paleta ID Consultoria.** Era temporário para um evento já encerrado. NÃO use em nenhum output da ID. A paleta agora é teal-only: #050A0F, #003B46, #4AC6D3, #66E8F1. Indigo (#6366F1) também removido.

⚠️ **Cenas 3D (Three.js) no dark theme ID ficam invisíveis se não ajustadas.** O fundo CSS `#050A0F` é quase idêntico a cores renderizadas escuras. Três causas comuns: (1) Fog exponencial > 0.03 dissolve a cena a 7+ unidades de distância — reduza para 0.01–0.015; (2) ShaderMaterial com sintaxe GLSL 1.00 falha silenciosamente em WebGL2 — adicione `glslVersion: 1`; (3) Cor base do terreno/tema muito escura — use no mínimo `#0C2A40` para contraste visível. Veja `vercel-deploy` skill → `references/threejs-invisible-scene-debugging.md` para o guia completo de diagnóstico.

⚠️ **Não confundir guias.** O Hermes Agent tem azul royal #0000F2, Cormorant Garamond serif, Space Mono corpo; outras marcas têm paletas distintas. Misturar os dois quebra a identidade visual.
⚠️ **Guias HTML precisam de parsing.** Extraia os tokens CSS do bloco `<style>` — não tente renderizar o HTML inteiro.
⚠️ **O Hermes Agent é SEMPRE o fallback.** Se não houver menção explícita de marca, use Hermes.
⚠️ **Para agy (Antigravity), carregue o guia primeiro e extraia os tokens.** Depois inclua os tokens no prompt do agy como constraints de design.
⚠️ **O guia Hermes Agent tem 15 componentes visuais.** O HTML é uma página interativa com previews e código de cada componente. Use como referência visual e de código, não apenas como lista de tokens.
⚠️ **Para relatórios de consultoria com agy,** carregue a skill `agy` primeiro e siga o padrão `references/data-report-prompt-pattern.md`. Ele já inclui como embutir os tokens Hermes no prompt.
