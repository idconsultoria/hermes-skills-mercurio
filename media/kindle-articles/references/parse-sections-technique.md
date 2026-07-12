# Section Parsing for Kindle Article EPUBs

## The challenge

Long-form articles (360K chars, 1766 lines) need to be split into chapters and sections for EPUB navigation. Markdown from web extraction uses a specific pattern:

```
[Chapter Title](https://.../#section-anchor)
### [Sub-section Title](https://.../#sub-anchor)
```

Lines are prefixed with `N|` from the `read_file` cache format.

## State machine approach

Use a three-state parser:

```python
chapters = []
current_chap = None
current_sec = None
intro_buf = []
sec_buf = []
in_intro = True  # collecting text before first subsection

CHAPTER_RE = re.compile(r'^\[([^\]]+)\]\(https?://[^\)]+\)\s*$')
SECTION_RE = re.compile(r'^#+\s*\[([^\]]+)\]\(https?://[^\)]+\)\s*$')
SKIP_LINKS = {'Transformer Circuits Thread', 'Anthropic', 'Authors', 'Affiliations', 'Published'}

### Anchor extraction from URL fragments

Each `[Title](url)` link contains the original page anchor (`#intro`,
`#methods`, `#fig-workspace`). Extract it for use as `id` on heading
elements — this enables internal cross-reference navigation in the EPUB:

```python
anchor_m = re.search(r'#([a-zA-Z][a-zA-Z0-9_-]+)\)\s*$', s)
if anchor_m:
    anchor = anchor_m.group(1)  # e.g., 'intro', 'fig-workspace'
```

Store the anchor alongside the title. For sections, use a dict when an
anchor exists (backwards-compatible with string-only for plain titles):

```python
# In the chapter-heading handler:
current_chap = {'num': len(chapters)+1, 'title': m.group(1),
                'anchor': anchor, 'intro_text': '', 'sections': []}

# In the section-heading handler:
if sec_anchor_m:
    current_sec = {'title': m.group(1), 'anchor': sec_anchor_m.group(1)}
else:
    current_sec = m.group(1)  # string fallback for sections without URL
```

**In `flush()`**, the section storage must handle both formats:

```python
if isinstance(current_sec, dict):
    sec_entry = {'title': current_sec['title'], 'text': t}
    if 'anchor' in current_sec:
        sec_entry['anchor'] = current_sec['anchor']
    current_chap['sections'].append(sec_entry)
else:
    current_chap['sections'].append({'title': current_sec, 'text': t})
```

See `references/web-article-media.md` §Internal cross-reference linking
for how these anchors become `id` attributes in the EPUB HTML.
```

### Logic

1. **Chapter heading** (`CHAPTER_RE` matches, not in SKIP_LINKS):
   - `flush_current()` — save intro_buf → current_chap['intro_text'], sec_buf → current_chap['sections']
   - `chapters.append(current_chap)` — **CRITICAL** must append explicitly
   - Start new `current_chap`, reset intro_buf/sec_buf, set in_intro=True

2. **Section heading** (`SECTION_RE` matches):
   - `flush_current()` — move intro_buf to chapter['intro_text'], OR sec_buf to chapter['sections'][-1]
   - Set in_intro=False, start tracking new section with sec_buf

3. **Content line**:
   - If `current_chap is None`, skip (metadata before first chapter)
   - If `in_intro`, append to intro_buf
   - Else append to sec_buf

4. **After loop**:
   - `flush_current()` + `chapters.append(current_chap)` for the last chapter
   - Filter: `chapters = [c for c in chapters if c['intro_text'] or c['sections']]`

### Cleanup

Before parsing, remove from raw markdown:
```python
clean = re.sub(r'^\d+\|', '', raw, flags=re.MULTILINE)      # line-number prefixes
clean = re.sub(r'^!\[.*\]\(.*\)\s*$', '', clean, flags=re.MULTILINE)  # image markdown
clean = re.sub(r'\[\?\?\]\(https?://[^\)]+\)', '', clean)    # dead-reference links
clean = re.sub(r'^\-{3,}\s*$', '', clean, flags=re.MULTILINE) # horizontal rules
clean = re.sub(r'^\* \* \*\s*$', '', clean, flags=re.MULTILINE) # separators
clean = re.sub(r'\n{4,}', '\n\n\n', clean)                  # collapse blank lines
```

### Real example

Transformer Circuits article "Workspace" (360K chars, 1766 lines):

| Chapter | Sections | Content |
|---------|----------|---------|
| Introduction | 5 | Motivation, global workspace in LMs, Jacobian lens, J-space contents, takeaways |
| Methods | 5 | Jacobian lens, interpreting, J-space, comparisons, technical details |
| The J-space acts as a Global Workspace | 8 | Verbal report, modulation, reasoning, generalization, selectivity + ablation studies |
| The J-space's structure supports its function | 6 | Layer organization, capacity, broadcast across depth + tokens |
| Using the J-lens for alignment auditing | 5 | Blackmail, prompt injection, Opus examples, reward-hacking, hidden objectives |
| Post-training | 2 | Assistant's POV, self-monitoring |
| Counterfactual Reflection Training | 0 | Continuous text, no subsections |
| Related work | 0 | Continuous text, no subsections |
| Discussion | 4 | Limitations, alignment, human cognition, consciousness |
| Appendix | 31 | Methods detail, formalization, additional experiments, ablation details |

66 sub-sections total across 10 chapters.

## Debugging

If the EPUB comes out with 0 chapters or fewer than expected:

1. **Check CHAPTER_RE matching**: Print all lines matching your heading regex to confirm they're caught
2. **Check SKIP_LINKS**: Are real chapters being filtered out? Check the set
3. **Check append logic**: Are you calling `chapters.append()` inside `start_new_chapter()`?
4. **Check flush**: Does `flush_current()` save intro_buf before `start_new_chapter()` overwrites it?
5. **Check content routing**: If a chapter has intro_text=0 and sections=0, the content isn't being routed to any buffer
