"""
Exponential backoff com jitter — padrão do repositório para chamadas a APIs externas.

Uso:
    from agemini.backoff import retry_call

    result = retry_call(lambda: api.do_something(), max_attempts=5)

Ou como decorator:
    from agemini.backoff import backoff

    @backoff(max_attempts=5)
    def minha_funcao():
        ...

Parâmetros:
    max_attempts  — tentativas máximas (default: 5)
    base_delay    — delay inicial em segundos (default: 1.0)
    max_delay     — delay máximo em segundos (default: 120.0)
    backoff_factor — fator multiplicativo (default: 2.0)
    jitter        — True para adicionar ruído aleatório (default: True)
    retry_on      — tupla de exceções que disparam retry (default: Exception)
"""

import time
import random
import logging
import functools
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)

RETRYABLE_EXCEPTIONS = (Exception,)


def _is_rate_limit(exc: Exception) -> bool:
    """Detecta erros de rate limit / quota (HTTP 429 e equivalentes)."""
    msg = str(exc).lower()
    return any(kw in msg for kw in (
        '429', 'resource_exhausted', 'quota', 'rate limit',
        'too many requests', 'retry'
    ))


def _extract_retry_delay(exc: Exception) -> float | None:
    """Extrai o retry_delay sugerido pela API (ex: 'retry in 48.87s')."""
    import re
    match = re.search(r'retry in (\d+\.?\d*)s', str(exc))
    if match:
        return float(match.group(1))
    match = re.search(r'retry_delay.*?seconds:\s*(\d+)', str(exc))
    if match:
        return float(match.group(1))
    return None


def retry_call(
    fn: Callable,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 120.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_on: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    retry_predicate: Callable[[Exception], bool] | None = None,
) -> object:
    """Chama fn() com exponential backoff."""
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except retry_on as e:
            last_exc = e
            if retry_predicate and not retry_predicate(e):
                raise
            if retry_predicate is None and not _is_rate_limit(e):
                raise
            if attempt == max_attempts:
                logger.error(f'Todas as {max_attempts} tentativas esgotadas: {e}')
                raise

            suggested = _extract_retry_delay(e)
            if suggested is not None:
                delay = min(suggested + 5, max_delay)
            else:
                delay = base_delay * (backoff_factor ** (attempt - 1))
                delay = min(delay, max_delay)

            if jitter:
                delay *= 0.75 + random.random() * 0.5

            logger.warning(
                f'Backoff tentativa {attempt}/{max_attempts}: '
                f'agurdando {delay:.1f}s... ({type(e).__name__})'
            )
            time.sleep(delay)

    raise last_exc  # type: ignore


def backoff(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 120.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_on: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    retry_predicate: Callable[[Exception], bool] | None = None,
):
    """Decorator para aplicar exponential backoff a uma função."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry_call(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                jitter=jitter,
                retry_on=retry_on,
                retry_predicate=retry_predicate,
            )
        return wrapper
    return decorator
