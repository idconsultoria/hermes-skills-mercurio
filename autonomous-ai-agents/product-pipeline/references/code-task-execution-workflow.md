# Code Task Execution Workflow

> Pattern validated in TaskFlow (72 tasks, 11 layers, ~7.500 linhas em ~2h)

## Visão Geral

```
code-tasks.md → [LER por layer] → [AGRUPAR em lote] → [Pi gera] → [VERIFICAR] → [COMMIT] → [todo() update] → próximo layer
```

Cada layer vira UM prompt para Pi, não 72 prompts individuais.

## Passo a Passo

### 1. Ler o escopo do layer

```bash
grep "^## LAYER\|^### Task-" product/engineering/code-tasks.md
```

Isso mostra a estrutura completa: quantas tasks, o que cada uma faz, dependências.

### 2. Construir o prompt do lote

Ler as tasks específicas do layer em code-tasks.md com `read_file` e construir um prompt único:

```
"Execute Tasks X-Y em batch:
Task-X: [descrição resumida + specs]
Task-Y: [descrição resumida + specs]
...
Crie TODOS os arquivos e confirme quando terminar."
```

Regras:
- Incluir a estrutura exata de diretórios e nomes de arquivo
- Incluir os critérios de aceitação como parte da descrição
- Para models: especificar SQLAlchemy 2.0 style (mapped_column, Mapped, relationship)
- Para schemas: especificar `model_config = ConfigDict(from_attributes=True)`
- Para routes: especificar padrão de injeção de dependência (Depends(get_current_user))

### 3. Invocar Pi

```bash
ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
LC_DIR=code/PROJETO pi-agent 'pi -c -p "<prompt completo do lote>" --provider deepseek --model deepseek/deepseek-v4-flash'
ENDSCRIPT
```

- Usar `pi -c` (continua sessão existente) — se não existir, criar com `pi --name "projeto-code"`
- v4-flash é suficiente para CODE (não precisa de v4-pro para implementação)
- timeout natural do SSH (~600s) é suficiente para lotes de até ~15 tasks

### 4. Verificar arquivos

```bash
# Listar arquivos criados
find /opt/data/code/workstation/PROJETO/<path> -type f | sort

# Checar linhas
wc -l /opt/data/code/workstation/PROJETO/<path>/*

# Chegar conteúdo crítico (se aplicável)
grep -c "keyword\|pattern" /opt/data/code/workstation/PROJETO/<path>/*
```

### 5. Commitar

```bash
ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
git add <path/glob> && git commit -m "feat: Tasks X-Y — descrição concisa"
ENDSCRIPT
```

Usar `git add` com path específico (não `-A`) para evitar mixed ownership issues.

### 6. Atualizar progresso

```bash
todo(todos=[{id: "layer-X", content: "descrição", status: "completed"}, ...])
```

## Tamanhos de lote (valores práticos)

| Tipo de task | Tasks por lote | Prompt size | Tempo Pi |
|---|---|---|---|
| Migrations (alembic) | 8-10 | ~2.000 chars | 2-3 min |
| Models (SQLAlchemy) | 6-8 | ~2.500 chars | 2-3 min |
| Repositories | 5-7 | ~2.500 chars | 2-3 min |
| Services | 8-10 | ~3.000 chars | 3-5 min |
| Schemas + Middleware + Routes | 15-20 | ~4.000 chars | 5-8 min |
| Infra (Docker, compose, nginx) | 3-5 | ~1.500 chars | 2-3 min |
| Frontend completo | 10-13 | ~4.000 chars | 5-10 min |
| Tests (unit + integration + CI) | 20-25 | ~3.000 chars | 5-10 min |

## Pipeline completo (TaskFlow)

```
Layer  | Tasks | Batch | Tempo
L1     | 001   | 1     | 2 min
L2     | 002-010 | 1   | 4 min
L3     | 011-018 | 1   | 3 min
L4     | 019-024 | 1   | 3 min
L5     | 025-033 | 1   | 4 min
L6-8   | 034-052 | 1   | 6 min
L9     | 053-056 | 1   | 3 min
L10    | 057-069 | 1   | 7 min
L11    | 070-072 | 1   | 6 min
Total  | 72      | 9   | ~40 min Pi + ~10 min verify/commit
```

## Pitfalls

- **Não usar create-vite**: scaffolding interativo não funciona no pi-agent. Criar package.json + configs manualmente.
- **Não esquecer `chmod -R 777`**: se Hermes precisar ler/escrever os arquivos depois, Pi cria com 755.
- **Sessão Pi morre se o container reiniciar**: verificar com `pi -r` antes de continuar.
- **v4-flash vs v4-pro**: flash gera código de qualidade equivalente para implementação. Reservar pro para decisões de arquitetura/design.
- **Prompt muito grande**: se Pi parar de responder sem erro, o prompt pode ter excedido o limite de contexto. Quebrar em 2 lotes menores.
