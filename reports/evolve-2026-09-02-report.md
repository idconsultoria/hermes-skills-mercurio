# Relatório Evolve — 2026-09-02

## Resumo
- **Skills:** 87 → 94 (+7 indexadas, 0 merges, 0 deletes, 48 drift removidos do disco)
- **Relações:** 103 → 118 (+15), 0 órfãos, 0 bad targets
- **Grafo:** 94 nós, 118 arestas, regenerado via generate_catalog_graph.py

## Detalhe por etapa

### Update
- **Index:** Total 87->94. Inserções: business (+3), autonomous-ai-agents (+1), infrastructure (+2), software-development (+1). Tabelas atualizadas via patch LLM.
- **Novas skills:** hermes-inference-config, brand-design-system-html, planejamento-estrategico-8h-id-olimpo, proposta-biotechse, hermes-cron-script-dispatch, moodle-id-operacoes, artemishub-onboarding-patterns — todas com type/timestamp/category corretos após fix.
- **Modificadas:** auxiliar-adm-id (HERMES_HOME /opt/mercurio-data, oauth dual-token 01/09), devops-artemishub (+3 pitfalls crash-loop/401/ICT + ref onboarding-2026-08-31), macroprocess-swimlane-html (+16 linhas branching Safety v13), motor-nfse-id (recriado, Fase 1 DPS, Termux pitfall)
- **Refs removidas:** 12 productivity/google-workspace/* (clone-spreadsheet, docs-api-batch-update, docs-api-table-extraction, docs-table-extraction, drive-batch-download-pattern, drive-trashed-files-pitfall, gmail-large-file-delivery, gmail-search-syntax, scope-recovery, sheets-column-padding, workspace-automation-patterns-full, workspace-automation-patterns.md) — consolidadas ou obsoletas
- **Prune:** 48 SKILL.md drift (apple 4, creative 14, media 3, mlops 5, note-taking 1, smart-home 1, social-media 1, research 5, email/himalaya 1, productivity genéricas 7, github/DESCRIPTION.md 1) + node_modules/package artifacts
- **Descrições:** planejamento-8h 257->70, proposta-biotechse 212->52, brand-design/hermes-inference/artemishub frontmatters corrigidos. Fork mantém single-line para 80+ skills (padrão deliberado), apenas longas truncadas.
- **Script:** generate_catalog_graph.py corrigido chdir /opt/data -> /opt/mercurio-data

### Evolve — MECE
- **Merges avaliados:** 7 pares (hermes-inference vs hermes-agent, brand-design vs html-report-hermes, planejamento-8h vs planejamento-2h, proposta-biotechse vs elaboracao-proposta, moodle vs devops-artemishub, artemishub-onboarding vs devops-artemishub/react-fastapi, hermes-cron-dispatch vs hermes-agent) — todos mantidos separados (critério: workflows distintos, artefatos diferentes, não incorporáveis)
- **Relações adicionadas:**
  - Similar 8: brand-design→proposta-biotechse, proposta-biotechse→elaboracao-proposta-comercial, planejamento-8h→planejamento-2h, hermes-inference→hermes-agent, hermes-cron-dispatch→hermes-agent, moodle→devops-artemishub, artemishub-onboarding→devops-artemishub, artemishub-onboarding→react-fastapi-debugging
  - Uses 7: proposta-biotechse→brand-design, planejamento-8h→planejamento-2h, hermes-inference→hermes-agent, hermes-cron→hermes-agent, moodle→google-workspace, artemishub-onboarding→devops-artemishub, brand-design→html-report-hermes
- **Órfãos:** 0 (validado via grafos deg)
- **Grafo:** generate_catalog_graph.py 94 nós/118 arestas, template graph.html injetado, skills_graph.html 64KB

### Offload
- SKIP — memória não pré-injetada (cron skip_memory=true), tool memory sem action list. Nenhuma tentativa de listagem.

## Git
- Commit: update 87->94 + evolve 103->118 + offload SKIP
- Push: via push-skills-mercurio.sh para idconsultoria/hermes-skills-mercurio

## Artefatos
- reports/evolve-2026-09-02-plan.md, reports/evolve-2026-09-02-report.md, log.md, index.md, skills_graph.html, graph_data.json
