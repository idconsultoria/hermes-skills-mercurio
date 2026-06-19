# Engrama Creation Pattern

> Template e lista completa de engramas do Hephaistos. Use este guia para criar novos engramas mantendo consistência.

## Template Básico

```markdown
# Engrama|Workflow|Decisão|Referência: Nome do Conceito

> Resumo em uma linha — o que este conceito significa.

## Seção 1: [Título da seção]

Conteúdo direto. Use:
- Tabelas para comparações
- Listas para steps/checklists
- Blocos de código para exemplos
- `[ ]` checkboxes para deliverables

## Links Associativos

### Mesmo cluster
- [[engrama-do-mesmo-cluster]] — Descrição curta

### Cross-cluster
- [[engrama-de-outro-cluster]] — Descrição curta

### Opostos
- [[engrama-oposto]] — O que é o contrário / alternativa
```

## Regras

1. **Um conceito por engrama** — se precisa de dois, são dois engramas
2. **≤ 100 linhas** — se passar, dividir em sub-engramas
3. **Links associativos obrigatórios** — mínimo 3 links em cada categoria (9 no total)
4. **Prefixos obrigatórios**:
   - `engrama-` para conceitos (pipeline, design, código)
   - `workflow-` para modos do pipeline (inception, design, etc.)
   - `decision-` para ADRs (architectural decision records)
   - `ref-` para referências visuais
5. **Atualizar `index.md`** após criar — adicionar link no cluster e nas navegações relevantes

## Lista Completa (26 Engramas)

### pipeline/ (4)
| Arquivo | Resumo |
|---------|--------|
| `engrama-6-modos` | Pipeline de 6 modos sequenciais |
| `engrama-delegate-task` | Como orquestrar subagentes |
| `engrama-context-layers` | Camadas de contexto (economia de tokens) |
| `engrama-quality-gates` | Verification steps (lint, test, typecheck) |

### design/ (4)
| Arquivo | Resumo |
|---------|--------|
| `engrama-anti-ai-slop` | O que NUNCA fazer em design |
| `engrama-palette-generation` | Como gerar paletas únicas |
| `engrama-typography-pairs` | Pares tipográficos que funcionam |
| `engrama-layout-grids` | Grids e espaçamentos |

### codigo/ (4)
| Arquivo | Resumo |
|---------|--------|
| `engrama-tdd-cycle` | Red-green-refactor |
| `engrama-typescript-strict` | Config TypeScript strict |
| `engrama-biome-config` | Config Biome (lint + format) |
| `engrama-vitest-patterns` | Patterns de teste com Vitest |

### workflows/ (6)
| Arquivo | Resumo |
|---------|--------|
| `workflow-inception` | Modo INCEPTION |
| `workflow-design` | Modo DESIGN (3 fases) |
| `workflow-implementacao` | Modo IMPLEMENTACAO |
| `workflow-revisao` | Modo REVISAO |
| `workflow-deploy` | Modo DEPLOY |
| `workflow-atualizacao` | Modo ATUALIZACAO |

### decisoes/ (4)
| Arquivo | Resumo |
|---------|--------|
| `decision-6-modos` | Por que 6 modos |
| `decision-delegate-task` | Por que delegate_task |
| `decision-2-ecossistemas` | Por que 2 ecossistemas de skills |
| `decision-config-json` | Por que config unificada |

### referencias/ (4)
| Arquivo | Resumo |
|---------|--------|
| `ref-pinterest-saas` | Referências de SaaS do Pinterest |
| `ref-dribbble-modern` | Shots modernos do Dribbble |
| `ref-mobbin-onboarding` | Patterns de onboarding do Mobbin |
| `ref-behance-branding` | Projetos de branding do Behance |

## Links de Navegação no index.md

Para cada novo engrama, adicionar links em:
1. **Cluster específico** — Seção do cluster na lista
2. **Navegação por modo** — Se o engrama é relevante para um modo específico
3. **Links cruzados** — Se o engrama tem relação com engramas de outros clusters
4. **Navegação por tópico** — Se o engrama responde a uma pergunta comum
