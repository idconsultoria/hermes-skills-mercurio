#!/data/data/com.termux/files/usr/bin/bash
# Mede overflow vertical de cada .page de um HTML A4 (páginas com overflow:hidden).
# Uso: bash medir-overflow-paginas.sh caminho/arquivo.html
# Sadio = todos os valores 0. Qualquer valor positivo = conteúdo cortado no pé da página.
set -u
SRC="${1:?uso: bash medir-overflow-paginas.sh <arquivo.html>}"
[ -f "$SRC" ] || { echo "arquivo nao encontrado: $SRC"; exit 1; }

OUT="$(dirname "$SRC")/_measure.html"

python3 - "$SRC" "$OUT" <<'PY'
import sys
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
js = ("<script>window.addEventListener('load',function(){setTimeout(function(){"
      "var o=[].map.call(document.querySelectorAll('.page'),function(p,i){"
      "return 'pg'+(i+1)+'='+(p.scrollHeight-p.clientHeight)});"
      "var d=document.createElement('div');d.id='MEASURE';"
      "d.textContent='MEASURE:'+o.join(' ');document.body.appendChild(d);},400)});</script>")
if '</body>' not in html:
    print('ERRO: HTML sem </body>'); sys.exit(1)
open(out, 'w', encoding='utf-8').write(html.replace('</body>', js + '</body>'))
print('medidor injetado em', out)
PY

chromium-browser --headless --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --virtual-time-budget=6000 --dump-dom "file://$OUT" 2>/dev/null \
  | grep -o 'MEASURE:pg1=[^<]*' | head -1

echo "---- 0 em todas as paginas = nada cortado; positivo = overflow cortado por overflow:hidden ----"
