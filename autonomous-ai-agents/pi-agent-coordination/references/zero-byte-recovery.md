# Zero-Byte File Recovery After Pi Agent

## Symptom

After Pi Agent writes files, some or all files are 0 bytes (empty). The view
doesn't load in the browser — no console error because the JS file is empty.

```bash
ls -la js/views/dashboard.js  # shows 0 bytes
```

## Detection

Always check ALL frontend files after a Pi run:

```bash
for f in js/utils.js js/components.js js/app.js js/views/*.js css/views.css index.html; do
  size=$(wc -c < "$f" 2>/dev/null || echo 0)
  [ "$size" -eq 0 ] && echo "ZERADO: $f"
done
```

## Recovery

If git has the file properly:

```bash
# Find commits where the file was intact
git log --oneline -- js/views/dashboard.js

# Restore from a specific commit
git show <hash>:js/views/dashboard.js > js/views/dashboard.js
```

If git also has 0 bytes (the commit saved the empty version):

```bash
# Find an older commit with the file intact
git log --oneline -- js/views/dashboard.js
git show 76b3471:frontend/js/views/dashboard.js > js/views/dashboard.js
```

## Prevention

Before deploying after Pi, verify all files + JS syntax + API paths:

```bash
# 1. Zero-byte check
for f in js/utils.js js/components.js js/app.js js/views/*.js; do
  [ "$(wc -c < "$f")" -eq 0 ] && echo "FAIL: $f is empty"
done

# 2. JS syntax
for f in js/utils.js js/components.js js/app.js js/views/*.js; do
  node -e "try{new Function(require('fs').readFileSync('$f','utf8'))}catch(e){console.log('FAIL: $f')}"
done

# 3. API paths in restored files — old versions may have wrong endpoints
grep -rn "api\.get\|api\.post\|api\.put\|api\.delete\|api\.patch" js/views/ | grep -E "get\('/[^d]|get\('/p[^r]"

# 4. DayName/Weekday mapping in weekly views
grep -rn "weekday" js/views/weekly.js
```

## Common API Path Drift in Restored Files

| Wrong (old) | Correct |
|------------|---------|
| `api.get('/weekly')` | `api.get('/dashboard/weekly')` |
| `api.get('/projects', { limit: 5 })` | `api.get('/dashboard/recent-projects')` |
| `stats.completed_this_week` | `stats.completed` |
| Missing `dayName` mapping | `d.dayName || d.weekday` needed |
