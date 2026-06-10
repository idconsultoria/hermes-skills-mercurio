# Pi Session Inspection

> Como encontrar, inspecionar e verificar provider/model/custo de sessões do Pi Agent — tanto no setup local (Hermes) quanto no Docker legacy.

## Localização das Sessões (Local)

Pi roda localmente (não Docker). Sessions no diretório do usuário:

```
~/.pi/agent/sessions/--<working-dir-slug>--/<timestamp>_<uuid>.jsonl
```

Onde `<working-dir-slug>` é o path com `/` → `--`:
- `/opt/data/code/workstation/taskflow` → `--opt-data-code-workstation-taskflow--`
- `~/.pi/agent/sessions/` → atalho: `~/.pi/agent/sessions/`

```bash
# Listar últimas sessions de um projeto
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/ | head -5

# Ver entries e tamanho
for f in ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl; do
  echo "$(basename $f): $(wc -l < $f) entries | $(du -h "$f" | cut -f1)"
done
```

## Localização das Sessões (Docker legacy)

Sessões ficam dentro do container Pi no volume Docker `pi-agent-home`:

```bash
docker exec pi_agent ls /home/pi/.pi/agent/sessions/*/*.jsonl
docker exec pi_agent ls -lt /home/pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--/*.jsonl | head -5
```

## Verificar Provider e Model de uma Sessão

Cada sessão JSONL contém um evento `type: "model_change"` nas primeiras linhas com o provider e modelo usados:

```bash
# One-liner: extrair provider + model da sessão mais recente
python3 << 'PYEOF'
import json, glob
sessions = sorted(glob.glob(
    "/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl"
))
for sf in sessions[-3:]:
    with open(sf) as fh:
        for line in fh:
            d = json.loads(line.strip())
            if d.get("type") == "model_change":
                print(f"{sf.split('/')[-1][:40]}: {d['provider']}/{d['modelId']}")
                break
            if d.get("type") == "thinking_level_change":
                break  # fim dos metadados
PYEOF
```

**Saída esperada:**
```
2026-06-08T19-07-41-071Z_019ea8a2...: deepseek/deepseek-v4-pro
2026-06-08T18-50-35-158Z_019ea8a2...: deepseek/deepseek-v4-pro
```

**⚠️ Sempre verificar o provider após lançar um Pi.** O default do `pi` é `google` (built-in), mas sem provider "google" no auth.json, o Pi cai em fallback para `deepseek/deepseek-v4-pro` (caro). Se esperava `opencode/deepseek-v4-flash-free` (gratuito) e vê `deepseek/deepseek-v4-pro`, você esqueceu `--provider`.

### Extrair Custo de uma Sessão

O custo está nos eventos `type: "message"` com `role="assistant"` e `message.usage.cost`:

```bash
python3 << 'PYEOF'
import json
p = "/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/***.jsonl"
u = {"input":0,"output":0,"cacheRead":0,"cacheWrite":0}
c = {"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}
for line in open(p):
    e = json.loads(line.strip())
    if e.get("type") == "message" and e.get("message",{}).get("role") == "assistant":
        w = e["message"].get("usage",{})
        if w:
            for k in u: u[k] += w.get(k,0)
            for k in c: c[k] += w.get("cost",{}).get(k,0)
print(f"Tokens: {u}")
print(f"Custo: ${c['total']:.4f}")
PYEOF
```

## Eventos do JSONL Session

| Tipo | Quando aparece | Info disponível |
|------|---------------|-----------------|
| `session` | Sempre, linha 1 | id, timestamp, cwd |
| `session_info` | Sempre, linha 2 | name (se passou `--name`), parentId |
| `model_change` | Antes da 1a msg | **provider**, **modelId** |
| `message` + `role=user` | Cada turno do usuário | content (prompt) |
| `message` + `role=assistant` | Cada resposta | usage.tokens, usage.cost, stopReason |
| `thinking_level_change` | Config de thinking | level (0=off, 1=on) |

## Verificar stopReason (sessão completou vs travou)

No último evento `type: "message"` com `role="assistant"`:
- `"stop"` → completou normalmente ✅
- `"toolUse"` → aguardando tool result (ainda rodando)
- `"maxTokens"` → estourou limite (incompleto)
- `"endTurn"` → usuário interrompeu

```bash
python3 << 'PYEOF'
import json, glob
f = sorted(glob.glob("/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl"))[-1]
with open(f) as fh:
    for line in fh:
        d = json.loads(line.strip())
        if d.get("type") == "message":
            last = d
    msg = last.get("message",{})
    print(f"Role: {msg.get('role')} | Stop: {msg.get('stopReason')} | Model: {msg.get('model')}")
PYEOF
```

## Abrir Sessão no TUI do Pi

**⚠️ `--session` NÃO aceita partial UUID.** Use o path completo:

```bash
# Local
cd /opt/data/code/workstation/PROJETO
PATH="/opt/data/pi-global/bin:$PATH" pi --session ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/2026-06-08T03-26-43-478Z_019ea544-b316-7e2a-af57-630146f4cbd1.jsonl

# Docker legacy
docker exec -it pi_agent bash
cd /workspace/code/workstation/PROJETO
pi --session /home/pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--/2026-06-08T03-26-43-478Z_019ea544.jsonl
```

Ou use `pi -r` (seletor interativo), mas sessões headless (`pi -p`) **não aparecem** no seletor — só funcionam via path direto.

## Sessões Headless (`pi -p`)

Sessões rodadas com `pi -p` (print mode, não-interativo) são salvas como JSONL normalmente mas NÃO aparecem no seletor `pi -r`. Para acessá-las:
1. Liste os JSONLs por diretório de projeto
2. Use o path completo com `pi --session`
3. Verifique `stopReason: "stop"` no último turno

## Sessões Múltiplas em Paralelo

Quando múltiplos Pi rodam no mesmo diretório, cada um cria seu próprio JSONL no mesmo diretório de sessão. Para identificar qual JSONL pertence a qual processo:

```bash
# Correlacionar PID do processo com session ID
ps aux | grep " pi " | grep -v grep | awk '{print $2}'
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/ | head -5
# A sessão mais recente tende a ser do PID mais jovem
```

Ou usar `--name` ao lançar (ex: `--name "w2-f4-ui"`) — o nome aparece em `session_info.name` na linha 2 do JSONL.

## Exemplo Completo de Verificação

```bash
# 1. Listar sessions recentes
echo "=== Sessions ==="
ls -lt ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/ | head -3

# 2. Extrair provider/model da mais recente
echo "=== Provider/Model ==="
python3 -c "
import json
f = '$(ls -t ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl | head -1)'
with open(f) as fh:
    for line in fh:
        d = json.loads(line.strip())
        if d.get('type') == 'model_change':
            print(f\"{d['provider']}/{d['modelId']}\")
            break
"

# 3. Extrair custo total
echo "=== Custo ==="
python3 -c "
import json
f = '$(ls -t ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl | head -1)'
u={'input':0,'output':0,'cacheRead':0,'cacheWrite':0}
c={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'total':0}
for line in open(f):
    e = json.loads(line.strip())
    if e.get('type')=='message' and e.get('message',{}).get('role')=='assistant':
        w = e['message'].get('usage',{})
        if w:
            for k in u: u[k] += w.get(k,0)
            for k in c: c[k] += w.get('cost',{}).get(k,0)
print(f\"Tokens: {u}\")
print(f\"Custo: \${c['total']:.4f}\")
"

# 4. Último stop reason
echo "=== Stop reason ==="
python3 -c "
import json
f = '$(ls -t ~/.pi/agent/sessions/--opt-data-code-workstation-PROJETO--/*.jsonl | head -1)'
with open(f) as fh:
    for line in fh:
        d = json.loads(line.strip())
        if d.get('type') == 'message':
            last = d
    m = last.get('message',{})
    print(f\"{m.get('stopReason','?')}\")
"
```
