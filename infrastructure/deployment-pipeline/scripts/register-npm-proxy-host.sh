#!/bin/bash
# register-npm-proxy-host.sh — Register an ephemeral proxy host in Nginx Proxy Manager
# Usage: PR_NUMBER=42 DOMAIN_SUFFIX=praxis.example.com bash register-npm-proxy-host.sh
set -euo pipefail

PR_NUMBER="${PR_NUMBER:-}"
DOMAIN_SUFFIX="${DOMAIN_SUFFIX:-praxis.129.146.163.107.sslip.io}"  # change per infra

if [ -z "$PR_NUMBER" ]; then
  echo "USO: PR_NUMBER=42 $0"
  exit 1
fi

DOMAIN="${PR_NUMBER}.${DOMAIN_SUFFIX}"
BACKEND_HOST="taskflow-backend-${PR_NUMBER}"
FRONTEND_HOST="taskflow-frontend-${PR_NUMBER}"
BACKEND_PORT=8000
FRONTEND_PORT=5173
OWNER_USER_ID=1

echo "[npm] Registering ${DOMAIN} -> backend:${BACKEND_HOST}:${BACKEND_PORT}, frontend:${FRONTEND_HOST}:${FRONTEND_PORT}"

# Step 1: Register in NPM SQLite database
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm-register.sqlite

OUTPUT=$(python3 -c "
import sqlite3, json
from datetime import datetime, timezone

conn = sqlite3.connect('/tmp/npm-register.sqlite')
c = conn.cursor()

domain = '${DOMAIN}'
existing = c.execute('SELECT id FROM proxy_host WHERE domain_names LIKE ? AND is_deleted=0',
    (f'%{domain}%',)).fetchone()

if existing:
    print(f'Already exists: ID {existing[0]}')
    conn.close()
    exit(0)

max_id = c.execute('SELECT COALESCE(MAX(id), 0) + 1 FROM proxy_host').fetchone()[0]
now = datetime.now(timezone.utc).isoformat()

c.execute('''INSERT INTO proxy_host
    (id, created_on, modified_on, owner_user_id, is_deleted,
     domain_names, forward_host, forward_port,
     access_list_id, certificate_id, ssl_forced, caching_enabled,
     block_exploits, advanced_config, meta, allow_websocket_upgrade,
     http2_support, forward_scheme, enabled, locations,
     hsts_enabled, hsts_subdomains, trust_forwarded_proto)
    VALUES (?, ?, ?, ?, 0,
            ?, ?, ?,
            0, 0, 0, 0,
            0, '', '{}', 0,
            0, 'http', 1, '[]',
            0, 0, 0)''',
    (max_id, now, now, ${OWNER_USER_ID},
     json.dumps([domain]), '${BACKEND_HOST}', ${BACKEND_PORT}))

conn.commit()
conn.close()
print(f'Proxy host #{max_id}')
")

echo "${OUTPUT}"
PROXY_ID=$(echo "${OUTPUT}" | grep -oP '(?<=#)\d+')

docker cp /tmp/npm-register.sqlite nginx_proxy_manager:/data/database.sqlite

# Step 2: Write nginx config
CONF="/tmp/npm-proxy-${PR_NUMBER}.conf"
cat > "$CONF" << NGINX_EOF
# ${DOMAIN} (Preview PR #${PR_NUMBER})
server {
  set \$forward_scheme http;
  set \$server         "${FRONTEND_HOST}";
  set \$port           ${FRONTEND_PORT};

  listen 80;
  listen [::]:80;

  server_name ${DOMAIN};
  http2 on;
  include conf.d/include/block-exploits.conf;

  access_log /data/logs/proxy-host-${PROXY_ID}_access.log proxy;
  error_log /data/logs/proxy-host-${PROXY_ID}_error.log warn;

  location /api/ {
    proxy_pass http://${BACKEND_HOST}:8000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
  }
  location /health {
    proxy_pass http://${BACKEND_HOST}:8000;
    proxy_set_header Host \$host;
  }
  location /auth/ {
    proxy_pass http://${BACKEND_HOST}:8000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
  }
  location / {
    include conf.d/include/proxy.conf;
  }
  include /data/nginx/custom/server_proxy[.]conf;
}
NGINX_EOF

docker cp "$CONF" nginx_proxy_manager:/data/nginx/proxy_host/${PROXY_ID}.conf
docker exec nginx_proxy_manager nginx -t && docker exec nginx_proxy_manager nginx -s reload

echo "[npm] OK — http://${DOMAIN}"
