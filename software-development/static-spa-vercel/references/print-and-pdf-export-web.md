# Export PDF / impressão de um site estático (botão dentro da página)

Quando o PDF sai de um botão do próprio site (`html2pdf().set(opts).from(el).save()`, html2canvas),
o pipeline é rasterização do DOM no navegador — não impressão do Chromium. Estes são os modos de
falha reais e como fechá-los.

## 1. Falha silenciosa: prove a geração, não a ausência de erro

`save()` resolve a promise mesmo quando o html2canvas abortou (o erro morre num `.catch()` que só
remove a classe de estilo). Instrumente e afirme:

```js
window.__blobs=[];
const _o=URL.createObjectURL; URL.createObjectURL=b=>{window.__blobs.push({t:b.type,s:b.size}); return _o.call(URL,b)};
// clicar no botão do PDF e ler window.__blobs → [{t:'application/pdf', s:253584}]
```

Alternativas: `Browser.setDownloadBehavior` + `Page.downloadWillBegin`; ou `outputPdf('blob')`,
que propaga a exceção que o `save()` engole. Clique de JS pode não autorizar o download — para o
caminho completo, clique real (`Input.dispatchMouseEvent`).

## 2. `color-mix()` aborta a captura

Sintoma: `Attempting to parse an unsupported color function "color"` e arquivo que nunca sai.
Vale para `color-mix()`, `oklch()`, `light-dark()`. Use **rgba()/hex literais** em CSS que precisa
ser impresso: exponha as variações como custom properties por variante
(`--tag-line`/`--tag-fill` por `[data-sector]`) em vez de computá-las com `color-mix()`.
Grep obrigatório antes de fechar: `color-mix|oklch|light-dark` em `css/` e `js/`.

## 3. Captura de ELEMENTO: não passe `windowWidth`/`windowHeight`

Com `from(el)` + `windowWidth/Height` o alvo sai do recorte e páginas curtas saem **em branco**
(a promise resolve normal). Deixe o html2canvas dimensionar pela seção e faça a página fluir numa
classe de modo captura:

```css
.pdf-export .screen-content { position: static !important; inset: auto !important; height: auto !important;
  display: block !important; opacity: 1 !important; pointer-events: auto !important; }
.pdf-export .reveal, .pdf-export .reveal--stagger > * { opacity: 1 !important; filter: none !important; transform: none !important; }
```

Sem isso, telas com conteúdo fixo/`height: 100vh` (apresentações) saem com meia página vazia e o
que era animação de entrada aparece invisível.

## 4. Limite de canvas: escala pela altura

Documento alto × `scale: 2` estoura a dimensão máxima do canvas e o PDF sai quebrado/quase vazio.

```js
const escala = el.scrollHeight > 9000 ? 1 : 2;
html2canvas: { scale: escala, useCORS: true, backgroundColor: '#FFFFFF', logging: false }
```

## 5. Componente horizontal precisa empilhar no PDF

Carrossel/track com N cards lado a lado vira faixa de dezenas de milhares de pixels de largura e a
captura sai quase vazia. No modo captura, force pilha:

```css
.pdf-export .carousel-track { display: block !important; transform: none !important; }
.pdf-export .project-card { width: 100% !important; max-width: 100% !important; max-height: none !important; }
.pdf-export .carousel-arrow, .pdf-export .carousel-dots { display: none !important; }
```

`page-break-after: always` na seção capturada gera **página final vazia** — use `auto`.
`pagebreak: { mode: ['css','legacy'], avoid: [...blocos...] }` ajuda; `mode: ['css']` sozinho pode
zerar o conteúdo, então valide depois de mexer.

## 6. Verificação sem olho humano

O PDF é rasterizado (o `pdftotext` vem vazio — esperado). Meça tinta por página:

```bash
pdfinfo out.pdf | grep Pages      # nº de páginas
pdftoppm -png -r 40 out.pdf pg    # 1 PNG por página
```

```python
from PIL import Image
im = Image.open('pg-1.png').convert('L'); px = list(im.getdata())
print(100*sum(1 for v in px if v < 245)/len(px))   # 0% = página em branco; 30-45% = densa
```

Confira também o tamanho por tela: páginas em branco produzem PDFs de dezenas de KB onde o
esperado era centenas. Última página 0% = quebra sobrando.

## 7. Contraste no modo impresso

O modo captura redefine a paleta para fundo branco (variáveis `--text-*` trocadas dentro de
`.pdf-export`). Rode o mesmo audit de contraste **com a classe aplicada** — tons de tela escura
(`#7C8F99` sobre `#050A0F`) não garantem AA sobre branco, e cinzas de interface costumam ficar
abaixo de 4,5:1 no papel.
