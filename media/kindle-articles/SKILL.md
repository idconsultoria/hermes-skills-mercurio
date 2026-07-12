---
name: kindle-articles
description: "Prepare text content for Kindle — markdown to reflowable EPUB3.

Load this skill when putting research papers, long-form articles, blog posts, or any text-heavy documents on a Kindle. Covers markdown parsing, EPUB3 assembly, TOC generation, and delivery."
version: 1.0.0
author: Hermes
license: MIT
tags: [kindle, articles, epub, research, papers, ebook, ereader]
type: Media
timestamp: 2026-07-07
---

# Kindle Articles

Prepare text-based articles and research papers for Kindle reading. This skill covers the **creation** side (markdown → reflowable EPUB3 with proper text typography), while the delivery pipeline (Gmail API, Drive) is shared with the `kindle-manga` skill.

## When to load

- User asks to put a research paper, article, or blog post on Kindle
- User wants to read a long web article on their e-reader
- User has a cached markdown file of an article and wants an EPUB
- Any "convert this text to Kindle-friendly format" request

## Format choice

| Content type | EPUB type | Rationale |
|--------------|-----------|-----------|
| **Text articles / papers** | **Reflowable EPUB3** | Text needs reflow for font size changes. Chapter/section hierarchy with NCX navigation |
| **Manga / comics** | Fixed-layout EPUB | Use `kindle-manga` skill instead |
| **Mixed (text + figures)** | Reflowable with image placeholders | Figures rarely render well on e-ink; include captions |

## Workflow overview

For **markdown articles**:
```
Source (markdown cache, web_extract, local .md)
  → Parse sections (headers → chapter/section tree)
  → Build EPUB3 (cover → TOC → chapters → sections)
  → Validate structure (epubcheck, ZIP verify)
  → Deliver (Gmail API → Kindle email, or Drive)
```

For **LaTeX / arXiv papers** (see §3):
```
TeX source (arxiv.org/src/<ID>)
  → pandoc .tex → EPUB (handles text, tables, sections)
  → Compiled PDF (arxiv.org/pdf/<ID>) for figure extraction
  → Render TikZ/PDF figures as PNG with PyMuPDF
  → Inject images into EPUB HTML
  → Validate + Deliver
```

### 1. Source acquisition

Articles typically come from:
- **Web extraction**: `web_extract(url)` → cached markdown at `/opt/data/cache/web/*.md`
- **Local markdown files**: `.md`, `.txt`, or raw text
- **Browser scrape**: For sites that serve dynamic content, use `browser_snapshot()` then extract text
- **arXiv TeX source**: `curl -sL "https://arxiv.org/src/<ID>" -o source.tar.gz` — use the `src` URL, which returns a gzipped tarball of all .tex, .bib, and figure files
- **arXiv PDF** (for figure rendering): `curl -sL "https://arxiv.org/pdf/<ID>" -o paper.pdf`

### 2. Parse sections

The article markdown should be parsed into a hierarchical structure:

```python
# Detect chapter-level headings: [Title](url) on its own line
CHAPTER_RE = re.compile(r'^\[([^\]]+)\]\(https?://[^\)]+\)\s*$')

# Detect sub-section headings: ### [Title](url)  
SECTION_RE = re.compile(r'^#+\s*\[([^\]]+)\]\(https?://[^\)]+\)\s*$')

# State machine: chapter → section → content
chapters = []  # [{title, intro_text, sections: [{title, text}]}]
```

Key parsing rules:
- **Chapter heading** on its own line starts a new chapter; anything before the first subsection is chapter `intro_text`
- **Sub-section heading** (`### [...]`) ends the chapter intro and starts a new section
- **Regular content** goes to the current buffer (intro or section)
- **Append chapter to list** when encountering the next chapter heading (or at end of file)
- See `references/parse-sections-technique.md` for detailed state machine

### 3. Math rendering for web-extracted LaTeX (non-pandoc)

For articles extracted via `web_extract` that contain inline LaTeX (`\min`, `\mathcal`, `\Pi`, `\frac`, etc.), the article undergoes a **normalize → convert** pipeline that renders math as Unicode + HTML `<sub>`/`<sup>`, with display equations converted to MathML via `latex2mathml`.

**Two-phase approach:**

| Context | Method | Tool |
|---------|--------|------|
| **Display equations** (standalone; ≥2 strong LaTeX commands or heavy math density) | Converted to MathML | `latex2mathml` via `subprocess.check_output` |
| **Inline math** (short fragments in paragraph text) | Converted to Unicode + HTML | `convert_inline_math()` function |

**Display-equation detection heuristics** (prevents false positives on prose containing `\texttt` etc.):

```python
STRONG_NAMES = ['mathbb', 'frac', 'partial', 'sum', 'int', 'displaystyle',
                'operatorname', 'widehat', 'widetilde', 'limits', 'nolimits']
MODERATE_NAMES = ['ell', 'mathbf', 'mathcal', 'text', 'left', 'right',
                  'big', 'Big', 'bigg', 'Bigg', 'to', 'mapsto', 'rightarrow',
                  'leftarrow', 'nabla', 'approx', 'equiv', 'sim',
                  'prod', 'coprod', 'bigcup', 'bigcap', 'bigvee', 'bigwedge']

def is_display_equation(line):
    s = count_cmd(line, STRONG_NAMES)   # count of strong cmd hits
    m = count_cmd(line, MODERATE_NAMES) # count of moderate cmd hits
    eng_words = count of English words without backslash in line
    # returns True if any heuristic triggers — see references/latex-math-epub.md
```

**Backslash-normalisation (critical first step):**

Web-extracted text contains inconsistent escaping (`\\\\min`, `\\mathcal`, `\\_` etc.). A dedicated normaliser collapses these to a consistent single-backslash form **before** math conversion:

```python
def normalize_backslashes(t):
    # commands: \\\\mathbb → \\mathbb, \\\\frac → \\frac, etc.
    t = re.sub(r'\\\\(\\\\+)([a-zA-Z{])', lambda m: '\\\\' + m.group(2), t)
    # specials: \\\\_ → \\_, \\\\, → \\,, \\\\; → \\;, etc. (includes | for \\|)
    t = re.sub(r'\\\\(\\\\+)([_{},;:.!?()\\[\\]^~|])', lambda m: '\\\\' + m.group(2), t)
    return t
```

**`convert_inline_math` processing order (order matters — nested-brace avoidance):**

1. `\\frac{a}{b}` → `a/b` (simplify for inline)
2. `\\mathbb{...}`, `\\mathcal{...}` → Unicode (MUST run before subscripts to prevent `\\mathcal{F}` breaking nested-brace matching)
3. `h_\\text{...}` subscript pattern → `h<sub><span class=\"textrm\">...</span></sub>`
4. `\\text{...}` → `<span class=\"textrm\">...</span>`
5. Greek letters + math commands (`\\mu`→μ, `\\min`→min, `\\ell`→ℓ, etc.)
6. Size modifiers, `\\|`→`|`, `\\langle`→`⟨`, `\\rangle`→`⟩`
7. `\\underbrace`, `\\widehat`, `\\widetilde`, `\\operatorname`
8. **Subscripts/superscripts** (now safe because brace commands are already resolved):
   - `(\\w)\\_([^\\W\\d_])` → `\\1<sub>\\2</sub>` (single letter: `Π\\_S`, `h\\_ℓ`, `d\\_𝓕`)
   - `(\\w)\\_([\\d])` → `\\1<sub>\\2</sub>` (digit subscript)
   - `(\\w)\\_\\{([^}]+)\\}` → `\\1<sub>\\2</sub>` (curly-brace: `min\\_{|S|=k}`)
   - `(\\w)\\^\\{([^}]+)\\}` → `\\1<sup>\\2</sup>` (superscripts)
- `(?:\\w|\\))\\^\\{([^}]+)\\}` → `<sup>` (bare caret: `)^{-1}`)
- `(?:\\w|\\))\\^([a-zA-Z0-9])` → `<sup>` (bare caret single-char: `x^2`)
- Cleanup: strip stray `\\_`, `\\{`, `\\}`

**Common pitfalls:**

- **Backslash count in Python string literals:** `'\\_\\{'` produces ONE backslash + underscore + ONE backslash + brace. `'\\\\_\\\\{'` produces TWO backslashes + underscore + TWO backslashes + brace. This is the most common bug — triple-check when writing replacement strings.
- **`html.escape` inside subscript lambdas:** If the content already contains HTML (from `\\text{...}` conversions), escaping will double-escape it. Only call `html.escape` on raw LaTeX content, not on partially converted text.
- **`|` not in normalize set:** `\\|` survives if `|` isn't in the special-chars regex. Always include it.
- **`{}` vs `\\{\\}`:** The normalized text uses bare braces `{` `}` for subscript groups, but `\\_` (backslash-underscore) consistently. The subscript regex `(\\w)\\_\\{([^}]+)\\}` uses `\\{` to match `{` in text — NOT `\\\\\\{` which would match `\\{`.
- **Nested `\\mathcal{...}` inside `_{...}`:** If `\\mathcal{...}` conversion runs AFTER subscript matching, the inner `{` from `\\mathcal\\{F\\}` breaks `[^}]+` which stops at the first `}`, causing `\\mathcal{F</sub>}`. Always convert `\\mathbb`/`\\mathcal` first.

See `references/latex-math-epub.md` for the full `convert_inline_math` function with step-by-step ordering, and `references/parse-sections-technique.md` for section parsing.

**Markdown images & hyperlinks** in web articles: See `references/web-article-media.md` for handling `![](url)` → `<img>` and `[text](url)` → `<a>` with the placeholder-before-escaping strategy, **plus internal cross-reference linking**: converting external `https://...#anchor` URLs to `#anchor` links and adding `id` targets to headings and figure captions.

### 4. LaTeX / arXiv papers (pandoc + figure rendering)

For LaTeX source documents (arXiv papers, conference preprints), use **pandoc** as the primary converter instead of the hand-built EPUB3 approach above. Pandoc handles LaTeX structure (sections, citations, cross-refs, tables, math) far better than a custom parser.

**Prerequisites:**
```bash
# Install pandoc binary (ARM64 Debian — get the right arch!)
curl -sL "https://github.com/jgm/pandoc/releases/download/3.6.4/pandoc-3.6.4-linux-arm64.tar.gz" -o /tmp/pandoc.tar.gz
tar xzf /tmp/pandoc.tar.gz -C /tmp/
# Path: /tmp/pandoc-3.6.4/bin/pandoc
```

**Basic conversion:**
```bash
cd /path/to/extracted/tex
/tmp/pandoc-3.6.4/bin/pandoc main.tex -o output.epub \
  --to epub3 \
  --metadata title="Paper Title" \
  --metadata author="Authors"
```

**Figure handling (key challenge):** Pandoc cannot render TikZ diagrams — they produce empty `<figure>` tags. External PDF figures get embedded as `<embed src="file.pdf">` which Kindle cannot display. Fix both by rendering the compiled arXiv PDF as PNG images and injecting them:

1. Download the compiled PDF from `arxiv.org/pdf/<ID>`
2. Install `pymupdf` (PyMuPDF) via `uv pip install pymupdf`
3. Render figure pages as high-DPI PNGs: `page.get_pixmap(dpi=300)`
4. Smart-crop with Pillow to remove margins
5. Post-process the pandoc EPUB HTML:
   - Replace `<embed src="...pdf">` with `<img src="media/fig-NAME.png">`
   - Insert `<img>` before `<figcaption>` inside empty TikZ `<figure>` tags
6. Update the OPF manifest to reference the new image files

See `references/arxiv-latex-to-epub.md` for the full pipeline script and detailed steps, including table conversion and precise figure cropping.

**Pitfalls specific to LaTeX→EPUB:**
- **TikZ figures produce empty figures** — pandoc outputs `<figure>\n<figcaption>` with no image. You must render from the compiled PDF and inject images.
- **Embedded PDF figures** → pandoc produces `<embed src="file.pdf">` — must be replaced with `<img>` referencing a PNG conversion.
- **Multi-file LaTeX** — pandoc follows `\input{}` directives, so `main.tex` alone is sufficient. No need to merge files first.
- **`tabularx` tables produce `<div class="tabularx">` not `<table>`** — pandoc renders `tabularx` environments as `<div>` with plain text rows separated by `<br />` and cells by `&amp;`. Must be post-processed to proper HTML `<table>` (see `references/arxiv-latex-to-epub.md` §Table conversion). Simple `{tabular}` (no X columns) renders correctly.
- **Colspec `<span>` has nested tags** — pandoc outputs colspecs as `<span>p<span>0.045</span>p<span>0.20</span>Yc</span>`. A naive regex `^.*?</span>` breaks on the inner `</span>`. Use depth-aware span stripping.
- **Column count from first row, not colspec** — don't try to count columns by parsing the colspec string. Use `first_row.count('&amp;') + 1` — it's reliable, the colspec is not.
- **Citations** — pandoc drops `.bbl` bibliography content. The reference list may be sparse; check after conversion.
- **Math** — pandoc renders math as `<span class="math inline">` or `<span class="math display">`. It's readable but not rendered. Acceptable for Kindle text reading.
- **Gmail attachment limit** — 25 MB. A 136-page paper with 7 full-color figures comes to ~5 MB, well within limit.

### 4. Build EPUB3

Create a proper EPUB3 using Python's standard library (`zipfile`) — no external tools needed.

**Structure:**
```
EPUB/
├── mimetype                    (ZIP_STORED, first entry)
├── META-INF/
│   └── container.xml
└── OEBPS/
    ├── content.opf             (metadata + manifest + spine)
    ├── toc.ncx                  (navigation control XML)
    ├── css/style.css            (Kindle-optimized CSS)
    └── xhtml/xhtmlNNNN.xhtml    (one per chapter/section)
```

**CSS optimized for Kindle e-ink text reading:**
- Font: `Georgia, "Times New Roman", serif` — best serif on e-ink
- `text-align: justify` with `hyphens: auto` — proper justification
- `text-indent: 1.2em` — paragraph indent (not spacing between paragraphs)
- `line-height: 1.5` — comfortable reading
- `page-break-before: always` on chapter titles
- `widows: 2; orphans: 2` — prevent single lines at page edges
- Code blocks: `"Courier New", monospace` with subtle left border

See `templates/kindle-text-css.txt` for the full CSS.

**Key metadata for OPF:**
```xml
<meta property="rendition:layout">reflowable</meta>
<meta property="rendition:orientation">auto</meta>
<meta property="rendition:spread">auto</meta>
```

### 5. Validate

Check EPUB integrity before sending:
- `zipfile.ZipFile` opens without error
- No duplicate filenames in ZIP
- Each spine item has a corresponding manifest entry
- NCX has entry for every chapter + section
- Cover page is first in spine

### 6. Delivery

Use the Gmail API approach from `kindle-manga`'s `references/gmail-kindle-delivery.md`:

```python
# Send EPUB to Kindle email via Gmail API
# Token at /opt/data/google_token.json
# Kindle email from kindle-manga: gustavomelloenciv_0yDkTw@kindle.com
```

Subject line: the article title — no "Convert" needed for EPUB (Amazon accepts natively).

## Scripts

- `scripts/arxiv-latex-to-kindle.py` — Complete end-to-end pipeline: pandoc conversion, figure extraction with precise bbox detection, tabularx→table conversion, EPUB rebuild, and Kindle delivery. Copy to the TeX workspace, define your `FIGURES` list, and run.

## Templates

- `templates/kindle-text-css.txt` — Complete CSS for text-heavy Kindle EPUBs

## References

- `references/parse-sections-technique.md` — Section parsing state machine with real examples from the Transformer Circuits article (360K chars, 10 chapters, 66 sections)
- `references/arxiv-latex-to-epub.md` — LaTeX→EPUB pipeline with: precise figure bbox detection, depth-aware tabularx→table conversion, multi-figure page splitting, EPUB rebuild and Kindle delivery
- `kindle-manga` skill's `references/gmail-kindle-delivery.md` — Gmail API delivery to Kindle

## Pitfalls

- **Chapters not appended**: The parse loop must explicitly `chapters.append(chapter)` when hitting the next chapter heading, not just update the current chapter object. A chapter built but never appended = zero chapters in output.
- **Duplicate filenames**: Cover page and first chapter must not share the same XHTML filename. Increment a counter for each page, don't hardcode filenames.
- **ZIP_STORED for mimetype**: The `mimetype` file must be first in the archive and stored uncompressed. Use `ZIP_STORED` from `zipfile`.
- **Over-lapping text**: When a chapter has both intro text AND sub-sections, the intro text must NOT include the text of subsections. The state machine must stop collecting intro text at the first sub-section heading.
- **SKIP_LINKS**: Top-of-page links (site headers, "Authors", "Published", etc.) must be filtered out so they don't create phantom chapters.
- **NCX depth**: For articles with deep nesting, depth=2 (chapter + section) is sufficient. Deeper subsections can be omitted from NCX to avoid clutter.
- **Gmail attachment limit**: 25 MB total message size. For articles, this is rarely an issue (our 360K char article produced a 171 KB EPUB). Only relevant for articles with embedded images.
- **Markdown images `![](url)` in web cache**: Image URLs inside `![](...)` need their OWN detection in `text_to_html` — the regex `^https://...png$` doesn't match markdown-wrapped URLs. Match `!\\[([^\\]]*)\\]\\((https?://[^\\)]+)\\)` instead.
- **Hyperlink conversion before `html.escape`**: `html.escape` destroys `<a>` tags. Use a placeholder strategy: extract `[text](url)` → store → `html.escape` → restore as `<a href="...">text</a>`.  ⚠️ Apply this pattern in **every** text-processing code path (regular paragraphs, figure captions, list items, blockquotes). Figure captions containing cross-references like "as in Figure [??](url)" are the most commonly missed path — the `^Figure \\d+` handler often skips link conversion.
- **`[??]` placeholder cross-references** (Transformer Circuits, distill.pub, etc.): `??` is a JS-filled placeholder that stays as literal text in EPUB. Build an anchor map from the cache to replace `??` with actual figure numbers (e.g., `Figure 22`). See `references/web-article-media.md` §Resolving `[??]` placeholder cross-references for the anchor-map construction, the paren-balance fix, and the figure-caption completeness rules (italic + math conversion are commonly missed in the `^Figure` handler).
- **Bare `^{` superscript**: Web-extracted text may have `^{...}` without a backslash before `^`. Add both `(?:\\\\w|\\\\))\\\\^\\\\{...\\\\}` (bare) and `(?:\\\\w|\\\\))\\\\\\\\\\\\^\\\\{...\\\\}` (escaped) patterns. Update your `convert_inline_math` function's superscript step accordingly.
- **PNG RGBA (alpha channel) silently invisible on Kindle**: Web-origin PNGs almost always have color_type=6 (RGBA) even when fully opaque. Kindle Paperwhite, Kobo, and most EPUB readers SILENTLY drop RGBA images — the `<img>` tag is there, the file is in the ZIP and OPF manifest, but nothing renders. Fix: strip the alpha channel with Pillow before packing the EPUB: `Image.new('RGB', img.size, (255,255,255)).paste(img, mask=img.split()[3])`. See `references/web-article-media.md` §Image format for the full recipe. For LaTeX→EPUB (PyMuPDF): rendered pixmaps are always RGB — no conversion needed.
- **`display:block` em `<img>` some com imagem no Kindle sem MathML na página**: `display:block;width:100%;max-width:100%;height:auto` funciona em browsers, mas no Kindle renderiza imagens invisíveis quando a página não contém MathML. A diferença é binária: com MathML na página o Kindle usa engine web completo (que renderiza `display:block` corretamente); sem MathML, o engine simplificado esconde a imagem. **Fix:** use `display:inline-block` em vez de `display:block`, remova `width:100%` (só `max-width:100%` basta), e centralize via `text-align:center` no container pai: `.figure-img img{max-width:100%;height:auto;display:inline-block;margin:0;vertical-align:middle}`. O container `.figure-img` deve ter `text-align:center`. Ver `references/web-article-media.md` §Image detection.
