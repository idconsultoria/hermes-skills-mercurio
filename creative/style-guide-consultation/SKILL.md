---
name: style-guide-consultation
description: "Catálogo e consulta de guias de estilo: Hermes Agent (padrão), ID Consultoria, IAF Comunidade, IAF Newsletter. Carrega o guia correto para qualquer tarefa visual."
version: 1.0.0
tags: [design, style-guide, brand, visual-identity]
---

# Style Guide Consultation

Catálogo centralizado de todos os guias de estilo disponíveis. Use esta skill para carregar o design system correto antes de qualquer tarefa visual.

## Regra de ouro

> **Se o usuário NÃO especificar qual guia de estilo usar, carregue o Hermes Agent como padrão.**

Se o usuário especificar explicitamente uma marca (ID, IAF, etc.), carregue o guia correspondente.

## Índice de guias

| # | Guia | Caminho | Formato | Quando usar |
|---|------|---------|---------|-------------|
| 1 | **Hermes Agent** (padrão) | `/opt/data/referencias/hermes-agent/hermes-agent-design-style-guide.md` | Markdown | 🔵 **Sempre que não especificado.** Azul #0000FF, fundo #F0F5FF, Spectral títulos, Space Mono números, Inter corpo, dourado #E8B830 |
| 2 | **ID Consultoria** | `/opt/data/referencias/id-consultoria/id-style-guide.html` | HTML | Quando o output for para a ID Consultoria. Teal escuro #003B46, Bricolage Grotesque, Nunito Sans, dark mode #050A0F |
| 3 | **IAF Comunidade** | `/opt/data/referencias/iaf-comunidade/iaf-manual-identidade.html` | HTML | Para conteúdo da IA que Funciona. Teal #0da69e, fundo #080d0f, Outfit, Inter, Fira Code |
| 4 | **IAF Newsletter** | `/opt/data/referencias/iaf-newsletter/iaf-identidade-visual.html` | HTML | Para o newsletter diário da IAF. Variação do IAF com foco em legibilidade editorial |

## Como usar

### 1. Identificar o guia correto

Pergunte-se: "Este output visual é para qual marca/projeto?"

- Nenhuma menção / genérico → **Hermes Agent** (padrão)
- Explícitamente ID Consultoria → **ID Consultoria**
- IA que Funciona / IAF → **IAF Comunidade**
- Newsletter / daily digest → **IAF Newsletter**

### 2. Carregar o guia

```python
from hermes_tools import read_file

# Para Hermes Agent (padrão)
content = read_file('/opt/data/referencias/hermes-agent/hermes-agent-design-style-guide.md', limit=200)
# Extraia design tokens do conteúdo

# Para HTML (ID, IAF), leia as primeiras 100 linhas para os tokens CSS
content = read_file('/opt/data/referencias/id-consultoria/id-style-guide.html', limit=100)
# Extraia as variáveis CSS :root para cores, fontes, etc.
```

### 3. Extrair design tokens

Para guias HTML, procure na tag `<style>` pelas variáveis `:root`:

```css
:root {
    --bg-color: #050A0F;
    --deep-teal: #003B46;
    --electric-teal: #66E8F1;
    --font-headline: 'Bricolage Grotesque', sans-serif;
    --font-body: 'Nunito Sans', sans-serif;
    ...
}
```

Para guias Markdown (Hermes Agent), os tokens estão em tabelas no formato:

| Token | Hex | Uso |
|-------|-----|-----|
| `--blue-primary` | `#0000FF` | Background principal |

### 4. Aplicar no output visual

- Use as fontes, cores e materiais **exatos** do guia
- Respeite as regras de proibição (ex: sem azuis fora do espectro teal na ID)
- Siga o tom de voz e a filosofia de design

## Design tokens resumidos (quick reference)

### Hermes Agent (PADRÃO)
```css
--blue-primary: #0000FF;
--blue-bg: #F0F5FF;
--blue-border: #CCD9FF;
--gold-accent: #E8B830;
--text-dark: #1C1C1E;
--text-muted: #666680;
--font-heading: 'Spectral', Georgia, serif;
--font-mono: 'Space Mono', monospace;
--font-body: 'Inter', sans-serif;
```

### ID Consultoria
```css
--bg-color: #050A0F;
--deep-teal: #003B46;
--electric-teal: #66E8F1;
--teal-ciano: #4AC6D3;
--kintsugi-gold: #C9A227;
--deep-indigo: #1B2A6B;
--font-headline: 'Bricolage Grotesque', sans-serif;
--font-body: 'Nunito Sans', sans-serif;
--font-mono: 'IBM Plex Mono', monospace;
```

### IAF Comunidade
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

⚠️ **Light mode adaptation:** ID Consultoria é dark por padrão. Se o usuário pedir light mode, adapte: fundo #F7F9FB, texto #1C1C1E, bordas #DCE4E8. Mantenha o deep-teal #003B46 e electric-teal #4AC6D3. Veja `references/extraction-patterns.md` para a tabela completa.
```
├── STYLE_GUIDES_INDEX.md
├── hermes-agent/
│   ├── hermes-agent-design-style-guide.md   (39KB, 782 linhas)
│   └── hermes-agent-style-guide.md          (8KB)
├── id-consultoria/
│   ├── id-style-guide.html                  (112KB, 2798 linhas)
│   ├── id-guide-logo.png                    (460KB)
│   └── guia-notion-id.html                  (1.9MB, 3280 linhas)
├── iaf-comunidade/
│   └── iaf-manual-identidade.html           (850KB)
└── iaf-newsletter/
    └── iaf-identidade-visual.html           (41KB)
```

## Pitfalls

⚠️ **Não confundir guias.** O Hermes Agent tem tons de azul royal #0000FF; a ID Consultoria tem teal #003B46. Misturar os dois quebra a identidade visual.
⚠️ **Guias HTML precisam de parsing.** Extraia os tokens CSS do bloco `<style>` — não tente renderizar o HTML inteiro.
⚠️ **O Hermes Agent é SEMPRE o fallback.** Se não houver menção explícita de marca, use Hermes.
⚠️ **Para agy (Antigravity), carregue o guia primeiro e extraia os tokens.** Depois inclua os tokens no prompt do agy como constraints de design.
