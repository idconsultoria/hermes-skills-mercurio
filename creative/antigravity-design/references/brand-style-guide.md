# Brand Style Guide Generation — agy Workflow

Generate a complete visual HTML brand style guide from source materials (Google Docs manual + live website).

## Trigger

User has a brand manual (Google Docs, PDF) and wants a standalone HTML style guide. Uses agy on the host via SSH.

## Workflow

### Phase 1: Research & Compile

1. **Extract Google Doc content** via `google_api.py docs get <doc_id>`
2. **Browse the live website** at `browser_navigate(url)` — extract:
   - Logo URL from `document.querySelector('link[rel="icon"]')?.href`
   - Actual rendered colors (CSS computed values via `browser_console`)
   - Font families used
3. **Download logo** with `curl -s -o /path/file.png <logo_url>`

### Phase 2: Prepare Input Files

Copy source materials to the host:

```bash
# Write condensed reference with ALL brand data
cat > /tmp/brand-data.md << 'DATA'
# MANUAL [NAME] (MASTER V7)
## DNA Visual
- Deep Teal: #003B46
... ALL hex codes ...

## Typography
- Headlines: Bricolage Grotesque
- Body: Nunito Sans

## From live site
- Primary accent: #4AC6D3
- BG colors: #050A0F
DATA

scp /tmp/brand-data.md oracle-host:/home/ubuntu/agy-guide/manual.md
scp /tmp/brand-logo.png oracle-host:/home/ubuntu/agy-guide/logo.png
```

### Phase 3: agy Prompt

Embed ALL data inline — agy cannot read files from disk.

```bash
ssh oracle-host 'timeout 300 env HOME=/home/ubuntu \
  /home/ubuntu/.local/bin/agy -p "[full prompt with ALL specs inline]"'
```

### Phase 4: Retrieve

```bash
scp oracle-host:/home/ubuntu/agy-guide/style-guide.html /opt/data/
ln -sf /opt/data/logo.png /opt/data/id-logo.png  # match HTML expectations
browser_navigate(url="file:///opt/data/style-guide.html")
browser_vision(question="Verifique hero, cores e estrutura")
```

## Mode C — Multi-source (content + reference + logo)

When the user has MULTIPLE files (e.g. markdown content + existing style guide HTML + logo), **agy CAN read them from the host**. Use this instead of inlining everything.

```bash
# 1. Create project dir and copy ALL sources
ssh oracle-host 'mkdir -p /home/ubuntu/agy-project/'
scp /opt/data/conteudo.md oracle-host:/home/ubuntu/agy-project/
scp /opt/data/style-guide.html oracle-host:/home/ubuntu/agy-project/reference.html
scp /opt/data/logo.png oracle-host:/home/ubuntu/agy-project/logo.png

# 2. Prompt — tell agy to read the files
cat > /tmp/prompt.txt << 'PROMPT'
Leia /home/ubuntu/agy-project/conteudo.md (conteúdo base)
Leia /home/ubuntu/agy-project/reference.html (referência de design)
Veja /home/ubuntu/agy-project/logo.png (logo da marca)

Crie um HTML com este conteúdo usando o design system da marca.
PROMPT

# 3. Longer timeout — reading files + generating takes more time
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 420 agy --print "$(cat /tmp/prompt.txt)"'

# 4. Retrieve
scp oracle-host:/home/ubuntu/agy-project/output.html /opt/data/
```

⚠️ **Timeout para Mode C:** usar `timeout 420` (7 min) — agy precisa ler arquivos + gerar, demora mais.

## Light mode + PDF-friendly variant

Quando o usuário quer HTML responsivo com print CSS (para exportar como PDF):

No prompt do agy, incluir estas constraints:

```
Design constraints for this prompt:
- Light mode (NOT dark mode): bg #F7F9FB, cards #FFFFFF, text #0A1118
- Brand colors as ACCENTS only (headings, borders, badges, links)
- Fontes carregadas do Google Fonts via <link>
- NUNCA emojis — substituir cada emoji por SVG inline equivalente, stroke="#4AC6D3" (ou cor da marca), stroke-width="1.5-2", fill="none"
- @media print com -webkit-print-color-adjust: exact e print-color-adjust: exact no seletor universal *
- @media print deve PRESERVAR as cores da marca — NÃO converter para grayscale
- Responsivo (mobile + desktop)
- Print-friendly: page-break-inside: avoid em cards e tabelas
- Tamanho de fonte base 11pt-12pt para leitura confortável em papel
```

⚠️ **agy adiciona `@media print` grayscale por padrão.** agy converte tudo para preto-e-branco no print se não instruído. SEMPRE incluir: "Print styles must PRESERVE brand colors — do NOT convert to grayscale."

## Key Lessons

- `agy -p "prompt"` works (short form of `--print`)
- No tmux needed if agy already authenticated on host
- SCP both ways for file delivery (no sudo for ~/agy-guide/ dir)
- Create symlinks for logo paths agy generates (expects `src="id-logo.png"`)
- 300s timeout sufficient for ~110KB HTML (Mode A); 420s for Mode C multi-source
