# Evolve report — 2026-08-26

## Estado inicial → final
| Métrica | Inicial | Final |
|---|---|---|
| Skills (índice) | 85 | 87 |
| Arestas no grafo | 98 | 103 |
| Órfãos | 0 | 0 |
| Disco SKILL.md | 89 | 87 |
| Cenário | — | merge 3→1, +2 indexadas, −3 drift |

## Merge (3→1)
| Deletada | Absorvida em | Motivo |
|---|---|---|
| `creative/html-process-diagrams` | `software-development/macroprocess-swimlane-html` | mesmo workflow (swimlane HTML); levou `references/orthogonal-arrows.md` + design decisions |
| `creative/interactive-process-map-html` | `software-development/macroprocess-swimlane-html` | mesmo workflow; levou `references/svg-arrowheads-and-screenshots.md` (arrowhead refX=11.5) + regra "nunca inventar" |

`macroprocess-swimlane-html` promovida a **Orchestrator** (workflow de build, não só
Reference) e reescrita como canônica consolidada (timestamp 2026-08-26). Template
pronto preservado em `templates/swimlane-macroprocess.html`.

## Drift genérico removido (shells sem SKILL.md, violam prune/isolamento ID)
apple/, media/, mlops/, note-taking/, smart-home/, social-media/,
github/DESCRIPTION.md, creative/DESCRIPTION.md.

## Novas skills indexadas (update)
- `business/id-comunicacao-multiusuario` (Reference) — registro de comunicação do
  Mercúrio por sócio (identidade por chat_id; operacional, não PII pessoal).
- `software-development/macroprocess-swimlane-html` (Orchestrator) — canônica da merge.

## Relações adicionadas (5)
Similar: macroprocess-swimlane-html→bpmn-diagram-renderer,
macroprocess-swimlane-html→process-augmentation-pipeline,
id-comunicacao-multiusuario→messaging-platforms.
Uses: macroprocess-swimlane-html→google-workspace, id-comunicacao-multiusuario→hermes-agent.

## Nota de consistência (pré-existente)
Os `index.md` de categoria (progressive disclosure) já estavam defasados antes deste
ciclo (ex.: software-development/index.md sem `react-fastapi-debugging`, adicionada em
2026-08-25). Adicionei as 2 skills novas aos indexes de `business` e
`software-development` para não regredir na descoberta OKF; a reconciliação completa
dos indexes de categoria fica para um ciclo futuro.

## Git diff summary
- +2 skills indexadas; −3 skills (merge + drift); 98→103 arestas; 0 órfãos.
- devops-artemishub: +1 linha de pitfall (deploy-preview `03:00: command not found`).
