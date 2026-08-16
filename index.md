# Skills Index — Hermes Agent

*Total: 128 skills*

---

## Autonomous Ai Agents

### Computer Use (Desktop Automation)

- **Nome:** `computer-use`
- **Arquivo:** `computer-use/SKILL.md`
- **Tamanho:** 11,127 chars
- **Resumo:** Drive the user's desktop in the background — clicking, typing, scrolling
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T00:00:00Z

Load this skill whenever the `computer_use` tool is available. Cross-platform (macOS, Windows, Linux), works with any tool-capable model.

**Relações:**
- `similar` → `autonomous-ai-agents/hermes-agent`

### Autonomous AI Coding Agents

- **Nome:** `autonomous-ai-agents/autonomous-ai-agents`
- **Arquivo:** `autonomous-ai-agents/autonomous-ai-agents/SKILL.md`
- **Tamanho:** 3,388 chars
- **Resumo:** Delegate coding tasks to AI coding agent CLIs via Hermes: one-shot, review
- **Type:** Orchestrator
- **Timestamp:** 2026-06-21T05:11:49Z

Load this skill when you need to delegate coding tasks to autonomous AI coding agent CLIs. Covers one-shot queries to Claude Code, Codex, or OpenCode; PR review workflows with structured prompts; and session orchestration patterns for complex multi-step tasks across agents.

**Relações:**
- `similar` → `autonomous-ai-agents/pi-agent-coordination`
- `parent` → `autonomous-ai-agents/product-pipeline`
- `similar` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `autonomous-ai-agents/hephaistos`
- `uses` → `github/github-pr-workflow`

### Hephaistos — Hermes Meta-Framework

- **Nome:** `autonomous-ai-agents/hephaistos`
- **Arquivo:** `autonomous-ai-agents/hephaistos/SKILL.md`
- **Tamanho:** 67,272 chars
- **Resumo:** Hephaistos meta-framework — orquestra pipelines de projeto com Hermes, OpenCode e agy
- **Type:** Orchestrator
- **Timestamp:** 2026-06-19T19:47:50Z

Hephaistos meta-framework — Hermes-orchestrated project pipeline using delegate_task + OpenCode + Antigravity CLI (agy). Covers the full project lifecycle from inception through design, implementation, review, deploy, and update phases.

**Relações:**
- `similar` → `autonomous-ai-agents/autonomous-ai-agents`
- `uses` → `software-development/agy`
- `similar` → `autonomous-ai-agents/product-pipeline`
- `uses` → `autonomous-ai-agents/hermes-agent`

### Hermes Agent

- **Nome:** `autonomous-ai-agents/hermes-agent`
- **Arquivo:** `autonomous-ai-agents/hermes-agent/SKILL.md`
- **Tamanho:** 47,025 chars
- **Resumo:** Configure, extend, or contribute to Hermes Agent — setup, profiles, skills, and multi-agent
- **Type:** Reference
- **Timestamp:** 2026-06-21T05:11:49Z

Configure, extend, or contribute to Hermes Agent — setup, profiles, skills, and multi-agent orchestration. Load this skill when working with Hermes Agent itself. Covers initial setup and configuration, managing profiles, creating and installing skills, multi-agent spawning patterns, CLI usage, gateway configuration, and contributing to the Hermes codebase.

**Relações:**
- `parent` → `autonomous-ai-agents/messaging-platforms`
- `parent` → `autonomous-ai-agents/autonomous-ai-agents`
- `parent` → `autonomous-ai-agents/product-pipeline`
- `parent` → `autonomous-ai-agents/pi-agent-coordination`
- `parent` → `content-production/text-to-speech`
- `parent` → `content-production/iaf-newsletter-pipeline`
- `similar` → `creative/brand-studio-forge`
- `similar` → `creative/humanizer`

### Messaging Platforms

- **Nome:** `autonomous-ai-agents/messaging-platforms`
- **Arquivo:** `autonomous-ai-agents/messaging-platforms/SKILL.md`
- **Tamanho:** 26,940 chars
- **Resumo:** Reference for Hermes cross-platform messaging — platform quirks, ID formats, and
- **Type:** Reference
- **Timestamp:** 2026-06-28T05:11:55Z

Load this skill when troubleshooting message delivery across platforms, or when the user reports inconsistent response lag between platforms. Covers Telegram MEDIA file delivery rules, WhatsApp JID/group ID formats, bridge processes, known file-type limitations, platform-specific workarounds, and per-platform API latency diagnostics.

**Relações:**
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `parent` → `autonomous-ai-agents/hermes-agent`
- `used_by` → `content-production/text-to-speech`

### Pi Agent (Local)

- **Nome:** `autonomous-ai-agents/pi-agent-coordination`
- **Arquivo:** `autonomous-ai-agents/pi-agent-coordination/SKILL.md`
- **Tamanho:** 49,531 chars
- **Resumo:** Invoke Pi Agent locally from Hermes — provider/model hierarchy and session recovery
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-21T05:11:49Z

Invoke Pi Agent locally from Hermes: provider/model hierarchy, session recovery, stall detection, fallback patterns.
Load this skill for running Pi Coder Agent (v0.78.1) as a local npm binary — no Docker, no SSH. Covers the three-tier hierarchy (agy for strategy, Pi best via MiniMax M3 for planning, Pi cost via DeepSeek V4 Flash for code tasks), provider/model selection with fallback chains, session recovery from interrupted runs, stall detection and diagnosis, parallel execution patterns, and tmux-based monitoring. Includes GoUsageLimitError handling and pre-launch session reuse checks.

**Relações:**
- `uses` → `autonomous-ai-agents/pi-session-audit`
- `similar` → `autonomous-ai-agents/autonomous-ai-agents`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `parent` → `autonomous-ai-agents/hermes-agent`
- `uses` → `software-development/agy`

### Pi Agent Session Audit

- **Nome:** `autonomous-ai-agents/pi-session-audit`
- **Arquivo:** `autonomous-ai-agents/pi-session-audit/SKILL.md`
- **Tamanho:** 20,878 chars
- **Resumo:** Audit agent sessions — tokens, costs, models from Pi Agent, agy, and Hermes databases
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-16T11:30:00Z

Audit agent sessions — tokens, costs, models from Pi Agent (.jsonl), agy (protobuf SQLite DBs), and Hermes (state.db). Load this skill to analyze Pi Agent or agy session logs and calculate costs per provider. For Hermes sessions, extracts real token usage from state.db, computes costs based on model pricing with cache-hit/miss differentiation, and produces audit reports. Works across all three agent runtimes.

**Relações:**
- `used_by` → `autonomous-ai-agents/pi-agent-coordination`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `similar` → `autonomous-ai-agents/autonomous-ai-agents`
- `similar` → `productivity/relatorio-de-custos`

### Hermes Diagnostics

- **Nome:** `autonomous-ai-agents/hermes-diagnostics`
- **Arquivo:** `autonomous-ai-agents/hermes-diagnostics/SKILL.md`
- **Tamanho:** 24,782 chars
- **Resumo:** Systematic methodology for diagnosing Hermes Agent behavioral issues — session resets, context loss, compression failures
- **Type:** Research
- **Timestamp:** 2026-07-15T08:00:00Z

Load this skill when the user reports Hermes misbehaving: conversations resetting mid-turn, context being lost, sessions ending abruptly, repeated model fallbacks, or provider errors. Covers the full diagnostic pipeline: config analysis (compression, auxiliary models, session_reset settings), gateway log inspection (fallback patterns, compression events, error signatures), state.db SQLite analysis (session lifecycle, end_reasons, compression_failures, session_key chains), compressor source-code review, provider chain analysis, and causal-chain synthesis into a concrete remediation plan.

**Relações:**
- `similar` → `autonomous-ai-agents/hermes-agent`
### Product Development Pipeline

- **Nome:** `autonomous-ai-agents/product-pipeline`
- **Arquivo:** `autonomous-ai-agents/product-pipeline/SKILL.md`
- **Tamanho:** 104,713 chars
- **Resumo:** Multi-agent product pipeline — idea to MVP via sprints. Hermes orchestration
- **Type:** Orchestrator
- **Timestamp:** 2026-06-14T05:19:11Z

Load this skill when building a product from scratch through the full pipeline — ideation, research, design, sprints, and delivery. Covers orchestrating a multi-agent team with Hermes as coordinator, Pi Agent for execution, and Antigravity for visual design review.

**Relações:**
- `uses` → `autonomous-ai-agents/pi-agent-coordination`
- `uses` → `autonomous-ai-agents/autonomous-ai-agents`
- `uses` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `content-production/iaf-newsletter-pipeline`
- `uses` → `creative/copywriting`
- `uses` → `creative/humanizer`
- `uses` → `software-development/ideation-drilling`
- `uses` → `research/user-interview`
- `uses` → `research/deep-research`
- `uses` → `read-reddit`

### Pi Agent — Funcionamento Interno

- **Nome:** `autonomous-ai-agents/pi-agent-internals`
- **Arquivo:** `autonomous-ai-agents/pi-agent-internals/SKILL.md`
- **Tamanho:** 6,037 chars
- **Resumo:** How Pi Agent works internally — settings, sessions, compaction, costs.
- **Type:** Reference
- **Timestamp:** 2026-08-12T03:15:00Z

How Pi Agent works internally — settings, sessions, compaction, costs.

Load this skill when asked how the Pi Agent works internally — its settings.json hierarchy, session JSONL layout (--session append semantics), compaction, provider/model selection and the pi-cost wrapper. Reference for debugging Pi behavior and auditing sessions.

**Relações:**
- `similar` → `autonomous-ai-agents/pi-agent-coordination`
- `similar` → `autonomous-ai-agents/pi-session-audit`
- `similar` → `autonomous-ai-agents/hermes-diagnostics`

## Content Production

### AI Sound Design — SFX & Ambient Audio

- **Nome:** `content-production/ai-sound-design`
- **Arquivo:** `content-production/ai-sound-design/SKILL.md`
- **Tamanho:** 5,914 chars
- **Resumo:** Generate, process, and optimize sound effects and ambient audio using AI tools and
- **Type:** Media
- **Timestamp:** 2026-06-21T05:11:49Z

Load this skill when you need to create sound effects, ambient audio, or UI sounds for web/game/film projects. Covers prompt engineering for ElevenLabs SFX V2, settings optimization (Prompt Influence, duration, reverb), audio post-processing with ffmpeg (normalization, format conversion), and seamless loop creation for ambient drones.

**Relações:**
- `similar` → `content-production/sound-design`
- `similar` → `content-production/text-to-speech`

### IAF Newsletter Pipeline — Manhã Aumentada

- **Nome:** `content-production/iaf-newsletter-pipeline`
- **Arquivo:** `content-production/iaf-newsletter-pipeline/SKILL.md`
- **Tamanho:** 46,087 chars
- **Resumo:** Umbrella skill for newsletters — cron scheduling, curation, dedup, deploy
- **Type:** Orchestrator
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline. Covers multi-source content collection, editorial ranking and dedup, HTML generation, deploy no Vercel, e entrega via Telegram no formato WhatsApp-style.

**Relações:**
- `uses` → `creative/copywriting`
- `uses` → `creative/humanizer`
- `similar` → `autonomous-ai-agents/product-pipeline`
- `similar` → `creative/style-guide-consultation`
- `uses` → `social-media/brand-iaf-conteudo`
- `uses` → `infrastructure/data-pipeline-patterns`

### Sound Design — AI SFX & Audio Production

- **Nome:** `content-production/sound-design`
- **Arquivo:** `content-production/sound-design/SKILL.md`
- **Tamanho:** 10,132 chars
- **Resumo:** Umbrella skill for AI sound effects and audio production — prompt engineering and
- **Type:** Media
- **Timestamp:** 2026-06-21T05:11:49Z

Umbrella skill for AI sound effects (SFX) and audio production — prompt engineering, UI sound design, audio post-processing, format delivery. Load this skill for any sound design task: generating UI SFX with AI tools (ElevenLabs, Noiz AI), creating ambient/drone music, designing sonic identities for brands/interfaces, post-processing audio (normalization, format conversion, loudness), and integrating audio into web/desktop projects.

**Relações:**
- `similar` → `content-production/text-to-speech`
- `parent` → `content-production/ai-sound-design`

### Text-to-Speech (TTS)

- **Nome:** `content-production/text-to-speech`
- **Arquivo:** `content-production/text-to-speech/SKILL.md`
- **Tamanho:** 15,498 chars
- **Resumo:** Umbrella skill for TTS — voice design, multi-provider fallback, persona to audio
- **Type:** Media
- **Timestamp:** 2026-06-19T19:47:50Z

Umbrella skill for TTS: voice design, Gemini prompting, multi-provider fallback, self-hosted Fish Speech, and Hermes TTS provider. Full lifecycle from persona to audio.

**Relações:**
- `parent` → `autonomous-ai-agents/hermes-agent`
- `uses` → `creative/humanizer`
- `uses` → `autonomous-ai-agents/messaging-platforms`
- `uses` → `infrastructure/oracle-host-access`
- `uses` → `infrastructure/gemini-rate-limit-backoff`

### Research Report Standards — Estrutura e Conteúdo

- **Nome:** `content-production/research-report-standards`
- **Arquivo:** `content-production/research-report-standards/SKILL.md`
- **Tamanho:** 10,541 chars
- **Resumo:** Research report standards — content, narrative flow, visual consistency.
- **Type:** Reference
- **Timestamp:** 2026-08-09T05:08:04Z

Carregue esta skill quando for produzir um relatório de pesquisa, análise de mercado ou estudo entregue como HTML + PDF. Define o que o conteúdo deve conter: remoção de metadados de rótulo (nível/status/projeto/data), seção obrigatória 'Sobre este Relatório', framework SCR para sumário executivo e regras de consistência visual entre relatórios relacionados.

**Relações:**
- `similar` → `productivity/html-report-hermes`
- `similar` → `research/market-research-synthesis`

### Branded HTML Replication

- **Nome:** `content-production/branded-html-replication`
- **Arquivo:** `content-production/branded-html-replication/SKILL.md`
- **Tamanho:** 5,422 chars
- **Resumo:** Replicate designed PDFs/decks as faithful branded HTML — assets, fonts, SVG.
- **Type:** Creative
- **Timestamp:** 2026-08-14T00:00:00Z

Load this skill when recreating a designed document (PDF slides, deck, proposal) as HTML that carries the brand faithfully: backgrounds, logos, icons, fonts, colors — optionally as clean semantic HTML instead of pixel-perfect positioning. Validated with the ID Consultoria deck + proposal template (Aug 2026). Extracts brand assets from PDF for HTML use.

**Relações:**
- `similar` → `productivity/html-pdf-fidelity`
- `similar` → `content-production/research-report-standards`

## Creative

### AI Creative Assets — Tool Research & Production Prompts

- **Nome:** `creative/ai-creative-assets`
- **Arquivo:** `creative/ai-creative-assets/SKILL.md`
- **Tamanho:** 8,810 chars
- **Resumo:** Research AI tools for generating visual creative assets (textures, 3D models, sprites, vector icons) and craft optimized prompts
- **Type:** Creative
- **Timestamp:** 2026-06-21T05:11:49Z

Research AI tools for generating visual creative assets (textures, 3D models, sprites, vector icons) and craft optimized prompts + post-processing workflows for production-ready outputs. Load this skill when the user asks which AI tool to use for a specific asset type, needs optimized prompts for visual asset generation, or needs to plan a multi-asset pipeline across different AI tools.

**Relações:**
- `similar` → `content-production/sound-design`
- `similar` → `creative/style-guide-consultation`
- `similar` → `software-development/agy`

### Brand Studio Forge

- **Nome:** `creative/brand-studio-forge`
- **Arquivo:** `creative/brand-studio-forge/SKILL.md`
- **Tamanho:** 21,269 chars
- **Resumo:** Create, refine, or evolve a brand identity: interviews, identity kit, content
- **Type:** Creative
- **Timestamp:** 2026-06-19T19:47:50Z

Use when the user wants to create, refine, or evolve a brand identity. Covers brand interviews, identity kit generation (logo, color, type, voice, guidelines), brand-specific content skills, and ongoing content via cron. Not for UI design or non-brand creative tasks.

**Relações:**
- `uses` → `creative/popular-web-designs`
- `uses` → `creative/style-guide-consultation`
- `similar` → `creative/style-guide-consultation`
- `uses` → `creative/copywriting`
- `uses` → `software-development/agy`

### Copywriting

- **Nome:** `creative/copywriting`
- **Arquivo:** `creative/copywriting/SKILL.md`
- **Tamanho:** 9,304 chars
- **Resumo:** Expert conversion copywriting: write, rewrite, or improve marketing copy with
- **Type:** Creative
- **Timestamp:** 2026-06-21T05:11:49Z

Expert conversion copywriting: write, rewrite, or improve marketing copy — headlines, CTAs, value props, page sections.
Load this skill when the user needs marketing copy — landing pages, homepage sections, pricing copy, CTAs, taglines, or value propositions. Provides a complete framework for gathering context, applying copywriting principles (clarity over cleverness, benefits over features, specificity over vagueness), and producing organized output with annotations and alternatives. Covers page structure frameworks, voice and tone guidance, CTA copy guidelines, and page-specific strategies for homepages, landing pages, pricing pages, feature pages, and about pages. Pair with the humanizer skill for thorough line-by-line editing after drafting.

**Relações:**
- `similar` → `creative/humanizer`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `creative/brand-studio-forge`
- `similar` → `social-media/brand-iaf-conteudo`

### Humanizer: Remove AI Writing Patterns

- **Nome:** `creative/humanizer`
- **Arquivo:** `creative/humanizer/SKILL.md`
- **Tamanho:** 30,348 chars
- **Resumo:** Humanize text by stripping AI-isms and adding authentic voice and personality
- **Type:** Creative
- **Timestamp:** 2026-06-14T05:15:09Z

Humanize text: strip AI-isms and add real voice.

**Relações:**
- `similar` → `creative/copywriting`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `creative/brand-studio-forge`
- `used_by` → `creative/copywriting`

### Popular Web Designs

- **Nome:** `creative/popular-web-designs`
- **Arquivo:** `creative/popular-web-designs/SKILL.md`
- **Tamanho:** 10,356 chars
- **Resumo:** 54 real-world design systems from Stripe, Linear, Vercel — HTML and CSS
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.

**Relações:**
- `used_by` → `creative/brand-studio-forge`
- `similar` → `creative/style-guide-consultation`

### Style Guide Consultation

- **Nome:** `creative/style-guide-consultation`
- **Arquivo:** `creative/style-guide-consultation/SKILL.md`
- **Tamanho:** 8,089 chars
- **Resumo:** Catalog of style guides — load the correct design system for any visual task.
- **Type:** Reference
- **Timestamp:** 2026-06-28T05:11:55Z

Catalog and consultation of style guides — load the correct design system for any visual task. Load this skill when you need to apply a brand or design system to any visual output. Covers loading the correct style guide (Hermes Agent, ID Consultoria, IAF Comunidade, IAF Newsletter) for brand-consistent HTML, diagrams, and presentations.

**Relações:**
- `uses` → `creative/brand-studio-forge`
- `similar` → `creative/popular-web-designs`
- `similar` → `creative/brand-studio-forge`
- `used_by` → `infrastructure/vercel-deploy`
- `uses` → `creative/popular-web-designs`

### UI/UX Design Principles

- **Nome:** `creative/ui-ux-design-principles`
- **Arquivo:** `creative/ui-ux-design-principles/SKILL.md`
- **Tamanho:** 7,697 chars
- **Resumo:** Core UI/UX design principles — hierarchy, grids, typography, color, dark mode, icons
- **Type:** Reference
- **Timestamp:** 2026-06-28T18:35:00Z

Load this skill when you need to apply professional UI/UX design fundamentals to any visual output. Covers visual hierarchy, color strategy, typography rules, grid systems, spacing with 4-point scale, dark mode design, icon sizing, button states, micro-interactions, and overlay techniques.

**Relações:**
- `similar` → `creative/style-guide-consultation`
- `similar` → `creative/popular-web-designs`

### Hermes-Style Charts (matplotlib)

- **Nome:** `creative/hermes-style-charts`
- **Arquivo:** `creative/hermes-style-charts/SKILL.md`
- **Tamanho:** 5,593 chars
- **Resumo:** Data-viz in Hermes style — matplotlib pipeline, fonts, design tokens, QA.
- **Type:** Reference
- **Timestamp:** 2026-08-13T00:00:00Z

Load this skill when generating charts (bar, line, scatter) in the Hermes Agent design system with matplotlib. Covers the render pipeline and pitfalls: fonts, brand tokens, layout QA. Load style-guide-consultation for the catalog of other brands' guides (ID, IAF).

**Relações:**
- `similar` → `creative/style-guide-consultation`
- `similar` → `productivity/html-report-hermes`

### Open Design — daemon, CLI, MCP

- **Nome:** `creative/open-design`
- **Arquivo:** `creative/open-design/SKILL.md`
- **Tamanho:** 11,689 chars
- **Resumo:** Open Design daemon :7456, CLI od e MCP — gera protótipos e artes de marca.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-14T06:00:15Z

Carregue esta skill quando o usuário mencionar open-design, pedir para gerar artes/designs/protótipos, ou precisar diagnosticar o daemon :7456, o CLI od ou as tools MCP mcp_open_design_*. Workspace local-first (nexu-io/open-design, Apache-2.0) com daemon Express+SQLite e 460 plugins bundled (AirBnb, Apple, Ant, Linear). Layout persistente em /opt/data/open-design-repo — nunca /tmp.

**Relações:**
- `similar` → `software-development/agy`
- `similar` → `creative/style-guide-consultation`
- `similar` → `creative/ai-creative-assets`
- `similar` → `creative/brand-studio-forge`

## Copywriting

### Oferta Irresistível (Hormozi) — Landing Pages

- **Nome:** `copywriting/oferta-hormozi`
- **Arquivo:** `copywriting/oferta-hormozi/SKILL.md`
- **Tamanho:** 12,257 chars
- **Resumo:** Framework de Oferta Irresistível (Alex Hormozi) para landing pages de cursos e infoprodutos
- **Type:** Creative
- **Timestamp:** 2026-07-15T00:00:00Z

Carregue esta skill quando for escrever ou revisar uma landing page, página de vendas, seção de preços ou estrutura de oferta para cursos e infoprodutos. Aplica a Value Equation, o MAGIC headline framework, e os princípios de Grand Slam Offer para transformar copy de features em copy de transformação. pt-BR, zero anglicismos.

**Relações:**
- `similar` → `creative/copywriting`


## Board Game Design

### Board Game Design Pipeline

- **Nome:** `board-game-design`
- **Arquivo:** `board-game-design/SKILL.md`
- **Tamanho:** 19,393 chars
- **Resumo:** Board game design pipeline: concept to physical production.
- **Type:** Orchestrator
- **Timestamp:** 2026-07-31T00:00:00Z

Carregue esta skill quando for orquestrar o design de um board game — do pitch ao protótipo digital para playtest e produção física. Cobre arquitetura de agentes (Hermes orquestra, Pi Agent executa, Antigravity revisa), pesquisa de mercado BGG, GDD completo, implementação de protótipo web, balanceamento e produção. Compartilha volume /opt/data/code com os executores.

**Relações:**
- `uses` → `boardgame-design-principles`
- `similar` → `autonomous-ai-agents/product-pipeline`

### Board Game Design Skill

- **Nome:** `boardgame-design-principles`
- **Arquivo:** `boardgame-design-principles/SKILL.md`
- **Tamanho:** 8,202 chars
- **Resumo:** Eurogame design: asymmetry, economy, playtesting.
- **Type:** Reference
- **Timestamp:** 2026-07-31T00:00:00Z

Load this skill when designing or balancing a board game — mechanical design, asymmetric faction design, resource economy systems, playtesting methodology, and rules documentation. Reference for German-style Eurogame principles: meaningful decisions, action economy, tension points, and elegant mechanics.

**Relações:**
- `used_by` → `board-game-design`


## Business

### Análise Contratual (Risco para Subcontratada)

- **Nome:** `business/analise-contratual`
- **Arquivo:** `business/analise-contratual/SKILL.md`
- **Tamanho:** 5,159 chars
- **Resumo:** Use ao analisar contratos/minutas — subcontratação, LGPD.
- **Type:** Reference
- **Timestamp:** 2026-08-09T05:08:04Z

Carregue esta skill quando precisar analisar minuta de contrato, contrato, edital, plano de trabalho ou proposta — especialmente quando a ID Consultoria (ou um cliente) é subcontratada/fornecedora. Cobre checklist de riscos (subcontratação, pay-when-paid, LGPD, propriedade intelectual, SLA/multas), cruzamento contrato × plano de trabalho para achar divergências de escopo/valor/prazo, e identificação de partes e regime jurídico (Lei 14.133/2021, LGPD 13.709/2018). Usa google-workspace para localizar documentos no Drive e scripts/pdf2txt.py para extrair texto de PDFs. Entrega resumo executivo no chat + arquivo .md completo via MEDIA.

**Relações:**
- `uses` → `productivity/google-workspace`
- `uses` → `productivity/pdf`

### Elaboração de Proposta Comercial

- **Nome:** `business/elaboracao-proposta-comercial`
- **Arquivo:** `business/elaboracao-proposta-comercial/SKILL.md`
- **Tamanho:** 10,581 chars
- **Resumo:** ID Consultoria commercial proposals — client context to branded HTML + minuta.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-14T06:30:00Z

Load this skill when creating a commercial proposal from client context (documents, negotiation messages, meeting minutes). Builds the branded HTML proposal by editing the brand template directly, and produces a Google Docs contract minuta in the Minutas subfolder, preserving first/last pages. Validates content incrementally with the user following the Guia de Princípios.

**Relações:**
- `similar` → `business/analise-contratual`
- `uses` → `productivity/google-workspace`
- `similar` → `content-production/research-report-standards`

### Planejamento Estratégico para PME (≤2h)

- **Nome:** `business/planejamento-estrategico`
- **Arquivo:** `business/planejamento-estrategico/SKILL.md`
- **Tamanho:** 5,389 chars
- **Resumo:** Planejar estratégia de PME em sessão única de 2h — EOS, OKR, V2MOM, 1 página.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-15T00:00:00Z

Carregue esta skill quando um dono de PME (10-250 funcionários) + time pequeno pedirem planejamento estratégico em uma sessão de até 2h. Escolhe frameworks (EOS V/TO, OPSP, V2MOM, OKR) pelo tempo disponível e perfil da empresa, conduz a facilitação e entrega tudo em UMA página ao final. Trabalho em PT-BR com markdown estruturado e tabelas comparativas.

**Relações:**
- `similar` → `research/systematic-research`

### Facilitação de Planejamento Estratégico em 2 Horas

- **Nome:** `business/planejamento-estrategico-2h`
- **Arquivo:** `business/planejamento-estrategico-2h/SKILL.md`
- **Tamanho:** 9,226 chars
- **Resumo:** Facilitar planejamento estratégico em 2h — EOS V/TO + One-Page Strategic Plan.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-15T02:39:34Z

Carregue esta skill quando precisar facilitar uma sessão única de planejamento estratégico para dono de PME + time pequeno (3-12 pessoas), com entregável obrigatório de 1 página. Usa EOS V/TO (Wickman) + One-Page Strategic Plan (Harnish), técnicas Liberating Structures, pré-mortem e timeboxing rigoroso. BSC e Hoshin Kanri não fecham em 2h — servem só como lente conceitual.

**Relações:**
- `similar` → `productivity/meeting-action-items`
- `similar` → `productivity/weekly-review-planning`
- `similar` → `business/planejamento-estrategico`

### Proposta Comercial de Consultoria

- **Nome:** `business/proposta-comercial-consultoria`
- **Arquivo:** `business/proposta-comercial-consultoria/SKILL.md`
- **Tamanho:** 5,501 chars
- **Resumo:** Proposta comercial de consultoria — princípios, pricing e modelo HTML da marca ID.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-14T06:00:00Z

Carregue esta skill quando precisar criar, ajustar ou precificar uma proposta comercial de consultoria (ID Consultoria ou genérica). Validada em 14/08/2026 com 40+ fontes (HBR, VeraSage, RAIN Group, McKinsey/BCG/Bain). Cobre o Guia de Princípios, precificação, o modelo HTML com marca da ID e iterações slide a slide do modelo.

**Relações:**
- `similar` → `copywriting/oferta-hormozi`
- `similar` → `research/deep-research`
- `similar` → `creative/copywriting`
- `similar` → `productivity/html-pdf-fidelity`

### Valuation Consultivo

- **Nome:** `business/valuation-consultivo`
- **Arquivo:** `business/valuation-consultivo/SKILL.md`
- **Tamanho:** 12,593 chars
- **Resumo:** Valuation consultivo de startup early-stage — rNPV, âncoras de persuasão, planilha.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-15T03:00:00Z

Carregue esta skill quando conduzir valuation de empresa early-stage para investidores, do diálogo à planilha .xlsx pronta e narrativa persuasiva. Metodologia rNPV + 3 âncoras (deals comparáveis, rodadas, reverse DCF) + triangulação + cap table honesta. Não é biotech-only — serve para health, deeptech, SaaS e industrial.

**Relações:**
- `uses` → `productivity/xlsx`
- `similar` → `content-production/research-report-standards`
- `similar` → `business/proposta-comercial-consultoria`
- `similar` → `research/deep-research`

## Dogfood

### Dogfood: Systematic Web Application QA Testing

- **Nome:** `dogfood`
- **Arquivo:** `dogfood/SKILL.md`
- **Tamanho:** 9,600 chars
- **Resumo:** Exploratory QA of web applications — find bugs, gather evidence, produce reports
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

Exploratory QA of web applications — find bugs, gather evidence, produce reports.
Load this skill when you need to test a web application for issues. Covers systematic exploratory testing, bug discovery with screenshots and logs as evidence, structured bug reporting with reproduction steps, and QA summary reports for development teams.

**Relações:**
- `similar` → `github/codebase-inspection`
- `similar` → `software-development/systematic-debugging`
- `similar` → `github/github-pr-workflow`

## Education

### Backwards Design Unit Planner

- **Nome:** `education/backwards-design-unit-planner`
- **Arquivo:** `education/backwards-design-unit-planner/SKILL.md`
- **Tamanho:** 22,009 chars
- **Resumo:** Plan a unit using backwards design — outcomes to assessment to activities.
- **Type:** Template
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when starting a new unit or redesigning an existing one from standards. Maps desired outcomes through assessment evidence to learning activities. Based on Wiggins & McTighe's Understanding by Design framework.

**Relações:**
- `similar` → `education/scope-and-sequence-designer`
- `similar` → `education/competency-framework-translator`
- `similar` → `software-development/pipeline-educacional`


### Competency Framework Translator

- **Nome:** `education/competency-framework-translator`
- **Arquivo:** `education/competency-framework-translator/SKILL.md`
- **Tamanho:** 25,189 chars
- **Resumo:** Translate competency frameworks (DigComp, GreenComp, ISTE) into classroom activities.
- **Type:** Template
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when implementing framework standards in specific teaching contexts. Maps external competency frameworks like DigComp, GreenComp, or ISTE to classroom-ready activities with clear learning objectives and assessment criteria.

**Relações:**
- `similar` → `education/backwards-design-unit-planner`
- `similar` → `education/curriculum-knowledge-architecture-designer`
- `similar` → `software-development/pipeline-educacional`


### Curriculum Knowledge Architecture Designer

- **Nome:** `education/curriculum-knowledge-architecture-designer`
- **Arquivo:** `education/curriculum-knowledge-architecture-designer/SKILL.md`
- **Tamanho:** 48,056 chars
- **Resumo:** Map epistemic structure of a subject — knowledge types for curriculum sequencing.
- **Type:** Template
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when designing courses, restructuring programmes, or analysing knowledge architecture. Distinguishes vertical vs horizontal knowledge structures, conceptual vs contextual coherence, and cumulative vs segmented learning using Bernstein, Maton, and Muller frameworks.

**Relações:**
- `similar` → `education/scope-and-sequence-designer`
- `similar` → `education/competency-framework-translator`
- `similar` → `software-development/pipeline-educacional`


### Leverage and Response Design

- **Nome:** `education/leverage-and-response-design`
- **Arquivo:** `education/leverage-and-response-design/SKILL.md`
- **Tamanho:** 13,195 chars
- **Resumo:** Design wise systems interventions — maps actions against Meadows' leverage points.
- **Type:** Template
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when you have a systems analysis and need to design an intervention. Maps proposed actions against Meadows' 12 leverage points, checks for unintended consequences, generates alternatives, and identifies feedback loops that could undermine the intervention.

**Relações:**
- `similar` → `education/mental-model-mapper`
- `similar` → `education/scope-and-sequence-designer`


### Mental Model Mapper

- **Nome:** `education/mental-model-mapper`
- **Arquivo:** `education/mental-model-mapper/SKILL.md`
- **Tamanho:** 9,320 chars
- **Resumo:** Surface beliefs, assumptions, and values shaping a system.
- **Type:** Template
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when deeper mental models need examining with care and evidence. Elicits espoused theories vs theories-in-use, identifies paradigms as deep leverage points, and maps cultural mental models using Senge, Argyris & Schon, and Meadows frameworks.

**Relações:**
- `similar` → `education/leverage-and-response-design`
- `similar` → `education/scope-and-sequence-designer`


### Scope and Sequence Designer

- **Nome:** `education/scope-and-sequence-designer`
- **Arquivo:** `education/scope-and-sequence-designer/SKILL.md`
- **Tamanho:** 57,831 chars
- **Resumo:** Design scope and sequence — curriculum coherence across a programme or year.
- **Type:** Template
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when building new programmes, restructuring subjects, or ensuring progression. Shows vertical coherence (spiral curriculum, Bruner) and horizontal coherence (knowledge structures, Bernstein) across a programme or year, using Hattie's high-effect curriculum coherence variable.

**Relações:**
- `similar` → `education/backwards-design-unit-planner`
- `similar` → `education/curriculum-knowledge-architecture-designer`
- `similar` → `education/leverage-and-response-design`

## Email

### Email Inbox Triage

- **Nome:** `email/email-inbox-triage`
- **Arquivo:** `email/email-inbox-triage/SKILL.md`
- **Tamanho:** 4,320 chars
- **Resumo:** Triage an inbox: prioritize threads, draft replies safely.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-10T02:24:47Z

Triage an inbox: prioritize threads, draft replies safely.

Load this skill when you need to triage an email inbox — prioritize threads, spot urgent items, and draft safe replies without sending. Uses CLI mailboxes and integrates with google-workspace for Gmail flows.

**Relações:**
- `uses` → `productivity/google-workspace`
- `similar` → `productivity/document-to-action-items`
- `uses` → `productivity/taskflow-mcp`
- `similar` → `productivity/meeting-action-items`

## Github

### Codebase Inspection & Architecture Diagnostic

- **Nome:** `github/codebase-inspection`
- **Arquivo:** `github/codebase-inspection/SKILL.md`
- **Tamanho:** 10,326 chars
- **Resumo:** Multi-layered codebase diagnostics: structural mapping, dependency audit, git history, metrics, and health reports
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-12T02:23:22Z

Multi-layered codebase diagnostics: structural mapping, dependency audit, git history, metrics, and health reports.

**Relações:**
- `similar` → `software-development/systematic-debugging`
- `similar` → `software-development/improve-codebase-architecture`
- `uses` → `github/github-pr-workflow`

### GitHub Pull Request Workflow

- **Nome:** `github/github-pr-workflow`
- **Arquivo:** `github/github-pr-workflow/SKILL.md`
- **Tamanho:** 13,427 chars
- **Resumo:** GitHub umbrella — authentication, PR lifecycle, code review, and repo management
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-19T19:47:50Z

GitHub PR lifecycle: branch, commit, open, CI, merge.

**Relações:**
- `uses` → `infrastructure/deployment-pipeline`
- `uses` → `infrastructure/oracle-host-access`
- `similar` → `github/codebase-inspection`
- `similar` → `software-development/systematic-debugging`
- `uses` → `software-development/test-driven-development`

### GitHub Issue to Pull Request

- **Nome:** `github/github-issue-to-pr`
- **Arquivo:** `github/github-issue-to-pr/SKILL.md`
- **Tamanho:** 6,331 chars
- **Resumo:** Carry a GitHub issue to a verified PR with honest CI state.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-10T02:24:47Z

Carry a GitHub issue to a verified PR with honest CI state.

Load this skill when you need to turn a GitHub issue into a pull request — branch strategy, commits, PR body, and running CI to verify the change actually passes before claiming success. Complements github-pr-workflow.

**Relações:**
- `uses` → `github/github-pr-workflow`
- `similar` → `software-development/simplify-code`
- `uses` → `software-development/test-driven-development`
- `uses` → `software-development/systematic-debugging`

## Health

### Ares — Deus da Guerra, Coach Fitness

- **Nome:** `health/ares-fitness-coach`
- **Arquivo:** `health/ares-fitness-coach/SKILL.md`
- **Tamanho:** 6,392 chars
- **Resumo:** Deus da Guerra como coach fitness do Projeto Ares. Perfil, treinos e dieta calculados com base no biotipo
- **Type:** Health
- **Timestamp:** 2026-06-21T05:11:49Z

Load this skill when the user wants Ares (War God persona) as a fitness coach. Covers user profiling (biotype, exams, goals), workout plan generation, diet and nutrition calculation, and progress tracking with adjustments.

**Relações:**
- `similar` → `health-fitness/body-recomposition`
- `uses` → `health-fitness/body-recomposition`

### Ares Progress Graph — Weight Tracking

- **Nome:** `health/grafico-progresso-peso-ares`
- **Arquivo:** `health/grafico-progresso-peso-ares/SKILL.md`
- **Tamanho:** 7,587 chars
- **Resumo:** Gráfico de progresso de peso estilo Ares — matplotlib, vermelhos, claro.
- **Type:** Health
- **Timestamp:** 2026-07-12T00:00:00Z

Carregue esta skill quando precisar gerar o grafico padrao de progresso de peso do Projeto Ares. Renderiza PNG via matplotlib com paleta cardinal/crimson sobre fundo off-white, proporcao 10x5.5, linha de tendencia, linha de meta e eixo Y a partir de 70 kg. Usa venv dedicado em /opt/data/.venv-chart/.

**Relações:**
- `similar` → `health/ares-fitness-coach`
- `similar` → `health-fitness/body-recomposition`
- `uses` → `health-fitness/body-recomposition`

## Health & Fitness

### Body Recomposition — Métricas e Timeline

- **Nome:** `health-fitness/body-recomposition`
- **Arquivo:** `health-fitness/body-recomposition/SKILL.md`
- **Tamanho:** 8,465 chars
- **Resumo:** Tracking de métricas corporais (peso, BF, composição) + cálculos de TDEE/BMR, déficit calórico e timeline para recomposição
- **Type:** Health
- **Timestamp:** 2026-06-21T05:11:49Z

Load this skill when tracking body recomposition metrics — weight, body fat, and composition. Covers CSV data management, TDEE/BMR calculations, caloric deficit planning, timeline projections, and chart generation for progress visualization.

**Relações:**
- `similar` → `health/ares-fitness-coach`
- `used_by` → `health/ares-fitness-coach`
- `parent` → `health/ares-fitness-coach`
- `similar` → `productivity/html-report-hermes`

## Infrastructure

### Dashboard Performance Pipeline

- **Nome:** `infrastructure/dashboard-performance-pipeline`
- **Arquivo:** `infrastructure/dashboard-performance-pipeline/SKILL.md`
- **Tamanho:** 5,942 chars
- **Resumo:** Optimize dashboards — move aggregation from browser to backend via materialized views
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when a SPA dashboard loads slowly or transfers too much data (300 MB to 50 KB target). Covers Supabase materialized views, progressive loading with pagination, Vercel preview branch deployment, and the full backend-aggregation pipeline pattern.

**Relações:**
- `similar` → `infrastructure/data-pipeline-patterns`
- `similar` → `infrastructure/vercel-deploy`
- `uses` → `infrastructure/supabase`

### Data Pipeline Patterns

- **Nome:** `infrastructure/data-pipeline-patterns`
- **Arquivo:** `infrastructure/data-pipeline-patterns/SKILL.md`
- **Tamanho:** 6,742 chars
- **Resumo:** Reliability patterns for batch data pipelines — exponential backoff, API safeguards, cell-size truncation, and parallel execution guardrails
- **Type:** Reference
- **Timestamp:** 2026-08-09T05:08:04Z

Reliability patterns for batch data pipelines: exponential backoff, API call safeguards, error handling strategies for cron-driven automation.

**Relações:**
- `similar` → `infrastructure/deployment-pipeline`
- `used_by` → `software-development/dedalo-squad`
- `parent` → `infrastructure/gemini-rate-limit-backoff`

### Deployment Pipeline — Docker + GitHub Actions + SSH Deploy

- **Nome:** `infrastructure/deployment-pipeline`
- **Arquivo:** `infrastructure/deployment-pipeline/SKILL.md`
- **Tamanho:** 46,064 chars
- **Resumo:** CI/CD for Docker apps — GitHub Actions, ghcr.io registry, SSH deploy to bare metal
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

CI/CD pipeline for Docker-based apps: GitHub Actions → ghcr.io → SSH deploy to bare metal. Covers workflow design, registry auth, tag strategy, deploy key setup, migration management, and common pitfalls.

**Relações:**
- `uses` → `infrastructure/oracle-host-access`
- `similar` → `infrastructure/vercel-deploy`
- `similar` → `infrastructure/data-pipeline-patterns`
- `parent` → `infrastructure/vercel-deploy`

### Gemini Rate Limit Backoff

- **Nome:** `infrastructure/gemini-rate-limit-backoff`
- **Arquivo:** `infrastructure/gemini-rate-limit-backoff/SKILL.md`
- **Tamanho:** 4,395 chars
- **Resumo:** Exponential backoff for Google Gemini API rate limits (HTTP 429) — monkey-patching the genai SDK with jitter
- **Type:** Reference
- **Timestamp:** 2026-06-28T05:11:55Z

Exponential backoff for Google Gemini API rate limits (HTTP 429). Covers monkey-patching the genai SDK, extracting retry_delay from error messages, exponential backoff with jitter, and transparent retry for cron jobs.

**Relações:**
- `similar` → `infrastructure/data-pipeline-patterns`
- `used_by` → `software-development/dedalo-squad`

### GCP Cloud Build — CI/CD Automation

- **Nome:** `infrastructure/gcp-cloud-build`
- **Arquivo:** `infrastructure/gcp-cloud-build/SKILL.md`
- **Tamanho:** 6,140 chars
- **Resumo:** GCP Cloud Build CI/CD setup — GitHub triggers, connections, Docker builds, troubleshooting
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-17T00:00:00Z

Load this skill when setting up continuous integration on GCP: connecting GitHub repos to Cloud Build, creating push-to-deploy triggers, debugging connection/authentication issues, and wiring builds to Cloud Run jobs.

**Relações:**
- `similar` → `infrastructure/deployment-pipeline`
- `similar` → `infrastructure/vercel-deploy`
- `similar` → `github/github-pr-workflow`

### Hermes Cron Patterns

- **Nome:** `infrastructure/hermes-cron-patterns`
- **Arquivo:** `infrastructure/hermes-cron-patterns/SKILL.md`
- **Tamanho:** 10,219 chars
- **Resumo:** Hermes cron job patterns — timeout limits and background execution
- **Type:** Reference
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill when a cron job exceeds the 3-minute hard limit or needs to run long scripts. Covers the nohup background spawn pattern, script delivery, and timeout workarounds for the Hermes cron scheduler.

**Relações:**
- `similar` → `infrastructure/data-pipeline-patterns`

### Oracle VM — SSH Access from Hermes Container

- **Nome:** `infrastructure/oracle-host-access`
- **Arquivo:** `infrastructure/oracle-host-access/SKILL.md`
- **Tamanho:** 39,566 chars
- **Resumo:** SSH from Hermes Docker container to Oracle Linux host — key setup and diagnostics
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T05:11:55Z

SSH from Hermes Docker container to Oracle Linux host — key setup and diagnostics.

**Relações:**
- `used_by` → `infrastructure/deployment-pipeline`
- `used_by` → `github/github-pr-workflow`
- `used_by` → `productivity/relatorio-de-custos`

### Vercel Deploy — Skill

- **Nome:** `infrastructure/vercel-deploy`
- **Arquivo:** `infrastructure/vercel-deploy/SKILL.md`
- **Tamanho:** 27,451 chars
- **Resumo:** Deploy static sites and frontend apps to Vercel — from zero to production
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T05:11:55Z

Deploy static sites and frontend apps to Vercel — from zero to production. Covers CLI install, device-flow authentication, project creation, deploy, custom domains, env vars, and common pitfalls. Works in restricted environments.

**Relações:**
- `similar` → `infrastructure/deployment-pipeline`
- `similar` → `github/github-pr-workflow`
- `uses` → `productivity/html-report-hermes`

### Production Deployment — Post-CI Operations

- **Nome:** `infrastructure/production-deployment`
- **Arquivo:** `infrastructure/production-deployment/SKILL.md`
- **Tamanho:** 13,295 chars
- **Resumo:** Post-CI deploy operations — Docker rollout, DB schema, ingress routing, DNS fallback.
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when deploying a built application to production: verifying DB migrations ran, diagnosing container startup failures, checking Nginx/NPM routing, or handling a domain that stopped resolving. Covers the gray zone between CI completing and the site being live — the step most pipelines leave unscripted.

**Relações:**
- `similar` → `infrastructure/deployment-pipeline`
- `similar` → `infrastructure/vercel-deploy`
- `uses` → `infrastructure/oracle-host-access`
- `similar` → `infrastructure/moodle-admin`

### WhatsApp via Baileys — Python Integration

- **Nome:** `infrastructure/whatsapp-baileys-integration`
- **Arquivo:** `infrastructure/whatsapp-baileys-integration/SKILL.md`
- **Tamanho:** 22,530 chars
- **Resumo:** Integrate WhatsApp messaging into Python pipelines via Baileys — lifecycle, QR auth, REST bridge, multi-number
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill when you need to send WhatsApp messages from Python without paid APIs. Covers full lifecycle management (spawn, QR auth, session persistence, health checks, graceful shutdown), REST bridge with Z-API compatible interface for file/media delivery, and multi-number architecture. Replaces paid Z-API with local WhatsApp Web. Absorveu messaging/whatsapp-automation (merge 08/2026): migration checklist Z-API→Baileys, rate limiting, WhatsApp Web limitations e reference files (baileys-bridge-server.js, whatsapp_client.py, multi_assessor_config.py).

**Relações:**
- `similar` → `autonomous-ai-agents/messaging-platforms`

### Selfhost Service Deploy — Oracle ARM64

- **Nome:** `infrastructure/selfhost-service-deploy`
- **Arquivo:** `infrastructure/selfhost-service-deploy/SKILL.md`
- **Tamanho:** 40,247 chars
- **Resumo:** Deploy selfhosted services on Oracle ARM64 — Docker Compose, NPM routing, SSL
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when deploying any new selfhosted service on the Oracle VM (Docker host). Follows the established pattern: directory structure, docker-compose.yml, Nginx Proxy Manager routing, SSL termination via Let's Encrypt, and common ARM64 pitfalls.

**Relações:**
- `similar` → `infrastructure/selfhost-web-apps`
- `uses` → `infrastructure/oracle-host-access`

### Selfhost Web Apps on Oracle ARM64

- **Nome:** `infrastructure/selfhost-web-apps`
- **Arquivo:** `infrastructure/selfhost-web-apps/SKILL.md`
- **Tamanho:** 9,356 chars
- **Resumo:** Deploy web apps on Oracle ARM64 — Docker Compose, NPM, SSL, and hardening
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when deploying PHP, Python, or Node web applications on the Oracle host behind Nginx Proxy Manager. Covers the standard architecture pattern, SSL termination, PHP redirect loop fixes, and post-deploy hardening.

**Relações:**
- `similar` → `infrastructure/selfhost-service-deploy`
- `uses` → `infrastructure/oracle-host-access`

### Supabase Operations

- **Nome:** `infrastructure/supabase`
- **Arquivo:** `infrastructure/supabase/SKILL.md`
- **Tamanho:** 7,054 chars
- **Resumo:** Manage Supabase from Hermes — run SQL, deploy Edge Functions, manage migrations
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when working with any Supabase-backed project from a restricted environment. Covers running SQL without psql, linking projects, deploying Edge Functions, managing migrations, and refreshing materialized views.

**Relações:**
- `similar` → `infrastructure/data-pipeline-patterns`

### Moodle Administration — treinamentos.idconsultoria.ai

- **Nome:** `infrastructure/moodle-admin`
- **Arquivo:** `infrastructure/moodle-admin/SKILL.md`
- **Tamanho:** 22,057 chars
- **Resumo:** Administer Moodle — DB, students, mass email.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-09T05:08:04Z

Carregue esta skill quando precisar administrar o Moodle 5.2 de treinamentos.idconsultoria.ai — consultas SQL no Postgres via docker exec, gestão de estudantes, envio de email em massa personalizado e operações de manutenção. Cobre arquitetura Docker Compose (app, nginx, postgres, redis, cron) no host Oracle via SSH.

**Relações:**
- `uses` → `infrastructure/oracle-host-access`
- `similar` → `productivity/google-workspace`
- `similar` → `infrastructure/production-deployment`

### SearXNG + Firecrawl Repair (web_search vazio)

- **Nome:** `infrastructure/searxng-firecrawl-repair`
- **Arquivo:** `infrastructure/searxng-firecrawl-repair/SKILL.md`
- **Tamanho:** 6,724 chars
- **Resumo:** web_search empty? Diagnose and fix SearXNG→Firecrawl search engine chain.
- **Type:** Research
- **Timestamp:** 2026-08-15T04:00:00Z

Load this skill when web_search returns success with an empty web list — the search backend died silently. Covers the SearXNG→Firecrawl architecture, how to verify each link in the chain on the Oracle host, and repair steps. Not a Hermes bug: fix the backend.

**Relações:**
- `similar` → `autonomous-ai-agents/hermes-diagnostics`
- `similar` → `infrastructure/selfhost-service-deploy`
- `uses` → `infrastructure/oracle-host-access`

## Media

### HyperFrames Video Production

- **Nome:** `media/hyperframes-video-production`
- **Arquivo:** `media/hyperframes-video-production/SKILL.md`
- **Tamanho:** 22,551 chars
- **Resumo:** Produce deterministic MP4 videos via HyperFrames — HTML compositions to video
- **Type:** Media
- **Timestamp:** 2026-06-12T02:23:22Z

Produce deterministic MP4 videos using HyperFrames (HTML→video engine). Generates HTML compositions with GSAP animations, renders locally via npx hyperframes.

**Relações:**
- `uses` → `creative/brand-studio-forge`
- `uses` → `creative/style-guide-consultation`
- `similar` → `productivity/html-report-hermes`
- `similar` → `media/kindle-manga`

### Kindle Manga — Quality-Gated Manga to EPUB/MOBI

- **Nome:** `media/kindle-manga`
- **Arquivo:** `media/kindle-manga/SKILL.md`
- **Tamanho:** 59,831 chars
- **Resumo:** Prepare and transfer manga to Kindle — quality-gated conversion with resolution check, contrast correction, and grayscale EPUB generation
- **Type:** Media
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill when putting manga or comics on a Kindle, converting CBR/CBZ/PDF to Kindle format, or using KCC and Calibre for MOBI/AZW3 conversion. Covers source acquisition (Archive.org, Nyaa torrents, MangaDex API), quality gate with resolution and contrast checks, grayscale EPUB generation with PW11-native resize, and USB or Drive delivery.

**Relações:**
- `similar` → `media/manga-anime-data`
- `uses` → `productivity/google-workspace`
- `uses` → `media/manga-anime-data`

### Manga & Anime Data Research via AniList API

- **Nome:** `media/manga-anime-data`
- **Arquivo:** `media/manga-anime-data/SKILL.md`
- **Tamanho:** 4,718 chars
- **Resumo:** Research manga and anime data via AniList GraphQL API — rankings, scores, metadata, completion status, and genre filtering
- **Type:** Research
- **Timestamp:** 2026-06-28T05:11:55Z

Load this skill instead of web search when you need authoritative community ratings, detailed metadata, or status verification for anime/manga. Returns structured JSON data via direct GraphQL queries to the AniList public API.

**Relações:**
- `similar` → `media/kindle-manga`

### arXiv LaTeX to Kindle EPUB

- **Nome:** `media/arxiv-latex-to-kindle`
- **Arquivo:** `media/arxiv-latex-to-kindle/SKILL.md`
- **Tamanho:** 18,789 chars
- **Resumo:** Convert arXiv LaTeX to Kindle EPUB — tables, figures, Gmail delivery.
- **Type:** Media
- **Timestamp:** 2026-07-08T10:30:00Z

Load this skill when the user wants to download an arXiv paper, convert its LaTeX source to EPUB, and deliver it to a Kindle device. Handles the full pipeline: arXiv source download, Pandoc conversion, post-processing for tabularx->HTML table conversion, precise figure extraction from the PDF, EPUB rebuild, and Gmail API delivery.

**Relações:**
- `similar` → `media/kindle-articles`
- `similar` → `media/kindle-manga`
- `uses` → `productivity/google-workspace`

### Kindle Articles — Text Content to EPUB3

- **Nome:** `media/kindle-articles`
- **Arquivo:** `media/kindle-articles/SKILL.md`
- **Tamanho:** 19,012 chars
- **Resumo:** Prepare text content for Kindle — markdown to reflowable EPUB3.
- **Type:** Media
- **Timestamp:** 2026-07-07

Load this skill when putting research papers, long-form articles, blog posts, or any text-heavy documents on a Kindle. Covers markdown parsing, EPUB3 assembly, TOC generation, and delivery.

**Relações:**
- `similar` → `media/arxiv-latex-to-kindle`
- `similar` → `media/kindle-manga`
- `uses` → `productivity/google-workspace`

### HTML to Social Image (PNG)

- **Nome:** `media/html-to-social-image`
- **Arquivo:** `media/html-to-social-image/SKILL.md`
- **Tamanho:** 5,922 chars
- **Resumo:** Render HTML to social-media-optimized PNG images using Chromium headless screenshots
- **Type:** Media
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when creating images for Instagram, Twitter, Open Graph, or any social media platform. Covers Instagram stories/posts/reels, Twitter/OG cards, and any HTML-to-PNG export using Chromium headless via .deb extraction.

**Relações:**
- `similar` → `productivity/html-to-pdf-chromium`
- `similar` → `productivity/html-report-hermes`

### PDF/Deck → HTML Reconstruction

- **Nome:** `media/pdf-deck-to-html`
- **Arquivo:** `media/pdf-deck-to-html/SKILL.md`
- **Tamanho:** 7,714 chars
- **Resumo:** Convert PDF/Figma decks to HTML slides — original art preserved, real text.
- **Type:** Media
- **Timestamp:** 2026-08-14T00:00:00Z

Load this skill when converting presentations/PDFs into HTML that opens in the browser, keeping the ORIGINAL art with real selectable text. Validated formula: semantic HTML + original PDF art as background + real text positioned over PDF regions + explicit colors. Never redraw brand assets manually — extract them (v3 approved by user, v2 rejected).

**Relações:**
- `similar` → `productivity/html-pdf-fidelity`
- `similar` → `content-production/research-report-standards`

## Hermes Desktop Plugins

### Hermes Desktop Plugins

- **Nome:** `hermes-desktop-plugins`
- **Arquivo:** `hermes-desktop-plugins/SKILL.md`
- **Tamanho:** 9,198 chars
- **Resumo:** Write desktop app plugins for Hermes — UI panes, commands, keybinds, and themes
- **Type:** Reference
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when adding new UI elements or commands to the Hermes desktop app. Covers the plugin SDK: statusbar items, layout panes, command-palette commands, keybinds, routes, themes, and the Python backend namespace. A plugin is a single ESM file with no build step.

**Relações:**
- `similar` → `autonomous-ai-agents/hermes-agent`

## Productivity

### Google Workspace

- **Nome:** `productivity/google-workspace`
- **Arquivo:** `productivity/google-workspace/SKILL.md`
- **Tamanho:** 24,914 chars
- **Resumo:** Gmail, Calendar, Drive, Docs, Sheets via gws CLI — OAuth2 setup and automation
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T05:11:55Z

Gmail, Calendar, Drive, Docs, Sheets via gws CLI — OAuth2 setup and automation.

**Relações:**
- `similar` → `productivity/notion`
- `similar` → `productivity/taskflow-mcp`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `uses` → `infrastructure/data-pipeline-patterns`

### HTML Report — Hermes Design System

- **Nome:** `productivity/html-report-hermes`
- **Arquivo:** `productivity/html-report-hermes/SKILL.md`
- **Tamanho:** 15,276 chars
- **Resumo:** Render research reports as dark-themed HTML with SVG charts and Tufte typography
- **Type:** Template
- **Timestamp:** 2026-06-12T02:23:22Z

Render research reports as dark-themed HTML with SVG charts and Tufte-inspired typography.

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `productivity/html-to-pdf-chromium`
- `used_by` → `productivity/relatorio-de-custos`
- `used_by` → `productivity/html-to-pdf-chromium`
- `similar` → `content-production/research-report-standards`

### HTML → PDF com Chromium Headless

- **Nome:** `productivity/html-to-pdf-chromium`
- **Arquivo:** `productivity/html-to-pdf-chromium/SKILL.md`
- **Tamanho:** 8,717 chars
- **Resumo:** Convert HTML to high-fidelity PDF using Chromium headless via .deb extraction. Fallback to WeasyPrint on ARM64
- **Type:** Template
- **Timestamp:** 2026-07-16T22:30:00Z

Convert HTML to high-fidelity PDF using Chromium headless via .deb extraction. Fallback to WeasyPrint on ARM64 when Chromium binaries are unavailable. Covers Chromium headless installation via Debian .deb extraction without root or Playwright, PDF generation with full CSS support, WeasyPrint for ARM64 systems, and common rendering fixes.

**Relações:**
- `uses` → `productivity/html-report-hermes`
- `used_by` → `productivity/html-report-hermes`
- `similar` → `infrastructure/data-pipeline-patterns`

### Notion

- **Nome:** `productivity/notion`
- **Arquivo:** `productivity/notion/SKILL.md`
- **Tamanho:** 15,982 chars
- **Resumo:** Notion API plus ntn CLI — pages, databases, markdown import, Workers integration
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-12T02:23:22Z

Notion API + ntn CLI: pages, databases, markdown import, Workers integration.

**Relações:**
- `similar` → `productivity/taskflow-mcp`
- `similar` → `productivity/google-workspace`

### Relatório de Custos — Skill de Geração

- **Nome:** `productivity/relatorio-de-custos`
- **Arquivo:** `productivity/relatorio-de-custos/SKILL.md`
- **Tamanho:** 10,354 chars
- **Resumo:** Generate cost reports for multi-agent projects with real token data from Hermes and
- **Type:** Template
- **Timestamp:** 2026-06-19T19:47:50Z

Generate cost reports for multi-agent projects with real token data from Hermes and Pi Agent session logs.

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `productivity/html-report-hermes`
- `similar` → `software-development/backlog-and-sprint`
- `similar` → `productivity/taskflow-mcp`

### TaskFlow MCP — Ferramentas e Workflows

- **Nome:** `productivity/taskflow-mcp`
- **Arquivo:** `productivity/taskflow-mcp/SKILL.md`
- **Tamanho:** 9,983 chars
- **Resumo:** GTD task management via MCP (Model Context Protocol) — connects over SSE
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-14T05:15:09Z

Load this skill when managing tasks via the TaskFlow MCP server. Covers connecting over SSE (StreamableHTTP POST does not work), creating and updating tasks, managing contexts and projects, processing inbox items, and running weekly GTD reviews.

**Relações:**
- `similar` → `productivity/notion`
- `similar` → `software-development/backlog-and-sprint`
- `used_by` → `autonomous-ai-agents/hermes-agent`

### TaskFlow MCP Rules — Timezone e Padrões

- **Nome:** `taskflow-mcp-rules`
- **Arquivo:** `taskflow-mcp-rules/SKILL.md`
- **Tamanho:** 2,258 chars
- **Resumo:** TaskFlow MCP usage rules — timezone, date patterns, best practices.
- **Type:** Reference
- **Timestamp:** 2026-08-02T00:00:00Z

Carregue esta skill ao usar as ferramentas MCP do TaskFlow: converte datas UTC para BRT (UTC-3) ao exibir, segue o padrão de confirmação em 2 passos para escritas com ActionToken, e usa os comandos de leitura disponíveis. Cobre regras de exibição de prioridade e boas práticas de escrita.

**Relações:**
- `uses` → `productivity/taskflow-mcp`
- `similar` → `software-development/taskflow-ui-debugging`

### Petdex — Animated Mascot Pets

- **Nome:** `productivity/petdex`
- **Arquivo:** `productivity/petdex/SKILL.md`
- **Tamanho:** 3,725 chars
- **Resumo:** Install and select animated petdex mascots for Hermes
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T00:00:00Z

Load this skill when you want to browse, install, or switch animated mascot pets that react to agent activity across the CLI and TUI.

**Relações:**
- `similar` → `autonomous-ai-agents/hermes-agent`

### DOCX Skill

- **Nome:** `productivity/docx`
- **Arquivo:** `productivity/docx/SKILL.md`
- **Tamanho:** 8,637 chars
- **Resumo:** Create, read, edit Word .docx documents and templates.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-02T00:00:00Z

Load this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx) or Word templates (.dotx) — reports, memos, letters, letterheads, tables of contents, tracked changes, and comments. Covers both the high-level creation path (docx-js npm) and surgical XML editing, plus pandoc/LibreOffice for reading and rendering. Do NOT use for PDFs, spreadsheets, or presentations.

**Relações:**
- `similar` → `productivity/pdf`
- `similar` → `productivity/xlsx`

### PDF Skill

- **Nome:** `productivity/pdf`
- **Arquivo:** `productivity/pdf/SKILL.md`
- **Tamanho:** 7,498 chars
- **Resumo:** Create, merge, split, fill, and secure PDF files.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-02T00:00:00Z

Load this skill whenever the user wants to do anything with PDF files: reading or extracting text/tables, combining or merging multiple PDFs, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting, extracting images, or OCR on scanned PDFs. Uses pypdf, pdfplumber, reportlab, poppler-utils, and qpdf. For heavy text extraction from scanned documents prefer ocr-and-documents.

**Relações:**
- `similar` → `productivity/docx`
- `similar` → `productivity/xlsx`
- `similar` → `productivity/html-to-pdf-chromium`

### XLSX Skill

- **Nome:** `productivity/xlsx`
- **Arquivo:** `productivity/xlsx/SKILL.md`
- **Tamanho:** 9,632 chars
- **Resumo:** Create, read, edit Excel .xlsx spreadsheets and CSVs.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-02T00:00:00Z

Load this skill any time a spreadsheet file is the primary input or output: opening, reading, editing, or fixing an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file; creating a new spreadsheet from scratch or from other data; converting between tabular formats; cleaning messy tabular data. Uses openpyxl, pandas, markitdown, and LibreOffice for formula recalculation. Every formula-bearing output must be recalculated and error-free before delivery.

**Relações:**
- `similar` → `productivity/docx`
- `similar` → `productivity/pdf`

### Document to Action Items

- **Nome:** `productivity/document-to-action-items`
- **Arquivo:** `productivity/document-to-action-items/SKILL.md`
- **Tamanho:** 4,231 chars
- **Resumo:** Extract cited obligations, deadlines, tasks from documents.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-10T02:24:47Z

Extract cited obligations, deadlines, tasks from documents.

Load this skill when you need to extract obligations, deadlines and tasks from a document (contract, report, brief) — with citations back to the source, owners, and due dates. Works with pdf/docx/notion inputs.

**Relações:**
- `uses` → `productivity/pdf`
- `uses` → `productivity/docx`
- `similar` → `productivity/meeting-action-items`
- `uses` → `productivity/xlsx`
- `uses` → `productivity/google-workspace`
- `uses` → `productivity/notion`

### Google Docs/Sheets Formatting (REST API)

- **Nome:** `productivity/google-docs-formatting`
- **Arquivo:** `productivity/google-docs-formatting/SKILL.md`
- **Tamanho:** 7,564 chars
- **Resumo:** Format Google Docs/Sheets via REST API (markdown, chips).
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-11T00:00:00Z

Format Google Docs/Sheets via REST API (markdown, chips).

Load this skill when you need to format Google Docs or Sheets through the REST API — markdown conversion (md-to-gdoc), chips and checkboxes, tables, and mermaid rendering to images. Complements google-workspace with pixel-level fidelity notes.

**Relações:**
- `uses` → `productivity/google-workspace`
- `similar` → `productivity/google-sheets-automation`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `similar` → `productivity/xlsx`

### Google Sheets Automation (UX/UI via API)

- **Nome:** `productivity/google-sheets-automation`
- **Arquivo:** `productivity/google-sheets-automation/SKILL.md`
- **Tamanho:** 5,953 chars
- **Resumo:** Polish Google Sheets via API (dropdowns, formulas, KPIs).
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-12T00:00:00Z

Polish Google Sheets via API (dropdowns, formulas, KPIs).

Load this skill when you need to polish Google Sheets via API — data validation dropdowns, formulas, KPI sheets, and UX best practices. Complements google-workspace and xlsx.

**Relações:**
- `uses` → `productivity/google-workspace`
- `similar` → `productivity/google-docs-formatting`
- `similar` → `productivity/xlsx`
- `used_by` → `autonomous-ai-agents/product-pipeline`

### HTML → PDF Fidelity (browser-identical)

- **Nome:** `productivity/html-pdf-fidelity`
- **Arquivo:** `productivity/html-pdf-fidelity/SKILL.md`
- **Tamanho:** 9,298 chars
- **Resumo:** HTML→PDF identical to the browser — fonts, layout, 1 page.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-12T02:54:45Z

HTML→PDF identical to the browser — fonts, layout, 1 page.

Load this skill when a PDF export differs from the browser rendering (fonts, layout, pagination) or the user demands fidelidade máxima HTML→PDF. Chromium headless print pipeline with exact font embedding and one-page control.

**Relações:**
- `uses` → `productivity/html-to-pdf-chromium`
- `similar` → `productivity/resume-ats-engine`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `similar` → `media/html-to-social-image`
- `similar` → `productivity/html-report-hermes`
- `used_by` → `content-production/research-report-standards`

### Meeting Action Items

- **Nome:** `productivity/meeting-action-items`
- **Arquivo:** `productivity/meeting-action-items/SKILL.md`
- **Tamanho:** 4,072 chars
- **Resumo:** Turn meeting notes into cited decisions, owners, tickets.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-10T02:24:47Z

Turn meeting notes into cited decisions, owners, tickets.

Load this skill when you have meeting notes or transcripts and need to extract decisions, action items, owners and deadlines — with citations and optional ticket creation. Complements document-to-action-items.

**Relações:**
- `uses` → `productivity/google-workspace`
- `similar` → `productivity/document-to-action-items`
- `similar` → `productivity/weekly-review-planning`
- `uses` → `productivity/taskflow-mcp`
- `uses` → `productivity/notion`

### Product Price Monitor

- **Nome:** `productivity/product-price-monitor`
- **Arquivo:** `productivity/product-price-monitor/SKILL.md`
- **Tamanho:** 4,677 chars
- **Resumo:** Watch product, flight, or listing prices; alert on target.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-10T02:24:47Z

Watch product, flight, or listing prices; alert on target.

Load this skill when you need to monitor product, flight or listing prices and alert when they hit a target — watch URLs, parse price changes, and deliver notifications. Pair with hermes-cron-patterns for scheduled checks.

**Relações:**
- `uses` → `infrastructure/hermes-cron-patterns`
- `similar` → `research/competitor-news-monitor`
- `uses` → `autonomous-ai-agents/messaging-platforms`

### Resume ATS Engine — currículo otimizado por vaga

- **Nome:** `productivity/resume-ats-engine`
- **Arquivo:** `productivity/resume-ats-engine/SKILL.md`
- **Tamanho:** 13,032 chars
- **Resumo:** Currículo ATS: desenha p/ vaga, exporta .docx/PDF e avalia.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-11T00:00:00Z

Currículo ATS: desenha p/ vaga, exporta .docx/PDF e avalia.

Carregue esta skill quando for otimizar um currículo para uma vaga específica — desenho direcionado ao ATS, exportação .docx/PDF e avaliação 0-10 da adequação. Integra docx, pdf, html-to-pdf-chromium e html-report-hermes.

**Relações:**
- `uses` → `productivity/docx`
- `uses` → `productivity/pdf`
- `uses` → `productivity/html-to-pdf-chromium`
- `uses` → `software-development/agy`
- `uses` → `autonomous-ai-agents/messaging-platforms`

### Weekly Review and Planning

- **Nome:** `productivity/weekly-review-planning`
- **Arquivo:** `productivity/weekly-review-planning/SKILL.md`
- **Tamanho:** 4,234 chars
- **Resumo:** Weekly reset: commitments, stalled work, next-week plan.
- **Type:** Orchestrator
- **Timestamp:** 2026-08-10T02:24:47Z

Weekly reset: commitments, stalled work, next-week plan.

Load this skill when you need a weekly review and planning session — collect open commitments, identify stalled work, and produce a focused next-week plan. Integrates with taskflow and calendar workflows.

**Relações:**
- `uses` → `productivity/google-workspace`
- `similar` → `email/email-inbox-triage`
- `similar` → `productivity/taskflow-mcp`
- `similar` → `productivity/document-to-action-items`
- `uses` → `taskflow-mcp-rules`

### Google Sheets — Formatação via API (pitfalls)

- **Nome:** `productivity/google-sheets-formatting`
- **Arquivo:** `productivity/google-sheets-formatting/SKILL.md`
- **Tamanho:** 6,001 chars
- **Resumo:** Formatar Google Sheets via API — batchUpdate pitfalls validados.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-15T09:15:00Z

Carregue esta skill ao criar/popular/formatar planilha Google via Sheets API (googleapiclient, gws, batchUpdate): múltiplas abas, fórmulas vivas, banding, charts e numberFormat. Cobre erros reais (No grid with id, sobreposição de addBanding, BOTTOM_AXIS, valores que não formatam como moeda/%). Complementa google-workspace com lições de formatação validadas em execução real.

**Relações:**
- `uses` → `productivity/google-workspace`
- `similar` → `business/valuation-consultivo`

### PDF Slides → HTML

- **Nome:** `productivity/pdf-slides-to-html`
- **Arquivo:** `productivity/pdf-slides-to-html/SKILL.md`
- **Tamanho:** 6,502 chars
- **Resumo:** Convert PDF slide decks to HTML — original art preserved, real text.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-14T05:00:55Z

Load this skill when the user hands over a PDF slide deck / proposal / presentation and wants it as HTML: pixel-perfect clone, strongly inspired rebuild, or semantic HTML. Also applies when the PDF came out of Figma or contains unselectable text. Covers analysis, vector art extraction, and semantic HTML output.

**Relações:**
- `similar` → `productivity/html-pdf-fidelity`
- `uses` → `productivity/html-to-pdf-chromium`
- `uses` → `productivity/pdf`

### PDF → HTML

- **Nome:** `productivity/pdf-to-html`
- **Arquivo:** `productivity/pdf-to-html/SKILL.md`
- **Tamanho:** 9,297 chars
- **Resumo:** PDF→HTML: Type3/Figma extraction gotchas + clean semantic rebuild.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-14T05:00:00Z

Load this skill when replicating a PDF design as HTML (slide deck, proposal, one-pager) or extracting vector art/text for the web. Especially relevant for Figma-exported PDFs (Type3 fonts) — full of silent traps. Default for this user: clean semantic rebuild with foreground/background separated, not pixel-perfect SVG.

**Relações:**
- `similar` → `productivity/html-pdf-fidelity`
- `uses` → `productivity/pdf`
- `uses` → `productivity/html-to-pdf-chromium`
- `similar` → `productivity/html-report-hermes`

### PDF → HTML Replication

- **Nome:** `productivity/pdf-to-html-replication`
- **Arquivo:** `productivity/pdf-to-html-replication/SKILL.md`
- **Tamanho:** 5,893 chars
- **Resumo:** Convert PDF decks/documents to faithful HTML — pixel-perfect or semantic.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-14T05:35:18Z

Load this skill when converting a PDF deck or document to faithful HTML, whether the user wants pixel-perfect positioning or clean semantic structure. Covers brand asset extraction (logos, icons, backgrounds) and the pitfalls of Type3/Figma exports. Complements html-pdf-fidelity for the reverse direction.

**Relações:**
- `uses` → `productivity/pdf`
- `similar` → `productivity/html-pdf-fidelity`
- `similar` → `autonomous-ai-agents/messaging-platforms`

## Read Reddit

### Read Reddit via RSS

- **Nome:** `read-reddit`
- **Arquivo:** `read-reddit/SKILL.md`
- **Tamanho:** 11,231 chars
- **Resumo:** Read Reddit subreddits via RSS feeds — bypasses API rate limits and bot detection
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T05:11:55Z

Read Reddit subreddits reliably via RSS feeds — bypasses API rate limits and bot detection. For research, curation, or news gathering.

**Relações:**
- `similar` → `research/tech-trend-discovery`
- `similar` → `research/deep-research`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `research/deep-research`
- `used_by` → `research/augmentation-process-design`

## Research

### Augmentação Query — Busca Semântica

- **Nome:** `research/augmentacao-query`
- **Arquivo:** `research/augmentacao-query/SKILL.md`
- **Tamanho:** 4,590 chars
- **Resumo:** Busca semântica nas 97 soluções de Aumentação de Processos com IA via Vulcano MCP
- **Type:** Research
- **Timestamp:** 2026-06-28T05:11:55Z

Busca semântica nas 97 soluções de Aumentação de Processos com IA via Vulcano MCP.

**Relações:**
- `similar` → `research/augmentation-process-design`
- `used_by` → `software-development/process-augmentation-pipeline`

### Augmentation Process Design

- **Nome:** `research/augmentation-process-design`
- **Arquivo:** `research/augmentation-process-design/SKILL.md`
- **Tamanho:** 9,639 chars
- **Resumo:** Design, research and curadoria de soluções de augmentação de processos com IA
- **Type:** Research
- **Timestamp:** 2026-06-28T05:11:55Z

Design, research and curadoria de soluções de augmentação de processos com IA — taxonomia A/B × I/II/III.

**Relações:**
- `similar` → `research/augmentacao-query`
- `uses` → `software-development/process-augmentation-pipeline`
- `parent` → `research/augmentacao-query`
- `similar` → `research/deep-research`

### Deep Research Skill

- **Nome:** `research/deep-research`
- **Arquivo:** `research/deep-research/SKILL.md`
- **Tamanho:** 25,738 chars
- **Resumo:** Multi-agent deep research: decompose, dispatch agents, cross-validate, synthesize
- **Type:** Research
- **Timestamp:** 2026-06-19T19:47:50Z

Multi-agent deep research pipeline: decompose topics, dispatch parallel agents, review, cross-validate, synthesize.

**Relações:**
- `similar` → `research/tech-trend-discovery`
- `uses` → `research/tech-trend-discovery`
- `uses` → `research/user-interview`
- `uses` → `read-reddit`
- `similar` → `research/augmentacao-query`
- `uses` → `productivity/html-report-hermes`
- `similar` → `research/systematic-research`

### Digital Clone Persona

- **Nome:** `research/digital-clone-persona`
- **Arquivo:** `research/digital-clone-persona/SKILL.md`
- **Tamanho:** 10,081 chars
- **Resumo:** Create digital clone personas through deep web research — discover, extract, and
- **Type:** Research
- **Timestamp:** 2026-06-14T05:15:09Z

Create digital clone personas through deep web research — discover, extract, and embody a person's identity, voice, and expertise as an AI-roleplayable persona.

**Relações:**
- `uses` → `research/deep-research`
- `uses` → `research/user-interview`
- `similar` → `research/tech-trend-discovery`
- `similar` → `creative/brand-studio-forge`
- `similar` → `research/systematic-research`

### Model Benchmark Frontier

- **Nome:** `research/model-benchmark-frontier`
- **Arquivo:** `research/model-benchmark-frontier/SKILL.md`
- **Tamanho:** 7,371 chars
- **Resumo:** Compare AI models — intelligence vs parameters, convex hull, local hardware analysis
- **Type:** Research
- **Timestamp:** 2026-06-12T02:23:22Z

Compare AI models — intelligence vs parameters, convex hull analysis, local hardware analysis for inference.

**Relações:**
- `similar` → `research/deep-research`
- `similar` → `research/tech-trend-discovery`
- `similar` → `software-development/spike`
- `used_by` → `software-development/plan`

### Tech Trend Discovery

- **Nome:** `research/tech-trend-discovery`
- **Arquivo:** `research/tech-trend-discovery/SKILL.md`
- **Tamanho:** 15,641 chars
- **Resumo:** Discover what tech and AI communities discuss — trending topics and hot discussions
- **Type:** Research
- **Timestamp:** 2026-06-12T02:23:22Z

Discover what the tech/AI community is discussing right now — trending topics, hot discussions, and breaking conversations.

**Relações:**
- `similar` → `research/deep-research`
- `used_by` → `research/deep-research`
- `uses` → `read-reddit`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `similar` → `read-reddit`

### User Interview

- **Nome:** `research/user-interview`
- **Arquivo:** `research/user-interview/SKILL.md`
- **Tamanho:** 9,558 chars
- **Resumo:** Structured user/proxy interview protocol for product research — plan, frame
- **Type:** Research
- **Timestamp:** 2026-06-12T02:23:22Z

Structured user/proxy interview protocol for product research — plan, frame, listen, synthesize, extract personas.

**Relações:**
- `used_by` → `software-development/ideation-drilling`
- `used_by` → `software-development/backlog-and-sprint`
- `used_by` → `research/deep-research`
- `uses` → `research/digital-clone-persona`
- `similar` → `research/deep-research`

### Market Research Synthesis

- **Nome:** `research/market-research-synthesis`
- **Arquivo:** `research/market-research-synthesis/SKILL.md`
- **Tamanho:** 19,103 chars
- **Resumo:** Produce market analysis reports — personas, journeys, expectations, behavior.
- **Type:** Research
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when conducting market research for Brazilian/LATAM markets where web research tools face comprehensive blocking. Produces structured reports covering buyer personas, customer journeys, expectations hierarchies, purchasing behavior, and retention/fidelization. Pivots to domain-knowledge synthesis with transparent caveats when web tools fail.

**Relações:**
- `similar` → `research/deep-research`
- `similar` → `research/user-interview`
- `similar` → `software-development/ideation-drilling`
- `similar` → `research/systematic-research`
- `similar` → `content-production/research-report-standards`

### Systematic Single-Agent Research

- **Nome:** `research/systematic-research`
- **Arquivo:** `research/systematic-research/SKILL.md`
- **Tamanho:** 26,836 chars
- **Resumo:** Single-agent deep research via direct source URLs.
- **Type:** Research
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill when web_search is consistently unavailable (returns empty arrays for ALL queries after 2+ attempts) and you need thorough research without multi-agent dispatch. Uses domain knowledge to identify authoritative source URLs, batch parallel web_extract calls, handle blocked/404 pages, and page through large truncated encyclopedia-style articles. Produces cited, structured reports with source attribution. Complementary to deep-research (which covers multi-agent dispatch).

**Relações:**
- `similar` → `research/deep-research`
- `similar` → `research/market-research-synthesis`
- `similar` → `research/digital-clone-persona`

### Grounded Citations

- **Nome:** `research/grounded-citations`
- **Arquivo:** `research/grounded-citations/SKILL.md`
- **Tamanho:** 11,937 chars
- **Resumo:** Ground answers and documents in cited, verifiable sources.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill whenever an answer or artifact rests on information you fetched rather than knew — research, comparisons, news summaries, reports, briefs, docs, decks, or any multi-source synthesis where the user will want to check your work. Uses a ledger script (scripts/sources.py, stdlib-only) that owns the url → [n] mapping so citation numbers come from retrieval, never memory; cite-while-drafting with inline [n] ids, mechanically rendered Sources blocks, and a verify step that fails drafts with unknown ids or thin coverage. Fact-checking mode attaches verbatim quotes per source and flags model-knowledge claims [unverified].

**Relações:**
- `similar` → `research/systematic-research`
- `similar` → `research/deep-research`
- `similar` → `content-production/research-report-standards`

### Competitor News Monitor

- **Nome:** `research/competitor-news-monitor`
- **Arquivo:** `research/competitor-news-monitor/SKILL.md`
- **Tamanho:** 4,752 chars
- **Resumo:** Watch named companies for material news; cited digests.
- **Type:** Research
- **Timestamp:** 2026-08-10T02:24:47Z

Watch named companies for material news; cited digests.

Load this skill when you need to monitor named companies for material news — sources, deduplication, and cited digests delivered on a schedule. Complements market-research-synthesis and deep-research.

**Relações:**
- `similar` → `research/market-research-synthesis`
- `similar` → `research/deep-research`
- `similar` → `research/tech-trend-discovery`
- `uses` → `infrastructure/hermes-cron-patterns`

## Social Media

### Brand IAF — Conteúdo

- **Nome:** `social-media/brand-iaf-conteudo`
- **Arquivo:** `social-media/brand-iaf-conteudo/SKILL.md`
- **Tamanho:** 5,867 chars
- **Resumo:** Content for IA que Funciona community — brand constants, voice, tone, templates
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

Content for IA que Funciona community — brand constants, voice, tone, templates. Use to generate any community text — daily newsletter, posts, discussions, welcome messages.

**Relações:**
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `similar` → `creative/copywriting`
- `similar` → `creative/style-guide-consultation`
- `uses` → `software-development/agy`

### Social Media Video Content Extraction

- **Nome:** `social-media/social-media-video-content`
- **Arquivo:** `social-media/social-media-video-content/SKILL.md`
- **Tamanho:** 4,495 chars
- **Resumo:** Extract subtitles, descriptions, and metadata from social media videos
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-28T19:30:00Z

Load this skill when the user sends a TikTok, Instagram Reel, or YouTube Shorts URL and needs transcript, summary, or spoken content extraction — especially when the browser can't play the video.

**Relações:**
- `similar` → `social-media/brand-iaf-conteudo`

## NSFW Content Discovery

### NSFW Content Discovery

- **Nome:** `nsfw-content-discovery`
- **Arquivo:** `nsfw-content-discovery/SKILL.md`
- **Tamanho:** 5,656 chars
- **Resumo:** Find adult/NSFW content across platforms — creators, performers, search engines
- **Type:** Reference
- **Timestamp:** 2026-06-28T00:00:00Z

Load this skill when searching for explicit content from a specific creator or performer. Covers the ecosystem of external search engines, agent skills landscape, and Hermes browser automation workflow for adult sites.

**Relações:**
- `similar` → `social-media/social-media-video-content`

## Software Development

### agy — Antigravity CLI (Consultor Externo)

- **Nome:** `software-development/agy`
- **Arquivo:** `software-development/agy/SKILL.md`
- **Tamanho:** 29,176 chars
- **Resumo:** Versatile skill for coordinating Google Antigravity CLI for any design project type.
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-21T05:11:49Z

Load this skill for strategic design tasks — visual HTML output, brand presentations, UI mockups, SVGs, and prototypes. Covers agy installation, OAuth authentication via tmux, and design workflows. Part of the three-tier agent hierarchy (agy > Pi best > Pi cost) where agy serves as external specialist consultant.

**Relações:**
- `used_by` → `software-development/backlog-and-sprint`
- `used_by` → `productivity/relatorio-de-custos`
- `similar` → `creative/ai-creative-assets`
- `used_by` → `software-development/process-augmentation-pipeline`
- `uses` → `software-development/threejs-rendering-debug`
- `similar` → `autonomous-ai-agents/pi-agent-coordination`

### Backlog & Sprint

- **Nome:** `software-development/backlog-and-sprint`
- **Arquivo:** `software-development/backlog-and-sprint/SKILL.md`
- **Tamanho:** 79,774 chars
- **Resumo:** Backlog management and Sprint execution for product iteration (Fase 5) —
- **Type:** Orchestrator
- **Timestamp:** 2026-06-12T02:23:22Z

Backlog management and Sprint execution for product iteration (Fase 5). Mantém uma backlog não-estruturada de pedidos de melhoria, e orquestra Sprints completas (PM → UX/UI → Engineering → Review → Close).

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `research/user-interview`
- `similar` → `productivity/relatorio-de-custos`
- `similar` → `productivity/taskflow-mcp`
- `uses` → `software-development/ideation-drilling`
- `uses` → `software-development/plan`
- `uses` → `software-development/test-driven-development`
- `uses` → `autonomous-ai-agents/pi-session-audit`
- `uses` → `software-development/simplify-code`
- `similar` → `software-development/dedalo-squad`

### BPMN Diagram Renderer

- **Nome:** `software-development/bpmn-diagram-renderer`
- **Arquivo:** `software-development/bpmn-diagram-renderer/SKILL.md`
- **Tamanho:** 11,205 chars
- **Resumo:** Render BPMN 2.0 XML diagrams to SVG/PNG using bpmn-js and Chromium headless
- **Type:** Template
- **Timestamp:** 2026-06-28T05:11:55Z

Render BPMN 2.0 XML diagrams to SVG/PNG using bpmn-js + Chromium headless — identify business process flows from process mapping.

**Relações:**
- `similar` → `software-development/dedalo-squad`
- `uses` → `productivity/html-to-pdf-chromium`
- `used_by` → `software-development/dedalo-squad`
- `used_by` → `software-development/process-augmentation-pipeline`
- `similar` → `software-development/threejs-rendering-debug`

### Dédalo Squad

- **Nome:** `software-development/dedalo-squad`
- **Arquivo:** `software-development/dedalo-squad/SKILL.md`
- **Tamanho:** 18,807 chars
- **Resumo:** Pipeline Dédalo Squad — mapeamento de processos com POPs e diagramas BPMN 2.0
- **Type:** Orchestrator
- **Timestamp:** 2026-06-19T19:47:50Z

Pipeline Dédalo Squad — mapeamento de processos com POPs e diagramas BPMN 2.0 automatizados.

**Relações:**
- `similar` → `software-development/bpmn-diagram-renderer`
- `uses` → `productivity/html-to-pdf-chromium`
- `uses` → `software-development/bpmn-diagram-renderer`
- `uses` → `infrastructure/gemini-rate-limit-backoff`
- `uses` → `research/user-interview`

### Authoring Hermes-Agent Skills (in-repo)

- **Nome:** `software-development/hermes-agent-skill-authoring`
- **Arquivo:** `software-development/hermes-agent-skill-authoring/SKILL.md`
- **Tamanho:** 12,026 chars
- **Resumo:** Author SKILL.md and DESIGN.md token specs in-repo — frontmatter, validator
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

Author in-repo SKILL.md + DESIGN.md token specs: frontmatter, validator, structure. Merged with design-md skill.

**Relações:**
- `uses` → `software-development/plan`
- `used_by` → `software-development/skills-repo-curator`
- `similar` → `software-development/skills-repo-curator`

### Ideation Drilling (Hermes — Orchestrator)

- **Nome:** `software-development/ideation-drilling`
- **Arquivo:** `software-development/ideation-drilling/SKILL.md`
- **Tamanho:** 14,643 chars
- **Resumo:** Product ideation (Fase 1): refine raw ideas through structured drilling
- **Type:** Orchestrator
- **Timestamp:** 2026-06-12T02:23:22Z

Product ideation (Fase 1): refine raw ideas through structured drilling. Covers user research, competitor analysis, and producing a refined product concept ready for further pipeline stages.

**Relações:**
- `uses` → `research/user-interview`
- `parent` → `software-development/backlog-and-sprint`
- `similar` → `software-development/spike`
- `uses` → `research/deep-research`
- `uses` → `software-development/spike`

### Improve Codebase Architecture

- **Nome:** `software-development/improve-codebase-architecture`
- **Arquivo:** `software-development/improve-codebase-architecture/SKILL.md`
- **Tamanho:** 16,646 chars
- **Resumo:** Scan a codebase for deepening opportunities and present them as a structured report
- **Type:** Orchestrator
- **Timestamp:** 2026-06-28T05:11:55Z

Scan a codebase for deepening opportunities, present them as a structured report with prioritized recommendations for refactoring and improvement.

**Relações:**
- `similar` → `github/codebase-inspection`
- `similar` → `software-development/systematic-debugging`
- `uses` → `software-development/spike`
- `similar` → `software-development/test-driven-development`
- `used_by` → `software-development/plan`

### Plan Mode

- **Nome:** `software-development/plan`
- **Arquivo:** `software-development/plan/SKILL.md`
- **Tamanho:** 11,862 chars
- **Resumo:** Write actionable markdown plans to .hermes/plans — bite-sized tasks, exact paths
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code.

**Relações:**
- `uses` → `software-development/test-driven-development`
- `used_by` → `software-development/spike`
- `used_by` → `software-development/hermes-agent-skill-authoring`
- `used_by` → `software-development/systematic-debugging`
- `used_by` → `software-development/backlog-and-sprint`
- `similar` → `software-development/spike`
- `used_by` → `software-development/ideation-drilling`
- `used_by` → `software-development/improve-codebase-architecture`
- `used_by` → `software-development/process-augmentation-pipeline`

### Pipeline ID Consultoria — Process Augmentation

- **Nome:** `software-development/process-augmentation-pipeline`
- **Arquivo:** `software-development/process-augmentation-pipeline/SKILL.md`
- **Tamanho:** 51,393 chars
- **Resumo:** Pipeline ID Consultoria: análise de processos, brainstorming de soluções e site 3D
- **Type:** Orchestrator
- **Timestamp:** 2026-06-28T05:11:55Z

Load this skill when the user requests the ID Consultoria process augmentation pipeline — pain/opportunity/bottleneck mapping, causal loop diagrams, solution brainstorming, multi-criteria evaluation, and packaging into an interactive 3D site. Covers 4 pipeline stages with parallel subagent orchestration.

**Relações:**
- `uses` → `research/augmentation-process-design`
- `uses` → `creative/style-guide-consultation`
- `uses` → `software-development/agy`
- `uses` → `research/augmentacao-query`
- `uses` → `infrastructure/vercel-deploy`
- `uses` → `software-development/backlog-and-sprint`
- `uses` → `software-development/bpmn-diagram-renderer`
- `uses` → `software-development/threejs-rendering-debug`

### Simplify Code

- **Nome:** `software-development/simplify-code`
- **Arquivo:** `software-development/simplify-code/SKILL.md`
- **Tamanho:** 11,210 chars
- **Resumo:** Simplify recent code changes — 3 parallel agents review logic, formatting, and dead
- **Type:** Orchestrator
- **Timestamp:** 2026-06-28T05:11:55Z

Simplify recent code changes — 3 parallel agents review logic, formatting, and dead code independently.

Load this skill after making code changes that need cleanup. Three parallel agents review for logic issues, formatting problems, and dead code, then aggregate findings for selective application.

**Relações:**
- `similar` → `software-development/systematic-debugging`
- `similar` → `software-development/improve-codebase-architecture`
- `uses` → `software-development/test-driven-development`
- `similar` → `software-development/test-driven-development`

### Skills Repository Curator

- **Nome:** `software-development/skills-repo-curator`
- **Arquivo:** `software-development/skills-repo-curator/SKILL.md`
- **Tamanho:** 63,070 chars
- **Resumo:** Manage the Hermes skills repo — consolidation cycles, MECE analysis, offload, graph
- **Type:** Orchestrator
- **Timestamp:** 2026-06-28T05:11:55Z

Load this skill when the skills repo needs maintenance — evolve cycles, description audits, relation rebuilding, orphan review, or installing community skills. Covers the full consolidation lifecycle: update, evolve, offload, commit, push, and interactive D3 graph generation.

**Relações:**
- `uses` → `software-development/hermes-agent-skill-authoring`
- `uses` → `software-development/plan`
- `similar` → `software-development/backlog-and-sprint`
- `uses` → `infrastructure/data-pipeline-patterns`

### Educational Product Pipeline

- **Nome:** `software-development/pipeline-educacional`
- **Arquivo:** `software-development/pipeline-educacional/SKILL.md`
- **Tamanho:** 28,936 chars
- **Resumo:** Pipeline de produto educacional — da concepção pedagógica ao lançamento.
- **Type:** Orchestrator
- **Timestamp:** 2026-07-12T00:00:00Z

Carregue esta skill quando for projetar um curso, treinamento, bootcamp ou jornada de aprendizado. Cobre a pipeline completa do design instrucional: analise de publico, definicao de objetivos, design de conteudo, producao, lancamento e iteracao continua. Base de referencia em IA e design instrucional (ADDIE, Backward Design, SAM, Kirkpatrick).

**Relações:**
- `similar` → `autonomous-ai-agents/product-pipeline`
- `parent` → `education/backwards-design-unit-planner`
- `similar` → `education/scope-and-sequence-designer`
- `uses` → `creative/copywriting`
- `uses` → `software-development/ideation-drilling`

### Spike

- **Nome:** `software-development/spike`
- **Arquivo:** `software-development/spike/SKILL.md`
- **Tamanho:** 9,365 chars
- **Resumo:** Throwaway experiments to validate an idea before building — fast, focused
- **Type:** Research
- **Timestamp:** 2026-06-12T02:23:22Z

Throwaway experiments to validate an idea before building — fast, focused.

**Relações:**
- `uses` → `software-development/plan`
- `similar` → `software-development/plan`
- `similar` → `software-development/ideation-drilling`
- `uses` → `software-development/test-driven-development`
- `similar` → `research/model-benchmark-frontier`
- `used_by` → `software-development/improve-codebase-architecture`

### Inspecting Hermes Desktop DOM

- **Nome:** `software-development/inspecting-hermes-desktop-dom`
- **Arquivo:** `software-development/inspecting-hermes-desktop-dom/SKILL.md`
- **Tamanho:** 6,867 chars
- **Resumo:** Read the live Hermes desktop DOM/CSS over CDP.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-09T05:08:04Z

Load this skill when developing apps/desktop and you need to inspect the live rendered DOM of the running Hermes desktop app — computed styles, geometry, which CSS rule won, renderer console errors. Dev-server runs open a CDP port on 127.0.0.1:9222; scripts/eval.mjs and the shared CDP client in scripts/perf/lib/cdp.mjs read the Chromium page directly. Answers factual questions (did this render, which selector matches, inherited vs own styles) — not aesthetics. Includes isolated-instance launch pattern, stable data-slot selectors, and pitfalls (never kill the user's app, never dump the whole DOM).

**Relações:**
- `similar` → `software-development/systematic-debugging`
- `similar` → `dogfood`
- `similar` → `hermes-desktop-plugins`

### Systematic Debugging

- **Nome:** `software-development/systematic-debugging`
- **Arquivo:** `software-development/systematic-debugging/SKILL.md`
- **Tamanho:** 12,903 chars
- **Resumo:** 4-phase root cause debugging — methodology plus Python debugpy and Node.js inspect
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

4-phase root cause debugging — methodology + Python (pdb/debugpy) + Node.js (--inspect). Understand bugs before fixing.

**Relações:**
- `uses` → `software-development/test-driven-development`
- `uses` → `software-development/plan`
- `similar` → `software-development/spike`
- `parent` → `software-development/threejs-rendering-debug`

### Test-Driven Development (TDD)

- **Nome:** `software-development/test-driven-development`
- **Arquivo:** `software-development/test-driven-development/SKILL.md`
- **Tamanho:** 10,432 chars
- **Resumo:** Enforce RED-GREEN-REFACTOR cycle — tests before code, incremental development
- **Type:** Reference
- **Timestamp:** 2026-06-12T02:23:22Z

TDD: enforce RED-GREEN-REFACTOR, tests before code.

**Relações:**
- `uses` → `software-development/systematic-debugging`
- `used_by` → `software-development/plan`
- `used_by` → `software-development/systematic-debugging`
- `uses` → `software-development/spike`
- `used_by` → `software-development/backlog-and-sprint`
- `used_by` → `software-development/simplify-code`

### Three.js Rendering Debug

- **Nome:** `software-development/threejs-rendering-debug`
- **Arquivo:** `software-development/threejs-rendering-debug/SKILL.md`
- **Tamanho:** 5,232 chars
- **Resumo:** Debug invisible 3D WebGL/Three.js scenes — shaders, fog, visibility, and asset
- **Type:** Reference
- **Timestamp:** 2026-06-28T05:11:55Z

Load this skill when a Three.js scene is rendering (triangles > 0) but appears invisible. Provides a diagnostic protocol covering renderer setup, fog, lighting, material visibility, shader compilation, and asset loading verification.

**Relações:**
- `uses` → `software-development/agy`
- `similar` → `productivity/html-report-hermes`
- `uses` → `software-development/systematic-debugging`
- `used_by` → `software-development/process-augmentation-pipeline`

### TaskFlow UI Debugging

- **Nome:** `software-development/taskflow-ui-debugging`
- **Arquivo:** `software-development/taskflow-ui-debugging/SKILL.md`
- **Tamanho:** 2,211 chars
- **Resumo:** Debug TaskFlow UI when API returns data but frontend hides.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-02T00:00:00Z

Load this skill when diagnosing a TaskFlow frontend issue where the backend API returns correct data but the page doesn't render what is expected. Pipeline: verify DB data via psql, test the API directly with curl, verify the frontend build for expected strings, and check date/timezone handling (UTC vs BRT). Includes diagnostic queries and curl examples.

**Relações:**
- `similar` → `taskflow-mcp-rules`
- `uses` → `productivity/taskflow-mcp`
- `similar` → `software-development/systematic-debugging`

### Telegram Bot (Python)

- **Nome:** `software-development/telegram-bot-python`
- **Arquivo:** `software-development/telegram-bot-python/SKILL.md`
- **Tamanho:** 9,794 chars
- **Resumo:** Telegram bots: mock-first, MarkdownV2, python-telegram-bot.
- **Type:** ToolIntegration
- **Timestamp:** 2026-08-12T03:30:00Z

Telegram bots: mock-first, MarkdownV2, python-telegram-bot.

Load this skill when building or debugging a Telegram bot in Python — mock-first development, MarkdownV2 formatting rules, and python-telegram-bot patterns that avoid silent send failures.

**Relações:**
- `similar` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `infrastructure/whatsapp-baileys-integration`
- `uses` → `infrastructure/oracle-host-access`
