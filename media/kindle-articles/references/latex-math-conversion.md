# LaTeX Math → HTML/MathML for Kindle EPUB

Key techniques for converting scientific articles with heavy LaTeX to clean Kindle EPUBs.

## Architecture Decision: MathML + Inline Fallback

- **Display equations** (detected as multi-line `\[...\]`, aligned `\begin{align}`, or single-line with `\displaystyle`): → MathML via `latexml` (or `pylatexenc` fallback)
- **Inline math** (`$...$` fragments embedded in paragraphs): → Unicode + HTML superscripts/subscripts. MathML for inline is fragile on older Kindle firmware.

## Critical Processing Order (avoided nested-brace bugs)

The inline converter must process commands **before** subscript/superscript patterns:

```
1. \mathbb{...}  → ℝ, ℤ, ℂ      (single Unicode char)
2. \mathcal{...} → 𝓕, 𝓖, 𝓗      (single Unicode char)
3. \text{...}    → <span>         (generates HTML)
4. Greek/math → Unicode           (α, β, Π, Σ, ∈, →)
5. Size mods removed              (\big\| → \|)
6. Sub/superscripts → HTML tags   (\_\{...\} → <sub>, \^\{...\} → <sup>)
7. Cleanup: strip remaining \_ \{ \}
```

**Why this order:** `\mathcal{F}` inside `_{y ∈ \mathcal{F}}` — if subscripts are processed first, the regex `[^}]+` incorrectly consumes the `{` from `\mathcal{F}` (it only stops at the first `}`, which is `\mathcal{F}`'s own closing brace). By converting `\mathcal{F}` → `𝓕` (a single char with no `{`/`}`) before subscript matching, the nested-brace problem vanishes.

## Subscript Patterns (post-normalization)

After backslash normalization, all subscripts have `\_` (backslash + underscore):

```python
# Single-letter: h\_ℓ, Π\_S, d\_𝓕
re.sub(r'(\w)\\_([^\W\d_])', r'\1<sub>\2</sub>', text)

# Digits: h\_2
re.sub(r'(\w)\\_(\d)', r'\1<sub>\2</sub>', text)

# Curly-brace: min\_{|S|=k}, h\_{vocab}
re.sub(r'(\w)\\_\{([^}]+)\}', lambda m: f'{m.group(1)}<sub>{m.group(2)}</sub>', text)
```

Note: `\{` in the regex matches literal `{` (bare brace in text), and `\}` matches `}`. The matched text has `\_` (backslash underscore) but bare `{`/`}` braces because LaTeX subscripts `_{...}` use bare braces.

## Superscript Patterns

Text may have `\^{` (backslash-caret) or bare `^{`:

```python
re.sub(r'(?:\w|\))\^\{([^}]+)\}', lambda m: f'{m.group(0)[0]}<sup>{m.group(1)}</sup>', text)
re.sub(r'(?:\w|\))\^([a-zA-Z0-9])', lambda m: f'{m.group(0)[0]}<sup>{m.group(1)}</sup>', text)
```

Use `(?:...)` non-capturing group to handle both word chars and `)` before the caret.

## Backslash Normalization Pitfalls

The raw cache from `web_extract` often has `\\_` (two backslashes) which must be collapsed:

```python
def normalize_backslashes(t):
    # commands: \\mathbb → \mathbb  (double→single before [a-zA-Z])
    t = re.sub(r'\\(\\+)([a-zA-Z{])', lambda m: '\\' + m.group(2), t)
    # specials: \\_ → \_, \\, → \,, \\| → \|
    t = re.sub(r'\\(\\+)([_{},;:.!?()\[\]^~|])', lambda m: '\\' + m.group(2), t)
    return t
```

**Key detail:** The second regex's charset MUST include `|` and `^` (commonly missed). Without them `\\|` remains with multiple backslashes and `\| → |` never fires.

## HTML Escape Gotcha

`html.escape()` is called **before** `convert_inline_math()`. This means:
- Backslashes pass through unchanged (not HTML-special)
- After `\text{...}` → `<span>` conversion inside the converter, subsequent patterns must NOT re-escape the HTML content
- Subscript/superscript lambdas should NOT use `html.escape(m.group(2))` because the content may already contain HTML

## Display Equation Detection Heuristic

For line-by-line processing, detect display equations by counting backslash commands:

```python
def is_display_equation(s):
    backslash = s.count('\\') 
    mathcmds  = sum(s.count(f'\\{c}') for c in 'displaystyle int sum prod lim'.split())
    english   = sum(1 for w in re.findall(r'[a-zA-Z]{2,}', s) 
                    if w.lower() not in STOPWORDS)
    # 0 math cmds + low english = not an equation  
    # high math cmds + moderate english = inline math in paragraph
    # etc.
```

## Image Embedding (fetch + embed)

```python
# For each <img> in source HTML: download, convert to PNG, embed as base64
# or zip into EPUB as OEBPS/images/xxx.png and reference via
# <image href="images/xxx.png" id="img_xxx"/>
```

## Kindle Delivery via Gmail API

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
if not creds.valid:
    creds.refresh(Request())

# Build MIME with EPUB attachment, subject='convert'
service = build('gmail', 'v1', credentials=creds)
service.users().messages().send(userId='me', body={'raw': raw}).execute()
```

Subject **must** be `convert` for Amazon's Kindle pipeline to process it. Attachment is the `.epub` file.
