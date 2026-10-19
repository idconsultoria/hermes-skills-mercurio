# Botão "Exportar PDF" dentro do próprio site (html2pdf / html2canvas)

Quando a entrega não é um documento para renderizar no host, e sim **um site que precisa
ofertar o PDF de cada tela ao visitante** (peça de apresentação, entrega de cliente).
O pipeline é outro: `html2pdf.js` (bundle de html2canvas + jsPDF) rodando no navegador.

Regra de ouro: **o arquivo é a evidência, não a promise.** O `save()` do html2pdf engole
exceção no `catch` próprio; a promise resolve "com sucesso" e nenhum PDF é gerado. Sempre
confirme um artefato (blob criado, download concluído, páginas no arquivo).

## Armadilhas que invalidam a exportação (silenciosamente)

- **CSS moderno mata o html2canvas.** `color-mix()`, `oklch()`, `color(display-p3 …)` fazem o
  parser abortar com `Attempting to parse an unsupported color function`. Use `rgb()/rgba()/hex`
  literais. Se a cor precisa variar por variante (setor, tema), exponha uma custom property com
  o **literal** por variante (`--sector-line: rgba(…,0.55)`) em vez de calcular com `color-mix()`.
  Antes de entregar, `grep` o CSS do projeto por `color-mix|oklch|light-dark|color(` — é rápido
  e evita descobrir na frente do cliente.
- **Não passe `windowWidth`/`windowHeight` ao capturar um elemento.** Essas opções deslocam o
  recorte: telas curtas saem **em branco** (0% de tinta). Deixe o html2canvas dimensionar pela
  própria seção; o tamanho do alvo se controla por CSS.
- **A subárvore capturada precisa estar em fluxo normal.** Tela de site cinematográfico costuma
  ser `position: fixed; inset: 0; height: 100vh` com o conteúdo centralizado — capturada assim,
  o PDF sai com meia página vazia. Crie um modo de impressão com uma classe na raiz
  (`html.pdf-export`) que flipa para `position: static; height: auto; display: block; opacity: 1`
  e force `.reveal`/animações visíveis. Isso **não** contradiz a regra de "não alterar layout no
  print" dos documentos: num site full-screen o print *precisa* de um modo próprio, senão não
  há conteúdo em fluxo para capturar.
- **Conteúdo longo estoura o canvas.** Acima de ~9.000 px de altura, escala 2 passa do limite de
  dimensão do canvas (~32k px) e falha. Escolha a escala pelo tamanho medido
  (`el.scrollHeight > 9000 ? 1 : 2`).
- **Carrossel/horizontal track captura uma faixa enorme.** Se os itens estão lado a lado num
  track transladado, a captura vira uma faixa de dezenas de milhares de px de largura e o PDF
  sai quase vazio. No modo impressão, empilhe: `display: block; width: 100%` no track e nos
  itens, `transform: none`, `overflow: visible` no viewport.
- **Página final em branco.** `page-break-after: always` na seção capturada gera uma página
  extra; use `auto`. E mantenha `pagebreak.mode: ['css','legacy']` — só `['css']` fez o conteúdo
  desaparecer (páginas com ~4% de tinta em vez de ~43%).
- **Página órfã com pouco conteúdo.** Blocos pequenos (rodapé, último card) quebram sozinhos;
  `pagebreak.avoid` nos blocos internos (`tr`, cartão, tabela) reduz, mas não elimina — se
  sobrar, é cosmético: relate em vez de inventar corte de conteúdo.

## Verificação com números (não com olho)

```bash
pdfinfo out.pdf | grep Pages                      # contagem
pdftoppm -png -r 40 out.pdf pg                   # renderiza páginas
python3 -c "from PIL import Image; im=Image.open('pg-1.png').convert('L'); \
px=list(im.getdata()); print('%.2f%%' % (100*sum(1 for v in px if v<245)/len(px)))"
```

- 0% de tinta = página em branco; ~30–45% em página densa é normal; fundo escuro vazando daria
  ~85%+ (background escuro no PDF = modo impressão não aplicado).
- Confira **a primeira, uma do meio e a última** página de documento longo.
- Para provar que a geração aconteceu sem esperar download, instrumente
  `URL.createObjectURL` e leia `{type, size}` do blob.
- Para ver a exceção real, avalie dentro da página e capture o `catch` como string
  (`outputPdf('blob')` em vez de `save()`); foi assim que o erro de CSS apareceu em uma linha.
- Ao testar várias telas em sequência, use **uma sessão de navegador por tela**: a política de
  download automático do Chrome bloqueia o segundo arquivo e o sintoma parece bug do site.

## Contrato de uso no site

- Um botão por tela, cada um exportando **o seu** arquivo A4 (nome versionado: `-1-apresentacao`,
  `-2-mapa…`), com fundo branco forçado (`backgroundColor: '#FFFFFF'`) e a paleta clara do modo
  impressão, para o PDF não sair com tema escuro.
- O botão só aparece nas telas que fazem sentido como documento; a tela de abertura costuma ficar
  sem botão de propósito.
- Botão de exportação é controle como qualquer outro: ao revisar, clique e **confirme o
  arquivo** (nome, páginas, tinta) — "cliquei e nada aconteceu" é o modo de falha mais comum
  desta feature.
