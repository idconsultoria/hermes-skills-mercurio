# Brand Kit Generation with agy + Open Design

## Pattern: Generating Premium Brand Assets

Combine agy (Gemini Flash 3.5 image gen) with Open Design's brandkit skill methodology.

### Pipeline

1. **Extract skill context** from Open Design API:
   ```bash
   curl -s http://127.0.0.1:7456/api/skills/brandkit | python3 -c "import json,sys; print(json.load(sys.stdin).get('body',''))"
   ```
   This gives premium brand-board methodology: 3x3 grid, panel logic, visual modes, anti-generic rules.

2. **Write a brand-kit prompt** embedding:
   - Exact brand colors (hex)
   - Logo description
   - Brand strategy (category, audience, personality, metaphor)
   - Layout spec (3x3, 2x3, etc.)
   - Visual mode (Dark Developer, Light Editorial, etc.)
   - Panel descriptions for each cell
   - Anti-clutter rules from brandkit skill

3. **Generate via agy**:
   ```bash
   scp -F ~/.ssh/config prompt.txt oracle-host:/tmp/
   ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && timeout 300 agy --dangerously-skip-permissions --print "$(cat /tmp/prompt.txt)"'
   ```

4. **Retrieve image**:
   ```bash
   ssh oracle-host 'find ~/.gemini/antigravity-cli/brain/ -name "*.png" -mmin -5 | head -1'
   ssh oracle-host 'sudo cp <path> /tmp/'
   # Then pipe to container: ssh ... 'sudo cat /tmp/file.png | base64' | base64 -d > /opt/data/file.png
   ```

#### WhatsApp/Profile Icon Generation

When generating a circular WhatsApp group icon or profile picture:

1. **Use the existing logo as reference** — describe it in extreme detail instead of embedding base64 (which can be 300-400KB). Include exact hex colors, shape description, mechanical details, eye color/glow.

2. **Key differences from full logo version:**
   - Circular format (WhatsApp crops to circle)
   - Higher contrast for small sizes (48x48 must remain legible)
   - Simplified details — what works at 512px may not read at 48px
   - The focal point (LED eye, unique silhouette) must pop
   - Strong silhouette is more important than fine details
   - No text in the icon itself

3. **Prompt structure for WhatsApp icon:**
   - State it's a VERSION of an EXISTING logo (agy respects this)
   - Exact specification of the current logo's appearance
   - Explicit differences from the original (circular, higher contrast, simplified)
   - "NO text in the icon"

4. **Image retrieval** (same as brand kit):

```bash
ssh oracle-host 'find ~/.gemini/antigravity-cli/brain/ -name "*.png" -mmin -5 2>/dev/null | head -1'
ssh oracle-host 'sudo cp <path> /home/ubuntu/selfhost/hermes/data/iaf-whatsapp-icon.png'
```

## Open Design API (runs at localhost:7456)

| Endpoint | Method | Returns |
|----------|--------|---------|
| `/api/health` | GET | `{"ok":true,"version":"0.10.0"}` |
| `/api/skills` | GET | 155 skills with name, description, body, triggers |
| `/api/design-systems` | GET | DESIGN.md based systems with swatches |
| `/api/projects` | GET/POST | Create and list projects |

Skill content is available directly in the JSON response under `body` field for each skill.

### Image extraction from agy HTML output

When agy embeds images as base64 in HTML, extract with:
```python
import re, base64
with open("file.html") as f: html = f.read()
pattern = r'data:image/(?:png|jpeg);base64,([A-Za-z0-9+/=]{50000,})'
match = re.search(pattern, html)
if match:
    with open("image.png", "wb") as f:
        f.write(base64.b64decode(match.group(1)))
```
