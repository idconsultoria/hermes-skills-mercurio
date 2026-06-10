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
