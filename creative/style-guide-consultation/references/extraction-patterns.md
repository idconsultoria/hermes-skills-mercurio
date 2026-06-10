# Style Guide Extraction & Application Patterns

## From HTML style guides (ID Consultoria, IAF)

HTML style guides store design tokens in CSS custom properties in the `<style>` block.
Read with:

```python
from hermes_tools import read_file
content = read_file('/opt/data/referencias/id-consultoria/id-style-guide.html', limit=100)
# Search for ":root {" in content — that's where the design tokens live
```

### Extraction pattern

After reading the first 100 lines of the HTML, the `:root { ... }` block contains
all design tokens. Copy-paste them into your prompt/command directly.

For dark-mode brands (ID, IAF), if the user asks for **light mode**, adapt:

| Token | Dark | Light |
|-------|------|-------|
| bg-page | #050A0F | #F7F9FB |
| bg-card | #1C1C1E | #FFFFFF |
| text-primary | #E2E9EE | #1C1C1E |
| text-body | (same) | #3D4A53 |
| accent colors | keep same | keep same |
| borders | rgba(255,255,255,0.06) | #DCE4E8 |

### When using agy for HTML generation

Two approaches, ordered by preference:

**Fast path (no SCP needed):** Include ONLY the design tokens (6-8 colors, 3 fonts)
in the agy prompt inline. Tell agy the content is in a file on the host.

**Thorough path:** Copy the reference style guide HTML to the host side-by-side
with the content file, tell agy to read both.

## From Markdown style guides (Hermes Agent)

Design tokens are in tables in the body. Read with `read_file()` limited to ~80 lines.
The token table format is:

```
| Token | Hex | Uso |
|-------|-----|-----|
| --blue-primary | #0000FF | Background principal |
```

## Light mode adaptation rules

For ID Consultoria specifically, when user asks for light mode:

- Flip backgrounds: #050A0F → #F7F9FB, #1C1C1E → #FFFFFF
- Keep deep-teal #003B46 as main accent (works on both)
- Use electric-teal #4AC6D3 instead of #66E8F1 for borders (less glow)
- Text goes from white → near-black (#3D4A53 body, #1C1C1E titles)
- Remove all glassmorphism/blur/neon — use clean borders (#DCE4E8) instead
- Cards get subtle shadow instead of glow
