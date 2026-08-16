# Evolve Report — 2026-08-16

## Estado inicial → final
- **Skills:** 128 → 122 (−6)
- **Órfãos:** 0 → 0
- **Bad-targets (dangling relations):** 0 → 0
- **Auditoria de descrições:** 128/128 → 122/122 compliant
- **Size mismatches:** 0

## Merges executados (3 clusters, 7 skills absorvidas)

### 1. PDF→HTML: 5 → 1
**Alvo:** `productivity/pdf-to-html` (9,297 → 11,787 chars)
**Absorvidas e deletadas:**
| Skill | Motivo |
|---|---|
| `media/pdf-deck-to-html` | Mesmo pipeline Figma→HTML (Type3, get_svg_image, .bg/.fg, bullets li::before) |
| `productivity/pdf-slides-to-html` | Mesmo pipeline + mesmas expectativas ID Consultoria (Minuzzo deck, 3 iterações) |
| `productivity/pdf-to-html-replication` | Winning formula idêntica (semantic HTML + arte original + texto explícito) |
| `content-production/branded-html-replication` | Mesmo workflow em fases (analyze → SVG → strip text → brand assets → HTML) |

Todas criadas na mesma sessão (14/08) com a mesma toolchain (PyMuPDF) e as mesmas validações do usuário (v2 rejeitada, v3 "perfeito"). **Conteúdo preservado:** 3 references únicas copiadas (`type3-svg-extraction.md`, `figma-pdf-pymupdf-pipeline.md`, `pdf-to-html-pipeline.md`) + seção "Templates de proposta comercial — estrutura aprovada" (Capa→…→Final) + pitfall do ícone exato da referência.

### 2. Planejamento estratégico: 2 → 1
**Alvo:** `business/planejamento-estrategico-2h` (9,226 → 11,225 chars)
**Absorvida e deletada:** `business/planejamento-estrategico` — mesma sessão única de PE de PME em 2h, mesma regra de ouro (1 página), mesmas exclusões (BSC/Hoshin). **Conteúdo preservado:** tabela de adequação de 11 frameworks + `references/frameworks-2h.md` + pitfall URLs mortas (V2MOM/Destination Postcard fora do ar).

### 3. Google Sheets: 2 → 1
**Alvo:** `productivity/google-sheets-automation` (5,953 → 8,856 chars)
**Absorvida e deletada:** `productivity/google-sheets-formatting` — mesma API (googleapiclient, batchUpdate). **Conteúdo preservado:** 9 pitfalls de formatação (0-based ranges, addBanding overlap, BOTTOM_AXIS, numberValue vs stringValue, sheetIds reais) + convenções de cor financeiro (nunca pizza/donut).

## Relações
- `business/planejamento-estrategico-2h`: removida auto-relação `similar → planejamento-estrategico` (deletada)
- `productivity/pdf-to-html`: herdou `similar → research-report-standards` + `similar → messaging-platforms` das deletadas
- `productivity/google-sheets-automation`: ganhou `similar → business/valuation-consultivo` (era do google-sheets-formatting)
- Todas as 6 entries removidas do index.md; relações apontando para elas corrigidas (0 dangling)

## Git
- Commit `update: ...` (edc8a4e) — etapa update
- Commit `evolve: ...` — este ciclo

## Grafo
- Regenerado: `python3 scripts/generate_graph.py` → `skills_graph.html` + `graph_data.json`
