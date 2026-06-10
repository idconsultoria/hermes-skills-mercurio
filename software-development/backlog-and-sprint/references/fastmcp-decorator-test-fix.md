# FastMCP Decorator Test Fix — `@mcp.tool()`, `@mcp.prompt()`, `@mcp.resource()`

## Erro no CI

```
FAILED test_prompts.py::TestPromptProcessInbox::test_prompt_includes_title
  TypeError: 'FunctionPrompt' object is not callable

FAILED test_resources.py::TestStatsInbox::test_inbox_with_tasks
  TypeError: 'FunctionResource' object is not callable
```

**16 testes falham** — os 3 decoradores FastMCP (`@mcp.tool`, `@mcp.prompt`, `@mcp.resource`) wrappam funções em objetos que só o servidor MCP consegue executar.

## Causa Raiz

FastMCP v2+ (fastmcp >= 2.0.0) converte funções decoradas em objetos internos:

| Decorador | Objeto gerado |
|-----------|---------------|
| `@mcp.tool()` | `FunctionTool` |
| `@mcp.prompt()` | `FunctionPrompt` |
| `@mcp.resource()` | `FunctionResource` |

Nenhum deles é callable diretamente. Testes que importam e tentam `await fn()` quebram.

## Solução: Padrão `_impl` + Wrapper

### 1. Refatorar definição (backend)

```python
# definitions.py — antes
@mcp.prompt(name="process-inbox")
async def prompt_process_inbox(title: str, ...) -> str:
    # lógica aqui
    return result

# definitions.py — depois
async def _prompt_process_inbox_impl(title: str, ...) -> str:
    # lógica aqui (exatamente igual, só renomeada)
    return result

@mcp.prompt(name="process-inbox")
async def prompt_process_inbox(title: str, ...) -> str:
    return await _prompt_process_inbox_impl(title, ...)
```

### 2. Atualizar imports nos testes

```python
# test_prompts.py — antes
from taskflow.mcp.prompts.definitions import (
    prompt_process_inbox,
    prompt_morning_briefing,
    prompt_weekly_review,
)

# test_prompts.py — depois
from taskflow.mcp.prompts.definitions import (
    _prompt_process_inbox_impl as prompt_process_inbox,
    _prompt_morning_briefing_impl as prompt_morning_briefing,
    _prompt_weekly_review_impl as prompt_weekly_review,
)
```

### 3. Verificar CI

```bash
cd /opt/data/code/workstation/taskflow
pytest tests/unit/mcp/test_prompts.py tests/unit/mcp/test_resources.py -v
# 0 failed ✅
```

## Escopo completo dos arquivos que precisam de refatoração

| Arquivo backend | Testes | # tests |
|----------------|--------|---------|
| `backend/taskflow/mcp/tools/core.py` | `tests/unit/mcp/test_core.py` | 6 |
| `backend/taskflow/mcp/tools/gtd.py` | `tests/unit/mcp/test_gtd.py` | 4 |
| `backend/taskflow/mcp/prompts/definitions.py` | `tests/unit/mcp/test_prompts.py` | 9 |
| `backend/taskflow/mcp/resources/stats.py` | `tests/unit/mcp/test_resources.py` | 7 |

**Total: 26 testes** que dependem desse padrão.

## Gatilho

Esse erro aparece no CI quando:
1. Novas MCP tools/prompts/resources são adicionadas com `@mcp.<decorator>()`
2. Testes unitários importam a função decorada em vez da `_impl`
3. O CI testa com `pip install -e .` que resolve os módulos normalmente

## Prevenção

Ao criar novos MCP tools/prompts/resources, SEMPRE:
1. Definir a lógica em `_nome_impl()`
2. Criar wrapper `async def nome(...)` decorado que chama `await _nome_impl(...)`
3. Testar a `_impl`, não a função decorada
