# LaTeX math → EPUB conversion

Complete technique for converting web-extracted articles with LaTeX math into Kindle-readable content (Unicode + HTML + MathML).

## Pipeline overview

```
Raw markdown with LaTeX (from web_extract)
  → normalize_backslashes()      # collapse \\cmd → \cmd consistently
  → text_to_html()               # paragraph-by-paragraph
    ├─ is_display_equation()?    # heuristics for display vs inline
    │   ├─ Yes → latex2mathml → <div class="equation"><math>...</math></div>
    │   └─ No  → html.escape() → convert_inline_math() → <p>...</p>
  → EPUB assembly (zipfile)
```

## normalize_backslashes()

The web-extracted markdown has inconsistent escaping — `\\\\min`, `\\_`, `\\{`, `\\\\mathcal` etc. This must be normalised FIRST:

```python
def normalize_backslashes(t):
    # commands:  \\\\mathbb → \\mathbb,  \\\\frac → \\frac, etc.
    t = re.sub(r'\\\\(\\\\+)([a-zA-Z{])', lambda m: '\\\\' + m.group(2), t)
    # specials:  \\\\_ → \\_, \\\\, → \\,, \\\\; → \\;, etc.
    t = re.sub(r'\\\\(\\\\+)([_{},;:.!?()\\[\\]^~|])', lambda m: '\\\\' + m.group(2), t)
    return t
```

Both regexes collapse `\\N`+ → `\\` (N≥2) to `\\` (single backslash). The second regex handles `|` — without it, `\\\\|` (4 backslashes + pipe) survives as `\\\\|` and `result.replace('\\\\|', '|')` can't match it.

After normalisation, the text has single backslashes throughout: `\\min`, `\\mathcal{F}`, `\\_`, `\\{`, `\\}` (but braces may also be bare `{` `}`).

## convert_inline_math() — order of operations

Processing ORDER is critical. Converting `\\mathcal{...}` AFTER subscript matching causes the inner `{` to break `[^}]+` patterns. The order below is tested against a real 360K-char Transformer Circuits article with ~200 equation fragments.

```python
def convert_inline_math(text):
    result = text

    # 1. \\frac simplification — inline only
    result = re.sub(r'\\\\frac\\{([^}]+)\\}\\{([^}]+)\\}', r'\\1/\\2', result)

    # 2. Brace commands MUST run BEFORE subscripts to prevent nested-brace bugs
    # \\mathbb{R} → ℝ, \\mathcal{F} → 𝓕
    bb_map = {'R':'ℝ','N':'ℕ','Z':'ℤ','Q':'ℚ','C':'ℂ','F':'ℱ','E':'𝔼','P':'ℙ','H':'ℍ'}
    for c, u in bb_map.items():
        result = result.replace(f'\\\\mathbb{{{c}}}', u)
    cal_map = {'A':'𝓐','B':'𝓑','C':'𝓒','D':'𝓓','E':'𝓔','F':'𝓕','G':'𝓖','H':'𝓗',
               'I':'𝓘','J':'𝓙','K':'𝓚','L':'𝓛','M':'𝓜','N':'𝓝','O':'𝓞',
               'P':'𝓟','Q':'𝓠','R':'𝓡','S':'𝓢','T':'𝓣','U':'𝓤','V':'𝓥',
               'W':'𝓦','X':'𝓧','Y':'𝓨','Z':'𝓩'}
    for c, u in cal_map.items():
        result = result.replace(f'\\\\mathcal{{{c}}}', u)

    # 3. h_\\text{...} subscript pattern — MUST run before general \\text conversion
    result = re.sub(
        r'(\\w)\\\\?_\\\\text\\{([^}]*)\\}',
        lambda m: f'{m.group(1)}<sub><span class=\\"textrm\\">{html.escape(m.group(2))}</span></sub>',
        result
    )
    # also catch bare-underscore-brace: h{\\text{model}}
    result = re.sub(
        r'(\\w)_{\\\\\\text\\{([^}]*)\\}}',
        lambda m: f'{m.group(1)}<sub><span class=\\"textrm\\">{html.escape(m.group(2))}</span></sub>',
        result
    )

    # 4. General \\text → <span> (runs after subscript pattern consumed its target)
    result = re.sub(r'\\\\text\\{([^}]*)\\}',
                   lambda m: f'<span class=\\"textrm\\">{html.escape(m.group(1))}</span>', result)

    # 5. Greek letters
    greek = { 'alpha':'α', 'beta':'β', ... }  # full map below
    for n, u in greek.items():
        result = result.replace('\\\\' + n, u)

    # 6. Math commands (\\ell→ℓ, \\min→min, \\cos→cos, etc.)
    math_cmds = {
        'ell': 'ℓ', 'partial': '∂', 'nabla': '∇', 'infty': '∞',
        'cdot': '·', 'cdots': '…', 'dots': '…', 'forall': '∀', 'exists': '∃',
        'emptyset': '∅', 'subset': '⊂', 'supset': '⊃', 'subseteq': '⊆',
        'supseteq': '⊇', 'cap': '∩', 'cup': '∪', 'in': '∈', 'notin': '∉',
        'to': '→', 'mapsto': '↦', 'implies': '⇒', 'iff': '⇔',
        'approx': '≈', 'equiv': '≡', 'sim': '∼', 'ne': '≠', 'le': '≤', 'ge': '≥',
        'pm': '±', 'times': '×', 'div': '÷', 'circ': '∘', 'bullet': '•',
        'oplus': '⊕', 'otimes': '⊗', 'dagger': '†', 'ddagger': '‡',
        'min': 'min', 'max': 'max', 'argmin': 'arg min', 'argmax': 'arg max',
        'cos': 'cos', 'sin': 'sin', 'tan': 'tan', 'log': 'log', 'exp': 'exp',
        'sum': '∑', 'prod': '∏', 'int': '∫',
    }
    for n, u in math_cmds.items():
        result = result.replace('\\\\' + n, u)

    # 7. Size modifiers + vertical bars
    result = re.sub(r'\\\\[bB]ig[lr]?', '', result)
    result = re.sub(r'\\\\[bB]igg[lr]?', '', result)
    result = result.replace('\\\\|', '|')
    result = result.replace('\\\\vert', '|')
    result = result.replace('\\\\Vert', '‖')
    result = result.replace('\\\\lvert', '|').replace('\\\\rvert', '|')
    result = result.replace('\\\\langle', '⟨').replace('\\\\rangle', '⟩')
    result = re.sub(r'\\\\underbrace\\{([^}]*)\\}_\\{([^}]*)\\}', r'\\1 (\\2)', result)
    result = re.sub(r'\\\\widehat\\{([^}]*)\\}', r'\\1', result)
    result = re.sub(r'\\\\widetilde\\{([^}]*)\\}', r'\\1', result)
    result = re.sub(r'\\\\operatorname\\{([^}]*)\\}', r'\\1', result)

    # 8. Subscripts (now safe — no nested brace commands remain)
    result = re.sub(r'(\\w)\\\\_([^\\W\\d_])', r'\\1<sub>\\2</sub>', result)       # h\\_ℓ, Π\\_S, d\\_𝓕
    result = re.sub(r'(\\w)\\\\_(\\d)', r'\\1<sub>\\2</sub>', result)                # h\\_2
    result = re.sub(r'(\\w)\\\\_\\{([^}]+)\\}', lambda m: f'{m.group(1)}<sub>{m.group(2)}</sub>', result)  # min\\_{|S|=k}

    # Superscripts (both backslash-escaped and bare caret)
    result = re.sub(r'(?:\\w|\\))\\\\\\\^\\{([^}]+)\\}', lambda m: f'{m.group(0)[0]}<sup>{m.group(1)}</sup>', result)
    result = re.sub(r'(?:\\w|\\))\\^\\{([^}]+)\\}', lambda m: f'{m.group(0)[0]}<sup>{m.group(1)}</sup>', result)
    result = re.sub(r'(?:\\w|\\))\\\\\\\^([a-zA-Z0-9])', lambda m: f'{m.group(0)[0]}<sup>{m.group(1)}</sup>', result)
    result = re.sub(r'(?:\\w|\\))\\^([a-zA-Z0-9])', lambda m: f'{m.group(0)[0]}<sup>{m.group(1)}</sup>', result)

    # 9. Cleanup
    result = re.sub(r'\\\\([\\\\,;:!])', r'\\1', result)  # \\,, \\;, \\: → , ; :
    result = re.sub(r'\\\\(\\s)', r'\\1', result)          # \\  → (space)
    result = result.replace('\\\\_', '_')                   # stray \\_ → _
    result = result.replace('\\\\{', '{').replace('\\\\}', '}')  # stray braces
    result = result.replace('\\\\ ', '')                    # \\  → empty

    return result
```

## Display-equation detection

Display equations use `latex2mathml` for proper MathML rendering. Heuristics prevent false-positive detection on prose:

```python
STRONG_NAMES = ['mathbb', 'frac', 'partial', 'sum', 'int',
                'displaystyle', 'operatorname', 'widehat', 'widetilde',
                'limits', 'nolimits']

MODERATE_NAMES = ['ell', 'mathbf', 'mathcal', 'text', 'left', 'right',
                  'big', 'Big', 'bigg', 'Bigg', 'to', 'mapsto', 'rightarrow',
                  'leftarrow', 'nabla', 'approx', 'equiv', 'sim',
                  'prod', 'coprod', 'bigcup', 'bigcap', 'bigvee', 'bigwedge']

def is_display_equation(line):
    if not line or len(line) < 8: return False
    if line.startswith(('Figure ', 'http', '* ')): return False

    s = count_cmd(line, STRONG_NAMES)
    m = count_cmd(line, MODERATE_NAMES)

    eng_words = sum(1 for w in line.split()
                    if re.match(r'^[A-Za-z]', w) and '\\\\' not in w)

    # Heuristics (tested on ~10K lines of Transformer Circuits prose)
    if s >= 2: return True
    if s >= 1 and eng_words <= 3: return True
    if s >= 1 and m >= 4 and eng_words <= 6: return True
    if s >= 1 and m >= 2 and eng_words <= 5: return True
    if m >= 5 and eng_words <= 2: return True
    if m >= 3 and eng_words <= 1: return True
    if eng_words == 0 and s + m >= 2: return True
    return False
```

## Latex2MathML setup

```bash
uv pip install latex2mathml
```

Usage:
```python
import subprocess, json
mml = subprocess.check_output(
    ['python3', '-c', f'import latex2mathml.converter as c; ' +
     f'print(c.convert({json.dumps(latex_text)}))'],
    timeout=15, text=True
)
```

Only for display equations (not inline — MathML is heavy for short fragments).

## Known limitations

| Issue | Impact | Workaround |
|-------|--------|------------|
| `\\|` surviving | Shows `\\|` in text | Ensure `|` is in `normalize_backslashes` special-chars set |
| Bare `^` without backslash | Superscript `^{-1}` not rendered, shows literal | Add both `(?:\\w|\\))\\^\\{...\\}` (bare caret) and `(?:\\w|\\))\\\\^\\{...\\}` patterns |
| Nested braces in general | `_{y \\in \\mathcal{F}}` pattern | Requires `\\mathcal` conversion BEFORE subscript regex |
| Double `n` in subscript replacement | `minn_{|S|=k|}` if regex captures `(\\w)` from multi-char word | The single `(\\w)` captures only the last char; pattern `mi`+`n<sub>...</sub>` = correct `min<sub>...</sub>` |
| superscript on `)` | `)^{-1}` no match | Use `(?:\\w|\\))\\^\\{...\\}` to catch both `\\w` and `)` |
