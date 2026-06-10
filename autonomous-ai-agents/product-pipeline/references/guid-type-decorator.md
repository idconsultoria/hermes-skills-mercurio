# GUID TypeDecorator — Cross-Dialect UUID

> **Problema:** Pi scaffolda models com `mapped_column(UUID, ...)` importando de `sqlalchemy.dialects.postgresql`. Isso funciona com PostgreSQL mas quebra em SQLite com `AttributeError: 'str' object has no attribute 'hex'`, porque o type processor do PostgreSQL UUID espera `uuid.UUID` mas recebe string.

## Solução: TypeDecorator com fallback

Adicionar ao `models/base.py`:

```python
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID natively, falls back to String(36) for SQLite.
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        return value  # keep as string
```

## Migração

1. Adicionar `GUID` ao `models/base.py`
2. Em CADA model: trocar `from sqlalchemy.dialects.postgresql import UUID` por importar `GUID` de `models.base`
3. Trocar `mapped_column(UUID, ...)` → `mapped_column(GUID, ...)` em TODOS os models
4. Rebuildar a imagem Docker (`docker compose build backend --no-cache`)

## Models a atualizar

- user.py: `id`
- task.py: `id`, `user_id`, `project_id`, `context_id`, `parent_task_id`
- project.py: `id`, `user_id`
- context.py: `id`, `user_id`
- subtask.py: `id`, `task_id`
- webhook.py: `id`, `user_id`
- report.py: `id`, `user_id`
- gcal_sync.py: `id`, `user_id`

## Verificação

```bash
# Teste unitário (SQLite):
docker exec taskflow-backend bash -c "cd /app && python -m pytest tests/unit/ -x --tb=short -q"

# Teste de integração (PostgreSQL via container):
docker exec taskflow-backend bash -c "cd /app && python -m pytest tests/integration/ -x --tb=short -q"

# Confirma nenhum import de UUID postgresql nos models:
grep -rn "from sqlalchemy.dialects.postgresql import UUID" backend/taskflow/models/
# Esperado: nenhum resultado
```
