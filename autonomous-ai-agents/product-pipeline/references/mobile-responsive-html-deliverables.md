# Mobile Responsive HTML Deliverables

## Problema Comum

HTML com sidebar + conteúdo em grid horizontal quebra no mobile.
O usuário reporta: "precisa scrollar para a direita para ler o conteúdo".

## Diagnóstico Rápido

```javascript
// Colar no console do navegador para detectar overflow
const all = document.querySelectorAll('*');
let offenders = [];
all.forEach(el => {
  const rect = el.getBoundingClientRect();
  if (rect.right > window.innerWidth + 1 && rect.width > 50) {
    offenders.push({tag: el.tagName, cls: el.className, right: rect.right, width: rect.width});
  }
});
console.table(offenders.slice(0, 20));
```

## Checklist de Correção

### 1. Container raiz
```css
html { overflow-x: hidden; }
body { overflow-x: hidden; }
```

### 2. Grid layout → single column no mobile
```css
.app-layout {
  display: grid;
  grid-template-columns: 300px 1fr;  /* desktop */
}

@media (max-width: 1023px) {
  .app-layout {
    grid-template-columns: 1fr;  /* mobile */
  }
  .sidebar { display: none; }
}
```

### 3. Tabelas — container de scroll obrigatório

**Cada `<table>` DEVE estar dentro de `<div class="table-wrapper">`.**

```css
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  max-width: 100%;
}

.report-content table {
  width: 100%;
  border-collapse: collapse;
}
```

**NÃO** fazer no mobile:
```css
/* RUIM — causa overflow horizontal na página */
.report-content table {
  display: block;
  white-space: nowrap;
  overflow-x: auto;
}
```

Em vez disso, o scroll deve estar no `.table-wrapper`, não na tabela.

**Técnica: como embrulhar todas as tabelas existentes com .table-wrapper**

Se o HTML já existe e tem `<table>` soltas sem wrapper, usar este script Python:

```python
with open('seu-arquivo.html', 'r') as f:
    html = f.read()

result = []
i = 0
count = 0
while True:
    table_start = html.find('<table', i)
    if table_start == -1:
        result.append(html[i:])
        break
    table_end_tag = html.find('</table>', table_start)
    if table_end_tag == -1:
        result.append(html[i:])
        break
    table_end = table_end_tag + len('</table>')
    
    result.append(html[i:table_start])
    result.append('<div class="table-wrapper">\n')
    result.append(html[table_start:table_end])
    result.append('\n</div>')
    i = table_end
    count += 1

with open('seu-arquivo.html', 'w') as f:
    f.write(''.join(result))

print(f"Envelopou {count} tabelas")
```

**Verificar se funcionou:** `grep -c 'class="table-wrapper"' arquivo.html` deve igualar `grep -c '<table' arquivo.html`.

### 4. Código (pre/code)
```css
.report-content pre {
  word-break: break-word;
  white-space: pre-wrap;     /* quebra linhas longas */
  overflow-x: auto;          /* fallback se não quebrar */
  max-width: 100%;
}

.code-wrapper {
  max-width: 100%;
  overflow-x: auto;
}
```

### 5. Texto longo e links
```css
.report-content p,
.report-content li {
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
}
```

### 6. Imagens e SVGs
```css
img, svg, video, iframe {
  max-width: 100%;
  height: auto;
}
```

### 7. Breakpoints recomendados (640px e 400px)

| Breakpoint | Padding | Font size (h1) | Ajustes |
|-----------|---------|----------------|---------|
| < 1024px (tablet) | 24px 16px | 1.85rem | Sidebar escondida, bottom nav |
| < 640px (mobile) | 16px 12px | 1.35rem | Tabelas com scroll, fontes menores, TOC oculto |
| < 400px (muito pequeno) | 12px 8px | 1.2rem | Padding mínimo, fontes ainda menores |

## Procedimento de Deploy

1. Aplicar correções diretamente no HTML/CSS
2. Se houver tabelas sem `.table-wrapper`, rodar o script Python acima
3. Fazer deploy (Vercel, etc.)
4. Testar no celular OU redimensionar navegador para 375px de largura
5. Verificar se scroll horizontal sumiu
6. Verificar se tabelas e código têm scroll interno (não página)

## Referência

Este documento complementa a seção de HTML responsivo na Fase 2 do product-pipeline.
