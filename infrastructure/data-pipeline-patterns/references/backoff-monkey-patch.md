# Exponential Backoff — Monkey-Patch Pattern

## Architecture

Two-layer backoff in Dédalo Squad:

1. **Module:** `agemini/backoff.py` — generic `retry_call()` + `@backoff` decorator
2. **Injection:** `agemini/modelos/gemini.py` — monkey-patches `genai` at import time

## Monkey-patch code (gemini.py:24-53)

```python
import google.generativeai as genai
from agemini.backoff import retry_call

_original_generate_content = genai.GenerativeModel.generate_content
_original_send_message = genai.ChatSession.send_message

def _generate_content_with_backoff(self, *args, **kwargs):
    return retry_call(
        lambda: _original_generate_content(self, *args, **kwargs),
        max_attempts=5, base_delay=2.0, max_delay=120.0,
        backoff_factor=2.0, jitter=True,
    )

def _send_message_with_backoff(self, *args, **kwargs):
    return retry_call(
        lambda: _original_send_message(self, *args, **kwargs),
        max_attempts=5, base_delay=2.0, max_delay=120.0,
        backoff_factor=2.0, jitter=True,
    )

genai.GenerativeModel.generate_content = _generate_content_with_backoff
genai.ChatSession.send_message = _send_message_with_backoff
```

## Why monkey-patch

Agents (Diarizador, Escriba, Popeye, Disgrama) call `genai.GenerativeModel`
directly. Modifying each agent would be invasive and error-prone. The patch
at the `genai` module level ensures **all existing and future agents** get
retry automatically — zero code changes needed in agent files.

## Gemini Free Tier Limits

- `gemini-3.1-flash-lite`: 15 RPM per key (GenerateRequestsPerMinutePerProjectPerModel-FreeTier)
- `gemini-3.5-flash`: 20 requests/day total (not RPM!) — unusable for batch
- Error format includes `retry_delay { seconds: N }` — the backoff module parses this

## Google Sheets backoff

`agemini/conectores/google_sheets.py:96-109` — wraps `values().update().execute()` in
`retry_call` with `retry_predicate=lambda e: True` because Sheets API errors
can be 400s (not 429s) and still transient (network, quota).
