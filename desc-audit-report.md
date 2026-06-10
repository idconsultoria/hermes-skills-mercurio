# Description Conformity Audit Report

**Date:** 2026-06-10
**Total skills scanned:** 83
**Conformant skills:** 20
**Non-conformant skills:** 63

---

## Criteria

1. **One-liner summary (~80 chars max, ≤85):** Concise, self-contained description of what the skill does. NO truncation markers (no `...`).
2. **Descriptive paragraph:** Explains activation triggers, expands capabilities, tools used, and what it produces.

---

## Conformant Skills (20)

These skills have a proper one-liner (≤85 chars) followed by a descriptive paragraph:

- ai-voice-selfhost
- autonomous-ai-agents
- backlog-and-sprint
- brand-iaf-conteudo
- brand-studio-forge
- claude-design
- comfyui
- hyperframes-video-production
- ideation-drilling
- oracle-host-access
- plan
- polymarket
- product-pipeline
- read-reddit
- relatorio-de-custos
- skill-curation
- style-guide-consultation
- user-interview
- vercel-deploy

---

## Non-Conformant Skills (63)

### Type A: One-liner too long (>85 chars)

| # | Skill | Problem | Old Description |
|---|-------|---------|-----------------|
| 1 | **skills-repo-curator** | Single blob, no clear one-liner (217 chars) | "Gerencia o repositório git de skills do Hermes — ciclo evolve de consolidação MECE, index.md/log.md/reports, offload de memória, e manutenção de AGENTS.md. Executa o processo completo de análise, merge, delete, relatório e commit." |
| 2 | **text-to-speech** | One-liner too long (111 chars) | "Umbrella skill for TTS: voice design, Gemini prompting, multi-provider fallback, self-hosted Fish Speech, and Hermes TTS provider. Full lifecycle from persona to audio." |
| 3 | **whatsapp-bridge-baileys** | One-liner too long (87 chars) | "Send messages, discover group IDs, and manage media via local WhatsApp Baileys bridge.\n\nLocal Node.js HTTP bridge..." |
| 4 | **copywriting** | One-liner too long (113 chars) | "Expert conversion copywriting: write, rewrite, or improve marketing copy — headlines, CTAs, value props, page sections.\n\nLoad this skill when..." |
| 5 | **iaf-newsletter-pipeline** | One-liner too long (123 chars) | "Umbrella skill for newsletter/briefing/digest pipelines: IAF Manhã Aumentada, Daily AI Digest, editorial curation, cron scheduling. Covers multi-source collection, ranking, HTML→PDF, delivery." |
| 6 | **messaging-platforms** | One-liner too long (110 chars) | "Hermes cross-platform messaging: platform quirks, JID/ID formats, bridge workarounds for Telegram, WhatsApp, more." |
| 7 | **deep-research** | One-liner too long (101 chars) | "Multi-agent deep research pipeline: decompose topics, dispatch parallel agents, review, cross-validate, synthesize.\n\nInspired by GPT-Researcher..." |
| 8 | **tech-trend-discovery** | One-liner too long (112 chars) | "Discover what the tech/AI community is discussing right now — trending topics, hot discussions, and breaking conversations. Covers Reddit alternatives and HN Algolia API..." |
| 9 | **pi-agent-coordination** | One-liner too long (101 chars) | "Invoke Pi Agent locally from Hermes: provider/model hierarchy, session recovery, stall detection, fallback patterns.\n\nComprehensive reference..." |
| 10 | **pi-session-audit** | One-liner too long (99 chars) | "Auditar sessões do Pi Agent: extrair duração, tokens, custo e modelo dos arquivos .jsonl de sessão. Script de extração e cálculo de custo por provider." |
| 11 | **taskflow-mcp** | No clear one-liner (157 chars blob) | "Interact with the TaskFlow MCP server via Hermes Agent — SSE transport setup, full tool catalog, 2-step confirmation flow, context UUID requirements, NLP quick-add workflows, GTD pipeline." |
| 12 | **html-to-pdf-chromium** | One-liner too long (118 chars) | "Convert HTML files to high-fidelity PDF using Chromium headless (via Debian .deb extraction, no root or Playwright required). Use when weasyprint..." |
| 13 | **macos-computer-use** | One-liner too long (107 chars) | "Drive macOS desktop in background — screenshots, mouse, keyboard, scroll, drag — without stealing cursor, focus, or Space. Works with any model. Load when computer_use tool is available." |
| 14 | **pretext** | One-liner too long (139 chars) | "Creative browser demos with @chenglou/pretext: DOM-free text layout for ASCII art, kinetic typography, text-as-geometry games, and generative art. Single-file HTML output." |
| 15 | **codebase-inspection** | One-liner too long (107 chars) | "Multi-layered codebase diagnostics: structural mapping, dependency audit, git history, metrics, and health reports." |
| 16 | **html-report-hermes** | One-liner too long (93 chars) | "Render research reports as dark-themed HTML with SVG charts and Tufte-inspired typography.\n\nTwo design systems in one skill..." |
| 17 | **systematic-debugging** | One-liner too long (89 chars) | "4-phase root cause debugging — methodology + Python (pdb/debugpy) + Node.js (--inspect). Understand bugs before fixing." |
| 18 | **agy** | No clear one-liner (164 chars blob) | "Google Antigravity CLI (agy) — instalação, autenticação OAuth via tmux, e workflows de design (image generation, prototipagem, subagentes paralelos, HTML reports)." |
| 19 | **deployment-pipeline** | One-liner too long (87 chars) | "CI/CD pipeline for Docker-based apps: GitHub Actions → ghcr.io → SSH deploy to bare metal. Covers workflow design, registry auth, tag strategy, deploy key setup, migration management, and common pitfalls." |

### Type B: Only a one-liner, no descriptive paragraph

| # | Skill | One-liner |
|---|-------|-----------|
| 20 | **spike** | "Throwaway experiments to validate an idea before build." |
| 21 | **xurl** | "X/Twitter via xurl CLI: post, search, DM, media, v2 API." |
| 22 | **blogwatcher** | "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool." |
| 23 | **jupyter-live-kernel** | "Iterative Python via live Jupyter kernel (hamelnb)." |
| 24 | **himalaya** | "Himalaya CLI: IMAP/SMTP email from terminal." |
| 25 | **maps** | "Geocode, POIs, routes, timezones via OpenStreetMap/OSRM." |
| 26 | **findmy** | "Track Apple devices/AirTags via FindMy.app on macOS." |
| 27 | **powerpoint** | "Create, read, edit .pptx decks, slides, notes, templates." |
| 28 | **ocr-and-documents** | "Extract text from PDFs/scans (pymupdf, marker-pdf)." |
| 29 | **apple-reminders** | "Apple Reminders via remindctl: add, list, complete." |
| 30 | **nano-pdf** | "Edit PDF text/typos/titles via nano-pdf CLI (NL prompts)." |
| 31 | **google-workspace** | "Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python." |
| 32 | **airtable** | "Airtable REST API via curl. Records CRUD, filters, upserts." |
| 33 | **notion** | "Notion API + ntn CLI: pages, databases, markdown, Workers." |
| 34 | **github-pr-workflow** | "GitHub PR lifecycle: branch, commit, open, CI, merge." |
| 35 | **ascii-art** | "ASCII art: pyfiglet, cowsay, boxes, image-to-ascii." |
| 36 | **humanizer** | "Humanize text: strip AI-isms and add real voice." |
| 37 | **github-repo-management** | "Clone/create/fork repos; manage remotes, releases." |
| 38 | **hermes-agent** | "Configure, extend, or contribute to Hermes Agent." |
| 39 | **github-auth** | "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login." |
| 40 | **arxiv** | "Search arXiv papers by keyword, author, category, or ID." |
| 41 | **research-paper-writing** | "Write ML papers for NeurIPS/ICML/ICLR: design→submit." |
| 42 | **llm-wiki** | "Karpathy's LLM Wiki: build/query interlinked markdown KB." |
| 43 | **obsidian** | "Read, search, create, and edit notes in the Obsidian vault." |
| 44 | **serving-llms-vllm** | "vLLM: high-throughput LLM serving, OpenAI API, quantization." |
| 45 | **llama-cpp** | "llama.cpp local GGUF inference + HF Hub model discovery." |
| 46 | **weights-and-biases** | "W&B: log ML experiments, sweeps, model registry, dashboards." |
| 47 | **evaluating-llms-harness** | "lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.)." |
| 48 | **huggingface-hub** | "HuggingFace hf CLI: search/download/upload models, datasets." |
| 49 | **github-code-review** | "Review PRs: diffs, inline comments via gh or REST." |
| 50 | **github-issues** | "Create, triage, label, assign GitHub issues via gh or REST." |
| 51 | **imessage** | "Send and receive iMessages/SMS via the imsg CLI on macOS." |
| 52 | **apple-notes** | "Manage Apple Notes via memo CLI: create, search, edit." |
| 53 | **youtube-content** | "YouTube transcripts to summaries, threads, blogs." |
| 54 | **p5js** | "p5.js sketches: gen art, shaders, interactive, 3D." |
| 55 | **architecture-diagram** | "Dark-themed SVG architecture/cloud/infra diagrams as HTML." |
| 56 | **baoyu-infographic** | "Infographics: 21 layouts x 21 styles (信息图, 可视化)." |
| 57 | **ascii-video** | "ASCII video: convert video/audio to colored ASCII MP4/GIF." |
| 58 | **songwriting-and-ai-music** | "Songwriting craft and Suno AI music prompts." |
| 59 | **excalidraw** | "Hand-drawn Excalidraw JSON diagrams (arch, flow, seq)." |
| 60 | **popular-web-designs** | "54 real design systems (Stripe, Linear, Vercel) as HTML/CSS." |
| 61 | **manim-video** | "Manim CE animations: 3Blue1Brown math/algo videos." |

### Type C: No proper descriptive paragraph (two-sentence but not descriptive)

| # | Skill | Problem |
|---|-------|---------|
| 62 | **hermes-agent-skill-authoring** | One-liner (80 chars) OK, but second sentence is just merge note |
| 63 | **dogfood** | Single sentence (49 chars), no descriptive paragraph |

---

## Fixes Applied

All 63 non-conformant SKILL.md files were patched with corrected descriptions following the format:
1. One-liner summary (≤85 chars, no `...`)
2. Descriptive paragraph with activation triggers and expanded capabilities

The index.md was also updated for each non-conformant skill.
