# Evolve — 2026-08-23 · Report

**Fork:** `idconsultoria/hermes-skills-mercurio` · master em `46a214d` (prune 122→41) · **41 skills / 7 categorias** (inalterado).

## Estado inicial → final
| Métrica | Inicial | Final |
|---|---|---|
| Skills no catálogo (tracked) | 41 | 41 |
| Skills no disco | 140 | 140 |
| Skills untracked (residual env) | ~99 | ~99 (intocadas) |
| Relações no catálogo | 0 (compact prune zerou) | 44 (25 similar + 20 uses) |
| Grafo | inexistente (infra podada na raiz) | regenerado (41 nós, 44 arestas) |

## Decisões de escopo (integridade do fork — foco 100% ID)
1. **99 skills untracked NÃO indexadas/commitadas.** O disco foi re-populado com o conjunto completo do ambiente (~99 dirs, > qualquer estado pré-prune → overflow do canônico ressemeado). Arrastá-las ao fork reverteria o prune deliberado e violaria a isolação vs canônico. Permanecem untracked (reversível via git).
2. **Merges: NENHUM executado.** Bordeline documentados abaixo — exigem decisão humana (cron sem usuário). Todos representam fluxos genuinamente distintos sob o critério MECE.
3. **Relações reconstruídas** (o prune zerou): 44 arestas curadas entre as 41 skills, documentadas no apêndice `## Relações entre skills` do index.md e no grafo.

## Candidatos de merge borderline (NÃO executados — requerem ok explícito)
| Skills | Análise | Veredito sugerido |
|---|---|---|
| `proposta-comercial-consultoria` × `elaboracao-proposta-comercial` | ambos propostas comerciais da ID: princípios/pricing vs pipeline do contexto | Manter; pedir ao principal |
| `document-to-action-items` × `meeting-action-items` | extraem action items — documento vs reunião | Fluxos distintos; manter |
| Família PDF (`pdf`, `pdf-to-html`, `html-pdf-fidelity`, `html-to-pdf-chromium`, `html-report-hermes`) | create/merge/split vs extração vs render idêntico vs headless vs report | manter |

## Gap de catálogo (fora do ciclo — recomendação ao principal)
O catálogo-41 é 100% knowledge/consultoria mas **não** contém as skills operacionais ID-core presentes no disco untracked: `business/emissao-nfse`, `business/inter-api-id-consultoria`, `business/gestao-financeira-id`, `business/auxiliar-adm-id`, `productivity/id-papel-timbrado`, `productivity/md-to-timbrado-id`, `software-development/motor-nfse-id`, `cicd-oracle-preview/`. **Decisão recomendada:** adicioná-las ao fork compartilhado (são 100% ID) ou mantê-las locais ao container.

## Git diff summary
- `update` commit: `.gitignore` (+`*.pem/*.key/*_deploy_key` ignore), `productivity/html-to-pdf-chromium/SKILL.md` (workaround SIGTRAP ARM64 validado 08/2026), `log.md`.
- `evolve` commit: `index.md` (+apêndice relatório), `reports/evolve-2026-08-23-plan.md`, `reports/evolve-2026-08-23-report.md`, `skills_graph.html`, `graph_data.json`, `log.md`.
- No scripts temporários committados (`_graph_catalog.py` removido antes do commit).

## Órfãos
0 — catálogo compacto sem sistema de relações anterior; novo apêndice conecta as 41 skills (44 arestas). TODAS as relações com alvo no catálogo (0 dangling).

## Nota grafo
`generate_graph.py` padrão varre o DISCO (≥140 nós) e não serve ao catálogo; `skills_graph_template.html` da raiz foi podado. Gerado via helper `_graph_catalog.py` (escopo=catálogo) reutilizando o template D3 do skill `skills-repo-curator/templates/graph.html`; aplicada correção do bug de modal (filtro `links` em vez de `DATA.edges`).