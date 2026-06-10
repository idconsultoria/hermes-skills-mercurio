# Nginx Proxy Manager — SQLite Schema (proxy_host table)

NPM stores proxy host configurations in `/data/database.sqlite` inside its container.
The `proxy_host` table is the source of truth — nginx config files are generated from it.

Alembic migration-style reference. Columns in insertion order.

## proxy_host table

```sql
CREATE TABLE proxy_host (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    created_on            TEXT NOT NULL,         -- ISO timestamp
    modified_on           TEXT NOT NULL,         -- ISO timestamp
    owner_user_id         INTEGER NOT NULL,      -- references user.id (1 = admin)
    is_deleted            INTEGER NOT NULL DEFAULT 0,

    domain_names          TEXT NOT NULL,          -- JSON array: ["example.com"]
    forward_host          TEXT NOT NULL,          -- container name or IP
    forward_port          INTEGER NOT NULL DEFAULT 80,

    access_list_id        INTEGER,                -- 0 = no restriction
    certificate_id        INTEGER,                -- 0 = no SSL cert
    ssl_forced            INTEGER NOT NULL DEFAULT 0,  -- 1 = redirect HTTP->HTTPS
    caching_enabled       INTEGER NOT NULL DEFAULT 0,
    block_exploits        INTEGER NOT NULL DEFAULT 0,
    advanced_config       TEXT NOT NULL DEFAULT '',
    meta                  TEXT NOT NULL DEFAULT '{}',
    allow_websocket_upgrade INTEGER NOT NULL DEFAULT 0,
    http2_support         INTEGER NOT NULL DEFAULT 0,
    forward_scheme        TEXT NOT NULL DEFAULT 'http',
    enabled               INTEGER NOT NULL DEFAULT 1,
    locations             TEXT NOT NULL DEFAULT '[]',  -- JSON array of custom locations

    hsts_enabled          INTEGER NOT NULL DEFAULT 0,
    hsts_subdomains       INTEGER NOT NULL DEFAULT 0,
    trust_forwarded_proto INTEGER NOT NULL DEFAULT 0
);
```

## Critical column values for preview hosts

| Column | Value for HTTP preview | Value for HTTPS (production) |
|--------|----------------------|------------------------------|
| `ssl_forced` | `0` | `1` |
| `certificate_id` | `0` (no cert) | Let's Encrypt cert ID |
| `forward_scheme` | `'http'` | `'http'` (NPM handles SSL) |
| `enabled` | `1` | `1` |
| `allow_websocket_upgrade` | `0` | `1` (if needed) |

## Finding existing proxy hosts

```sql
-- List all active hosts
SELECT id, domain_names, forward_host, forward_port, ssl_forced, certificate_id
FROM proxy_host
WHERE is_deleted = 0
ORDER BY id;

-- Find by domain
SELECT id FROM proxy_host
WHERE domain_names LIKE '%example.com%' AND is_deleted = 0;

-- Soft-delete (NPM convention, not hard DELETE)
UPDATE proxy_host
SET is_deleted = 1, modified_on = datetime('now')
WHERE domain_names LIKE '%example.com%';
```

## File structure on disk

NPM writes nginx configs to:
```
/data/nginx/proxy_host/1.conf     ← for proxy_host.id = 1
/data/nginx/proxy_host/2.conf     ← for proxy_host.id = 2
```

Each `.conf` is generated from the DB row + NPM's internal templates.
When editing the DB directly (not through NPM's API), you MUST write
the `.conf` file manually and reload nginx.
