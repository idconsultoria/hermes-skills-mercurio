# Verificação da peça final

A prosa só existe depois de o arquivo abrir certo. Rode esta sequência antes de dizer "pronto".

## 1. Renderizar o PDF

Caminho preferido neste host: o Chromium nativo do Termux, sem Node e sem Playwright:

```bash
chromium-browser --headless --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-pdf-header-footer \
  --print-to-pdf="$PWD/peca.pdf" "file://$PWD/peca.html"
```

O stderr enche de erro de dbus; o sinal de sucesso é a linha `N bytes written to file`. Se
`node -e "console.log(process.platform)"` responder `android`, Playwright não roda aqui; o Chromium
do cache do Playwright é glibc e pede `grun`.

**Se nenhum binário de browser resolver no host, use WeasyPrint.** É Python puro, não pede browser e
renderiza fielmente A4 com flex, SVG inline e `@font-face` em base64 — o mesmo HTML/CSS da peça:

```bash
python3 -c "from weasyprint import HTML; HTML(filename='peca.html').write_pdf('peca.pdf')"
pdfinfo peca.pdf | grep Pages
```

O que muda: sem browser não há sonda de `scrollHeight` (§2). A verificação passa a ser contagem de
páginas **mais** inspeção da faixa inferior de cada página (§3), porque a paginação do WeasyPrint
também respeita `break-after:page` do `.page`. Com WeasyPrint há caminho melhor que a sonda: medir a
árvore de caixas em Python (§2b).

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

## 2b. Medidor em milímetros (WeasyPrint)

Quando o PDF sai de WeasyPrint, a árvore de caixas fica acessível em Python: dá para dizer em
milímetros quanto cada página passa da linha do rodapé, em vez de julgar por captura de tela.

```python
from weasyprint import HTML
doc = HTML(filename='peca.html').render()
for i, pg in enumerate(doc.pages, 1):
    caixas = []
    def walk(b):
        caixas.append(b)
        for c in getattr(b, 'children', []) or []:
            walk(c)
    walk(pg._page_box)
    fundo = max(b.position_y + b.height for b in caixas if getattr(b, 'height', 0))
    rodape = pg.height - 20 * 96 / 25.4          # margem inferior em px
    print(f'pg {i}: excesso={(fundo - rodape) * 25.4 / 96:+.1f} mm')
```

Alvo: excesso negativo em todas as páginas, com folga de 2 a 5 mm. Folga acima de 20 mm também é
sinal — falta conteúdo ou a página ficou desequilibrada. **SVG e imagem não entram nessa conta**: o
medidor anda em caixas de bloco e de linha, e a altura de caixa substituída (figura, print) fica de
fora. Depois de inserir um diagrama ou um print, o excesso que o script imprime é falso — o portão
real é `pdfinfo | grep Pages` mais a faixa de tinta na base da página medida por pixel. Se a
contagem subiu, o desenho empurrou texto para outra página.

## 2c. Justificação: verifique por medição, não por visão

Com `text-align:justify` (e `hyphens:auto`, que precisa de `<html lang="pt-BR">` para acionar), as
linhas de um parágrafo fecham na mesma coordenada à direita; só as últimas linhas variam, e é correto
que variem.

```python
from collections import Counter
linhas = []
def walk(b):
    if type(b).__name__ == 'LineBox':
        linhas.append((round(b.position_x + b.width), b.element_tag))
    for c in getattr(b, 'children', []) or []:
        walk(c)
walk(doc.pages[2]._page_box)
print(Counter(x for x, t in linhas if t in ('p', 'li')).most_common(3))
```

Coordenada dominante repetida em muitas linhas = justificado de fato. **Não pergunte isso ao
`vision_analyze`**: ele olha a última linha do parágrafo, curta por natureza, e responde "está
alinhado à esquerda". Justifique `p` e a nota de abertura; tabela, célula e subtítulo seguem à
esquerda, onde o justificado abre buracos.

## 3. Contagem de páginas e conferência visual

```bash
pdfinfo peca.pdf | grep Pages
rm -f pg-*.png && pdftoppm -r 115 -png peca.pdf pg
```

**Contagem de páginas não prova que o texto coube.** Com `.page{height:297mm;overflow:hidden}` e o
rodapé posicionado em absoluto (`.foot{position:absolute;bottom:...}`), um parágrafo a mais não cria
página nova: ele passa por cima do rodapé e o `pdfinfo` continua dizendo 7. Sempre que acrescentar
texto a uma peça já fechada, olhe a **faixa inferior de cada página** no PNG — último parágrafo
encostando no filete do rodapé, texto sobreposto à numeração ou caixa de destaque invadindo a base.

Leia os PNG com `vision_analyze`, página por página, perguntando explicitamente: texto cortado,
sobreposição, logo renderizado, filete encostando em texto, espaço no fim da última página. Visão
pega o que a medição numérica não pega, e vice-versa. Pergunta que funciona: "os últimos 20% desta
página colidem com o rodapé?".

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

Antes de cortar, procure duplicata: parágrafo de posicionamento acrescentado no fim costuma repetir
o que já está no fecho ou na seção vizinha. Remover a repetição libera mais espaço do que qualquer
ajuste tipográfico e melhora a peça.

## 6. Paginação escrita à mão

Rodapé `n / N` e páginas do sumário são números digitados no script de build (`TOTAL = 8`,
`<td class="p">7</td>`). Ao mudar a paginação, atualize os dois na mesma rodada: senão o sumário aponta
para a seção errada e o leitor reclama do documento, não do texto.

```bash
pdfinfo peca.pdf | grep Pages
pdftotext peca.pdf - | tr '\n' ' ' | grep -o '5  Rito de gestão'   # página real da seção
pdftotext peca.pdf - | wc -w                                      # extensão
```

## 7. Célula de tabela com total e composição

Quando a célula mostra um valor e a conta que o origina, a ordem é **total primeiro** (corpo forte, na
fonte de título, `display:block`) e **composição abaixo** (cinza, 8,2 pt, entrelinha 1,45). O olho pega
o número e desce à conta só quando quer conferir; composição primeiro obriga a ler tudo para achar o
resultado.

## 8. Conferência do que o cliente já viu

Quando ele responde "ainda está lá" a um ajuste feito, meça antes de refazer: extraia o texto do PDF
entregue, procure o termo e, se não houver ocorrência, responda com a evidência e envie o arquivo de
novo — ele está olhando a versão anterior. Recompilar à toa desarruma o que já estava aprovado.

## 9. Figuras de produto no PDF (print de painel, link, QR)

Print de tela dá robustez à peça: prova que o modelo descrito existe em software. Sequência que
funciona:

1. **Confirme que o print é da versão que o cliente vê.** Compare o repositório local com o deploy
   (md5 de `index.html`, `app.js`, `data.js`, `styles.css`); se diferirem, capture do deploy ou faça o
   deploy antes. Print de build local apresentado como "o painel no ar" cai no primeiro clique.
2. **Capture em DPR 2 com o Chromium nativo**, sem Node:
   ```bash
   chromium-browser --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
     --force-device-scale-factor=2 --window-size=1240,1500 \
     --screenshot="$PWD/shots/pagina.png" "http://127.0.0.1:8917/index.html#/rota"
   ```
   Sirva o diretório local com `python3 -m http.server <porta>` em background; navegação por hash
   funciona direto na URL. Porta ocupada falha na hora — troque em vez de insistir.
3. **Recorte em lacuna, nunca por estimativa.** Ache as faixas de fundo vazio por linha de pixel:
   ```python
   a = np.asarray(Image.open('shots/pagina.png').convert('L')).astype(float)
   empty = (a > 248).mean(axis=1) > 0.995      # linha sem tinta
   ```
   Corte que atravessa um cartão é o defeito que o leitor percebe na hora ("a borda está serrada").
   **Termine o recorte na borda inferior do card** (filete + ícones), não logo depois da última
   palavra: sobra do título ou da sombra do bloco seguinte cortada ao meio é o que mais salta aos
   olhos. A borda se decide por pixel — última linha da imagem recortada sem tinta — e não por visão:
   depois de ver um recorte com sobra, o `vision_analyze` tende a afirmar que a sobra continua ali
   mesmo com a imagem limpa. Quando os dois discordarem, a medida manda; refaça um zoom 3x só da faixa
   dos últimos 120 px e pergunte apenas "há texto ou resto de card aqui?".

   Para print de estado interativo (modal, aba, filtro), não dependa de clique em sessão de browser:
   copie a página para um `_shot-*.html` temporário com um clique automático e capture com orçamento
   de tempo virtual.
   ```python
   inj = '''
   <script>window.addEventListener('load',function(){setTimeout(function(){
     var a=document.querySelector('[data-indicador="TUF"] [data-pay]'); if(a) a.click();
   },1200);});</script>
   </body>'''
   open('_shot-modal.html','w').write(open('index.html').read().replace('</body>', inj, 1))
   ```
   ```bash
   chromium-browser --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
     --force-device-scale-factor=2 --virtual-time-budget=6000 --window-size=1240,1400 \
     --screenshot="$PWD/shots/modal.png" "http://127.0.0.1:8917/_shot-modal.html#/operacao"
   ```
   Sem `--virtual-time-budget` a captura sai antes do clique. O modal tem fundo escurecido: ache o
   retângulo claro (máscara de brilho `a>240`, limiar de 25% das colunas/linhas) e recorte 4 px dentro
   da borda, senão a figura leva um bloco preto em volta. Apague o `_shot-*.html` no fim.

   Escolha a tela que prova um mecanismo, não a mais movimentada: a ficha de um indicador (definição,
   fórmula, regra de negócio, fonte do dado) sustenta mais que uma tabela de origem. E o recorte precisa
   conter o título da página — figura que começa no meio de uma fileira de cartões não diz de que tela
   veio.
4. **Pese a imagem.** JPEG qualidade 90 basta para print de UI e leva o PDF de ~2 MB para ~0,5 MB;
   embuta em base64 no HTML, como as fontes.
5. **QR + endereço em bloco de tabela.** `pip install qrcode`, gere com a cor da marca
   (`fill_color='#0A1929'`), 18 mm de lado, ao lado do endereço em corpo de título e de uma linha
   dizendo o que abre. Tabela de duas células funciona no WeasyPrint; flex é instável.
6. **Legende e numere:** "Figura N." em negrito de título seguido do que a figura *prova*, não do que
   ela mostra. Figura sem legenda vira ilustração decorativa.
7. **Rótulo de dado fictício na própria imagem.** Se o painel já traz a tarja, ela aparece no print e
   resolve; se não, escreva na legenda.

**Emoji no título de página capturada não é defeito do produto:** o harness de browser injeta
marcador no `<title>`. Antes de reportar, abra o `index.html` do repositório e confira o título real.
