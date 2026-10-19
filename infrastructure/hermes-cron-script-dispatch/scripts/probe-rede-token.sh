#!/usr/bin/env bash
# Probe de saúde de rede + token OAuth para jobs de cron que tocam o Google.
# Responde: "o cron que coleta falhou por CREDENCIAL ou por DNS transitório?"
#
# Somente leitura: nao grava nada, nao renova token em disco, nao toca planilha.
# Uso: probe-rede-token.sh [token.json] [N]
set -uo pipefail

TOKEN="${1:-$HERMES_HOME/google_token.json}"
N="${2:-5}"
[[ -z "$TOKEN" || "$TOKEN" != /* ]] && TOKEN="${HERMES_HOME:-/data/data/com.termux/files/home/capitolium}/google_token.json"

echo "=== 1. Quem resolve o DNS ==="
grep -v '^\s*#' /etc/resolv.conf | grep . || echo "resolv.conf vazio"
NS=$(grep -oE 'nameserver [0-9.]+' /etc/resolv.conf | head -1 | awk '{print $2}')
if [[ -n "$NS" ]]; then
  /data/data/com.termux/files/home/capitolium/work/idata/.venv/bin/python - "$NS" <<'PY' 2>/dev/null \
    || echo "  (python nao disponivel para classificar o resolver)"
import ipaddress, sys
try:
    a = ipaddress.ip_address(sys.argv[1])
    print(f"  {a} -> {'MagicDNS/Tailscale (CGNAT 100.64.0.0/10)' if a in ipaddress.ip_network('100.64.0.0/10') else 'resolver comum'}")
except Exception as e:
    print("  nao classificavel:", e)
PY
fi

echo
echo "=== 2. Token em disco: existe e esta expirado? (forense do disparo falho) ==="
PY=""
for p in "$HERMES_HOME/work/idata/.venv/bin/python" /data/data/com.termux/files/home/capitolium/work/idata/.venv/bin/python \
         /data/data/com.termux/files/home/capitolium/work/idata/.venv/bin/python /data/data/com.termux/files/home/capitolium/id-nfse-motor/.venv/bin/python python3; do
  [[ -x "$p" ]] && "$p" -c "import googleapiclient, google.oauth2" >/dev/null 2>&1 && { PY="$p"; break; }
done
[[ -z "$PY" ]] && { echo "  ERRO: nenhum python com googleapiclient encontrado."; exit 5; }
echo "  python: $PY"
[[ -f "$TOKEN" ]] || { echo "  ERRO: token ausente: $TOKEN"; exit 4; }
"$PY" - "$TOKEN" <<'PY'
import json, sys, datetime
d = json.load(open(sys.argv[1]))
exp = d.get("expiry")
print("  token_uri:", d.get("token_uri"))
print("  expiry   :", exp)
if exp:
    try:
        e = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
        agora = datetime.datetime.now(datetime.timezone.utc)
        print("  agora    :", agora.isoformat(), "-> EXPIRADO ha", agora - e if e < agora else "ainda valido")
    except Exception as ex:
        print("  (expiry ilegivel:", ex, ")")
print("  refresh_token presente:", bool(d.get("refresh_token")))
PY

echo
echo "=== 3. N=$N resolucoes + N=$N refreshs (rede viva ou nao) ==="
"$PY" - "$TOKEN" "$N" <<'PY'
import json, socket, sys, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
path, n = sys.argv[1], int(sys.argv[2])
info = json.load(open(path))
scopes = info.get("scopes") or []
f1 = f2 = 0
for i in range(n):
    try:
        socket.getaddrinfo("oauth2.googleapis.com", 443, socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:
        f1 += 1; print(f"  dns[{i}] FALHOU {type(e).__name__}: {e}")
    try:
        c = Credentials.from_authorized_user_info(info, scopes)
        c.refresh(Request())
        print(f"  refresh[{i}] OK expira {c.expiry}")
    except Exception as e:
        f2 += 1; print(f"  refresh[{i}] FALHOU {type(e).__name__}: {e}")
    time.sleep(1)
print(f"\n  RESUMO: dns {n-f1}/{n} ok | refresh {n-f2}/{n} ok")
if f1 == 0 and f2 == 0:
    print("  VEREDITO: rede e credencial sadias -> a falha no cron foi TRANSITORIA (falta retry no script).")
elif f2 == n:
    print("  VEREDITO: credencial quebrada (refresh falha sempre) -> re-auth necessario.")
else:
    print("  VEREDITO: instabilidade de rede -> o cron precisa de retry com backoff.")
PY
