# NPM Proxy Host — Direct SQLite Insert Recipe

Complete working recipe for adding a proxy host to Nginx Proxy Manager via direct database manipulation. Use when NPM UI (port 81) is inaccessible (Oracle Cloud blocks non-80/443 ports).

## Quick Recipe

```bash
# 1. Export DB
ssh oracle-host 'docker cp nginx_proxy_manager:/data/database.sqlite /tmp/npm.sqlite'

# 2. Insert proxy host
python3 << 'PYEOF'
import sqlite3, json
from datetime import datetime, timezone

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
c = sqlite3.connect("/tmp/npm.sqlite").cursor()

# Check if already exists
c.execute("SELECT id, domain_names FROM proxy_host WHERE domain_names LIKE ?", ("%YOUR_DOMAIN%",))
if c.fetchall():
    print("Already exists — update instead of insert")
else:
    c.execute("""INSERT INTO proxy_host 
        (created_on, modified_on, owner_user_id, domain_names, forward_host, forward_port, 
         forward_scheme, ssl_forced, enabled, http2_support, certificate_id, caching_enabled, 
         allow_websocket_upgrade, access_list_id, advanced_config, locations, block_exploits, 
         hsts_enabled, hsts_subdomains, meta, trust_forwarded_proto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (now, now, 1, json.dumps(["YOUR_DOMAIN"]), "CONTAINER_NAME", 80, "http",
         0, 1, 0, 0, 0, 0, 0, "", json.dumps([]), 1, 0, 0, json.dumps({}), 0))
    c.connection.commit()
    print(f"✅ Created (id={c.lastrowid})")

c.close()
PYEOF

# 3. Import DB back
ssh oracle-host 'docker cp /tmp/npm.sqlite nginx_proxy_manager:/data/database.sqlite'
```

## Full Column Reference

All 21 columns needed for a valid INSERT (NOT NULL constrained):

| Column | Value | Notes |
|--------|-------|-------|
| `created_on` | `now` | UTC timestamp |
| `modified_on` | `now` | UTC timestamp |
| `owner_user_id` | `1` | Admin user ID from `user` table |
| `domain_names` | `json.dumps(["domain.com"])` | JSON array |
| `forward_host` | `"container-name"` | Docker DNS name |
| `forward_port` | `80` | Internal container port |
| `forward_scheme` | `"http"` | Always http (NPM→container is HTTP) |
| `ssl_forced` | `0` initially | Set to 1 after cert is added |
| `enabled` | `1` | Active |
| `http2_support` | `0` initially | Set to 1 after cert is added |
| `certificate_id` | `0` initially | **CRITICAL**: set to actual cert ID after Let's Encrypt |
| `caching_enabled` | `0` | |
| `allow_websocket_upgrade` | `0` | Set to 1 for websocket apps |
| `access_list_id` | `0` | No access restriction |
| `advanced_config` | `""` | Custom nginx directives |
| `locations` | `json.dumps([])` | JSON array |
| `block_exploits` | `1` | Enable exploit blocking |
| `hsts_enabled` | `0` initially | Set to 1 after cert |
| `hsts_subdomains` | `0` | |
| `meta` | `json.dumps({})` | JSON object |
| `trust_forwarded_proto` | `0` | Not needed for most apps |

## SSL Workflow

1. Insert proxy host with `certificate_id=0`, `ssl_forced=0`, `http2_support=0`
2. User accesses NPM UI (via SSH tunnel: `ssh -L 81:localhost:81 ubuntu@<IP>`) → `http://localhost:81`
3. SSL Certificates → Add Let's Encrypt → fill domain + email → Save
4. Note the certificate ID from `certificate` table
5. Update proxy host: `UPDATE proxy_host SET certificate_id=<ID>, ssl_forced=1, http2_support=1, hsts_enabled=1 WHERE id=<ID>`

## Common Pitfalls

- **`certificate_id=1` breaks new domains** — ID 1 is usually the first cert (e.g., praxis.gotdns.ch). Set to 0 for new domains until their own cert is generated.
- **`owner_user_id` is NOT NULL** — must be set. Check `SELECT id FROM user WHERE is_deleted=0 AND is_disabled=0` for valid user IDs.
- **Changes auto-reload** — NPM picks up proxy_host changes within seconds. No restart needed.
- **DB is locked during NPM operations** — copy/restore operations are atomic (cp) but NPM may write between copy and restore. Do it quickly.

## Delete Proxy Host (soft)

```python
c.execute("UPDATE proxy_host SET is_deleted=1, modified_on=? WHERE id=?", (now, proxy_id))
```
