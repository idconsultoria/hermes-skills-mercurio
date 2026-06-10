# index.md Entry Specification

Every skill in index.md follows this exact format.

## Template

```markdown
### [Title of the Skill](skills/path/to/SKILL.md)

- **Nome:** `path/to/skill`
- **Arquivo:** `path/to/skill/SKILL.md`
- **Tamanho:** N,NNN chars
- **Resumo:** One-line summary (~80 chars max, extracted from first sentence of description)

Full descriptive paragraph from SKILL.md frontmatter description field.
This may be 1-3 sentences explaining what the skill does, when to use it,
and what territory it covers.

**Relações:**
- `uses` → `other-skill-name`
- `similar` → `another-skill`
- `used_by` → `parent-skill`
```

## Fields

| Field | Source | Format |
|-------|--------|--------|
| Title | SKILL.md H1 or frontmatter title | Plain text |
| Nome | Relative path without SKILL.md | backtick-wrapped |
| Arquivo | Relative path with SKILL.md | backtick-wrapped |
| Tamanho | `wc -c` of SKILL.md | comma-separated + "chars" |
| Resumo | First sentence of description | 80-90 chars max, with "..." if truncated |
| Description | Full frontmatter `description:` field | Paragraph form, no length limit (but keep <300 chars for readability) |
| Relações | LLM-inferred from skill content | List of `type → name` pairs, sorted by type |

## Relation Types

| Type | Meaning | Index representation |
|------|---------|---------------------|
| `uses` | This skill depends on / invokes another | `- \`uses\` → \`target\`` |
| `used_by` | Another skill depends on this one | `- \`used_by\` → \`target\`` |
| `similar` | Both cover overlapping territory | `- \`similar\` → \`target\`` |
| `parent` | This is the umbrella for another | `- \`parent\` → \`child\`` |
| `child` | This is a specialization | `- \`child\` → \`parent\`` |

## Category Headers

```markdown
## Category Name
```
Uses title-case of the directory name (e.g., "content-production" → "Content Production").

## Regeneration
Run after every `update` or `evolve` operation. Scan all SKILL.md files, extract frontmatter, build entries, sort by category then name, write to index.md.
