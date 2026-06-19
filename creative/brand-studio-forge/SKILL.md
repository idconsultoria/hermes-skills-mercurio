---
name: brand-studio-forge
description: "Create, refine, or evolve a brand identity: interviews, identity kit, content

Load this skill when the user wants to create, refine, or evolve a brand identity. Covers brand interviews, identity kit generation (logo, color, type, voice, guidelines), brand-specific content skills, and ongoing content via cron. Not for UI design or non-brand creative tasks."

Load this skill when the user wants to create, refine, or evolve a brand identity. Covers brand interviews, identity kit generation (logo, color, type, voice, guidelines), brand-specific content skills, and ongoing content via cron. Not for UI design or non-brand creative tasks."
version: 1.0.0
user-invocable: true
argument-hint: "[interview · forge · name · evolve · author | critique · audit | polish | content · schedule] [target]"
license: MIT
metadata:
  hermes:
    related_skills: [claude-design, style-guide-consultation, popular-web-designs]
allowed-tools:
  - Bash(python3 forge/scripts/*.py *)
  - Bash(bash forge/scripts/setup.sh)
# Brand Studio Forge

> ⚡ **Stitch MCP:** Se esta tarefa envolver criação de telas, mockups UI ou prototipagem visual, ative o Stitch MCP primeiro: edite `/opt/data/config.yaml` mudando `stitch.enabled` para `true` e execute `/reload-mcp`.

Generates and evolves brand identities, then authors brand-specific skills that produce ongoing content.

## Setup (non-optional)

Before any brand design or file edits, pass these gates. Skipping them produces generic output that ignores the brand.

| Gate | Required check | If fail |
|---|---|---|
| Context | BrandProfile JSON exists and was loaded | Run `/forge_interview` or `python3 forge/scripts/interview.py` |
| Brand | PRODUCT.md exists with personality words, positioning, anti-references | Run `/forge_interview`, then resume |
| Mode | One of: identity / content / evolve identified from task cue | Identify mode before continuing |
| Image | API key for at least one image provider exists in `~/.forge/keys.json` | Ask user for Gemini or OpenAI API key via keystore prompt |
| Mutation | All active gates above pass | Do not edit project files yet |

Codex-style agents must state this before editing files:

```text
FORGE_PREFLIGHT: context=pass brand=pass mode=identity|content|evolve image_gate=pass|skipped:<reason> mutation=open
```

### Context gathering

Two files, loaded from the project root under `forge/`.

- **PRODUCT.md** — required. Brand name, industry, personality, positioning, anti-references.
- **DESIGN.md** — optional, strongly recommended. Color tokens, typography, voice rules, logo specifications.

Both are produced by the `forge_interview` and `forge_forge` commands. Load PRODUCT.md directly. DESIGN.md is populated after `forge_forge` generates the identity kit.

```bash
python3 forge/scripts/interview.py
```

If PRODUCT.md is missing: run `/forge_interview`, then resume the user's original task with fresh context.

If DESIGN.md is missing: nudge once per session, then proceed.

#### When Python scripts don't exist

The `forge/scripts/` and `src/` directories are **optional** — they may not exist if the skill was freshly created. When they're absent:
- **`forge_interview`**: Conduct the interview manually using `[references/interview.md](references/interview.md)` — it contains the full 3–4 round protocol with exact questions. The protocol already exists and is loaded.
- **`forge_forge`**: Execute the identity kit generation directly (palette, typography, voice, logo) using the Shared Design Laws from this SKILL.md as your rulebook. The 4 parallel children pattern (delegate_task) is the Hermes-native mechanism; write each child's output as a section in a single document instead of writing partial files to disk.
- **FTS5 recall / NL cron / self-evolving skills**: Fall back to native Hermes tools (`session_search` for recall, `cronjob` for scheduling, `skill_manage` for authoring). The Python scripts were conveniences, not requirements.

### Mode selection

Three modes derived from the brand identity lifecycle. Priority: (1) task cue ("create a brand" → identity, "write a post" → content, "make this bolder" → evolve); (2) BrandProfile state (incomplete → identity, complete → content/evolve); (3) explicit user declaration. First match wins.

| Mode | When | Reference files loaded |
|---|---|---|
| **identity** | Creating brand from scratch | color-theory.md, typography-voice.md, voice.md, logo-and-mark.md, identity-system.md, strategy.md |
| **content** | Generating ongoing branded content | voice.md, tone-and-copy.md, mood-vocabulary.md |
| **evolve** | Refining existing identity | identity-system.md, anti-slop.md, touchpoints.md |

## Shared design laws

Apply to every brand identity the skill generates. Vary across brands. Never converge on the same choices.

### Color

- Use OKLCH. Reduce chroma as lightness approaches 0 or 100.
- Never use `#000` or `#fff`. Tint every neutral toward the brand hue.
- Pick a **color strategy** before picking colors. Four steps on the commitment axis:
  - **Restrained** — tinted neutrals + one accent ≤10%. Corporate, professional services.
  - **Committed** — one saturated color carries 30–60% of the surface. Most consumer brands.
  - **Full palette** — 3–4 named roles, each used deliberately. Fashion, lifestyle, food.
  - **Drenched** — the surface IS the color. Entertainment, youth, disruptive brands.
- Category-aware: never pick the same primary color as the brand's top 3 competitors.

### Typography

Font selection follows a 4-step procedure:
1. Write three concrete brand-voice words (physical-object words, not "modern" or "elegant").
2. List the three fonts you'd reach for by reflex. If any are on the reflex-reject list, reject them.
3. Browse a real catalog with the three words in mind. Find the font as a physical object.
4. Cross-check. If the final pick lines up with the original reflex, start over.

Reflex-reject fonts (training-data defaults): Fraunces · Newsreader · Lora · Crimson · Crimson Pro · Playfair Display · Cormorant · Cormorant Garamond · Syne · IBM Plex Mono · IBM Plex Sans · Space Mono · Space Grotesk · Inter · DM Sans · DM Serif Display · Outfit · Plus Jakarta Sans · Instrument Sans · Instrument Serif.

Reflex-reject aesthetic lanes:
- **Tech-minimal blue.** Blue primary, white background, Inter/DM Sans, rounded corners, gradient accents.
- **Editorial-magazine.** Display serif italic + small mono labels + ruled separators + monochromatic restraint.
- **DTC pastel.** Soft pinks, lavender, mint, rounded everything, script accents.

### Voice

- Brand voice is constant. Tone shifts by context. Style is execution.
- Every generated copy must pass the voice-consistency check: remove the brand name — can you still tell which brand this belongs to?
- No "elevate", "empower", "seamless", "leverage", "innovative", "cutting-edge" — these are AI-branding tells.

### Absolute bans

Match-and-refuse. If generated output contains any of these, rewrite.

- **Side-stripe borders.** `border-left/right` > 1px as colored accent.
- **Gradient text.** `background-clip: text` with gradient.
- **Glassmorphism as default.** Blurs and glass cards used decoratively.
- **The hero-metric template.** Big number, small label, gradient accent.
- **Identical card grids.** Same-sized cards repeated endlessly.
- **Purple-blue gradients.** The single most common AI brand cliché.
- **"Empower" word family.** elevate, seamless, leverage, innovative, cutting-edge, transform, unlock.

### The AI slop test

If someone could look at this brand identity and say "AI made that" without doubt, it's failed.

**First-order check:** Can someone guess the color palette from the industry alone? "fintech → navy + gold", "wellness → sage + cream", "tech startup → blue + white" — rework until the answer isn't obvious from the category.

**Second-order check:** Can someone guess the aesthetic family from category-plus-anti-references? "coffee brand that's not brown → editorial-typographic cream", "SaaS that's not blue → terminal-dark mono" — the trap one tier deeper. Rework until both answers are not obvious.

## Commands

All commands use `forge_<subcommand>` format (underscore-delimited) for Telegram bot compatibility. Spaces are not supported in Telegram slash commands.

| Command | Category | Description | Reference |
|---|---|---|---|
| `forge_interview` | Create | Discover brand through multi-round questioning | [references/interview.md](references/interview.md) |
| `forge_forge` | Create | Generate identity kit from brand profile | [references/process.md](references/process.md) |
| `forge_name` | Create | Brand naming and tagline generation | [references/naming.md](references/naming.md) |
| `forge_evolve` | Create | Refine existing identity kit | [references/identity-system.md](references/identity-system.md) |
| `forge_author` | Create | Write brand-specific .py skill to disk | [references/skill-authoring.md](references/skill-authoring.md) |
| `forge_critique` | Evaluate | Brand identity review with heuristic scoring | [references/anti-slop.md](references/anti-slop.md) |
| `forge_audit` | Evaluate | Check identity kit completeness and consistency | [references/identity-system.md](references/identity-system.md) |
| `forge_polish` | Refine | Final quality pass on brand collateral | [references/grid-and-layout.md](references/grid-and-layout.md) |
| `forge_content` | Generate | Generate brand-voice social/marketing content | [references/tone-and-copy.md](references/tone-and-copy.md) |
| `forge_schedule` | Generate | Set up NL cron for brand content | [references/process.md](references/process.md) |
| `forge_analyze` | Analyze | Browser-based visual identity analysis of existing brands → style guide | [merged from brand-aesthetic-analysis] |

### Routing rules

1. **No argument** — render the table above as the user-facing command menu, grouped by category. Ask what they'd like to do.
2. **Argument starts with `forge_`** — strip the `forge_` prefix, extract the subcommand, and load its reference file. Everything after `forge_<subcommand>` is the target context. Only the underscore-delimited format is valid for routing; bare subcommand names are never matched to avoid collisions with other skills.
3. **No match** — general invocation. Apply the setup steps, shared design laws, and the loaded mode reference, using the full argument as context.

Setup (context gathering, mode selection) is already loaded by then; sub-commands don't re-run the skill.

## Hermes-specific

**delegate_task:** The `forge_forge` command fans out to 4 parallel children via `delegate_task` with `max_spawn_depth=2`. Child 1 loads `color-theory.md` and generates the palette. Child 2 loads `typography-voice.md` and selects fonts. Child 3 loads `voice.md` and defines the voice. Child 4 loads `logo-and-mark.md` and constructs logo prompts. Each child writes partial results to the shared filesystem. The parent merges and validates via `src/identity_kit.py`.

**Post-forge visual materialization:** After the identity kit is complete, use **agy (antigravity-design)** to generate the visual HTML presentation and logo image. agy's Gemini Flash 3.5 produces superior visual output vs manual coding. See [references/post-forge-agy.md](references/post-forge-agy.md) for the complete workflow with prompts that worked in production.

**FTS5 recall:** Cross-session brand memory via `python3 forge/scripts/recall.py --search "<query>"`. Example use: "make it more like the coffee brand from last month" searches FTS5 index, retrieves the previous brand profile as reference.

**NL cron:** Recurring content scheduling via `python3 forge/scripts/schedule.py`. Hermes' built-in scheduler runs the generated `brand_<name>_content.py` skill on the specified cadence. Example: "Post Instagram captions every Tuesday at 9am" registers the cron job.

**Self-evolving skills:** The centerpiece. After `forge_forge` completes an identity kit, `src/skill_forge.py` writes `brand_<name>_content.py` to `~/.hermes/skills/`. This file is a standalone Hermes skill containing baked brand constants, `generate_content()`, `generate_weekly_calendar()`, and `get_brand_info()`. The skill IS the deliverable. File tree shows a new .py appearing live. Next cron run uses that skill to generate authentic brand-voice content.

**API key persistence:** On first `forge_forge` invocation, if no image provider key is found in `~/.forge/keys.json`, the agent MUST ask the user for at least one key (Gemini or OpenAI). Store via `KeyStore.save()`. Keys are reused across sessions — never re-ask if keys already exist. Supported providers: `gemini` (Google Gemini 3.1 Flash Image / Nano Banana 2), `chatgpt` (OpenAI GPT Image 2).

## Flavor Text Refinement Protocol

**Initial flavor texts (taglines, voice examples, mission statements, metaphors) are DRAFTS, not final.** The user expects an explicit refinement round after the first pass. Follow this protocol:

1. **After completing forge_forge**, review all flavor texts (lema/tagline, definição de voz, exemplos por contexto, metáfora central, descrição do símbolo).
2. **Present a brainstorming document** mapping each text → original → 3-5 alternatives → your recommended pick.
3. **Flag texts you're least confident about** — the user will override your picks where they disagree.
4. **After user approval**, propagate changes to all documents (manual, DESIGN.md, PRODUCT.md, HTML).
5. **DO NOT treat first-pass flavor texts as final.** The interview captures data; copywriting is a separate, iterative craft. Follow the protocol at [references/flavor-text-refinement.md](references/flavor-text-refinement.md) for brainstorming and selecting alternatives.
6. **When updating agy-generated HTML** (which has base64-embedded images), **patch the existing HTML file** instead of regenerating from scratch. This preserves the embedded images. Use `patch` tool for targeted text replacements.

Common flavor text categories that need refinement:
- **Lema/tagline principal** (appears in hero, manual header, PRODUCT.md)
- **Tagline secundária** (hero subtitle)
- **Definição central de voz** (1-2 sentences)
- **Exemplos de voz por contexto** (newsletter, discussion, welcome, debate)
- **Metáfora central** (1-sentence philosophy)
- **Descrição do símbolo/mascote**
- **Anti-referências list**

## User Preferences

Style guide output format should match user preferences (language, detail level, delivery format). Adjust per session — ask the user or infer from context. Common dimensions to clarify:
- **Language**: Which language should the guide be written in?
- **Format**: Comprehensive deep-dive vs. quick reference?
- **Style**: Tables, ASCII diagrams, hex codes, practical reference data?
- **Delivery**: Downloadable file via MEDIA: path vs. inline?
- **Detail level**: Exhaustive component breakdown vs. high-level overview?

## forge_analyze — Browser-Based Brand Analysis

Systematically inspect a product/brand's visual identity using browser tools and vision analysis, then produce a style guide file.

### Workflow

1. **Scout** — `browser_navigate` to landing, feature, docs, and brand hub pages. Also `web_extract` the main URL for structured text content (pricing, descriptions, value props).
2. **Extract CSS** — Find the site's primary stylesheet URL (grep the page source for `.css` links or `<style>` blocks). Download it with `curl -s "<css-url>"`. Extract exact data:
   - `grep -oP '#[0-9A-Fa-f]{6,8}' | sort | uniq -c | sort -rn` → definitive hex color ranking
   - `grep -oP "font-family:\s*[^;]+" | sort | uniq -c | sort -rn` → definitive font stack
   - `grep -iE 'gradient|button|primary|accent'` → design token hints
   This is more reliable than vision analysis for colors and fonts — vision models approximate; CSS is exact.
3. **See** — `browser_vision` on each page with structured questions about layout, components, decorative elements, interactive states, and overall philosophy. Use vision for spatial reasoning (card layouts, proportions, icon styles) — not for color/font identification.
4. **Analyze the logo** — Download the logo file with `curl`, then use `vision_analyze` on the local file to describe: logo type (wordmark/icon/combo), exact shape elements, color regions, proportions. Cross-reference with CSS colors.
5. **Harvest brand assets** — `browser_get_images` to find logo, icon, favicon, and partner-image URLs. Download actual asset files with `curl` to a dedicated directory (`/opt/data/<brand>-assets/`). Verify files are non-empty. These assets feed downstream production (video, social posts, ads).
6. **Dive** — Click interactive elements, toggle dark mode, scroll to capture full layout.
7. **Organize** — Structure findings: Philosophy → Color → Typography → Layout → Navigation → Components → Icons → Interactions → Voice → Design Principles. Include CSS-derived hex values in the palette section and CSS-derived font families in the typography section. Mark vision-approximated items with "(approx)".
8. **Produce** — Write polished markdown style guide at `/opt/data/<brand>-design-style-guide.md`. Include an **asset manifest** section listing downloaded files and their paths. Deliver the guide via MEDIA: and mention the assets directory.

### Pitfalls
- **Vision model may be unreliable on colors/fonts** — cross-reference with CSS source code. CSS hex values and `@font-face` declarations are definitive; vision is approximate. Use `curl` + `grep` on the site's stylesheet URL for exact data (see Step 2 — Extract CSS). For WordPress/Elementor sites with Litespeed Cache, see `references/wp-elementor-css-extraction.md` for the complete extraction pipeline including Elementor global variables and CORS workarounds.
- **Reflex-reject fonts in existing brands** — the Shared Design Laws' reflex-reject list applies to brand *creation*, not *analysis*. When analyzing an existing brand, document the actual fonts used even if they appear on the reflex-reject list. The brand already chose them; your job is to record them accurately.
- **Asset URLs may be behind lazy-loading** — scroll down fully before running `browser_get_images`
- **Font identification is approximate** — note "appears to be" and suggest fallbacks
- **Different surfaces (marketing vs docs) may use different design systems** — check at least the main site + one sub-page
- **Cross-skill handoff** — when the brand analysis feeds a downstream skill (video, social media, print), pass the asset manifest and style guide path in the downstream context. The harvest step's downloaded files are the raw material.

---

## Pitfalls

⚠️ **Delegation depth limits:** `forge_forge` fans out to 4 parallel children via `delegate_task`, but this requires `max_spawn_depth >= 2` in Hermes config. If delegation is restricted to depth=1, run the 4 pillars sequentially instead: color → typography → voice → logo. The result is equivalent, just slower.

⚠️ **Reference files may not exist:** The skill references `references/interview.md`, `references/process.md`, etc. These are not guaranteed to be present. The `forge_interview` and `forge_forge` workflows work fine without them — conduct the interview via direct conversation questions and synthesize the identity kit from the responses.

- **Reference files may be missing.** The SKILL.md references several `references/<name>.md` files and `forge/scripts/*.py` scripts that may not exist on disk if the skill was freshly created. Check with `skill_view(name, file_path)` before relying on them. When absent, conduct the interview manually via the `references/interview.md` protocol (the agent should already have this file loaded).
- **Delegation spawn depth.** The Hermes-specific `forge_forge` pattern using `delegate_task` with `max_spawn_depth=2` may be blocked if the user's config limits delegation (`max_spawn_depth=1` prevents nesting). Check the user's delegation config before fanning out. When depth is limited, serialize the 4 children (palette → typography → voice → logo) instead.
- **Portuguese/BR interviews.** When the user speaks Portuguese, conduct the interview in Portuguese. Never translate the protocol — the questions should feel natural in the user's language. Store the BrandProfile and output files in the user's language as well.
- **Existing brand assets.** When the user already has a brand manual, logo, color palette, or font stack from a prior identity (e.g., a newsletter brand for the same community), treat them as **constraints and inspiration** — the forge process may keep, evolve, or discard them based on the interview. Always reconcile before generating.
- **Community vs. product brands.** A community brand (people, culture, belonging) is fundamentally different from a product brand (tool, utility, transaction). The forge interview emphasizes *who gathers and why*, not *what problem the tool solves*. Tune the questions accordingly — the persona becomes a member archetype, not a buyer persona.
