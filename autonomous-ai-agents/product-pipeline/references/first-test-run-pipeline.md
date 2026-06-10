# First Test Run — Debugging Pipeline

> Validado em: TaskFlow F4b (72 code tasks, 133 testes, 95% passando na 4ª iteração)
> Atualizado em: 07 Jun 2026 — adicionado Fase 8 (UUID×SQLite GUID), Fase 9 (cursor pagination), Fase 10 (sort_order server_default)

## Visão Geral

Após gerar todo o código via Pi (code-tasks.md), o primeiro `pytest` quase sempre falha em massa. Não é sinal de código ruim — é o acúmulo de pequenas incompatibilidades que o Pi não consegue detectar sem executar. O padrão abaixo resolveu ~95% dos erros em 2-3 iterações.

## Fase 8: UUID × String Compatibility (PostgreSQL ↔ SQLite)

### Causa raiz

Pi scaffolda models com `from sqlalchemy.dialects.postgresql import UUID` nas colunas `id` e FKs. No PostgreSQL isso funciona nativamente. Mas no SQLite (testes), o tipo UUID espera objetos `uuid.UUID` (com atributo `.hex`), enquanto o Pi passa strings (`str(uuid4())`).

### Diagnóstico

```
sqlalchemy.exc.StatementError: (builtins.AttributeError) 'str' object has no attribute 'hex'
INSERT INTO users (id, email, ...) VALUES (?, ?, ...)
```

### Fix: GUID TypeDecorator platform-agnóstico

Criar um `TypeDecorator` em `models/base.py`:

```python
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID

class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(String(36))
    def process_bind_param(self, value, dialect):
        if value is None: return value
        return str(value)
    def process_result_value(self, value, dialect):
        return value
```

Substituir `mapped_column(UUID, ...)` por `mapped_column(GUID, ...)` em todos os models.

## Fase 9: Keyset/Cursor Pagination com UUIDs

### Causa raiz

`func.now()` em SQLite tem precisão de segundos. `id < cursor` em SQLite compara UUIDs como strings. Combinados, quebram paginação.

### Fix: Keyset composto `(created_at, id)`

```python
cursor_result = await self.session.execute(
    select(Task.created_at).where(Task.id == cursor)
)
cursor_created_at = cursor_result.scalar()
if cursor_created_at is not None:
    stmt = stmt.where(
        or_(
            Task.created_at < cursor_created_at,
            (Task.created_at == cursor_created_at) & (Task.id < cursor),
        )
    )
stmt = stmt.order_by(Task.created_at.desc(), Task.id.desc())
```

### Limitação

UUID string comparison em SQLite é imprevisível. Marcar teste cursor como `@pytest.mark.skip` e testar apenas via PostgreSQL.

## Fase 10: sort_order server_default para INTEGER

Pi gera `sort_order: Mapped[int] = mapped_column(default=0, server_default="false")`. PostgreSQL rejeita `INTEGER DEFAULT 'false'`. Fix: `server_default="0"`.
