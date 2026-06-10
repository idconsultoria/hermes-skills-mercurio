# Skills Index — Hermes Agent

*Total: 93 skills*

Catálogo completo com metadados e relacionamentos.

---


## Apple

### Apple Notes

- **Nome:** `apple/apple-notes`
- **Arquivo:** `apple/apple-notes/SKILL.md`
- **Tamanho:** 2,169 chars
- **Resumo:** Manage Apple Notes via memo CLI: create, search, edit

Manage Apple Notes via memo CLI: create, search, edit.

**Relações:**
- `uses` → `obsidian`
- `similar` → `obsidian`

### Apple Reminders

- **Nome:** `apple/apple-reminders`
- **Arquivo:** `apple/apple-reminders/SKILL.md`
- **Tamanho:** 3,606 chars
- **Resumo:** Apple Reminders via remindctl: add, list, complete

Apple Reminders via remindctl: add, list, complete.

**Relações:**
- `similar` → `notion`

### Find My (Apple)

- **Nome:** `apple/findmy`
- **Arquivo:** `apple/findmy/SKILL.md`
- **Tamanho:** 3,709 chars
- **Resumo:** Track Apple devices/AirTags via FindMy

Track Apple devices/AirTags via FindMy.app on macOS.

### iMessage

- **Nome:** `apple/imessage`
- **Arquivo:** `apple/imessage/SKILL.md`
- **Tamanho:** 2,442 chars
- **Resumo:** Send and receive iMessages/SMS via the imsg CLI on macOS

Send and receive iMessages/SMS via the imsg CLI on macOS.

### macOS Computer Use (universal, any-model)

- **Nome:** `apple/macos-computer-use`
- **Arquivo:** `apple/macos-computer-use/SKILL.md`
- **Tamanho:** 7,309 chars
- **Resumo:** You have a `computer_use` tool that drives the Mac in the **background**

You have a `computer_use` tool that drives the Mac in the **background**. Your actions do NOT move the user's cursor, steal keyboard focus, or switch Spaces. The user can keep typing in their editor while you click around in Safari in another Space. This is the opposite of pyautogui-style automation


## Autonomous Ai Agents

### Claude Code — Hermes Orchestration Guide

- **Nome:** `autonomous-ai-agents/claude-code`
- **Arquivo:** `autonomous-ai-agents/claude-code/SKILL.md`
- **Tamanho:** 34,288 chars
- **Resumo:** Delegate coding to Claude Code CLI (features, PRs)

Delegate coding to Claude Code CLI (features, PRs).

**Relações:**
- `uses` → `codex`
- `uses` → `hermes-agent`
- `uses` → `opencode`
- `similar` → `plan`

### Codex CLI

- **Nome:** `autonomous-ai-agents/codex`
- **Arquivo:** `autonomous-ai-agents/codex/SKILL.md`
- **Tamanho:** 5,386 chars
- **Resumo:** Delegate coding to OpenAI Codex CLI (features, PRs)

Delegate coding to OpenAI Codex CLI (features, PRs).

**Relações:**
- `uses` → `claude-code`
- `uses` → `hermes-agent`

### Hermes Agent

- **Nome:** `autonomous-ai-agents/hermes-agent`
- **Arquivo:** `autonomous-ai-agents/hermes-agent/SKILL.md`
- **Tamanho:** 46,692 chars
- **Resumo:** Configure, extend, or contribute to Hermes Agent

Configure, extend, or contribute to Hermes Agent.

**Relações:**
- `uses` → `claude-code`
- `uses` → `codex`
- `uses` → `opencode`
- `similar` → `codex`
- `similar` → `opencode`
- `similar` → `yuanbao`
- `similar` → `imessage`

### Messaging Platforms

- **Nome:** `autonomous-ai-agents/messaging-platforms`
- **Arquivo:** `autonomous-ai-agents/messaging-platforms/SKILL.md`
- **Tamanho:** 11,222 chars
- **Resumo:** Hermes cross-platform message sending — platform-specific quirks, JID/ID format require...

Hermes cross-platform message sending — platform-specific quirks, JID/ID format requirements, bridge API workarounds, and channel directory resolution. Covers Telegram, WhatsApp, and other messaging adapters.

### OpenCode CLI

- **Nome:** `autonomous-ai-agents/opencode`
- **Arquivo:** `autonomous-ai-agents/opencode/SKILL.md`
- **Tamanho:** 7,259 chars
- **Resumo:** Delegate coding to OpenCode CLI (features, PR review)

Delegate coding to OpenCode CLI (features, PR review).

**Relações:**
- `uses` → `claude-code`
- `uses` → `codex`
- `uses` → `hermes-agent`
- `similar` → `plan`

### Pi Agent (Local)

- **Nome:** `autonomous-ai-agents/pi-agent-coordination`
- **Arquivo:** `autonomous-ai-agents/pi-agent-coordination/SKILL.md`
- **Tamanho:** 26,294 chars
- **Resumo:** Pi Coder Agent local no Hermes

Pi Coder Agent local no Hermes. Hierarquia: agy > Pi best > Pi cost. Invoacao direta sem Docker/SSH.

**Relações:**
- `similar` → `agy`
- `similar` → `opencode`

### Product Development Pipeline

- **Nome:** `autonomous-ai-agents/product-pipeline`
- **Arquivo:** `autonomous-ai-agents/product-pipeline/SKILL.md`
- **Tamanho:** 80,167 chars
- **Resumo:** **Orquestrador:** Hermes **Executores:** Pi Agent (local, v0

**Orquestrador:** Hermes **Executores:** Pi Agent (local, v0.78.1) + Antigravity (revisor visual) **Shared volume:** `/opt/data/code/` ↔ `/workspace/code/` ┌───────────────────────────────────────────────────┐ │                     Hermes                         │ │  Orquestrador • valida • agenda •

**Relações:**
- `similar` → `plan`
- `similar` → `agy`
- `similar` → `opencode`
- `similar` → `dogfood`


## Content Production

### IAF Newsletter Pipeline — Manhã Aumentada

- **Nome:** `content-production/iaf-newsletter-pipeline`
- **Arquivo:** `content-production/iaf-newsletter-pipeline/SKILL.md`
- **Tamanho:** 8,803 chars
- **Resumo:** Umbrella skill for all newsletter/briefing/digest pipelines — IAF Manhã Aumentada, Dail...

Umbrella skill for all newsletter/briefing/digest pipelines — IAF Manhã Aumentada, Daily AI Digest, editorial curation, cron scheduling, briefing patterns. Covers multi-source collection, ranking/scoring, HTML→PDF, dedup, WhatsApp companion, and delivery.

**Relações:**
- `similar` → `humanizer`
- `similar` → `copywriting`

### Text-to-Speech (TTS)

- **Nome:** `content-production/text-to-speech`
- **Arquivo:** `content-production/text-to-speech/SKILL.md`
- **Tamanho:** 7,413 chars
- **Resumo:** Umbrella skill

Umbrella skill. Covers: - [Voice design & prompting](#gemini-31-flash-tts) — Gemini TTS prompt structure, voice selection, audio tags - [Hermes TTS system](#hermes-tts-command-provider-chain) — multi-provider fallback, config - [Self-hosted inference](#fish-speech-s2-pro-gguf-self-hosted) — Fish Spe

**Relações:**
- `uses` → `hermes-agent`


## Creative

### Architecture Diagram Skill

- **Nome:** `creative/architecture-diagram`
- **Arquivo:** `creative/architecture-diagram/SKILL.md`
- **Tamanho:** 5,830 chars
- **Resumo:** Dark-themed SVG architecture/cloud/infra diagrams as HTML

Dark-themed SVG architecture/cloud/infra diagrams as HTML.

**Relações:**
- `uses` → `excalidraw`
- `similar` → `excalidraw`

### ASCII Art Skill

- **Nome:** `creative/ascii-art`
- **Arquivo:** `creative/ascii-art/SKILL.md`
- **Tamanho:** 10,556 chars
- **Resumo:** ASCII art: pyfiglet, cowsay, boxes, image-to-ascii

ASCII art: pyfiglet, cowsay, boxes, image-to-ascii.

**Relações:**
- `uses` → `excalidraw`

### ASCII Video Production Pipeline

- **Nome:** `creative/ascii-video`
- **Arquivo:** `creative/ascii-video/SKILL.md`
- **Tamanho:** 14,864 chars
- **Resumo:** ASCII video: convert video/audio to colored ASCII MP4/GIF

ASCII video: convert video/audio to colored ASCII MP4/GIF.

### Infographic Generator

- **Nome:** `creative/baoyu-infographic`
- **Arquivo:** `creative/baoyu-infographic/SKILL.md`
- **Tamanho:** 10,434 chars
- **Resumo:** Infographics: 21 layouts x 21 styles (信息图, 可视化)

Infographics: 21 layouts x 21 styles (信息图, 可视化).

### brand-studio-forge

- **Nome:** `creative/brand-studio-forge`
- **Arquivo:** `creative/brand-studio-forge/SKILL.md`
- **Tamanho:** 17,756 chars
- **Resumo:** Use when the user wants to create, refine, or evolve a brand identity

Use when the user wants to create, refine, or evolve a brand identity. Covers brand interviews, identity kit generation (logo, color, type, voice, guidelines), brand-specific content skills, and ongoing content via cron. Not for UI design or non-brand creative tasks.

**Relações:**
- `similar` → `codex`
- `similar` → `agy`
- `similar` → `copywriting`

### Claude Design for CLI/API Agents

- **Nome:** `creative/claude-design`
- **Arquivo:** `creative/claude-design/SKILL.md`
- **Tamanho:** 19,859 chars
- **Resumo:** Design one-off HTML artifacts (landing, deck, prototype)

Design one-off HTML artifacts (landing, deck, prototype).

**Relações:**
- `uses` → `design-md`
- `uses` → `popular-web-designs`
- `uses` → `excalidraw`
- `uses` → `architecture-diagram`
- `similar` → `notion`

### ComfyUI

- **Nome:** `creative/comfyui`
- **Arquivo:** `creative/comfyui/SKILL.md`
- **Tamanho:** 24,287 chars
- **Resumo:** Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, ...

Generate images, video, and audio with ComfyUI — install, launch, manage nodes/models, run workflows with parameter injection. Uses the official comfy-cli for lifecycle and direct REST/WebSocket API for execution.

### Copywriting

- **Nome:** `creative/copywriting`
- **Arquivo:** `creative/copywriting/SKILL.md`
- **Tamanho:** 7,429 chars
- **Resumo:** Expert conversion copywriting — write, rewrite, or improve marketing copy for any page

Expert conversion copywriting — write, rewrite, or improve marketing copy for any page. Use when the user says 'write copy for,' 'improve this copy,' 'headline help,' 'CTA copy,' 'value proposition,' 'tagline,' 'hero section copy,' 'above the fold,' 'this copy is weak,' 'make this more compelling.' For email copy see emails skill. For editing copy see copy-editing.

**Relações:**
- `similar` → `plan`

### DESIGN.md Skill

- **Nome:** `creative/design-md`
- **Arquivo:** `creative/design-md/SKILL.md`
- **Tamanho:** 7,023 chars
- **Resumo:** Author/validate/export Google's DESIGN

Author/validate/export Google's DESIGN.md token spec files.

**Relações:**
- `uses` → `popular-web-designs`
- `uses` → `claude-design`
- `uses` → `excalidraw`
- `uses` → `architecture-diagram`

### Excalidraw Diagram Skill

- **Nome:** `creative/excalidraw`
- **Arquivo:** `creative/excalidraw/SKILL.md`
- **Tamanho:** 7,300 chars
- **Resumo:** Hand-drawn Excalidraw JSON diagrams (arch, flow, seq)

Hand-drawn Excalidraw JSON diagrams (arch, flow, seq).

**Relações:**
- `similar` → `maps`

### Humanizer: Remove AI Writing Patterns

- **Nome:** `creative/humanizer`
- **Arquivo:** `creative/humanizer/SKILL.md`
- **Tamanho:** 30,025 chars
- **Resumo:** Humanize text: strip AI-isms and add real voice

Humanize text: strip AI-isms and add real voice.

**Relações:**
- `uses` → `songwriting-and-ai-music`
- `similar` → `codex`

### Manim Video Production Pipeline

- **Nome:** `creative/manim-video`
- **Arquivo:** `creative/manim-video/SKILL.md`
- **Tamanho:** 12,023 chars
- **Resumo:** Manim CE animations: 3Blue1Brown math/algo videos

Manim CE animations: 3Blue1Brown math/algo videos.

**Relações:**
- `similar` → `plan`

### p5.js Production Pipeline

- **Nome:** `creative/p5js`
- **Arquivo:** `creative/p5js/SKILL.md`
- **Tamanho:** 27,494 chars
- **Resumo:** p5

p5.js sketches: gen art, shaders, interactive, 3D.

**Relações:**
- `uses` → `ascii-video`
- `uses` → `manim-video`
- `uses` → `excalidraw`
- `similar` → `sketch`

### Popular Web Designs

- **Nome:** `creative/popular-web-designs`
- **Arquivo:** `creative/popular-web-designs/SKILL.md`
- **Tamanho:** 9,722 chars
- **Resumo:** 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS

54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.

**Relações:**
- `similar` → `airtable`
- `similar` → `maps`
- `similar` → `opencode`
- `similar` → `notion`

### Pretext Creative Demos

- **Nome:** `creative/pretext`
- **Arquivo:** `creative/pretext/SKILL.md`
- **Tamanho:** 14,168 chars
- **Resumo:** Use when building creative browser demos with @chenglou/pretext — DOM-free text layout ...

Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art. Produces single-file HTML demos by default.

**Relações:**
- `uses` → `p5js`
- `uses` → `claude-design`
- `uses` → `excalidraw`
- `uses` → `architecture-diagram`
- `similar` → `p5js`

### Sketch

- **Nome:** `creative/sketch`
- **Arquivo:** `creative/sketch/SKILL.md`
- **Tamanho:** 9,304 chars
- **Resumo:** Throwaway HTML mockups: 2-3 design variants to compare

Throwaway HTML mockups: 2-3 design variants to compare.

**Relações:**
- `uses` → `spike`
- `uses` → `claude-design`
- `uses` → `popular-web-designs`
- `uses` → `excalidraw`
- `similar` → `excalidraw`
- `similar` → `spike`

### Songwriting & AI Music Generation

- **Nome:** `creative/songwriting-and-ai-music`
- **Arquivo:** `creative/songwriting-and-ai-music/SKILL.md`
- **Tamanho:** 10,206 chars
- **Resumo:** Songwriting craft and Suno AI music prompts

Songwriting craft and Suno AI music prompts.

### Style Guide Consultation

- **Nome:** `creative/style-guide-consultation`
- **Arquivo:** `creative/style-guide-consultation/SKILL.md`
- **Tamanho:** 5,729 chars
- **Resumo:** Catálogo e consulta de guias de estilo: Hermes Agent (padrão), ID Consultoria, IAF Comu...

Catálogo e consulta de guias de estilo: Hermes Agent (padrão), ID Consultoria, IAF Comunidade, IAF Newsletter. Carrega o guia correto para qualquer tarefa visual.

**Relações:**
- `similar` → `agy`

### TouchDesigner Integration (twozero MCP)

- **Nome:** `creative/touchdesigner-mcp`
- **Arquivo:** `creative/touchdesigner-mcp/SKILL.md`
- **Tamanho:** 15,429 chars
- **Resumo:** Control a running TouchDesigner instance via twozero MCP — create operators, set parame...

Control a running TouchDesigner instance via twozero MCP — create operators, set parameters, wire connections, execute Python, build real-time visuals. 36 native tools.

**Relações:**
- `uses` → `ascii-video`
- `uses` → `manim-video`


## Data Science

### Jupyter Live Kernel (hamelnb)

- **Nome:** `data-science/jupyter-live-kernel`
- **Arquivo:** `data-science/jupyter-live-kernel/SKILL.md`
- **Tamanho:** 5,285 chars
- **Resumo:** Iterative Python via live Jupyter kernel (hamelnb)

Iterative Python via live Jupyter kernel (hamelnb).


## Dogfood

### Dogfood: Systematic Web Application QA Testing

- **Nome:** `dogfood`
- **Arquivo:** `dogfood/SKILL.md`
- **Tamanho:** 9,269 chars
- **Resumo:** Exploratory QA of web apps: find bugs, evidence, reports

Exploratory QA of web apps: find bugs, evidence, reports.

**Relações:**
- `similar` → `plan`


## Email

### Himalaya Email CLI

- **Nome:** `email/himalaya`
- **Arquivo:** `email/himalaya/SKILL.md`
- **Tamanho:** 7,164 chars
- **Resumo:** Himalaya CLI: IMAP/SMTP email from terminal

Himalaya CLI: IMAP/SMTP email from terminal.


## Github

### Codebase Inspection & Architecture Diagnostic

- **Nome:** `github/codebase-inspection`
- **Arquivo:** `github/codebase-inspection/SKILL.md`
- **Tamanho:** 9,747 chars
- **Resumo:** Multi-layered codebase diagnostics: structural mapping, module analysis, dependency aud...

Multi-layered codebase diagnostics: structural mapping, module analysis, dependency audit, git history, quantitative metrics, and critical health reports.

**Relações:**
- `uses` → `github-repo-management`
- `uses` → `github-code-review`

### GitHub Authentication Setup

- **Nome:** `github/github-auth`
- **Arquivo:** `github/github-auth/SKILL.md`
- **Tamanho:** 10,190 chars
- **Resumo:** GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login

GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login.

**Relações:**
- `uses` → `github-pr-workflow`
- `uses` → `github-code-review`
- `uses` → `github-issues`
- `uses` → `github-repo-management`

### GitHub Code Review

- **Nome:** `github/github-code-review`
- **Arquivo:** `github/github-code-review/SKILL.md`
- **Tamanho:** 13,565 chars
- **Resumo:** Review PRs: diffs, inline comments via gh or REST

Review PRs: diffs, inline comments via gh or REST.

**Relações:**
- `uses` → `github-auth`
- `uses` → `github-pr-workflow`

### GitHub Issues Management

- **Nome:** `github/github-issues`
- **Arquivo:** `github/github-issues/SKILL.md`
- **Tamanho:** 9,265 chars
- **Resumo:** Create, triage, label, assign GitHub issues via gh or REST

Create, triage, label, assign GitHub issues via gh or REST.

**Relações:**
- `uses` → `github-auth`
- `uses` → `github-pr-workflow`

### GitHub Pull Request Workflow

- **Nome:** `github/github-pr-workflow`
- **Arquivo:** `github/github-pr-workflow/SKILL.md`
- **Tamanho:** 26,249 chars
- **Resumo:** GitHub PR lifecycle: branch, commit, open, CI, merge

GitHub PR lifecycle: branch, commit, open, CI, merge.

**Relações:**
- `uses` → `github-auth`
- `uses` → `github-code-review`

### GitHub Repository Management

- **Nome:** `github/github-repo-management`
- **Arquivo:** `github/github-repo-management/SKILL.md`
- **Tamanho:** 16,758 chars
- **Resumo:** Clone/create/fork repos; manage remotes, releases

Clone/create/fork repos; manage remotes, releases.

**Relações:**
- `uses` → `github-auth`
- `uses` → `github-pr-workflow`
- `uses` → `github-issues`


## Infrastructure

### AI Voice Selfhost — TTS no Oracle ARM64

- **Nome:** `infrastructure/ai-voice-selfhost`
- **Arquivo:** `infrastructure/ai-voice-selfhost/SKILL.md`
- **Tamanho:** 30,160 chars
- **Resumo:** Self-host AI voice/TTS models (OmniVoice, Qwen3-TTS, Fish Speech S2 Pro GGUF) on Oracle...

Self-host AI voice/TTS models (OmniVoice, Qwen3-TTS, Fish Speech S2 Pro GGUF) on Oracle ARM64 server with Docker. Covers Python inference wrappers (Pattern A) and C++ native inference via subprocess (Pattern B, with s2.cpp). Includes OpenAI-compatible endpoint design, Hermes TTS command provider integration, GGUF quantized model deployment, ARM64 PyTorch pitfalls, voice steering strategies, and GPU acceleration research.

**Relações:**
- `similar` → `plan`

### Deployment Pipeline — Docker + GitHub Actions + SSH Deploy

- **Nome:** `infrastructure/deployment-pipeline`
- **Arquivo:** `infrastructure/deployment-pipeline/SKILL.md`
- **Tamanho:** 45,584 chars
- **Resumo:** CI/CD pipeline for Docker-based apps: GitHub Actions → ghcr

CI/CD pipeline for Docker-based apps: GitHub Actions → ghcr.io → SSH deploy to bare metal. Covers workflow design, registry auth, tag strategy, deploy key setup, migration management, and common pitfalls.

**Relações:**
- `uses` → `github-pr-workflow`
- `uses` → `github-auth`
- `uses` → `oracle-host-access`

### Oracle VM — SSH Access from Hermes Container

- **Nome:** `infrastructure/oracle-host-access`
- **Arquivo:** `infrastructure/oracle-host-access/SKILL.md`
- **Tamanho:** 35,840 chars
- **Resumo:** SSH access from a Hermes Docker container to its Oracle Linux host

SSH access from a Hermes Docker container to its Oracle Linux host. Covers key setup, SSH config quirks, Docker host discovery, and host diagnostics.

**Relações:**
- `similar` → `agy`

### Vercel Deploy — Skill

- **Nome:** `infrastructure/vercel-deploy`
- **Arquivo:** `infrastructure/vercel-deploy/SKILL.md`
- **Tamanho:** 19,814 chars
- **Resumo:** Deploy static sites and frontend apps to Vercel — from zero to production

Deploy static sites and frontend apps to Vercel — from zero to production. Covers CLI install, device-flow authentication, project creation, deploy, custom domains, env vars, and common pitfalls. Works in restricted environments (no root, npm global install with custom prefix).


## Media

### HyperFrames Video Production

- **Nome:** `media/hyperframes-video-production`
- **Arquivo:** `media/hyperframes-video-production/SKILL.md`
- **Tamanho:** 11,345 chars
- **Resumo:** **Engine:** HyperFrames v0

**Engine:** HyperFrames v0.6.79 (HTML → deterministic MP4) **Deps:** Node.js 22+, FFmpeg, `npx hyperframes` **Style default:** Hermes Style Guide (Amber, Blue & Dither) adapted for video node --version          # needs 22+ ffmpeg -version         # needs ffmpeg npx hyperframes --version  # should pr

**Relações:**
- `similar` → `plan`

### YouTube Content Tool

- **Nome:** `media/youtube-content`
- **Arquivo:** `media/youtube-content/SKILL.md`
- **Tamanho:** 3,218 chars
- **Resumo:** YouTube transcripts to summaries, threads, blogs

YouTube transcripts to summaries, threads, blogs.


## Messaging Platforms

### WhatsApp Bridge (Baileys)

- **Nome:** `messaging-platforms/whatsapp-bridge-baileys`
- **Arquivo:** `messaging-platforms/whatsapp-bridge-baileys/SKILL.md`
- **Tamanho:** 5,281 chars
- **Resumo:** Operações no WhatsApp bridge baileys — enviar mensagens para grupos, descobrir IDs de g...

Operações no WhatsApp bridge baileys — enviar mensagens para grupos, descobrir IDs de grupos, consultar metadados, gerenciar envio de mídia. Bridge HTTP local na porta 3000, socket baileys via @whiskeysockets/baileys.


## Mlops

### lm-evaluation-harness - LLM Benchmarking

- **Nome:** `mlops/evaluation/lm-evaluation-harness`
- **Arquivo:** `mlops/evaluation/lm-evaluation-harness/SKILL.md`
- **Tamanho:** 12,020 chars
- **Resumo:** lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc

lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.).

**Relações:**
- `uses` → `vllm`

### Weights & Biases: ML Experiment Tracking & MLOps

- **Nome:** `mlops/evaluation/weights-and-biases`
- **Arquivo:** `mlops/evaluation/weights-and-biases/SKILL.md`
- **Tamanho:** 12,395 chars
- **Resumo:** W&B: log ML experiments, sweeps, model registry, dashboards

W&B: log ML experiments, sweeps, model registry, dashboards.

### Hugging Face CLI (`hf`) Reference Guide

- **Nome:** `mlops/huggingface-hub`
- **Arquivo:** `mlops/huggingface-hub/SKILL.md`
- **Tamanho:** 3,674 chars
- **Resumo:** HuggingFace hf CLI: search/download/upload models, datasets

HuggingFace hf CLI: search/download/upload models, datasets.

### llama.cpp + GGUF

- **Nome:** `mlops/inference/llama-cpp`
- **Arquivo:** `mlops/inference/llama-cpp/SKILL.md`
- **Tamanho:** 8,880 chars
- **Resumo:** llama

llama.cpp local GGUF inference + HF Hub model discovery.

### vLLM - High-Performance LLM Serving

- **Nome:** `mlops/inference/vllm`
- **Arquivo:** `mlops/inference/vllm/SKILL.md`
- **Tamanho:** 9,071 chars
- **Resumo:** vLLM: high-throughput LLM serving, OpenAI API, quantization

vLLM: high-throughput LLM serving, OpenAI API, quantization.

### Pi Agent Session Audit

- **Nome:** `mlops/pi-session-audit`
- **Arquivo:** `mlops/pi-session-audit/SKILL.md`
- **Tamanho:** 13,878 chars
- **Resumo:** Extrair métricas reais de uso das sessões do Pi Agent a partir dos arquivos

Extrair métricas reais de uso das sessões do Pi Agent a partir dos arquivos .jsonl ~/.pi/agent/sessions/--<path-normalizado>--/<timestamp>_<uuid>.jsonl Onde `<path-normalizado>` é o diretório de trabalho com `/` substituído por `-`. Ex: `--opt-data-code-workstation-taskflow--` Cada linha é um JSON. 

**Relações:**
- `similar` → `agy`


## Note Taking

### Obsidian Vault

- **Nome:** `note-taking/obsidian`
- **Arquivo:** `note-taking/obsidian/SKILL.md`
- **Tamanho:** 2,919 chars
- **Resumo:** Read, search, create, and edit notes in the Obsidian vault

Read, search, create, and edit notes in the Obsidian vault.


## Productivity

### Airtable — Bases, Tables & Records

- **Nome:** `productivity/airtable`
- **Arquivo:** `productivity/airtable/SKILL.md`
- **Tamanho:** 11,302 chars
- **Resumo:** Airtable REST API via curl

Airtable REST API via curl. Records CRUD, filters, upserts.

### Google Workspace

- **Nome:** `productivity/google-workspace`
- **Arquivo:** `productivity/google-workspace/SKILL.md`
- **Tamanho:** 16,272 chars
- **Resumo:** Google OAuth2 client credentials (downloaded from Google Cloud Console)

Google OAuth2 client credentials (downloaded from Google Cloud Console)

**Relações:**
- `uses` → `himalaya`
- `similar` → `himalaya`

### HTML Report — Hermes Design System

- **Nome:** `productivity/html-report-hermes`
- **Arquivo:** `productivity/html-report-hermes/SKILL.md`
- **Tamanho:** 15,051 chars
- **Resumo:** Render dense research reports, analyses, and data summaries as beautiful standalone HTM...

Render dense research reports, analyses, and data summaries as beautiful standalone HTML using the Hermes CRT Design System (amber/blue inversion, terminal aesthetic, serif + monospace typography, scanlines + vignette overlays). Activates automatically whenever the user needs a visual-rich response — HTML landing pages, dashboards, comparative analysis, benchmarks, documentation, or any report that would benefit from structured visual presentation.

**Relações:**
- `similar` → `agy`

### HTML → PDF com Chromium Headless

- **Nome:** `productivity/html-to-pdf-chromium`
- **Arquivo:** `productivity/html-to-pdf-chromium/SKILL.md`
- **Tamanho:** 5,924 chars
- **Resumo:** Convert HTML files to high-fidelity PDF using Chromium headless (via Debian

Convert HTML files to high-fidelity PDF using Chromium headless (via Debian .deb extraction, no root or Playwright required). Use when weasyprint or other tools lose CSS features like gradients, webkit-background-clip, grid, and glow effects.

**Relações:**
- `similar` → `agy`

### Maps Skill

- **Nome:** `productivity/maps`
- **Arquivo:** `productivity/maps/SKILL.md`
- **Tamanho:** 6,726 chars
- **Resumo:** Geocode, POIs, routes, timezones via OpenStreetMap/OSRM

Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.

### nano-pdf

- **Nome:** `productivity/nano-pdf`
- **Arquivo:** `productivity/nano-pdf/SKILL.md`
- **Tamanho:** 1,414 chars
- **Resumo:** Edit PDF text/typos/titles via nano-pdf CLI (NL prompts)

Edit PDF text/typos/titles via nano-pdf CLI (NL prompts).

### Notion

- **Nome:** `productivity/notion`
- **Arquivo:** `productivity/notion/SKILL.md`
- **Tamanho:** 15,359 chars
- **Resumo:** Notion API + ntn CLI: pages, databases, markdown, Workers

Notion API + ntn CLI: pages, databases, markdown, Workers.

**Relações:**
- `uses` → `plan`

### PDF & Document Extraction

- **Nome:** `productivity/ocr-and-documents`
- **Arquivo:** `productivity/ocr-and-documents/SKILL.md`
- **Tamanho:** 5,280 chars
- **Resumo:** Extract text from PDFs/scans (pymupdf, marker-pdf)

Extract text from PDFs/scans (pymupdf, marker-pdf).

**Relações:**
- `uses` → `powerpoint`
- `similar` → `powerpoint`
- `uses` → `arxiv`

### Powerpoint Skill

- **Nome:** `productivity/powerpoint`
- **Arquivo:** `productivity/powerpoint/SKILL.md`
- **Tamanho:** 9,298 chars
- **Resumo:** Create, read, edit

Create, read, edit .pptx decks, slides, notes, templates.

**Relações:**
- `similar` → `plan`

### Relatório de Custos — Skill de Geração

- **Nome:** `productivity/relatorio-de-custos`
- **Arquivo:** `productivity/relatorio-de-custos/SKILL.md`
- **Tamanho:** 9,688 chars
- **Resumo:** Gera relatórios técnicos de custos com dados reais de tokens de todos os agentes

Gera relatórios técnicos de custos com dados reais de tokens de todos os agentes. Usuário pede relatório de custos do projeto X, breakdown de gastos, quanto custou o MVP. sqlite3 /opt/data/state.db " SELECT id, title, source, model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,

**Relações:**
- `similar` → `agy`

### TaskFlow MCP — Ferramentas e Workflows

- **Nome:** `productivity/taskflow-mcp`
- **Arquivo:** `productivity/taskflow-mcp/SKILL.md`
- **Tamanho:** 4,485 chars
- **Resumo:** TaskFlow é um sistema GTD de gerenciamento de tarefas exposto via MCP (Model Context Pr...

TaskFlow é um sistema GTD de gerenciamento de tarefas exposto via MCP (Model Context Protocol). Conecta-se via SSE (StreamableHTTP POST não funciona — SSE deve ser explícito). Transport: SSE (StreamableHTTP POST padrão do Hermes não funciona) URL:       http://172.19.0.1/mcp/sse Messages:  http://17

### Teams Meeting Pipeline

- **Nome:** `productivity/teams-meeting-pipeline`
- **Arquivo:** `productivity/teams-meeting-pipeline/SKILL.md`
- **Tamanho:** 6,867 chars
- **Resumo:** Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect...

Operate the Teams meeting summary pipeline via Hermes CLI — summarize meetings, inspect pipeline status, replay jobs, manage Microsoft Graph subscriptions.


## Read Reddit

### Read Reddit via RSS

- **Nome:** `read-reddit`
- **Arquivo:** `read-reddit/SKILL.md`
- **Tamanho:** 7,130 chars
- **Resumo:** How to read Reddit subreddits reliably using RSS feeds — bypassing API rate limits and ...

How to read Reddit subreddits reliably using RSS feeds — bypassing API rate limits and bot detection. Use this skill whenever you need to fetch content from Reddit for research, curation, or news gathering.


## Research

### arXiv Research

- **Nome:** `research/arxiv`
- **Arquivo:** `research/arxiv/SKILL.md`
- **Tamanho:** 10,085 chars
- **Resumo:** Search arXiv papers by keyword, author, category, or ID

Search arXiv papers by keyword, author, category, or ID.

**Relações:**
- `uses` → `ocr-and-documents`

### Blogwatcher

- **Nome:** `research/blogwatcher`
- **Arquivo:** `research/blogwatcher/SKILL.md`
- **Tamanho:** 5,111 chars
- **Resumo:** Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool

Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.

### Deep Research Skill

- **Nome:** `research/deep-research`
- **Arquivo:** `research/deep-research/SKILL.md`
- **Tamanho:** 33,335 chars
- **Resumo:** 基于 GPT-Researcher 架构，适配 Hermes delegate_task 的多 agent 深度调研流水线

基于 GPT-Researcher 架构，适配 Hermes delegate_task 的多 agent 深度调研流水线。 用户问题 │ ▼ [Phase 0] 问题分析 & 子问题分解 (Hermes 自身) │ ▼ [Phase 1] 并行调研 agents (delegate_task batch, 4 agents) │         ├─ Web 调研 agent │         ├─ GitHub/代码 调研 agent │         ├─ 新闻/时事 调研 agent │         └─ 学术/论文 调研 agent │ ▼ [Phase 2] 并行审核 ag

**Relações:**
- `similar` → `plan`
- `similar` → `arxiv`

### Karpathy's LLM Wiki

- **Nome:** `research/llm-wiki`
- **Arquivo:** `research/llm-wiki/SKILL.md`
- **Tamanho:** 20,113 chars
- **Resumo:** Karpathy's LLM Wiki: build/query interlinked markdown KB

Karpathy's LLM Wiki: build/query interlinked markdown KB.

**Relações:**
- `uses` → `obsidian`
- `uses` → `arxiv`
- `similar` → `obsidian`

### Polymarket — Prediction Market Data

- **Nome:** `research/polymarket`
- **Arquivo:** `research/polymarket/SKILL.md`
- **Tamanho:** 2,985 chars
- **Resumo:** Query Polymarket: markets, prices, orderbooks, history

Query Polymarket: markets, prices, orderbooks, history.

### Research Paper Writing Pipeline

- **Nome:** `research/research-paper-writing`
- **Arquivo:** `research/research-paper-writing/SKILL.md`
- **Tamanho:** 103,375 chars
- **Resumo:** Write ML papers for NeurIPS/ICML/ICLR: design→submit

Write ML papers for NeurIPS/ICML/ICLR: design→submit.

**Relações:**
- `uses` → `arxiv`
- `uses` → `plan`
- `similar` → `plan`
- `similar` → `powerpoint`
- `similar` → `excalidraw`
- `similar` → `arxiv`

### Tech Trend Discovery

- **Nome:** `research/tech-trend-discovery`
- **Arquivo:** `research/tech-trend-discovery/SKILL.md`
- **Tamanho:** 15,028 chars
- **Resumo:** Discover what the tech/AI community is discussing right now — trending topics, hot disc...

Discover what the tech/AI community is discussing right now — trending topics, hot discussions, and breaking conversations. Covers Reddit alternatives and HN Algolia API as primary sources when traditional search tools fail.

### User Interview

- **Nome:** `research/user-interview`
- **Arquivo:** `research/user-interview/SKILL.md`
- **Tamanho:** 9,161 chars
- **Resumo:** **Core principle:** A good interview is a conversation, not a questionnaire

**Core principle:** A good interview is a conversation, not a questionnaire. The best insights come from what users *don't* say — hesitation, emotion, workarounds, and the stories they tell. - During the Research phase (Fase 2) of the product pipeline - Understanding user needs, pain points, and beh


## Social Media

### Brand IAF — Conteúdo

- **Nome:** `social-media/brand-iaf-conteudo`
- **Arquivo:** `social-media/brand-iaf-conteudo/SKILL.md`
- **Tamanho:** 5,276 chars
- **Resumo:** Skill de conteúdo da comunidade IA que Funciona (IAF)

Skill de conteúdo da comunidade IA que Funciona (IAF). Contém constantes de marca, voz, tom, paleta, tipografia, regras de idioma e templates de conteúdo. Use para gerar qualquer texto da comunidade — newsletter diária, posts, discussões, boas-vindas.

### xurl — X (Twitter) API via the Official CLI

- **Nome:** `social-media/xurl`
- **Arquivo:** `social-media/xurl/SKILL.md`
- **Tamanho:** 15,518 chars
- **Resumo:** X/Twitter via xurl CLI: post, search, DM, media, v2 API

X/Twitter via xurl CLI: post, search, DM, media, v2 API.

**Relações:**
- `similar` → `plan`


## Software Development

### agy — Antigravity CLI (Consultor Externo)

- **Nome:** `software-development/agy`
- **Arquivo:** `software-development/agy/SKILL.md`
- **Tamanho:** 8,099 chars
- **Resumo:** Google Antigravity CLI (agy) — instalação, autenticação OAuth via tmux, e workflows de ...

Google Antigravity CLI (agy) — instalação, autenticação OAuth via tmux, e workflows de design (image generation, prototipagem, subagentes paralelos, HTML reports).

### Backlog & Sprint

- **Nome:** `software-development/backlog-and-sprint`
- **Arquivo:** `software-development/backlog-and-sprint/SKILL.md`
- **Tamanho:** 78,483 chars
- **Resumo:** **Agente:** Hermes (orquestrador) + Pi best + Antigravity **Local da backlog:** `workst...

**Agente:** Hermes (orquestrador) + Pi best + Antigravity **Local da backlog:** `workstation/<projeto>/product/backlog.md` **Workstation (rw para Hermes e Pi):** `/opt/data/code/workstation/` = `/workspace/code/workstation/` Usuário dá feedback │ ▼ ┌──────────────┐ │   Backlog    │ ← Hermes adiciona

**Relações:**
- `similar` → `plan`
- `similar` → `agy`
- `similar` → `opencode`

### Code Tasks

- **Nome:** `software-development/code-tasks`
- **Arquivo:** `software-development/code-tasks/SKILL.md`
- **Tamanho:** 8,258 chars
- **Resumo:** **Core principle:** Every task should be completable in 2-15 minutes by a competent dev...

**Core principle:** Every task should be completable in 2-15 minutes by a competent developer. If a task takes longer, it's not small enough — split it. - After engineering docs (SAD, TechSpecs, ERD, API contracts) are approved - Before writing any implementation code - During the MVP build phase (F

**Relações:**
- `similar` → `plan`

### Authoring Hermes-Agent Skills (in-repo)

- **Nome:** `software-development/hermes-agent-skill-authoring`
- **Arquivo:** `software-development/hermes-agent-skill-authoring/SKILL.md`
- **Tamanho:** 7,609 chars
- **Resumo:** Author in-repo SKILL

Author in-repo SKILL.md: frontmatter, validator, structure.

**Relações:**
- `uses` → `plan`
- `uses` → `dogfood`

### Ideation Drilling (Hermes — Orchestrator)

- **Nome:** `software-development/ideation-drilling`
- **Arquivo:** `software-development/ideation-drilling/SKILL.md`
- **Tamanho:** 14,550 chars
- **Resumo:** Skill orquestradora

Skill orquestradora. Chama o Pi Agent com `/skill:ideation-drilling` para conduzir a fase de ideação, gerencia o projeto, e captura o resultado. - O usuário diz: "Tenho uma ideia para um produto/feature" - O usuário pede: "Me ajude a refinar essa ideia" - Início do pipeline de produto (Fase 1) - A b

**Relações:**
- `similar` → `opencode`

### Node.js Inspect Debugger

- **Nome:** `software-development/node-inspect-debugger`
- **Arquivo:** `software-development/node-inspect-debugger/SKILL.md`
- **Tamanho:** 10,929 chars
- **Resumo:** Debug Node

Debug Node.js via --inspect + Chrome DevTools Protocol CLI.

**Relações:**
- `uses` → `systematic-debugging`
- `uses` → `python-debugpy`
- `similar` → `maps`

### Plan Mode

- **Nome:** `software-development/plan`
- **Arquivo:** `software-development/plan/SKILL.md`
- **Tamanho:** 11,315 chars
- **Resumo:** Plan mode: write an actionable markdown plan to

Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code.

**Relações:**
- `uses` → `test-driven-development`

### Python Debugger (pdb + debugpy)

- **Nome:** `software-development/python-debugpy`
- **Arquivo:** `software-development/python-debugpy/SKILL.md`
- **Tamanho:** 13,172 chars
- **Resumo:** Debug Python: pdb REPL + debugpy remote (DAP)

Debug Python: pdb REPL + debugpy remote (DAP).

**Relações:**
- `uses` → `systematic-debugging`
- `uses` → `node-inspect-debugger`

### Skill Curation — Discover, Evaluate & Install Hermes Skills

- **Nome:** `software-development/skill-curation`
- **Arquivo:** `software-development/skill-curation/SKILL.md`
- **Tamanho:** 10,756 chars
- **Resumo:** Hermes Agent has a rich ecosystem of **70+ bundled skills** and **hundreds of community...

Hermes Agent has a rich ecosystem of **70+ bundled skills** and **hundreds of community skills** across GitHub, HermesHub (`hermeshub.xyz`), Hermes Atlas (`hermesatlas.com`), and the `skills.sh` marketplace. The challenge is not finding skills — it's finding the **right** skill and evaluating whethe

### Skills Repository Curator

- **Nome:** `software-development/skills-repo-curator`
- **Arquivo:** `software-development/skills-repo-curator/SKILL.md`
- **Tamanho:** 6,893 chars
- **Resumo:** Gerencia o repositório git de skills do Hermes — ciclo evolve de consolidação MECE, index

Gerencia o repositório git de skills do Hermes — ciclo evolve de consolidação MECE, index.md/log.md/reports, offload de memória, e manutenção de AGENTS.md. Executa o processo completo de análise, merge, delete, relatório e commit.

### Spike

- **Nome:** `software-development/spike`
- **Arquivo:** `software-development/spike/SKILL.md`
- **Tamanho:** 8,730 chars
- **Resumo:** Throwaway experiments to validate an idea before build

Throwaway experiments to validate an idea before build.

**Relações:**
- `uses` → `sketch`
- `uses` → `plan`
- `similar` → `plan`

### Systematic Debugging

- **Nome:** `software-development/systematic-debugging`
- **Arquivo:** `software-development/systematic-debugging/SKILL.md`
- **Tamanho:** 11,444 chars
- **Resumo:** 4-phase root cause debugging: understand bugs before fixing

4-phase root cause debugging: understand bugs before fixing.

**Relações:**
- `uses` → `test-driven-development`
- `uses` → `plan`

### Test-Driven Development (TDD)

- **Nome:** `software-development/test-driven-development`
- **Arquivo:** `software-development/test-driven-development/SKILL.md`
- **Tamanho:** 9,810 chars
- **Resumo:** TDD: enforce RED-GREEN-REFACTOR, tests before code

TDD: enforce RED-GREEN-REFACTOR, tests before code.

**Relações:**
- `uses` → `systematic-debugging`
- `uses` → `plan`


## Yuanbao

### Yuanbao Group Interaction

- **Nome:** `yuanbao`
- **Arquivo:** `yuanbao/SKILL.md`
- **Tamanho:** 3,795 chars
- **Resumo:** Yuanbao (元宝) groups: @mention users, query info/members

Yuanbao (元宝) groups: @mention users, query info/members.
