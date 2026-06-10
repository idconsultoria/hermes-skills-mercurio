# Nginx Proxy Manager — SQLite Database Schema

NPM stores all configuration in `/data/database.sqlite` inside the container.
The SQLite DB can be manipulated directly (NPM auto-reloads on next read).

## Access

```bash
# Copy DB from container
docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite

# Modify via Python
python3 -c "
import sqlite3, json
conn = sqlite3.connect('/tmp/npm.sqlite')
# ... operations ...
conn.commit()
conn.close()
"

# Copy back to container
docker cp /tmp/npm.sqlite nginx_proxy_manager:/data/database.sqlite
```

## Key Tables

### `proxy_host` — HTTP/HTTPS reverse proxy rules

```sql
CREATE TABLE proxy_host (
  id                INTEGER NOT NULL,
  created_on        datetime NOT NULL,
  modified_on       datetime NOT NULL,
  owner_user_id     INTEGER NOT NULL,
  is_deleted        INTEGER NOT NULL DEFAULT 0,
  domain_names      json NOT NULL,           -- JSON array
  forward_host      varchar(255) NOT NULL,   -- container name or IP
  forward_port      INTEGER NOT NULL,
  access_list_id    INTEGER NOT NULL DEFAULT 0,
  certificate_id    INTEGER NOT NULL DEFAULT 0,
  ssl_forced        INTEGER NOT NULL DEFAULT 0,
  caching_enabled   INTEGER NOT NULL DEFAULT 0,
  block_exploits    INTEGER NOT NULL DEFAULT 0,
  advanced_config   TEXT NOT NULL DEFAULT '',
  meta              json NOT NULL DEFAULT '{}',
  allow_websocket_upgrade INTEGER NOT NULL DEFAULT 1,
  http2_support     INTEGER NOT NULL DEFAULT 0,
  forward_scheme    varchar(255) NOT NULL DEFAULT 'http',
  enabled           INTEGER NOT NULL DEFAULT 1,
  locations         json,
  hsts_enabled      INTEGER NOT NULL DEFAULT 0,
  hsts_subdomains   INTEGER NOT NULL DEFAULT 0,
  trust_forwarded_proto tinyint NOT NULL DEFAULT 0
);
```

**Register:**
```python
c.execute("""INSERT INTO proxy_host (
  id, created_on, modified_on, owner_user_id, is_deleted,
  domain_names, forward_host, forward_port,
  access_list_id, certificate_id, ssl_forced, caching_enabled,
  block_exploits, advanced_config, meta, allow_websocket_upgrade,
  http2_support, forward_scheme, enabled, locations,
  hsts_enabled, hsts_subdomains, trust_forwarded_proto
) VALUES (?, ?, ?, ?, 0,
          ?, ?, ?,
          0, 0, 1, 0,
          0, '', '{}', 1,
          0, 'http', 1, '[]',
          0, 0, 0)""",
  (max_id, now, now, owner_id,
   json.dumps([domain]), forward_host, forward_port))
```

**Unregister (soft delete):**
```python
c.execute("UPDATE proxy_host SET is_deleted=1, modified_on=? WHERE domain_names LIKE ? AND is_deleted=0",
          (now, f"%{domain}%"))
```

### `user` — Admin users

| Column | Type |
|--------|------|
| id | INTEGER PK |
| email | varchar(255) |
| name | varchar(255) |
| nickname | varchar(255) |
| is_disabled | INTEGER |
| is_deleted | INTEGER |

### `auth` — Authentication

| Column | Type |
|--------|------|
| id | INTEGER PK |
| user_id | INTEGER FK |
| type | varchar(30) |
| secret | varchar(255) (bcrypt) |

### `certificate` — SSL certificates

| Column | Type |
|--------|------|
| id | INTEGER PK |
| provider | varchar(255) |
| nice_name | varchar(255) |
| domain_names | json |
| expires_on | datetime |

## Docker Network Requirement

The forwarding target container must be on the same Docker network as NPM.
```bash
docker inspect nginx_proxy_manager --format "{{json .NetworkSettings.Networks}}"
docker inspect <target> --format "{{json .NetworkSettings.Networks}}"
```

## Notes

- Changes to `proxy_host` are picked up by NPM within seconds (no restart)
- Soft delete preferred over hard delete
- Default admin: `SELECT id, email FROM user WHERE is_disabled=0 AND is_deleted=0`
