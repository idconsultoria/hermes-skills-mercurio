# Evolve report — 2026-08-24

## Estado inicial vs final
- Skills: 83 → 84 (adotada `git-fork-isolation` na etapa update)
- Arestas: 90 → 95 (+5 relações semânticas)
- Órfãos: 0 → 0
- Merges: 0 · Deletes: 0

## Relações adicionadas (5, todas similar, validadas por leitura dos dois SKILL.md)
| Par | Justificativa |
|---|---|
| `claude-code` → `product-pipeline` | espelha codex/opencode→product-pipeline |
| `email-inbox-triage` → `document-to-action-items` | ambos extraem obrigações/tarefas de texto |
| `docx` → `pdf` | cluster de documentos autorar/converter |
| `dogfood` → `requesting-code-review` | QA acha bugs + revisão pré-commit corrige |
| `user-interview` → `ideation-drilling` | pesquisa de usuário informa ideação |

## Análise MECE
- Nenhum merge proposto: catálogo já pruneado; cada skill é fluxo distinto (business 9, research 8,
  productivity 16, email 1, software-development 26, autonomous 11, infrastructure 2, cicd 3, devops 1, github 7).
- 0 órfãos no grafo (checks: dangling 0, auto 0, duplicatas 0, `|- \`` 0).

## Necessidade discreta
- Removido drift genérico untracked do canônico (57 itens) na etapa update — disco 141→84 SKILL.md.

## Git diff summary
- index.md: +5 relações (apêndice); log.md: entrada evolve
- graph regenerado: 84 nós, 95 arestas

## Config do catálogo
- Grafo gerado por `scripts/generate_catalog_graph.py` (lê index.md, não disco) — template `graph.html`.