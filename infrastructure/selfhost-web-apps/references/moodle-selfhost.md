# Moodle 5.2 Selfhost on Oracle ARM64

Deployed 2026-07-22 at `https://treinamentos.idconsultoria.ai`.

## Stack

| Container | Image | Port/Net |
|-----------|-------|----------|
| moodle-app | Built (php:8.3-fpm) | 9000 / moodle-net |
| moodle-nginx | nginx:stable | 8082→80 / moodle-net + proxy_network |
| moodle-postgres | postgres:16 | 5432 / moodle-net |
| moodle-redis | redis:7-alpine | 6379 / moodle-net |
| moodle-cron | Built from same Dockerfile | moodle-net |

## Key Config

```php
// config.php — only these proxy settings are needed:
$CFG->wwwroot   = 'https://treinamentos.idconsultoria.ai';
$CFG->sslproxy = true;
// ⚠️ DO NOT set $CFG->reverseproxy = true.
// It causes 'reverseproxyabused' in lib/setuplib.php, killing the
// full Moodle bootstrap needed by image.php, font.php, javascript.php
// and styles.php on first request. sslproxy alone is sufficient.
```

## The `reverseproxy` Trap (ARM64 + Docker + NPM)

**Symptom:** After fresh deploy or cache purge, all asset PHP endpoints return 500:
- `image.php` — login backgrounds, favicons
- `font.php` — Font Awesome `.woff2`/`.ttf`
- `javascript.php` — JS files that need minification
- `styles.php` — CSS when SCSS isn't pre-compiled

**Root cause:** `$CFG->reverseproxy = true` triggers `setup_get_remote_url()` in `lib/setuplib.php` (line ~740). It compares the internal `Host` header against `$CFG->wwwroot`. In Docker+NPM, both are the same domain → Moodle throws `reverseproxyabused`. This aborts the `require setup.php` call that asset scripts use for cache misses.

**Fix:** Remove `reverseproxy`. Keep only `sslproxy=true` + `fastcgi_param HTTPS on` in nginx.

**Why it was hard to find:** The scripts fail silently (`NO_DEBUG_DISPLAY` + `log_errors=Off`), returning a generic Moodle error page with HTTP 500. Individual files that already have cached versions (from prior successful requests) keep working, masking the issue. Browser devtools were essential — they showed `Content-Type: text/html` for assets that should be `text/css` or `font/woff2`.

## Nginx Config

```nginx
server {
    resolver 127.0.0.11 valid=10s;          # Docker DNS re-resolution
    listen 80;
    server_name treinamentos.idconsultoria.ai;
    root /var/www/html/public_web;           # → public/
    index index.php;

    location / {
        try_files $uri $uri/ /r.php;
    }

    location ~ \.php(/|$) {
        include        fastcgi_params;
        fastcgi_param  HTTPS on;              # ← critical for sslproxy
        set $moodle_backend "moodle:9000";   # variable → DNS re-resolve
        fastcgi_pass $moodle_backend;
    }
}
```

## Moodle 5.2 Source Quirks

- Docroot is `public/`. setup.sh creates `public_web → public/` symlink.
- `version.php` is at `public/version.php`; `config.php` lives at the root `/var/www/html/config.php`.
- **setup.sh hot patch:** The `ensure_router_middleware_order()` function looks for the old router.php path. Fix: `sed -i 's/\[ -f "$file" \] || return/[ -f "$file" ] || return 0/' scripts/setup.sh`
- **NPM port 81 is blocked** by Oracle firewall. User needs SSH tunnel: `ssh -L 81:localhost:81 ubuntu@host`.

## Post-Deploy

Only theme CSS pre-compilation is needed:

```bash
docker exec moodle-app php /var/www/html/admin/cli/build_theme_css.php
```

No warm scripts for JS, fonts, or images — those serve correctly on first request with the fixed config.

## Diagnostic Workflow

```bash
# 1. Test from host, bypassing proxy
ssh oracle-host 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/path'

# 2. Verify config doesn't have reverseproxy
ssh oracle-host 'sudo grep "reverseproxy" /home/ubuntu/selfhost/moodle/data/html/config.php'
# Should return NOTHING.

# 3. If debugging asset 500s, enable error display temporarily
ssh oracle-host 'sudo sed -i "/preventexecpath/a\$CFG->debug=32767;\n\$CFG->debugdisplay=true;" config.php'

# 4. Browser devtools: check Content-Type of failing assets
# text/html on styles.php → debug flag leakage or PHP error
# text/css / font/woff2 / application/javascript → correct

# 5. Clean up debug when done
ssh oracle-host 'sudo sed -i "/debug=32767\|debugdisplay=true/d" config.php'
```

## pluginfile.php 404 — Moodle 5.2 URL Format Change

**Symptom:** All `pluginfile.php` URLs return 404, even for core files and properly uploaded theme logos/favicons via the file API.

**Root cause:** Moodle 5.2's `setting_file_url()` in `lib/classes/output/theme_config.php` generates pluginfile URLs differently. Instead of three separate path segments:

```
/logo/0x200/1784696505/logo-id.png     ← expected (size/itemid/filename)
```

It now concatenates `$itemid` and `$filepath` into one segment:

```php
$url = moodle_url::make_file_url(
    "$CFG->wwwroot/pluginfile.php",
    "/$syscontext->id/$component/$filearea/$itemid" . $filepath,
);
// Result: /logo/0x200/1784696505logo-id.png
//                                         ^^^^^^^^ themerev+filename merged
```

The `theme_boost_union_pluginfile()` and `core_admin_pluginfile()` callbacks parse path segments sequentially — they expect 3 elements after the filearea (`size/itemid/filename`), but get only 2 (`size/concatenated`). `clean_param(array_shift($args), PARAM_FILE)` returns `null`, and the file lookup fails.

**Fix — patch `theme_boost_union_pluginfile()` in `theme/boost_union/lib.php`:**

```php
// BEFORE:
$itemid = clean_param(array_shift($args), PARAM_INT);
$filename = clean_param(array_shift($args), PARAM_FILE);

// AFTER:
$itemidraw = array_shift($args);
$itemid = clean_param($itemidraw, PARAM_INT);
// If themerev is baked into filename (no separator), strip leading digits.
$filename = clean_param(
    (array_shift($args) ?: preg_replace("/^[0-9]+/", "", $itemidraw)),
    PARAM_FILE
);
```

The same pattern applies to `core_admin_pluginfile()` in `admin/lib.php` and any theme using `setting_file_url()`.

**Verification:**
```bash
THEMEREV=$(docker exec moodle-postgres psql -U moodle -d moodle -At \
  -c "SELECT value FROM mdl_config WHERE name='themerev';")

curl -s -o /dev/null -w "HTTP %{http_code} Size:%{size_download}\n" \
  "https://treinamentos.idconsultoria.ai/pluginfile.php/1/theme_boost_union/logo/0x200/${THEMEREV}logo-id.png"
# Expected: HTTP 200 Size:24452
```

## Credentials

- Admin: `admin` / `IdConsultoria2026!`
- DB: `moodle` / `moodle_secure_2026`

## Boost Union Theme Installation

Installed 2026-07-22 from the MOODLE_500_STABLE branch:

```bash
# 1. Clone & fix permissions
sudo rm -rf /home/ubuntu/selfhost/moodle/data/html/public/theme/boost_union
sudo git clone --depth 1 --branch MOODLE_500_STABLE \
  https://github.com/moodle-an-hochschulen/moodle-theme_boost_union.git \
  /home/ubuntu/selfhost/moodle/data/html/public/theme/boost_union
sudo chown -R www-data:www-data /home/ubuntu/selfhost/moodle/data/html/public/theme/boost_union

# 2. Detect & install via upgrade CLI
docker exec moodle-app php /var/www/html/admin/cli/upgrade.php --non-interactive
# → "Nenhuma atualização necessária" means it installed

# 3. Activate globally
docker exec moodle-postgres psql -U moodle -d moodle \
  -c "UPDATE mdl_config SET value='boost_union' WHERE name='theme';"

# 4. Purge caches + rebuild CSS
docker exec moodle-app php /var/www/html/admin/cli/purge_caches.php
docker exec moodle-app php /var/www/html/admin/cli/build_theme_css.php
```

**Version checked:** Boost Union v5.0-r31 (plugin version 2025041476), requires Moodle 2025041401. Compatible with 5.2+ despite minor version gap — theming API is stable across minor releases.

## Branding (Logo + Favicon)

**Direct nginx (fallback):**
```bash
sudo cp /tmp/logo-id.png /home/ubuntu/selfhost/moodle/data/html/public/logo-id.png
sudo chown www-data:www-data /home/ubuntu/selfhost/moodle/data/html/public/logo-id.png
# → Accessible at https://treinamentos.idconsultoria.ai/logo-id.png
```

**File API approach (for theme settings):**
```php
$fs = get_file_storage();
$fs->delete_area_files($context->id, "theme_boost_union", "logo");
$fs->create_file_from_pathname([
    "contextid" => $context->id, "component" => "theme_boost_union",
    "filearea" => "logo", "itemid" => 0,
    "filepath" => "/", "filename" => "logo-id.png",
], "/path/to/logo-id.png");
set_config("logo", "logo-id.png", "theme_boost_union");
```

**Brand color:**
```sql
UPDATE mdl_config_plugins SET value='#1a3a5c'
WHERE plugin='theme_boost_union' AND name='brandcolor';
```

## Plugins

### Boost Union ✅
Installed and active. Extensive customization: login layout, course cards, tiles, sliders, footer, info banners, accessibility.

### Edwiser Course Formats ✅ v4.1.21 (compatible)
`format_remuiformat` v4.1.21 supports Moodle 3.4–5.2. Install from GitHub tag, NOT master branch:

```bash
# Download from GitHub release tag (not marketplace, not master)
sudo curl -sL -o /tmp/remuiformat.zip \
  "https://github.com/WisdmLabs/moodle-format_remuiformat/archive/refs/tags/v4.1.21.zip"
sudo unzip -o /tmp/remuiformat.zip -d /tmp/remuiformat_extract/
sudo cp -r /tmp/remuiformat_extract/moodle-format_remuiformat-4.1.21 \
  /home/ubuntu/selfhost/moodle/data/html/public/course/format/remuiformat
sudo chown -R www-data:www-data /home/ubuntu/selfhost/moodle/data/html/public/course/format/remuiformat

# Install via upgrade
docker exec moodle-app php /var/www/html/admin/cli/upgrade.php --non-interactive
```

The DB version (`$plugin->version = 2026042200`) matches disk when installed correctly. Provides 3 layouts: List, Card, and Video (premium add-on).

## Known Issues

- **CLI upgrade script** may timeout on first run after plugin install (SCSS compilation on ARM64). Use `--non-interactive` and let it finish.

## Backups

```bash
docker exec moodle-postgres pg_dump -U moodle moodle > moodle_$(date +%Y%m%d).sql
sudo tar czf moodledata_$(date +%Y%m%d).tar.gz data/moodledata/
```
