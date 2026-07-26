# Skills Index — Hermes Agent

*Total: 89 skills*

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
- **Tamanho:** 24,693 chars
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
- **Tamanho:** 15,494 chars
- **Resumo:** Systematic methodology for diagnosing Hermes Agent behavioral issues — session resets, context loss, compression failures
- **Type:** Research
- **Timestamp:** 2026-07-15T08:00:00Z

Load this skill when the user reports Hermes misbehaving: conversations resetting mid-turn, context being lost, sessions ending abruptly, repeated model fallbacks, or provider errors. Covers the full diagnostic pipeline: config analysis (compression, auxiliary models, session_reset settings), gateway log inspection (fallback patterns, compression events, error signatures), state.db SQLite analysis (session lifecycle, end_reasons, compression_failures, session_key chains), compressor source-code review, provider chain analysis, and causal-chain synthesis into a concrete remediation plan.

**Relações:**
- `similar` → `autonomous-ai-agents/hermes-agent`
### Product Development Pipeline

- **Nome:** `autonomous-ai-agents/product-pipeline`
- **Arquivo:** `autonomous-ai-agents/product-pipeline/SKILL.md`
- **Tamanho:** 81,763 chars
- **Resumo:** Multi-agent product pipeline — idea to MVP via sprints. Hermes orchestration
- **Type:** Orchestrator
- **Timestamp:** 2026-06-14T05:19:11Z

Multi-agent product pipeline from raw idea to MVP with iterative sprints. Orchestrated by Hermes, executed by Pi Agent + Antigravity.
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
- **Tamanho:** 43,906 chars
- **Resumo:** Umbrella skill for newsletters — cron scheduling, curation, dedup, deploy
- **Type:** Orchestrator
- **Timestamp:** 2026-06-19T19:47:50Z

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
- **Resumo:** Grafico de progresso de peso estilo Ares — matplotlib, vermelhos, claro.
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
- **Tamanho:** 6,648 chars
- **Resumo:** Reliability patterns for batch data pipelines — exponential backoff, API safeguards, cell-size truncation, and parallel execution guardrails
- **Type:** Reference
- **Timestamp:** 2026-06-28T05:11:55Z

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
- **Tamanho:** 3,591 chars
- **Resumo:** Hermes cron job patterns — timeout limits and background execution
- **Type:** Reference
- **Timestamp:** 2026-07-26T05:05:12Z

Load this skill when a cron job exceeds the 3-minute hard limit or needs to run long scripts. Covers the nohup background spawn pattern, script delivery, and timeout workarounds for the Hermes cron scheduler.

**Relações:**
- `similar` → `infrastructure/data-pipeline-patterns`

### Oracle VM — SSH Access from Hermes Container

- **Nome:** `infrastructure/oracle-host-access`
- **Arquivo:** `infrastructure/oracle-host-access/SKILL.md`
- **Tamanho:** 39,373 chars
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
- **Tamanho:** 10,286 chars
- **Resumo:** Post-CI deploy operations — Docker rollout, DB schema, ingress routing, DNS fallback.
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when deploying a built application to production: verifying DB migrations ran, diagnosing container startup failures, checking Nginx/NPM routing, or handling a domain that stopped resolving. Covers the gray zone between CI completing and the site being live — the step most pipelines leave unscripted.

**Relações:**
- `similar` → `infrastructure/deployment-pipeline`
- `similar` → `infrastructure/vercel-deploy`
- `uses` → `infrastructure/oracle-host-access`

### WhatsApp via Baileys — Python Integration

- **Nome:** `infrastructure/whatsapp-baileys-integration`
- **Arquivo:** `infrastructure/whatsapp-baileys-integration/SKILL.md`
- **Tamanho:** 20,615 chars
- **Resumo:** Integrate WhatsApp messaging into Python pipelines via Baileys — lifecycle, QR auth, REST bridge, multi-number
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-17T00:00:00Z

Load this skill when you need to send WhatsApp messages from Python without paid APIs. Covers full lifecycle management (spawn, QR auth, session persistence, health checks, graceful shutdown), REST bridge with Z-API compatible interface for file/media delivery, and multi-number architecture. Replaces paid Z-API with local WhatsApp Web.

**Relações:**
- `similar` → `messaging/whatsapp-automation`
- `similar` → `autonomous-ai-agents/messaging-platforms`

### Selfhost Service Deploy — Oracle ARM64

- **Nome:** `infrastructure/selfhost-service-deploy`
- **Arquivo:** `infrastructure/selfhost-service-deploy/SKILL.md`
- **Tamanho:** 12,856 chars
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
- **Tamanho:** 7,658 chars
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
- **Tamanho:** 58,440 chars
- **Resumo:** Prepare and transfer manga to Kindle — quality-gated conversion with resolution check, contrast correction, and grayscale EPUB generation
- **Type:** Media
- **Timestamp:** 2026-06-28T05:11:55Z

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
- **Tamanho:** 21,380 chars
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
- **Tamanho:** 15,328 chars
- **Resumo:** Render research reports as dark-themed HTML with SVG charts and Tufte typography
- **Type:** Template
- **Timestamp:** 2026-06-12T02:23:22Z

Render research reports as dark-themed HTML with SVG charts and Tufte-inspired typography.

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `productivity/html-to-pdf-chromium`
- `used_by` → `productivity/relatorio-de-custos`
- `used_by` → `productivity/html-to-pdf-chromium`

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
- **Tamanho:** 9,294 chars
- **Resumo:** GTD task management via MCP (Model Context Protocol) — connects over SSE
- **Type:** ToolIntegration
- **Timestamp:** 2026-06-14T05:15:09Z

TaskFlow é um sistema GTD de gerenciamento de tarefas exposto via MCP (Model Context Protocol). Conecta-se via SSE.

**Relações:**
- `similar` → `productivity/notion`
- `similar` → `software-development/backlog-and-sprint`
- `used_by` → `autonomous-ai-agents/hermes-agent`

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

## Messaging

### WhatsApp Automation (Baileys)

- **Nome:** `messaging/whatsapp-automation`
- **Arquivo:** `messaging/whatsapp-automation/SKILL.md`
- **Tamanho:** 5,717 chars
- **Resumo:** Automate WhatsApp messaging from Python projects — Baileys bridge, Z-API migration, multi-assessor patterns
- **Type:** ToolIntegration
- **Timestamp:** 2026-07-16T00:00:00Z

Load this skill when your Python project needs to send WhatsApp messages (text, PDFs, documents) without paying for third-party APIs. Covers Baileys Node.js bridge setup, Z-API compatible REST interface, QR authentication workflow, and multi-number multi-assessor patterns.

**Relações:**
- `similar` → `infrastructure/whatsapp-baileys-integration`


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
- **Tamanho:** 9,025 chars
- **Resumo:** Produce market analysis reports — personas, journeys, expectations, behavior.
- **Type:** Research
- **Timestamp:** 2026-07-12T00:00:00Z

Load this skill when conducting market research for Brazilian/LATAM markets where web research tools face comprehensive blocking. Produces structured reports covering buyer personas, customer journeys, expectations hierarchies, purchasing behavior, and retention/fidelization. Pivots to domain-knowledge synthesis with transparent caveats when web tools fail.

**Relações:**
- `similar` → `research/deep-research`
- `similar` → `research/user-interview`
- `similar` → `software-development/ideation-drilling`

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
- **Tamanho:** 3,945 chars
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
- **Tamanho:** 27,267 chars
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
- **Tamanho:** 10,968 chars
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
- **Tamanho:** 12,297 chars
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
- **Tamanho:** 50,454 chars
- **Resumo:** Manage the Hermes skills repo — consolidation cycles, MECE analysis, offload, graph
- **Type:** Orchestrator
- **Timestamp:** 2026-06-28T05:11:55Z

Manage the Hermes skills repo — consolidation cycles, MECE analysis, offload, graph generation.

**Relações:**
- `uses` → `software-development/hermes-agent-skill-authoring`
- `uses` → `software-development/plan`
- `similar` → `software-development/backlog-and-sprint`
- `uses` → `infrastructure/data-pipeline-patterns`

### Educational Product Pipeline

- **Nome:** `software-development/pipeline-educacional`
- **Arquivo:** `software-development/pipeline-educacional/SKILL.md`
- **Tamanho:** 28,936 chars
- **Resumo:** Pipeline de produto educacional — da concepcao pedagogica ao lancamento.
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
