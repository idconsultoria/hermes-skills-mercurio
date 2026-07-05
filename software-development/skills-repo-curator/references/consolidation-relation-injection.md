# Consolidation — Relation Injection After Depth-1

After 3 parallel subagents return depth-1 inference results (typically 80-120
proposed relations), the index.md must be updated. This reference covers the
full process from consolidation to injection.

## 1. Consolidate Reports

Each subagent returns a markdown report with `RELATION: source → type → target // reason`
lines. Parse and deduplicate:

```python
import re
from collections import Counter

# Collect all proposed relations from 3 reports
proposals = []

# Parse: RELATION: autonomous-ai-agents/hermes-agent → similar → creative/brand-studio-forge // Both define agent personality
pattern = r'^RELATION:\s*(\S+)\s*→\s*(\w+)\s*→\s*(\S+)\s*//'
for report_text in [batch1, batch2, batch3]:
    for m in re.finditer(pattern, report_text, re.MULTILINE):
        proposals.append((m.group(1), m.group(2).strip(), m.group(3)))

# 2. Deduplicate symmetric pairs
# similar is bidirectional — A→similar→B and B→similar→A are the same edge
seen = set()
deduped = []
for src, rtype, tgt in proposals:
    if rtype == 'similar':
        key = tuple(sorted([src, tgt]))
        if key not in seen:
            seen.add(key)
            deduped.append((src, rtype, tgt))
    else:
        # For directed relations, check if reverse already exists
        rev = {'uses': 'used_by', 'used_by': 'uses', 'parent': 'child'}
        rev_key = (tgt, rev.get(rtype, rtype), src)
        if rev_key not in seen and (src, rtype, tgt) not in seen:
            seen.add((src, rtype, tgt))
            deduped.append((src, rtype, tgt))
```

## 2. Read Existing Relations

Use the correct regex with `re.MULTILINE`:

```python
import re
with open('/opt/data/skills/index.md') as f:
    idx = f.read()

# CRITICAL: re.MULTILINE is REQUIRED. Without it, findall returns 0 matches
# because the arrow → (U+2192) and newlines don't match without the flag.
existing = set()
for m in re.finditer(r'^- `(\w+)` → `(.+)`', idx, re.MULTILINE):
    existing.add((m.group(1), m.group(2)))
```

## 3. Inject Into index.md

Walk lines sequentially, track current skill name, find each `**Relações:**`
block, and append new relations after the last existing one:

```python
result = []
i = 0
current_skill = None
added = 0

while i < len(lines):
    line = lines[i]
    result.append(line)
    
    # Track current skill
    m = re.search(r'- \*\*Nome:\*\* `([^`]+)`', line)
    if m:
        current_skill = m.group(1)
    
    # When hitting a Relações line, copy existing relations then inject new
    if current_skill and line.strip() == '**Relações:**':
        j = i + 1
        existing_set = set()
        while j < len(lines):
            rm = re.match(r'^- `(\w+)` → `(.+)`', lines[j].strip())
            if rm:
                existing_set.add((rm.group(1).strip(), rm.group(2).strip()))
                result.append(lines[j])
                j += 1
            else:
                break
        
        # Add new relations not already present
        if current_skill in new_rels:
            for rtype, target in new_rels[current_skill]:
                if (rtype, target) not in existing_set:
                    result.append(f'- `{rtype}` → `{target}`')
                    existing_set.add((rtype, target))
                    added += 1
        
        i = j  # Skip past processed relation lines
        continue
    
    i += 1
```

Save with `write_file` (LLM tool, not script — respects index.md rule).

## 4. Verify

```bash
grep -c '^- `' index.md                    # count relation lines
grep -c '^### ' index.md                   # count skills
python3 scripts/generate_graph.py          # should show no orphans
```

## Pitfalls

- **`re.MULTILINE` é obrigatório.** Sem ele o parser retorna 0 relações silenciosamente.
- **Skip offset bug:** ao usar `j = len(result_lines)` para escanear relações existentes, o índice `j` aponta para a POSIÇÃO ATUAL no loop principal, não para a PRÓXIMA linha. Use `j = i + 1` (posição da linha seguinte no vetor original `lines`).
- **Archived skills poluem o grafo.** O `generate_graph.py` precisa pular `.archive/`. Já corrigido no script, mas verificar sempre.
- **write_file pode falhar silenciosamente** se chamado via execute_code com file caching. Prefira modificar arquivos via terminal com Python heredoc quando precisar de escrita direta e verificável.
