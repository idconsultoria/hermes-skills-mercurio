# Plano Evolve — 2026-09-02

## Estado inicial
- 87 skills indexadas (11 categorias), 103 arestas, 0 órfãos (pós-update 87->94 com 7 novas pendentes de relações)
- 55 untracked no disco (drift canônico + 7 novas Mercúrio legítimas)
- 4 SKILL.md modificadas (auxiliar-adm-id, devops-artemishub, macroprocess-swimlane-html, motor-nfse-id)
- 12 refs productivity/google-workspace deletadas

## Análise MECE

### Novas skills (7) — avaliação de merge
1. **hermes-inference-config** (Reference, autonomous-ai-agents) — model/provider/fallback + cron routing. Distinto de hermes-agent (setup geral) e pi-agent-coordination (invocação). **Manter separado.** Relação: uses hermes-agent.
2. **brand-design-system-html** (Template, business) — DS HTML de cliente (BiotechSe, liquid glass, Solar Icons). Distinto de html-report-hermes (relatórios) e id-papel-timbrado (timbrado ID). **Manter.**
3. **planejamento-estrategico-8h-id-olimpo** (Orchestrator) — 8h Olimpo/Capitolino. Distinto de planejamento-estrategico-2h (workshop curto). Granularidade e público diferentes (time interno ID vs cliente). **Manter.**
4. **proposta-biotechse** (Orchestrator) — adaptação de elaboracao-proposta-comercial para marca BiotechSe (v5). Especialização de domínio, não redundante. **Manter.** Usa brand-design-system-html.
5. **hermes-cron-script-dispatch** (Reference, infrastructure) — scripts resilientes a HERMES_HOME. Distinto de hermes-agent e hermes-environment-replication. **Manter.**
6. **moodle-id-operacoes** (Orchestrator) — papéis/aulas/fórum Moodle ID. Domínio educacional ID. **Manter.**
7. **artemishub-onboarding-patterns** (Orchestrator, software-development) — padrões de falha de onboarding ArtemisHub (porte ICT, CheckViolation). Complementa devops-artemishub (operar/deploy) e react-fastapi-debugging (debug genérico). **Manter.**

Nenhum par candidato a merge (workflows distintos, artefatos diferentes).

### Drift
- apple/creative/media/mlops/note-taking/smart-home/social-media/research/*, productivity genéricas, github/DESCRIPTION.md — fora do prune ID (122→41). **Prunar** (rm).

### Descrições
- 2 summaries >85 chars (planejamento-8h 257, proposta-biotechse 212) → truncar ≤85 + adicionar parágrafo trigger
- 5 frontmatters sem category/type/timestamp → corrigir

### Relações
- Adicionar 15 relações (8 similar + 7 uses) cobrindo as 7 novas, garantindo 0 órfãos.
- Verificar grafo: 94 nós, 118 arestas após injection.

## Execução
1. Prune drift
2. Fix frontmatters/descrições
3. Indexar 7 novas no index.md + total 87->94
4. Inject 15 relações
5. Regenerar grafo (generate_catalog_graph.py) → 0 órfãos
6. Log update+evolve+offload, commit, push via push-skills-mercurio.sh

## Riscos
- Mass deletion guard → usar shutil python incremental
- generate_catalog_graph.py path hardcoded /opt/data → patch para /opt/mercurio-data
