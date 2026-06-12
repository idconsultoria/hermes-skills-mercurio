---
name: pi-session-audit
description: "Audit Pi Agent sessions — duration, tokens, costs, and model from JSONL files.

Load this skill to analyze Pi Agent session logs and calculate costs per provider. Extracts real usage metrics from session JSONL files, computes costs based on model pricing, and produces audit reports for tracking agent usage and spending."

Load this skill to analyze Pi Agent session logs and calculate costs per provider. Extracts real usage metrics from session JSONL files, computes costs based on model pricing, and produces audit reports for tracking agent usage and spending."
category: autonomous-ai-agents
metadata:
  hermes:
    related_skills: [autonomous-ai-agents/pi-agent-coordination]
---

# Pi Agent Session Audit

> Extrair métricas reais de uso das sessões do Pi Agent a partir dos arquivos .jsonl

## Localização das Sessões

```
~/.pi/agent/sessions/--<path-normalizado>--/<timestamp>_<uuid>.jsonl
```

Onde `<path-normalizado>` é o diretório de trabalho com `/` substituído por `-`.
Ex: `--opt-data-code-workstation-taskflow--`

## Formato do JSONL (v3)

Cada linha é um JSON. Tipos relevantes:

### SessionHeader (1ª linha)
```json
{"type":"session","version":3,"id":"uuid","timestamp":"2026-06-08T05:55:24.329Z","cwd":"..."}
```

### SessionInfo (2ª linha, se nomeada)
```json
{"type":"session_info","id":"...","parentId":null,"timestamp":"...","name":"sprint1-codetasks"}
```

### ModelChange
```json
{"type":"model_change","id":"...","parentId":"...","timestamp":"...","provider":"opencode-go","modelId":"minimax-m3"}
```

### AssistantMessage (contém USAGE)
```json
{
  "type":"message","id":"...","parentId":"...","timestamp":"...",
  "message":{
    "role":"assistant","content":[...],
    "usage":{"input":134918,"output":22130,"cacheRead":1049069,"cacheWrite":0,"totalTokens":1206117,
      "cost":{"input":0.080951,"output":0.053112,"cacheRead":0.125888,"cacheWrite":0,"total":0.259951}},
    "provider":"opencode-go","model":"minimax-m3","timestamp":1748858124
  }
}
```

## Script de Extração

```python
import json, os, glob
from datetime import datetime

def audit_session(session_path: str) -> dict:
    entries = []
    with open(session_path) as f:
        for line in f:
            line = line.strip()
            if line: entries.append(json.loads(line))

    if not entries: return {"error": "empty session"}
    header = entries[0]
    session_info = next((e for e in entries if e.get("type") == "session_info"), {})
    model_change = next((e for e in entries if e.get("type") == "model_change"), {})
    first_ts = header.get("timestamp", "")
    last_ts = entries[-1].get("timestamp", first_ts)

    total_usage = {"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"totalTokens":0}
    total_cost = {"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}
    assistant_count = 0

    for e in entries:
        if e.get("type")=="message" and e.get("message",{}).get("role")=="assistant":
            usage = e["message"].get("usage",{})
            if usage:
                assistant_count += 1
                for k in total_usage: total_usage[k] += usage.get(k,0)
                cost = usage.get("cost",{})
                for k in total_cost: total_cost[k] += cost.get(k,0)

    t1 = datetime.fromisoformat(first_ts.replace("Z","+00:00"))
    t2 = datetime.fromisoformat(last_ts.replace("Z","+00:00"))
    duration_s = (t2 - t1).total_seconds()

    return {
        "name": session_info.get("name","unnamed"),
        "provider": model_change.get("provider","unknown"),
        "model": model_change.get("modelId","unknown"),
        "cwd": header.get("cwd",""),
        "entries": len(entries),
        "assistant_calls": assistant_count,
        "duration_s": duration_s,
        "duration_min": round(duration_s/60, 1),
        "usage": total_usage,
        "cost": total_cost,
    }

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv)>1 else None
    if target:
        r = audit_session(target)
        print(f"Sessão: {r.get('name','unnamed')}")
        print(f"Modelo: {r.get('provider','?')}/{r.get('model','?')}")
        print(f"Duração: {r.get('duration_min',0)} min")
        print(f"Tokens: {r['usage']['totalTokens']:,}")
        print(f"Custo: ${r['cost']['total']:.4f}")
```

## ⚠️ Tool_Use Analysis — Pi JSONL NUNCA tem tool_use, mas TEM bash com cat

**TODAS as sessões do Pi auditadas mostram 0 tool_use calls** — mesmo as
produtivas que escreveram código. O Pi não expõe tool_use no formato Hermes porque delega a
execução para um subprocesso interno que não é logado no JSONL.

### 🔑 Pi escreve via `bash` + `cat >`, não via `write_file`

Pi **nunca** usa o tool `write_file` no JSONL. Em vez disso, escreve arquivos
executando `cat >` heredocs dentro de chamadas `bash`:

```json
{"type":"toolCall","name":"bash","arguments":{"command":"cat > product/engineering/api-contracts.yaml << 'EOF'\n..."}}
```

Para detectar escritas reais na sessão:

```python
# Extrair paths escritos via bash heredocs
import json, re

entries = [json.loads(l) for l in open('SESSION.jsonl') if l.strip()]
write_paths = set()

for e in entries:
    if e.get('type')=='message' and e.get('message',{}).get('role')=='assistant':
        for c in e['message'].get('content',[]):
            if isinstance(c, dict) and c.get('type') == 'toolCall':
                name = c.get('name','')
                args = str(c.get('arguments',''))
                if name == 'bash' and 'cat >' in args:
                    paths = re.findall(r"cat > ([^ \n<|&;]+)", args)
                    write_paths.update(paths)

print(f"Arquivos escritos via heredoc: {len(write_paths)}")
for p in sorted(write_paths)[:20]:
    print(f"  {p}")
```

**Não use tool_use count para medir produtividade de sessões Pi.** Use
`bash` + `cat >` count ou git diff como métrica.

**TODAS as sessões do Pi auditadas mostram 0 tool_use calls** — mesmo as
produtivas que escreveram código. O Pi não expõe tool_use no formato Hermes porque delega a
execução para um subprocesso interno que não é logado no JSONL.

**Não use tool_use count para medir produtividade de sessões Pi.** A métrica
só funciona para Claude Code, não para Pi.

### Como encontrar o session file correto

Pi salva sessions como `~/.pi/agent/sessions/--<path-normalizado>--/<timestamp>_<uuid>.jsonl`.
Para achar a sessão certa quando há múltiplas com o mesmo nome:

```bash
# Buscar por nome da sessão (--name usado na invocação)
for f in ~/.pi/agent/sessions/--*/<prefixo>*.jsonl; do
    name=$(head -2 "$f" | python3 -c "
import sys, json
for l in sys.stdin:
    try:
        e=json.loads(l.strip())
        if e.get('type')=='session_info':
            print(e.get('name','unnamed'))
            break
    except: pass
")
    if [ "$name" = "NOME_DA_SESSAO" ]; then
        echo "FOUND: $f"
        wc -l "$f"
    fi
done

# Ou: ordenar por tamanho (maior = mais trabalho feito)
ls -lS ~/.pi/agent/sessions/--opt-data-code-workstation-taskflow--/*.jsonl | head -5
```

### Como determinar onde o Pi parou (últimas entradas)

Útil quando Pi foi morto por timeout ou crash. Lê o que Pi estava fazendo
no momento em que parou:

```bash
python3 -c "
import json
path = 'SESSION.jsonl'
entries = []
with open(path) as f:
    for l in f:
        l=l.strip()
        if l: entries.append(json.loads(l))

print(f'Total entries: {len(entries)}')

# Últimas 5 entradas
for i in range(max(0,len(entries)-5), len(entries)):
    e = entries[i]
    t = e.get('type','?')
    if t == 'message':
        m = e.get('message',{})
        role = m.get('role','?')
        content = m.get('content',[])
        snippet = ''
        if content and isinstance(content,list):
            first = content[0]
            if isinstance(first, dict):
                ct = first.get('type','?')
                if ct in ('text','tool_result'):
                    txt = str(first.get('text','') or first.get('content',''))
                    snippet = txt[:150].replace(chr(10),' ')
                else:
                    snippet = f'type={ct}'
        print(f'[{i:3d}] {role:12s} | {snippet}')
    else:
        print(f'[{i:3d}] type={t}')
"

# Interpretação:
# toolResult com "diff --git" = Pi estava lendo changes
# toolResult com "def " / "class " = Pi estava lendo código
# assistant type=thinking = Pi raciocinando (não travado)
# toolResult como última entry + SIGTERM = Pi morto antes de processar
```

**Indicadores de sessão produtiva vs rumorosa (corrigido para Pi):**
| Métrica | Produtiva | Rumoroza (só pensou) |
|---------|-----------|---------------------|
| Entradas totais | >50 | <20 |
| Custo total | >$0.05 | <$0.01 |
| Arquivos modificados (git diff) | sim | não |
| Última entrada | toolResult com código lido | assistant sem conteúdo |

## Progress Classification — O Que Pi Está Fazendo Agora

Para determinar se Pi está progredindo ou travado, classifique o conteúdo
das últimas toolResults:

| Último toolResult contém | Pi está... | Decisão |
|--------------------------|------------|---------|
| `diff --git` ou `--- a/` | Lendo git diffs (fase inicial) | ✅ Aguardar |
| `def `, `class `, `@router.` | Lendo código fonte | ✅ Aguardar |
| `cat >`, `write_file` | **Escrevendo arquivos** | ✅ Aguardar conclusão |
| `git commit`, `git add` | Preparando commits | ✅ Quase lá |
| `gh pr create`, `pull request` | Criando PR | ✅ Última fase |
| Erro 429, Permission denied | **Travou** | ❌ Intervir |
| Vazio (assistant thinking) | Raciocinando | ✅ Aguardar (pode levar 30-60s) |

### Script de classificação automática

```python
import json

def classify_progress(session_path: str, tail: int = 5):
    entries = [json.loads(l) for l in open(session_path) if l.strip()]
    recent = entries[-tail:]
    
    for i, e in enumerate(recent):
        abs_i = len(entries) - tail + i
        if e.get('type') == 'message':
            role = e['message'].get('role', '?')
            for c in e['message'].get('content', []):
                if isinstance(c, dict):
                    txt = str(c.get('text','') or c.get('content','') or '')
                    if '--- a/' in txt[:20]:
                        label = '📖 LENDO git diff'
                    elif 'def ' in txt[:50] or 'class ' in txt[:50]:
                        label = '📖 LENDO código'
                    elif 'cat >' in txt[:50]:
                        label = '✍️ ESCREVENDO arquivo'
                    elif 'git commit' in txt.lower():
                        label = '📦 COMMIT'
                    elif 'gh pr' in txt.lower():
                        label = '🔄 CRIANDO PR'
                    else:
                        label = f'❓ {txt[:80]}'
                    print(f'  [{abs_i}] {label}')
    
    # Decision
    last_text = ''
    for c in recent[-1]['message']['content']:
        if isinstance(c, dict):
            last_text = str(c.get('text','') or c.get('content','') or '')
    
    if 'Permission denied' in last_text or '429' in last_text:
        print('\n🔴 TRAVADO — intervir necessário')
    elif 'gh pr' in last_text.lower():
        print('\n✅ PR finalizando')
    elif 'git commit' in last_text.lower() or 'git add' in last_text.lower():
        print('\n📦 Commitando — quase lá')
    else:
        print('\n🟢 Aguardando — progresso normal')

# Uso
# classify_progress('sessao.jsonl')
```

## One-liner Rápido

```bash
python3 -c "
import json
p = '/opt/data/home/.pi/agent/sessions/--opt-data-code-workstation-taskflow--/***.jsonl'
u={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'totalTokens':0}
c={'input':0,'output':0,'cacheRead':0,'cacheWrite':0,'total':0}
for l in open(p):
    e=json.loads(l.strip())
    if e.get('type')=='message' and e.get('message',{}).get('role')=='assistant':
        w=e['message'].get('usage',{})
        if w:
            for k in u: u[k]+=w.get(k,0)
            for k in c: c[k]+=w.get('cost',{}).get(k,0)
print(f'Tokens: {u}\nCusto: \${c[\"total\"]:.4f}')
"
```
