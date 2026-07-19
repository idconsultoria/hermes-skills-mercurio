# Hermes state.db — Schema & Cost Query Patterns

> Última verificação: 2026-07-16. Schema pode divergir entre versões do Hermes — sempre confirme com `PRAGMA table_info(sessions)` antes de queries novas.

## Localização

O banco principal é `state.db` no diretório de trabalho do Hermes (não em `~/.hermes/`). Em Docker, tipicamente em `/opt/data/state.db`.

```bash
# Confirmar localização
python3 -c "import os; print(os.path.getsize('/opt/data/state.db'))"
```

> ⚠️ O `~/.hermes/state.db` pode existir mas estar vazio (0 bytes). O banco real é o do diretório de trabalho.

## Schema da Tabela `sessions`

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- ex: 'cron_b874e9037245_20260716_070017'
    source TEXT NOT NULL,             -- 'cron', 'telegram', 'whatsapp', 'cli'
    user_id TEXT,
    model TEXT,                       -- ex: 'deepseek-v4-pro'
    model_config TEXT,
    system_prompt TEXT,
    parent_session_id TEXT,
    started_at REAL NOT NULL,
    ended_at REAL,
    end_reason TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,        -- cache miss (não-cacheado)
    output_tokens INTEGER DEFAULT 0,       -- tokens de resposta (inclui reasoning?)
    cache_read_tokens INTEGER DEFAULT 0,   -- cache hit
    cache_write_tokens INTEGER DEFAULT 0,  -- tokens escritos no cache
    reasoning_tokens INTEGER DEFAULT 0,    -- tokens de reasoning (DeepSeek thinking)
    cwd TEXT,
    billing_provider TEXT,
    billing_base_url TEXT,
    billing_mode TEXT,
    estimated_cost_usd REAL,
    actual_cost_usd REAL,
    cost_status TEXT,                      -- 'unknown' (não preenchido pelo Hermes)
    cost_source TEXT,                      -- 'none' (não preenchido pelo Hermes)
    pricing_version TEXT,
    title TEXT,
    api_call_count INTEGER DEFAULT 0,
    -- + várias colunas de gateway/session management
);
```

### ⚠️ Armadilhas do Schema

- **Coluna é `id`, NÃO `session_id`.** `WHERE session_id = ?` falha com `no such column`.
- **`cost_status` é `'unknown'` e `actual_cost_usd` é `NULL`** — o Hermes NÃO preenche custos automaticamente. Todo cálculo de custo é manual (tokens × preço).
- **`reasoning_tokens` pode ou não estar incluído em `output_tokens`.** Na prática do DeepSeek, `completion_tokens` = `output_tokens` + `reasoning_tokens`. Mas o state.db pode ou não aplicar essa soma. Na dúvida, tratar como aditivo (pior caso).
- **`cache_write_tokens` é sempre 0** nas sessões observadas — o cache write pode não ser tracked.

## Padrões de Query

### Encontrar sessões de cron jobs específicos

Cron sessions seguem o formato `cron_{job_id_12chars}_{YYYYMMDD_HHMMSS}`.

```sql
-- Todas as sessões de um job específico
SELECT id, model, input_tokens, output_tokens, cache_read_tokens,
       reasoning_tokens, api_call_count, started_at
FROM sessions
WHERE id LIKE 'cron_b874e9037245%'
ORDER BY started_at DESC
LIMIT 10;
```

### Sessões de uma data específica

```sql
SELECT id, model, source,
       input_tokens, output_tokens, cache_read_tokens, reasoning_tokens,
       api_call_count
FROM sessions
WHERE id LIKE '%20260716%'
  AND source = 'cron'
ORDER BY started_at;
```

### Query canônica para cálculo de custo

```python
import sqlite3

SESSIONS = [
    'cron_b874e9037245_20260716_070017',
    'cron_c03bb6e1124c_20260716_103019',
    'cron_e418042f0c99_20260716_104019',
]

conn = sqlite3.connect('/opt/data/state.db')
cur = conn.cursor()

for sid in SESSIONS:
    cur.execute('''
        SELECT id, model, input_tokens, output_tokens,
               cache_read_tokens, reasoning_tokens, api_call_count
        FROM sessions WHERE id = ?
    ''', (sid,))
    row = cur.fetchone()
    if row:
        print(row)

conn.close()
```

## Metodologia de Cálculo de Custo

### Passo 1: Extrair tokens do state.db

Usar a query canônica acima. Colunas relevantes:
- `input_tokens` → cache miss (input NÃO cacheado)
- `cache_read_tokens` → cache hit (input cacheado)
- `output_tokens` → tokens de resposta visível
- `reasoning_tokens` → tokens de thinking (DeepSeek); **adicionar ao output** para custo real

### Passo 2: Obter preços atuais do modelo

**NUNCA usar preços hardcoded de skills antigas.** Preços de API mudam. Buscar no momento:

```
web_search("deepseek-v4-pro API pricing per million tokens 2026 opencode go")
```

Sites confiáveis:
- `benchlm.ai/deepseek/api-pricing` — preços atualizados com date de sync
- `aimodelapis.com/providers/opencode-go/opencode-go-deepseek-v4-pro` — preços específicos do provider
- `opencode.ai/data/deepseek/deepseek-v4-pro` — analytics do próprio OpenCode

### Passo 3: Aplicar a fórmula

```python
RATE_MISS = 0.435   # $/M input (cache miss) — VERIFICAR se é o promocional ou standard
RATE_HIT  = 0.003625  # $/M input (cache hit)
RATE_OUT  = 0.87    # $/M output (inclui reasoning)

cost = (
    input_tokens / 1_000_000 * RATE_MISS +
    cache_read_tokens / 1_000_000 * RATE_HIT +
    (output_tokens + reasoning_tokens) / 1_000_000 * RATE_OUT
)
```

### Passo 4: Calcular eficiência de cache

```python
total_input = input_tokens + cache_read_tokens
cache_ratio = cache_read_tokens / total_input  # % de tokens servidos do cache

# Quanto o cache economizou
saved = total_input / 1_000_000 * RATE_MISS - (
    input_tokens / 1_000_000 * RATE_MISS +
    cache_read_tokens / 1_000_000 * RATE_HIT
)
```

### Passo 5: Reportar

Formato padrão: tabela por cron com input miss, cache hit, output, reasoning, custo USD, cache ratio, e total geral. Converter para BRL a ~R$5.50/USD se relevante.

## Preços de Referência (Julho 2026)

> ⚠️ Snapshot. Sempre verificar no momento do cálculo.

### DeepSeek V4 Pro (promocional — vigente)
| Componente | $/1M tokens |
|---|---|
| Input (cache miss) | $0.435 |
| Input (cache hit) | $0.003625 |
| Output (inclui reasoning) | $0.87 |

Provider: opencode-go. Base URL: `https://opencode.ai/zen/go/v1`

### DeepSeek V4 Pro (standard — pode voltar)
| Componente | $/1M tokens |
|---|---|
| Input (cache miss) | $1.74 |
| Input (cache hit) | $0.0145 |
| Output | $3.48 |

### DeepSeek V4 Flash
| Componente | $/1M tokens |
|---|---|
| Input (cache miss) | $0.14 |
| Input (cache hit) | $0.0028 |
| Output | $0.28 |

## Cache na Prática

O cache do DeepSeek é **automático e best-effort** — prefixos de prompt reutilizados (system prompt, skills, instruções fixas) geram cache hits. Não há garantia de hit rate.

Na prática (newsletter IAF, 16/07/2026):
- **88.4% de cache hit** — 1.7M dos 1.95M tokens de input foram servidos do cache
- O cache reduziu o custo de input de $0.85 para $0.10 (8.5× mais barato)
- Crons com prompts longos e skills fixas se beneficiam mais

## Pitfalls

1. **`id` vs `session_id`:** A coluna é `id`. `WHERE session_id = ?` quebra.
2. **`cost_status = 'unknown'`:** O Hermes não calcula custos. Toda estimativa é manual.
3. **`reasoning_tokens` podem ser zero** em modelos sem thinking (ex: Flash).
4. **state.db pode estar em WAL mode** — usar `-shm` e `-wal` coexistem. SQLite lida com isso transparentemente.
5. **Preços promocionais expiram.** O desconto de 75% do DeepSeek V4 Pro pode acabar. Sempre verificar.
6. **openai-compatible providers** podem ter margem diferente do preço direto da DeepSeek. Verificar o preço do provider, não do modelo upstream.
