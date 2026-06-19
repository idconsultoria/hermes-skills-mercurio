# Self-Contained Skill Consolidation

When installing an external community skill that has dependencies (other skills it expects to be loaded), consolidate everything into a single self-contained skill. Zero external skill dependencies — reference files in `references/` instead.

## When to use

- User downloads a skill that references `/other-skill`, `/another-skill`, etc.
- User explicitly says "make it work standalone" or "compile everything into one skill"
- Skill has `See SKILL.md of dependency` or `Run the /dependency skill` instructions

## Process

### 1. Fetch the main skill

```bash
curl -sL 'https://raw.githubusercontent.com/<user>/<repo>/main/path/to/SKILL.md' -o /tmp/skill-main.md
```

Read it and identify all dependency references:
- `/skill-name` references in prose
- References to external `.md` files (e.g., `See HTML-REPORT.md`)
- Skills listed as prerequisites or in trigger conditions

### 2. Fetch all dependencies

For each dependency, check if it lives in the same repo. Most community skill repos follow `skills/<category>/<name>/SKILL.md`:

```bash
# Check repo structure
curl -sL 'https://api.github.com/repos/<user>/<repo>/contents/skills/<category>' | python3 -c "..."

# Fetch each dependency SKILL.md
curl -sL 'https://raw.githubusercontent.com/.../SKILL.md' -o /tmp/skill-dep.md
```

Also fetch referenced files (HTML-REPORT.md, DEEPENING.md, FORMAT.md, etc.).

### 3. Merge into single SKILL.md

Consolidation rules:
- **Vocabulary/glossary**: inline directly (these are the foundation)
- **Process steps**: merge into the main process flow
- **Sub-workflows**: inline with clear section headers
- **Format templates**: save as `references/<name>.md`
- **Design patterns**: save as `references/<name>.md` if >30 lines; inline if shorter
- **Keep the dependency's own reference files**: they're part of the pattern

Structure the consolidated SKILL.md:
```
---
name: <skill-name>
description: "...Zero external skill dependencies."
---
# Title

## Architecture Vocabulary (from dependency-skill-1)
[merged glossary]

## Deepening Guide (from dependency-skill-2)
[merged strategy]

## Domain Modeling (from dependency-skill-3)
[merged workflow]

## Process
### 1. Phase One
### 2. Phase Two
...

## Reference Files
| File | Content |
|------|---------|
| `references/X.md` | ... |
```

### 4. Save reference files

```bash
mkdir -p /opt/data/skills/<category>/<skill-name>/references/
cp /tmp/DEP.md /tmp/DESIGN.md /tmp/HTML-REPORT.md /opt/data/skills/<category>/<skill-name>/references/
```

### 5. Verify

- Read the SKILL.md to ensure it reads as a coherent document
- Check no `/external-skill` references remain in prose
- Verify all reference files are listed in the Reference Files section
- Load with `skill_view(name='<skill-name>')` to confirm it parses

## Example: improve-codebase-architecture

Consolidated from:
- `codebase-design` (vocabulary, deepening)
- `domain-modeling` (CONTEXT.md, ADR format)
- `grill-with-docs` (grilling loop)
- `HTML-REPORT.md` (report scaffold)
- `DEEPENING.md` (dependency categories)
- `DESIGN-IT-TWICE.md` (sub-agent pattern)
- `CONTEXT-FORMAT.md` (glossary format)
- `ADR-FORMAT.md` (ADR template)

Result: 1 SKILL.md (16.5 KB) + 5 reference files. Zero external skill dependencies.

## Pitfalls

- **Don't just concatenate**: merge content at the right level — vocabulary inline, patterns as references
- **Keep the dependency's reference files**: if DEEPENING.md was referenced by the original skill, it's part of the pattern — save it, don't inline it (keeps SKILL.md manageable)
- **Remove all `/skill-name` references**: search for `/codebase-design`, `/grilling`, etc. and remove or replace with "see section below"
- **Update the description**: add "Zero external skill dependencies." to signal self-containment
