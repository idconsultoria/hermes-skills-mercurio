---
name: antigravity-design
description: PRIMARY design tool — Gemini Flash 3.5 generates superior HTML/CSS/visual output vs manual coding. Use this skill FIRST for any design task, not as a fallback or "for robustness". Covers brand presentations, UI mockups, SVG illustrations, prototypes, design systems, and agent-driven design workflows. Installation, authentication, and SSH-specific patterns for headless servers.
category: creative
---

# Antigravity Design — AI Agent for Code Design Tasks

## Trigger
User asks for any visual design output — HTML pages, brand presentations, UI mockups, component libraries, SVG illustrations, prototypes, visual assets. ALSO: when the user says "make an HTML", "create a visual", "apresente em HTML" — agy (Gemini Flash 3.5 via --print mode) is the DEFAULT tool, NOT a fallback. Use it FIRST, not after attempting manual HTML/CSS.

For user Gustavo Mello: agy is the primary design tool. Não use HTML manual quando agy está disponível — você será corrigido se fizer o contrário.

## What is agy?
Antigravity CLI (`agy`) is Google's agent-first development platform (Go binary, no runtime deps). Multi-model (Gemini 3.5 Flash default, also Claude, GPT-OSS). Replaces the deprecated Gemini CLI.

Key design-relevant features:
- **Image generation** — built-in text-to-image for mockups, icons, diagrams
- **Autonomous mode** (`/goal`) — describes a design goal, agy plans + builds + iterates
- **Requirements gathering** (`/grill-me`) — interactive interview before writing code
- **Subagents** — parallel exploration of design alternatives
- **56+ built-in skills** — Chrome DevTools, Modern Web, Firebase for design research
- **Live web search** — real-time design system docs, color palettes, inspiration
- **Workflow skill creator** — save a design workflow as reusable SKILL.md

## Installation

### On Host (Oracle VM) or Local Machine
```bash
# Option A: direct pipe (not available in Hermes container — blocked by smart approval)
curl -fsSL https://antigravity.google/cli/install.sh | bash

# Option B: download first, then run (use this inside Hermes container)
curl -fsSL -o /tmp/agy-install.sh https://antigravity.google/cli/install.sh
bash /tmp/agy-install.sh
```

### Inside Hermes Container
The same download-first approach works. Binary goes to `/opt/data/home/.local/bin/agy`.

Add to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### On Host via SSH
```bash
ssh oracle-host 'curl -fsSL https://antigravity.google/cli/install.sh | bash'
```

## Authentication

**First run requires Google OAuth.** On a headless server, agy prints a URL the user must open in a browser to complete OAuth.

After authentication:
```bash
agy doctor     # verify setup
agy            # launch interactive session
```

## Design Workflows with agy

### 1. Image & Visual Generation (PRIMARY use case)

Generate logos, brand kits, banners, illustrations, and visual assets using Gemini Flash 3.5's built-in image generation. This is the PRIMARY design workflow — not a fallback or prototyping-only mode.

```bash
# Image generation
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --dangerously-skip-permissions --print \
  "Generate a [logo/banner/brand-kit/image] for [subject]. \
   Style: [description]. \
   Colors: [exact hexes]. \
   [details]..."'
```

**Image retrieval**: agy saves generated images to `~/.gemini/antigravity-cli/brain/<uuid>/<name>.png`. Find and copy with:
```bash
ssh oracle-host 'find ~/.gemini/antigravity-cli/brain/ -name "*.png" -mmin -5 2>/dev/null | head -3'
ssh oracle-host 'sudo cp ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png /tmp/'
```

Then pipe to the container via base64 or use the bind mount.

### 2. HTML Generation (brand presentations, landing pages)

Use agy's `--print` mode with Gemini Flash 3.5 to generate standalone HTML files (brand manuals, style guides, presentations). NEVER write manual HTML/CSS for visual output when agy is available — you will be corrected.

**CRITICAL: `--print` syntax.** `--print` takes a STRING argument. Piping (`|`) or redirecting (`<`) stdin does NOT work. Use command substitution:
```bash
# CORRECT:
agy --print "your prompt here"
agy --print "$(cat /tmp/prompt.txt)"

# WRONG (will fail with "flag needs an argument"):
cat prompt.txt | agy --print
agy --print < prompt.txt
```

### 2. HTML Report Generation (pipe mode via SSH) OR editing existing files

**This is the PRIMARY pattern for visual HTML output when agy lives on a remote host.** Use this instead of manual HTML/CSS.

**Two modes — prefer Mode B when a file already exists:**

**Mode A — Generate from scratch (use when no existing file to build on)**
Create a detailed prompt with ALL data inline, send to host, run agy, retrieve output:

```bash
# 1. Write a detailed prompt file with ALL data inline
cat > /tmp/prompt.md << 'PROMPT'
[detailed prompt with ALL data, colors, specs inline]
PROMPT

# 2. SCP to host using SSH alias
scp -F ~/.ssh/config /tmp/prompt.md oracle-host:/tmp/prompt.txt

# 3. Run agy with --print and file content inline
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && timeout 300 agy --print "$(cat /tmp/prompt.txt)"'

# 4. Copy result back
ssh oracle-host 'sudo cp /home/ubuntu/output.html /home/ubuntu/selfhost/hermes/data/'
```

**Mode B — Edit an existing file (preferred when user provides one)**
Copy the file to the host first, then have agy read and modify it. This is FASTER and more accurate than regenerating from scratch because agy preserves the existing structure, embedded images, and design:

```bash
# 1. Copy existing file to host first
scp -F ~/.ssh/config /path/to/original.html oracle-host:/home/ubuntu/file.html

# 2. Write a focused prompt — describe exact edits (line ranges, code to inject, functions to add)
#    Do NOT describe the full design from scratch — just what needs to change
cat > /tmp/prompt.md << 'PROMPT'
Edite /home/ubuntu/file.html.

## Alterações necessárias
[Descreva apenas as mudanças — exatas, específicas, com código quando possível]

### 1. Substituir emojis por SVGs
Adicione esta função no <script> e chame-a no init...
PROMPT

# 3. Use LONGER timeout — existing files with base64 images are often 500KB+
#    timeout 300 WILL fail; timeout 600 is the minimum
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && timeout 600 agy --print "$(cat /tmp/prompt.txt)"'

# 4. Copy edited file back
ssh oracle-host 'sudo cp /home/ubuntu/file.html /home/ubuntu/selfhost/hermes/data/'
```

**When to use each mode:**
- **Mode A (from scratch):** No existing file, or the user asked for a completely new design
- **Mode B (edit existing):** User provides an HTML file and asks for fixes/features. agy reads the file, applies targeted JS/HTML changes, and rewrites it. More efficient because it preserves the base64 logo, existing CSS, and slide structure.

⚠️ **Editing existing files needs more time.** Files with embedded base64 images (500KB+) require `timeout 600` — agy spends significant time reading, parsing, and rewriting the file. With `timeout 300`, agy will time out mid-edit.

⚠️ **For editing, describe JS DOM manipulation, not HTML rewriting.** When adding interactivity (editable cards, emoji replacement, add/remove buttons), tell agy to inject JavaScript functions that modify the DOM at runtime. This avoids agy having to parse and rewrite complex HTML structures. Pattern:
  - Write the JS function as a code block in the prompt
  - Tell agy to "add this function to the script block"
  - Tell agy to "call this function in initSlides()"

⚠️ **Always copy the file to the host BEFORE running agy.** agy's --print mode cannot read files from disk unless they're already on the host filesystem. The sequence is: SCP first → agy edits → SCP back.

**Key rules for report prompts:**
- Embed ALL data inline — agy cannot read files from disk
- Include exact colors (hex), font names, spacing values
- Specify section order and design constraints
- Use the brand's exact palette and typography specs
- For 300s timeout use `timeout 300` wrapper

### 3. Design Requirements (`/grill-me`)
```bash
agy /grill-me "I want a dashboard for my analytics platform"
```

### 4. Image/Mockup Generation (built-in)
```bash
agy "Generate a futuristic dashboard UI mockup with dark theme"
```

### 5. SSH-Specific Workflows (via oracle-host)

**IMPORTANT: `--print` requires an argument string. Pipe (`|`) does NOT work with `--print`. Use `agy --print "$(cat file)"` instead.**

```bash
# SIMPLE: inline prompt (short tasks)
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && agy --print-timeout 120s --print "Create a single HTML file..."'

# COMPLEX: prompt in a file (brand identities, full presentations)
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && timeout 300 agy --print "$(cat /tmp/agy-prompt-iaf.txt)"'

# File delivery to Hermes bind mount
ssh oracle-host 'sudo cp /home/ubuntu/<filename> /home/ubuntu/selfhost/hermes/data/'
```

### 6. Image Generation & File Retrieval

agy's Gemini Flash 3.5 has **built-in image generation** for logos, illustrations, icons. Use `--dangerously-skip-permissions` so agy can write files.

When agy generates an image, it saves PNG/JPEG files to:
```
~/.gemini/antigravity-cli/brain/<uuid>/<descriptive-name>.png
```

```bash
# Image generation (SSH via oracle-host)
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --dangerously-skip-permissions --print \
  "Generate a logo image for [brand]. Style: [description]. Colors: [exact hexes]..."'

# Find the latest generated image
ssh oracle-host 'ls -lt ~/.gemini/antigravity-cli/brain/*/*.png 2>/dev/null | head -3'

# Copy to Hermes bind mount
ssh oracle-host 'sudo cp ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png /home/ubuntu/selfhost/hermes/data/'

# ALTERNATIVE (bind mount permission issues): pipe via base64
ssh oracle-host 'sudo cat ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png | base64' 2>/dev/null | \
  base64 -d > /opt/data/<filename>.png
```

### 7. File Delivery from SSH Host

agy saves output files to its working directory (`/home/ubuntu/` on the host).
The Hermes bind mount (`/home/ubuntu/selfhost/hermes/data/`) is owned by UID
10000 with `0700` permissions — the `ubuntu` user cannot write to it without `sudo`.

**Standard delivery (HTML/text files):**
```bash
ssh oracle-host 'sudo cp /home/ubuntu/<filename> /home/ubuntu/selfhost/hermes/data/'
```

**Fallback (binary files, permission issues):**
```bash
ssh oracle-host 'sudo cat /home/ubuntu/<filename> | base64' 2>/dev/null | base64 -d > /opt/data/<filename>
```

```bash
# Copy file from agy working dir to Hermes bind mount
ssh oracle-host 'sudo cp /home/ubuntu/<filename> /home/ubuntu/selfhost/hermes/data/'

# File is now accessible at /opt/data/<filename> inside Hermes container
# Then send via MEDIA:/opt/data/<filename>
```

## Design Preferences (User Gustavo Mello)

### No emojis — use SVG icons instead
Em qualquer output visual (HTML, slides, dashboards), NUNCA use emojis. Substitua cada emoji por um SVG inline equivalente, com `stroke="#00f2c3"` (ciano) ou a cor de destaque do projeto, `stroke-width="1.5-2"`, `fill="none"`, `viewBox="0 0 24 24"`. Predefinir os SVGs no prompt para que agy os copie e cole — não confie que agy vai criá-los do zero.

### PNG images: always transparent background
Se o output incluir imagens PNG, garantir que usem fundo transparente (PNG-24 com canal alpha). Nunca usar PNG com fundo branco ou colorido sólido.

### Interactive presentations: editable cards + localStorage
Para apresentações que o usuário quer usar durante reuniões (não apenas assistir), incluir:
- Cards editáveis via `contenteditable` nos slides de conteúdo (projetos, oportunidades, etc.)
- Botões de adicionar/remover cards, com ícone SVG de "+" e "X"
- Persistência via `localStorage` — cada conjunto de dados com chave própria
- Tabelas editáveis (contenteditable) com botão "+ Adicionar Linha"
- Checklist interativo no slide final com add/remove/check
- Todo `localStorage` e DOM manipulation isolado em try-catch para não quebrar a navegação

### Logo images in presentations
Quando o usuário fornece uma logo em arquivo (JPG/PNG):
1. Copiar o arquivo para o host via SCP primeiro
2. No prompt do agy, instruir a ler o arquivo e converter para base64
3. Armazenar o base64 em UMA ÚNICA variável JavaScript (`const LOGO_URI = "data:image/...;base64,..."`) e referenciá-la dinamicamente nos `<img>` tags via JS no `DOMContentLoaded`. Isso reduz o tamanho do arquivo em ~78% comparado a inlinar o base64 múltiplas vezes.

## Hermes Style Guide (for agy prompts)

When the user requests visual work, default to this design system:

```css
--primary: #0000FF;
--blue-bg: #F0F5FF;
--blue-border: #CCD9FF;
--gold-accent: #E8B830;
--green-accent: #059669;
--text-dark: #1C1C1E;
--text-muted: #666680;
```

- **Headings:** 'Spectral', Georgia, serif
- **Numbers/Code:** 'Space Mono', monospace
- **Body:** 'Inter', sans-serif
- **Structure:** Executive summary first (KPI cards, donut chart, token table, insights), detailed sections after
- **Report structure:** Hero (gradient blue, gold total), Executive Summary (blue bg, negative margin overlapping hero), Sections (white, blue borders), Footer

## Key Commands Reference

| Command | Purpose |
|---|---|
| `agy` | Launch interactive TUI session |
| `agy --print "prompt"` | One-shot execution, prompt as string arg |
| `agy --print "$(cat prompt.txt)"` | One-shot execution from file |
| `agy /goal "..."` | Autonomous mode — hands-free build |
| `agy /grill-me` | Interactive requirements interview |
| `agy design "..."` | ⚠️ Creative mode — generates NEW artifacts, not review |
| `agy doctor` | Verify setup and auth |

## Reference Files

- `references/agy-session-setup.md` — tmux-based OAuth and interactive session setup
- `references/html-report-workflow.md` — Detailed guide for generating cost/financial HTML reports with Hermes Style Guide
- `references/agy-vs-manual-html.md` — When to use agy vs manual HTML (user prefers agy for all visual output)
- `references/brand-extraction-from-site.md` — Two-phase workflow: extract brand identity from live website via browser, then generate deck with agy
- `references/brand-kit-generation.md` — AI brand board/logo/icon generation patterns
- `references/brand-style-guide.md` — Generate full HTML brand style guide from Google Doc + live site (brand manual → standalone HTML via agy)
- `references/brand-guide-generation.md` — Multi-source pattern: agy reads content.md + reference.html + logo.png from the host. Mode C workflow.
- `references/deck-generation.md` — Multi-slide HTML deck generation from newsletter/report content

## Pitfalls

⚠️ **`--print` syntax is non-obvious.** `--print` takes a STRING argument. These do NOT work and produce "flag needs an argument: -print": `cat prompt | agy --print`, `agy --print < file`, `agy --print` (bare). The CORRECT syntax is `agy --print "prompt"` or `agy --print "$(cat /tmp/file)"`.

⚠️ **Timeout:** For multi-section HTML reports, use `timeout 300`. Default 120s is insufficient — agy takes 30s-4min for complete artifacts. Para gerar HTML com referências (Mode C — multi-source), usar `timeout 420+`. Para editar arquivos HTML grandes (600KB+ com base64), usar `timeout 600` — o tempo extra é necessário para agy ler, processar e reescrever o arquivo completo.

⚠️ **Prefira editar existente a regenerar:** Quando o usuário já tem uma versão de arquivo funcionando, peça o arquivo e passe para agy editá-lo com `timeout 600` em vez de regenerar do zero. Editar preserva ajustes manuais e o resultado é mais fiel ao que o usuário espera. Inclua instruções precisas de edição (funções JS específicas, nomes de classes CSS, estrutura HTML) no prompt.

⚠️ **Zero emojis em apresentações profissionais:** Em slides e apresentações para cliente, substitua TODO emoji por SVG inline equivalente (stroke="#00f2c3" ou cor do brand, stroke-width="1.5-2", viewBox="0 0 24 24"). Ícones SVGs parecem mais profissionais e não dependem de renderização do sistema do usuário. Manter conjunto de SVGs padronizados no prompt.

⚠️ **File reading capability:** agy CAN read files from the host filesystem using its own tools (cat, read_file, ls, grep). The limitation is that you can't PIPE stdin from Hermes container to agy. To have agy read files, put them on the host first (SCP) and include the path in the prompt. For reference documents (markdown content, style guides), use Mode C (multi-source) instead of inlining everything.

⚠️ **One-shot only:** Pipe mode cannot handle follow-up questions or multi-turn. If the output is wrong, fix the prompt and retry.

⚠️ **`agy -p` vs bare `agy`:** `-p` is print mode — non-interactive, cannot handle permission prompts (docker, curl). For code review or interactive workflows, use tmux + bare `agy`.

⚠️ **`agy design` vs `agy <prompt>`:** `agy design` generates NEW artifacts. For reviewing existing code, use bare pipe mode.

⚠️ **Delivery:** Some Telegram clients block .html attachments. If the user reports not receiving the file, zip it: `python3 -c "import shutil; shutil.make_archive('report','zip','.','report.html')"`. Test sending raw .html first — it may work.

⚠️ **Closed source:** agy binary is not open source. Google collects interaction data.

⚠️ **`--dangerously-skip-permissions`:** Use with extreme caution. Without it, agy asks for approval before writing files. Only use when you're certain about the side effects.

⚠️ **Quota exhaustion:** agy shares Google Cloud usage quota with other Gemini services. When quota is exhausted, `agy --print` fails with auth error or empty output. Fall back to manual HTML/CSS — apply brand visual identity (colors, fonts, grid, glow effects) by hand. Design quality must NOT degrade; use the same CSS tokens and component patterns agy would have generated. See `iaf-newsletter` skill for an example of production-quality manual HTML under quota pressure.

⚠️ **First run color scheme:** agy walks through a color scheme picker on first launch. This is cached after first use — subsequent runs skip it. If agy seems stuck on first run, it's waiting for interactive input; use `--print` mode or complete the setup via TTY.

⚠️ **Agy-generated HTML slides: DOMContentLoaded timing can break navigation.** agy places the `<script>` block at the bottom of `<body>` and uses `window.addEventListener('DOMContentLoaded', ...)` to initialize slide navigation, interactive tables, and localStorage features. By the time the browser reaches the script tag, `DOMContentLoaded` may already have fired — the listener never runs, and the slides stay frozen on slide 0. The fix — demand this pattern in the agy prompt for any interactive presentation:

```javascript
function initSlides() {
  // Wrap ALL localStorage/init calls in try-catch
  try { loadTableData(); } catch(e) { console.warn(e); }
  try { loadTodoList(); } catch(e) { console.warn(e); }
  showSlide(0);
}
// Check readyState — if already past 'loading', call directly
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSlides);
} else {
  initSlides();
}
```

⚠️ **Large base64 images inline bloat the HTML file.** When embedding logo images (80KB+ base64), inlining the data URI in every `<img>` tag produces files of 500-600KB. **Fix** — demand a single JS variable pattern in the agy prompt:

```javascript
// In the script section — base64 written ONCE:
const LOGO_URI = "data:image/jpeg;base64,/9j/4AAQ..."; // 80KB, one copy

// In HTML — empty src, class target:
<img class="id-logo" src="" alt="Logo">
<img class="id-logo-small" src="" alt="Logo">

// In JS init — assign dynamically:
document.querySelectorAll('.id-logo, .id-logo-small').forEach(img => { img.src = LOGO_URI; });
```

This reduces file size by ~78% while keeping it self-contained. agy understands this pattern when explicitly requested.

⚠️ **User Gustavo Mello: no emojis in visual outputs.** Em qualquer HTML, slide ou dashboard gerado pelo agy, NUNCA use emojis. Eles devem ser substituídos por SVGs inline. A melhor abordagem é pré-definir os SVGs no prompt do agy para que ele copie e cole — não confiar que agy vai criá-los do zero. Exemplo de como pedir no prompt: 'Substitua CADA emoji pelo SVG correspondente — use esta lista de SVGs: [SVG definitions inline]'.

## Verification
```bash
agy --version        # → 1.0.5+
agy doctor           # → "All checks passed" (requires auth)
```
