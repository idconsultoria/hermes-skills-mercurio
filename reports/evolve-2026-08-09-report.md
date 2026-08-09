# Evolve Report — 2026-08-09

## Estado inicial vs final

| Métrica | Inicial | Final |
|---------|---------|-------|
| Skills | 102 | 101 |
| Orphans | 0 | 0 |
| Bad relation targets | 0 | 0 |
| Descrições conforme | 102/102 | 101/101 |
| Size mismatches | 0 | 0 |

## Merges

| Deletada | Absorvida por | Motivo |
|----------|---------------|--------|
| `messaging/whatsapp-automation` (5.7KB) | `infrastructure/whatsapp-baileys-integration` (22.5KB) | Mesmo domínio (automação WhatsApp via Baileys), mesmo workflow (Node bridge → QR auth → session → send), `whatsapp-baileys-integration` era superset estrito: cobria tudo do automation + 40 seções extras (pairing code 428, Cloud Run jobs, Drive/Sheets, ADC fallback, Gemini 429). |

**Conteúdo preservado no merge:**
- References copiados: `baileys-bridge-server.js`, `whatsapp_client.py`, `multi_assessor_config.py`
- Seções adicionadas ao SKILL.md destino: Migration Checklist (Z-API→Baileys), WhatsApp Web Limitations, Rate Limiting, Z-API Compatibility Details, tabela References
- Diretório `messaging/` removido (ficou vazio)

## Relações alteradas
- `infrastructure/whatsapp-baileys-integration`: removida relação `similar → messaging/whatsapp-automation` (target deletado); mantida `similar → autonomous-ai-agents/messaging-platforms`

## Órfãos
- 0 órfãos — todas as 101 skills têm relações válidas (verificado por parser)

## Skills mantidas separadas (avaliadas p/ merge)
- `infrastructure/selfhost-service-deploy` × `infrastructure/selfhost-web-apps`: toolchain idêntica (docker compose + NPM + SSL) mas workflows distintos — service-deploy é o padrão genérico para QUALQUER serviço novo; web-apps cobre apps PHP/Python/Node com nginx frontend, hardening e SSL redirect loop. Já conectadas via `similar` bilateral.
- `health/ares-fitness-coach` × `health-fitness/body-recomposition`: persona coach vs tracking de métricas — workflows distintos.

## Git diff summary
- `git diff HEAD --stat` (pós-update): merges + index.md + SKILL.md edits
- 1 skill deletada, 1 skill expandida, index.md 102→101

## Limpeza de scripts temporários
- `_evolve_analysis.py`, `_verify_index.py` removidos antes do commit final
