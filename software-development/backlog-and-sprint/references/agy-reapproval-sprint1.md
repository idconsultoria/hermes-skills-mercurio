# Agy Re-Approval Cycle — Sprint 1 TaskFlow (Real Example)

> **Sprint:** Sprint 1 reattempt (sprint1-v2)
> **Projeto:** taskflow
> **Data:** 2026-06-08

## Contexto

A Sprint 1 original pulou o agy review — Pi gerou wireframes/user-flows/prototype, marcou `PHASE_COMPLETE: design`, e a sprint avançou para engineering sem validação visual. Na reattempt (sprint1-v2), o agy review foi executado e identificou 3 ressalvas:

| # | Ressalva | Severidade |
|---|----------|------------|
| 1 | Símbolo NLP `!p` conflita com prioridade (deveria ser `!ok`) | ❌ Crítica |
| 2 | CSS `mix-blend-mode: difference` inviável em produção | ⚠️ Alta |
| 3 | Backtracking no Focus Mode sem UX de undo | ⚠️ Alta |

## Ciclo de Correção

### 1. Pi best (`opencode-go/minimax-m3`) — 3 correções

- **Custo:** $0.77
- **Duração:** 907s (15 min)
- **Entries:** 125
- **Provider:** opencode-go / minimax-m3

Pi corrigiu os 3 arquivos (user-stories.md, prototype.html, user-flows.md) mas bloqueou no `PHASE_COMPLETE: design-fixes` (EACCES — arquivo owned por uid 1001). Seguiu a REGRA ABSOLUTA do AGENTS.md: criou `permission-block-*.log` e parou.

> **Fix:** `ssh oracle-host 'sudo chmod -R o+w /home/ubuntu/selfhost/shared/code/workstation/taskflow/product/sprint_1/'` + patch manual do marcador.

### 2. Agy re-review (`opencode-go/gemini-3.5-flash`) — confirmação + implementação

Agy foi invocado novamente para verificar as 3 correções. Durante a re-revisão:

1. Leu os arquivos corrigidos via `git diff HEAD~1 HEAD`
2. Verificou cada correção individualmente
3. **Foi além:** implementou o botão "Desfazer e Mover de Volta para Inbox" diretamente no prototype.html (+111 linhas) porque a feature estava especificada em user-flows.md mas ausente no HTML
4. Marcou: `DESIGN REVIEW FINAL: APROVADO SEM RESSALVAS`

### Lições

1. **Agy implementa features faltantes** — não só revisa. Incluir "*If something is missing that the spec requires, implement it*" no prompt de re-review.
2. **Aprovar permissões com option 3** — agy pede confirmação para cada comando (git status, git log, git diff, git show, git add, git commit). Option 3 (always allow in settings.json) evita prompts repetitivos.
3. **Check diff após agy** — agy pode ter feito alterações que não estão no feedbacks.md. `git diff HEAD` revela o que ele implementou diretamente.
4. **`PHASE_COMPLETE` sem `ACORDO` = design incompleto** — Pi marca `PHASE_COMPLETE` ao terminar a geração. O verdadeiro gate é o `ACORDO` do agy. Numa reattempt, verificar ambos.
