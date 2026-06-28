# Open Knowledge Format (OKF) v0.1 — Reference

> Google Cloud, June 2026. Sam McVeety & Amir Hormati.
> Spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

## Core Philosophy

OKF formalizes the **LLM-wiki pattern** (Andrej Karpathy) into a portable markdown
format. A bundle is a directory tree of `.md` files with YAML frontmatter.
No SDK, no registry, no central authority.

> *"If you can `cat` a file, you can read OKF; if you can `git clone` a repo, you can ship it."*

**Three principles:**
1. **Minimally opinionated** — only `type` is required
2. **Producer/consumer independence** — hand-written or pipeline-generated, same contract
3. **Format, not platform** — not tied to any cloud, DB, provider, or framework

## Bundle Structure

```
bundle/
├── index.md           # Optional — directory listing (progressive disclosure)
├── log.md             # Optional — change history, newest first
├── <concept>.md       # Concept at root
└── <subdirectory>/
    ├── index.md       # Listing for this subdirectory
    ├── <concept>.md
    └── ...
```

**Reserved filenames:** `index.md` (directory listing), `log.md` (change history).
All other `.md` files are concept documents.

## Concept Document

```yaml
---
type: BigQuery Table          # REQUIRED — freeform string, no central registry
title: Customer Orders         # Recommended
description: One row per order # Recommended (finishes "is a…" thought)
resource: https://...          # URI to underlying asset (optional)
tags: [sales, orders]          # Optional
timestamp: 2026-05-28T14:30:00Z # ISO 8601 datetime
# Any producer-defined keys allowed (forward-compatible)
---
```

**Rules:**
- `type` is the **only required field**. Consumers route/filter by it.
- Consumers **must tolerate** unknown types, missing optional fields, unknown keys.
- Broken internal links are tolerated — may represent not-yet-written knowledge.
- Body is free markdown.
- Conventional headings: `# Schema`, `# Examples`, `# Citations`.

## Agent-Readable Stack

| Layer | Purpose |
|---|---|
| `robots.txt` / `sitemap.xml` | Tells crawler which URLs exist |
| `llms.txt` | Points agent to pages worth reading |
| `AGENTS.md` / `CLAUDE.md` | Instructions for agent behaviour inside one repo |
| **OKF** | Hands the agent the **knowledge itself** as a portable graph |

## Two Agent Roles

1. **Enrichment agents** — write *into* a bundle (draft concepts from DBs, codebases)
2. **Consumption agents** — read and traverse (progressive disclosure from root `index.md`)

Contract is just files. Neither knows about the other.

## Hermes Skills Repo — OKF Mapping

| OKF Concept | Hermes Equivalent |
|---|---|
| Bundle | `/opt/data/skills/` (root) |
| Concept | SKILL.md |
| Concept ID | `category/skill-name` |
| `type` (required) | `type:` in frontmatter (8-value taxonomy) |
| `timestamp` (recommended) | `timestamp:` in frontmatter (ISO 8601 from git log) |
| `index.md` (per directory) | Root `index.md` + per-category `index.md` |
| `log.md` | Root `log.md` |
| Producer/consumer | Hermes enriches via evolve cycle, consumes via skill_view() |

## 8-Type Taxonomy

| Type | Count | What it covers |
|---|---|---|
| `Orchestrator` | 11 | Multi-step pipelines orchestrating agents/tools |
| `ToolIntegration` | 11 | Wrapper for specific CLI/API external tool |
| `Reference` | 14 | Knowledge, consultation, troubleshooting guide |
| `Template` | 4 | Produces structured output (HTML, PDF, diagram) |
| `Research` | 9 | Gathers and synthesizes information |
| `Media` | 5 | Produces audio/video/image/manga |
| `Creative` | 4 | Brand, copy, humanization, visual assets |
| `Health` | 2 | Fitness coaching, body metrics |

## Progressive Disclosure Pattern

Each category has its own `index.md` listing only that category's skills
with type, timestamp, and size. OKF-compliant consumption agents start
at root `index.md`, read the categories they need, and follow links into
per-category indexes (OKF §6).

## Skills Repo vs OKF — Key Differences

| Aspect | Skills Repo (Hermes) | OKF v0.1 |
|---|---|---|
| index.md | Single root catalog listing ALL skills | Per-directory progressive disclosure |
| Relations | Typed (similar/uses/parent/used_by) | Untyped markdown links |
| Maintenance | Full consolidation cycle (update→evolve→offload) | Format only, no maintenance |
| Hierarchy | 2-level (category/skill) | Arbitrary nesting |
| Extensibility | Fixed structure, references/ dir | Any field, any heading, any subdir |
| Audience | Hermes agent (internal, private) | Any agent across organizations |
