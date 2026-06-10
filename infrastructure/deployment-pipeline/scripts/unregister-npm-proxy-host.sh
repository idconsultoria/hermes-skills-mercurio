#!/bin/bash
# unregister-npm-proxy-host.sh — Remove an ephemeral proxy host from NPM
# Usage: PR_NUMBER=42 DOMAIN_SUFFIX=praxis.example.com bash unregister-npm-proxy-host.sh
set -euo pipefail

PR_NUMBER="${PR_NUMBER:-}"
DOMAIN_SUFFIX="${DOMAIN_SUFFIX:-praxis.129.146.163.107.sslip.io}"

if [ -z "$PR_NUMBER" ]; then
  echo "USO: PR_NUMBER=42 $0"
  exit 1
fi

DOMAIN="${PR_NUMBER}.${DOMAIN_SUFFIX}"
echo "[npm] Removing ${DOMAIN}"

# Step 1: Find proxy host ID and mark as deleted
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm-unregister.sqlite

PROXY_ID=$(python3 -c "
import sqlite3
conn = sqlite3.connect('/tmp/npm-unregister.sqlite')
c = conn.cursor()
row = c.execute(\"SELECT id FROM proxy_host WHERE domain_names LIKE ? AND is_deleted=0\",
    (f'%${DOMAIN}%',)).fetchone()
conn.close()
if row: print(row[0])
")

python3 -c "
import sqlite3
conn = sqlite3.connect('/tmp/npm-unregister.sqlite')
c = conn.cursor()
c.execute(\"UPDATE proxy_host SET is_deleted=1, modified_on=datetime('now') WHERE domain_names LIKE ? AND is_deleted=0\",
    (f'%${DOMAIN}%',))
deleted = c.rowcount
conn.commit()
conn.close()
print(f'[npm] Removed {deleted} records for ${DOMAIN}')
"

docker cp /tmp/npm-unregister.sqlite nginx_proxy_manager:/data/database.sqlite

# Step 2: Remove nginx config file
if [ -n "$PROXY_ID" ]; then
  echo "[npm] Removing nginx config proxy_host/${PROXY_ID}.conf"
  docker exec nginx_proxy_manager rm -f "/data/nginx/proxy_host/${PROXY_ID}.conf" 2>/dev/null || true
  docker exec nginx_proxy_manager nginx -t && docker exec nginx_proxy_manager nginx -s reload || true
fi

echo "[npm] OK"
