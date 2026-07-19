# Evolve Report — 2026-07-19

## Summary
- **Skills:** 77 → 82 (5 new, 0 merges, 0 deletes)
- **Orphans:** 0 (all skills have ≥1 relation)
- **New sections:** Copywriting, Messaging
- **Graph relations:** ~200 edges

## Changes

### New skills added:
| Skill | Type | Relations |
|-------|------|-----------|
| hermes-diagnostics | Research | `similar` → hermes-agent |
| gcp-cloud-build | ToolIntegration | `similar` → deployment-pipeline, vercel-deploy, github-pr-workflow |
| whatsapp-baileys-integration | ToolIntegration | `similar` → messaging-platforms, whatsapp-automation |
| oferta-hormozi | Creative | `similar` → creative/copywriting |
| whatsapp-automation | ToolIntegration | `similar` → whatsapp-baileys-integration |

### Frontmatter fixes:
- `oferta-hormozi`: type Copywriting→Creative, +timestamp
- `whatsapp-baileys-integration`: +timestamp
- `whatsapp-automation`: +type (ToolIntegration), +timestamp

### Description fixes:
- `oferta-hormozi`: added blank-line separator + trigger paragraph (pt-BR)
- `whatsapp-baileys-integration`: added blank-line separator + trigger paragraph
- `whatsapp-automation`: added blank-line separator + trigger paragraph

### Index updates:
- 5 new entries in 2 new sections
- 2 descriptions synced (pi-session-audit, html-to-pdf-chromium)
- 4 sizes synced
- curator_backups removed from tracking
