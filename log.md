# Skills Repository — Change Log

Diário cronológico de operações no repositório de skills.

---

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
|**Untracked reference files added:** 7 new reference files across iaf-newsletter-pipeline, brand-studio-forge, hyperframes-video-production.

## [2026-06-11] evolve | Depth-1 relations inferred via 3 subagentes. 66/83 skills received new relations (~180 edges). 0 merges, 0 deletes — skills MECE. 100% skills now have relations.
**Análise:** 3 subagentes paralelos leram 83 skills (profundidade 1 bilateral), confirmaram conexões semânticas. Relações adicionadas a 66 skills — similar, uses, used_by, parent.
**Clusters novos:** creative/* (ascii ↔ p5js ↔ manim ↔ pretext ↔ TTS), research/* (deep-research ↔ user-interview ↔ paper-writing ↔ arxiv), productivity/* (html-to-pdf ↔ nano-pdf ↔ pptx ↔ OCR), cross-category (maps↔reddit, vercel↔reports).
**index.md:** 66 entries patched com novas relações. Grafo regenerado.