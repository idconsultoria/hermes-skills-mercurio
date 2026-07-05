---
name: ui-ux-design-principles
description: "Core UI/UX design principles — hierarchy, grids, typography, color, dark mode, icons.

Load this skill when you need to apply professional UI/UX design fundamentals to any visual output. Covers visual hierarchy, color strategy, typography rules, grid systems, spacing with 4-point scale, dark mode design, icon sizing, button states, micro-interactions, and overlay techniques."
version: 1.0.0
tags: [design, ui, ux, visual-design, typography, color-theory, layout, principles]
type: Reference
timestamp: 2026-06-28T18:35:00Z
---

# UI/UX Design Principles

> Conhecimento fundamental de design de interfaces — aplique estes princípios em qualquer output visual.
> Para tokens de design de marcas específicas, carregue `style-guide-consultation` (guias próprios) ou `popular-web-designs` (54 sistemas de empresas reais).

Baseado no vídeo "Every UI/UX Concept Explained in Under 10 Minutes" por Kole Jain.

---

## 1. Visual Signifiers & Affordances

Elementos de UI comunicam como funcionam sem texto:

| Signifier | O que comunica |
|-----------|---------------|
| Container ao redor de itens | Agrupamento |
| Container destacado | Estado selecionado |
| Texto cinza | Inativo / desabilitado |
| Hover effect | Interatividade |
| Active nav highlight | Localização atual |
| Tooltip | Informação adicional |
| Button press state | Confirmação de clique |

**Regra:** "Good UI has many signifiers to tell the user what a UI affords, or what it can do."

---

## 2. Visual Hierarchy

Hierarquia se constrói com **size, position, colour, and contrast**.

- Informação **mais importante**: maior, mais bold, mais colorida, no topo
- **Imagens** adicionam cor instantânea e ajudam scanning (ex: cards da Uber)
- **Contraste entre tamanhos/cores** cria a hierarquia — não os valores absolutos
- **Right-alignment + cor única** (ex: azul) atrai o olho para dados-chave (preço)
- **Ícones + alinhamento** mostram direção (ex: from → to) sem palavras

> "The difference between small and big, or colorful and not, actually creates the hierarchy."

---

## 3. Grids, Layouts & White Space

### Grid System
- **12-column grid** é guideline, não jaula. Landing pages custom muitas vezes ignoram.
- Grids brilham para **conteúdo estruturado e repetitivo** (galerias, blogs):
  - Tablet: 8 colunas
  - Mobile: 4 colunas
- **White space é mais importante que o grid**: "Let things breathe."

### Four-Point Grid System
- Spacing em múltiplos de **4 px** (ex: 32 px entre itens)
- Garante consistência e fácil divisão
- **Agrupamento**: reduza o espaço entre itens relacionados (ex: título + subtítulo) — é hierarquia por proximidade

---

## 4. Typography

### Regras fundamentais
- **Uma fonte sans-serif é suficiente.** Passar tempo escolhendo múltiplas fontes é perda de produtividade.
- Letter-spacing para texto grande: **-2% a -3%** + line-height de **110-120%** — instantaneamente profissional.

### Limites de tamanho por contexto
| Contexto | Máximo de font sizes | Range |
|----------|---------------------|-------|
| Landing pages / websites | ≤ 6 | Amplo |
| Dashboards | ~24px body max | Alta densidade de info |

> "Design is mostly just text. You'll never need more than one font for any design."

---

## 5. Colour Strategy

### Método: colour ramp a partir de uma cor primária
1. Comece com **uma cor primária da marca**
2. **Clareie** para backgrounds
3. **Escureça** para texto
4. Isso constrói uma **colour ramp** coesa

### Semantic colours — emergem da função
| Cor | Significado |
|-----|------------|
| 🔴 Red | Danger / error / urgency |
| 🟡 Yellow | Warning |
| 🟢 Green | Success / new |
| 🔵 Blue | Trust / focus |

> "Use color for purpose, not just for decoration."
> "Let the color find you — like an announcement bar, a focus state on an input, or a green new chip."

---

## 6. Dark Mode Design

| Elemento | Regra |
|----------|-------|
| **Sombras** | **NÃO use.** Profundidade = cards claros sobre fundo escuro |
| **Bordas** | Reduza contraste (bordas muito claras ficam agressivas) |
| **Elementos brilhantes** (chips) | Reduza saturação e brilho |
| **Background** | Pode ser deep purple, red, green — não só navy/grey |
| **Light mode shadows** | Reduza opacidade, aumente blur. Mais fortes em popovers, sutis em cards |

> "If the shadow is the first thing you notice on a design, you're not using it right."

---

## 7. Icons & Ghost Buttons

### Icons
- **Tamanho do ícone = line-height da fonte** (ex: 24px)
- Garante equilíbrio visual entre texto e ícone

### Ghost Buttons
- Sem background até hover
- Uso: CTAs secundários
- **Padding rule**: width ≈ 2 × height
- Podem incluir ícones ou não

---

## 8. States & Feedback

**Regra fundamental: toda interação precisa de resposta.**

### Button states (mínimo 4)
1. Default
2. Hover
3. Active / Pressed
4. Disabled
+ Loading spinner

### Input states
- Focus (borda destacada)
- Error (borda vermelha + mensagem)
- Warning

### Feedback geral
- Loading spinners
- Success messages
- Micro-animações em scroll/swipe

---

## 9. Micro-interactions

Feedback que eleva o nível da interface:

- Exemplo: chip "copied!" deslizando após clicar copy — confirma a ação
- Range: do prático ao playful
- Devem ser **rápidas e não bloquear** o fluxo do usuário
- Sempre **confirmam uma ação**, nunca são só decorativas

---

## 10. Overlays & Image Treatment

### ❌ Errado
Overlay preto full-screen que mata a imagem.

### ✅ Certo
**Linear gradient** de transparente para fundo escuro — mostra a imagem e deixa o texto legível.

### 🔥 Extra
**Progressive blur** sobre o gradient para um visual moderno.

---

## Quick Reference Card

| Tópico | Pro Tip |
|--------|---------|
| **Typography** | Negative letter-spacing + line-height curto = polimento instantâneo |
| **Spacing** | Múltiplos de 4px; agrupe itens relacionados com menos espaço |
| **Icons** | Tamanho = line-height exato da fonte |
| **Ghost buttons** | Padding width ≈ 2× height |
| **Dark mode** | Card > background em lightness; diminua cores brilhantes |
| **Light shadows** | Baixa opacidade + blur alto; nunca roubam a cena |
| **Hierarchy** | Size + position + colour + contrast juntos |
| **Colour** | Comece de 1 cor; deixe as semânticas emergirem da função |
| **Fonts** | 1 sans-serif é suficiente; ≤ 6 sizes |
| **Overlays** | Gradient, não preto sólido |

---

## Relações com outras skills

- **`popular-web-designs`** → use quando precisar de tokens CSS de empresas reais (Stripe, Linear, Vercel)
- **`style-guide-consultation`** → use quando o output for para uma marca específica (Hermes, ID, IAF)
- **`html-report-hermes`** → use para renderizar relatórios com os princípios aplicados

---

## Pitfalls

⚠️ **Esta skill ensina princípios, não fornece tokens.** Para cores e fontes exatas de uma empresa, carregue `popular-web-designs`. Para guias de marcas próprias, carregue `style-guide-consultation`.

⚠️ **Não aplique dark mode rules no light mode.** Sombras são para light mode. No dark mode, profundidade vem de cards claros sobre fundo escuro.

⚠️ **Grid de 12 colunas não é universal.** Landing pages e designs mais artísticos podem (e devem) quebrar o grid. Use grids para conteúdo repetitivo e estruturado.

⚠️ **Letter-spacing negativo só para texto grande.** Em body text (≤18px), deixe o tracking padrão — aperto excessivo reduz legibilidade.

⚠️ **Menos cores é mais.** Comece com 1 cor primária. Cores semânticas (red, green, yellow) emergem naturalmente dos componentes — não as force em tudo.
