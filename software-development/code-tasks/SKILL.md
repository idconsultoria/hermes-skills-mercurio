---
name: code-tasks
description: >-
  Code Tasks generation and execution system. Pi (best model) generates
  bite-sized tasks from engineering docs, then executes them in parallel
  batches by feature. Tracks progress in code-tasks.md. See backlog-and-sprint
  for the full sprint execution workflow.
category: software-development
---

# Code Tasks

> **Core principle:** Every task should be completable in 2-15 minutes by a
> competent developer. If a task takes longer, it's not small enough — split it.

## When to Load This Skill

- After engineering docs (SAD, TechSpecs, ERD, API contracts) are approved
- Before writing any implementation code
- During the MVP build phase (Fase 4 — Engineering)
- During Sprint execution (Fase 5 — Iteration)

---

## 1. Flow Overview

```
Pi (best model)
    │
    ├── Lê: SAD, TechSpecs, ERD, API Contracts, Test Plan
    ├── Gera: code-tasks.md (lista exaustiva de tarefas)
    └── Entrega para: Hermes
                    │
                    ▼
        ┌─────────────────────────────┐
        │   Hermes                     │
        │   1. Lê primeira task        │
        │   2. Invoca Pi (cost)        │
        │   3. Valida resultado        │
        │   4. Marca [x] ou [FAIL]     │
        │   5. Próxima task...         │
        └─────────────────────────────┘
                    │
                    ▼
          Todas completas?
              │          │
             Sim        Não
              │          │
              ▼          ▼
        Pi (best)    Corrige +
        revisão +    nova task
        build
```

---

## 2. Task Format

Cada task em `code-tasks.md` segue este formato:

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

### Campos da task

| Campo | Descrição |
|-------|-----------|
| **ID** | `Task-NNN` — único, sequencial |
| **Tipo** | `schema`, `model`, `api`, `service`, `test`, `config`, `docs`, `refactor` |
| **Depende de** | IDs das tasks que precisam estar prontas antes |
| **Esforço** | Estimativa em minutos (2-15 ideal) |
| **O que fazer** | Instruções específicas e acionáveis |
| **Critério de aceite** | Checklist que Hermes usa para validar |
| **Arquivos afetados** | Paths exatos para criar/modificar |
| **Status** | Controle de progresso |

---

## 3. Geração de Tasks (Pi — modelo best)

Quando Pi carrega esta skill com os documentos de engenharia, ele deve:

1. **Ler todos os documentos:** SAD → TechSpecs → ERD → API Contracts → Test Plan
2. **Quebrar em camadas:** Primeiro schema, depois modelos, depois APIs, depois serviços, depois testes
3. **Respeitar dependências:** Tasks de schema vêm antes de tasks de API
4. **Estimar esforço:** Cada task 2-15 min. Se passar de 15, quebrar em mais tasks.
5. **Escrever `code-tasks.md`** na raiz do projeto

### Regras de granularidade

| ❌ Muito grande (quebrar) | ✅ Tamanho certo |
|--------------------------|-----------------|
| "Implementar autenticação" | "Criar tabela users", "Criar endpoint POST /auth/login", "Criar middleware JWT" |
| "Fazer o dashboard" | "Criar query de métricas", "Criar endpoint GET /dashboard/metrics", "Criar componente Card de métrica" |
| "Adicionar testes" | "Testar validação de email no signup", "Testar fluxo de recuperação de senha" |

---

## 4. Execução (Hermes) — ver `backlog-and-sprint` para detalhes de paralelismo

A execução das code-tasks é coberta pela skill `backlog-and-sprint` (seção 2.5). Features independentes rodam em paralelo, cada uma com seu próprio `pi -p` em background.

### 4.1 Setup Inicial

```bash
ls -la /opt/data/code/workstation/PROJETO/product/engineering/code-tasks.md
```

### 4.2 Delegar para Pi (modelo cost-effective)

Provider priority: free Zen → Go → API direta. NUNCA usar `timeout N`:

```bash
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "Task-001: Criar migration projects table..." \
  --provider opencode --model opencode/deepseek-v4-flash-free
```

### 4.3 Validação (Hermes)

```bash
ls -la backend/migrations/001_create_projects.sql
head -20 backend/migrations/001_create_projects.sql
```

### 4.4 Atualizar Status

```bash
# Marcar task como concluída no code-tasks.md
patch --path /opt/data/code/workstation/PROJETO/product/engineering/code-tasks.md \
  --old_string "[ ] pendente" --new_string "[x] concluída"
```

Se falhou:

```bash
patch --path /opt/data/code/workstation/PROJETO/product/engineering/code-tasks.md \
  --old_string "[ ] pendente" --new_string "[!] falha"
```

---

## 5. Integração com o Pipeline

### Fase 4 — MVP Engineering

```bash
# 1. Pi (best) gera code-tasks.md
# 2. Hermes executa tasks sequencialmente
# 3. Pi (best) revisa + build final
# 4. agy testa e dá feedback
# 5. Pi (best) cria novas tasks dos feedbacks
# 6. Repete até agy aprovar
```

### Fase 5 — Sprint

```bash
# Para cada Sprint i:
# 1. Pi (best) com skills de PM revisa backlog → define user stories
# 2. Pi (best) com skills de UX/UI faz wireframes → agy revisa
# 3. Pi (best) com skills de engenharia gera code-tasks.md
# 4. Hermes executa tasks
# 5. agy testa
# 6. Reporta pro usuário
```

---

## 6. code-tasks.md Template

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

## 7. Exemplo de Ciclo Completo

```bash
# Hermes lê code-tasks.md
# Task-001: Criar migration users table (schema)
# Status: [ ] pendente

# Hermes delega pro Pi (local, sem timeout)
PATH="/opt/data/pi-global/bin:$PATH" \
  pi -p "Task-001: Criar migration users..." \
  --provider opencode --model opencode/deepseek-v4-flash-free

# Pi executa, Hermes valida
ls backend/migrations/001_create_users.sql  # ✅ existe

# Hermes marca concluída
patch --path product/engineering/code-tasks.md \
  --old_string "[ ] pendente" --new_string "[x] concluída"

# Próxima task: Task-002: Model User (depende de Task-001)
```

---

## Dependências

Esta skill depende de:

| Recurso | Para quê |
|---------|----------|
| **Pi Agent** (local) | `pi -p "..." --provider deepseek --model deepseek-v4-flash` |
| **Skills de engenharia no Pi** | Documentos de entrada para gerar code-tasks |
| **Eng docs no projeto** | `product/engineering/*.md` — contexto para geração de tasks |

---

## Pitfalls

⚠️ **Task grande demais:** Se Pi demorar > 15 min numa task, é sinal que ela deveria ser quebrada. Pause, divida em subtasks, atualize code-tasks.md.

⚠️ **Task falha repetidamente:** Se Pi falhar 2x na mesma task, pode ser problema de escopo. Reveja os critérios de aceite ou quebre em tasks menores.

⚠️ **Dependência circular:** Tasks com dependência A→B→A. Raro, mas se acontecer, replaneje a ordem.

----
