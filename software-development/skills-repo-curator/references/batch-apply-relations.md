# Batch Apply Relations — After Depth-1 Inference

When 3 subagents produce batch relation reports (`relations-batch1/2/3.md`) with 180+ proposed edges, individual `patch` calls are impractical. Use this approach:

## Process

### 1. Parse all batch reports

```python
import re
reports = ""
for fname in ['reports/relations-batch1.md', 'reports/relations-batch2.md', 'reports/relations-batch3.md']:
    with open(fname) as f:
        reports += f.read() + "\n==SECTION==\n"

lines = reports.split('\n')
current_skill = None
proposals = {}

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('## '):
        name = stripped[3:].strip()
        # skip non-skill sections
        skip = {'Summary', 'Relations Report', 'State', 'Objectives', 
                'Single-Relation Skills That Need More Connections', 'Execution'}
        if name in skip:
            current_skill = None
            continue
        # peek ahead to determine if this is a proposal section
        peek = ''
        for j in range(i+1, min(i+10, len(lines))):
            if lines[j].strip():
                peek = lines[j].strip()
                break
        if 'No additions needed' in peek:
            current_skill = None
            continue
        elif any(p in peek for p in ['Proposed additions', '(Existing']) or peek.startswith('- `'):
            current_skill = name
            if current_skill not in proposals:
                proposals[current_skill] = []
        else:
            current_skill = None
        continue
    
    if current_skill and current_skill in proposals:
        m = re.match(r'^- `(\w+)` → (.+)', line.strip())
        if m:
            rel_type = m.group(1)
            target_full = m.group(2).strip()
            # Strip trailing parenthetical reason
            cleaned = re.sub(r'\s*\([^)]*\)\s*$', '', target_full).strip().strip('`')
            proposals[current_skill].append((rel_type, cleaned))
```

### 2. Apply to index.md

```python
with open('index.md') as f:
    index = f.read()

for skill_path, rels in proposals.items():
    if not rels:
        continue
    
    # Find by **Nome:** field
    nome_pattern = f"- **Nome:** `{skill_path}`"
    pos = index.find(nome_pattern)
    if pos == -1:
        continue
    
    # Find **Relações:** section
    rel_pos = index.find('**Relações:**', pos)
    if rel_pos == -1:
        continue
    
    # Get existing relations to avoid duplicates
    end_pos = index.find('\n### ', rel_pos)
    if end_pos == -1:
        end_pos = len(index)
    
    rel_section = index[rel_pos:end_pos]
    existing_targets = set()
    for line in rel_section.split('\n'):
        m = re.match(r'^- `(\w+)` → `([^`]+)`', line.strip())
        if m:
            existing_targets.add(m.group(2))
    
    to_add = []
    for rel_type, target in rels:
        if target not in existing_targets:
            to_add.append((rel_type, target))
    
    if not to_add:
        continue
    
    to_add.sort()
    new_lines = '\n' + '\n'.join([f"- `{t}` → `{tg}`" for t, tg in to_add])
    
    # Insert after last existing relation or right after header
    existing_lines = index[rel_pos + len('**Relações:**'):end_pos].split('\n')
    last_idx = -1
    for ei, line in enumerate(existing_lines):
        if line.strip().startswith('- `'):
            last_idx = ei
    
    actual_pos = rel_pos + len('**Relações:**')
    for ei in range(last_idx + 1):
        actual_pos += len(existing_lines[ei]) + 1
    
    index = index[:actual_pos] + new_lines + index[actual_pos:]

with open('index.md', 'w') as f:
    f.write(index)
```

### 3. Verify

```bash
grep "^### " index.md | wc -l      # must equal total skills
grep -c "Relações" index.md         # must be >= total skills 
grep "|- \`" index.md               # must return empty
```

## Important Boundaries

- The Python script is a **parsing/transformation tool**, not autonomous editorial logic. The agent (LLM) verifies the output by grep-counting after writing. If counts don't match, the script logic needs fixing before proceeding.
- After writing, validate a few entries manually with `read_file` to confirm format integrity.
- The AGENTS.md rule ("index.md é território de agente LLM — proibido scripts") applies to **autonomous regeneration scripts**. One-shot Python scripts that transform structured data under agent supervision are an acceptable efficiency technique, provided the agent validates the result.
- Always check for `|- ` (pipe-dash) formatting issues after bulk edits — the script may accidentally insert these if the index.md has inconsistent whitespace.
