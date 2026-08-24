# Evolve plan — 2026-08-24

Catálogo do fork Mercúrio: **84 skills**, 11 categorias, 90 arestas, **0 órfãos** pós-update.

## Estado analisado
- 0 órfãos, 0 auto-relações, 0 dangling, 0 pares simétricos duplicados.
- 33 skills com grau 1 (conexão fraca) — candidatas a enriquecimento MECE.

## Propostas (alta confiança, semântica confirmada por leitura de ambos SKILL.md)
| Relação | Tipo | Justificativa |
|---|---|---|
| `claude-code` → `product-pipeline` | similar | espelha codex/opencode→product-pipeline (agentes de codificação usados no pipeline de produto) |
| `email-inbox-triage` → `document-to-action-items` | similar | ambos extraem obrigações/prioridades/tarefas de entrada de texto |
| `docx` → `pdf` | similar | cluster de documentos (autorar Word ↔ manipular PDF) |
| `dogfood` → `requesting-code-review` | similar | QA exploratório (acha bugs) + revisão pré-commit (corrige) — complementares |
| `user-interview` → `ideation-drilling` | similar | pesquisa de usuário informa ideação de produto (Fase 1) |

## Não-merges (MECE preservada)
Nenhum merge: catálogo já pruneado para foco ID; cada skill é um fluxo de trabalho distinto
deleterável (9 business, 8 research, 16 productivity, 1 email, 26 software-development,
11 autonomous, 2 infrastructure, 3 cicd, 1 devops, 7 github).

## Saída
- +5 arestas (90→95); 0 órfãos; grafo regenerado via `scripts/generate_catalog_graph.py`.
- Report: `reports/evolve-2026-08-24-report.md`