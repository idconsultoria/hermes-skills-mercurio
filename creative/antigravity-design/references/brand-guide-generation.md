# Brand Style Guide & Tutorial HTML Generation — agy Workflow

Generate a complete visual HTML brand style guide or branded tutorial from source materials
(Google Docs manual + live website + markdown content).

## Trigger

- User has a brand manual (Google Docs, PDF) and wants a standalone HTML style guide
- User has content in markdown and wants an HTML version styled after a brand guide
- Use agy on the host via SSH — NOT manual HTML

## Workflow

### Phase 1: Research & Compile

1. **Extract Google Doc content** via `google_api.py docs get <doc_id>`
2. **Browse the live website** at `browser_navigate(url)` — extract:
   - Logo URL from `document.querySelector('link[rel="icon"]')?.href`
   - Actual rendered colors (CSS computed values via `browser_console`)
   - Font families used
3. **Download logo** with `curl -s -o /path/file.png <logo_url>`

### Phase 2: Prepare Input Files on Host

Create a working directory on the host and copy ALL source materials:

```bash
# Create working dir
ssh oracle-host 'mkdir -p /home/ubuntu/agy-guide/'

# Copy source content (markdown tutorial, Google Doc export, etc.)
scp /opt/data/source-content.md oracle-host:/home/ubuntu/agy-guide/content.md

# Copy reference style guide (for agy to read as design constraint)
scp /opt/data/referencias/id-consultoria/id-style-guide.html oracle-host:/home/ubuntu/agy-guide/reference.html

# Copy logo
scp /opt/data/logo.png oracle-host:/home/ubuntu/agy-guide/logo.png

# Write the prompt — DON'T inline all content, just tell agy to READ the files
cat > /tmp/agy-prompt.md << 'PROMPT'
CRIE um HTML /home/ubuntu/agy-guide/output.html

## Design Constraints
[exact colors, fonts, layout rules — NO content here, just design system]

## Content Source
O conteúdo está em /home/ubuntu/agy-guide/content.md.
LEIA este arquivo e use o texto EXATAMENTE como está.

## Reference Design
O guia de estilo de referência está em /home/ubuntu/agy-guide/reference.html.
LEIA as primeiras 100 linhas para extrair os design tokens CSS.

## Logo
O logo está em /home/ubuntu/agy-guide/logo.png. Converta para base64.
PROMPT

scp /tmp/agy-prompt.md oracle-host:/tmp/agy-prompt.md
```

### Phase 3: Run agy

```bash
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 420 agy --print "$(cat /tmp/agy-prompt.md)"'
```

**Important:** agy can read files that are on the HOST filesystem. It has its own
tool access (cat, read_file, ls, etc.) when running on the host. You do NOT need
to inline entire documents. Just tell agy the file path and it will read them.
Use timeout 420+ for generating brand HTML + reading reference files.

### Phase 4: Retrieve & Verify

```bash
scp oracle-host:/home/ubuntu/agy-guide/output.html /opt/data/output.html

# Fix logo path if needed (agy often hardcodes filenames)
ln -sf /opt/data/logo.png /opt/data/id-logo.png

# Verify in browser
browser_navigate(url="file:///opt/data/output.html")
browser_vision(question="Verifique hero, cores e estrutura")
```

## Multi-File Read Pattern (Mode C)

> **Don't inline everything.** agy on the host can read multiple files simultaneously:
>   - Source markdown content (read for exact text)
>   - Reference HTML style guide (read for design tokens)
>   - Logo file (read for base64 embedding)
> 
> This is a THIRD mode distinct from "Mode A" (all data inline) and "Mode B" (edit one file).

### When to use each mode

| Mode | Files agy reads | Best for |
|------|----------------|----------|
| **A — All inline** | None (data in prompt) | Short content, no existing reference |
| **B — Edit existing** | One existing HTML | User has a file that needs targeted edits |
| **C — Multi-source** | content.md + reference.html + logo.png | Brand guide from manual, tutorial md → HTML |

## Design Tokens — Quick Reference

When adapting a brand design system, extract these tokens from the reference style guide
and include ONLY these in the prompt (not the whole guide):

```css
/* HERMES AGENT (default, unless specified) */
--primary: #0000FF;
--blue-bg: #F0F5FF;
--font-heading: 'Spectral', serif;
--font-mono: 'Space Mono', monospace;
--font-body: 'Inter', sans-serif;
--gold-accent: #E8B830;

/* ID CONSULTORIA (dark) */
--bg: #050A0F;
--deep-teal: #003B46;
--electric-teal: #66E8F1;
--font-headline: 'Bricolage Grotesque', sans-serif;
--font-body: 'Nunito Sans', sans-serif;
--font-mono: 'IBM Plex Mono', monospace;

/* ID CONSULTORIA (light adaptation) */
--bg-page: #F7F9FB;
--bg-card: #FFFFFF;
--text-primary: #1C1C1E;
--deep-teal: #003B46;
--electric-teal: #4AC6D3;
/* fonts same as dark */
```

## Key Lessons

- `agy -p "prompt"` works (short form of `--print`)
- No tmux needed if agy already authenticated on host
- SCP both ways for file delivery (no sudo for ~/agy-guide/ dir)
- Create symlinks for logo paths agy generates (expects `src="id-logo.png"`)
- 300s timeout sufficient for ~110KB HTML; 420s for multi-file generation
- **agy CAN read files from the host filesystem** — do NOT inline entire documents
