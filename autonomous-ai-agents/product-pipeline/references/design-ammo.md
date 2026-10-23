# Munição de design, branding, motion e UX (para Pi e agy)

Pacote vendorizado das skills de design usadas no product-pipeline. **Não são skills do
Hermes** — são referências que os executores (Pi) e o revisor (agy) leem antes de projetar
ou julgar uma interface.

## Onde estão

- Termux (Hefesto): `~/forja/ammo/hub/<nome>/SKILL.md`
- Oracle (Pi): `/home/ubuntu/forja/ammo/hub/<nome>/SKILL.md`

Cada pasta preserva `SKILL.md` + `scripts/`, `assets/` e referências originais.
Se o caminho não existir na máquina do executor, copiar o hub antes de iniciar a fase —
nunca improvisar sem a munição.

## Inventário

### Identidade e direção de arte
| Skill | Uso |
|-------|-----|
| `brand` | voz, identidade, messaging, brand guidelines, paleta, tipografia, uso de logo |
| `design` | identidade do zero, tokens, estilos de logo, entregáveis de CIP, mockups |
| `frontend-design` | direção estética, tipografia e identidade que não parece template |
| `canvas-design` | composição e peças de marca em PNG/PDF |
| `anti-ui-slop` | contrato visual anti-genérico; evita cara de template shadcn |
| `impeccable` | design system, hierarquia, cor, tipografia, UX copy, consistência |

### Movimento
| Skill | Uso |
|-------|-----|
| `animate` | decidir se anima, propósito, propriedade, curva, duração, interrupção, saída |
| `review-animations` | crítica de motion existente |
| `improve-animations` | auditoria de motion no codebase com plano priorizado |
| `find-animation-opportunities` | onde falta motion e onde animar seria ruído |
| `animation-vocabulary` | traduzir descrição leiga no nome técnico do efeito |
| `animation-performance` | frame budget, composite-only, jank, will-change |
| `apple-design` | springs, gestos, sheets, momentum, profundidade, reduced-motion |
| `make-interfaces-feel-better` | hover, stagger, microinterações, ícones, sombras, contenção |
| `userinterface-wiki` | regras de animação, CSS, tipografia e padrões de UX |
| `vercel-react-view-transitions` | View Transitions em React/Next (só se o stack for React) |

### Qualidade de interface
| Skill | Uso |
|-------|-----|
| `web-design-guidelines` | auditoria contra as Web Interface Guidelines |
| `accessibility` | WCAG 2.2, teclado, contraste, foco, leitor de tela |
| `core-web-vitals` | LCP, INP, CLS |
| `performance` | carregamento, resposta, entrega de recursos |
| `best-practices` | segurança, compatibilidade, qualidade web |
| `design-mobile-apps` | telas mobile (só para app nativo/PWA dedicado) |
| `web-artifacts-builder` | artefatos React/Tailwind/shadcn autocontidos |

## Contrato de uso por fase

**Fase 3 (conceito) e Fase 4a (UX/UI):**
1. Pi lê, nesta ordem: `brand` → `design` → `frontend-design` → `anti-ui-slop` → `impeccable`.
2. Antes de escrever componente, Pi lê `make-interfaces-feel-better` e `userinterface-wiki`.
3. Se houver movimento, Pi lê `animate` + `apple-design`; se for só microinteração,
   `make-interfaces-feel-better` basta.
4. Pi entrega junto com a tela um bloco `## Design rationale` citando as regras aplicadas
   (não o conteúdo inteiro das skills).

**Fase 4b (engenharia):**
- `core-web-vitals` + `performance` viram critério de aceite mensurável.
- `accessibility` é gate: teclado, foco visível, contraste AA, `prefers-reduced-motion`.

**Gate do agy (revisão visual):**
- Julgar contra `web-design-guidelines`, `accessibility`, `anti-ui-slop` e `impeccable`.
- Reprovar automaticamente: emoji como ícone, gradiente roxo-azul genérico, card com
  sombra difusa sem hierarquia, tipografia de sistema sem escolha deliberada,
  animação sem propósito, layout que quebra abaixo de 390 px.

## Regra de ouro

Munição não é decoração. Cada skill lida tem que produzir uma decisão registrada —
tipografia, cor, densidade, movimento, estados. Se a decisão não aparece no artefato,
a skill não foi usada.
