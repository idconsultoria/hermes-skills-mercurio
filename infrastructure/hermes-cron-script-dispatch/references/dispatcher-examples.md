# Dispatcher examples — Hermes cron resilientes

## dispatcher (vai em ~/.hermes/scripts/<nome>.sh)
```bash
#!/usr/bin/env bash
set -euo pipefail
HH="${HERMES_HOME:-/opt/mercurio-data}"
[[ ! -d "$HH" ]] && HH=/opt/data
TARGET="$HH/scripts/<nome>.sh"
[[ ! -f "$TARGET" ]] && { echo "ERRO: $TARGET ausente"; exit 4; }
exec "$TARGET" "$@"
```

## wrapper real (vai em $HERMES_HOME/scripts/<nome>.sh) — varre múltiplos homes/venv/backend
```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${HERMES_HOME:-}" && -d "$HERMES_HOME" ]]; then HH="$HERMES_HOME"
elif [[ -d /opt/mercurio-data ]]; then HH=/opt/mercurio-data
elif [[ -d /opt/data ]]; then HH=/opt/data
else echo "ERRO: HERMES_HOME indisponível."; exit 3; fi
export HERMES_HOME="$HH"

BACKENDS=("$HH/work/idata/entrypoint_ingestão_inter.py" "/opt/data/work/idata/entrypoint_ingestão_inter.py")
PYTHONS=("$HH/venvs/google/bin/python" "/opt/data/venvs/google/bin/python" "python3")
PY=""; for p in "${PYTHONS[@]}"; do command -v "$p" >/dev/null 2>&1 || [[ -x "$p" ]] && { PY="$p"; break; }; done
SCRIPT=""; for s in "${BACKENDS[@]}"; do [[ -f "$s" ]] && { SCRIPT="$s"; break; }; done
if [[ -z "$SCRIPT" ]]; then echo "ERRO: backend não encontrado em ${BACKENDS[*]}"; exit 4; fi
if [[ -z "$PY" ]]; then echo "ERRO: venv Python não encontrado."; exit 5; fi
exec "$PY" "$SCRIPT" "$@"
```

## watchdog no_agent (mudo vs grito)
```bash
OUT="$(bash "$RUNNER" "$@" 2>&1)"; RC=$?
if [[ $RC -eq 0 && -z "$OUT" ]]; then exit 0; fi
echo "$OUT"; exit $RC
```
