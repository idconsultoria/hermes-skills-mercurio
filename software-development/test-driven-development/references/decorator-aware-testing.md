# Testing Decorated Functions (Impl/Wrapper Pattern)

## Problem

Async functions decorated with framework decorators (like `@mcp.tool()` from FastMCP) wrap the original function in a framework object that is NOT callable directly. Tests that import and `await` the decorated function fail with:

```
TypeError: 'FunctionTool' object is not callable
```

This happens because `@mcp.tool()` replaces `taskflow_create_task` with a `FunctionTool` instance. Other decorators (`@app.get()`, `@router.post()`, `@click.command()`) may have similar issues.

## Solution: Impl/Wrapper Pattern

Extract the business logic into a private `_impl` function (no decorator), then create a thin decorated wrapper that delegates to it:

```python
# ❌ Before — tests can't call the decorated function
@mcp.tool(name="taskflow_create_task")
async def taskflow_create_task(title: str, ...) -> dict:
    # Business logic here
    ...

# ✅ After — tests call the _impl function directly
async def _taskflow_create_task_impl(title: str, ...) -> dict:
    """Pure implementation — no decorator, directly testable."""
    # Business logic here
    ...

@mcp.tool(name="taskflow_create_task")
async def taskflow_create_task(title: str, ...) -> dict:
    """MCP tool — thin wrapper."""
    return await _taskflow_create_task_impl(title=title, ...)
```

## Test Changes

```python
# ❌ Before
from module import decorated_func
result = await decorated_func(...)

# ✅ After
from module import _decorated_func_impl
result = await _decorated_func_impl(...)
```

## When to Use

- Framework decorators (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt`, `@app.get`, `@router.post`)
- Any decorator that replaces the function with a non-callable proxy object
- When the decorated function contains logic worth testing in isolation (not just routing/plumbing)

## When NOT to Use

- Simple routing decorators (`@app.get("/health")`) that just return static data — integration test at the HTTP level instead
- Decorators that preserve callability (e.g., `@functools.wraps` wrappers, `@pytest.mark.asyncio`)
- When the test framework supports the decorator natively (e.g., FastMCP's test client)

## Verification

After refactoring: run both unit tests (calling `_impl`) and integration tests (calling the decorated version through the framework) to confirm both paths work.
