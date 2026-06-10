# Nginx Proxy Manager — Proxy Host Setup

> Setup de proxy host no NPM sem acessar a UI (porta 81).
> Validado em: 07 Jun 2026 (TaskFlow deploy)

## Quando usar

- NPM já está rodando na porta 80/443
- Não tem acesso à UI (senha desconhecida, sem browser)
- App Docker em container na rede `proxy_network`

## Pré-requisitos

- Container do app conectado à rede `proxy_network` (externa, criada pelo NPM)
- Acesso SSH ao servidor
- `sudo` para escrever no banco SQLite do NPM (owned by root)

## Passo a passo

### 1. Conectar o container à proxy_network

No `docker-compose.yml` do app:

```yaml
nginx:
  # ...
  networks:
    - app-net
    - proxy_network    # <-- adicionar

networks:
  app-net:
    driver: bridge
  proxy_network:       # <-- declarar como externa
    external: true
```

```bash
docker compose up -d nginx --force-recreate
```

### 2. Verificar conectividade

```bash
# NPM consegue resolver o nome do container?
docker exec nginx_proxy_manager ping taskflow-nginx -c 1
# Se não tiver ping, testar via curl interno:
docker exec nginx_proxy_manager curl -s -o /dev/null -w "%{http_code}" http://taskflow-nginx:80/
# Esperado: 200
```

### 3. Inserir proxy host no SQLite

```bash
ssh oracle-host "sudo python3 << 'PYEOF'
import sqlite3, json
from datetime import datetime, timezone

DB = '/home/ubuntu/selfhost/nginx-proxy-manager/data/database.sqlite'
now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

conn = sqlite3.connect(DB)

domains = json.dumps(['<IP-DO-SERVER>'])
container = '<NOME-DO-CONTAINER-NGINX>'

conn.execute('''INSERT INTO proxy_host (
    created_on, modified_on, owner_user_id, is_deleted,
    domain_names, forward_host, forward_port,
    access_list_id, certificate_id, ssl_forced,
    caching_enabled, block_exploits, advanced_config,
    meta, allow_websocket_upgrade, http2_support,
    forward_scheme, enabled, locations,
    hsts_enabled, hsts_subdomains, trust_forwarded_proto
) VALUES (?, ?, 1, 0, ?, ?, 80,
          0, 0, 0,
          0, 1, '',
          '{}', 1, 0,
          'http', 1, '[]',
          0, 0, 1)''',
    (now, now, domains, container))

pid = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
print(f'Proxy host created: ID={pid}')
conn.commit()
conn.close()
PYEOF"
```

### 4. Escrever o nginx config

O NPM gera nginx configs em `/data/nginx/proxy_host/`. O formato esperado usa **variáveis NPM-internas** — não copiar template nginx comum.

```bash
ssh oracle-host 'sudo tee /home/ubuntu/selfhost/nginx-proxy-manager/data/nginx/proxy_host/1.conf << "CONFEOF"
server {
    set $forward_scheme http;
    set $server         "<NOME-DO-CONTAINER>";
    set $port           80;

    listen 80;
    listen [::]:80;

    server_name <IP-DO-SERVER>;

    access_log /data/logs/proxy-host-1_access.log proxy;
    error_log /data/logs/proxy-host-1_error.log warn;

    location / {
        include conf.d/include/proxy.conf;
        proxy_http_version 1.1;
        proxy_buffering off;
    }

    include /data/nginx/custom/server_proxy[.]conf;
}
CONFEOF'
```

> **CRÍTICO:** Usar `include conf.d/include/proxy.conf;` em vez de definir os headers manualmente. O `proxy.conf` do NPM tem os cabeçalhos corretos (X-Forwarded-Proto, X-Real-IP, etc.). Não incluir `$connection_upgrade` — o NPM não define essa variável e o nginx test falha.

### 5. Recarregar nginx

```bash
docker exec nginx_proxy_manager nginx -t && \
docker exec nginx_proxy_manager nginx -s reload
```

### 6. Testar

```bash
# Com Host header correspondente ao server_name:
curl -s -H "Host: <IP-DO-SERVER>" http://localhost:80/ | head -3
# Deve mostrar o app (ex: <title>TaskFlow</title>)

# Sem Host header (cai no default):
curl -s http://localhost:80/ | head -3
# Deve mostrar "Default Site" (fallback do NPM)
```

Do navegador: `http://<IP-DO-SERVER>/` — o browser envia `Host: <IP>` automaticamente.

## Para adicionar SSL (Let's Encrypt)

Via UI do NPM (porta 81):
1. Acessar `http://<IP>:81`
2. Ir em **SSL Certificates > Add SSL Certificate > Let's Encrypt**
3. Adicionar o domain e aguardar (~30s)
4. Editar o proxy host e ativar SSL

## Estrutura do banco NPM

Tabela `proxy_host`:
- `domain_names`: JSON array de domínios/IPs (ex: `["129.146.163.107"]`)
- `forward_host`: nome do container Docker (ex: `taskflow-nginx`)
- `forward_port`: porta interna (ex: `80`)
- `forward_scheme`: `http` ou `https`
- `ssl_forced`: `0` (sem SSL) ou `1` (redireciona HTTP→HTTPS)
- `enabled`: `1` (ativo) ou `0` (inativo)

## Troubleshooting

| Sintoma | Causa | Fix |
|---------|-------|-----|
| "Default Site" no browser | server_name não corresponde ao Host header | Verificar se o dominio/IP no config corresponde ao que o browser envia |
| nginx -t falha: "unknown variable" | Template copiado de nginx comum (usa `$connection_upgrade`) | Usar `include conf.d/include/proxy.conf` |
| 502 Bad Gateway | Container de destino não está na proxy_network | `docker compose up -d nginx --force-recreate` com `proxy_network` adicionada |
| Config file não é lido | Arquivo em `/data/nginx/proxy_host/*.conf` mas não incluído | Verificar `include /data/nginx/proxy_host/*.conf;` no nginx.conf do NPM |
