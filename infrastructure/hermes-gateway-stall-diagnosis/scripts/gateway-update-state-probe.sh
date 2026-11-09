#!/usr/bin/env bash
# gateway-update-state-probe.sh — foto DETERMINÍSTICA (sem carimbo de tempo) do estado de um
# gateway Hermes cujo ambiente foi isolado pelo pm, mais a obrigação pendente do update.
#
# Serve como fonte de um cron em modo monitor: saída idêntica entre ticks suprime o agente,
# saída diferente o acorda com o diff. NÃO acrescente data/hora nem ordenação aleatória.
#
# Uso: bash gateway-update-state-probe.sh [HERMES_HOME]     (default: $HOME/.hermes)
export HOME="${HOME:-/data/data/com.termux/files/home}"
H="${1:-$HOME/.hermes}"
LOG="$H/logs/gateway.log"

FACTS=$(ls -1 "$H"/installs/*/facts.json 2>/dev/null | head -1)
if [ -n "$FACTS" ]; then
  SEL_VENV=$(python3 -c "import json;print(json.load(open('$FACTS'))['packages']['venv']['environment'])" 2>/dev/null)
  echo "sel_env=$(basename "$(dirname "$SEL_VENV")" 2>/dev/null | cut -c1-8)"
  MARKER="$(dirname "$FACTS")/source-completion-pending"
  ATT="$(dirname "$FACTS")/source-completion-attempts"
  [ -f "$MARKER" ] && echo "pending=yes" || echo "pending=no"
  echo "attempts=$(cat "$ATT" 2>/dev/null || echo 0)"
else
  SEL_VENV=""; echo "sel_env=none"; echo "pending=unknown"; echo "attempts=0"
fi

# gateway vivo, em qual interpretador, e com quantas libs do venv legado mapeadas
GW=$(ps -ef 2>/dev/null | grep -a 'gateway run' | grep -v grep | grep -av 'bash -c' | awk '{print $2}' | head -1)
if [ -z "$GW" ]; then
  echo "gateway=down"; echo "gateway_python=none"; echo "venv_legado_mapeado=0"
else
  echo "gateway=up"
  echo "gateway_python=$(readlink -f /proc/$GW/exe 2>/dev/null | grep -oE 'python3\.[0-9]+' | head -1)"
  echo "venv_legado_mapeado=$(grep -c 'hermes-agent/venv' /proc/$GW/maps 2>/dev/null || true)"
fi

# falhas de ABI do boot atual (janela desde a última linha de boot — o log guarda as antigas)
LAST=$(grep -an 'Starting Hermes Gateway' "$LOG" 2>/dev/null | tail -1 | cut -d: -f1)
if [ -n "$LAST" ]; then
  echo "abi_failures_boot=$(tail -n +"$LAST" "$LOG" | grep -ac 'did not return an extension module')"
else
  echo "abi_failures_boot=$(grep -ac 'did not return an extension module' "$LOG" 2>/dev/null || true)"
fi

# catálogos i18n alcançáveis pelo ambiente selecionado (chaves cruas = missing)
if [ -n "$SEL_VENV" ] && [ -x "$SEL_VENV/bin/python" ]; then
  echo "i18n_catalog=$("$SEL_VENV/bin/python" -c "import agent.i18n as i; print('ok' if i._locales_dir().is_dir() else 'missing')" 2>/dev/null || echo erro)"
else
  echo "i18n_catalog=unknown"
fi
