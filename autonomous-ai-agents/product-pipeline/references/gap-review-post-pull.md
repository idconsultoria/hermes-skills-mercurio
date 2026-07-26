# Gap Review Pattern — Post-Pull/Rebrand Audit

## When to use

After `git pull` when the user has made uncoordinated changes:
- Rebrand (design system overhaul: dark → light theme, new color palette, emoji → SVG)
- Refactor (architecture change: single-file → modular, or vice versa)
- User-edited prototype (manual HTML/CSS/JS changes without Pi coordination)

## Flow

1. **Pull and verify state diff:**
   ```bash
   cd /opt/data/<projeto> && git pull origin main
   wc -c public/index.html product/design/design-system.html
   ```

2. **Sync to shared volume** (Pi needs to read from `/workspace/code/`):
   ```bash
   cp public/index.html /opt/data/code/workstation/<projeto>/product/design/design-system.html
   ```

3. **Create gap-review prompt** instructing Pi best to:
   - Read PRD.md (ground truth: what MUST exist)
   - Read referencia_completa_de_ui.md (checklist: every field, modal, table)
   - Read design-system.html (current code)
   - Read user-stories.md (acceptance criteria)
   - Do dual review: Code Review (line-by-line field comparison) + Dogfood QA (simulate user flows)
   - Generate `gap-report.md` with: Summary (total gaps × severity), per-module gaps with line numbers, RN status matrix, missing modals list, mock data audit, effort estimate

4. **Dispatch Pi best** — `deepseek-v4-pro`, timeout 1200s (large context)

5. **Output:** `product/engineering/gap-report.md` with `<!-- PHASE_COMPLETE: gap-report -->`

## Gap Report Structure

```markdown
# Gap Report — PROJETO MVP → Produção

## Sumário Executivo
| Métrica | Valor |
| Total de gaps | N |
| 🔴 Críticos | N |
| 🟠 Altos | N |
| 🟡 Médios | N |
| 🟢 Baixos | N |

## Gaps por Módulo
### Dashboard
| ID | Severidade | Descrição | Local (linha) | Correção necessária |

### Apontamentos
...

## Regras de Negócio Não Implementadas
| RN | Status | Evidência |

## Recomendações
- Fase 1 → Fase N com esforço estimado
```

## Execution Pattern (proven in VERO)

After gap report is generated, execute fixes in consolidated phases:

### Phase 1: Foundation + Architecture (GAP-072 to GAP-078 + GAP-102-105)
- Refactor monolith → modular architecture (CSS, JS, views, services, utils, store)
- Expand seed data (8+ entities, realistic values)
- Bundle Chart.js locally
- Create build.sh for deployment
- **Pi best**, ~12 min, one session

### Phases 3-5: All Modals + Business Rules (GAP-001 to GAP-093)
- **Single massive Pi session** (~9KB prompt, deepseek-v4-pro, ~15 min)
- **Key pattern:** "Para cada view, completar TODOS os campos da referência de UI. Nenhum campo pode faltar."
- List every field of every modal explicitly in the prompt
- Include RN01/02/03 implementation requirements per view
- 8 views rewritten in one execution

### After fixes:
- `bash build.sh` → vercel build + deploy --prebuilt
- Verify with `curl`: `<!-- PHASE_COMPLETE: fase-X -->` present
- git commit + push

## Key metrics from this session

VERO V6.0 rebrand audit results (83 gaps, 34 critical):
- 0/18 user stories implemented
- 0/3 business rules (RN01/02/03) implemented
- 84% form fields missing from UI reference
- 100% calculations (MIP, irrigation, LMR) depend on non-existent services
- Estimated fix: ~40 hours across 5 phases

After Phase 1 + Phase 345 execution:
- 18/18 user stories functional (mocked data)
- 3/3 business rules implemented
- 100% form fields matching UI reference
- All services with real calculations
- Deployed to Vercel in 2 phases (~27 min total Pi time)
