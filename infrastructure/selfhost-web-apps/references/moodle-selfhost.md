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
UPDATE mdl_config_plugins SET value='#005465'
WHERE plugin='theme_boost_union' AND name='brandcolor';
```

### ⚠️ Brand CSS Gap (2026-07-29)

After initial deploy, **only** `brandcolor` and logo/favicon were set. The Boost Union CSS customization fields are all empty:

| Setting | Value |
|---------|-------|
| `scss` / `scsspre` / `scsspost` | ❌ Empty |
| `linkcolor` | ❌ Empty |
| `buttonbrandcolor` | ❌ Empty |
| `loginbackgroundimage` | ❌ Empty |
| `customfonts` | ❌ Empty |

This means the login page is the Bootstrap 5 default — white background, floating elements, no brand personality.

#### Brand Extraction Workflow

Before writing Moodle CSS, extract the brand's design tokens from its source repo:

```bash
# Clone the brand's site repo
gh repo clone <org>/<site-repo> /tmp/brand-check -- --depth 1

# Read design tokens
cat /tmp/brand-check/tailwind.config.js    # colors, fonts, shadows
cat /tmp/brand-check/src/constants.ts       # theme object
cat /tmp/brand-check/index.html             # Google Fonts URLs
```

> See `references/id-consultoria-brand-tokens.md` for the full ID Consultoria design system and Moodle Boost Union mapping table.

#### ⚠️ SCSS Pipeline Pitfall (Moodle 5.2 + Boost Union 5.0)

**The `scsspre`, `scss`, and `scsspost` DB fields do NOT compile into the theme CSS.** Setting them and running `build_theme_css.php` produces zero output — the rules never appear in `styles.php`. Verified 2026-07-29:

```bash
# Inject test SCSS → rebuild → grep the compiled CSS → 0 matches
docker exec moodle-postgres psql ... -c "UPDATE ... SET value='body{border:5px solid red}' WHERE name='scsspre';"
docker exec moodle-app php /var/www/html/admin/cli/build_theme_css.php
curl -s https://.../theme/styles.php/boost_union/<rev>_<subrev>/all | grep "5px solid red"
# → no output (not compiled)
```

**Root cause:** In Moodle 5.2, `theme_boost_get_pre_scss()` only processes `brandcolor` → `$primary`. `theme_boost_get_main_scss_content()` only processes presets. Boost Union's `get_external_scss()` only reads from URL/GitHub sources. None of the SCSS callback chain reads `scss`/`scsspre`/`scsspost` from the DB. The `admin_setting_scsscode` type is defined in settings.php but orphaned at compile time.

> This was working in Moodle 4.x. The pipeline regression appears specific to the 5.2 + Boost Union 5.0 combination.

#### ✅ Workaround: `additionalhtmlhead` (Core Setting)

The Moodle core `additionalhtmlhead` setting is injected into `<head>` on every page and does NOT depend on the SCSS compiler:

```bash
# 1. Write CSS to a file on the host (avoids SSH quoting hell)
cat > /tmp/moodle-custom.css << 'CSSEOF'
<style>
#page-login-index {
  background: linear-gradient(135deg, #005465 0%, #050a0f 100%) !important;
  min-height: 100vh !important;
}
/* ... more rules ... */
</style>
CSSEOF

# 2. Inject via Python (handles single-quote escaping reliably)
ssh oracle-host "python3 << 'PYEOF'
with open('/tmp/moodle-custom.css') as f:
    css = f.read()
escaped = css.replace(\"'\", \"''\")
import subprocess
subprocess.run(
    ['docker','exec','-i','moodle-postgres','psql','-U','moodle','-d','moodle'],
    input=f\"UPDATE mdl_config SET value = '{escaped}' WHERE name = 'additionalhtmlhead';\",
    text=True)
PYEOF"

# 3. Purge caches (REQUIRED — additionalhtmlhead is cached in MUC)
docker exec moodle-app php /var/www/html/admin/cli/purge_caches.php

# 4. Verify injection
curl -s https://treinamentos.idconsultoria.ai/login/index.php | grep -c "linear-gradient"
# → 2 (CSS is in the HTML output)
```

#### CSS Injection — Lessons from the Login Page Polish

Three iterations were needed to get the dark-themed login card rendering correctly:

1. **Flexbox centering beats fixed margins.** Initial `margin: 60px auto` on `#region-main` caused the card to be cut off at the bottom of the viewport. Fix: `display: flex; flex-direction: column; align-items: center; justify-content: center` on `body#page-login-index` and all wrapper divs.

2. **Scope ALL wrapper divs for transparent backgrounds.** Bootstrap `.container-fluid`, `#page-wrapper`, `#page`, `#page-content`, `#region-main-box`, `[role="main"]`, `.loginform`, `#theme_boost_union-loginform`, `#login-method-local` — all need `background: transparent !important` or white bleeds through the dark theme.

3. **Placeholder contrast needs `0.5+` alpha on dark inputs.** `rgba(255,255,255,0.3)` was too faint on dark semi-transparent fields; `0.5–0.6` is the sweet spot for readability without looking harsh.

#### Pitfall: `visually-hidden` Override Required for Login Heading

Moodle's login page heading (`h1.login-heading`) carries Bootstrap's `.visually-hidden` class by default. Even with correct `color` and `font-family` rules, the heading stays invisible unless you explicitly override the hiding styles:

```css
#page-login-index h1.login-heading.visually-hidden {
    position: static !important;
    width: auto !important;
    height: auto !important;
    margin: 0 0 8px 0 !important;
    overflow: visible !important;
    clip: auto !important;
    clip-path: none !important;
    white-space: normal !important;
}
```

> Without this, `color: #4AC6D3 !important` on `h1.login-heading` silently fails — the text element exists in the DOM but is visually hidden by Bootstrap's utility class.

#### Pitfall: Chromium `background-clip: text` Renders Invisible

`-webkit-background-clip: text` + `-webkit-text-fill-color: transparent` for gradient text causes the heading to disappear entirely in Chromium-based browsers. This is a known Chrome/Edge bug triggered by re-renders. **Fix:** use solid `color` + `text-shadow` glow instead:

```css
/* BROKEN (Chromium): */
background: linear-gradient(135deg, #4AC6D3, #5FDBA7);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;

/* FIXED (solid + glow): */
color: #4AC6D3;
text-shadow: 0 0 20px rgba(74, 198, 211, 0.3), 0 2px 4px rgba(0, 0, 0, 0.5);
```

> This pitfall is especially likely when using agy to generate CSS — agy naturally produces gradient text styles. Always audit for `background-clip: text` before injecting into Moodle.

#### Workflow: agy for Moodle CSS Generation

agy (`--print` mode) can generate polished Moodle CSS when given a prompt with:
1. The exact HTML structure (selectors from the live page)
2. Design tokens (colors, fonts, shadows)
3. Moodle-specific constraints (`#page-login-index` prefix, `!important` on Bootstrap overrides, mobile breakpoints)

```bash
# 1. Curl the login page to extract the exact DOM structure
curl -s https://treinamentos.idconsultoria.ai/login/index.php > /tmp/page.html

# 2. Write prompt with HTML structure + design tokens + requirements
cat > /tmp/agy-prompt.txt << 'PROMPT'
Gere CSS para página de login Moodle. Todos seletores prefixados com #page-login-index.
Estrutura HTML: [paste from page inspection]
Design tokens: primaria=#4AC6D3, secundaria=#5FDBA7, depth=#005465, bg=#050a0f
Fontes: Bricolage Grotesque (headings), Nunito (body)
Requisitos: background animado, card glass morphism, icones SVG nos inputs, responsivo <=640px, prefers-reduced-motion
Output: APENAS <style>...</style> completo
PROMPT

# 3. Run agy in background (takes 1-3 min)
ssh oracle-host 'export PATH=$PATH:/home/ubuntu/.local/bin && agy --print "$(cat /tmp/agy-prompt.txt)"'

# 4. Audit output for Chromium traps before injecting:
#    - Search for "background-clip: text" → replace with solid color + glow
#    - Search for "webkit-text-fill-color" → same replacement
#    - Confirm .visually-hidden override is present

# 5. Inject via additionalhtmlhead (see workaround above) + purge caches
```

> agy saves 30-60 min of hand-writing CSS, but its output MUST be audited for the two pitfalls above before injection. See `references/id-consultoria-brand-tokens.md` for the token source.

#### Pitfall: Logo and Favicon Identical

Both were set to the same 357KB file. The logo should be the full wordmark; the favicon a small square icon. Fix by uploading separate files via the File API.

### Login Heading Customization

The login page heading is controlled by the Boost Union `loginpageheading` setting. Default value `logintofullname` uses the language string "Acesso a {fullname}" (pt_br). To show a custom heading:

```sql
-- 1. Set heading mode to show the site fullname verbatim (no prefix)
UPDATE mdl_config_plugins SET value = 'fullname'
WHERE plugin = 'theme_boost_union' AND name = 'loginpageheading';

-- 2. Set the fullname to exactly the desired heading text
UPDATE mdl_course SET fullname = 'Acesse o portal de Treinamentos da ID Consultoria' WHERE id = 1;

-- 3. Purge caches (REQUIRED — heading is cached in MUC)
```

Available `loginpageheading` values in Boost Union 5.0:
- `logintofullname` — "Acesso a {fullname}" (default, uses lang string with site fullname)
- `fullname` — site fullname only, no prefix
- `logintosite` — "Acesso ao site" (site-independent, ignores fullname)

> **Prefer `fullname` + direct fullname edit over language string overrides.** The `mdl_tool_customlang` route (overriding the `logintofullname` string) requires populating `mdl_tool_customlang_components` first, and the language cache may not clear with `purge_caches.php` alone. The `fullname` approach is a single SQL UPDATE and works reliably.

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

- **SCSS pipeline broken in 5.2 + Boost Union 5.0:** `scss`/`scsspre`/`scsspost` DB fields do not compile into the theme stylesheet. Use `additionalhtmlhead` core setting instead (see Branding → SCSS Pipeline Pitfall above).
- **CLI upgrade script** may timeout on first run after plugin install (SCSS compilation on ARM64). Use `--non-interactive` and let it finish.

## User Management via SQL

When the `admin/tool/uploaduser` CLI is missing (common in minimal Moodle images), batch-create users and enrol them with direct SQL.

### Create Users

```bash
# 1. Generate bcrypt hash for the default password
docker exec moodle-app php -r 'echo password_hash("DefaultPass2026!", PASSWORD_DEFAULT);'
# → $2y$10$wTDP9P9tPD5Bhv9CRNHDjewhWu8xi3bQT6UIOAHS1xcoHBHAuFISC

# 2. Insert users (Python on host — avoids shell quoting hell)
```

```python
# Template: batch user creation script
PASSWORD_HASH = "$2y$10$..."  # from step 1
now = int(time.time())

for firstname, lastname, username, email in users:
    # Check duplicate first
    existing = run_sql(f"SELECT id FROM mdl_user WHERE email = '{email}';")
    if existing: continue  # skip

    sql = f"""INSERT INTO mdl_user (
        auth, confirmed, policyagreed, deleted, suspended, mnethostid,
        username, password, firstname, lastname, email,
        timecreated, timemodified, firstaccess, lastaccess,
        lang, calendartype, mailformat, maildisplay, maildigest,
        trackforums, timezone
    ) VALUES (
        'manual', 1, 0, 0, 0, 1,
        '{username}', '{PASSWORD_HASH}', '{firstname}', '{lastname}', '{email}',
        {now}, {now}, 0, 0,
        'pt_br', 'gregorian', 1, 2, 0,
        0, '99'
    );"""
    run_sql(sql)

# 3. Fetch the new user ID
uid = run_sql(f"SELECT id FROM mdl_user WHERE username = '{username}';")
```

**Naming convention:** `username` = email local-part (before `@`), with dots preserved (e.g., `trajano.souza`). `firstname` = first name(s), `lastname` = remaining names. Deduplicate by email before inserting.

**Post-creation:** Users log in with the default password and use "Perdeu a senha?" (Forgot password) link to set their own. No need to force password change flags — Moodle's forgot-password flow handles it cleanly.

### Find or Create Manual Enrolment Instance

```sql
-- Check if manual enrolment exists for the course
SELECT id FROM mdl_enrol WHERE courseid = 2 AND enrol = 'manual' LIMIT 1;

-- Create if missing
INSERT INTO mdl_enrol (enrol, status, courseid, timecreated, timemodified)
VALUES ('manual', 0, 2, EXTRACT(EPOCH FROM NOW())::bigint, EXTRACT(EPOCH FROM NOW())::bigint);
```

### Enrol Users

```python
enrol_id = 1  # from query above
for uid in user_ids:
    # Check not already enrolled
    existing = run_sql(f"SELECT id FROM mdl_user_enrolments WHERE userid = {uid} AND enrolid = {enrol_id};")
    if existing: continue

    run_sql(f"""INSERT INTO mdl_user_enrolments (enrolid, userid, status, timecreated, timemodified)
                VALUES ({enrol_id}, {uid}, 0, {now}, {now});""")
```

### Verify

```sql
SELECT u.id, u.username, u.firstname || ' ' || u.lastname AS nome, u.email,
       CASE WHEN ue.id IS NOT NULL THEN 'Matriculado' ELSE 'Nao' END
FROM mdl_user u
LEFT JOIN mdl_user_enrolments ue ON ue.userid = u.id AND ue.enrolid = 1
WHERE u.id >= 3
ORDER BY u.id;
```

### Pitfall: `psql` output parsing

The `psql -At` flag produces unaligned tuples but INSERT/UPDATE commands emit extra lines (e.g., `INSERT 0 1`). When using `RETURNING id`, parse only numeric lines:

```python
lines = [l for l in output.split('\n') if l.strip().isdigit()]
uid = int(lines[0]) if lines else None
```

## CSS Cascade Management

When iterating on injected CSS (via `additionalhtmlhead`), repeated `UPDATE ... SET value = '...'` with incremental patches leads to conflicts. After 3+ patches, the CSS file becomes self-contradictory (competing `!important` rules, broken layouts, overlapping inputs).

**Pattern:** when a layout breaks after a patch iteration, rewrite the entire CSS blob cleanly rather than adding another fix layer. A single well-structured 14KB file outperforms a 30KB accumulation of patches.

```python
# Clean rewrite approach:
css = """<style>
/* Single coherent block: background → wrappers → card → inputs → button → footer → responsive */
</style>"""
escaped = css.replace("'", "''")
run_sql(f"UPDATE mdl_config SET value = '{escaped}' WHERE name = 'additionalhtmlhead';")
```

### Pitfall: Pseudo-element Icons Break Bootstrap Form Layout

Adding `::before` pseudo-elements with `position: absolute` on Moodle's `.login-form-username` / `.login-form-password` containers (to inject SVG icons) causes severe layout breakage:

- **Symptom:** The password input overlaps the username input, the eye toggle is misaligned, the underline bar detaches.
- **Root cause:** Moodle's form containers include the `<label>` element, making the container taller than the input. `position: absolute` with `bottom` or `top` on `::before` positions relative to the container, not the input. When the label is `.visually-hidden` (height 0 in rendering but 1px in layout), the icon position calculation is unpredictable across browsers.
- **Fix:** Remove all `::before` pseudo-element icons from form containers. Let Bootstrap handle the eye toggle natively. Style inputs with `padding`, `border-radius`, `background`, and `:focus` states only. The SVG icon approach is fragile on Moodle's DOM and not worth the maintenance cost.

> This took 3 debugging iterations to isolate. The clean rewrite (single coherent 14KB block without pseudo-element icons) resolved all overlap issues immediately.

## Admin Account Management

Moodle stores admin privileges in the `siteadmins` config value (comma-separated user IDs). To demote the original admin and promote a new one:

```sql
-- 1. Rename old admin username to free 'admin' for the new account
UPDATE mdl_user SET username = 'gustavo.mello' WHERE id = 2;

-- 2. Create new admin user
INSERT INTO mdl_user (
    auth, confirmed, policyagreed, deleted, suspended, mnethostid,
    username, password, firstname, lastname, email,
    timecreated, timemodified, firstaccess, lastaccess,
    lang, calendartype, mailformat, maildisplay, maildigest,
    trackforums, timezone
) VALUES (
    'manual', 1, 0, 0, 0, 1,
    'admin', '<bcrypt_hash>', 'Admin', '', 'admin@idconsultoria.ai',
    EXTRACT(EPOCH FROM NOW())::bigint, EXTRACT(EPOCH FROM NOW())::bigint, 0, 0,
    'pt_br', 'gregorian', 1, 2, 0, 0, '99'
) RETURNING id;  -- → id=10

-- 3. Set new admin as sole site admin
UPDATE mdl_config SET value = '10' WHERE name = 'siteadmins';

-- 3b. CRITICAL: Kill old admin's sessions + purge caches
-- The demoted user retains admin capabilities from their existing session
-- until the session is destroyed. siteadmins change alone is NOT sufficient.
docker exec moodle-app php /var/www/html/admin/cli/kill_all_sessions.php --for-users=2 --run
docker exec moodle-app php /var/www/html/admin/cli/purge_caches.php

-- 4. Enrol both in existing courses
INSERT INTO mdl_user_enrolments (enrolid, userid, status, timecreated, timemodified)
SELECT 1, 10, 0, EXTRACT(EPOCH FROM NOW())::bigint, EXTRACT(EPOCH FROM NOW())::bigint
WHERE NOT EXISTS (SELECT 1 FROM mdl_user_enrolments WHERE userid = 10 AND enrolid = 1);
```

> **Always enrol the new admin in courses** — admin privileges grant site-wide access but explicit enrolment is still needed for course dashboards to show the course. Without it, the admin sees an empty dashboard.

## Language String Customization

Moodle's `tool_customlang` allows overriding any language string via the DB. This is useful for changing the login page heading prefix without modifying PHP files.

### The `logintofullname` string

```sql
-- 1. Populate the components table (empty on fresh installs)
INSERT INTO mdl_tool_customlang_components (name, version) 
VALUES ('moodle', '2025041400')
ON CONFLICT DO NOTHING;

-- 2. Override the string (e.g., change "Acesso a {$a}" → "Acesse o {$a}")
INSERT INTO mdl_tool_customlang 
  (lang, componentid, stringid, original, master, local, timecustomized, timemodified, outdated, modified)
SELECT 'pt_br', id, 'logintofullname', 'Acesso a {$a}', 'Acesso a {$a}', 'Acesse o {$a}', 
       EXTRACT(EPOCH FROM NOW())::bigint, EXTRACT(EPOCH FROM NOW())::bigint, 0, 1
FROM mdl_tool_customlang_components WHERE name = 'moodle';
```

### Pitfall: `$a` Placeholder Escaping

The `$a` variable in Moodle lang strings MUST be written literally as `{$a}` in the DB. Shell escaping through SSH + psql requires **Python script injection** — never try heredoc or in-line escaping:

```python
# ✅ Correct — Python handles $ escaping cleanly
target = 'Acesse o {$a}'
escaped = target.replace("'", "''")
sql = f"UPDATE mdl_tool_customlang SET local = '{escaped}' WHERE stringid='logintofullname';"
subprocess.run(["docker", "exec", "-i", "moodle-postgres", "psql", ...], input=sql)

# ❌ Wrong — Bash swallows $a, result is "Acesse o {}"
ssh oracle-host "docker exec ... psql ... -c \"UPDATE ... SET local = 'Acesse o {\$a}'\""
```

### Pitfall: Language Cache Invalidation

`purge_caches.php` does NOT reliably clear the language string cache in Moodle 5.2. If the heading still shows the old string after updating `mdl_tool_customlang`, the `loginpageheading` → `fullname` approach is more reliable:

```sql
-- Direct fullname edit bypasses the language system entirely
UPDATE mdl_config_plugins SET value = 'fullname' WHERE name = 'loginpageheading';
UPDATE mdl_course SET fullname = 'Acesse o portal de Treinamentos da ID Consultoria' WHERE id = 1;
```

> **Prefer `fullname` over `tool_customlang`** for login heading changes. One SQL UPDATE, guaranteed to work. See Login Heading Customization section above.

## Backups

```bash
docker exec moodle-postgres pg_dump -U moodle moodle > moodle_$(date +%Y%m%d).sql
sudo tar czf moodledata_$(date +%Y%m%d).tar.gz data/moodledata/
```
