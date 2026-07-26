# Variable Shadowing in Nested Callbacks

> Capturado do VERO Run #3 (Jul 2026): `TypeError: s.find is not a function` em `nutricao-aplicacoes.js`.

## O bug

Em reduce/forEach aninhados, usar o mesmo nome de variável para a store e um acumulador causa shadowing:

```js
// ❌ BUG: s é sombreado
var s = VERO.store;
var totalCusto = aplicacoes.reduce(function (sum, a) {
  return sum + (a.produtos || []).reduce(function (s, p) {
    // s aqui é o número acumulador (sum), NÃO VERO.store!
    var prod = s.find(function (pr) { ... });  // TypeError: s.find is not a function
  }, 0);
}, 0);
```

## Sintoma

- Tela carrega mas mostra dados errados (totais zerados ou NaN)
- Console: `TypeError: s.find is not a function` ou `TypeError: Cannot read properties of undefined`
- Mais sutil que o IIFE scope bug porque a view NÃO quebra completamente — só mostra dados incorretos

## Root cause

O callback interno `function(s, p)` cria uma nova variável `s` que SOMBREIA a `s` do escopo externo (`VERO.store`). Dentro do callback, `s` é um número (acumulador), não a store.

## Fix

Usar nomes semanticamente distintos para cada nível de escopo:

```js
// ✅ CORRETO: nomes distintos
var store = VERO.store;
var totalCusto = aplicacoes.reduce(function (acc, a) {
  return acc + (a.produtos || []).reduce(function (sum, p) {
    var prod = store.find(function (pr) { return pr.id === p.produtoId; });
    return sum + (p.qtdConsumida || 0) * (prod ? prod.custoMedio || 0 : 0);
  }, 0);
}, 0);
```

## Prevention checklist

| Nome da store | Acumuladores recomendados | NUNCA usar |
|--------------|--------------------------|------------|
| `store` | `acc`, `sum`, `total` | `s`, `st`, `sto` |
| `s` | `acc`, `sum`, `total` | `s` (em escopo aninhado) |

**Regra:** se a store é `store`, acumuladores são `acc`/`sum`/`total`. Se a store é `s`, acumuladores NUNCA podem ser `s` em nenhum nível aninhado.

## Detection script

```bash
# Find nested callbacks where a store variable is shadowed
for f in js/views/*.js; do
  # Find store variable declarations
  store_var=$(grep -oP "var\s+\K\w+(?=\s*=\s*VERO\.store)" "$f")
  if [ -n "$store_var" ]; then
    # Check if any inner function param matches the store variable name
    shadow_count=$(grep -c "function\s*(\s*$store_var\s*[,)]" "$f")
    if [ "$shadow_count" -gt 1 ]; then
      echo "⚠️  $f: variável de store '$store_var' potencialmente sombreada em $shadow_count callbacks"
    fi
  fi
done
```

## Caso real

VERO `nutricao-aplicacoes.js` — 60 linhas. `var s = VERO.store` (linha 12), callback interno `function(s, p)` (linha 17) sombreava a store. `s.find()` falhava porque `s` era um número. Corrigido renomeando para `store` + `acc`/`sum`.
