# Web-article EPUB: markdown images & hyperlinks

When building an EPUB from a web-extracted (not arXiv/LaTeX) article, the
markdown may contain images `![](url)` and links `[text](url)` that the
text-to-HTML pipeline must handle.

## Image detection in text_to_html

In the cache (from `web_extract`), images appear as markdown on their own line:

```markdown
![](https://site.com/path/to/img_xxx.png)
Figure 1: Caption text
```

**Wrong approach** (what failed):
```python
# ONLY matches a bare URL line — never matches ![](url)
if re.match(r'^https://site\\.com[^\\s)]+\\.png\\s*$', st):
```

**Fix**: match `![alt](url)` markdown first, fall back to bare URL:

```python
img_m = re.match(r'^!\\[([^\\]]*)\\]\\(([^\\)]+)\\)\\s*$', st)
if img_m:
    url = img_m.group(2)
    fname = os.path.basename(url)
    if image_exists(fname):
        out.append(f'<div class="figure-img">'
                   f'<img src="images/{fname}" '
                   f'alt="{html.escape(img_m.group(1))}" '
                   f'width="100%"/></div>')
    continue
```

**⚠️ Kindle rendering: do NOT use `width="100%"` as an HTML attribute on `<img>` tags.** On Kindle Paperwhite (and several other EPUB readers), `<img width="100%">` can resolve to 0px when the image sits near a chapter/section page break (the container width hasn't been computed during reflow). Use CSS for sizing instead — the example below shows the corrected pattern:

```python
if img_m:
    url = img_m.group(2)
    fname = os.path.basename(url)
    if image_exists(fname):
        out.append(f'<div class="figure-img">'
                   f'<img src="images/{fname}" '
                   f'alt="{html.escape(img_m.group(1))}"/></div>')
    continue
```

Required CSS (replaces `width="100%"` attribute):
```css
.figure-img img{width:100%;max-width:100%;height:auto;display:block;margin:0 auto}
```

Also remove `page-break-inside:avoid` from `.figure-img` — it interacts badly with images at section boundaries on Kindle and can suppress rendering entirely.

The image **registration** step (scanning all text for image URLs to add to
the EPUB manifest) should use `re.findall(r'https?://[^\\s)]+\\.png'...)`
which extracts the URL even from inside `![](...)` (the `)` stops the match).

## Image format: Kindle silently drops RGBA PNGs

**Critical finding:** Web-source PNG images almost always carry an
alpha channel (PNG color_type=6 / RGBA, even when fully opaque).
Kindle Paperwhite, Kobo, and several common EPUB readers SILENTLY
refuse to render RGBA PNGs — no error, no placeholder, just nothing
rendered. The image `<img>` tag exists in the XHTML, the file is in
the ZIP and registered in the OPF manifest, but it's invisible to
the reader.

**Detection:** Check PNG color_type in the IHDR chunk:

```python
import struct
with open('img.png', 'rb') as f:
    data = f.read(33)
    color_type = data[25]   # 2=RGB, 6=RGBA, 0=Grayscale, 4=Grayscale+Alpha
```

**Fix:** Strip the alpha channel by compositing onto a white background
using Pillow, then save as RGB (color_type=2):

```python
from PIL import Image
img = Image.open(path)
if img.mode == 'RGBA':
    bg = Image.new('RGB', img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])  # use alpha as mask
    bg.save(path, 'PNG')
elif img.mode != 'RGB':
    img = img.convert('RGB').save(path, 'PNG')
```

**When to apply:** Run this conversion on every image in the
epub figures directory BEFORE building the EPUB. The builder script
can auto-convert them during the registration step — but the images
on disk are the canonical source, so in-place conversion is fine
(alpha channel is a waste for e-ink anyway).

For LaTeX→EPUB (PyMuPDF rendering): rendered pixmaps are always RGB
(color_type=2) — this RGBA issue only affects web-extracted articles
where images came from curl/requests downloads of web-origin PNGs
(common: Twitter/X card images, article screenshots, web-optimized
PNGs all carry an alpha channel).

## Pre-processing: Firecrawl HTML→markdown artifacts

`web_extract` uses Firecrawl, which introduces three consistent artifacts
when converting HTML with links and punctuation:

### Artifact 1: Space before punctuation

Firecrawl inserts a space before `.`, `!`, `?`, `;`, `:` in certain contexts:
```
... recurrent connections . Several ...
```

**Fix** — global replace at the start of `text_to_html`:
```python
txt = re.sub(r' ([.!?;:])', r'\1', txt)
```

### Artifact 2: Broken parentheticals after markdown links

When a sentence has `(text [??](url))`, the outer closing `)` ends up
on its own line:
```
We find the J-space ... selectivity ([??](https://site.com/page#fig-x)
). The model can speak fluently...
```

Because the markdown link `[??](url)` consumes the first `)` (closing the
URL paren), leaving the outer `)` orphaned. Firecrawl splits it at the
HTML `<a>` boundary.

**Fix** — merge the orphaned `)` back onto the previous line:
```python
txt = re.sub(
    r'\(([^)]*)\[([^\]]+)\]\(([^)]+)\)\s*\n\s*\)',
    r'(\1[\2](\3))',
    txt
)
```

This only triggers when the full `(...[text](url)\n)` pattern exists
(an opening paren BEFORE the link, and a bare closing paren on the next
line). A plain `[text](url)\n)` (no opening paren) is NOT matched.

### Artifact 3: Period orphaned on its own line after link

When a sentence ends with `[text](url)`, the trailing `.` sometimes
lands on its own line:
```
...established in [??](https://site.com/page#fig-x)
.
```

**Fix** — merge the orphaned `.` onto the previous line:
```python
txt = re.sub(
    r'(\[[^\]]+\]\([^)]+\)[)]*)\s*\n\s*\.',
    r'\1.',
    txt
)
```

The `[)]*` captures any trailing `)` from Fix #2 so both artifacts can be
resolved in sequence without interference.

### Processing order matters

Apply them **in order** in `text_to_html`:
1. Fix #1 (space before punctuation)
2. Fix #2 (broken parens)
3. Fix #2b (orphaned period)

This order ensures Fix #2 merges `([??](url)\n)` into `([??](url))`
before Fix #2b tries to merge a trailing `.` — the `[)]*` in Fix #2b's
regex catches the `)` from the Fix #2 merge if a period also follows.

## Hyperlink conversion ([text](url) → <a>)

Links appear inline within paragraphs:
```
as shown in Figure [??](https://site.com/page#anchor)
we use the method of [Author et al.](https://doi.org/...)
```

**Critical constraint**: links must be converted to `<a>` tags BEFORE
`html.escape()` runs, otherwise the `<` and `>` in the tag get escaped.

**Placeholder strategy**:

```python
# Extract links BEFORE escaping
links_data = []
def save_link(m):
    text = m.group(1)
    url = m.group(2)
    idx = len(links_data)
    links_data.append((text, url))
    return f'\\x00LINK{idx}\\x00'

p = re.sub(r'\\[([^\\]]+)\\]\\(([^\\)]+)\\)', save_link, st)
p = html.escape(p)
for i, (text, url) in enumerate(links_data):
    p = p.replace(
        f'\\x00LINK{i}\\x00',
        f'<a href=\\"{html.escape(url)}\\">'
        f'{html.escape(text)}</a>'
    )
```

**Why this works**: `\\x00` (null byte) is transparent to `html.escape`
(no special HTML chars in it). After escaping, each placeholder is restored
with fully escaped href and visible text.

**Pitfalls**:
- Do NOT put the `def save_link` outside the loop AND re-use the
  `links_data` list — reset it per-line or you'll accumulate stale links
  across paragraphs.
- The regex `r'\\[([^\\]]+)\\]\\(([^\\)]+)\\)'` matches `[text](url)`.
  It assumes well-formed markdown (no nested brackets). Fine for
  web-extracted articles where links are simple.

- **Apply link conversion in EVERY text-processing code path, not just
  regular paragraphs.** Figure captions (lines matching `^Figure \\d+`),
  list items (`* `, `1. `), and blockquotes (`> `) all bypass the regular
  paragraph link converter. If any of these paths contain `[text](url)`,
  the markdown link leaks into the XHTML unmodified. Copy the full
  placeholder-before-escape pattern into each path, or extract the pattern
  into a helper function like `convert_markdown_links(text) → (text,
  links_data)` and reuse it everywhere text hits `html.escape`.
  - **Figure captions** are especially common culprits — cross-references
    like "conventions as in Figure [??](url)" appear inside `<p class="figure-caption">`.
  - If you forget, the bare `[text](url)` survives `html.escape()` unscathed
    (since `[]() ` aren't HTML special chars) and ends up as literal text
    in the EPUB.

## Resolving `[??]` placeholder cross-references

Many web articles (especially Transformer Circuits Thread, distill.pub, and
other research blogs) use `[??](url)` as a JavaScript-filled cross-reference
placeholder. Without JS in the EPUB, `??` renders as literal text inside the
`<a>` tag, looking broken.

**Fix**: Build an anchor map from the cache BEFORE building the EPUB, then
replace `??` link text with actual figure/section references.

### Building the anchor map

Parse the cleaned cache text to associate `#fig-*` URL anchors with their
figure numbers:

```python
ANCHOR_MAP = {}
# Strategy 1: extract from Figure caption lines themselves
for m in re.finditer(
    r'^Figure\s+(\d+):\s*((?:.|\n(?!Figure\s+\d|\[))+)',
    clean, re.MULTILINE
):
    fig_num = m.group(1)
    for url_m in re.finditer(r'\[([^\]]*)\]\(([^\)]+)\)', m.group(2)):
        url = url_m.group(2)
        if '#' in url:
            anchor = url.split('#')[1]
            if anchor not in ANCHOR_MAP:
                ANCHOR_MAP[anchor] = fig_num
```

Strategy 1 catches every anchor explicitly referenced inside another
figure's caption (e.g., "conventions as in Figure [??](#fig-structure)"
inside Figure 50's text maps `#fig-structure → 50`).  Strategy 2 is a
fallback for anchors referenced in body text before their own figure
definition:

```python
# Strategy 2: fallback for anchors referenced outside their own
# figure caption (e.g., in body text before the figure definition)
for m in re.finditer(r'#([a-zA-Z][a-zA-Z0-9_-]+)\)', clean):
    anchor = m.group(1)
    if anchor not in ANCHOR_MAP and 'fig-' in anchor:
        before = clean[:m.start()]
        fig_m = re.findall(r'^Figure\s+(\d+)', before, re.MULTILINE)
        if fig_m:
            ANCHOR_MAP[anchor] = fig_m[-1]
```

### Applying the map during link conversion

In the `save_link` callback (both regular paragraph AND figure caption paths):

```python
def save_link(m):
    text = m.group(1); url = m.group(2)
    # Replace ?? placeholder with actual figure reference
    if text == '??' and '#' in url:
        anchor = url.split('#')[1]
        if anchor in ANCHOR_MAP:
            text = f'Figure {ANCHOR_MAP[anchor]}'
    # Detect unclosed parenthetical (see § below)
    # Only add ) back if there isn't one already in the remaining text
    remaining = m.string[m.end():]
    has_unclosed_paren = (m.start() > 0 and m.string[m.start()-1] == '('
                          and ')' not in remaining)
    links_data.append((text, url, has_unclosed_paren))
    return f'\x00LINK{idx}\x00'
```

And in the restore loop:

```python
for i, (text, url, has_unclosed) in enumerate(links_data):
    close = ')' if has_unclosed else ''
    p = p.replace(f'\x00LINK{i}\x00',
        f'<a href="{html.escape(url)}">{html.escape(text)}</a>{close}')
```

### Handling unbalanced parentheses

The markdown `([??](url))` creates a subtle problem: the `)` after the URL
is consumed by the link syntax `\(...\)` as its closing paren, leaving the
parenthetical `(...)` unbalanced. After link conversion, the `(` remains
bare with no matching `)`:

```
Original: ([??](https://site.com/page#anchor)
After basic conversion: (<a href="...">??</a>     # ← missing closing )
```

**Detection:** In the `save_link` callback, check `m.string[m.start()-1]`
(the character just before `[`). If it's `(`, the closing `)` was consumed
by the regex. BUT: after Fix #2 merged the broken paren, both `)`s (URL
closing + outer closing) end up after the link, and the `)` in remaining
text tells us the outer paren is already balanced. Only add `)` when the
parenthetical is genuinely unclosed:

```python
def save_link(m):
    text = m.group(1); url = m.group(2)
    ...
    # Check if `(` before `[` indicates an unclosed parenthetical
    # Only add ) back if there isn't one already in the remaining text
    remaining = m.string[m.end():]
    has_unclosed_paren = (m.start() > 0 and m.string[m.start()-1] == '('
                          and ')' not in remaining)
    links_data.append((text, url, has_unclosed_paren))
    return f'\x00LINK{idx}\x00'
```

The `remaining` check prevents doubling: after Fix #2 produces
`([??](url))`, the `save_link` regex matches `[??](url)` and remaining
text is `)` (the outer paren) — `)` IS in remaining, so
`has_unclosed_paren = False`. No extra `)` added. Without the check,
the link would output `(<a>...</a>))` — a doubled closing paren.

**Fix:** Append `)` right after `</a>` ONLY when `has_unclosed_paren` is True.
The restored HTML becomes:
```
(<a href="...">Figure N</a>)    # ← balanced and correct
```

This makes the figure reference read as "(Figure N)" — typographically
correct and consistent with the original web article's intent.

---

## Figure caption completeness rules

Figure caption lines (`^Figure \d+`) need ALL of the same processing
that regular paragraphs get, not just link conversion. They commonly
contain:

1. **Markdown links** — `[text](url)` → `<a>` tags (via placeholder strategy)
2. **Bold** — `**text**` → `<b>text</b>`
3. **Italic** — `*text*` → `<i>text</i>`  ⚠️ **Easily missed** — the `^Figure` handler often omits this
4. **Inline math** — `\ell`, `\_`, `\frac`, etc. → Unicode/HTML via `convert_inline_math()` ⚠️ **Also easily missed** — without it, the caption shows raw LaTeX like `J\_\ell`

The missing steps cause:
- Math expressions render as literal `\ell` with backslash-underscore
- Italicised words (common in figure captions) appear as `*text*`
- Both make the caption look broken to the reader

**Order of operations for a complete figure caption handler:**

```python
if re.match(r'^Figure\s+\d+', st, re.IGNORECASE):
    # 1. Extract/restore links (placeholder before escape)
    links_data = []
    def save_link_fig(m):
        ...  # Replace ??, detect paren, store
    p = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', save_link_fig, st)

    # 2. html.escape (safe now — placeholders survive)
    p = html.escape(p)

    # 3. Restore links + fix parens
    for i, (text, url, has_unclosed) in enumerate(links_data):
        close = ')' if has_unclosed else ''
        p = p.replace(f'\x00LINK{i}\x00',
            f'<a href="{html.escape(url)}">{html.escape(text)}</a>{close}')

    # 4. Bold
    p = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', p)

    # 5. Italic  ← MISSED IN INITIAL IMPLEMENTATION
    p = re.sub(r'\*(.+?)\*', r'<i>\1</i>', p)

    # 6. Inline math  ← MISSED IN INITIAL IMPLEMENTATION
    p = convert_inline_math(p)

    out.append(f'<p class="figure-caption">{p}</p>')
```

**Why steps 5 and 6 are critical:** Figure captions frequently mix
LaTeX notation (variable names, math symbols) with italicised terms.
Without `convert_inline_math`, `\ell` renders as-is. Without the italic
pass, `*attention head*` renders with asterisks — both look broken.

---

## Internal cross-reference linking (external → #anchor)

Web-extracted articles (Transformer Circuits, distill.pub) have ALL
cross-references as external URLs like `https://site.com/page#fig-workspace`.
On Kindle, tapping these tries to open the browser — broken UX.

**Goal:** Rewrite external URLs to internal `#anchor` links so tapping a
`(Figure N)` reference navigates within the EPUB. For this to work, the
target anchors must exist as `id` attributes in the XHTML.

### 1. Rewrite links in save_link / save_link_fig

In both `save_link` (regular paragraphs) and `save_link_fig` (figure
captions), add a rewrite step after the `??` placeholder resolution and
paren-balance check:

```python
# Convert external cross-references to internal EPUB links
if url.startswith('https://transformer-circuits.pub/') and '#' in url:
    url = '#' + url.split('#')[1]
```

For a general version that works on any domain:

```python
# Extract anchor from known article domains
for domain in ['transformer-circuits.pub', 'distill.pub', 'arxiv.org']:
    if domain in url and '#' in url:
        url = '#' + url.split('#')[1]
        break
```

This converts `https://transformer-circuits.pub/2026/workspace/index.html#fig-workspace`
to `#fig-workspace` — an internal EPUB link.

### 2. Extract anchors from chapter/section URL markers

The markdown cache uses `[Title](url)` for chapters and `### [Title](url)`
for sections, where `url` contains the original page anchor
(e.g., `https://site.com/page#intro`). Extract and store these anchors to
use as `id` on heading elements.

**In the parser** (after matching CHAPTER_RE/HEADER_RE):

```python
# Extract anchor from the full line
anchor_m = re.search(r'#([a-zA-Z][a-zA-Z0-9_-]+)\)\s*$', s)
if anchor_m:
    anchor = anchor_m.group(1)
```

Store the anchor alongside the title in the chapter/section dict:

```python
# For chapters:
current_chap = {'num': len(chapters)+1, 'title': m.group(1),
                'anchor': anchor, 'intro_text': '', 'sections': []}

# For sections — handle both string (no anchor) and dict (has anchor):
if anchor_m:
    current_sec = {'title': m.group(1), 'anchor': anchor}
else:
    current_sec = m.group(1)  # backwards-compatible string form
```

**In flush()**, handle the mixed section format:

```python
if isinstance(current_sec, dict):
    sec_entry = {'title': current_sec['title'], 'text': t}
    if 'anchor' in current_sec:
        sec_entry['anchor'] = current_sec['anchor']
    current_chap['sections'].append(sec_entry)
else:
    current_chap['sections'].append({'title': current_sec, 'text': t})
```

### 3. Add id to section headings

When rendering chapters and sections, emit the `id` attribute:

```python
# Chapter title:
ch_anchor = ' id="' + html.escape(pc['anchor']) + '"' if pc.get('anchor') else ''
body = f'<h1 class="chapter-title"{ch_anchor}>{html.escape(pc["title"])}</h1>'

# Section title:
sec_anchor = ' id="' + html.escape(sec['anchor']) + '"' if sec.get('anchor') else ''
body = f'<h2 class="section-title"{sec_anchor}>{html.escape(sec["title"])}</h2>'
```

### 4. Build FIG_ANCHORS reverse mapping

`ANCHOR_MAP` maps `anchor → figure_number`. For emitting `<span id="fig-xxx"/>`
targets next to figure captions, you need the reverse: `figure_number → [anchors]`.

```python
FIG_ANCHORS = {}  # figure number → list of fig-* anchors
for anchor, fig_num in ANCHOR_MAP.items():
    if anchor.startswith('fig-'):
        FIG_ANCHORS.setdefault(fig_num, []).append(anchor)
```

### 5. Emit span targets for all fig anchors

In the figure caption handler (`^Figure \d+`), after extracting the first
anchor for the `<p>` id, emit `<span id="fig-xxx"/>` for every fig anchor
belonging to that figure number:

```python
fig_num_m = re.match(r'^Figure\s+(\d+)', st, re.IGNORECASE)
if fig_num_m:
    fig_num = fig_num_m.group(1)
    extra_spans = ''.join(
        f'<span id="{html.escape(a)}"/>'
        for a in FIG_ANCHORS.get(fig_num, [])
        if a != fig_caption_anchor  # skip the one already on <p>
    )
else:
    extra_spans = ''

# Prepend spans before the caption:
out.append(f'{extra_spans}<p class="figure-caption"{fig_caption_id}>{p}</p>')
```

### Result verification

After applying these fixes, verify:

```python
# Count external vs internal links
ext_count = 0  # should be ~4 (GitHub, Neuronpedia, external tools)
int_anchor_count = 0  # should be ~(total fig-anchor links)

for n in zipped_epub.namelist():
    if not n.endswith('.xhtml'): continue
    c = z.read(n).decode()
    for href in re.findall(r'href="([^"]+)"', c):
        if href.startswith('http'): ext_count += 1
        elif href.startswith('#'): int_anchor_count += 1

# Check that every #fig-* link has a matching id target
all_ids = {m.group(1) for m in re.findall(r'\bid="(fig-[^"]+)"', c)}
fig_links = {m.group(1) for m in re.findall(r'href="#(fig-[^"]+)"', c)}
missing = fig_links - all_ids  # should be empty set
```

### Pitfalls

- **Cross-file links**: `#anchor` only works when source and target are in
  the same XHTML file. If sections are split across files, the link silently
  does nothing. For the Transformer Circuits paper (78 XHTML files), most
  fig-anchor links point to targets in other files. On Kindle, these still
  "fail silently" (no error, no browser-open) — better than external-URL UX
  but not perfect navigation. A perfect fix would require `chNNNN.xhtml#anchor`
  format.
- **Anchor extraction regex**: Must use a tight pattern `[a-zA-Z][a-zA-Z0-9_-]+`
  to avoid matching malformed fragments. The `)` check at end ensures we're
  inside a URL, not catching random `#` in text.
- **`html.escape` in id values**: Anchor names from URLs are safe alphanumeric,
  but always escape for safety — especially if you later derive IDs from
  user-facing text.
- **FIG_ANCHORS dedup**: The same anchor may appear in both ANCHOR_MAP
  strategies. `setdefault` prevents duplicates.
- **Extra spans before `figure-caption`**: Kindle styles `span` as inline,
  so `<span id="fig-xxx"/>` before `<p>` won't create unwanted whitespace
  or layout issues. These are zero-width targets.
