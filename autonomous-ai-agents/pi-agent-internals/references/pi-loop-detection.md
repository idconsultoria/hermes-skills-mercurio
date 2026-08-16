# Pi Loop Detection — Entradas Crescendo ≠ Progresso

> Caso real: Zera (ex-CFP IA) Onda 5 · Q08, 14/08/2026. Pi cost repetiu o mesmo comando de
> load test (`timeout 100 ... load_test_api.py`) por ~45 min em loop. Cada execução travava
> no mesmo deadlock de subprocesso; o Pi relançava o comando indefinidamente. O JSONL crescia
> (150+ entries) — mas zero progresso.

## Sinal de loop

- Últimos toolCalls **idênticos** (mesmo comando bash, mesmo resultado de falha: `exit=124`,
  mesmo traceback).
- Entradas crescem normalmente (cada tentativa = nova entrada) → o teste "entries crescendo =
  progresso" passa, mas nada avança.
- Durou minutos sem que a sessão mudasse de fase (fica sempre na mesma toolCall).

## Detecção — comparar os últimos toolCalls

```python
import json, glob, os
sessions_dir = os.path.expanduser("~/.pi/agent/sessions")
candidates = sorted(glob.glob(os.path.join(sessions_dir, "*cfp-ia*", "*.jsonl")), key=os.path.getmtime, reverse=True)
target = None
for f in candidates:
    name = ""
    try:
        with open(f) as fh:
            for line in fh:
                try: e = json.loads(line)
                except: continue
                if e.get("type") == "session_info":
                    name = e.get("name",""); break
    except: continue
    if name == "NOME_DO_JOB":   # o --name usado na invocação
        target = f; break
if not target:
    print("não achei a sessão"); raise SystemExit(1)
entries = [json.loads(l) for l in open(target) if l.strip()]
calls = []
for e in entries:
    if e.get('type') == 'message':
        m = e['message']
        if m.get('role') == 'assistant':
            for c in m.get('content', []):
                if isinstance(c, dict) and c.get('type') == 'toolCall':
                    calls.append((e.get('timestamp','')[11:19], c.get('name'), str(c.get('arguments',''))[:80]))
        elif m.get('role') == 'toolResult':
            for c in m.get('content', []):
                if isinstance(c, dict) and c.get('type') == 'text':
                    calls.append((e.get('timestamp','')[11:19], 'RESULT', c.get('text','')[:100]))
print(f"{len(entries)} entries | {len(calls)} eventos")
for ts, name, args in calls[-6:]:
    print(f"[{ts}] {name} | {args}")
```

**Loop:** os últimos 3-6 `bash` têm comandos idênticos (ou quase) com `exit=124`/mesmo erro.
**Stall real (não loop):** entradas PARADAS >120s (nada novo no JSONL).

## Ação do orquestrador (Hermes)

1. **Matar o processo específico** — NUNCA `pkill -f "pi$"` (mata tudo, incluindo jobs paralelos).
   ```bash
   ps aux | grep -E "pi --name.*NOME_DO_JOB" | grep -v grep
   kill <PID>
   ```
2. **Diagnosticar o bloqueio você mesmo** — ler o script que o Pi escreveu e achar o bug real
   (o Pi não vai se desvencilhar sozinho; vai relançar o mesmo comando para sempre).
3. **Corrigir** (mudança mecânica 🟢) — commit + push.
4. **Relançar** com `--session <arquivo> -p "<continuação curta>"` para reaproveitar o contexto.

## Causas de loop vistas na prática (Python subprocesso)

| Padrão | Sintoma | Fix |
|---|---|---|
| `proc.stdout.read()` em subprocesso VIVO | Bloqueia para sempre (pipe nunca fecha) → deadlock → timeout do wrapper → Pi relança | `readline()` best-effort + `proc.terminate()` + `proc.wait(timeout=5)` (com `kill()` no TimeoutExpired) |
| Flag de "sincronização" atribuída mas nunca lida | ex.: `base_url_explicito = (...) ` setada na linha 408 e nunca usada → healthcheck mira porta errada → travamento silencioso | Procurar flags atribuídas e não lidas ao revisar script do Pi |
| SQLite single-writer + load test concorrente | >1 VU: setup (~9 escritas/VU) serializa no lock → httpx timeout estoura → VUs travam | Load test real exige PostgreSQL; SQLite efêmera só serve smoke de 1 VU (não é bug do produto) |

## Regra geral

"Entradas crescendo" é condição NECESSÁRIA mas NÃO SUFICIENTE para progresso. Sempre comparar
os últimos toolCalls antes de decidir "está progredindo, deixa rodar". Loop é mais caro que
stall: 45 min queimados sem diagnóstico.
