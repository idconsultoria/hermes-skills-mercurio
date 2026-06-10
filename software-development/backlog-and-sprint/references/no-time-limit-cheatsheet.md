# No Time Limit — Cheatsheet de Agentes

> Comandos prontos para Pi background + agy tmux + session monitoring + polling.
> Copie e cole ajustando PROJETO e modelo.

## Pi: Disparar em background

```bash
PROJETO="taskflow"
mkdir -p /opt/data/code/workstation/$PROJETO/prompts

# Escrever prompt
cat > /opt/data/code/workstation/$PROJETO/prompts/pi-job.md << 'PROMPT'
Seu prompt aqui...
PROMPT

# Copiar pro host e disparar
scp /opt/data/code/workstation/$PROJETO/prompts/pi-job.md \
  oracle-host:/home/ubuntu/selfhost/shared/code/workstation/$PROJETO/prompts/pi-job.md

ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
LC_DIR=code/workstation/PROJETO \
  nohup pi-agent 'pi --name "job-name" \
  -p "$(cat prompts/pi-job.md)" \
  --provider opencode-go --model minimax-m3' \
  > /tmp/pi-job.log 2>&1 &
ENDSCRIPT
```

## Pi: Continuar sessão existente

```bash
ssh oracle-host 'bash -s' << 'ENDSCRIPT'
cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO
LC_DIR=code/workstation/PROJETO \
  nohup pi-agent 'pi -c -p "Continue: ..." --provider opencode-go --model minimax-m3' \
  > /tmp/pi-job.log 2>&1 &
ENDSCRIPT
```

## Pi: Monitorar session files

```bash
ssh oracle-host '
  SESS=$(ls -dt ~pi/.pi/agent/sessions/--workspace-code-workstation-PROJETO--* 2>/dev/null | head -1)
  if [ -n "$SESS" ]; then
    echo "Session: $SESS"
    wc -l "$SESS"/*.jsonl 2>/dev/null
    echo "Último turno:"
    tail -1 "$SESS"/*.jsonl 2>/dev/null | python3 -m json.tool 2>/dev/null | tail -5
  else
    echo "Aguardando sessão..."
  fi
'
```

## Agy: tmux review completa

```bash
ssh oracle-host 'tmux kill-session -t agy-job 2>/dev/null; true'
ssh oracle-host 'tmux new-session -d -s agy-job \
  "HOME=/home/ubuntu /home/ubuntu/.local/bin/agy"'
sleep 8
ssh oracle-host 'tmux send-keys -t agy-job \
  "Review at /path/ — Write feedback in /path/feedbacks.md" Enter'

# Polling
for i in $(seq 1 20); do
  sleep 60
  ssh oracle-host 'tmux capture-pane -t agy-job -p -S -10' 2>/dev/null
  if ssh oracle-host "grep -q 'APROVADO\|ACORDO' /path/feedbacks.md" 2>/dev/null; then
    echo "✅ agy concluiu!"
    break
  fi
done
ssh oracle-host 'tmux kill-session -t agy-job 2>/dev/null; true'
```

## Agy: Revisão rápida (foreground)

```bash
ssh oracle-host 'cd /home/ubuntu/selfhost/shared/code/workstation/PROJETO && \
  timeout 300 /home/ubuntu/.local/bin/agy -p "Quick review: ..."'
```

## Polling genérico (PHASE_COMPLETE)

```bash
for i in $(seq 1 40); do
  sleep 30
  ssh oracle-host '
    SESS=$(ls -dt ~pi/.pi/agent/sessions/--workspace-* 2>/dev/null | head -1)
    [ -n "$SESS" ] && echo "Turnos: $(wc -l < "$SESS"/*.jsonl 2>/dev/null || echo 0)"
  ' 2>/dev/null
  if grep -q "PHASE_COMPLETE" /opt/data/code/workstation/PROJETO/product/target/file.md 2>/dev/null; then
    echo "✅ Completo!"; break
  fi
  echo "  ($((i * 30))s)"
done
```
