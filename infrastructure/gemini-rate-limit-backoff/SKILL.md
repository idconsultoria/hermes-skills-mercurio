---
name: gemini-rate-limit-backoff
description: "Exponential backoff for Google Gemini API rate limits (HTTP 429) — monkey-patching the genai SDK with jitter.

Load this skill when Gemini returns 429 ResourceExhausted, you need to handle rate limits at scale, or you're building a multi-agent pipeline that calls Gemini from multiple agents simultaneously. Covers monkey-patching the genai SDK, extracting retry_delay from error messages, exponential backoff with jitter, and transparent retry for cron jobs."
trigger: Gemini API rate limit errors (HTTP 429, ResourceExhausted, quota exceeded), multi-agent Gemini pipelines, or setting up resilient Gemini API clients in Python.
related_skills: [autonomous-ai-agents, html-to-pdf-chromium]
---

# Gemini API — Exponential Backoff

## O problema

O free tier do Gemini tem limites severos:
- **gemini-3.1-flash-lite:** 15 RPM (requests per minute), 1000 RPD (requests per day)
- **gemini-2.5-flash:** 20 RPM, 1500 RPD

Com múltiplos agentes chamando a API simultaneamente (diarização, questionário, POP, BPMN), 4 processos paralelos estouram 15 RPM facilmente.

## Solução: monkey-patch no SDK

Em vez de modificar cada agente individualmente, aplica-se um monkey-patch no `google.generativeai` que injeta exponential backoff em `generate_content()` e `send_message()`. **Zero mudanças nos agentes.**

```python
# agemini/modelos/gemini.py

import google.generativeai as genai
from agemini.backoff import retry_call

_original_generate_content = genai.GenerativeModel.generate_content
_original_send_message = genai.ChatSession.send_message

def _generate_content_with_backoff(self, *args, **kwargs):
    return retry_call(
        lambda: _original_generate_content(self, *args, **kwargs),
        max_attempts=5,
        base_delay=2.0,
        max_delay=120.0,
        backoff_factor=2.0,
        jitter=True,
    )

genai.GenerativeModel.generate_content = _generate_content_with_backoff
genai.ChatSession.send_message = _send_message_with_backoff  # idêntico
```

## Módulo reutilizável: `agemini/backoff.py`

Fornece `retry_call()` e decorator `@backoff`. Usar em qualquer chamada de API externa.

### `retry_call(fn, max_attempts=5, base_delay=1.0, max_delay=120.0, backoff_factor=2.0, jitter=True)`

Estratégia de delay:
1. Extrai `retry_delay` da mensagem de erro do Gemini (`"retry in 48.87s"`)
2. Se disponível, usa `retry_delay + 5s`
3. Senão: `base_delay * backoff_factor^(attempt-1)` com jitter ±25%

```
Tentativa 1: falha → 2s * 2^0 = 2s   (±0.5s jitter)
Tentativa 2: falha → 2s * 2^1 = 4s   (±1s)
Tentativa 3: falha → 2s * 2^2 = 8s   (±2s)
Tentativa 4: falha → 2s * 2^3 = 16s  (±4s)
Tentativa 5: falha → raise
```

Se a API sugerir `retry in 48s` na tentativa 2, usa 53s em vez de 4s.

### Detecção de rate limit

A função `_is_rate_limit(exc)` verifica a mensagem da exceção por palavras-chave:
`429`, `resource_exhausted`, `quota`, `rate limit`, `too many requests`, `retry`

### Decorator

```python
from agemini.backoff import backoff

@backoff(max_attempts=3, base_delay=5.0)
def minha_chamada_api():
    ...
```

## Estratégia de execução com múltiplos agentes

Com o monkey-patch ativo, a estratégia de paralelismo muda:

| Abordagem | Antes | Depois |
|-----------|-------|--------|
| 4 processos em paralelo | ❌ 429 em todos | ✅ Backoff serializa automaticamente |
| Sequencial | ✅ Lento mas seguro | ✅ Mais rápido (backoff só quando necessário) |

O backoff transforma paralelismo ingênuo em paralelismo resiliente — se 2 processos colidem, o que recebe 429 espera o `retry_delay` sugerido enquanto o outro conclui.

## Pitfalls

- **Monkey-patch deve ser aplicado ANTES de qualquer import de agente.** O padrão no Dédalo Squad é fazer o import em `gemini.py` que é carregado via `from agemini import modelos` no `elaboracao_de_pops_e_diagramas.py`.
- **Não use `time.sleep` fixo** — o `retry_delay` da API reflete a janela real de rate limit e é muito mais eficiente que um sleep arbitrário de 60s.
- **Free tier vs paid:** os limites são por projeto GCP. Múltiplas API keys no mesmo projeto compartilham a mesma cota. Para escalar, use projetos GCP diferentes ou paid tier.
- **Jitter é essencial** — sem jitter, múltiplos processos que recebem 429 simultaneamente tendem a colidir de novo no mesmo segundo após o backoff.
