# Code Tasks Format

> **Core principle:** Every task should be completable in 2-15 minutes by a
> competent developer. If a task takes longer, it's not small enough — split it.

This document specifies the code-tasks format used in Sprint Engineering (Section 2.5 of `backlog-and-sprint`). Pi best generates the `code-tasks.md` file; Hermes executes it with Pi cost.

---

## Task Format

Each task in `code-tasks.md` follows this structure:

```markdown
## Task-001: Criar modelo Project no banco

**Tipo:** schema
**Depende de:** — (nenhuma)
**Esforço estimado:** 5min

### O que fazer
- Criar migration `001_create_projects.sql`
- Adicionar colunas: id (UUID PK), name (VARCHAR 255), owner_id (UUID FK users), description (TEXT), created_at, updated_at
- Adicionar índices: owner_id, created_at DESC
- Adicionar trigger de updated_at

### Critério de aceite
- [x] Migration cria tabela projects com todas as colunas
- [x] FK owner_id referencia users(id) ON DELETE CASCADE
- [x] Índices criados
- [x] Trigger de updated_at funciona
- [ ] Migration é reversível (down)

### Arquivos afetados
- `backend/migrations/001_create_projects.sql`
- `backend/migrations/001_create_projects.down.sql`

### Status: [ ] pendente  |  [x] concluída  |  [~] em progresso  |  [!] falha
```

### Task Fields

| Field | Description |
|-------|-------------|
| **ID** | `Task-NNN` — unique, sequential |
| **Tipo** | `schema`, `model`, `api`, `service`, `test`, `config`, `docs`, `refactor` |
| **Depende de** | IDs of tasks that must be completed before this one |
| **Esforço** | Estimate in minutes (2-15 ideal) |
| **O que fazer** | Specific, actionable instructions |
| **Critério de aceite** | Checklist that Hermes uses to validate completion |
| **Arquivos afetados** | Exact paths to create/modify |
| **Status** | Progress tracking: `[ ]` pending, `[x]` done, `[~]` in progress, `[!]` failed |

---

## Granularity Rules

| ❌ Too big (split) | ✅ Right size |
|---------------------|---------------|
| "Implementar autenticação" | "Criar tabela users", "Criar endpoint POST /auth/login", "Criar middleware JWT" |
| "Fazer o dashboard" | "Criar query de métricas", "Criar endpoint GET /dashboard/metrics", "Criar componente Card de métrica" |
| "Adicionar testes" | "Testar validação de email no signup", "Testar fluxo de recuperação de senha" |

### Task Generation Rules (Pi best)

When Pi loads this format with engineering documents, it must:

1. **Read all documents:** SAD → TechSpecs → ERD → API Contracts → Test Plan
2. **Break into layers:** First schema, then models, then APIs, then services, then tests
3. **Respect dependencies:** Schema tasks come before API tasks
4. **Estimate effort:** Each task 2-15 min. If it exceeds 15, break into more tasks.
5. **Write `code-tasks.md`** at the project root or under `product/sprint_N/engineering/`

---

## code-tasks.md Template

```markdown
# Code Tasks: [Project Name]

> Gerado em: [date]
> Por: Pi Agent (best model)
> A partir de: SAD, TechSpecs, ERD, API Contracts, Test Plan

## Ordem de execução
As tasks estão ordenadas por dependência. Siga a ordem.

---

## Task-001: [Título curto]

**Tipo:** [schema|model|api|service|test|config|docs|refactor]
**Depende de:** —
**Esforço:** [N] min

### O que fazer
- [ ] Passo 1
- [ ] Passo 2

### Critério de aceite
- [ ] Checklist item 1
- [ ] Checklist item 2

### Arquivos afetados
- `path/to/file`

### Status: [ ] pendente

---

## Task-002: [Título curto]

**Tipo:** api
**Depende de:** Task-001
**Esforço:** 10 min

...

### Status: [ ] pendente
```

---

## Task Execution (Hermes)

Each task is delegated to Pi cost (free Zen → Go → API direta). Never use `timeout N`:

```bash
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "Task-001: Criar migration projects table..." \
  --provider opencode --model opencode/deepseek-v4-flash-free
```

After execution, Hermes validates the output and updates the status:

```bash
# Mark task as done
patch --path /path/to/code-tasks.md \
  --old_string "[ ] pendente" --new_string "[x] concluída"

# Mark task as failed
patch --path /path/to/code-tasks.md \
  --old_string "[ ] pendente" --new_string "[!] falha"
```

---

## Pitfalls

⚠️ **Task too large:** If Pi takes > 15 min on a single task, it should be split. Pause, divide into subtasks, update code-tasks.md.

⚠️ **Task fails repeatedly:** If Pi fails 2x on the same task, it may be a scope issue. Review acceptance criteria or break into smaller tasks.

⚠️ **Circular dependency:** Tasks with dependency A→B→A. Rare, but if it happens, replan the order.

⚠️ **Pi exits with code 0 but no output:** Always verify the output file exists after execution — Pi can stall silently.

⚠️ **Status tracking:** Always update the status marker immediately after validation. Don't batch status updates — one task, one status update.
