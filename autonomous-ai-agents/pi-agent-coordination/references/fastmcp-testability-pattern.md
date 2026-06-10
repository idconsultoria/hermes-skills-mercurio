# FastMCP Testability Pattern — Impl/Wrapper

## O Problema

Testes unitários de MCP tools falham com `TypeError: 'FunctionTool' object is not callable` porque o decorador `@mcp.tool()` do FastMCP 2.x envolve a função original em um objeto `FunctionTool` que não é diretamente chamável.

```python
@mcp.tool(name="taskflow_create_task")
async def taskflow_create_task(...):  # → vira FunctionTool, não mais callável
    ...

# Test tenta:
result = await taskflow_create_task(...)  # TypeError!
```

## Solução: Impl/Wrapper Pattern

Para cada tool, criar uma função `_impl` pura (sem decorador) e um wrapper decorado fino que delega para ela:

```python
# --- Impl (testável) ---
async def _taskflow_create_task_impl(
    title: str,
    priority: int | None = None,
    confirm_token: str | None = None,
) -> dict[str, Any]:
    """Pure implementation — no FastMCP decorator."""
    user_id = get_default_user_id()
    store = get_token_store()
    # ... lógica real ...

# --- Wrapper (MCP tool) ---
@mcp.tool(
    name="taskflow_create_task",
    description="Cria uma nova task. Requer confirmação via ActionToken.",
)
async def taskflow_create_task(
    title: str,
    priority: int | None = None,
    confirm_token: str | None = None,
) -> dict[str, Any]:
    """MCP tool — delegates to _impl for testability."""
    return await _taskflow_create_task_impl(
        title=title,
        priority=priority,
        confirm_token=confirm_token,
    )
```

## Nos Testes

Importar a `_impl` em vez da função decorada:

```python
from taskflow.mcp.tools.core import (
    _taskflow_create_task_impl,   # ✅ certa
    # taskflow_create_task,       # ❌ FunctionTool, não callável
)

# Usa normalmente — sem decorador
result = await _taskflow_create_task_impl(
    title="Test Task",
    priority=2,
)
```

## Funciona para Todos os Decoradores FastMCP

| Decorador | Aplica-se a |
|-----------|-------------|
| `@mcp.tool()` | tools |
| `@mcp.resource()` | resources |
| `@mcp.prompt()` | prompts |

Os 3 tipos de decorador produzem objetos não-calláveis. Use `_impl` para todos.

## Atenção

- A função `_impl` DEVE ser importável (`__all__` ou exposta no módulo)
- O wrapper NÃO pode adicionar lógica extra — só delegar
- Patches com `replace_all` podem duplicar imports (`_taskflow_create_task_impl` → `__taskflow_create_task_impl_impl`) — verificar import line após replace_all
