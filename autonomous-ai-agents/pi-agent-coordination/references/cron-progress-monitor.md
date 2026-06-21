# Cron-Based Pi Agent Progress Monitor

> Use quando: Pi Agent roda em `terminal(background=true)` por 30+ minutos e o
> agente precisa continuar trabalhando em outras tarefas enquanto monitora.

## Por que cron em vez de tmux?

| Abordagem | Bloqueia o agente? | Visibilidade | Escala |
|-----------|:---:|-------------|--------|
| tmux + loop `sleep 30` | Sim — agente preso no loop | Em tempo real | 1 Pi por vez |
| `process(action='poll')` | Sim — agente precisa lembrar de chamar | Sob demanda | Frágil (esquece fácil) |
| **Cron job** | Não — agente livre | A cada 5 min | Ilimitado |

## Receita

### 1. Lançar o Pi Agent

```bash
terminal(
  command="cd /opt/data/PROJETO && pi -p \"$(cat /tmp/prompt.md)\" --provider opencode-go --model glm-5.2 --name \"projeto-tarefa\"",
  background=true,
  notify_on_complete=true
)
```

### 2. Criar o cron de monitoramento

```python
cronjob(
  action='create',
  schedule='5m',           # checar a cada 5 minutos
  repeat=20,               # parar após 20 checagens (100 min)
  name='check-pi-<nome>',
  enabled_toolsets=['terminal'],
  deliver='origin',        # entrega no mesmo chat
  prompt="""Verifique o progresso do Pi Agent "<nome>" que está rodando em background.

Use este comando para checar:
python3 -c "
import json, glob, os
session_dir = os.path.expanduser('/opt/data/home/.pi/agent/sessions')
files = sorted(glob.glob(os.path.join(session_dir, '**', '*.jsonl'), recursive=True), key=os.path.getmtime, reverse=True)
for f in files[:15]:
    try:
        with open(f) as fh:
            entries = [json.loads(l) for l in fh if l.strip()]
        if not entries: continue
        si = next((e for e in entries if e.get('type')=='session_info'), {})
        if '<nome>' not in si.get('name','').lower(): continue
        tcs = [e for e in entries if e.get('type')=='toolCall']
        reads = sum(1 for t in tcs if t.get('name')=='read')
        writes = sum(1 for t in tcs if t.get('name')=='write')
        bashes = sum(1 for t in tcs if t.get('name')=='bash')
        cats = sum(1 for t in tcs if t.get('name')=='bash' and 'cat >' in str(t.get('arguments','')))
        last = entries[-1]
        last_type = last.get('type','?')
        print(f'ENTRADES={len(entries)} TOOL_CALLS={len(tcs)} READS={reads} WRITES={writes} BASH={bashes} CAT>{cats}')
        print(f'LAST={last_type}')
        break
    except: pass
"

Responda APENAS com este formato conciso (sem introdução, sem despedida):

⏱️ **Progresso Pi Agent** (X min desde o lançamento)
- Entradas: N
- Reads: N | Writes: N | Bash: N (cat >: N)
- Arquivos em <diretório de output>: N
- Última ação: [descrição curta]
- Fase: [LENDO | PLANEJANDO | ESCREVENDO | FINALIZANDO]

Se o Pi Agent já terminou (processo não existe mais), diga "✅ Finalizado" e PARE.
Se o Pi Agent estiver travado (entradas paradas por >5 min vs último check), ALERTE.
"""
)
```

### 3. Cancelar o cron quando Pi terminar

```python
cronjob(action='remove', job_id='<job_id>')
```

## Sinais de que Pi está progredindo (não matar)

- Entradas no JSONL crescendo (>1 nova entrada por minuto em média)
- Tool calls de `read` — está lendo arquivos do projeto
- Tool calls de `bash` com `cat >` — está escrevendo arquivos
- `write` tool calls — está criando arquivos

## Sinais de stall real (intervir)

- Zero entradas novas por >5 minutos
- Última tool call foi `bash` sem `cat >` (comando que não produz output)
- Exit code do processo ≠ null mas arquivo esperado não existe

## Pitfalls

- ⚠️ Não usar `execute_code` para o check — cron jobs podem ter restrições. Use `terminal` com `python3 -c`
- ⚠️ O `deliver='origin'` é essencial — sem ele, o relatório vai para lugar nenhum
- ⚠️ O `repeat` deve ser finito (ex: 20) para não rodar eternamente
- ⚠️ Pi best (modelos grandes) pode levar 5-10 min só lendo antes da primeira escrita — é normal
