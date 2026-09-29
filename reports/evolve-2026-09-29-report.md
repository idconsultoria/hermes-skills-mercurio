# Evolve report — 2026-09-29 (ciclo diário 02:00 UTC)

## Métricas
- Skills: 106 → 106 (0 merges, 0 deletes, 0 indexações).
- Arestas: 135 → 135 (74 Similar + 61 Uses, 0 adicionadas, 0 descartadas).
- Órfãos: 0 → 0. Grafo: 106 nós/135 arestas/0 órfãos (bytes idênticos ao 28/09).

## Update (resumo)
Varredura 29/09: nenhum commit de conteúdo desde cb65aa6 (28/09). Detectados 16 SKILL.md
canônicos untracked em disco — 12ª ocorrência do prune drift (detalhe no log.md).
Decisão: NÃO indexar (prune 41 + foco 100% ID). Audit: tracked 106/106 type+timestamp OK,
0 block-scalar, full-audit 51 two-part + 55 single-line deliberado (4 unquoted são drift,
fora do catálogo). Disco-catálogo 106 = tabela index 106 linhas, drift 0.

## Evolve — pares reavaliados (leitura bilateral FM + corpo)
1. nano-pdf × pdf — MANTER separadas. nano-pdf = edição de texto em PDF via prompts em
   linguagem natural (pip nano-pdf); pdf = toolkit estrutural (merge/split/forms/marca
   d'água). Edição NLP ≠ manipulação estrutural.
2. session-librarian × peer-session-audit — MANTER separadas. session-librarian organiza a
   biblioteca de sessões do usuário por prompt (find/rename/archive); peer-session-audit é
   auditoria viva de sessão de agente com SQLite + triagem (trabalho ID 27–28/09).
   Organização pessoal ≠ auditoria operacional.
3. blogwatcher × competitor-news-monitor — MANTER separadas. blogwatcher = tracker genérico
   RSS/Atom via blogwatcher-cli (Go/Docker); competitor-news-monitor = monitor de
   concorrentes com digests citados (workflow ID). Ferramenta genérica ≠ workflow ID.
4. research-paper-writing × deep-research — MANTER separadas. research-paper-writing =
   pipeline iterativo de escrita de papers ML (NeurIPS/ICML, LaTeX, revisão); deep-research
   = pesquisa multi-agente com decomposição e agregação citada. Escrita acadêmica ≠ pesquisa.
5. excalidraw × bpmn-diagram-renderer — MANTER separadas. excalidraw = diagramas hand-drawn
   via JSON (.excalidraw); bpmn-diagram-renderer = BPMN normativo (n Affordable-setup npm).
   Estilo livre ≠ norma BPMN.
6. huggingface-hub × llama-cpp — par INTERNO ao drift (ambos fora do catálogo). Registry
   (search/download/upload) ≠ inference local GGUF. Sem ação no catálogo.

Nenhuma aresta nova: nenhum dos 6 pares cruza duas skills DO catálogo de forma inédita
(blogwatcher-paper e demais candidatas estão fora do catálogo).

## Offload
SKIP — memória não pré-injetada no cron (skip_memory=true), tool memory sem action list.

## Git
- Commit: log.md + reports/evolve-2026-09-29-0200.md + este report.
- Push: via /opt/data/scripts/push-skills-mercurio.sh (registrar output no SUMMARY final).
- Working tree restante: drift untracked (16 SKILL.md + .locks/ + DESCRIPTION.md) — remoção
  adiada 12ª vez (guard bloqueia rm em lote no cron). Grafo imune (lê só index.md).
