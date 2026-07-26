# IIFE Scope Bug in Vanilla JS Views

> Capturado do VERO (Jul 2026): `ReferenceError: fmt is not defined` em `apontamentos.js` após modularização.

## O bug

Em SPAs vanilla que usam IIFE para namespacing, é comum declarar dependências dentro da função `render()`:

```js
VERO.views.apontamentos = (function () {
  'use strict';

  function render(container) {
    var store = VERO.store, dom = VERO.dom, fmt = VERO.format;
    // ...
    html += _renderRows(store, items);  // ⚠️ _renderRows não vê fmt!
  }

  function _renderRows(store, items) {
    items.forEach(function(a) {
      html += '<td>' + fmt.formatData(a.data) + '</td>';  // ReferenceError: fmt is not defined
    });
  }
})();
```

## Symptom

- Console: `VERO Router: erro ao carregar módulo "apontamentos"`
- Stack: `ReferenceError: fmt is not defined` ou `TypeError: Cannot read properties of undefined (reading 'get')`
- UI: Fallback "⚠️ Erro ao carregar módulo"

## Root cause

`var fmt = VERO.format` está no closure de `render()`. Funções helper definidas no escopo IIFE (como `_renderRows`, `_paginationHtml`) NÃO têm acesso às variáveis locais de `render()`.

## Fix options

### Option A: Pass as parameters (recommended for safety)

```js
function render(container) {
  var store = VERO.store, fmt = VERO.format;
  html += _renderRows(store, items, fmt);  // passa fmt explicitamente
}

function _renderRows(store, items, fmt) {  // aceita como parâmetro
  // fmt é o parâmetro, não a variável do closure
}
```

### Option B: Declare at IIFE level (only if script loads AFTER dependencies)

```js
VERO.views.apontamentos = (function () {
  var store = VERO.store, dom = VERO.dom, fmt = VERO.format;  // IIFE scope

  function render(container) {
    var apontamentos = store.get('apontamentos');
    html += _renderRows(apontamentos);  // _renderRows acessa fmt do closure
  }

  function _renderRows(items) {
    // fmt disponível via closure
  }
})();
```

⚠️ **Option B só funciona se a view carregar DEPOIS de store.js, dom.js, format.js no index.html.** Se houver dúvida sobre ordem, use Option A.

## Detection script

```bash
# Find helpers that use fmt/store/dom but don't receive them as parameters
for f in js/views/*.js; do
  echo "=== $f ==="
  # Count fmt usage in helper functions
  helpers=$(sed -n '/^  function _/p' "$f")
  echo "$helpers" | while read -r line; do
    helper_name=$(echo "$line" | grep -oP 'function \K\w+')
    # Get body of helper and count fmt usage
    fmt_count=$(sed -n "/function $helper_name/,/^  }/p" "$f" | grep -c 'fmt\.')
    if [ "$fmt_count" -gt 0 ]; then
      # Check if fmt is in function parameters
      has_param=$(echo "$line" | grep -c "fmt")
      if [ "$has_param" -eq 0 ]; then
        echo "  ⚠️  $helper_name usa fmt $fmt_count vezes mas não está nos parâmetros"
      fi
    fi
  done
done
```

## Real example

VERO `apontamentos.js` — 393 linhas. `fmt` declarado em `render()` (linha 12), usado em `_renderRows()` (linhas 56, 63, 64) e `_refreshTable()` (linha 386). Nenhum dos dois recebia `fmt` como parâmetro.

Fix: `_renderRows(store, items, fmt)` + `_refreshTable` usa `VERO.format` diretamente.

Outras 7 views não usavam `fmt` e estavam OK.
