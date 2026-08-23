# Evolve 2026-08-23 — plano

## Contexto (diagnóstico pré-execução)
- Fork `idconsultoria/hermes-skills-mercurio`, master em `46a214d` (prune 122→41, PII removida, index regenerado em tabela compacta — **sem** blocos `###`, sem `Tamanho`, sem `**Relações:**`).
- **Git rastreia 41 skills; disco tem 140.** O ambiente re-populou `/opt/data/skills` com o conjunto completo (~99 dirs untracked, maior que qualquer estado pré-prune → overflow do canônico ressemeado).
- WIP legítimo trackado: `.gitignore` (+ignore `*.pem/*.key/*_deploy_key` — segredos) e `productivity/html-to-pdf-chromium/SKILL.md` (workaround SIGTRAP ARM64 validado em produção 08/2026).
- `skills_graph_template.html`/`graph_data.json`/`skills_graph.html` ausentes do disco e não trackados (prune removeu infra de grafo da raiz). Template D3 completo existe em `software-development/skills-repo-curator/templates/graph.html` (placeholder `__DATA_PLACEHOLDER__`).
- `generate_graph.py` padrão varre o DISCO (140 nós) — não serve para o catálogo-41.

## Decisões de escopo (integridade do fork — foco 100% ID)
1. **NÃO** indexar/commitar as ~99 skills untracked genéricas (reverteria o prune deliberado e violaria isolação vs canônico). Permanecem untracked no disco.
2. **NÃO** commitar skills ID-core que estão untracked mas ausentes do catálogo-41 (ex: `business/emissao-nfse`, `business/inter-api-id-consultoria`, `business/gestao-financeira-id`, `business/auxiliar-adm-id`, `productivity/id-papel-timbrado`, `productivity/md-to-timbrado-id`, `software-development/motor-nfse-id`) — **decisão do principal**, sinalizada no report. Não as adiciono autonomamente em cron.
3. **Etapa update**: commitar WIP trackado legítimo (`.gitignore` + `html-to-pdf-chromium`) + log.
4. **Etapa evolve**: MECE das 41 sem merges autônomos (candidatos borderline documentados); **reconstruir relações curadas** (o prune zerou as relações) e **gerar grafo do catálogo-41** via helper `_graph_catalog.py` (escopo = catálogo, não disco).

## Candidatos de merge borderline (NÃO executados — exigem olho humano, cron não tem usuário)
- `proposta-comercial-consultoria` × `elaboracao-proposta-comercial` — ambos propostas comerciais da ID (princípios/pricing vs pipeline do contexto). Fluxos parcialmente sobrepostos; manter separado até decisão.
- `document-to-action-items` × `meeting-action-items` — ambos extraem action items (documento vs reunião). Fluxos distintos (fontes diferentes); manter.
- Família PDF: `pdf`, `pdf-to-html`, `html-pdf-fidelity`, `html-to-pdf-chromium`, `html-report-hermes` — workflows distintos (create/merge/split vs extração vs render idêntico vs headless vs report). Manter.

## Gap de catálogo (fora do ciclo — reportar ao principal)
O catálogo-41 é 100% knowledge/consultoria mas **não** contém as skills operacionais ID-core (NFS-e, Inter, financeiro, timbrado, motor NFS-e) que estão untracked no disco. Recomenda-se decisão: adicioná-las ao fork compartilhado ou mantê-las locais.