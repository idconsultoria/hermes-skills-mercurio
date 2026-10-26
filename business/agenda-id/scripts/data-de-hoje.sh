#!/usr/bin/env bash
# Prova a data de HOJE por fontes externas independentes.
# Rode ANTES de agendar qualquer coisa datada (evento, lembrete, marco).
# Uso: bash data-de-hoje.sh [America/Sao_Paulo]
# Regra: host NAO e fonte. O que vale e o consenso entre as fontes externas.
set -uo pipefail

TZ_OWNER="${1:-America/Sao_Paulo}"

echo "host (nao e fonte): $(TZ="$TZ_OWNER" date '+%F %T %Z')  epoch=$(date +%s)"
echo
echo "-- headers Date (CDN/servidor, independentes) --"
for U in https://cloudflare.com https://www.google.com https://www.microsoft.com https://www.nic.br; do
  D=$(curl -sI --max-time 8 "$U" 2>/dev/null | tr -d '\r' \
      | awk 'tolower($1)=="date:"{ $1=""; sub(/^ +/,""); print; exit }')
  [ -n "${D:-}" ] && printf '  %-28s %s\n' "$U" "$D"
done

echo
echo "-- timeapi.io (fonte de hora) --"
curl -s --max-time 10 "https://timeapi.io/api/Time/current/zone?timeZone=${TZ_OWNER}" 2>/dev/null \
  | python3 -c 'import sys,json
"""extrai a data/hora da resposta do timeapi"""
d=json.load(sys.stdin)
print("  %04d-%02d-%02d %02d:%02d (%s)" % (d["year"],d["month"],d["day"],d["hour"],d["minute"],d.get("timeZone","")))' 2>/dev/null \
  || echo "  indisponivel"

echo
echo "Compare as linhas acima. Datas divergentes = dia incerto: NAO agende; repita em alguns minutos."
