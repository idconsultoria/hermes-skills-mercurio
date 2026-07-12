# Skills Repository — Change Log

Diário cronológico de operações no repositório de skills.

---

## [2026-06-28] update | Descriptions audited: 21 summaries shortened to ≤85 chars, 1 pt-BR trigger added (augmentacao-query), 3 missing blank-line separators fixed. Audit script updated to accept pt-BR trigger. 17 Resumo drifts synced. 60/100% compliant. Type + timestamp verified across all active skills.

## [2026-06-14] update | Index synced with working tree — 7 sizes updated, 1 new skill (digital-clone-persona), 2 resumos fixed. Descriptions audited: 6 YAML formats fixed (4 `|`→`"..."`, 5 `\n\n`→real newlines), 2 summaries shortened (product-pipeline, digital-clone-persona). ideation-drilling corrupted description replaced.

## [2026-06-14] evolve | Description cleanup cycle: 12 Resumo truncations fixed, 3 duplicate paragraphs removed. 0 merges, 0 orphans. 47 skills MECE. Graph regenerated (47 nodes).

## [2026-06-10] update | First seed — scanned 113 skills, generated initial index.md
Repositório git iniciado em /opt/data/skills/. AGENTS.md, index.md e log.md criados.
113 skills catalogadas do estado atual instalado.

## [2026-06-10] evolve | Merged 11 skills into 4, deleted 10 skills. 113→92. Offload pending.
**Deletes:** godmode, requesting-code-review, segment-anything, gif-search, songsee, audiocraft, obliteratus, heartmula, openhue, kanban-orchestrator, kanban-worker
**Merges:**
- antigravity-design → agy (visual design workflows, style guide, image gen)
- daily-ai-digest+iaf-newsletter+newsletter-curation+cron-newsletter-pipeline+daily-briefing-pipeline → iaf-newsletter-pipeline
- hermes-tts-voice+voice-design → text-to-speech
- notion-mcp → notion
- brand-aesthetic-analysis → brand-studio-forge
**AGENTS.md:** Added offload operation to evolve cycle
**index.md:** Regenerated (92 skills)

## [2026-06-10] offload | Memory cleaned: 11→6 entries (94%→47%). Procedural facts moved to skills.
Removed: agy CLI config (→ agy skill), Pi version/providers (→ pi-agent-coordination), IAF pipeline v1.4 (→ iaf-newsletter-pipeline), Fish Speech (→ text-to-speech), Gemini TTS API (→ text-to-speech), Charon persona (→ text-to-speech)
Kept: GitHub auth, WhatsApp groups, permission rule, git conventions, OpenCode Go, Google Workspace

## [2026-06-10] update | AGENTS.md updated: evolve steps now include report writing, reports dir documented with plan+report pattern

## [2026-06-10] update | index.md regenerated with full spec — added summary + relations + per-skill descriptions for all 93 skills
**Diff:** +858 / -222 lines, 39KB total. Every skill now has: summary (~80 chars), full description paragraph, relations (similar/uses/used_by). 60/93 skills have at least one relation. Inferred via automated content scan + frontmatter metadata.

## [2026-06-10] update | index.md relations replaced with LLM-inferred semantic analysis. 207 edges, 76/93 skills
3 parallel subagents read every SKILL.md, determined relations by understanding content (not regex). Types: similar, uses, used_by, parent. 45KB total. Replaced automated-heuristic relations from previous version.

## [2026-06-10] evolve | Cycle #2: merged 6→3, deleted 3. 93→86 skills. Description audit passed.
**Deletes:** teams-meeting-pipeline, yuanbao, touchdesigner-mcp
**Merges:**
- sketch → claude-design (Sketch Mode section)
- python-debugpy+node-inspect-debugger → systematic-debugging (Python + Node.js sections)
- design-md → hermes-agent-skill-authoring (DESIGN.md Token Specs section)
**AGENTS.md:** Evolve step 7 now audits skill descriptions
**index.md:** Regenerated (86 skills)

## [2026-06-10] evolve | Cycle #4: skill-by-skill deep audit, PII removal, 1 merge, 900+ ephemeral lines cleaned. 84→83 skills.

**Análise:** 3 subagentes paralelos leram todos os 84 SKILL.md avaliando descrições, efêmeros, merges e relações.

**Merge:** code-tasks → backlog-and-sprint (task format moved to references/code-tasks-format.md)

**PII removal:** 6 skills limpas — whatsapp-bridge-baileys (contatos reais), brand-studio-forge (username), style-guide-consultation (marcas do usuário), messaging-platforms (JIDs), pi-agent-coordination (dotfiles URL), ideation-drilling (IP exposto)

**Limpeza de efêmeros:** ~900 linhas removidas. deep-research (135 linhas Kusto → references/), ai-voice-selfhost (80 linhas benchmarks → references/), github-pr-workflow (446 linhas CI/CD duplicadas), oracle-host-access (178 linhas PR Preview), pi-session-audit (64 linhas)

**Descrições:** 21 skills corrigidas — 6 críticas (copywriting 400+→120, pi-agent-coordination PT→EN, polymarket sem parágrafo, html-report-hermes 500+→80, whatsapp-bridge PT→EN, deep-research multi→80), 12 encurtadas, 3 com relações erradas corrigidas

**Relações:** 22 novas adicionadas (apple-reminders, findmy, airtable, google-workspace, html-to-pdf-chromium, maps, nano-pdf, notion, ocr-and-documents, powerpoint, relatorio-de-custos, taskflow-mcp, github-pr-workflow, oracle-host-access, github-repo-management, brand-studio-forge, ascii-art, humanizer, copywriting)

**De-duplicação:** github-pr-workflow e oracle-host-access agora referenciam deployment-pipeline para CI/CD

**AGENTS.md:** Regra adicionada — index.md é território de agente LLM, proibida edição por scripts

**index.md:** Regenerado (83 skills, 12 edges)

## [2026-06-10] update | Relations rebuilt depth-1 via 3 subagentes. 75/83 skills com relações.
**Análise:** 3 subagentes leram cada skill + suas potenciais relações (profundidade 1), confirmaram bilateralmente. Total: ~223 relações analisadas, 141 arestas no grafo — 75 skills com `**Relações:**` em index.md.

## [2026-06-11] update | Index.md synced with working-tree changes, 14 descriptions fixed, 5 YAML `>-`/`>` folded descriptions converted to quoted strings
**Modified SKILL.md synced to index.md:** messaging-platforms, iaf-newsletter-pipeline, brand-studio-forge, hyperframes-video-production, agy, skills-repo-curator — sizes and descriptions updated.
**YAML folded → quoted:** backlog-and-sprint, ideation-drilling, relatorio-de-custos, user-interview, skill-curation — `>-`/`>` descriptions converted to `"..."` format with explicit `\n\n` separation.
**Descriptions fixed (added trigger + paragraph):** autonomous-ai-agents, product-pipeline, comfyui, style-guide-consultation, ai-voice-selfhost, oracle-host-access, vercel-deploy, hyperframes-video-production, read-reddit, polymarket, brand-iaf-conteudo, test-driven-development — all now have `Load this skill when` activation trigger and proper summary+paragraph format.
**Index.md critical Resumo fixes:** product-pipeline, backlog-and-sprint, llama-cpp, skill-curation, style-guide-consultation, user-interview, relatorio-de-custos, taskflow-mcp, hermes-agent-skill-authoring — truncation and wrong summaries replaced.
**Untracked reference files added:** 7 new reference files across iaf-newsletter-pipeline, brand-studio-forge, hyperframes-video-production.

## [2026-06-11] evolve | Relations expanded + index.md cleanup. 83 skills, 260 edges (graph). 0 merges, 0 deletes.

## [2026-06-11] offload | No redundant memory found — all 6 entries are user preferences/environment facts, not procedural. Skipped.

## [2026-06-12] update | Index synced 83→46 skills (38 archived removed). Description audit on all 46 SKILL.md — 40 summaries trimmed to ≤85 chars, 2 missing trigger phrases fixed, 4 corrupted GitHub descriptions restored from git. YAML folded format eliminated. Stale temp files cleaned.
## [2026-06-12] evolve | Zero merges (46 skills MECE after prior archival). Google Workspace empty Relações fixed (+3 relations). Graph regenerated (46 nodes, 364 edges).
## [2026-06-12] offload | No memory to offload — cron session has memory disabled (skip_memory=true). No procedural facts in memory for this profile.

## [2026-06-11] evolve | Umbrella consolidation pass: 1 merge + 37 pruned. 83→46 skills. 37 archived.
**Consolidation:** skill-curation → skills-repo-curator (external curation lifecycle merged into umbrella repo curator skill; reference files migrated)
**Prunings (stale built-ins):** airtable, apple-notes, apple-reminders, architecture-diagram, arxiv, ascii-art, ascii-video, baoyu-infographic, blogwatcher, claude-design, comfyui, evaluating-llms-harness, excalidraw, findmy, github-issues, himalaya, huggingface-hub, imessage, jupyter-live-kernel, llama-cpp, llm-wiki, macos-computer-use, manim-video, maps, nano-pdf, obsidian, ocr-and-documents, p5js, polymarket, powerpoint, pretext, research-paper-writing, serving-llms-vllm, songwriting-and-ai-music, weights-and-biases, xurl, youtube-content
**Rationale:** All 37 are built-in skills with zero usage/activity, mostly platform-unsupported (macOS on Linux) or too narrow for standalone entries. Prune-Builtins mode: `hermes update` restores them on explicit demand. skills-repo-curator description updated to cover external curation. skill-curation reference files moved to skills-repo-curator/references/.
## [2026-06-14] offload | No memory to offload — cron session has memory disabled (skip_memory=true). No procedural facts in memory for this profile.
## [2026-06-21] update | Index regenerated 47→56 skills. 15 missing skills added (hephaistos, ai-sound-design, sound-design, ai-creative-assets, body-recomposition, ares-fitness-coach, data-pipeline-patterns, gemini-rate-limit-backoff, augmentacao-query, augmentation-process-design, bpmn-diagram-renderer, dedalo-squad, improve-codebase-architecture, process-augmentation-pipeline, simplify-code). 5 stale entries removed (github-auth, github-code-review, github-repo-management, ai-voice-selfhost, whatsapp-bridge-baileys). 3 unquoted descriptions fixed (ai-sound-design, body-recomposition, ares-fitness-coach). 3 duplicate paragraphs removed (autonomous-ai-agents, hermes-agent, copywriting). 1 escaped-\n description fixed (process-augmentation-pipeline). 1 stale reference (pi-agent-coordination/cron-progress-monitor.md) added.
## [2026-06-21] evolve | Relations expanded: 11 new edges added via depth-1 analysis. 161→172 relations. 0 orphans. 0 merges. Graph regenerated (95 nodes, 112 edges).
## [2026-06-21] offload | No memory to offload — cron session has memory disabled (skip_memory=true). No procedural facts in memory for this profile.

## [2026-06-28] update | Index synced 57→60 skills. 3 new skills added (kindle-manga, manga-anime-data, threejs-rendering-debug). 16 size entries updated... *hephaistos SKILL.md owned by different user (uid 1001), only index.md description updated.

## [2026-06-28] evolve | 0 merges, 0 deletes, 0 orphans. 49 similar pairs analyzed — all distinct workflows. Graph regenerated (98 nodes, 115 edges). Reports saved.

## [2026-06-28] offload | No memory to offload — cron session has memory disabled (skip_memory=true). No procedural facts in memory for this profile.

## [2026-07-12] update | Index synced 65→77 skills. 12 new skills added (education/*6, grafico-progresso-peso-ares, production-deployment, arxiv-latex-to-kindle, kindle-articles, market-research-synthesis, pipeline-educacional). All 77 SKILL.md descriptions audited and compliant: 12 descriptions reformatted (summary + paragraph + trigger), 12 types added (6 Template, 1 Health, 1 ToolIntegration, 1 Media, 1 Research, 1 Orchestrator, 1 ToolIntegration fix), 9 timestamps added. computer-use got type+timestamp. 13 sizes updated for modified skills. hermes-agent truncated summary fixed.

## [2026-06-28] evolve | Depth-1 inference: 87 new relations across 46 skills. 261 total (95 similar, 95 uses, 54 used_by, 17 parent). 0 merges, 0 deletes, 0 orphans. 3 parallel subagents analyzed all 60 skills. Graph regenerated (98 nodes, 184 edges).

## [2026-06-28] offload | Memory cleaned: 2 duplicate user-preference entries removed (NUNCA responder vazio, User pref responder antes — both already in USER PROFILE). Kindle operational data preserved in memory (specific Drive IDs, manga sources, cron).
