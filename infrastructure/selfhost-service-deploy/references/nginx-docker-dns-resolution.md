# Nginx Docker DNS Resolution

## Problem

Nginx containers proxying to other Docker Compose services fail with `connect() failed (111: Connection refused)` after the target container restarts.

**Root cause:** Nginx resolves DNS names in `upstream` blocks and `proxy_pass`/`fastcgi_pass` directives at **startup time only**. When a Docker container restarts, it gets a new IP. Nginx keeps trying the old cached IP.

## Solution: Dynamic DNS with Variable

Use Docker's embedded DNS server (`127.0.0.11`) with a **variable** to force per-request DNS re-resolution:

### Before (broken — DNS cached at startup)

```nginx
upstream moodle_fpm {
    server moodle:9000;
}

server {
    listen 80;
    location ~ \.php(/|$) {
        fastcgi_pass moodle_fpm;   # DNS resolved ONCE at startup
    }
}
```

### After (fixed — per-request DNS resolution)

```nginx
server {
    listen 80;
    resolver 127.0.0.11 valid=10s;   # Docker embedded DNS

    location ~ \.php(/|$) {
        set $backend "moodle:9000";   # Variable forces dynamic resolution
        fastcgi_pass $backend;
    }
}
```

## Why It Works

- `fastcgi_pass $backend;` — nginx treats variables as requiring runtime resolution
- Without the variable: `fastcgi_pass moodle:9000;` — resolved at startup, cached forever
- `resolver 127.0.0.11` — tells nginx to use Docker's embedded DNS, not `/etc/resolv.conf`

The same pattern works for `proxy_pass`:

```nginx
resolver 127.0.0.11 valid=10s;
location / {
    set $upstream "app-container:3000";
    proxy_pass http://$upstream;
}
```

## Verification

```bash
# From inside the nginx container, test connectivity via bash /dev/tcp:
docker exec <nginx-container> bash -c "echo > /dev/tcp/<service>/<port> 2>&1 && echo OK || echo FAIL"

# Check nginx error log for upstream failures:
docker logs <nginx-container> 2>&1 | grep -i "upstream\|Connection refused"
```

## When NOT to Use

Don't use the variable trick for services that are **guaranteed to never restart** (e.g. nginx proxying to a static file server on the same container). In those cases, `fastcgi_pass localhost:9000;` is fine because `localhost` never changes IP.
