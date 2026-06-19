# agy Protobuf Parsing — Field Hierarchy & Heurística de Títulos

## Field Hierarchy (from CortexStepGeneratorMetadata)

```
gen_metadata (table) = repeated CortexStepGeneratorMetadata
  └── field 1 → ChatModelMetadata (oneof: chat_model)
       ├── field 3 → model (enum)
       │    1016 = Gemini 3.5 Flash
       │    1020 = Gemini 3.1 Pro
       │    (sempre validar com `agy models`)
       └── field 4 → ModelUsageStats
            ├── field 2 → input_tokens (uint64)
            ├── field 3 → output_tokens (uint64)
            ├── field 4 → cache_write_tokens (uint64)
            ├── field 5 → cache_read_tokens (uint64)
            ├── field 9 → thinking_output_tokens (uint64)
            └── field 10 → response_output_tokens (uint64)
```

## Heurística para Extrair Título da Sessão

O `state.vscdb` do IDE armazena o título em `TrajectorySummary.title`,
mas os DBs de conversa do CLI **não têm** nome amigável. Use os `step_payload`
da tabela `steps` para extrair o primeiro prompt do usuário:

```python
def extract_prompt_from_steps(steps):
    """Busca texto de prompt do usuário nos step_payload BLOBs"""
    for idx, stype, status, task, payload in steps:
        if not payload: continue
        i = 0
        while i < len(payload):
            if i >= len(payload): break
            key = payload[i]; wt = key & 0x07; i += 1
            if wt == 2:
                length, i2 = dv(payload, i)
                if length is None or i2 + length > len(payload): break
                sub = payload[i2:i2+length]; i = i2 + length
                try:
                    t = sub.decode('utf-8')
                    # Filtros para texto real vs IDs/binário
                    if (t.count(" ") > 2 and any(c.islower() for c in t[:30])
                        and len(t) > 20 and len(t) < 500
                        and not t.startswith("file://")
                        and "lint error" not in t[:50]
                        and "Prioritizing Tool" not in t[:30]
                        and "As IDE" not in t[:20]
                        and sum(1 for c in t[:20] if c in "0123456789abcdef-") < 10):
                        return t.strip()
                except:
                    pass
            elif wt == 0:
                v, i = dv(payload, i)
                if v is None: break
            elif wt == 5: i += 4
            elif wt == 1: i += 8
    return "(unnamed)"
```

## Pitfalls

- Model ID pode ser 0 em sessões antigas — usar MODEL_MAP com fallback
- DBs sem steps ou com 1 gen_metadata vazio = sessão abortada, ignorar
- Prompt extraído pode conter lixo binário no final — truncar no primeiro caractere de controle
- Valores uint64 > 2^63 são int64 negativos — sempre converter
