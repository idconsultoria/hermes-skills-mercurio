# Identidade ID vs Identidade do Cliente — regra de paleta e tipografia

**Correção 26/08/2026 — erro real cometido: relatório Hephaistos (artefato DA ID) foi gerado com paleta Biotechse (#029190/#00ffa3). Corrigido para ID.TEAL.**

## Regra

Antes de gerar qualquer HTML, pergunte: **este artefato é DA ID ou DO CLIENTE?**

| Artefato | Paleta | Tipografia | Fundo |
|---|---|---|---|
| **DA ID** (relatórios internos, análises, propostas ID, framework) | **ID.TEAL** `#14b8a6` + `#0d9488` / `#0b3d47` + navy `#0a1929` + claros `#5eead4` `#ccfbf1` `#f0fdfa` | **Neulis Neue** (títulos, 400/500) + **Nunito Sans** (corpo, 400/600/700) | `#f8fafc` claro ou gradiente navy→teal-deep para cards dark |
| **DO CLIENTE** (DS do cliente) | Paleta do cliente (ex.: Biotechse `#029190`/`#00ffa3`/`#f7eadf`) | Tipografia do cliente (ex.: Clash Display + Tomato Grotesk) | Conforme manual do cliente |

Fonte canônica ID: `companies/identidade-visual-id.md` (KB) — teal #14b8a6 é cor societária (ID.TEAL).

## Sinais de erro

- Relatório/análise com nome "ID" mas usando cores de cliente
- Tipografia do cliente em documento da ID
- Fundo escuro em teal do cliente quando deveria ser navy da ID

## Pitfall adicional — cards de composição com fundo claro

Falha 26/08 na seção "composição da marca" (B + DNA + folha): 3 cards com **glass claro translúcido** mas **texto branco + ícone mint** (pensados para fundo escuro) → ilegível (~3:1).

**Fix:** cards de conceito com ícone claro/mint + texto branco **devem ter fundo escuro sólido** (`linear-gradient(150deg,#0a1929→#0b3d47→#0d9488)` para ID, ou `#0d6f6e→#055c5b→#024140` para Biotechse), com contraste ≥7:1. Glass claro só quando texto é charcoal/teal-deep.

**Auditoria:** calcular WCAG para cada par real; remover `opacity` em textos pequenos (0.72–0.86rem) — já causou 3 reprovações em 26/08 (teal como texto 3.2:1, branco sobre teal 3.85:1, cinza #5a5a5a sobre glass).
