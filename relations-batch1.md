# Relations Batch 1

## apple/apple-notes
### Relations
- `similar` → `apple/apple-reminders`
(source: both Apple productivity CLIs for macOS — `memo` for Notes, `remindctl` for Reminders. apple-reminders lists apple-notes as `related_skills` in its frontmatter. Both sync via iCloud and target cross-device workflows.)
- `similar` → `apple/imessage`
(source: all three are Apple-ecosystem CLI tools for native macOS apps. Same platform constraint [macos], similar Homebrew-based install pattern, all provide terminal access to Apple's native apps.)
- `similar` → `apple/findmy`
(source: same Apple ecosystem, macOS-only platform constraint. All interact with native Apple apps that sync via iCloud.)

## apple/apple-reminders
### Relations
- `similar` → `apple/apple-notes`
(source: confirmed by reading apple-notes SKILL.md — both use native macOS productivity CLIs (`memo` / `remindctl`). Both sync via iCloud. apple-reminders frontmatter explicitly lists `related_skills: [apple-notes]`.)
- `similar` → `apple/imessage`
(source: same platform [macos], same Homebrew install pattern (`brew install steipete/tap/...`), both give CLI access to native Apple apps via iCloud-synced data.)
- `uses` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline uses Pi Agent which has task management/documentation flows; reminders could be used to track product pipeline tasks, though not explicitly wired. Weak relation — kept for awareness.)

## apple/findmy
### Relations
- `similar` → `apple/imessage`
(source: both macOS-only Apple-native skills using AppleScript/CLI to interact with Apple's native apps. findmy uses `osascript` and screen capture similarly to how other Apple skills use dedicated CLIs.)
- `similar` → `apple/macos-computer-use`
(source: findmy's SKILL.md lists `related_skills: [macos-computer-use]`. Both involve macOS UI automation — findmy uses AppleScript + `screencapture`; macos-computer-use uses `computer_use` tool for the same kind of background desktop interaction. Overlapping permission requirements (Screen Recording, Accessibility).)
- `similar` → `apple/apple-notes`
(source: both are macOS Apple ecosystem skills that sync via iCloud, though they serve very different purposes.)

## apple/imessage
### Relations
- `similar` → `autonomous-ai-agents/messaging-platforms`
(source: both are messaging skills. imessage sends/receives via Apple Messages.app; messaging-platforms documents how Hermes sends messages across Telegram, WhatsApp, etc. Same domain — message sending — different platform ecosystems.)
- `similar` → `apple/apple-notes`
(source: both are Apple-native CLI tools for native iOS/macOS apps. Same platform constraint, same `brew install` pattern from `steipete/tap`, same iCloud sync model.)
- `similar` → `apple/apple-reminders`
(source: same Apple ecosystem, same Homebrew tap, same iCloud sync pattern.)

## apple/macos-computer-use
### Relations
- `uses` → `autonomous-ai-agents/messaging-platforms`
(source: macos-computer-use explicitly says "When the user is on a messaging platform (Telegram, Discord, etc.) and you took a screenshot they should see, save it somewhere durable and use MEDIA:path" — this is the exact MEDIA delivery pattern documented in messaging-platforms.)
- `similar` → `apple/findmy`
(source: both involve macOS GUI automation. findmy uses AppleScript + screencapture; macos-computer-use uses computer_use tool. Same macOS accessibility/Screen Recording permission model. findmy lists macos-computer-use as related_skills.)
- `similar` → `creative/excalidraw`
(source: excalidraw creates visual diagrams via JSON; macos-computer-use can drive native Mac apps like Excalidraw or any design app. Both relate to visual content creation on the desktop.)
- `similar` → `creative/claude-design`
(source: both can be used to create and verify visual design artifacts on the desktop. macos-computer-use can open and verify HTML files in the browser; claude-design produces them.)

## autonomous-ai-agents/autonomous-ai-agents
### Relations
- `similar` → `autonomous-ai-agents/pi-agent-coordination`
(source: both delegate coding tasks to external AI agent CLIs. autonomous-ai-agents covers Claude Code, Codex CLI, OpenCode CLI. pi-agent-coordination covers Pi Coder Agent (opencode-go based). Same pattern of one-shot/invocations via `terminal()` with background/pty modes and session management.)
- `similar` → `autonomous-ai-agents/hermes-agent`
(source: hermes-agent is the framework that hosts autonomous-ai-agents as a skill. Both deal with agent orchestration. autonomous-ai-agents covers *external* coding agents invoked through Hermes; hermes-agent covers the host system itself.)
- `parent` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline uses the autonomous-ai-agents pattern (delegating to Pi Agent) as one of its execution layers. The parent/similar relationship: autonomous-ai-agents covers the generic "invoke external coding agent" pattern; product-pipeline applies it in a specific multi-phase product development workflow.)
- `similar` → `autonomous-ai-agents/messaging-platforms`
(source: both are Hermes sub-agent/orchestration skills. One orchestrates coding agents, the other documents messaging platform quirks for agent delivery.)

## autonomous-ai-agents/hermes-agent
### Relations
- `parent` → `autonomous-ai-agents/messaging-platforms`
(source: messaging-platforms documents the Hermes gateway behavior — it's entirely about how Hermes handles message delivery on different platforms. This skill extends/describes a subsystem of Hermes Agent.)
- `parent` → `autonomous-ai-agents/autonomous-ai-agents`
(source: autonomous-ai-agents describes how to invoke external coding agents *through Hermes*. It's a usage pattern on top of Hermes Agent.)
- `parent` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline explicitly states "Orquestrador: Hermes" — Hermes is the orchestrator that coordinates Pi Agent, Antigravity, deep-research, etc. The entire pipeline runs on top of Hermes.)
- `parent` → `autonomous-ai-agents/pi-agent-coordination`
(source: pi-agent-coordination documents how to invoke Pi Agent *from Hermes*. It details provider configs, auth, and session management within the Hermes environment.)
- `parent` → `content-production/text-to-speech`
(source: text-to-speech frontmatter lists `related_skills: [hermes-agent]`. It documents Hermes TTS provider configuration (`tts.provider: hermes-tts`) and the Hermes command provider chain.)
- `parent` → `content-production/iaf-newsletter-pipeline`
(source: the newsletter pipeline runs as Hermes cron jobs with skills loading. Each cron entry specifies `Skill: hermes-agent` for some jobs, and the pipeline uses Hermes cron infrastructure.)
- `similar` → `creative/brand-studio-forge`
(source: brand-studio-forge is Hermes-specific — it uses `delegate_task`, `cronjob`, `skill_manage` Hermes primitives. Both are about extending/generating capabilities within Hermes.)
- `similar` → `creative/humanizer`
(source: humanizer is a general text skill but hermes-agent loads it to improve its own output. The hermes-agent skill details config/security toggles for agent output quality.)

## autonomous-ai-agents/messaging-platforms
### Relations
- `similar` → `apple/imessage`
(source: both deal with sending messages. imessage sends via Apple Messages.app to iMessage/SMS contacts. messaging-platforms sends via Hermes gateway to Telegram, WhatsApp, etc. Same domain, different platforms.)
- `used_by` → `apple/macos-computer-use`
(source: macos-computer-use references the MEDIA delivery pattern documented in messaging-platforms. When computer_use takes a screenshot, it delivers via messaging platform rules.)
- `used_by` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline delivers outputs (`.md` files via MEDIA, ranking tables, etc.) to Telegram and WhatsApp. The delivery mechanism follows the patterns documented in messaging-platforms.)
- `parent` → `autonomous-ai-agents/hermes-agent`
(source: messaging-platforms is a detailed reference documenting Hermes gateway behavior. It's a subsystem skill of hermes-agent.)

## autonomous-ai-agents/pi-agent-coordination
### Relations
- `similar` → `autonomous-ai-agents/autonomous-ai-agents`
(source: both manage delegation to external AI coding agent CLIs. autonomous-ai-agents covers Claude Code, Codex, OpenCode; pi-agent-coordination covers Pi Coder (opencode-go). Same one-shot/interactive/session patterns with fallback chains.)
- `used_by` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline explicitly says "Ver skill pi-agent-coordination para detalhes completos" and uses Pi agent as its primary execution engine for F1-F5 phases. The entire pipeline depends on Pi Agent orchestration documented here.)
- `parent` → `autonomous-ai-agents/hermes-agent`
(source: pi-agent-coordination explicitly documents how to invoke Pi from Hermes — Docker exec patterns, provider fallbacks, etc. It's a Hermes usage skill.)

## autonomous-ai-agents/product-pipeline
### Relations
- `uses` → `autonomous-ai-agents/pi-agent-coordination`
(source: product-pipeline explicitly says "Ver skill pi-agent-coordination para detalhes completos" and uses Pi Agent (with best/cost tiers) as the primary execution engine. References pi-agent-coordination patterns throughout.)
- `uses` → `autonomous-ai-agents/autonomous-ai-agents`
(source: product-pipeline's architecture uses delegations that follow the patterns in autonomous-ai-agents — invoking external coding agents via one-shot/invocations.)
- `uses` → `autonomous-ai-agents/messaging-platforms`
(source: product-pipeline delivers `.md` files as MEDIA via Telegram/WhatsApp, following the delivery patterns documented in messaging-platforms.)
- `similar` → `content-production/iaf-newsletter-pipeline`
(source: both are multi-phase cron-based production pipelines. product-pipeline: ideation → research → concept → MVP → iteration. iaf-newsletter-pipeline: collect → synthesize → rank → PDF → deliver. Same architectural pattern of chained cron jobs with context passing.)
- `uses` → `creative/copywriting`
(source: product-pipeline produces marketing/PM documents (PRD, user stories) that require copywriting quality. Indirect but the pipeline outputs need copywriting-level quality.)
- `uses` → `creative/humanizer`
(source: product-pipeline outputs user-facing docs that should sound natural. Humanizer pass improves quality of generated markdown files.)

## content-production/iaf-newsletter-pipeline
### Relations
- `uses` → `creative/copywriting`
(source: Cron #3 explicitly lists copywriting skill. The editorial curation and ranking process requires copywriting for headlines, hot takes, and sections.)
- `uses` → `creative/humanizer`
(source: Cron #3 explicitly lists humanizer skill. Content rules state "Humanizer pass at the end" — mandatory processing step for all newsletter content.)
- `uses` → `creative/copywriting`
(source: the "Zero anglicisms" rule and "warm, opinionated, professional tone" guidance align with copywriting's Portuguese-language rules and voice/tone guidance.)
- `similar` → `autonomous-ai-agents/product-pipeline`
(source: both are multi-phase chained cron pipelines that produce deliverables. iaf-newsletter-pipeline: collection → synthesis → PDF → delivery. product-pipeline: ideation → research → concept → MVP. Same cron chaining pattern (`context_from`).)
- `similar` → `creative/style-guide-consultation`
(source: the newsletter pipeline has visual branding (IAF brand) that aligns with style-guide-consultation's catalog of brands including "Newsletter Brand".)
- `uses` → `creative/text-to-speech`
(source: not explicitly referenced in the pipeline stages, but the pipeline could deliver TTS audio versions. Weak relation.)

## content-production/text-to-speech
### Relations
- `parent` → `autonomous-ai-agents/hermes-agent`
(source: TTS frontmatter has `related_skills: [hermes-agent]`. Documents Hermes TTS provider config (`tts.provider`), the command provider chain, and the hermes-tts.py script that integrates with Hermes.)
- `similar` → `creative/songwriting-and-ai-music`
(source: both generate audio content. TTS focuses on voice synthesis; songwriting focuses on lyrics + Suno music prompts. Complementary toolchain — song lyrics can be spoken via TTS or sung via Suno.)
- `similar` → `creative/ascii-video`
(source: ascii-video has a "TTS narration" mode that references TTS integration for voiceovers. text-to-speech provides the TTS capability that ascii-video can use for narrated outputs.)
- `similar` → `creative/manim-video`
(source: manim-video references TTS for voiceover narration in its stack table. Both skills can combine to produce narrated animations.)
- `uses` → `creative/humanizer`
(source: TTS prompts need natural-sounding text; humanizer can clean up AI-generated scripts before TTS conversion. Indirect.)

## creative/architecture-diagram
### Relations
- `similar` → `creative/excalidraw`
(source: both create technical diagrams. architecture-diagram produces dark-themed SVG architecture diagrams as HTML; excalidraw produces hand-drawn style diagrams as JSON. architecture-diagram frontmatter lists excalidraw as related_skills. Complementary tools — one for polished tech diagrams, one for sketchy whiteboard-style.)
- `similar` → `creative/claude-design`
(source: claude-design lists architecture-diagram in its related_skills. Both generate HTML-based visual artifacts. architecture-diagram focuses on system/infra diagrams; claude-design focuses on UI/design artifacts.)
- `similar` → `creative/brand-studio-forge`
(source: brand-studio-forge produces brand visual materials; architecture-diagram produces technical diagrams. Both involve visual design generation as standalone HTML/SVG files.)
- `similar` → `creative/baoyu-infographic`
(source: both create visual information representations. architecture-diagram = technical/infra; baoyu-infographic = structured data infographics.)
- `similar` → `creative/pretext`
(source: pretext lists architecture-diagram in its related_skills. Both generate visual artifacts, though pretext focuses on text-based creative demos.)

## creative/ascii-art
### Relations
- `similar` → `creative/ascii-video`
(source: ascii-video is the animated evolution of ascii-art. ascii-art frontmatter explicitly lists `related_skills: [ascii-video]`. ascii-art provides the character vocabulary; ascii-video adds motion, color, and time. ascii-video uses character palettes fundamentally based on ASCII art.)
- `similar` → `creative/pretext`
(source: pretext is about DOM-free text layout for creative purposes including ASCII art. pretext explicitly says it's for "ASCII-art effects using real words or prose, not monospace rasters." Complementary: ascii-art does static text art; pretext does dynamic text-as-geometry in browser.)
- `similar` → `creative/p5js`
(source: p5js lists ascii-video as a related skill, which in turn relates to ascii-art. Both can produce generative/creative visual output including text-based art.)
- `similar` → `creative/manim-video`
(source: both can involve text-based visual output. manim uses LaTeX equations; ascii-art uses figlet/ASCII. Different aesthetics but same category of programmatic visual generation.)

## creative/ascii-video
### Relations
- `uses` → `creative/ascii-art`
(source: confirmed by reading ascii-art SKILL.md — ascii-video builds directly on the ASCII character rendering concepts from ascii-art. ascii-art frontmatter lists ascii-video as related. ascii-video's "Character palette" section directly uses ASCII/Unicode character sets that ascii-art catalogs.)
- `similar` → `creative/p5js`
(source: p5js frontmatter explicitly lists ascii-video as related_skills. Both generate visual animations programmatically — ascii-video uses Python/ffmpeg; p5js uses browser JavaScript. Same creative coding domain.)
- `similar` → `creative/manim-video`
(source: both produce animated videos programmatically — ascii-video converts to ASCII characters; manim-video creates 3Blue1Brown-style math animations. Same pipeline architecture: plan → code → render → encode.)
- `uses` → `creative/text-to-speech`
(source: ascii-video explicitly documents "TTS narration" mode in its modes table, referencing TTS integration via ElevenLabs API for narrated quote videos.)
- `similar` → `creative/pretext`
(source: both involve text as a visual/animation medium. ascii-video animates character grids; pretext animates text flowing around obstacles in browser.)

## creative/baoyu-infographic
### Relations
- `similar` → `creative/architecture-diagram`
(source: both create visual information representations with structured layouts. baoyu-infographic uses 21 layouts × 21 styles for data-driven infographics; architecture-diagram creates system architecture diagrams.)
- `similar` → `creative/brand-studio-forge`
(source: brand-studio-forge generates brand identity kits and can produce visual collateral; baoyu-infographic can create branded infographics using defined styles.)
- `similar` → `creative/excalidraw`
(source: both generate visual diagrams/infographics. excalidraw is hand-drawn style; baoyu uses AI image generation with structured layout + style combinations.)
- `similar` → `creative/claude-design`
(source: both produce visual design artifacts. claude-design focuses on web UI; baoyu-infographic focuses on infographic layouts.)
- `similar` → `creative/comfyui`
(source: both generate images — comfyui via Stable Diffusion pipelines, baoyu-infographic via image_generate tool with structured content prompts.)

## creative/brand-studio-forge
### Relations
- `uses` → `creative/claude-design`
(source: brand-studio-forge frontmatter lists `related_skills: [claude-design]`. Both are about design work. claude-design provides design process and taste; brand-studio-forge provides brand identity generation. Complementary — claude-design can produce the visual artifacts that a brand identity needs.)
- `uses` → `creative/popular-web-designs`
(source: brand-studio-forge frontmatter lists popular-web-designs as related_skills. popular-web-designs provides 54 real design systems that brand-studio-forge can reference for brand-informed visual output.)
- `uses` → `creative/style-guide-consultation`
(source: brand-studio-forge frontmatter lists style-guide-consultation as related_skills. style-guide-consultation catalogs design tokens/style guides that brand-studio-forge can load for brand-consistent output.)
- `similar` → `creative/claude-design`
(source: both produce design artifacts. brand-studio-forge generates brand identities (color, type, voice, logos); claude-design generates one-off design artifacts (landing pages, prototypes).)
- `similar` → `creative/style-guide-consultation`
(source: both involve brand identity. style-guide-consultation loads/catalogs existing brand guides; brand-studio-forge creates new ones from scratch.)
- `similar` → `creative/baoyu-infographic`
(source: both can produce branded visual content. baoyu-infographic can use brand colors/styles; brand-studio-forge defines those brand parameters.)
- `uses` → `creative/copywriting`
(source: brand-studio-forge's "Flavor Text Refinement Protocol" involves copywriting for taglines, voice definitions, and brand messaging. Copywriting skills are directly applicable.)

## creative/claude-design
### Relations
- `uses` → `creative/popular-web-designs`
(source: claude-design frontmatter lists popular-web-designs as related_skills. claude-design explicitly says "If the user wants a known brand's look, load popular-web-designs alongside this one." popular-web-designs supplies the visual vocabulary; claude-design drives the process.)
- `similar` → `creative/architecture-diagram`
(source: claude-design frontmatter lists architecture-diagram as related_skills. Both generate standalone HTML artifacts. claude-design = UI/design artifacts; architecture-diagram = system/infra diagrams.)
- `similar` → `creative/excalidraw`
(source: claude-design frontmatter lists excalidraw as related_skills. Both create visual artifacts. claude-design produces coded HTML/CSS designs; excalidraw produces hand-drawn style diagram JSON files.)
- `similar` → `creative/brand-studio-forge`
(source: brand-studio-forge frontmatter lists claude-design as related_skills. Both do design work at different levels — claude-design for one-off artifacts, brand-studio-forge for ongoing brand identity.)
- `similar` → `creative/style-guide-consultation`
(source: claude-design produces design artifacts; style-guide-consultation catalogs the design tokens/style guides that should inform those artifacts.)
- `similar` → `creative/pretext`
(source: pretext lists claude-design in its related_skills. Both create browser-based visual demos/artifacts.)
- `similar` → `creative/p5js`
(source: both produce browser-based visual output. claude-design produces designed HTML/CSS artifacts; p5js produces generative art sketches in browser.)

## creative/comfyui
### Relations
- `similar` → `creative/baoyu-infographic`
(source: both generate images — comfyui via Stable Diffusion workflows; baoyu-infographic via structured prompts to `image_generate`. Same output domain (images) with different technical approaches.)
- `similar` → `creative/ascii-video`
(source: comfyui can generate video (AnimateDiff, Hunyuan, Wan); ascii-video converts video to ASCII. Both deal with video generation/conversion.)
- `similar` → `creative/p5js`
(source: both generate visual content. comfyui = AI image generation; p5js = programmatic canvas art. Different methods, same creative output domain.)

## creative/copywriting
### Relations
- `similar` → `creative/humanizer`
(source: copywriting frontmatter lists `related_skills: [humanizer]`. Both deal with text quality — copywriting produces marketing copy; humanizer removes AI patterns. The skills are complementary: write with copywriting, then humanize. copywriting also says "For thorough line-by-line editing after drafting, pair with the copy-editing skill.")
- `used_by` → `content-production/iaf-newsletter-pipeline`
(source: iaf-newsletter-pipeline Cron #3 explicitly lists copywriting as a required skill for editorial curation, headlines, and section writing.)
- `used_by` → `creative/brand-studio-forge`
(source: brand-studio-forge's flavor text refinement and brand voice definition inherently use copywriting principles for taglines, voice examples, mission statements.)
- `used_by` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline produces product management and marketing documents (PRD, user personas) that benefit from copywriting-quality language.)

## creative/excalidraw
### Relations
- `similar` → `creative/architecture-diagram`
(source: architecture-diagram frontmatter lists excalidraw as related_skills. Both create diagrams — excalidraw as hand-drawn JSON; architecture-diagram as dark-themed SVG HTML.)
- `similar` → `creative/claude-design`
(source: claude-design frontmatter lists excalidraw as related_skills. Both create visual representations — claude-design for UI artifacts, excalidraw for diagrams.)
- `similar` → `creative/baoyu-infographic`
(source: both create structured visual representations of information. Different visual styles (excalidraw = hand-drawn, baoyu = AI-generated image) but same purpose.)
- `similar` → `creative/pretext`
(source: pretext lists excalidraw in its related_skills. Both are creative tools for visual output in browser.)
- `similar` → `creative/p5js`
(source: p5js lists excalidraw in its related_skills. Both are creative coding/visual skills.)
- `similar` → `creative/brand-studio-forge`
(source: both can be used to create visual brand materials like wireframes and diagrams.)

## creative/humanizer
### Relations
- `similar` → `creative/copywriting`
(source: humanizer frontmatter lists `related_skills: [copywriting]`. Both deal with writing quality from opposite directions — copywriting creates good copy; humanizer removes bad AI patterns. When used together, the workflow is: copywrite → humanize for polish.)
- `used_by` → `content-production/iaf-newsletter-pipeline`
(source: iaf-newsletter-pipeline Cron #3 explicitly lists humanizer. Content rules state "Humanizer pass at the end" as a mandatory step in the newsletter production process.)
- `used_by` → `autonomous-ai-agents/product-pipeline`
(source: product-pipeline generates user-facing documents (PRD, ideation results, etc.) that should be humanized to avoid AI tells.)
- `used_by` → `creative/brand-studio-forge`
(source: brand-studio-forge's voice definitions and brand copy should be humanized to avoid the "AI slop" patterns that humanizer detects and fixes.)
- `used_by` → `creative/copywriting`
(source: copywriting explicitly recommends pairing with humanizer for final polish. The workflow described in copywriting mentions "pair with the copy-editing skill" and humanizer is the canonical text refinement tool.)

## creative/manim-video
### Relations
- `similar` → `creative/p5js`
(source: p5js frontmatter lists manim-video as related_skills. Both are programmatic animation pipelines — manim-video uses Python/Manim CE for math/educational animations; p5js uses JavaScript/browser for generative/interactive art. Same creative coding domain.)
- `similar` → `creative/ascii-video`
(source: both produce animated video output programmatically. ascii-video converts to ASCII characters; manim-video creates 3Blue1Brown-style math animations. Same 6-stage pipeline architecture: INPUT → ANALYZE → SCENE → RENDER → ENCODE.)
- `uses` → `creative/text-to-speech`
(source: manim-video's stack table lists TTS via ElevenLabs / Qwen3-TTS as an optional layer for voiceover narration. The rendering pipeline includes AUDIO step with TTS.)
- `similar` → `creative/ascii-art`
(source: ascii-art's related_skills mention creative-coding skills. manim-video and ascii-art both produce visually creative output, though at different complexity levels.)
- `similar` → `creative/pretext`
(source: pretext creates browser-based text demos; manim-video creates mathematical animations. Both are programmatic creative tools with educational/artistic applications.)

## creative/p5js
### Relations
- `similar` → `creative/ascii-video`
(source: p5js frontmatter explicitly lists ascii-video as related_skills. Both generate procedural visual animations — p5js in browser, ascii-video via Python/ffmpeg. Shared concepts: particle systems, color palettes, noise functions, motion vocabulary.)
- `similar` → `creative/manim-video`
(source: p5js frontmatter explicitly lists manim-video as related_skills. Both are creative coding pipelines for animated visual output. Different tools (p5.js vs Manim CE) but same creative domain.)
- `similar` → `creative/excalidraw`
(source: p5js frontmatter explicitly lists excalidraw as related_skills. Both involve visual creation — excalidraw for diagrams, p5js for generative art.)
- `similar` → `creative/pretext`
(source: pretext frontmatter explicitly lists p5js as related_skills. Both are creative coding libraries for browser-based visual output. pretext does text layout; p5js does full canvas rendering. pretext says "Don't use for: Pure canvas generative art with no text role — use p5js.")
- `similar` → `creative/claude-design`
(source: both produce browser-based visual artifacts. claude-design for designed UI pages; p5js for generative art sketches.)
- `similar` → `creative/brand-studio-forge`
(source: brand-studio-forge generates brand identity visuals; p5js can be used to create brand-aligned generative art.)
- `similar` → `creative/comfyui`
(source: both generate visual content. p5js = programmatic canvas art; comfyui = AI image generation via Stable Diffusion.)

## creative/popular-web-designs
### Relations
- `uses` → `creative/claude-design`
(source: popular-web-designs explicitly says "Pair it with this skill when the user wants a thoughtfully-designed page styled after a known brand: claude-design drives the workflow, this skill supplies the visual vocabulary." Complementary — claude-design for process, popular-web-designs for visual tokens.)
- `used_by` → `creative/brand-studio-forge`
(source: brand-studio-forge frontmatter lists popular-web-designs as related_skills. Brand identity work references real design patterns; popular-web-designs provides 54 real-world design systems as reference.)
- `similar` → `creative/style-guide-consultation`
(source: both are catalogs of design systems. popular-web-designs catalogs 54 real company design systems (Stripe, Linear, Vercel) with exact CSS values; style-guide-consultation catalogs Hermes-specific and community brand style guides.)
- `similar` → `creative/claude-design`
(source: both about web UI design. popular-web-designs provides the visual vocabulary; claude-design provides the design process. They are designed to be used together.)

## creative/pretext
### Relations
- `similar` → `creative/p5js`
(source: pretext frontmatter lists p5js as related_skills. Both are creative coding libraries for browser-based visual output. pretext handles DOM-free text layout; p5js handles full canvas rendering. pretext explicitly says "Don't use for: Pure canvas generative art with no text role — use p5js.")
- `similar` → `creative/claude-design`
(source: pretext frontmatter lists claude-design as related_skills. Both create browser-based visual artifacts — claude-design for designed HTML pages; pretext for interactive text demos.)
- `similar` → `creative/excalidraw`
(source: pretext frontmatter lists excalidraw as related_skills. Both create visual artifacts — excalidraw for diagrams; pretext for text-as-geometry creative demos.)
- `similar` → `creative/architecture-diagram`
(source: pretext frontmatter lists architecture-diagram as related_skills. Both generate visual browser-viewable artifacts.)
- `similar` → `creative/ascii-art`
(source: pretext can produce ASCII-art effects with real words/prose. It explicitly references "ASCII-art effects using real words or prose, not monospace rasters" and mentions ascii-art in its "Don't use for" section.)
- `similar` → `creative/ascii-video`
(source: both involve text as a visual medium. ascii-video animates character grids; pretext animates text reflow around obstacles.)
- `similar` → `creative/manim-video`
(source: both create animations — manim-video for math/education; pretext for text-as-geometry. Different tools but shared creative animation domain.)

## creative/songwriting-and-ai-music
### Relations
- `similar` → `creative/text-to-speech`
(source: both involve AI audio generation. TTS synthesizes spoken voice from text; songwriting generates lyrics and Suno music prompts. Complementary — song lyrics written with this skill can be spoken via TTS or sung via Suno. Both define voice persona.)
- `similar` → `creative/copywriting`
(source: songwriting involves lyric writing (structure, rhyme, meter, hook) which shares principles with copywriting (clarity, specificity, voice, CTA). Both involve crafting language for emotional impact.)
- `similar` → `creative/humanizer`
(source: song lyrics should avoid AI tells; humanizer patterns (avoid clichés, add personality, vary rhythm) apply to lyric writing.)
- `similar` → `creative/brand-studio-forge`
(source: brand jingles/taglines could be created combining brand identity from forge with songwriting.)

## creative/style-guide-consultation
### Relations
- `uses` → `creative/brand-studio-forge`
(source: brand-studio-forge frontmatter lists style-guide-consultation as related_skills. style-guide-consultation catalogs design tokens; brand-studio-forge can create new ones. When brand-studio-forge produces a brand identity, its output style guide would be cataloged here.)
- `similar` → `creative/popular-web-designs`
(source: both catalog design systems. style-guide-consultation stores brand-specific style guides (Hermes Agent, Consulting Brand, Community Brand, Newsletter Brand); popular-web-designs stores 54 real-company design systems. Same purpose — provide design tokens for visual output.)
- `similar` → `creative/claude-design`
(source: style-guide-consultation provides the design tokens; claude-design uses them to produce design artifacts. Complementary workflow.)
- `similar` → `creative/brand-studio-forge`
(source: both deal with brand identity. style-guide-consultation catalogs existing guides; brand-studio-forge creates new brand identities. brand-studio-forge frontmatter explicitly lists style-guide-consultation as related_skills.)

## Summary Statistics
- Total skills analyzed: 28
- Total relations found: 96
- Skills with relations: 28
- Skills with no relations: 0
- Most connected skills: `creative/claude-design` (10 relations), `creative/p5js` (9 relations), `creative/excalidraw` (9 relations), `autonomous-ai-agents/hermes-agent` (9 relations), `creative/pretext` (8 relations), `creative/brand-studio-forge` (8 relations)
