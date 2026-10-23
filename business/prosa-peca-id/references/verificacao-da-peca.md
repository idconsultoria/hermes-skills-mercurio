# Verificação da peça final

A prosa só existe depois de o arquivo abrir certo. Rode esta sequência antes de dizer "pronto".

## 1. Renderizar o PDF

Neste host o caminho é o Chromium nativo do Termux, sem Node e sem Playwright:

```bash
chromium-browser --headless --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-pdf-header-footer \
  --print-to-pdf="$PWD/peca.pdf" "file://$PWD/peca.html"
```

O stderr enche de erro de dbus; o sinal de sucesso é a linha `N bytes written to file`. Se
`node -e "console.log(process.platform)"` responder `android`, Playwright não roda aqui; o Chromium
do cache do Playwright é glibc e pede `grun`.

## 2. Medir overflow de cada página

`.page{overflow:hidden}` corta texto sem avisar. Injete uma sonda no HTML e leia o resultado pelo
`--dump-dom`:

```python
html = open('peca.html').read()
js = ("<script>window.addEventListener('load',function(){setTimeout(function(){"
      "var o=[].map.call(document.querySelectorAll('.page'),function(p,i){"
      "return 'pg'+(i+1)+'='+(p.scrollHeight-p.clientHeight)});"
      "var d=document.createElement('div');d.id='MEASURE';d.textContent='MEASURE:'+o.join(' ');"
      "document.body.appendChild(d);},300)});</script>")
open('_measure.html','w').write(html.replace('</body>', js + '</body>'))
```

```bash
chromium-browser --headless --no-sandbox --disable-gpu --virtual-time-budget=5000 \
  --dump-dom "file://$PWD/_measure.html" 2>/dev/null | grep -o 'MEASURE:pg1=[^<]*'
```

Zero em todas as páginas é a única condição de pronto. Zero com até 10 px de sobra ainda pode
significar descida de letra cortada: confira no PNG.

## 3. Contagem de páginas e conferência visual

```bash
pdfinfo peca.pdf | grep Pages
rm -f pg-*.png && pdftoppm -r 115 -png peca.pdf pg
```

Leia os PNG com `vision_analyze`, página por página, perguntando explicitamente: texto cortado,
sobreposição, logo renderizado, filete encostando em texto, espaço no fim da última página. Visão
pega o que a medição numérica não pega, e vice-versa.

## 4. Espaçamento que o cliente nota

Filete nunca encosta em texto. Valores que funcionam em A4 com margem de 15/16 mm:

| Elemento | Ajuste |
|---|---|
| Filete sob o título | `margin:6.5mm 0 0` |
| Primeiro subtítulo depois do filete | `margin-top:7mm` (`.rule + h3`) |
| Subtítulos no corpo | `margin:7.5mm 0 3.6mm` |
| Parágrafo após parágrafo | `margin-top:2.8mm` |
| Célula de tabela | `padding:3.4mm 0` |
| Linha de lista com filete | `padding:2.6mm 0` |
| Rodapé | `padding-top:3.4mm`, `bottom:8mm` |
| Caixa que fecha a página | `padding-bottom:6.4mm` |

## 5. Sinal de que a página precisa de ar

Se a medição dá overflow de 20 a 100 px, resista à tentação de apertar entrelinha: corte texto ou
mova uma seção para a página seguinte. O leitor percebe aperto antes de perceber comprimento, e uma
página a mais não é defeito em documento de 6 ou 7 páginas.
