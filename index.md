# Skills Index — Hermes Agent

*Total: 83 skills*

---


## Apple

### Apple Notes

- **Nome:** `apple/apple-notes`
- **Arquivo:** `apple/apple-notes/SKILL.md`
- **Tamanho:** 2,169 chars
- **Resumo:** Manage Apple Notes via the memo CLI — create, search, and edit notes from the terminal.

Manage Apple Notes via the memo CLI — create, search, and edit notes from the terminal. Load this skill to interact with Apple Notes programmatically on macOS. Covers creating new notes with formatted content, searching through existing notes by keyword, editing note content, and organizing notes into folders.

**Relações:**
- `similar` → `apple/apple-reminders`
- `similar` → `apple/imessage`
- `similar` → `apple/findmy`

### Apple Reminders

- **Nome:** `apple/apple-reminders`
- **Arquivo:** `apple/apple-reminders/SKILL.md`
- **Tamanho:** 3,606 chars
- **Resumo:** Apple Reminders via remindctl — add, list, and complete tasks from the command line.

Apple Reminders via remindctl — add, list, and complete tasks from the command line. Load this skill to manage Apple Reminders programmatically from macOS terminal. Covers adding new reminders with due dates and notes, listing pending and completed reminders, marking tasks as complete, and searching through existing reminders.

**Relações:**
- `similar` → `apple/apple-notes`
- `similar` → `apple/imessage`
- `uses` → `autonomous-ai-agents/product-pipeline`

### Find My (Apple)

- **Nome:** `apple/findmy`
- **Arquivo:** `apple/findmy/SKILL.md`
- **Tamanho:** 3,709 chars
- **Resumo:** Track Apple devices and AirTags via the FindMy app on macOS.

Track Apple devices and AirTags via the FindMy app on macOS. Load this skill when you need to locate lost devices, check AirTag positions, or monitor location of Apple devices. Uses the FindMy.app infrastructure on macOS to query device locations and display them on a map.

**Relações:**
- `similar` → `apple/imessage`
- `similar` → `apple/macos-computer-use`
- `similar` → `apple/apple-notes`
- `similar` → `productivity/maps`

- `uses` → `autonomous-ai-agents/hermes-agent`
### iMessage

- **Nome:** `apple/imessage`
- **Arquivo:** `apple/imessage/SKILL.md`
- **Tamanho:** 2,442 chars
- **Resumo:** Send and receive iMessages and SMS via the imsg CLI on macOS.

Send and receive iMessages and SMS via the imsg CLI on macOS. Load this skill for Apple iMessage automation from the terminal. Covers sending iMessages to individual contacts and group chats, reading received messages, checking delivery status, and managing conversations through the imsg CLI tool on macOS.

**Relações:**
- `similar` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `apple/apple-notes`
- `similar` → `apple/apple-reminders`

- `uses` → `apple/macos-computer-use`
### macOS Computer Use (universal, any-model)

- **Nome:** `apple/macos-computer-use`
- **Arquivo:** `apple/macos-computer-use/SKILL.md`
- **Tamanho:** 7,309 chars
- **Resumo:** Drive macOS desktop in background — screenshots, mouse, keyboard, scroll, drag — without stealing cursor focus.

Drive macOS desktop in background — screenshots, mouse, keyboard, scroll, drag — without stealing cursor focus. Load this skill when the computer_use tool is available and you need to automate macOS GUI interactions. Works with any tool-capable model. Covers background desktop automation (screenshots, mouse clicks and drag, keyboard input, scrolling) without stealing cursor focus or switching Spaces. Includes canonical workflows for app launching, web browsing, and file management.

**Relações:**
- `uses` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `apple/findmy`
- `similar` → `creative/excalidraw`
- `similar` → `creative/claude-design`

- `similar` → `autonomous-ai-agents/hermes-agent`
- `used_by` → `apple/findmy`
- `used_by` → `apple/imessage`

## Autonomous Ai Agents

### Autonomous AI Coding Agents

- **Nome:** `autonomous-ai-agents/autonomous-ai-agents`
- **Arquivo:** `autonomous-ai-agents/autonomous-ai-agents/SKILL.md`
- **Tamanho:** 3,200 chars
- **Resumo:** Delegate coding tasks to autonomous AI coding agent CLIs (Claude Code, Codex, OpenCode)...

Delegate tasks to autonomous AI coding agent CLIs via Hermes. One-shot, PR review, and session orchestration patterns.

**Relações:**
- `similar` → `autonomous-ai-agents/pi-agent-coordination`
- `similar` → `autonomous-ai-agents/hermes-agent`
- `parent` → `autonomous-ai-agents/product-pipeline`
- `similar` → `autonomous-ai-agents/messaging-platforms`

- `similar` → `autonomous-ai-agents/product-pipeline`
- `uses` → `autonomous-ai-agents/hermes-agent`
### Hermes Agent

- **Nome:** `autonomous-ai-agents/hermes-agent`
- **Arquivo:** `autonomous-ai-agents/hermes-agent/SKILL.md`
- **Tamanho:** 46,692 chars
- **Resumo:** Configure, extend, or contribute to Hermes Agent — setup, profiles, skills, and multi-agent orchestration.

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

- `parent` → `apple/macos-computer-use`
- `uses` → `autonomous-ai-agents/autonomous-ai-agents`
### Messaging Platforms

- **Nome:** `autonomous-ai-agents/messaging-platforms`
- **Arquivo:** `autonomous-ai-agents/messaging-platforms/SKILL.md`
- **Tamanho:** 15,243 chars
- **Resumo:** Reference for Hermes cross-platform messaging — platform quirks, ID formats, and bridge workarounds.

Load this skill when troubleshooting message delivery across platforms. Covers Telegram MEDIA file delivery rules, WhatsApp JID/group ID formats, bridge processes for WhatsApp and Telegram, known file-type limitations, and platform-specific workarounds for reliable cross-platform messaging.

**Relações:**
- `similar` → `apple/imessage`
- `used_by` → `apple/macos-computer-use`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `parent` → `autonomous-ai-agents/hermes-agent`
- `parent` → `messaging-platforms/whatsapp-bridge-baileys`

- `used_by` → `apple/imessage`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `content-production/text-to-speech`
### Pi Agent (Local)
- **Nome:** `autonomous-ai-agents/pi-agent-coordination`
- **Arquivo:** `autonomous-ai-agents/pi-agent-coordination/SKILL.md`
- **Tamanho:** 26,843 chars
- **Resumo:** Invoke Pi Agent locally from Hermes with provider/model hierarchy, session recovery, and stall detection.

Invoke Pi Agent locally from Hermes: provider/model hierarchy, session recovery, stall detection, fallback patterns.

Load this skill for running Pi Coder Agent (v0.78.1) as a local npm binary — no Docker, no SSH. Covers the three-tier hierarchy (agy for strategy, Pi best via MiniMax M3 for planning, Pi cost via DeepSeek V4 Flash for code tasks), provider/model selection with fallback chains, session recovery from interrupted runs, stall detection and diagnosis, parallel execution patterns, and tmux-based monitoring. Includes GoUsageLimitError handling and pre-launch session reuse checks.

**Relações:**
- `uses` → `autonomous-ai-agents/pi-session-audit`

**Relações:**
- `similar` → `autonomous-ai-agents/autonomous-ai-agents`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `parent` → `autonomous-ai-agents/hermes-agent`

- `uses` → `autonomous-ai-agents/hermes-agent`
### Product Development Pipeline

- **Nome:** `autonomous-ai-agents/product-pipeline`
- **Arquivo:** `autonomous-ai-agents/product-pipeline/SKILL.md`
- **Tamanho:** 80,167 chars
- **Resumo:** Multi-agent product pipeline from raw idea to MVP with iterative sprints — orchestrated by Hermes, executed by Pi Agent + Antigravity.

Multi-agent product pipeline from raw idea to MVP with iterative sprints. Orchestrated by Hermes, executed by Pi Agent + Antigravity.

Load this skill when building a product from scratch through the full pipeline — ideation, research, design, sprints, and delivery. Covers orchestrating a multi-agent team with Hermes as coordinator, Pi Agent for execution, and Antigravity for visual design review.

**Relações:**
- `uses` → `autonomous-ai-agents/pi-agent-coordination`
- `uses` → `autonomous-ai-agents/autonomous-ai-agents`
- `uses` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `content-production/iaf-newsletter-pipeline`
- `uses` → `creative/copywriting`
- `uses` → `creative/humanizer`

- `uses` → `content-production/text-to-speech`
- `uses` → `creative/brand-studio-forge`

## Content Production

### IAF Newsletter Pipeline — Manhã Aumentada

- **Nome:** `content-production/iaf-newsletter-pipeline`
- **Arquivo:** `content-production/iaf-newsletter-pipeline/SKILL.md`
- **Tamanho:** 12,391 chars
- **Resumo:** Umbrella skill for newsletter, briefing, and digest pipelines with cron scheduling and multi-source curation.

Load this skill to set up, modify, run, or troubleshoot any daily newsletter, briefing, digest, or curated report pipeline — IAF Manhã Aumentada, Daily AI Digest, or similar. Covers multi-source content collection, editorial ranking and dedup, HTML-to-PDF rendering, Telegram and WhatsApp delivery, and chained cron job architecture.

**Relações:**
- `uses` → `creative/copywriting`
- `uses` → `creative/humanizer`
- `similar` → `autonomous-ai-agents/product-pipeline`
- `similar` → `creative/style-guide-consultation`
- `uses` → `creative/text-to-speech`
- `uses` → `social-media/brand-iaf-conteudo`

- `uses` → `autonomous-ai-agents/hermes-agent`
- `uses` → `content-production/text-to-speech`
### Text-to-Speech (TTS)

- **Nome:** `content-production/text-to-speech`
- **Arquivo:** `content-production/text-to-speech/SKILL.md`
- **Tamanho:** 7,413 chars
- **Resumo:** Umbrella skill for TTS covering voice design, multi-provider fallback, and full lifecycle from persona to audio.

Umbrella skill for TTS: voice design, Gemini prompting, multi-provider fallback, self-hosted Fish Speech, and Hermes TTS provider. Full lifecycle from persona to audio.

**Relações:**
- `parent` → `autonomous-ai-agents/hermes-agent`
- `similar` → `creative/songwriting-and-ai-music`
- `similar` → `creative/ascii-video`
- `similar` → `creative/manim-video`
- `uses` → `creative/humanizer`

- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `creative/ascii-video`
- `used_by` → `creative/manim-video`
- `uses` → `autonomous-ai-agents/messaging-platforms`

## Creative

### Architecture Diagram Skill

- **Nome:** `creative/architecture-diagram`
- **Arquivo:** `creative/architecture-diagram/SKILL.md`
- **Tamanho:** 5,830 chars
- **Resumo:** Dark-themed SVG architecture, cloud, and infrastructure diagrams as standalone HTML.

Dark-themed SVG architecture, cloud, and infrastructure diagrams as standalone HTML. Load this skill when you need to create architecture diagrams for presentations or documentation. Covers drawing cloud infrastructure topologies, system architecture diagrams, network flows, and component relationships using SVG rendered as dark-themed HTML pages.

**Relações:**
- `similar` → `creative/excalidraw`
- `similar` → `creative/claude-design`
- `similar` → `creative/brand-studio-forge`
- `similar` → `creative/baoyu-infographic`
- `similar` → `creative/pretext`

- `similar` → `creative/popular-web-designs`
- `used_by` → `creative/manim-video`
### ASCII Art Skill

- **Nome:** `creative/ascii-art`
- **Arquivo:** `creative/ascii-art/SKILL.md`
- **Tamanho:** 10,556 chars
- **Resumo:** ASCII art generation — pyfiglet, cowsay, boxes, and image-to-ascii conversion.

ASCII art: pyfiglet, cowsay, boxes, image-to-ascii.

**Relações:**
- `similar` → `creative/ascii-video`
- `similar` → `creative/pretext`
- `similar` → `creative/p5js`
- `similar` → `creative/manim-video`

- `used_by` → `creative/ascii-video`
- `used_by` → `creative/pretext`
### ASCII Video Production Pipeline

- **Nome:** `creative/ascii-video`
- **Arquivo:** `creative/ascii-video/SKILL.md`
- **Tamanho:** 14,864 chars
- **Resumo:** Convert video and audio into colored ASCII art MP4 or GIF animations.

ASCII video: convert video/audio to colored ASCII MP4/GIF.

**Relações:**
- `uses` → `creative/ascii-art`
- `similar` → `creative/p5js`
- `similar` → `creative/manim-video`
- `uses` → `creative/text-to-speech`
- `similar` → `creative/pretext`

- `similar` → `creative/ascii-art`
- `uses` → `content-production/text-to-speech`
### Infographic Generator

- **Nome:** `creative/baoyu-infographic`
- **Arquivo:** `creative/baoyu-infographic/SKILL.md`
- **Tamanho:** 10,434 chars
- **Resumo:** Create infographics with 21 layout templates and 21 visual styles for data storytelling.

Infographics: 21 layouts x 21 styles (信息图, 可视化).

**Relações:**
- `similar` → `creative/architecture-diagram`
- `similar` → `creative/brand-studio-forge`
- `similar` → `creative/excalidraw`
- `similar` → `creative/claude-design`
- `similar` → `creative/comfyui`

- `similar` → `creative/p5js`
- `similar` → `creative/popular-web-designs (Infographic templates (21 layouts × 21 styles) share the concept of pre-built design systems with the 54-web-design catalog)`
- `uses` → `creative/brand-studio-forge (Brand visual identity (colors, typography, voice) constrains infographic style choices)`
### brand-studio-forge

- **Nome:** `creative/brand-studio-forge`
- **Arquivo:** `creative/brand-studio-forge/SKILL.md`
- **Tamanho:** 20,607 chars
- **Resumo:** Use when the user wants to create, refine, or evolve a brand identity

Use when the user wants to create, refine, or evolve a brand identity. Covers brand interviews, identity kit generation (logo, color, type, voice, guidelines), brand-specific content skills, and ongoing content via cron. Not for UI design or non-brand creative tasks.

**Relações:**
- `uses` → `creative/claude-design`
- `uses` → `creative/popular-web-designs`
- `uses` → `creative/style-guide-consultation`
- `similar` → `creative/claude-design`
- `similar` → `creative/style-guide-consultation`
- `similar` → `creative/baoyu-infographic`
- `uses` → `creative/copywriting`

- `used_by` → `autonomous-ai-agents/product-pipeline`
- `uses` → `creative/humanizer`
### Claude Design for CLI/API Agents

- **Nome:** `creative/claude-design`
- **Arquivo:** `creative/claude-design/SKILL.md`
- **Tamanho:** 21,156 chars
- **Resumo:** Design one-off HTML artifacts (landing, deck, prototype)

Design one-off HTML artifacts (landing, deck, prototype). Includes Sketch Mode for throwaway variant comparison.

**Relações:**
- `uses` → `creative/popular-web-designs`
- `similar` → `creative/architecture-diagram`
- `similar` → `creative/excalidraw`
- `similar` → `creative/brand-studio-forge`
- `similar` → `creative/style-guide-consultation`
- `similar` → `creative/pretext`
- `similar` → `creative/p5js`

### ComfyUI

- **Nome:** `creative/comfyui`
- **Arquivo:** `creative/comfyui/SKILL.md`
- **Tamanho:** 24,287 chars
- **Resumo:** Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, ...

Generate images, video, and audio with ComfyUI. Install, manage nodes/models, run workflows via comfy-cli and direct REST/WebSocket API.

**Relações:**
- `similar` → `creative/baoyu-infographic`
- `similar` → `creative/ascii-video`
- `similar` → `creative/p5js`

- `similar` → `creative/brand-studio-forge`
### Copywriting

- **Nome:** `creative/copywriting`
- **Arquivo:** `creative/copywriting/SKILL.md`
- **Tamanho:** 7,429 chars
- **Resumo:** Expert conversion copywriting to write, rewrite, or improve marketing copy.

Expert conversion copywriting: write, rewrite, or improve marketing copy — headlines, CTAs, value props, page sections.

Load this skill when the user needs marketing copy — landing pages, homepage sections, pricing copy, CTAs, taglines, or value propositions. Provides a complete framework for gathering context, applying copywriting principles (clarity over cleverness, benefits over features, specificity over vagueness), and producing organized output with annotations and alternatives. Covers page structure frameworks, voice and tone guidance, CTA copy guidelines, and page-specific strategies for homepages, landing pages, pricing pages, feature pages, and about pages. Pair with the humanizer skill for thorough line-by-line editing after drafting.

**Relações:**
- `similar` → `creative/humanizer`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `creative/brand-studio-forge`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `similar` → `social-media/brand-iaf-conteudo`

- `similar` → `creative/songwriting-and-ai-music`
### Excalidraw Diagram Skill

- **Nome:** `creative/excalidraw`
- **Arquivo:** `creative/excalidraw/SKILL.md`
- **Tamanho:** 7,300 chars
- **Resumo:** Hand-drawn Excalidraw JSON diagrams — architecture, flowcharts, and sequence diagrams.

Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).

**Relações:**
- `similar` → `creative/architecture-diagram`
- `similar` → `creative/claude-design`
- `similar` → `creative/baoyu-infographic`
- `similar` → `creative/pretext`
- `similar` → `creative/p5js`
- `similar` → `creative/brand-studio-forge`

### Humanizer: Remove AI Writing Patterns

- **Nome:** `creative/humanizer`
- **Arquivo:** `creative/humanizer/SKILL.md`
- **Tamanho:** 30,025 chars
- **Resumo:** Humanize text by stripping AI-isms and adding authentic voice and personality.

Humanize text: strip AI-isms and add real voice.

**Relações:**
- `similar` → `creative/copywriting`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `used_by` → `creative/brand-studio-forge`
- `used_by` → `creative/copywriting`

### Manim Video Production Pipeline

- **Nome:** `creative/manim-video`
- **Arquivo:** `creative/manim-video/SKILL.md`
- **Tamanho:** 12,023 chars
- **Resumo:** Manim CE animations — 3Blue1Brown-style math and algorithm explainer videos.

Manim CE animations: 3Blue1Brown math/algo videos.

**Relações:**
- `similar` → `creative/p5js`
- `similar` → `creative/ascii-video`
- `uses` → `creative/text-to-speech`
- `similar` → `creative/ascii-art`
- `similar` → `creative/pretext`

- `similar` → `creative/architecture-diagram`
- `uses` → `content-production/text-to-speech`
### p5.js Production Pipeline

- **Nome:** `creative/p5js`
- **Arquivo:** `creative/p5js/SKILL.md`
- **Tamanho:** 27,494 chars
- **Resumo:** p5.js sketches — generative art, shaders, interactive animations, and 3D graphics.

p5.js sketches: gen art, shaders, interactive, 3D.

**Relações:**
- `similar` → `creative/ascii-video`
- `similar` → `creative/manim-video`
- `similar` → `creative/excalidraw`
- `similar` → `creative/pretext`
- `similar` → `creative/claude-design`
- `similar` → `creative/brand-studio-forge`
- `similar` → `creative/comfyui`

- `similar` → `creative/baoyu-infographic`
### Popular Web Designs

- **Nome:** `creative/popular-web-designs`
- **Arquivo:** `creative/popular-web-designs/SKILL.md`
- **Tamanho:** 9,722 chars
- **Resumo:** 54 real-world design systems from Stripe, Linear, Vercel and more — rendered as HTML and CSS.

54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.

**Relações:**
- `uses` → `creative/claude-design`
- `used_by` → `creative/brand-studio-forge`
- `similar` → `creative/style-guide-consultation`
- `similar` → `creative/claude-design`

- `similar` → `creative/architecture-diagram`
- `similar` → `creative/baoyu-infographic`
- `used_by` → `creative/claude-design`
### Pretext Creative Demos

- **Nome:** `creative/pretext`
- **Arquivo:** `creative/pretext/SKILL.md`
- **Tamanho:** 14,168 chars
- **Resumo:** Creative browser demos with @chenglou/pretext for DOM-free text layout, ASCII art, and kinetic typography.

Creative browser demos with @chenglou/pretext: DOM-free text layout for ASCII art, kinetic typography, text-as-geometry games, and generative art. Single-file HTML output.

**Relações:**
- `similar` → `creative/p5js`
- `similar` → `creative/claude-design`
- `similar` → `creative/excalidraw`
- `similar` → `creative/architecture-diagram`
- `similar` → `creative/ascii-art`
- `similar` → `creative/ascii-video`
- `similar` → `creative/manim-video`

### Songwriting & AI Music Generation

- **Nome:** `creative/songwriting-and-ai-music`
- **Arquivo:** `creative/songwriting-and-ai-music/SKILL.md`
- **Tamanho:** 10,206 chars
- **Resumo:** Songwriting craft and Suno AI music prompt engineering for AI-generated songs.

Songwriting craft and Suno AI music prompts.

**Relações:**
- `similar` → `creative/text-to-speech`
- `similar` → `creative/copywriting`
- `similar` → `creative/humanizer`
- `similar` → `creative/brand-studio-forge`

- `similar` → `content-production/iaf-newsletter-pipeline`
- `similar` → `creative/ascii-video`
- `uses` → `content-production/text-to-speech`
### Style Guide Consultation

- **Nome:** `creative/style-guide-consultation`
- **Arquivo:** `creative/style-guide-consultation/SKILL.md`
- **Tamanho:** 5,729 chars
- **Resumo:** Catálogo e consulta de guias de estilo — carrega o design system correto para qualquer tarefa visual.

Catálogo e consulta de guias de estilo — carrega o design system correto para qualquer tarefa visual.

Load this skill when you need to apply a brand or design system to any visual task. Covers loading the correct style guide (Hermes Agent, ID Consultoria, IAF Comunidade, IAF Newsletter) for visual output, ensuring brand-consistent HTML, diagrams, and presentations.

**Relações:**
- `uses` → `creative/brand-studio-forge`
- `similar` → `creative/popular-web-designs`
- `similar` → `creative/claude-design`
- `similar` → `creative/brand-studio-forge`


## Data Science

### Jupyter Live Kernel (hamelnb)

- **Nome:** `data-science/jupyter-live-kernel`
- **Arquivo:** `data-science/jupyter-live-kernel/SKILL.md`
- **Tamanho:** 5,285 chars
- **Resumo:** Iterative Python development via live Jupyter kernel using hamelnb.

Iterative Python via live Jupyter kernel (hamelnb).

**Relações:**
- `similar` → `software-development/spike`
- `similar` → `mlops/evaluation/weights-and-biases`
- `similar` → `mlops/huggingface-hub`

## Email

### Himalaya Email CLI

- **Nome:** `email/himalaya`
- **Arquivo:** `email/himalaya/SKILL.md`
- **Tamanho:** 7,164 chars
- **Resumo:** Himalaya CLI — IMAP/SMTP email management directly from the terminal.

Himalaya CLI: IMAP/SMTP email from terminal.

**Relações:**
- `similar` → `productivity/google-workspace`

- `similar` → `messaging-platforms/whatsapp-bridge-baileys`
- `similar` → `productivity/html-report-hermes`
## Github

### Codebase Inspection & Architecture Diagnostic

- **Nome:** `github/codebase-inspection`
- **Arquivo:** `github/codebase-inspection/SKILL.md`
- **Tamanho:** 9,747 chars
- **Resumo:** Multi-layered codebase diagnostics — structural mapping, dependency audit, git history, metrics, and health reports.

Multi-layered codebase diagnostics: structural mapping, dependency audit, git history, metrics, and health reports.

**Relações:**
- `similar` → `github/github-code-review`
- `uses` → `github/github-repo-management`
- `similar` → `dogfood/dogfood`

- `similar` → `software-development/systematic-debugging`
### GitHub Authentication Setup

- **Nome:** `github/github-auth`
- **Arquivo:** `github/github-auth/SKILL.md`
- **Tamanho:** 10,190 chars
- **Resumo:** GitHub authentication setup — HTTPS tokens, SSH keys, and gh CLI login.

GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login.

**Relações:**
- `used_by` → `github/github-code-review`
- `used_by` → `github/github-issues`
- `used_by` → `github/github-pr-workflow`
- `used_by` → `github/github-repo-management`
- `used_by` → `infrastructure/deployment-pipeline`

### GitHub Code Review

- **Nome:** `github/github-code-review`
- **Arquivo:** `github/github-code-review/SKILL.md`
- **Tamanho:** 13,565 chars
- **Resumo:** Review GitHub pull requests — diffs, inline comments via gh CLI or REST API.

Review PRs: diffs, inline comments via gh or REST.

**Relações:**
- `uses` → `github/github-auth`
- `used_by` → `github/github-pr-workflow`
- `similar` → `github/codebase-inspection`

- `similar` → `software-development/systematic-debugging`
### GitHub Issues Management

- **Nome:** `github/github-issues`
- **Arquivo:** `github/github-issues/SKILL.md`
- **Tamanho:** 9,265 chars
- **Resumo:** Create, triage, label, and assign GitHub issues via gh CLI or REST API.

Create, triage, label, assign GitHub issues via gh or REST.

**Relações:**
- `uses` → `github/github-auth`
- `used_by` → `github/github-pr-workflow`
- `similar` → `github/github-repo-management`

### GitHub Pull Request Workflow

- **Nome:** `github/github-pr-workflow`
- **Arquivo:** `github/github-pr-workflow/SKILL.md`
- **Tamanho:** 26,249 chars
- **Resumo:** GitHub PR lifecycle — branch, commit, open PR, CI checks, and merge.

GitHub PR lifecycle: branch, commit, open, CI, merge.

**Relações:**
- `uses` → `github/github-auth`
- `uses` → `github/github-code-review`
- `uses` → `infrastructure/deployment-pipeline`
- `uses` → `infrastructure/oracle-host-access`
- `similar` → `github/github-repo-management`

### GitHub Repository Management

- **Nome:** `github/github-repo-management`
- **Arquivo:** `github/github-repo-management/SKILL.md`
- **Tamanho:** 16,758 chars
- **Resumo:** Clone, create, and fork repos — manage remotes, releases, and repository settings.

Clone/create/fork repos; manage remotes, releases.

**Relações:**
- `uses` → `github/github-auth`
- `similar` → `github/github-pr-workflow`
- `similar` → `github/github-issues`
- `used_by` → `github/codebase-inspection`


## Infrastructure

### AI Voice Selfhost — TTS no Oracle ARM64

- **Nome:** `infrastructure/ai-voice-selfhost`
- **Arquivo:** `infrastructure/ai-voice-selfhost/SKILL.md`
- **Tamanho:** 30,160 chars
- **Resumo:** Self-host AI voice/TTS models (OmniVoice, Qwen3-TTS, Fish Speech S2 Pro GGUF) on Oracle...

Self-host TTS models (OmniVoice, Qwen3-TTS, Fish Speech) on Oracle ARM64 with Docker. Python and C++ inference patterns, OpenAI-compatible endpoints, Hermes TTS provider integration.

**Relações:**
- `uses` → `infrastructure/oracle-host-access`
- `uses` → `mlops/huggingface-hub`
- `similar` → `mlops/inference/llama-cpp`

- `similar` → `infrastructure/deployment-pipeline`
- `uses` → `mlops/inference/vllm`
### Deployment Pipeline — Docker + GitHub Actions + SSH Deploy

- **Nome:** `infrastructure/deployment-pipeline`
- **Arquivo:** `infrastructure/deployment-pipeline/SKILL.md`
- **Tamanho:** 45,584 chars
- **Resumo:** CI/CD pipeline for Docker-based apps — GitHub Actions, ghcr.io registry, and SSH deploy to bare metal.

CI/CD pipeline for Docker-based apps: GitHub Actions → ghcr.io → SSH deploy to bare metal. Covers workflow design, registry auth, tag strategy, deploy key setup, migration management, and common pitfalls.

**Relações:**
- `uses` → `github/github-auth`
- `uses` → `infrastructure/oracle-host-access`
- `used_by` → `github/github-pr-workflow`
- `similar` → `infrastructure/vercel-deploy`

- `similar` → `infrastructure/ai-voice-selfhost`
### Oracle VM — SSH Access from Hermes Container

- **Nome:** `infrastructure/oracle-host-access`
- **Arquivo:** `infrastructure/oracle-host-access/SKILL.md`
- **Tamanho:** 35,840 chars
- **Resumo:** SSH access from a Hermes Docker container to its Oracle Linux host

SSH access from a Hermes Docker container to its Oracle Linux host. Covers key setup, SSH config quirks, Docker host discovery, and host diagnostics.

**Relações:**
- `used_by` → `infrastructure/deployment-pipeline`
- `used_by` → `infrastructure/ai-voice-selfhost`
- `used_by` → `github/github-pr-workflow`

### Vercel Deploy — Skill

- **Nome:** `infrastructure/vercel-deploy`
- **Arquivo:** `infrastructure/vercel-deploy/SKILL.md`
- **Tamanho:** 19,814 chars
- **Resumo:** Deploy static sites and frontend apps to Vercel — from zero to production

Deploy static sites and frontend apps to Vercel — from zero to production. Covers CLI install, device-flow authentication, project creation, deploy, custom domains, env vars, and common pitfalls. Works in restricted environments (no root, npm global install with custom prefix).

**Relações:**
- `similar` → `infrastructure/deployment-pipeline`

- `similar` → `github/github-pr-workflow`
- `uses` → `github/github-repo-management` (reason: Vercel projects link to GitHub repositories; repo management (clone, push, create) is the upstream step before Vercel deployment.)`
- `uses` → `productivity/html-report-hermes`

## Media

### HyperFrames Video Production

- **Nome:** `media/hyperframes-video-production`
- **Arquivo:** `media/hyperframes-video-production/SKILL.md`
- **Tamanho:** 22,156 chars
- **Resumo:** Produce deterministic MP4 videos using HyperFrames (HTML→video engine).

Produce deterministic MP4 videos using HyperFrames (HTML→video engine). Generates HTML compositions with GSAP animations, renders locally via npx hyperframes. Hermes Style Guide is the default visual aesthetic for explainer/demo videos.

**Relações:**
- `similar` → `media/youtube-content`
- `uses` → `creative/brand-studio-forge`
- `uses` → `creative/style-guide-consultation`
- `similar` → `creative/manim-video`
- `similar` → `creative/comfyui`

- `uses` → `infrastructure/oracle-host-access`
### YouTube Content Tool

- **Nome:** `media/youtube-content`
- **Arquivo:** `media/youtube-content/SKILL.md`
- **Tamanho:** 3,218 chars
- **Resumo:** Convert YouTube transcripts into summaries, Twitter threads, and blog posts.

YouTube transcripts to summaries, threads, blogs.

**Relações:**
- `similar` → `media/hyperframes-video-production`
- `uses` → `research/llm-wiki`

- `similar` → `content-production/iaf-newsletter-pipeline` (reason: Both pipelines transform source content (YouTube videos or multi-source curation) into structured written outputs (summaries, newsletters, threads) for distribution.)`
- `uses` → `creative/copywriting`

## Messaging Platforms

### WhatsApp Bridge (Baileys)

- **Nome:** `messaging-platforms/whatsapp-bridge-baileys`
- **Arquivo:** `messaging-platforms/whatsapp-bridge-baileys/SKILL.md`
- **Tamanho:** 5,281 chars
- **Resumo:** Send messages, discover group IDs, and manage media via a local WhatsApp Baileys bridge.

Send messages, discover group IDs, and manage media via local WhatsApp Baileys bridge.

Load this skill when you need to interact with WhatsApp programmatically. Covers the local Node.js HTTP bridge on port 3000 using @whiskeysockets/baileys — sending text and media messages, editing sent messages, discovering group IDs from sender-key files, self-chat mode behavior, and common pitfalls including silent delivery failures and emoji issues. Always verify group names before sending to avoid wrong-group-ID errors.

**Relações:**
- `similar` → `autonomous-ai-agents/messaging-platforms`
- `similar` → `email/himalaya`
- `similar` → `productivity/html-report-hermes`

- `similar` → `apple/imessage`
- `used_by` → `content-production/iaf-newsletter-pipeline`
## Mlops

### lm-evaluation-harness - LLM Benchmarking

- **Nome:** `mlops/evaluation/lm-evaluation-harness`
- **Arquivo:** `mlops/evaluation/lm-evaluation-harness/SKILL.md`
- **Tamanho:** 12,020 chars
- **Resumo:** Benchmark LLMs using lm-eval-harness — MMLU, GSM8K, and other standard evaluations.

lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.).

**Relações:**
- `uses` → `mlops/inference/vllm`
- `uses` → `mlops/huggingface-hub`
- `similar` → `mlops/evaluation/weights-and-biases`

- `similar` → `mlops/inference/llama-cpp`
### Weights & Biases: ML Experiment Tracking & MLOps

- **Nome:** `mlops/evaluation/weights-and-biases`
- **Arquivo:** `mlops/evaluation/weights-and-biases/SKILL.md`
- **Tamanho:** 12,395 chars
- **Resumo:** W&B: log ML experiments, sweeps, model registry, dashboards

W&B: log ML experiments, sweeps, model registry, dashboards.

**Relações:**
- `uses` → `mlops/huggingface-hub`
- `similar` → `mlops/evaluation/lm-evaluation-harness`

- `similar` → `data-science/jupyter-live-kernel`
- `uses` → `mlops/inference/vllm`
### Hugging Face CLI (`hf`) Reference Guide

- **Nome:** `mlops/huggingface-hub`
- **Arquivo:** `mlops/huggingface-hub/SKILL.md`
- **Tamanho:** 3,674 chars
- **Resumo:** HuggingFace hf CLI: search/download/upload models, datasets

HuggingFace hf CLI: search/download/upload models, datasets.

**Relações:**
- `used_by` → `mlops/evaluation/lm-evaluation-harness`
- `used_by` → `mlops/inference/llama-cpp`
- `used_by` → `mlops/inference/vllm`
- `used_by` → `infrastructure/ai-voice-selfhost`

### llama.cpp + GGUF

- **Nome:** `mlops/inference/llama-cpp`
- **Arquivo:** `mlops/inference/llama-cpp/SKILL.md`
- **Tamanho:** 8,880 chars
- **Resumo:** Local GGUF inference with llama.cpp and model discovery via Hugging Face Hub.

Local GGUF inference with llama.cpp and model discovery via Hugging Face Hub.

**Relações:**
- `uses` → `mlops/huggingface-hub`
- `similar` → `mlops/inference/vllm`
- `similar` → `infrastructure/ai-voice-selfhost`

- `similar` → `mlops/evaluation/lm-evaluation-harness`
### vLLM - High-Performance LLM Serving

- **Nome:** `mlops/inference/vllm`
- **Arquivo:** `mlops/inference/vllm/SKILL.md`
- **Tamanho:** 9,071 chars
- **Resumo:** vLLM: high-throughput LLM serving, OpenAI API, quantization

vLLM: high-throughput LLM serving, OpenAI API, quantization.

**Relações:**
- `uses` → `mlops/huggingface-hub`
- `used_by` → `mlops/evaluation/lm-evaluation-harness`
- `similar` → `mlops/inference/llama-cpp`

- `similar` → `infrastructure/ai-voice-selfhost`
### Pi Agent Session Audit

- **Nome:** `autonomous-ai-agents/pi-session-audit`
- **Arquivo:** `autonomous-ai-agents/pi-session-audit/SKILL.md`
- **Tamanho:** 13,878 chars
- **Resumo:** Audita sessões do Pi Agent extraindo duração, tokens, custo e modelo dos arquivos .jsonl.

Audita sessões do Pi Agent extraindo duração, tokens, custo e modelo dos arquivos .jsonl. Load this skill to analyze Pi Agent session logs and calculate costs per provider. Extracts real usage metrics from session JSONL files, computes costs based on model pricing, and produces audit reports for tracking agent usage and spending.

**Relações:**
- `used_by` → `autonomous-ai-agents/pi-agent-coordination`
- `used_by` → `autonomous-ai-agents/product-pipeline`
- `similar` → `autonomous-ai-agents/autonomous-ai-agents`


## Note Taking

### Obsidian Vault

- **Nome:** `note-taking/obsidian`
- **Arquivo:** `note-taking/obsidian/SKILL.md`
- **Tamanho:** 2,919 chars
- **Resumo:** Read, search, create, and edit notes in the Obsidian vault

Read, search, create, and edit notes in the Obsidian vault.

**Relações:**
- `used_by` → `research/llm-wiki`

- `similar` → `apple/apple-notes`
- `similar` → `productivity/notion`

## Productivity

### Airtable — Bases, Tables & Records

- **Nome:** `productivity/airtable`
- **Arquivo:** `productivity/airtable/SKILL.md`
- **Tamanho:** 11,302 chars
- **Resumo:** Airtable REST API via curl

Airtable REST API via curl. Records CRUD, filters, upserts.

**Relações:**
- `similar` → `productivity/notion`
- `similar` → `productivity/google-workspace`

- `similar` → `productivity/html-report-hermes`
### Google Workspace

- **Nome:** `productivity/google-workspace`
- **Arquivo:** `productivity/google-workspace/SKILL.md`
- **Tamanho:** 16,272 chars
- **Resumo:** Google OAuth2 client credentials (downloaded from Google Cloud Console)

Google OAuth2 client credentials (downloaded from Google Cloud Console)

**Relações:**
- `similar` → `productivity/airtable`
- `uses` → `productivity/ocr-and-documents`
- `similar` → `email/himalaya`

### HTML Report — Hermes Design System

- **Nome:** `productivity/html-report-hermes`
- **Arquivo:** `productivity/html-report-hermes/SKILL.md`
- **Tamanho:** 15,051 chars
- **Resumo:** Render dense research reports, analyses, and data summaries as beautiful standalone HTM...

Render research reports as dark-themed HTML with SVG charts and Tufte-inspired typography.

Two design systems in one skill: Hermes CRT (amber/blue inversion, scanlines, terminal aesthetic) for visual showcases and landing pages, and Hermes Official (blue royal on white, Inter + Space Mono, clean cards) for data reports, benchmarks, and dashboards. Covers CRT overlay mechanics, inverted color coding, component library, report structure templates, Telegram delivery via ZIP, and the agy pipeline for complex CRT pages. Activates automatically when the user needs structured visual output.

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `productivity/html-to-pdf-chromium`
- `used_by` → `productivity/relatorio-de-custos`
- `used_by` → `productivity/html-to-pdf-chromium`

- `similar` → `email/himalaya`
- `similar` → `infrastructure/vercel-deploy`
### HTML → PDF com Chromium Headless

- **Nome:** `productivity/html-to-pdf-chromium`
- **Arquivo:** `productivity/html-to-pdf-chromium/SKILL.md`
- **Tamanho:** 5,924 chars
- **Resumo:** Convert HTML files to high-fidelity PDF using Chromium headless (via Debian

Convert HTML files to high-fidelity PDF using Chromium headless (via Debian .deb extraction, no root or Playwright required). Use when weasyprint or other tools lose CSS features like gradients, webkit-background-clip, grid, and glow effects.

**Relações:**
- `uses` → `productivity/html-report-hermes`
- `used_by` → `productivity/html-report-hermes`
- `used_by` → `productivity/nano-pdf`

- `similar` → `productivity/nano-pdf`
- `similar` → `productivity/powerpoint`
- `uses` → `productivity/ocr-and-documents`
### Maps Skill

- **Nome:** `productivity/maps`
- **Arquivo:** `productivity/maps/SKILL.md`
- **Tamanho:** 6,726 chars
- **Resumo:** Geocode, POIs, routes, timezones via OpenStreetMap/OSRM

Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.

**Relações:**
- `similar` → `apple/findmy`

- `similar` → `research/deep-research`
- `uses` → `read-reddit`
### nano-pdf

- **Nome:** `productivity/nano-pdf`
- **Arquivo:** `productivity/nano-pdf/SKILL.md`
- **Tamanho:** 1,414 chars
- **Resumo:** Edit PDF text/typos/titles via nano-pdf CLI (NL prompts)

Edit PDF text/typos/titles via nano-pdf CLI (NL prompts).

**Relações:**
- `uses` → `productivity/ocr-and-documents`
- `uses` → `productivity/html-to-pdf-chromium`
- `similar` → `productivity/ocr-and-documents`

- `similar` → `productivity/html-to-pdf-chromium`
- `similar` → `productivity/powerpoint`
### Notion

- **Nome:** `productivity/notion`
- **Arquivo:** `productivity/notion/SKILL.md`
- **Tamanho:** 15,359 chars
- **Resumo:** Notion API + ntn CLI: pages, databases, markdown, Workers

Notion API + ntn CLI: pages, databases, markdown, Workers.

**Relações:**
- `similar` → `productivity/airtable`
- `similar` → `productivity/taskflow-mcp`

- `similar` → `note-taking/obsidian`
- `similar` → `research/llm-wiki`
- `uses` → `productivity/taskflow-mcp`
### PDF & Document Extraction

- **Nome:** `productivity/ocr-and-documents`
- **Arquivo:** `productivity/ocr-and-documents/SKILL.md`
- **Tamanho:** 5,280 chars
- **Resumo:** Extract text from PDFs/scans (pymupdf, marker-pdf)

Extract text from PDFs/scans (pymupdf, marker-pdf).

**Relações:**
- `uses` → `productivity/powerpoint`
- `uses` → `productivity/nano-pdf`
- `used_by` → `productivity/google-workspace`
- `used_by` → `productivity/nano-pdf`
- `similar` → `productivity/nano-pdf`
- `used_by` → `productivity/powerpoint`

- `uses` → `research/arxiv`
- `uses` → `research/research-paper-writing`
### Powerpoint Skill

- **Nome:** `productivity/powerpoint`
- **Arquivo:** `productivity/powerpoint/SKILL.md`
- **Tamanho:** 9,298 chars
- **Resumo:** Create, read, edit

Create, read, edit .pptx decks, slides, notes, templates.

**Relações:**
- `uses` → `productivity/ocr-and-documents`
- `used_by` → `productivity/ocr-and-documents`

- `similar` → `productivity/html-to-pdf-chromium`
- `similar` → `productivity/nano-pdf`
- `uses` → `creative/copywriting`
- `uses` → `software-development/agy`
### Relatório de Custos — Skill de Geração

- **Nome:** `productivity/relatorio-de-custos`
- **Arquivo:** `productivity/relatorio-de-custos/SKILL.md`
- **Tamanho:** 9,688 chars
- **Resumo:** Gera relatórios técnicos de custos de execução de projetos multi-agente com dados reais de tokens.

Gera relatórios técnicos de custos de execução de projetos multi-agente com dados reais de tokens.

Load this skill when the user asks for cost reports, spending breakdowns, or project expense analysis. Extracts real data from Hermes (state.db) and Pi Agent (.jsonl) session logs, calculates costs based on model pricing per provider, and produces styled HTML reports via Antigravity (agy) with Hermes Style Guide design.

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `productivity/html-report-hermes`

- `similar` → `productivity/html-report-hermes`
- `similar` → `software-development/backlog-and-sprint`
- `uses` → `autonomous-ai-agents/product-pipeline`
### TaskFlow MCP — Ferramentas e Workflows

- **Nome:** `productivity/taskflow-mcp`
- **Arquivo:** `productivity/taskflow-mcp/SKILL.md`
- **Tamanho:** 4,485 chars
- **Resumo:** TaskFlow é um sistema GTD de gerenciamento de tarefas exposto via MCP (Model Context Protocol) — conecta-se via SSE.

TaskFlow é um sistema GTD de gerenciamento de tarefas exposto via MCP (Model Context Protocol). Conecta-se via SSE (StreamableHTTP POST não funciona — SSE deve ser explícito).

**Relações:**
- `similar` → `productivity/notion`
- `similar` → `software-development/backlog-and-sprint`

- `similar` → `note-taking/obsidian`
- `uses` → `productivity/notion`

## Research

### arXiv Research

- **Nome:** `research/arxiv`
- **Arquivo:** `research/arxiv/SKILL.md`
- **Tamanho:** 10,085 chars
- **Resumo:** Search arXiv papers by keyword, author, category, or ID

Search arXiv papers by keyword, author, category, or ID.

**Relações:**
- `used_by` → `research/deep-research`
- `similar` → `research/llm-wiki`

- `used_by` → `research/research-paper-writing`
- `uses` → `productivity/ocr-and-documents`
- `uses` → `research/llm-wiki`
### Blogwatcher

- **Nome:** `research/blogwatcher`
- **Arquivo:** `research/blogwatcher/SKILL.md`
- **Tamanho:** 5,111 chars
- **Resumo:** Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool

Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.

**Relações:**
- `similar` → `read-reddit/read-reddit`
- `used_by` → `research/deep-research`
- `similar` → `research/tech-trend-discovery`

- `similar` → `read-reddit`
- `uses` → `research/deep-research`
### Deep Research Skill

- **Nome:** `research/deep-research`
- **Arquivo:** `research/deep-research/SKILL.md`
- **Tamanho:** 33,335 chars
- **Resumo:** 基于 GPT-Researcher 架构，适配 Hermes delegate_task 的多 agent 深度调研流水线

Multi-agent deep research pipeline: decompose topics, dispatch parallel agents, review, cross-validate, synthesize.

Inspired by GPT-Researcher, this pipeline decomposes complex questions into sub-queries, dispatches parallel research agents across web, GitHub, news, and academic sources, runs independent reviewers for source verification, then conducts cross-validation and a roundtable discussion. Produces a final cited report with confidence-graded findings (HIGH/MEDIUM/LOW/CONTESTED). Supports three depth levels (Quick, Standard, Deep), adaptive phase skipping, local codebase analysis as Phase 0.5, and a bug-to-fix pipeline pattern.

**Relações:**
- `uses` → `research/arxiv`
- `uses` → `research/blogwatcher`
- `similar` → `research/llm-wiki`
- `similar` → `research/tech-trend-discovery`
- `similar` → `research/polymarket`

- `similar` → `research/research-paper-writing`
- `similar` → `software-development/spike`
- `uses` → `research/tech-trend-discovery`
- `uses` → `research/user-interview`
### Karpathy's LLM Wiki

- **Nome:** `research/llm-wiki`
- **Arquivo:** `research/llm-wiki/SKILL.md`
- **Tamanho:** 20,113 chars
- **Resumo:** Karpathy's LLM Wiki: build/query interlinked markdown KB

Karpathy's LLM Wiki: build/query interlinked markdown KB.

**Relações:**
- `similar` → `research/arxiv`
- `similar` → `research/deep-research`
- `uses` → `note-taking/obsidian`

- `similar` → `note-taking/obsidian`
- `similar` → `productivity/notion`
- `uses` → `productivity/ocr-and-documents`
### Polymarket — Prediction Market Data

- **Nome:** `research/polymarket`
- **Arquivo:** `research/polymarket/SKILL.md`
- **Tamanho:** 2,985 chars
- **Resumo:** Query Polymarket: markets, prices, orderbooks, history

Query Polymarket: markets, prices, orderbooks, history.

Read-only access to Polymarket prediction market data via three public REST APIs (Gamma, CLOB, Data) — no authentication required. Search markets, fetch real-time prices and orderbooks, retrieve price history, and present probabilities as human-readable percentages. Covers double-encoded JSON field parsing, rate limits, and the events-to-markets data model.

**Relações:**
- `similar` → `research/deep-research`
- `similar` → `research/tech-trend-discovery`

### Research Paper Writing Pipeline

- **Nome:** `research/research-paper-writing`
- **Arquivo:** `research/research-paper-writing/SKILL.md`
- **Tamanho:** 103,375 chars
- **Resumo:** Write ML papers for NeurIPS/ICML/ICLR: design→submit

Write ML papers for NeurIPS/ICML/ICLR: design→submit.

**Relações:**
- `uses` → `software-development/plan`

- `similar` → `software-development/plan`
- `uses` → `productivity/ocr-and-documents`
- `uses` → `research/arxiv`
- `uses` → `research/deep-research`
- `uses` → `research/user-interview`
### Tech Trend Discovery

- **Nome:** `research/tech-trend-discovery`
- **Arquivo:** `research/tech-trend-discovery/SKILL.md`
- **Tamanho:** 15,028 chars
- **Resumo:** Discover what the tech/AI community is discussing right now — trending topics, hot disc...

Discover what the tech/AI community is discussing right now — trending topics, hot discussions, and breaking conversations. Covers Reddit alternatives and HN Algolia API as primary sources when traditional search tools fail.

**Relações:**
- `similar` → `research/blogwatcher`
- `similar` → `research/deep-research`

- `similar` → `social-media/xurl`
- `used_by` → `research/deep-research`
- `uses` → `read-reddit`
- `uses` → `research/blogwatcher`
### User Interview

- **Nome:** `research/user-interview`
- **Arquivo:** `research/user-interview/SKILL.md`
- **Tamanho:** 9,161 chars
- **Resumo:** Structured user/proxy interview protocol for product research — plan, frame, listen, synthesize, extract personas.

Structured user/proxy interview protocol for product research — plan, frame, listen, synthesize, extract personas.

Load this skill during the Research phase (Fase 2) of the product pipeline to understand user needs, pain points, and behaviors before defining personas or user stories. Covers interview planning, question framing, active listening techniques, synthesis of findings, and persona extraction. Can interview real humans or simulate interviews with AI agent profiles.

**Relações:**
- `used_by` → `software-development/ideation-drilling`
- `used_by` → `software-development/backlog-and-sprint`

- `similar` → `software-development/ideation-drilling`
- `used_by` → `research/deep-research`
- `used_by` → `research/research-paper-writing`
## Social Media

### Brand IAF — Conteúdo

- **Nome:** `social-media/brand-iaf-conteudo`
- **Arquivo:** `social-media/brand-iaf-conteudo/SKILL.md`
- **Tamanho:** 5,276 chars
- **Resumo:** Skill de conteúdo da comunidade IA que Funciona (IAF)

Skill de conteúdo da comunidade IA que Funciona (IAF). Contém constantes de marca, voz, tom, paleta, tipografia, regras de idioma e templates de conteúdo. Use para gerar qualquer texto da comunidade — newsletter diária, posts, discussões, boas-vindas.

**Relações:**
- `similar` → `social-media/xurl`
- `used_by` → `content-production/iaf-newsletter-pipeline`
- `similar` → `creative/copywriting`

- `similar` → `productivity/powerpoint`
- `uses` → `research/tech-trend-discovery`
- `uses` → `social-media/xurl`
- `uses` → `software-development/agy`
### xurl — X (Twitter) API via the Official CLI

- **Nome:** `social-media/xurl`
- **Arquivo:** `social-media/xurl/SKILL.md`
- **Tamanho:** 15,518 chars
- **Resumo:** X/Twitter via xurl CLI: post, search, DM, media, v2 API

X/Twitter via xurl CLI: post, search, DM, media, v2 API.

**Relações:**
- `similar` → `social-media/brand-iaf-conteudo`

- `similar` → `read-reddit`
- `similar` → `research/tech-trend-discovery`
- `uses` → `research/polymarket`
- `uses` → `social-media/brand-iaf-conteudo`
## Software Development

### agy — Antigravity CLI (Consultor Externo)

- **Nome:** `software-development/agy`
- **Arquivo:** `software-development/agy/SKILL.md`
- **Tamanho:** 8,611 chars
- **Resumo:** Google Antigravity CLI (agy) — installation, OAuth auth, and design workflows for HTML reports and prototyping.

Load this skill for strategic design tasks — visual HTML output, brand presentations, UI mockups, SVGs, and prototypes. Covers agy installation, OAuth authentication via tmux, and design workflows including image generation, prototyping, parallel subagents, and HTML report generation. Part of the three-tier agent hierarchy (agy > Pi best > Pi cost) where agy serves as external specialist consultant.

**Relações:**
- `used_by` → `software-development/backlog-and-sprint`
- `used_by` → `productivity/relatorio-de-custos`

- `uses` → `productivity/powerpoint`
- `uses` → `social-media/brand-iaf-conteudo`
### Backlog & Sprint

- **Nome:** `software-development/backlog-and-sprint`
- **Arquivo:** `software-development/backlog-and-sprint/SKILL.md`
- **Tamanho:** 78,483 chars
- **Resumo:** Backlog management and Sprint execution for product iteration (Fase 5) — mantém backlog não-estruturada e orquestra Sprints completas.

Backlog management and Sprint execution for product iteration (Fase 5). Mantém uma backlog não-estruturada de pedidos de melhoria, e orquestra Sprints completas (PM → UX/UI → Engineering → Review → Close).

Load this skill during the execution phase (Fase 5) of the product pipeline. Covers maintaining an unstructured backlog of improvement requests and orchestrating complete Sprints — from PM and UX/UI through Engineering, Review, and Close.

**Relações:**
- `uses` → `software-development/agy`
- `uses` → `research/user-interview`
- `used_by` → `software-development/ideation-drilling`

- `similar` → `productivity/relatorio-de-custos`
- `similar` → `productivity/taskflow-mcp`
- `uses` → `software-development/ideation-drilling`
- `uses` → `software-development/plan`
### Authoring Hermes-Agent Skills (in-repo)

- **Nome:** `software-development/hermes-agent-skill-authoring`
- **Arquivo:** `software-development/hermes-agent-skill-authoring/SKILL.md`
- **Tamanho:** 8,523 chars
- **Resumo:** Author in-repo SKILL.md and DESIGN.md token specs — frontmatter, validator, structure.

Author in-repo SKILL.md + DESIGN.md token specs: frontmatter, validator, structure. Merged with design-md skill.

**Relações:**
- `uses` → `software-development/plan`
- `used_by` → `software-development/skill-curation`
- `used_by` → `software-development/skills-repo-curator`

- `similar` → `software-development/skill-curation`
### Ideation Drilling (Hermes — Orchestrator)

- **Nome:** `software-development/ideation-drilling`
- **Arquivo:** `software-development/ideation-drilling/SKILL.md`
- **Tamanho:** 14,550 chars
- **Resumo:** - O usuário diz: "Tenho uma ideia para um produto/feature" - O usuário pede: "Me ajude ...

- O usuário diz: "Tenho uma ideia para um produto/feature" - O usuário pede: "Me ajude a refinar essa ideia" - Início do pipeline de produto (Fase 1)

**Relações:**
- `uses` → `research/user-interview`
- `parent` → `software-development/backlog-and-sprint`

- `similar` → `software-development/spike`
- `used_by` → `software-development/backlog-and-sprint`
- `uses` → `software-development/plan`
### Plan Mode

- **Nome:** `software-development/plan`
- **Arquivo:** `software-development/plan/SKILL.md`
- **Tamanho:** 11,315 chars
- **Resumo:** Plan mode: write an actionable markdown plan to

Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code.

**Relações:**
- `uses` → `software-development/test-driven-development`
- `used_by` → `software-development/spike`
- `used_by` → `software-development/hermes-agent-skill-authoring`
- `used_by` → `research/research-paper-writing`
- `used_by` → `software-development/systematic-debugging`
- `used_by` → `software-development/backlog-and-sprint`
- `similar` → `software-development/spike`

- `uses` → `software-development/systematic-debugging`
### Skill Curation — Discover, Evaluate & Install Hermes Skills

- **Nome:** `software-development/skill-curation`
- **Arquivo:** `software-development/skill-curation/SKILL.md`
- **Tamanho:** 10,756 chars
- **Resumo:** Discover, evaluate, rank, and install community skills for Hermes Agent — full curation lifecycle from search to verification.

Discover, evaluate, rank, and install community skills for Hermes Agent — full curation lifecycle from search to verification.

Load this skill when you need to find, evaluate, and install community skills for Hermes. Covers web search for skills, extraction from GitHub repos, cross-referencing reviews, tiered ranking with user feedback, installation via tap+hub or raw URL, and post-install verification.

**Relações:**
- `uses` → `software-development/hermes-agent-skill-authoring`
- `similar` → `software-development/skills-repo-curator`

- `uses` → `read-reddit`
- `uses` → `research/tech-trend-discovery`
### Skills Repository Curator

- **Nome:** `software-development/skills-repo-curator`
- **Arquivo:** `software-development/skills-repo-curator/SKILL.md`
- **Tamanho:** 16,395 chars
- **Resumo:** Gerencia o repositório git de skills do Hermes — ciclo evolve de consolidação MECE, ind

Gerencia o repositório git de skills do Hermes — ciclo evolve de consolidação MECE, index.md/log.md/reports, offload de memória, e manutenção de AGENTS.md. Executa o processo completo de análise, merge, delete, relatório e commit.

**Relações:**
- `uses` → `software-development/hermes-agent-skill-authoring`
- `similar` → `software-development/skill-curation`

- `uses` → `productivity/relatorio-de-custos`
- `uses` → `software-development/plan`
### Spike

- **Nome:** `software-development/spike`
- **Arquivo:** `software-development/spike/SKILL.md`
- **Tamanho:** 8,730 chars
- **Resumo:** Throwaway experiments to validate an idea before build

Throwaway experiments to validate an idea before build.

**Relações:**
- `uses` → `software-development/plan`
- `similar` → `software-development/plan`
- `similar` → `data-science/jupyter-live-kernel`

- `similar` → `research/deep-research`
- `similar` → `software-development/systematic-debugging`
- `uses` → `software-development/ideation-drilling`
- `uses` → `software-development/test-driven-development`
### Systematic Debugging

- **Nome:** `software-development/systematic-debugging`
- **Arquivo:** `software-development/systematic-debugging/SKILL.md`
- **Tamanho:** 12,296 chars
- **Resumo:** 4-phase root cause debugging — methodology + Python (pdb/debugpy) + Node

4-phase root cause debugging — methodology + Python (pdb/debugpy) + Node.js (--inspect). Understand bugs before fixing.

**Relações:**
- `uses` → `software-development/test-driven-development`
- `uses` → `software-development/plan`
- `used_by` → `software-development/test-driven-development`

- `similar` → `software-development/spike`
- `uses` → `software-development/spike`
### Test-Driven Development (TDD)

- **Nome:** `software-development/test-driven-development`
- **Arquivo:** `software-development/test-driven-development/SKILL.md`
- **Tamanho:** 9,810 chars
- **Resumo:** TDD: enforce RED-GREEN-REFACTOR, tests before code

TDD: enforce RED-GREEN-REFACTOR, tests before code.

**Relações:**
- `uses` → `software-development/systematic-debugging`
- `used_by` → `software-development/plan`
- `used_by` → `software-development/systematic-debugging`

- `similar` → `software-development/systematic-debugging`
- `uses` → `software-development/plan`
- `uses` → `software-development/spike`
## Uncategorized

### Dogfood: Systematic Web Application QA Testing

- **Nome:** `dogfood`
- **Arquivo:** `dogfood/SKILL.md`
- **Tamanho:** 9,269 chars
- **Resumo:** Exploratory QA of web apps: find bugs, evidence, reports

Exploratory QA of web apps: find bugs, evidence, reports.

**Relações:**
- `similar` → `github/codebase-inspection`
- `uses` → `github/github-issues`
- `similar` → `github/github-pr-workflow`
- `similar` → `software-development/systematic-debugging`

### Read Reddit via RSS

- **Nome:** `read-reddit`
- **Arquivo:** `read-reddit/SKILL.md`
- **Tamanho:** 7,130 chars
- **Resumo:** How to read Reddit subreddits reliably using RSS feeds — bypassing API rate limits and ...

Read Reddit subreddits reliably via RSS feeds — bypasses API rate limits and bot detection. For research, curation, or news gathering.

**Relações:**
- `similar` → `research/blogwatcher`
- `similar` → `research/tech-trend-discovery`
- `similar` → `social-media/xurl`