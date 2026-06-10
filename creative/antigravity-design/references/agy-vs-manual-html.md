# Agy vs Manual HTML — Priority & Correct Syntax

## Core Rule

**Never write HTML/CSS by hand when agy is available.** Gemini Flash 3.5 (agy's default model) produces superior visual output. This is the user's explicit preference — attempting manual HTML first will be corrected.

The workflow is always: write detailed prompt → pipe to agy via SSH → review → refine prompt → retry.

## Correct Syntax (NOT pipe)

`--print` requires a **string argument**. Piped input (`| agy`) does NOT work.

```bash
# ✅ CORRECT — file content via command substitution
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --print "$(cat /tmp/prompt.txt)"'

# ✅ CORRECT — inline string for short prompts
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  agy --print-timeout 120s --print "Create a single HTML file..."
'
```

## SCP via SSH Alias (not raw IP)

Use the SSH alias to avoid auth issues:

```bash
# ✅ CORRECT — uses SSH alias from ~/.ssh/config
scp -F ~/.ssh/config /tmp/prompt.md oracle-host:/tmp/prompt.txt

# ❌ WRONG — raw IP may fail auth
scp /tmp/prompt.md ubuntu@172.19.0.1:/tmp/
```

## Complete Multi-Section Report Workflow

```bash
# 1. Write a detailed prompt with ALL data inline
cat > /tmp/prompt.md << 'PROMPT'
[full context: exact hex codes, fonts, section order, design rules]
PROMPT

# 2. SCP to host (use alias, not raw IP)
scp -F ~/.ssh/config /tmp/prompt.md oracle-host:/tmp/prompt.txt

# 3. Execute agy with file content
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --print "$(cat /tmp/prompt.txt)"'

# 4. Find generated file on host
ssh oracle-host 'ls -lt /home/ubuntu/*.html | head -3'

# 5. Copy to Hermes bind mount
ssh oracle-host 'sudo cp /home/ubuntu/<file>.html \
  /home/ubuntu/selfhost/hermes/data/'
```

## Image Generation Workflow

```bash
# 1. Generate image
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && \
  timeout 300 agy --dangerously-skip-permissions --print \
  "Generate a logo image for [brand]..."'

# 2. Find the generated image
ssh oracle-host 'ls -lt ~/.gemini/antigravity-cli/brain/*/*.png 2>/dev/null | head -3'

# 3. Copy to Hermes bind mount or pipe via base64
ssh oracle-host 'sudo cp ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png \
  /home/ubuntu/selfhost/hermes/data/'

# Fallback: pipe via base64 when bind mount has permission issues
ssh oracle-host 'sudo cat ~/.gemini/antigravity-cli/brain/<uuid>/<file>.png | base64' \
  2>/dev/null | base64 -d > /opt/data/<filename>.png
```
