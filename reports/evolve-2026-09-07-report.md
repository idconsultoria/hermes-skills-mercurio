# Report Evolve — 2026-09-07 02:00 UTC

## Resumo
Fork Mercúrio estável: **94 skills**, **0 merges**, **0 deletes**, **0 órfãos**, **118 arestas** (63 Similar + 55 Uses). Grafo 94 nós / 118 arestas / 0 órfãos idempotente. Catálogo MECE — nenhum candidato a merge (10 pares próximos reavaliados, workflows distintos mantidos).

## Métricas
- Skills: 94 (disk 94, index 94) — 11 categorias
- Arestas: 118 (Similar 63 + Uses 55), órfãos 0
- Grafo: 94 nós, 118 arestas, 0 órfãos via generate_catalog_graph.py (64279 bytes)
- audit-descriptions: 44/94 compliant + 50 single-line deliberado (--drift 0)
- type/timestamp: 94/94 OK
- Drift untracked: 0 (canônico já pruned)

## Candidatos avaliados
| Par | Decisão | Motivo |
|---|---|---|
| augmentation-process-design ↔ augmentacao-query | manter | níveis distintos |
| process-augmentation-pipeline ↔ dedalo-squad | manter | genérico vs POPs |
| hermes-agent ↔ hermes-inference-config | manter | setup vs routing |
| docx/pdf/xlsx/pdf-to-html | manter | formatos distintos |
| product-pipeline ↔ backlog-and-sprint | manter | macro vs sprint |
| planejamento-2h ↔ 8h-olimpo | manter | 2h externo vs 8h interno |
| brand-design ↔ proposta-biotechse ↔ elaboracao-proposta | manter | design vs propostas |
| moodle ↔ devops-artemishub | manter | hosts distintos |
| artemishub-onboarding ↔ devops-artemishub | manter | padrões vs deploy |
| hermes-cron-dispatch ↔ hermes-agent | manter | dispatch vs setup |

## Relações
- Varredura rápida: apêndice 118 arestas cobre todos os 0-órfãos — nenhuma injeção necessária
- Depth-1 completo adiado (cron 3 min insuficiente — pitfall validado 12/08); próxima janela manual

## Operações
- Grafo regenerado: generate_catalog_graph.py idempotente
- Log.md: update + evolve + offload SKIP
- Commit: update+evolve 2026-09-07 (log + reports + grafo)
- Push: via /opt/data/scripts/push-skills-mercurio.sh

## Próximos passos
- Manter prune de drift canônico (apple/creative/media/mlops/note-taking/social-media/github/DESCRIPTION.md) se reaparecer
- Depth-1 relations quando janela manual >10 min disponível
- Offload permanece SKIP em cron (skip_memory=true)
