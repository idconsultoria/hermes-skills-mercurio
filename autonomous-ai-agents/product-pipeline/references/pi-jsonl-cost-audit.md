# Pi Agent Cost Auditing via .jsonl

## Fonte de Dados

Pi Agent armazena logs de sessão em `/home/pi/.pi/agent/sessions/` como arquivos `.jsonl`.
Cada linha é uma chamada de API com metadados de tokens.

**Localização no Pi:**
```
~/.pi/agent/sessions/
└── --workspace-code-workstation-PROJETO--/
    ├── session_<id>.jsonl
    └── ...
```

## Script de Extração

```python
import json, os, glob
from collections import defaultdict

sessions = glob.glob(
    os.path.expanduser("~/.pi/agent/sessions/*/*.jsonl")
)

data = []
for path in sessions:
    with open(path) as f:
        for line in f:
            call = json.loads(line.strip())
            meta = call.get("response_metadata", {})
            sess = meta.get("session", {})
            data.append({
                "model": sess.get("model", "unknown"),
                "input_tokens": call.get("input_tokens", 0),
                "output_tokens": call.get("output_tokens", 0),
            })

# Agregar por sessão
by_session = defaultdict(lambda: {"calls": 0, "in": 0, "out": 0, "models": set()})
for d in data:
    s = d.get("session_id", "unknown")
    by_session[s]["calls"] += 1
    by_session[s]["in"] += d["input_tokens"]
    by_session[s]["out"] += d["output_tokens"]
    by_session[s]["models"].add(d["model"])

for sid, info in sorted(by_session.items()):
    print(f"{sid}: {info['calls']} calls, {info['in']} in, {info['out']} out, models={info['models']}")
```

## Cálculo de Custo

Usar preços do provedor e taxa de cache hit:

```python
PRICES = {
    "deepseek-v4-flash": {
        "input_miss": 0.14 / 1_000_000,
        "input_hit": 0.0028 / 1_000_000,
        "output": 0.28 / 1_000_000,
        "cache_hit_rate": 0.98,
    },
    "deepseek-v4-pro": {
        "input_miss": 0.435 / 1_000_000,
        "input_hit": 0.003625 / 1_000_000,
        "output": 0.87 / 1_000_000,
        "cache_hit_rate": 0.90,
    },
}

def calc_cost(model, input_tokens, output_tokens):
    p = PRICES[model]
    return (
        input_tokens * (1 - p["cache_hit_rate"]) * p["input_miss"]
        + input_tokens * p["cache_hit_rate"] * p["input_hit"]
        + output_tokens * p["output"]
    )
```

## Notas

- `.jsonl` filenames codificam paths como `--workspace-code-workstation-PROJETO--`.
- Cada linha tem `input_tokens`, `output_tokens`. Algumas são system/internal (sem `session_id`).
- Filtrar por diretório de trabalho para isolar um projeto.
- MiniMax M3 (free tier, 429) não gera linhas de custo.
