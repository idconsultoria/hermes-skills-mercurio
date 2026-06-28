---
name: pi-session-audit
description: "Audit agent sessions — tokens, costs, models from Pi Agent and agy databases

Load this skill to analyze Pi Agent or agy session logs and calculate costs per provider. Extracts real usage metrics from session files, computes costs based on model pricing, and produces audit reports."
category: autonomous-ai-agents
metadata:
  hermes:
    related_skills: [autonomous-ai-agents/pi-agent-coordination]
references:
  - agy-protobuf-parsing.md: Field hierarchy and wire-format parser for agy conversation DBs
type: ToolIntegration
timestamp: 2026-06-28T05:11:55Z
---

# Agent Session Audit (Pi + agy)

> Extrair métricas reais de uso de sessões de agentes — Pi Agent (.jsonl) e agy (protobuf SQLite DBs no host).
> Usuário prefere: uma sessão por linha, colunas com título/sessão, modelo, input cache miss, output, cache hit.
> Dados entregues como CSV anexado via MEDIA: path no Telegram.

## Fontes de Sessão Suportadas

| Ferramenta | Formato | Localização | Tokens extraíveis |
|-----------|---------|------------|:-----------------:|
| **Pi Agent** | JSONL com `usage{input, output, cacheRead, cost}` | `~/.pi/agent/sessions/--*/` | input, output, cache, cost |
| **agy** | Protobuf (SQLite DBs) | host `~/.gemini/antigravity-cli/conversations/*.db` | input, output, cache, thinking, response |
| **Hermes** | SQLite `state.db` | `./state.db` tabela `sessions` | input, output, cache_read, cache_write, reasoning |

Carregar `references/agy-protobuf-parsing.md` para o script de extração e field hierarchy do agy.

## Localização das Sessões (Pi)

```
~/.pi/agent/sessions/--<path-normalizado>--/<timestamp>_<uuid>.jsonl
```

Onde `<path-normalizado>` é o diretório de trabalho com `/` substituído por `-`.
Ex: `--opt-data-code-workstation-taskflow--`

## Formato Padrão de Relatório

Cada sessão vira uma linha nesta tabela:

| Coluna | Origem |
|--------|--------|
| `data` | `header.timestamp[:10]` |
| `projeto` | Nome legível do diretório (usar proj_map) |
| `sessao` | `session_info.name` ou `unnamed` |
| `modelo_provider` | `model_change.provider` |
| `modelo` | `model_change.modelId` |
| `entradas` | `len(entries)` |
| `input_miss` | Soma `usage.input` |
| `output` | Soma `usage.output` |
| `cache_hit` | Soma `usage.cacheRead` |
| `total_tokens` | Soma `usage.totalTokens` |
| `custo_usd` | Soma `usage.cost.total` |

Ordenação: cronológica (data → projeto → sessão).
Sessões com 0 tokens são puladas.

## Script de Extração (Pi Agent)

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
```

## Relatório Multi-sessão Agregado (Pi)

Para auditar **todas as sessões** de uma vez, com agregação por projeto e modelo:

```python
sessions_dir = os.path.expanduser("~/.pi/agent/sessions")
all_files = sorted(glob.glob(os.path.join(sessions_dir, "**", "*.jsonl"), recursive=True))

results = []
for path in all_files:
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try: entries.append(json.loads(line))
                except: pass
    if not entries: continue

    header = entries[0]
    session_info = next((e for e in entries if e.get("type") == "session_info"), {})
    model_change = next((e for e in entries if e.get("type") == "model_change"), {})
    name = (session_info.get("name") or "unnamed")[:60]
    provider = model_change.get("provider", "?")
    model = model_change.get("modelId", "?")
    first_ts = header.get("timestamp", "")

    proj = path.replace(sessions_dir, "").strip("/").split("/")[0]
    proj_clean = proj.replace("--", "").replace("-", " ").strip()
    proj_map = {
        "opt data code workstation taskflow": "Taskflow",
        "opt data pi dotfiles": "Pi Dotfiles",
        "opt data code workstation nexus": "Nexus",
        "opt data code workstation delfos": "Delfos",
        "opt data": "Hermes (raiz)",
    }
    proj_name = proj_map.get(proj_clean, proj_clean)

    usage = {"input": 0, "output": 0, "cacheRead": 0, "totalTokens": 0}
    cost_total = 0.0
    for e in entries:
        if e.get("type") == "message" and e.get("message", {}).get("role") == "assistant":
            u = e["message"].get("usage", {})
            if u:
                for k in usage: usage[k] += u.get(k, 0)
                cost_total += u.get("cost", {}).get("total", 0)

    if usage["totalTokens"] == 0: continue

    results.append({
        "date": first_ts[:10] if first_ts else "?",
        "proj": proj_name,
        "name": name,
        "model": f"{provider}/{model}",
        "in_miss": usage["input"],
        "output": usage["output"],
        "cache_hit": usage["cacheRead"],
        "total": usage["totalTokens"],
        "cost": cost_total,
    })

results.sort(key=lambda r: (r["date"], r["proj"], r["name"]))

# Tabela formatada
current_proj = ""
for r in results:
    if r["proj"] != current_proj:
        current_proj = r["proj"]
        print(f'\n  ═══ {current_proj} ═══')
        print('  DATA     SESSÃO              MODELO          INPUT MISS  OUTPUT  CACHE HIT       TOTAL  C$')
        print('  ' + '─'*95)
    print(f'  {r["date"]}  {r["name"]:42s} {r["model"]:30s} {r["in_miss"]:>10,} {r["output"]:>10,} {r["cache_hit"]:>12,} {r["total"]:>12,}  ${r["cost"]:.2f}')

# Totais
grand_in = sum(r["in_miss"] for r in results)
grand_out = sum(r["output"] for r in results)
grand_cache = sum(r["cache_hit"] for r in results)
grand_cost = sum(r["cost"] for r in results)
print(f'\n  TOTAL {len(results)} sessões')
print(f'  INPUT MISS: {grand_in:>12,}')
print(f'  OUTPUT:     {grand_out:>12,}')
print(f'  CACHE HIT:  {grand_cache:>12,}')
print(f'  TOTAL:      {grand_in+grand_out+grand_cache:>12,}')
print(f'  CUSTO:      ${grand_cost:.4f}')
```

## Agy — Extrair Tokens de DBs Protobuf (Conversas no Oracle Host)

agy armazena conversas em SQLite com BLOBs protobuf em:
```
~/.gemini/antigravity-cli/conversations/*.db
```

### Hierarquia de Campos (reverse-engineered dos schemas)

```
gen_metadata (CortexStepGeneratorMetadata, field 3 do Trajectory)
  └── field 1 -> chat_model (ChatModelMetadata)
       │    ├── field 3 -> model (enum: 2=gemini-2.5-pro, 1020=gemini-3.1-pro, 1016=gemini-3.5-flash)
       └── field 4 -> usage (ModelUsageStats)
            ├── field 2 -> input_tokens (uint64)
            ├── field 3 -> output_tokens (uint64)
            ├── field 4 -> cache_write_tokens (uint64)
            ├── field 5 -> cache_read_tokens (uint64)
            ├── field 9 -> thinking_output_tokens (uint64)
            └── field 10 -> response_output_tokens (uint64)
```

### Schema Discovery

Schemas disponíveis em: `github.com/jkfujinami/antigravity-grpc-schemas`

- `exa/codeium_common_pb/codeium_common.proto` -> `ModelUsageStats {input_tokens=2, output_tokens=3, cache_read_tokens=5}`
- `exa/cortex_pb/cortex.proto` -> `CortexStepGeneratorMetadata`, `ChatModelMetadata`
- `exa/gemini_coder/proto/trajectory.proto` -> `Trajectory`, `Step`

Repo complementar: `github.com/ag-donald/Antigravity-Database-Manager`

### Wire-Format Parser (Python, sem protoc)

```python
def dv(data, offset):
    r = 0; s = 0
    while offset < len(data):
        b = data[offset]; r |= (b & 0x7F) << s; s += 7; offset += 1
        if not (b & 0x80):
            if r > 0x7FFFFFFFFFFFFFFF: r -= 0x10000000000000000
            return r, offset
    return None, offset

def parse_agy_usage(blob):
    si = so = scr = scw = sthink = sresp = 0
    model_id = 0
    i = 0
    while i < len(blob):
        if i >= len(blob): break
        key = blob[i]; fn = key >> 3; wt = key & 0x07; i += 1
        if wt == 2 and fn == 1:  # chat_model sub-message
            length, i2 = dv(blob, i)
            if not length or i2 + length > len(blob): break
            cm = blob[i2:i2+length]; i = i2 + length
            j = 0
            while j < len(cm):
                ck = cm[j]; cf = ck >> 3; cw = ck & 0x07; j += 1
                if cw == 0:
                    cv, j = dv(cm, j)
                    if cv is None: break
                    if cf == 3 and 0 < cv < 10000: model_id = cv
                elif cw == 2 and cf == 4:  # usage -> ModelUsageStats
                    ulen, ustart = dv(cm, j)
                    if not ulen or ustart + ulen > len(cm): break
                    ud = cm[ustart:ustart+ulen]; j = ustart + ulen
                    k = 0
                    while k < len(ud):
                        uk = ud[k]; uf = uk >> 3; uw = uk & 0x07; k += 1
                        if uw == 0:
                            uv, k = dv(ud, k)
                            if uv is None: break
                            if uv < 0 or uv > 100_000_000: continue
                            if uf == 2: si += uv
                            elif uf == 3: so += uv
                            elif uf == 4: scw += uv
                            elif uf == 5: scr += uv
                            elif uf == 9: sthink += uv
                            elif uf == 10: sresp += uv
                        elif uw == 2:
                            sl, sk = dv(ud, k)
                            if sl and sk + sl <= len(ud): k = sk + sl
                            else: break
                        elif uw == 5: k += 4
                        elif uw == 1: k += 8
        elif wt == 2:  # skip other sub-messages
            length, i2 = dv(blob, i)
            if length and i2 + length <= len(blob): i = i2 + length
    return si, so, scr, scw, sthink, sresp, model_id
```

### Extração Multi-sessão

```python
import sqlite3, glob, os, datetime
HOME = os.path.expanduser("~")
DBS = sorted(glob.glob(os.path.join(HOME, ".gemini/antigravity-cli/conversations/*.db")))

MODEL_MAP = {1: "gemini-2.0-flash", 2: "gemini-2.5-pro",
             1016: "gemini-3.5-flash", 1020: "gemini-3.1-pro"}

for dbpath in DBS:
    db_id = os.path.basename(dbpath)[:12]
    mtime = os.path.getmtime(dbpath)
    date_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    cur.execute("SELECT idx, data, size FROM gen_metadata ORDER BY idx")
    rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM steps")
    steps = cur.fetchone()[0]
    conn.close()
    si = so = scr = scw = sthink = sresp = 0
    model_id = 0
    for idx, blob, sz in rows:
        if blob and len(blob) > 20:
            r = parse_agy_usage(blob)
            si += r[0]; so += r[1]; scr += r[2]; scw += r[3]
            sthink += r[4]; sresp += r[5]
            if r[6] and not model_id: model_id = r[6]
    model_name = MODEL_MAP.get(model_id, f"model_{model_id}")
    print(f"{db_id},{date_str},{model_name},{si},{so},{scr},{scw},{sthink},{sresp},{steps},{len(rows)}")
```

### ⚠️ Pitfalls do agy

- Valores uint64 com high bit set são int64 negativos — converter: `if v > 0x7FFFFFFFFFFFFFFF: v -= 0x10000000000000000`
- `gen_metadata` com apenas 1-2 entries = sessões curtas (header ~1KB + resposta ~300KB)
- Model ID (field 3 em ChatModelMetadata) pode vir 0 em sessões antigas ou sem modelo explícito
- DBs não contêm título da sessão — extrair do `step_payload` usando a heurística em `references/agy-protobuf-parsing.md`
- Para nomes, extrair strings de `executor_metadata` BLOBs ou logs em `~/.gemini/antigravity-cli/log/`
- agy roda no Oracle host — SSH via `ssh oracle-host 'python3 script.py'`
- **⚠️ Model naming pitfall:** Enums de modelo > 1000 (1016, 1020) são IDs internos.
  NUNCA chutar o nome. Confirmar com `ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && agy models'`

## Exportação CSV (comum a ambas as fontes)

Usuário prefere receber dados como CSV para abrir em planilhas.
Cada ferramenta gera um CSV separado; consolidar manualmente se necessário.

### Estrutura de colunas por ferramenta

| Ferramenta | Colunas | Observação |
|-----------|---------|------------|
| **Pi Agent** | data, projeto, sessao, provider, modelo, entries, input_miss, output, cache_hit, total_tokens, custo_usd | JSONL com `usage.cost` |
| **Hermes** | data, sessão, modelo, input_miss, output, cache_hit, cache_write, reasoning, api_calls, tool_calls, msgs | SQLite `sessions` table |
| **agy** | session_id, title (prompt extraído), date, model, input, output, cache_read, cache_write, thinking, response, steps, gen_entries | Protobuf via wire-format |

### Exportação genérica (Pi + agy)

```python
import csv, sys

writer = csv.writer(sys.stdout)
writer.writerow(["data","projeto","sessao","modelo_provider","modelo",
                 "entradas","duracao_min","input_miss","output",
                 "cache_hit","total_tokens","custo_usd"])

for r in results:  # results = saída de qualquer script de agregação
    prov, mod = r["model"].split("/", 1) if "/" in r["model"] else (r["model"], "")
    writer.writerow([
        r["date"], r["proj"], r["name"], prov, mod,
        "", "", r["in_miss"], r["output"],
        r["cache_hit"], r["total"], f'{r["cost"]:.2f}'
    ])
```

Salva e entrega:
```bash
python3 script.py > /opt/data/agent-sessions.csv
# Na resposta: MEDIA:/opt/data/agent-sessions.csv
```

## Formato do JSONL (v3 — Pi Agent)

### SessionHeader (1ª linha)
```json
{"type":"session","version":3,"id":"uuid","timestamp":"2026-06-08T05:55:24.329Z","cwd":"..."}
```

### SessionInfo (2ª linha, se nomeada)
```json
{"type":"session_info","id":"...","name":"sprint1-codetasks"}
```

### ModelChange
```json
{"type":"model_change","provider":"opencode-go","modelId":"minimax-m3"}
```

### AssistantMessage (contém USAGE)
```json
{"type":"message","message":{"role":"assistant","usage":{
  "input":134918,"output":22130,"cacheRead":1049069,"cacheWrite":0,"totalTokens":1206117,
  "cost":{"input":0.080951,"output":0.053112,"cacheRead":0.125888,"cacheWrite":0,"total":0.259951}},
  "provider":"opencode-go","model":"minimax-m3"}}
```

## ⚠️ Tool_Use Analysis — Pi JSONL nunca tem tool_use

Pi **nunca** usa o tool `write_file` no JSONL. Em vez disso, escreve arquivos executando `cat >` heredocs dentro de chamadas `bash`:

```json
{"type":"toolCall","name":"bash","arguments":{"command":"cat > product/engineering/api-contracts.yaml << 'EOF'\\n..."}}
```

**Não use tool_use count para medir produtividade de sessões Pi.** Use bash + cat > count ou git diff.

## Como encontrar o session file correto (Pi)

```bash
# Ordenar por tamanho (maior = mais trabalho)
ls -lS ~/.pi/agent/sessions/--opt-data-code-workstation-taskflow--/*.jsonl | head -5

# Buscar por nome
for f in ~/.pi/agent/sessions/--*/<prefixo>*.jsonl; do
    name=$(head -2 "$f" | python3 -c "
import sys, json
for l in sys.stdin:
    try:
        e=json.loads(l.strip())
        if e.get('type')=='session_info':
            print(e.get('name','unnamed')); break
    except: pass
")
    if [ "$name" = "NOME_DA_SESSAO" ]; then echo "FOUND: $f"; wc -l "$f"; fi
done
```

## Progress Classification (Pi)

Para determinar se Pi está progredindo ou travado:

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
                    if '--- a/' in txt[:20]: label = 'LENDO git diff'
                    elif 'def ' in txt[:50] or 'class ' in txt[:50]: label = 'LENDO codigo'
                    elif 'cat >' in txt[:50]: label = 'ESCREVENDO arquivo'
                    elif 'git commit' in txt.lower(): label = 'COMMIT'
                    elif 'gh pr' in txt.lower(): label = 'CRIANDO PR'
                    else: label = f'? {txt[:80]}'
                    print(f'  [{abs_i}] {label}')
    last_text = ''
    for c in recent[-1]['message']['content']:
        if isinstance(c, dict): last_text = str(c.get('text','') or c.get('content','') or '')
    if 'Permission denied' in last_text or '429' in last_text:
        print('TRAVADO — intervir necessario')
    elif 'gh pr' in last_text.lower(): print('PR finalizando')
    elif 'git commit' in last_text.lower() or 'git add' in last_text.lower(): print('Commitando')
    else: print('Aguardando — progresso normal')
```

| Ultimo toolResult | Pi esta... | Decisao |
|---|---|---|
| `diff --git` / `--- a/` | Lendo git diffs | Aguardar |
| `def ` / `class ` / `@router.` | Lendo codigo | Aguardar |
| `cat >` / `write_file` | **Escrevendo** | Aguardar |
| `git commit` / `git add` | Commitando | Quase la |
| Erro 429 / Permission denied | **Travou** | Intervir |

## Indicadores de Sessao Produtiva (Pi)

| Metrica | Produtiva | So pensou |
|---------|-----------|-----------|
| Entradas | >50 | <20 |
| Custo | >$0.05 | <$0.01 |
| git diff | sim | nao |
| Ultima entrada | toolResult com codigo | assistant vazio |
