# Evolve plan — 2026-08-26

## Objetivo
Consolidar o portfólio MECE do fork Mercúrio. Delta desde o ciclo 2026-08-25:
3 skills swimlane-HTML duplicadas + 1 skill operacional nova + drift genérico untracked.

## Diagnóstico
- Disco: 89 SKILL.md. Index: 85. Delta 4 = skills untracked (WIP de sessões manuais):
  - `software-development/macroprocess-swimlane-html` (HD)
  - `business/id-comunicacao-multiusuario`
  - `creative/html-process-diagrams`
  - `creative/interactive-process-map-html`
- **Violação MECE:** 3 das 4 (macroprocess-swimlane-html, html-process-diagrams,
  interactive-process-map-html) descrevem **o mesmo workflow** — mapa de macroprocesso
  swimlane em HTML interativo a partir do doc do Drive da ID, 1 tarefa=1 bloco, setas
  ortogonais bloco-a-bloco, pop-up por etapa. Conteúdo ~90% sobreposto (Data shape,
  source Drive, arrowhead/refX, redraw responsivo, validação headless).
- Drift genérico platform (shells sem SKILL.md): apple/, media/, mlops/, note-taking/,
  smart-home/, social-media/ + github/DESCRIPTION.md + creative/DESCRIPTION.md.

## Plano
1. **Merge 3→1** em `software-development/macroprocess-swimlane-html` (canônica: tem
   template pronto + workflow Drive + validação determinística). Absorver:
   - `orthogonal-arrows.md` (de html-process-diagrams)
   - `svg-arrowheads-and-screenshots.md` (de interactive-process-map-html, arrowhead refX)
   - Conteúdo design: identidade/fundo claro, espaçamento, não-duplicar participa.
2. **Delete** `creative/html-process-diagrams`, `creative/interactive-process-map-html`.
3. **Prune** drift genérico (apple, media, mlops, note-taking, smart-home, social-media,
   DESCRIPTION.md shells).
4. **Indexar** `id-comunicacao-multiusuario` (operacional, identidade por chat_id dos
   sócios) e `macroprocess-swimlane-html`. Total 85→87.
5. Relações: macroprocess-swimlane-html ~ bpmn-diagram-renderer, process-augmentation-pipeline;
   usos google-workspace. id-comunicacao-multiusuario ~ messaging-platforms; usos hermes-agent.
6. Grafo regenerado via generate_catalog_graph.py.
