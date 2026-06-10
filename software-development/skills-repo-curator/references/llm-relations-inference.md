# LLM Relations Inference Pattern

## Problem
Regex-based relation inference from SKILL.md content produces low-quality edges — mentions skills that aren't semantically related, misses actual dependencies, and can't distinguish between `uses`, `similar`, `used_by`, and `parent` types.

## Solution
Use 3 parallel `delegate_task` subagents, each reading ~31 SKILL.md files and determining relations by understanding content (not pattern matching).

## Execution

### 1. Split skills into 3 batches
```bash
cd /opt/data/skills
find . -name 'SKILL.md' -type f | sed 's|./||; s|/SKILL.md||' | sort | split -l 31 - batch_
```

### 2. Dispatch 3 subagents
Each subagent gets:
- A list of ~31 skill file paths to read
- Relation type definitions: `parent`, `child`, `similar`, `uses`, `used_by`
- Instructions to read each SKILL.md fully and determine relations
- Output format: `{"skill_name": [["relation_type", "other_skill_name"], ...]}`

### 3. Merge results
Combine the 3 JSON outputs, deduplicate bidirectional edges (parent↔child, uses↔used_by), and write the final edge list.

## Relation Types

| Type | Meaning | Edge rendering |
|------|---------|---------------|
| `similar` | Overlapping territory | Dashed line |
| `uses` | Depends on / invokes another | Solid arrow from user to used |
| `used_by` | Inverse of uses | Same as uses (deduplicated) |
| `parent` | Umbrella / parent skill | Solid arrow from parent to child |
| `child` | Specialization | Same as parent (deduplicated) |

## Results
Typical run: ~207 relations across 76/93 skills with high semantic precision. Compare: ~138 regex-based relations with lower accuracy.

## Cost
~3M input tokens across 3 subagents, ~21K output tokens. One-time per evolve cycle.