# Evolve Report — 2026-08-12

## Estado inicial vs final

| Métrica | Inicial | Final |
|---------|---------|-------|
| Skills | 101 (index) / 114 (disco) | 114 |
| Orphans | 13 | 0 |
| Bad relation targets | 0 | 0 |
| Edges (grafo) | 261 | 315 |
| Descrições conforme | 114/114 | 114/114 |

## Contexto do ciclo

Ciclo completo executado manualmente na sessão (fora do cron, a pedido do usuário — o cron de domingo 09/08 deixou 13 skills untracked e não indexadas; a regeneração do grafo no fix do popup as expôs como órfãs).

## UPDATE (commit 1e68d25)

- index 101→114: 13 skills novas indexadas (pi-agent-internals, email-inbox-triage, github-issue-to-pr, document-to-action-items, google-docs-formatting, google-sheets-automation, html-pdf-fidelity, meeting-action-items, product-price-monitor, resume-ats-engine, weekly-review-planning, competitor-news-monitor, telegram-bot-python)
- Nova seção `## Email` no index.md
- 13 frontmatters corrigidos: description 2 linhas (sumário ≤85 + parágrafo com gatilho "Load this skill when"/"Carregue esta skill quando"), `type` OKF, `timestamp`
- audit-descriptions.py: 114/114 compliant
- Sizes sincronizados (0 mismatches); 14 drifts de Resumo revisados (index.md mais completo — aceitável, sem ação)
- 20+ references novas commitadas (product-pipeline 13, hermes-diagnostics 3, resume-ats-engine 6, google-docs-formatting 4, etc.)

## EVOLVE — validação depth-1 (3 subagentes paralelos)

Relações iniciais das 13 novas validadas bilateralmente (subagentes leram skill principal + candidatos). **28 relações propostas → 25 confirmadas, 3 rejeitadas/corrigidas.**

### Rejeições/correções
| Skill | Relação | Ação |
|-------|---------|------|
| `resume-ats-engine` | `uses → html-report-hermes` | ❌ REMOVIDA (falso positivo — html-report-hermes só no frontmatter, nenhuma fase do workflow gera relatório Hermes) |
| `resume-ats-engine` | `similar → agy` | 🔄 RETIPADA para `uses → agy` (fase 6 executa agy explicitamente — dependência de workflow, não similaridade) |
| `pi-agent-internals` | `similar → product-pipeline` | ❌ REMOVIDA (Orchestrator ≠ Reference; 0 ocorrências de conexão no corpo) |
| `telegram-bot-python` | `uses → whatsapp-baileys-integration` | 🔄 RETIPADA para `similar` (não menciona Baileys; arquiteturas distintas; irmãs de padrão) |

### Novas relações aplicadas (+25)
- document-to-action-items: +3 (`uses xlsx/google-workspace/notion`)
- meeting-action-items: +3 (`similar weekly-review-planning`, `uses taskflow-mcp/notion`)
- weekly-review-planning: +2 (`similar document-to-action-items`, `uses taskflow-mcp-rules`)
- email-inbox-triage: +2 (`uses taskflow-mcp`, `similar meeting-action-items`)
- github-issue-to-pr: +2 (`uses test-driven-development/systematic-debugging`)
- google-docs-formatting: +2 (`used_by product-pipeline`, `similar xlsx`)
- google-sheets-automation: +1 (`used_by product-pipeline`)
- html-pdf-fidelity: +3 (`similar html-to-social-image/html-report-hermes`, `used_by research-report-standards`)
- resume-ats-engine: +1 (`uses messaging-platforms`)
- product-price-monitor: +1 (`uses messaging-platforms`)
- pi-agent-internals: +1 (`similar hermes-diagnostics`)
- competitor-news-monitor: +1 (`uses hermes-cron-patterns`)
- telegram-bot-python: +2 (`uses oracle-host-access`, `similar whatsapp-baileys-integration`)

### Merges avaliados (critério MECE) — 0 merges executados
Todos os pares avaliados **mantidos separados** com justificativa:
- document-to-action-items × meeting-action-items (fonte/evidência exclusiva: docs vs conversa)
- email-inbox-triage × document-to-action-items (artefato e política de mutação distintos)
- weekly-review-planning × taskflow-mcp (ritual multi-sistema vs conector MCP — camadas)
- google-docs-formatting × google-sheets-automation × google-workspace (partição por artefato + camada de auth)
- html-pdf-fidelity × html-to-pdf-chromium (fazer funcionar vs fazer idêntico — complementares)
- telegram-bot-python × messaging-platforms (builder vs reference)
- competitor-news-monitor × tech-trend-discovery (watchlist fixa vs descoberta aberta)

### Achados (não bloqueantes)
- `related_skills: [blogwatcher]` em CNM/tech-trend-discovery aponta para skill inexistente no repo (dangling) — ação editorial futura
- Corpos citam skills ausentes: ocr-and-documents, himalaya, requesting-code-review, teams-meeting-pipeline, github-issues — candidatas a entrada futura

## Órfãos
- 0 órfãos — todas as 114 skills têm relações válidas (verificado por parser no grafo)

## Git diff summary
- `1e68d25` update (63 files, +5382/−18)
- `18c29b5` (anterior, fix do popup do grafo)

## Limpeza
- Scripts temporários (`_update_analysis.py`, `_fix_frontmatters.py`, `_sync_sizes.py`) removidos antes do commit
