# SPRINTS.md Consolidation Pattern

## Problema

Arquivo SPRINTS.md muito grande (749 linhas, 33KB) dificulta busca e manutencao.

## Solucao

Dividir em arquivos menores por sprint, mantendo um indice simplificado.

## Estrutura Resultante

```
hephaistos/
├── SPRINTS.md                    → Indice simplificado (52 linhas)
└── notas-de-sessao/
    ├── sprint-1-fundacao.md      → Detalhes da Sprint 1
    ├── sprint-2-referencias.md   → Detalhes da Sprint 2
    ├── sprint-3-seguranca.md     → Detalhes da Sprint 3
    ├── sprint-4-peachweb.md      → Detalhes da Sprint 4
    ├── sprint-5-criadores.md     → Detalhes da Sprint 5
    └── sprint-6-skills.md        → Detalhes da Sprint 6
```

## Workflow de Consolidacao

1. **Ler SPRINTS.md completo** — Identificar secoes por sprint
2. **Criar diretorio notas-de-sessao/** — Se nao existir
3. **Extrair cada sprint** — Mover conteudo para arquivo separado
4. **Criar indice simplificado** — Manter visao geral + links
5. **Deletar SPRINTS.md original** — Substituir pelo novo indice
6. **Atualizar wikilinks** — Corrigir referencias quebradas

## Template de Arquivo de Sprint

```markdown
---
tags: [sprint, vault, engramas]
sprint: N
status: Completa
created: YYYY-MM-DD
---

# SPRINT N — Titulo

**Periodo:** YYYY-MM-DD
**Status:** Completa

## Objetivo
Descricao do objetivo da sprint.

## Tarefas Executadas
- [ ] Tarefa 1
- [ ] Tarefa 2

## Resultado
- X engramas criados
- Y arquivos modificados
```

## Template de Indice SPRINTS.md

```markdown
---
tags: [moc, sprints, projeto, vault, engramas]
created: YYYY-MM-DD
---

# Sprint Plan

## Visao Geral
Descricao curta do plano de sprints.

## Timeline de Sprints

| Sprint | Foco | Status | Resultado |
|--------|------|--------|-----------|
| **Sprint 1** | Fundacao | Completa | +25 engramas |
| **Sprint 2** | Referencias | Completa | +25 engramas |
| ... | ... | ... | ... |

## Detalhes

Para detalhes de cada sprint, ver:
- [[notas-de-sessao/sprint-1-fundacao|Sprint 1]]
- [[notas-de-sessao/sprint-2-referencias|Sprint 2]]
- ...
```

## Beneficios

1. **Busca mais rapida** — Arquivos menores = processamento mais rapido
2. **Manutencaofacil** — Atualizar apenas a sprint relevante
3. **Navegacao clara** — Links diretos para cada sprint
4. **Reducao de tamanho** — 749 linhas → 52 linhas (93% menor)
