# Skills Repository — Change Log

Diário cronológico de operações no repositório de skills.

---

## [2026-08-23] evolve | MECE 41 skills, 0 merges (borderline documentados p/ decisão humana: proposta-comercial-consultoria×elaboracao-proposta-comercial, document×meeting-action-items, família PDF), 0 deletes. Relações reconstruídas (compact prune havia zerado): +44 arestas (25 similar + 20 uses) no apêndice `## Relações entre skills` do index.md. Grafo regenerado via helper `_graph_catalog.py` (escopo catálogo-41, template D3 reutilizado de skills-repo-curator/templates/graph.html, bug modal fix `links`-filter): 41 nós, 44 arestas, 0 dangling → skills_graph.html + graph_data.json. ~99 untracked env-overflow preservadas (não indexadas; gaps ID-core sinalizados no report).

## [2026-08-23] update | Commit WIP trackado: `.gitignore` +ignore `*.pem/*.key/*_deploy_key` (segredos locais NUNCA commit); `productivity/html-to-pdf-chromium` ganhou workaround SIGTRAP/core-dump no `--print-to-pdf` ARM64/Debian trixie (`--headless=new`+`--no-zygote`+`--use-angle=swiftshader`, validado em produção 08/2026). index.md já coerente com as 41 skills (catálogo compacto do prune — sem blocos ###/Tamanho/Relações). Disco tem 140 skills: ~99 untracked = overflow do ambiente (canônico ressemeado) — NÃO indexadas (foco 100% ID, isolação do fork).

## [2026-08-16] offload | Análise de cobertura feita; remoção NÃO executada — tool `memory` indisponível nesta sessão cron (não listado em tools diretas nem no deferred catalog; tool_search só retorna taskflow MCP). Candidata identificada: "Open Design: CLI /opt/data/bin/od, daemon :7456, NUNCA nvm.sh (corrompe MCP)" → coberta por `creative/open-design/SKILL.md` (daemon :7456, CLI `/opt/data/bin/od`, NUNCA nvm.sh) + `references/mcp-connection-debug.md` + `references/restore.md`. Demais 28 entradas (MEMORY + USER PROFILE) são preferências, env facts, contatos, IDs operacionais ou avisos de projeto — preservadas. Remoção manual pendente: `memory(operations=[{action:'remove', old_text:'Open Design: CLI /opt/data/bin/od, daemon :7456, NUNCA nvm.sh (corrompe MCP).'}, ...])`.

## [2026-08-16] evolve | MECE analysis: 128→122 skills (−6). 3 merges: (1) PDF→HTML 5→1 — pdf-deck-to-html, pdf-slides-to-html, pdf-to-html-replication, branded-html-replication → productivity/pdf-to-html (3 references + estrutura de proposta comercial preservadas); (2) planejamento-estrategico → planejamento-estrategico-2h (tabela 11 frameworks + frameworks-2h.md); (3) google-sheets-formatting → google-sheets-automation (9 pitfalls + convenções de cor). 0 órfãos, 0 dangling. Relações atualizadas (auto-relação -2h removida, pdf-to-html herdou 2, automation ganhou valuation-consultivo). Graph regenerated (122 nodes).

## [2026-08-16] update | Index synced 114→128. 14 new skills indexed: elaboracao-proposta-comercial, planejamento-estrategico, planejamento-estrategico-2h, proposta-comercial-consultoria, valuation-consultivo (Business); branded-html-replication (Content Production); hermes-style-charts, open-design (Creative); searxng-firecrawl-repair (Infrastructure); pdf-deck-to-html (Media); google-sheets-formatting, pdf-slides-to-html, pdf-to-html, pdf-to-html-replication (Productivity). All 14 descriptions fixed to summary+paragraph with trigger (12 single-line, 2 unquoted). Frontmatter fixed: 4 missing type+timestamp (planejamento-estrategico-2h, open-design, pdf-slides-to-html, pdf-to-html-replication), 3 invalid OKF types corrected (planejamento-estrategico Domain→Orchestrator, branded-html-replication Workflow→Creative, pdf-deck-to-html Workflow→Media, pdf-to-html Workflow→ToolIntegration), 1 date-only timestamp made ISO (pdf-deck-to-html). Audit: 128/128 compliant, all have type+timestamp. 14 Resumo drifts verified — all acceptable (index more complete). Sizes synced to disk (0 mismatches).

## [2026-08-02] evolve | MECE analysis: 99 skills, 0 merges, 0 deletes, 0 orphans. 8 relation changes — board-game-design dedup (similar+uses→uses) + similar→product-pipeline, boardgame-design-principles dedup, 5 inbound symmetric edges (deep-research, html-report-hermes, market-research-synthesis, digital-clone-persona, production-deployment). 346→351 edges. Graph regenerated (99 nodes).

## [2026-08-02] update | Index synced 89→99. 10 new skills added: board-game-design (Orchestrator), boardgame-design-principles (Reference), research-report-standards (Reference), moodle-admin (ToolIntegration), docx (ToolIntegration), pdf (ToolIntegration), xlsx (ToolIntegration), systematic-research (Research), taskflow-ui-debugging (ToolIntegration), taskflow-mcp-rules (Reference). New section: Board Game Design. Frontmatter fixed on all 10 (type + timestamp; research-report-standards type Guideline→Reference; moodle-admin timestamp ISO). Descriptions audited: 99/99 compliant — 10 new skills converted from single-line to summary+paragraph with trigger, systematic-research literal \n escapes replaced with real newlines, taskflow-mcp-rules unquoted description quoted. 2 Resumo drifts fixed in index (pipeline-educacional accents, grafico-progresso-peso-ares accent). 3 stale index paragraphs synced (product-pipeline, taskflow-mcp, skills-repo-curator). 8 sizes synced to disk. All 99 SKILL.md have valid type + timestamp.

## [2026-07-26] offload | Skipped — memory unavailable (cron skip_memory=true, no entries to offload). See pitfall: offload needs manual session.

## [2026-07-26] evolve | MECE analysis: 89 skills, 0 merges, 0 deletes. 1 orphan resolved (hermes-desktop-plugins → similar → hermes-agent). Graph regenerated: 89 nodes, 236 edges. 5 root-level skills remain uncategorized by design (computer-use, dogfood, hermes-desktop-plugins, nsfw-content-discovery, read-reddit).

## [2026-07-26] update | Index synced 82→89. 7 new skills added: hermes-desktop-plugins (Reference), dashboard-performance-pipeline (ToolIntegration), hermes-cron-patterns (Reference), selfhost-service-deploy (ToolIntegration), selfhost-web-apps (ToolIntegration), supabase (ToolIntegration), html-to-social-image (Media). Frontmatter fixed on all 7 (type + timestamp). Descriptions audited: 13 skills fixed — 9 summaries shortened to ≤85 chars, 4 converted from single-line to summary+paragraph format with blank-line separator (dashboard-performance-pipeline, hermes-cron-patterns, selfhost-service-deploy, selfhost-web-apps, supabase, html-to-pdf-chromium, html-to-social-image, gcp-cloud-build), 1 unquoted description quoted (hermes-desktop-plugins). All 89 SKILL.md now have type + timestamp. All sizes synced to disk.

## [2026-06-28] update | Descriptions audited: 21 summaries shortened to ≤85 chars, 1 pt-BR trigger added (augmentacao-query), 3 missing blank-line separators fixed. Audit script updated to accept pt-BR trigger. 17 Resumo drifts synced. 60/100% compliant. Type + timestamp verified across all active skills.

## [2026-06-14] update | Index synced with working tree — 7 sizes updated, 1 new skill (digital-clone-persona), 2 resumos fixed. Descriptions audited: 6 YAML formats fixed (4 `|`→`"..."`, 5 `\\n\\n`→real newlines), 2 summaries shortened (product-pipeline, digital-clone-persona). ideation-drilling corrupted description replaced.

## [2026-07-19] update | Index synced 77→82.
## [2026-07-19] evolve | 82 skills, 0 orphans, 3 relations added (gcp-cloud-build), graph regenerated (225 edges)
## [2026-07-19] offload | Skipped — memory is disabled in cron environment (skip_memory=true). No user preferences or procedural facts to audit. Added: hermes-diagnostics (Research), gcp-cloud-build (ToolIntegration), whatsapp-baileys-integration (ToolIntegration), oferta-hormozi (Creative), whatsapp-automation (ToolIntegration). New sections: Copywriting, Messaging. Updated: pi-session-audit (desc+timestamp), html-to-pdf-chromium (desc+ARM64 fallback), 4 sizes synced. Fixed SKILL.md frontmatter: oferta-hormozi type (Copywriting→Creative) + timestamp, whatsapp-baileys-integration +timestamp, whatsapp-automation +type+timestamp. Descriptions fixed: oferta-hormozi, whatsapp-baileys-integration, whatsapp-automation (blank-line separator + trigger paragraph). curator backups removed from tracking.

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

## [2026-07-12] evolve | 12 orphans connected, 36 new relations added. 0 merges, 0 deletes. Graph regenerated (77 nodes). All education skills connected in cluster, production-deployment linked to deploy pipeline, grafico-progresso linked to fitness skills, Kindle skills linked, market-research linked to deep-research/user-interview, pipeline-educacional linked to product-pipeline + education.

## [2026-07-12] offload | No memory to offload — cron session has skip_memory=true, memory tool confirms disabled. Offload requires manual execution outside cron.

## [2026-06-28] evolve | Depth-1 inference: 87 new relations across 46 skills. 261 total (95 similar, 95 uses, 54 used_by, 17 parent). 0 merges, 0 deletes, 0 orphans. 3 parallel subagents analyzed all 60 skills. Graph regenerated (98 nodes, 184 edges).

## [2026-06-28] offload | Memory cleaned: 2 duplicate user-preference entries removed (NUNCA responder vazio, User pref responder antes — both already in USER PROFILE). Kindle operational data preserved in memory (specific Drive IDs, manga sources, cron).

## [2026-08-09] update | index 99->102: +3 skills (business/analise-contratual, research/grounded-citations, software-development/inspecting-hermes-desktop-dom); descriptions fixed (3 new skills got trigger paragraph + type + timestamp); timestamps refreshed on 7 modified skills; sizes synced; 8 SKILL.md content updates (moodle-admin +173, systematic-research +76, kindle-manga CDN-agnostic extraction, research-report-standards page-count workflow); new references/scripts/templates added (moodle-admin suite, erp-sync-pattern, cron-provider-outage-triage, wikipedia-action-raw-bypass, boletim-matinal-audio)

## [2026-08-09] evolve | 102->101 skills: 1 merge (messaging/whatsapp-automation absorbed into infrastructure/whatsapp-baileys-integration — same Baileys workflow, superset skill, 3 ref files + 5 sections preserved). 0 orphans, 0 bad targets. selfhost pair kept separate (distinct workflows). Report: reports/evolve-2026-08-09-report.md

## [2026-08-09] offload | 5 memory entries removed (redundant with skills): TaskFlow MCP URL/dir → taskflow-mcp; IAF crons+boletim → iaf-newsletter-pipeline+references/boletim-matinal-audio.md; Moodle IDs → moodle-admin; TaskFlow frontend UTC/BRT → taskflow-ui-debugging; NPM creds → selfhost-service-deploy. Memory 98%→71%. Kept: env facts (Oracle VM, gh accounts, ATLAS, SiteId, board game, augmentacao), Google OAuth dual-token swap (not in skill), WhatsApp bridge warning (operational).
## [2026-08-12] offload | 3 memory entries removed (redundant with skills): Google Docs pitfalls (visual-only trust, Pageless, insertInlineImage) → google-docs-formatting (md-to-gdoc-pitfalls #20 + mermaid-rendering.md); Chromium snap/Mermaid (headless_shell, mmdc, quotes) → iaf-newsletter-pipeline + google-docs-formatting mermaid-rendering.md; Pi Cost (--session, pi-cost-max preset) → pi-agent-internals + product-pipeline pi-delegation-content-formatting.md. Memory 99%→75%. Manual run outside cron (memory not visible to cron).
## [2026-08-12] update | index 101→114: +13 skills (pi-agent-internals, email-inbox-triage, github-issue-to-pr, document-to-action-items, google-docs-formatting, google-sheets-automation, html-pdf-fidelity, meeting-action-items, product-price-monitor, resume-ats-engine, weekly-review-planning, competitor-news-monitor, telegram-bot-python); nova seção ## Email; 13 frontmatters corrigidos (description 2 linhas + trigger, type OKF, timestamp ausente adicionado); audit 114/114 compliant; 0 size mismatches pós-sync (10 atualizados: product-pipeline +14.5K, hermes-diagnostics +7K, skills-repo-curator +6.7K); 20+ references novas commitadas (product-pipeline 13, hermes-diagnostics 3, agy, bpmn-diagram-renderer, social-media-video-content, merge-procedure); 14 Resumo drifts revisados — index.md mais completo que SKILL.md summary, aceitável, sem ação; header total 101→114; relações iniciais adicionadas às 13 (0 órfãos no index).
## [2026-08-12] evolve | 114 skills MECE, 0 merges, 0 orphans, 315 edges (+21). Depth-1: 3 subagentes validaram relações das 13 skills novas — 25 confirmadas, 3 corrigidas (resume-ats-engine: removida uses→html-report-hermes + retipada agy p/ uses; pi-agent-internals: removida similar→product-pipeline; telegram-bot-python: retipada whatsapp-baileys p/ similar). +25 relações novas aplicadas (taskflow/notion/google-workspace cluster, product-pipeline used_by gdocs+gsheets, hermes-cron-patterns para monitores, oracle-host-access p/ bot). 7 pares avaliados p/ merge — todos mantidos separados (MECE por artefato/camada). Report: reports/evolve-2026-08-12-report.md. Plan: reports/evolve-2026-08-12-0530.md
## [2026-08-12] offload | 2 memory entries removed (redundant with skills): gh accounts+Guard→urllib (2 contas, hosts.yml) → moodle-admin SKILL.md:317 + references/lesson-pipeline.md:56; Google OAuth dual-token swap (google_token.json/admin.json) → moodle-admin SKILL.md:146-155. Memory 75%→65%. Kept: user preferences (MEDIA tables, comm style), env facts (ATLAS, SiteId, board game, augmentacao, CFP, WhatsApp bridge warning, Drive IDs), contact/identity.

## [2026-08-18] evolve | Rama Mercúrio: prune para foco ID Consultoria (122→41 skills), remoção de PII pessoal (gustavomello9600, whatsapp pessoal), index raiz+categorias regenerados, fork sem upstream
