# Session Audit: Sprint 1 Code Tasks Generation

> **Sessão:** `sprint1-codetasks`
> **Modelo:** `opencode-go/minimax-m3`
> **Prompt:** 35 linhas, 5 features request
> **Output:** 47 code tasks, 1568 linhas, 57KB

## Métricas

| Métrica | Valor |
|---------|-------|
| Duração | 567s (9.5 min) |
| Entradas JSONL | 83 |
| Assistent calls | 26 |

### Tokens

| Tipo | Quantidade |
|------|-----------|
| Input | 134.918 |
| Output | 22.130 |
| Cache Read | 1.049.069 |
| **Total** | **1.206.117** |

### Custo

| Componente | Custo |
|------------|-------|
| Input | $0.081 |
| Output | $0.053 |
| Cache Read | $0.126 |
| **Total** | **$0.26** |

## Lições

- 1.2M tokens por $0.26 com MiniMax M3 via OpenCode Go
- Cache Read (1M) dominou o tráfego — cache hit alto reduz custo efetivo
- 9.5 min para 47 tasks → ~12s por task (incluindo raciocínio + escrita)
- `timeout 300` teria matado esta sessão (567s > 300s) — **nunca usar timeout com Pi**
- Background sem timeout é o padrão correto para geração de code tasks

## Extração (comando)

```bash
python3 -c "
import json
p = '/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-taskflow--/2026-06-08T05-55-24-329Z_019ea5cc-d229-740c-9892-7459907456bd.jsonl'
u={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'totalTokens':0}
c={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'total':0}
for l in open(p):
    e=json.loads(l.strip())
    if e.get('type')=='message' and e.get('message',{}).get('role')=='assistant':
        w=e['message'].get('usage',{})
        if w:
            for k in u: u[k]+=w.get(k,0)
            for k in c: c[k]+=w.get('cost',{}).get(k,0)
print(f'Tokens: {u}')
print(f'Custo:  \${c[\"total\"]:.4f}')
"
```
