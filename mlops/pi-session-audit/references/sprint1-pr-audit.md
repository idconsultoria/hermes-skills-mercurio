# Sprint 1 PR Session — Auditoria (2026-06-08)

## Resumo

Tentativa de criar PR da Sprint 1 via Pi best (`opencode-go/minimax-m3`).
Sessão morta DUAS vezes: primeiro por timeout Hermes, depois por quota Go.

## Sessão 1 (08:24) — Timeout prematuro

| Métrica | Valor |
|---------|-------|
| **Arquivo** | `2026-06-08T08-24-47-747Z_....jsonl` |
| **Entradas** | 129 |
| **Duração** | ~6.5 min |
| **Causa da morte** | 180s foreground timeout (Hermes) |
| **Estágio** | Leitura de código — nunca escreveu |

## Sessão 2 (08:31) — Timeout prematuro (re-lançada sem --session)

| Métrica | Valor |
|---------|-------|
| **Arquivo** | `2026-06-08T08-31-43-429Z_....jsonl` |
| **Entradas** | 497 |
| **Duração** | ~10 min |
| **Causa da morte** | 180s foreground timeout |
| **Estágio** | Leitura de código (git diffs, schemas, routes) — nunca escreveu |

ERRO: Relancei `pi -p "$(cat prompt.md)"` do zero em vez de reabrir
com `pi --session`. Perdeu-se todo o contexto acumulado da sessão 1.

## Sessão 3 (08:53) — Quota Go exaurida

| Métrica | Valor |
|---------|-------|
| **Arquivo** | `2026-06-08T08-53-00-153Z_....jsonl` |
| **Entradas** | 442 |
| **Duração** | ~30 min |
| **Modo** | Background (sem timeout) |
| **Causa da morte** | `GoUsageLimitError` — 5h mensais esgotadas |
| **Estágio** | Completou leitura, começou a escrever docs (api-contracts.yaml, release-notes.md, test-plan.md, tech-specs.md, SAD.md, ERD.md, backlog.md, .gitignore) |

## Lições

1. **Sempre usar `background=true` + `notify_on_complete=true` para Pi best**
   Foreground timeout de 180s é insuficiente — Pi best leva 5-10 min só lendo.

2. **Sempre `pi --session` para retomar sessão morta**
   Relançar do zero queima centenas de milhares de tokens e perde contexto.
   `--session` carrega histórico e continua sem perder progresso.

3. **Pi best NÃO precisa de tool_use calls para fazer trabalho**
   0 tool_use em 442 entradas, mas escreveu 8+ arquivos de documentação.
   O trabalho foi feito via `bash` + `cat >` heredocs internos.

4. **Git add/commit falha com UID 1001 vs 10000**
   Correção: `ssh oracle-host 'sudo chmod -R o+w /caminho/.git/objects/ /caminho/.git/refs/'`
