# Extract Editorial Excerpt — Regex Reference

## Problema

A função `extract_editorial_first_paragraph()` em `_deploy_new_edition.py`
extrai o texto do editorial do HTML fonte para usar como preview no index.

O padrão original era:
```python
r'class="hot-take"[^>]*>(.*?)</div>'
```

Isso **não casa** com `class="hot-take-box"`. O `"` literal depois de
`hot-take` na regex faz o matching falhar porque a string real é
`hot-take-box"` — o `-box` impede o match.

## Sintomas

O preview da edição no index.html mostra CSS bruto em vez do texto editorial:
```
"IAF — Manhã Aumentada · 10/06/2026 /* === PDF Styles ..."
```

Isso acontece porque a regex não encontra o editorial, cai no fallback
que tira tags HTML do documento inteiro, e o primeiro conteúdo visível
é do `<title>` e do `<style>`.

## Fix

Use `[^"]*` no lugar do `"` literal para casar o resto do valor do
atributo class:

```python
# Antes (quebrado):
r'class="hot-take"[^>]*>(.*?)</div>'

# Depois (funciona com hot-take-box, hot-take-text, etc.):
r'class="hot-take[^"]*"[^>]*>(.*?)</div>'
```

Também adicione um fallback para `hot-take-text` como segurança extra:
```python
r'class="hot-take-text"[^>]*>(.*?)</p>'
```

## Ordem de tentativa (do deploy script atual)

1. `class="editorial-text"[^>]*>(.*?)</div>` (template alternativo)
2. `class="hot-take[^"]*"[^>]*>(.*?)</div>` (template atual — hot-take-box)
3. `class="hot-take-text"[^>]*>(.*?)</p>` (fallback — parágrafo individual)

## Template HTML alvo

```html
<div class="hot-take-box">
  <p class="hot-take-text">
    <strong>Texto do editorial...</strong> ...
  </p>
  ...
</div>
```
