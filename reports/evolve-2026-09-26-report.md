# Report Evolve — 2026-09-26 (fork Mercúrio, ciclo 02:00 UTC)

## Métricas
- Skills: 103 → 106 (+3 indexadas, 0 merges, 0 deletes)
- Arestas: 129 → 134 (+5)
- Órfãos: 0 (generate_catalog_graph.py: 106 nós, 134 arestas, 0 órfãos, 0 descartadas)
- Audit descrições: 52 two-part com trigger + 54 single-line deliberado + 0 sem trigger; type/timestamp 106/106 OK
- Grafo: skills_graph.html (69.789 bytes) + graph_data.json regenerados

## Update — o que entrou
1. **3 skills novas ID (24–25/09, trabalho legítimo das sessões):**
   - `autonomous-ai-agents/facilitacao-grupo-agentes` (8,1KB + `references/protocolo-abertura.md`) — Mercúrio como facilitador de mesa multi-agente no Telegram (pauta, turno único, recado sem @)
   - `autonomous-ai-agents/peer-session-audit` (4,8KB) — postmortem de sessão ruim de agente par via sessão real (auditar=ler, ritual alheio não se escreve)
   - `business/roteiro-de-qualificacao` (7KB + `references/modos-e-armadilhas.md` + `scripts/scan-integridade-texto.py`) — roteiro bilateral Descoberta/Sabatina com gate de integridade de texto
   - Todas com two-part description + trigger + type + timestamp conformes (fix aplicado no ciclo)
2. **53 SKILL.md/references/scripts modified (24–25/09) — tema dominante browser policy proot:** Chromium ARM64 único (`/opt/data/.playwright/chromium-1117/chrome-linux/chrome`), runtime Playwright `/opt/mercurio-data/node_modules`, `browser_exec` para web externa — propagada em ~15 skills. Reescritas pontuais: html-to-pdf-chromium (shared runtime, WeasyPrint só fallback explícito), html-pdf-fidelity (sem SSH oracle-host), bpmn-diagram-renderer (npm direto, sem setup.sh/puppeteer), brand-design-system-html (extração de fonte via HTML renderizado, auditoria de paginação, verificação de links 1-a-1, chunked write anti-contaminação), messaging-platforms (mention por ID em caption, token por perfil), hermes-inference-config (rascunho-entregue-como-conteúdo ≠ reasoning), skills-library-audit (portão de aceite), product-pipeline/elaboracao (paths canônicos).
3. **Fixes de conformidade:** dups pós-aspas (notion, user-interview, backlog-and-sprint); blank-line (pi-agent-coordination, process-augmentation-pipeline); two-part (local-postgres-sandbox, postgres-sandbox-verification, hermes-agent-replication, stack2-mesh-failback); type Method/Runbook → Orchestrator (replication, stack2).
4. **Prune drift 9ª ocorrência ADIADO:** `.locks/` (locks de sessão) + 6 DESCRIPTION.md canônicos (apple/creative/media/note-taking/social-media/web) continuam untracked; guard do gateway bloqueia rm em lote no cron; grafo imune (lê só index).

## Evolve — análise MECE
Pares próximos reavaliados, todos mantidos separados (workflows distintos, relação no grafo já cobre):
- `local-postgres-sandbox` × `postgres-sandbox-verification` — montar cluster de dump vs PG17 descartável de .debs; Similar existente
- `hermes-agent-replication` × `hermes-environment-replication` — guia de replicação em VM nova vs levantamento de rama viva; Similar existente
- `facilitacao-grupo-agentes` × `reunioes-diarizadas` — conduzir reunião ao vivo vs extrair encaminhamentos de transcrição; nova Similar
- `roteiro-de-qualificacao` × `user-interview` — roteiro bilateral com sabatina vs protocolo de entrevista; nova Similar
- `peer-session-audit` × `hermes-inference-config` — postmortem vs config de modelo; nova Similar (auditoria cita a skill de inference como referência de diagnóstico)
- 0 merges, 0 deletes, 0 órfãos. Depth-1 completo via subagentes adiado (não cabe no cron 3 min — pitfall 12/08); análise direta depth-1 nas 3 novas executada (SKILL.md lidos nos dois lados).

## Offload
SKIP — cron sem memória injetada (skip_memory=true), tool memory sem action list.

## Git
- Commit único update+evolve+offload-skip (padrão dos últimos ciclos do fork: 2c9e3dd, 1102209)
- Push via `/opt/data/scripts/push-skills-mercurio.sh` (só fork idconsultoria/hermes-skills-mercurio)
