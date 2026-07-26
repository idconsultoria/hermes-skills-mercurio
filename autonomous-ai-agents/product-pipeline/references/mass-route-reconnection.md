# Mass Route Reconnection — "Views Exist, Router Doesn't Call Them"

## When to use

When you audit a SPA and find:
- 50+ `renderPlaceholder(...)` calls in `app.js`
- But 40+ view files already exist in `js/views/`
- The problem is **wiring**, not missing views

The router was never updated to connect the views after they were created. This typically happens after a Pi session creates views but doesn't update the router wiring, or after multiple incremental changes that left old placeholder calls in place.

## Pattern

### Step 1: Diagnose
```bash
# Count the damage
grep -c "renderPlaceholder" js/app.js
ls js/views/*.js | wc -l

# Identify which views exist but aren't connected
for f in js/views/*.js; do
  name=$(basename $f .js)
  grep -q "$name" js/app.js || echo "UNUSED: $name"
done
```

### Step 2: Give Pi the mapping table

The prompt must include an explicit mapping of every view file to its route. Pi cannot guess — the naming conventions may differ from what `secondaryNavs` expects.

```markdown
## Mapeamento views → rotas
| Arquivo | Rota |
|---------|------|
| dashboard-financeiro.js | dashboard/financeiro |
| mip-alertas-fitossanitarios.js | mip/alertas-fitossanitarios |
| estoque-almoxarifados.js | estoque/almoxarifados |
... (all 40+ views)
```

### Step 3: Pi rewrites app.js

Pi reads all view files to discover the exact `VERO.views.XXX` registration name, then rewrites the router to use:
```js
if (VERO.views.xxx) VERO.views.xxx.render(container);
else renderComingSoon(title, container, description);
```

The `renderComingSoon()` function is a visual placeholder that uses SVG icons (NOT emojis) and shows "Funcionalidade em implementação" with a construction icon from the design system.

### Step 4: Verify
```bash
# Should be 0 active renderPlaceholder calls
grep -c "renderPlaceholder" js/app.js

# Should be 40+
grep -c "VERO.views" js/app.js
```

## Result (real example: VERO Run #4)

| Before | After |
|--------|-------|
| 50 `renderPlaceholder` calls | 0 (only in function definition comment) |
| ~20 `VERO.views` invocations | 75 `VERO.views` invocations |
| app.js: 791 lines | app.js: ~620 lines (cleaner) |
| 51 view files, ~10 connected | 51 view files, all connected |

## Pitfalls

- Pi may try to create new view files instead of connecting existing ones — the prompt must explicitly say "connect existing views, don't create new ones"
- View registration names may use camelCase (`VERO.views.mipAlertasFitossanitarios`) while file names use kebab-case (`mip-alertas-fitossanitarios.js`) — Pi must read each file to discover the actual registration name
- Routes without a corresponding view file should use `renderComingSoon()`, not `renderPlaceholder()` — these are future features, not broken wiring
