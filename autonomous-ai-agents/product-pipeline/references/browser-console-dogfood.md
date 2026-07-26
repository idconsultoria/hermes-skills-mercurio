# Browser Console Dogfood QA Patterns

Quick verification techniques using `browser_console(expression=...)` during F4e dogfood QA.

## Sidebar verification

```js
// List all secondary sidebar items
Array.from(document.querySelectorAll('.sidebar-secondary__item')).map(el => el.textContent.trim())

// Expected: ["Dashboard Gerencial", "Dashboard Financeiro", ...]
```

## Card CSS verification

```js
// Check that card overflow fix is applied
var v = document.querySelector('.card--kpi .card__value');
v ? {wordBreak: getComputedStyle(v).wordBreak, overflow: getComputedStyle(v.parentElement).overflow} : 'no card'
// Expected: {wordBreak: "break-word", overflow: "hidden"}
```

## Zero emojis check

```js
// Must return false
document.body.innerHTML.includes('🚧')
```

## Design tokens verification

```js
// Single token
getComputedStyle(document.documentElement).getPropertyValue('--sidebar-primary-bg').trim()
// Expected: "#0D2329"

// Multiple tokens
getComputedStyle(document.documentElement).getPropertyValue('--sidebar-primary-bg').trim() + ' | ' + getComputedStyle(document.documentElement).getPropertyValue('--btn-primary-bg').trim()
// Expected: "#0D2329 | #064E5B"
```

## JS error check

```js
// Check console for errors after navigation
// Use browser_console() with no expression — returns console log + errors
// Expected: 0 js_errors, no "VERO Router: erro ao carregar módulo"
```

## View existence check

```js
// Check if a specific view is registered
VERO.views.apontamentos ? 'existe' : 'nao existe'
// Also: typeof VERO.format, typeof VERO.store
```

## Navigation without clicks

```js
// Force hash navigation to test router
location.hash = '#apontamentos'; 'ok'
// Then check: no "VERO Router: erro ao carregar módulo" in console
```

## Design system fidelity

```js
// Confirm tokens match design-system.html V3.0
getComputedStyle(document.documentElement).getPropertyValue('--bg-canvas').trim()
// Expected: "#F5F3ED" (warm off-white)
getComputedStyle(document.documentElement).getPropertyValue('--sidebar-primary-bg').trim()
// Expected: "#0D2329" (teal dark)
getComputedStyle(document.documentElement).getPropertyValue('--btn-primary-bg').trim()
// Expected: "#064E5B" (teal medium)
```

## SPA router connectivity check

After Pi rewires router, verify views are connected:

```bash
# In terminal (not browser)
grep -c "renderPlaceholder" js/app.js    # should be 0
grep -c "VERO.views" js/app.js            # should be 40+
```

## Google Maps integration check

```js
// After navigating to #gestao-agricola/mapa
typeof google !== 'undefined' && typeof google.maps !== 'undefined'
// Expected: true (if Google Maps API loaded)
```
