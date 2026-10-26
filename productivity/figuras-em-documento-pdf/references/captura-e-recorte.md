# Captura e recorte de prints de app

## 1. Servir e capturar

```bash
# servidor local em background, porta alta, loopback
cd <dir-do-app> && python3 -m http.server 8917 --bind 127.0.0.1 &

CHROME=/data/data/com.termux/files/usr/lib/chromium/chrome
$CHROME --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
  --force-device-scale-factor=2 --window-size=1240,1500 \
  --screenshot="$PWD/shots/pagina.png" "http://127.0.0.1:8917/index.html#/rota"
```

- A CLI entrega PNG determinístico em 2x, sem sessão interativa: é o caminho preferido para figura. Se precisar de
  geometria de elementos, tente medir por JS uma vez; se a página for pesada e a chamada demorar, siga para análise
  de pixel — o recorte não depende de geometria.
- `--window-size` é altura capturada em px CSS. Área abaixo do fold: aumente a altura (ex.: `1240,3400`) e recorte
  depois; não existe scroll por CLI.
- Rotas por hash funcionam direto na URL (`#/visao-geral`, `#/operacao`, `#/fontes`).

## 2. Estado interativo (modal, aba, filtro)

Cópia temporária da página com clique automático:

```python
s = open('index.html').read()
inj = '''
<script>window.addEventListener('load',function(){setTimeout(function(){
  var a=document.querySelector('[data-indicador="TUF"] [data-pay]'); if(a) a.click();
},1200);});</script>
</body>'''
open('_shot-modal.html','w').write(s.replace('</body>', inj, 1))
```

```bash
$CHROME --headless=new --disable-gpu --hide-scrollbars --no-sandbox --force-device-scale-factor=2 \
  --virtual-time-budget=6000 --window-size=1240,1400 \
  --screenshot="$PWD/shots/modal.png" "http://127.0.0.1:8917/_shot-modal.html#/operacao"
```

Sem `--virtual-time-budget` a captura sai antes do clique. Confira o PNG com visão ("o modal está aberto?") antes de
seguir. Apague o `_shot-*.html` no fim: não deixe arquivo de captura no diretório do app.

## 3. Provar que a captura é o que o cliente vê

```python
import urllib.request, hashlib
for nome in ('index.html','app.js','data.js','styles.css'):
    d = urllib.request.urlopen('https://<deploy>/'+nome, timeout=25).read()
    l = open('<dir-do-app>/'+nome,'rb').read()
    print(nome, 'igual' if hashlib.md5(d).hexdigest()==hashlib.md5(l).hexdigest() else 'DIFERENTE')
```

Divergiu: capture do deploy ou atualize o local antes de imprimir. Título estranho no `document.title` durante
a automação costuma ser artefato do harness, não do app — confirme lendo o HTML servido.

## 4. Recorte

```bash
python3 scripts/faixas_de_tinta.py shots/pagina.png --de 300 --ate 1800
python3 scripts/faixas_de_tinta.py shots/pagina.png --zoom-base 120 --saida-zoom /tmp/base.png
```

- Comece **antes do título da tela**; termine na borda inferior do card.
- Faixas vizinhas enganam: o bloco seguinte pode ter título na faixa A e subtítulo na faixa B, separados por 20 px.
  Recorte no vão posterior à faixa que você reconhece como fim do seu bloco.
- Modal: retângulo claro por máscara de brilho — `(a>240)` com limiar de 25% das colunas/linhas — e recorte 4 px
  dentro da borda.

## 5. Verificação do corte

1. **Pixel:** `(np.asarray(img.convert('L'))<200).sum(axis=1)` — primeira e última linhas da figura recortada com zero.
   O limiar 200 não pega borda clara de card nem sombra; use `<235` quando quiser ver qualquer tom.
2. **Zoom:** recorte os últimos 120 px, amplie 3x e pergunte apenas "há texto ou resto de card aqui?".

A visão ancora: se ela viu um recorte com resto de card antes, tende a repetir que o resto está lá. Quando pixel e
visão discordarem, a medida manda; refaça o zoom da faixa isolada para encerrar a dúvida.

## 6. Embutir

```python
from PIL import Image
Image.open('shots/recorte.png').convert('RGB').save('fig-tela.jpg', quality=90, optimize=True)

def b64img(path):
    import base64, os
    return base64.b64encode(open(os.path.join(BASE, path), 'rb').read()).decode()
```

```html
<div class="fig" style="width:154mm;margin:4mm auto 1mm">
  <img src="data:image/jpeg;base64,{FIG_TELA}" alt="..."/>
</div>
<div class="figcap" style="max-width:154mm"><b>Figura 1.</b> O que a figura prova.</div>
```

```css
.fig img{display:block;width:100%;border:.5pt solid var(--hair)}
.figcap{font-size:8.2pt;line-height:1.45;color:var(--quiet);margin-top:2mm}
```

## 7. QR de link

```python
import qrcode
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=1)
qr.add_data('https://<url>'); qr.make(fit=True)
qr.make_image(fill_color='#0A1929', back_color='#FFFFFF').convert('RGB').save('qr.png')
```

Bloco em tabela (não flex): `td.q` de 20 mm com o QR e a segunda célula com rótulo em caixa alta 7,4 pt, URL em
10,4 pt e uma linha de descrição. Borda só em cima e embaixo (`.5pt solid hair`), sem caixa.
