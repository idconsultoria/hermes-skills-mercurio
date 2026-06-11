# Relations Report — Batch 1 (28 Skills)

> Proposed depth-1 semantic relations based on shared tools, workflows, domains, and ecosystem overlap.
> Format: `<type>` → `<other-skill>` (reason)
> Only additions proposed; existing relations preserved.

---

## apple/apple-notes
- `similar` → apple/apple-reminders (Both manage Apple productivity data via macOS CLI tools — `memo` and `remindctl` — with iCloud sync and cross-device access)
- `uses` → apple/imessage (iMessage can deliver note content; both part of Apple ecosystem automation on macOS)

## apple/apple-reminders
- `similar` → apple/imessage (Apple ecosystem CLI tools on macOS, both use `brew install` pattern and require System Privacy permissions)
- `uses` → apple/macos-computer-use (Computer Use can automate Reminders.app UI for tasks remindctl cannot handle)
- `uses` → autonomous-ai-agents/hermes-agent (Hermes cron jobs can create reminders as scheduled agent alerts)

## apple/findmy
(Existing: macos-computer-use, maps)
- `similar` → apple/imessage (Both automate Apple native apps via CLI/AppleScript on macOS, share Screen Recording/Privacy permission requirements)
- `uses` → autonomous-ai-agents/hermes-agent (Cron scheduled tracking of AirTags uses Hermes cron subsystem)

## apple/imessage
(Existing: none — needs additions)
- `similar` → autonomous-ai-agents/messaging-platforms (Both handle cross-platform message delivery nuances; iMessage is one of many platforms Hermes gateway supports)
- `similar` → apple/apple-notes (Apple ecosystem CLI tools on macOS with similar `brew` install patterns and Privacy permissions)
- `uses` → apple/macos-computer-use (Computer Use can drive Messages.app for tasks the `imsg` CLI cannot handle, like reading message attachments)

## apple/macos-computer-use
(Existing: browser)
- `used_by` → apple/imessage (Computer Use provides GUI automation fallback for Messages.app)
- `used_by` → apple/findmy (Already listed; also `used_by` → all apple/* skills for macOS GUI automation)
- `similar` → autonomous-ai-agents/hermes-agent (Hermes tools include the `computer_use` tool; this skill documents its canonical usage)

## autonomous-ai-agents/autonomous-ai-agents
(Existing: none — needs additions)
- `similar` → autonomous-ai-agents/pi-agent-coordination (Both orchestrate external AI coding agents — one via Claude Code/Codex/OpenCode, the other via Pi Agent — with shared patterns for delegation, monitoring, and fallback)
- `uses` → autonomous-ai-agents/hermes-agent (Hermes delegates to these coding agents using `delegate_task` and terminal orchestration patterns)
- `similar` → autonomous-ai-agents/product-pipeline (Both involve multi-agent orchestration with task decomposition)

## autonomous-ai-agents/hermes-agent
(Existing: claude-code, codex, opencode)
- `parent` → autonomous-ai-agents/messaging-platforms (Messaging platforms are part of Hermes gateway; this skill documents gateway CLI commands)
- `uses` → autonomous-ai-agents/autonomous-ai-agents (Hermes delegates coding tasks to autonomous agents via the patterns in that skill)
- `parent` → apple/macos-computer-use (Hermes provides the `computer_use` tool that this skill documents)

## autonomous-ai-agents/messaging-platforms
(Existing: whatsapp-bridge-baileys)
- `used_by` → apple/imessage (iMessage is one of the messaging platforms Hermes gateway supports; imsg CLI is a bridge endpoint)
- `used_by` → content-production/text-to-speech (Audio delivery rules per platform are documented here — MEDIA delivery for Telegram, WhatsApp, Discord)
- `used_by` → content-production/iaf-newsletter-pipeline (Newsletter delivery via Telegram and WhatsApp follows these platform-specific rules)

## autonomous-ai-agents/pi-agent-coordination
(Existing: autonomous-ai-agents/pi-session-audit)
- `similar` → autonomous-ai-agents/autonomous-ai-agents (Both are agent orchestration skills — one for Pi Agent, one for Claude Code/Codex/OpenCode — with shared concepts of delegation, session recovery, and model fallback chains)
- `used_by` → autonomous-ai-agents/product-pipeline (Pi Agent is the primary executor in the product pipeline; this skill provides the fundamental invocation patterns)
- `uses` → autonomous-ai-agents/hermes-agent (Pi runs via Hermes terminal; Hermes orchestrates the tiered Pi hierarchy)

## autonomous-ai-agents/pi-session-audit
(Existing: autonomous-ai-agents/pi-agent-coordination)
- `used_by` → autonomous-ai-agents/product-pipeline (Pipeline phases require session audit to extract tokens, cost, and duration after Pi Agent execution)
- `similar` → autonomous-ai-agents/autonomous-ai-agents (Both analyze external agent usage — Pi session JSONL vs Claude Code/Codex session logs)

## autonomous-ai-agents/product-pipeline
(Existing: none — needs additions)
- `uses` → autonomous-ai-agents/pi-agent-coordination (Pi Agent is the primary executor across all pipeline phases — ideation, PM docs, UX/UI, engineering)
- `uses` → creative/brand-studio-forge (Product branding and identity work feeds into the design and management phases)
- `uses` → content-production/text-to-speech (TTS used for voiceover in product demos and announcements)
- `similar` → content-production/iaf-newsletter-pipeline (Both are multi-phase production pipelines with cron scheduling, chained phases, and delivery orchestration)

## content-production/iaf-newsletter-pipeline
(Existing: brand-iaf-conteudo)
- `uses` → creative/humanizer (Pipeline explicitly includes a humanizer pass at the end of editorial synthesis)
- `uses` → creative/copywriting (Editorial curation involves copywriting principles for Portuguese content with zero anglicisms)
- `uses` → content-production/text-to-speech (Audio versions of newsletter content require TTS)
- `uses` → autonomous-ai-agents/hermes-agent (The pipeline runs as chained Hermes cron jobs; this skill documents the cron architecture)

## content-production/text-to-speech
(Existing: hermes-agent)
- `used_by` → creative/ascii-video (ASCII video pipeline has a TTS narration mode that generates narrated testimonial/quote videos)
- `used_by` → creative/manim-video (Manim explainer videos optionally use TTS for voiceover narration)
- `used_by` → content-production/iaf-newsletter-pipeline (Newsletter audio versions use TTS)
- `uses` → autonomous-ai-agents/messaging-platforms (Audio delivery format varies by platform — WAV for WhatsApp, OGG for Telegram — documented in messaging-platforms skill)

## creative/architecture-diagram
(Existing: concept-diagrams, excalidraw)
- `similar` → creative/excalidraw (Both produce diagrams — one as dark SVG HTML, the other as hand-drawn JSON — with overlapping use cases for architecture visualization)
- `similar` → creative/popular-web-designs (Both provide visual design systems — architecture diagrams for infra, popular-web-designs for UI)
- `used_by` → creative/manim-video (Manim has an architecture diagram mode for system topology animations)

## creative/ascii-art
(Existing: ascii-video, creative-coding)
- `similar` → creative/p5js (Both are creative coding skills — ASCII art for terminal-based text art, p5js for browser-based generative art)
- `used_by` → creative/pretext (Pretext ASCII obstacle typography pattern uses measured ASCII masks made of character art)
- `used_by` → creative/ascii-video (ASCII video directly uses characters and palettes from the ASCII art vocabulary)

## creative/ascii-video
(Existing: none — needs additions)
- `similar` → creative/ascii-art (ASCII video uses ASCII characters as its visual medium; ascii-art skill provides the character vocabulary and conversion tools)
- `similar` → creative/manim-video (Both are video production pipelines — one for ASCII art animation, the other for mathematical/algorithmic animation — sharing ffmpeg encoding, scene composition, and rendering patterns)
- `uses` → content-production/text-to-speech (ASCII video pipeline supports TTS narration mode for voiceover)
- `similar` → creative/p5js (Both are programmatic visual media skills with generative, audio-reactive, and animation modes)

## creative/baoyu-infographic
(Existing: none — needs additions)
- `similar` → creative/architecture-diagram (Both produce structured visual information — infographics for data storytelling, architecture diagrams for system design — using templates and design systems)
- `similar` → creative/popular-web-designs (Infographic templates (21 layouts × 21 styles) share the concept of pre-built design systems with the 54-web-design catalog)
- `uses` → creative/brand-studio-forge (Brand visual identity (colors, typography, voice) constrains infographic style choices)
- `similar` → creative/p5js (Both generate visual output — infographics as static PNG, p5js as interactive/generative — from structured content)

## creative/brand-studio-forge
(Existing: claude-design, style-guide-consultation, popular-web-designs)
- `uses` → creative/copywriting (Brand voice definition and content generation follow copywriting principles; forge_content command generates brand-voice marketing copy)
- `used_by` → autonomous-ai-agents/product-pipeline (Brand identity feeds into product design and management phases of the pipeline)
- `uses` → creative/humanizer (Brand voice refinement and anti-slop checks apply humanizer principles)

## creative/claude-design
(Existing: design-md, popular-web-designs, excalidraw, architecture-diagram)
- `similar` → creative/p5js (Both create standalone HTML artifacts — claude-design for UI/UX prototypes, p5js for generative art sketches — sharing browser-based rendering and iterative design workflow)
- `similar` → creative/brand-studio-forge (Both deal with design systems and visual artifacts; claude-design produces prototypes, forge produces brand identity kits)

## creative/comfyui
(Existing: stable-diffusion-image-generation, image_gen)
- `similar` → creative/ascii-video (Both generate video output — ComfyUI via AnimateDiff/Hunyuan/Wan, ascii-video via Python/ffmpeg — with generative AI pipelines)
- `similar` → creative/p5js (Both are generative visual tools — ComfyUI for Stable Diffusion/Flux images/video, p5js for browser-based procedural art)
- `similar` → creative/brand-studio-forge (ComfyUI can generate brand imagery; forge references image generation for logo and visual materialization)

## creative/copywriting
(Existing: humanizer, brand-iaf-conteudo)
- `used_by` → creative/brand-studio-forge (Brand content generation relies on copywriting principles; forge_content command produces marketing copy)
- `used_by` → content-production/iaf-newsletter-pipeline (Newsletter editorial curation applies copywriting structure and voice principles)
- `similar` → creative/songwriting-and-ai-music (Both are creative writing skills — copywriting for marketing, songwriting for lyrics — sharing audience awareness, emotional arc, and revision workflow)

## creative/excalidraw
(Existing: none — needs additions)
- `similar` → creative/architecture-diagram (Both produce diagrams — Excalidraw for hand-drawn style JSON, architecture-diagram for dark-themed SVG HTML — with overlapping use in architecture visualization)
- `similar` → creative/claude-design (Both create design artifacts — Excalidraw for diagrams/wireframes, claude-design for HTML prototypes/screens)
- `similar` → creative/p5js (Both are creative visual tools — Excalidraw for JSON-based diagrams, p5js for code-driven generative art)

## creative/humanizer
(Existing: copywriting)
- `used_by` → content-production/iaf-newsletter-pipeline (Pipeline explicitly includes a humanizer pass on editorial content before delivery)
- `used_by` → creative/brand-studio-forge (Brand copy refinement and anti-slop review apply humanizer techniques)
- `used_by` → creative/copywriting (Copywriting skill recommends pairing with humanizer for line-by-line editing after drafting)

## creative/manim-video
(Existing: none — needs additions)
- `similar` → creative/p5js (Both are programmatic animation skills — Manim for 3Blue1Brown-style explainers with LaTeX, p5js for browser-based generative art — sharing scene composition, animation timing, and export pipeline patterns)
- `similar` → creative/ascii-video (Both produce video output through Python pipelines with ffmpeg encoding, scene planning, and TTS narration support)
- `uses` → content-production/text-to-speech (Manim pipeline optionally adds TTS voiceover narration via ElevenLabs or Qwen3-TTS)
- `similar` → creative/architecture-diagram (Manim has an architecture diagram mode for system topology animations)

## creative/p5js
(Existing: ascii-video, manim-video, excalidraw)
- `similar` → creative/pretext (Both create browser-based creative demos — p5js for canvas 2D/WebGL art, pretext for DOM-free text layout and kinetic typography)
- `similar` → creative/baoyu-infographic (Both transform structured content into visual output — p5js for interactive/generative, baoyu for static infographics)
- `similar` → creative/comfyui (Both are generative visual tools — p5js for procedural code art, ComfyUI for AI image/video generation)

## creative/popular-web-designs
(Existing: none — needs additions)
- `used_by` → creative/claude-design (Claude-design explicitly loads this skill for visual vocabulary when building HTML artifacts styled after known brands)
- `used_by` → creative/brand-studio-forge (Brand identity creation references existing design systems for inspiration and anti-slop benchmarking)
- `similar` → creative/baoyu-infographic (Both provide curated design templates — 54 web design systems vs 21 layout × 21 style infographic combinations)
- `similar` → creative/architecture-diagram (Both define visual design systems — popular-web-designs for UI, architecture-diagram for infrastructure diagrams)

## creative/pretext
(Existing: p5js, claude-design, excalidraw, architecture-diagram)
- `similar` → creative/ascii-art (Pretext's ASCII obstacle typography pattern uses measured character grids and real prose, complementing ascii-art's monospace ASCII vocabulary)
- `similar` → creative/manim-video (Both involve kinetic typography — pretext for browser-based canvas, manim for mathematical/animated text)

## creative/songwriting-and-ai-music
(Existing: none — needs additions)
- `similar` → creative/copywriting (Both are creative writing disciplines — songwriting for lyrics, copywriting for marketing copy — sharing structure, audience awareness, emotional arc, and revision workflow)
- `uses` → content-production/text-to-speech (Suno AI generates audio from lyrics; TTS skill provides complementary audio generation and voice design patterns)
- `similar` → creative/ascii-video (ASCII video has audio-reactive and music visualization modes that pair with AI-generated music)
- `similar` → content-production/iaf-newsletter-pipeline (Both involve content production — one for music/songs, the other for written newsletters — with iterative refinement cycles)
