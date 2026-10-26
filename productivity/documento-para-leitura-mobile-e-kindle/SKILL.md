---
name: documento-para-leitura-mobile-e-kindle
description: "Edição de leitura de documento: HTML mobile + EPUB/Kindle, texto integral.

Carregue esta skill quando o pedido for 'versão facilitada para leitura em celular', 'versão para Kindle', 'EPUB', 'transformar esse PDF em leitura confortável', edição de leitura de documento denso (manifesto, estatuto, contrato, relatório, capítulo) ou quando o PDF enviado não tiver camada de texto extraível. Produz um par por documento (HTML + EPUB) a partir do mesmo modelo JSON, com verificação de fidelidade em três gates."
trigger: Pedido de 'versão facilitada para leitura em celular', 'versão para Kindle', 'EPUB', 'transformar esse PDF em leitura confortável', ou quando o PDF enviado não tem texto extraível.
related_skills: [html-to-pdf-chromium, pdf, html-pdf-fidelity, revisao-entrega-cliente, documento-a4-marca-id]
type: Orchestrator
timestamp: 2026-10-26T00:00:00Z
---

# Documento → leitura mobile (HTML) e eBook (EPUB/Kindle)

Produzir uma **edição de leitura** de um documento já existente: mesmo conteúdo, tipografia e
estrutura pensadas para tela pequena, entregue como HTML (navegador do celular) e EPUB (Kindle).

## Quando usar

- "Gere uma versão facilitada para leitura no celular" / "manda em EPUB pro Kindle".
- Acervo longo demais para PDF A4 refletido em tela (manifestos, estatutos, leis, relatórios).
- Entrega recorrente de leitura (capítulos, newsletters) — o gerador de EPUB é reutilizável
  e não depende do documento.

## Regras que valem em toda entrega

1. **Nada é contraído.** Texto integral: todos os artigos, itens, parágrafos, listas de nomes,
   índices, anexos e assinaturas. "Facilitada para a leitura" quer dizer *conforto*, não *resumo*.
2. **Fidelidade vence correção.** Erros do documento original (numeração repetida, remissão a
   artigo errado, sigla trocada, concordância) ficam **como estão impressos**. Corrija só ruído de
   digitalização e declare o que corrigiu numa **nota de edição** no fim do arquivo.
3. **Entrega em dois formatos.** HTML (leitura no navegador) + EPUB (Kindle), enviados por
   `MEDIA:/caminho/absoluto`. Ofereça no fim PDF A4 paginado ou um volume único com vários documentos.
4. **Design system simples, focado em legibilidade.** Coluna única (`max-width` ~34em), corpo 18–19px,
   `line-height` 1.65–1.72, hierarquia por rótulo + peso (não por blocos coloridos), **um** acento de cor,
   modo escuro automático (`prefers-color-scheme`), sumário recolhível em `<details>`, botão "voltar ao topo".
   Zero emoji, zero nota interna, zero numeração inventada.
5. **Página de capa/divisória do original não vira capítulo.** Ela vira o cabeçalho da edição; folhas em
   branco desaparecem.

Comece o HTML por `templates/leitura-mobile.html` — CSS completo (tipografia, cartões numerados, sumário,
modo escuro, print) e marcadores de onde o conteúdo entra.

## Pipeline

1. **Extrair texto**
   ```bash
   mkdir -p $HOME/tmp            # /tmp NÃO existe neste Termux
   pdftotext -layout doc.pdf ~/tmp/doc.txt && wc -c ~/tmp/doc.txt
   pdfinfo doc.pdf | grep -E 'Pages|Page size'
   ```
   Leia o `.txt` inteiro antes de parsear. Se vier com poucos bytes e só `\f`, o PDF **não tem camada
   de texto** (comum em arquivo de Illustrator/InDesign com texto em curvas): siga
   `references/ocr-pdf-sem-camada-de-texto.md`.
2. **Normalizar** em script Python (nunca editando à mão): remover cabeçalho/rodapé repetido e número de
   página, fechar parágrafos, desfazer hifenização quebrada, consertar ruído sistemático de OCR.
   Identifique a **mobília de página** (cabeçalho repetido, rodapé numerado, filetes) e os **padrões
   estruturais** (títulos romanos, itens numerados, alíneas). Receita: `references/segmentacao-de-texto-pdf.md`.
3. **Estruturar em blocos, não regex ad-hoc por seção.** Duas etapas: (a) linhas → parágrafos;
   (b) parágrafos → estrutura (título, item, subitem, prosa). Grave o resultado como **modelo JSON**
   e **só depois** gere as saídas — HTML e EPUB saem do mesmo modelo, o que impede divergência
   entre formatos. Corretor de segmentação se resolve no parser, não em cada saída.
4. **Verificar fidelidade antes de desenhar.** Comparação de multiconjunto de palavras entre fonte e
   texto renderizado (HTML e EPUB):
   ```python
   from collections import Counter
   import re
   def words(s): return Counter(re.findall(r'\w+', s.lower()))
   ```
   Diferença esperada = só (a) mobília removida, (b) correções de OCR/ortografia, (c) dígitos que
   viraram `<ol>`/badge. **Palavra de conteúdo faltante é bug de parser** — corrija antes de seguir.
5. **Renderizar** HTML (template) e **EPUB** (`scripts/build_epub.py`, ou `references/epub-kindle-manual.md`
   para a versão sem dependências).
6. **Verificar de verdade** com os três gates de `references/verificacao-de-fidelidade.md`: todo bloco do
   modelo presente no HTML e no EPUB, EPUB com XML válido, screenshot em 390px conferido com visão.
7. **Entregar** os arquivos + 2 a 4 linhas dizendo o que foi feito, o que foi corrigido e o que foi preservado
   do original.

### HTML de leitura (celular)

- `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`.
- Coluna única, `max-width: 36em`, corpo 18px, `line-height: 1.7`. Nunca duas colunas.
- Títulos com kicker ("SEÇÃO 3"/"PRINCÍPIO VI") e itens longos em cartão com número circular.
- Índice recolhível no topo (`<details>` com links âncora) e botão flutuante de voltar ao topo.
- `@media (prefers-color-scheme: dark)` com fundo navy e texto claro; `theme-color` navy.
- Sem JS além do mínimo (fechar o índice); nenhuma fonte externa — quem lê está no celular,
  offline ou em rede ruim.
- Prosa corrida **não** vai dentro de cartão: só o primeiro parágrafo como destaque; os demais
  em prosa com respiro (`margin-bottom: 1.2em`). Cartão em tudo vira parede de texto.

### EPUB (Kindle)

```bash
python scripts/build_epub.py chapters.json saida.epub
```

EPUB 3 + NCX (Kindle antigo) + capa JPEG + sumário. O JSON tem `title`, `subtitle`, `cover_line`,
`author`, `chapters[{title, kicker, html}]` e `notes[]`. O script valida o XML de cada capítulo,
confere o `mimetype` (primeiro e sem compressão) e reporta tamanho, arquivos e capítulos.

- **Subconjunto seguro de marcação:** `<p>`, `<ul>`, `<li>`, `<ol>`, `<h1>`, `<h2>`, `div` só
  para caixas simples. Nada de flex/grid, badge posicionado ou `<p>` aninhado.
- **Um capítulo por seção** — o sumário do Kindle é a navegação real do leitor.
- **Capa sem metadado:** título grande, sigla curta no topo, uma linha de assunto. Contagem de
  páginas, nome da entidade repetido e nome completo duplicado **não** entram.
- Nota de edição (transcrição integral + correções aplicadas) no último capítulo.

### Renderizar e conferir o pixel

Descubra o binário do Chromium (o caminho muda entre migrações do host):

```bash
command -v chromium-browser chromium google-chrome 2>/dev/null
CHROMIUM=/data/data/com.termux/files/usr/bin/chromium-browser
"$CHROMIUM" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --hide-scrollbars --window-size=390,14000 \
  --screenshot=$HOME/tmp/full.png "file://$PWD/pagina.html"
```

- `--window-size=390,H` = viewport de celular; `H` alto captura o documento inteiro.
- Abra a imagem e inspecione **regiões** (crop), não a página longa inteira em escala 1.
- Para o EPUB, além do XML: extraia `OEBPS/ch*.xhtml`, tire as tags e rode a mesma comparação
  de palavras da etapa 4; procure restos de marcação (`class="badge"`, `</p></p>`, `<div`).
- Navegação por âncora (`#secao`) não posiciona a captura de forma confiável; use imagem longa
  + crop. Área vazia no topo é posição de scroll, não bug de CSS.

### Entrega

Nomeie com o documento e o destino (`Documento-leitura-celular.html`, `Documento-Kindle.epub`),
um par por documento. Diga em uma linha o que mudou e o que foi corrigido do original. Anexe
arquivos, não pasta.

## Pitfalls que custam retrabalho

- **`read_file` devolve `N|` na frente de cada linha.** Nunca leia com `read_file` e reescreva com `write_file`:
  o prefixo entra no conteúdo e corrompe o arquivo. Edite com `patch`; para reescrever, gere do zero.
  Se já corrompeu, limpe com `re.sub(r'(?m)^\s*\d+\|', '', s)` antes de qualquer outra coisa.
- **Caput truncado por quebra de linha.** A continuação do texto depois de `Art. N.` só é capturada se a regra
  for "existe bloco aberto?", e não "a linha anterior era um artigo" — com a segunda forma, todo o resto do
  caput desaparece em silêncio.
- **`§` e romanos são o ruído nº 1 do OCR:** `§` sai como `8`, `$`, `&`, `£`, `8§`; `I` sai como `|`, `l`, `1`;
  `II`/`III` como `Il`/`Ill`/`HI`/`IM`. A regex de inciso **precisa aceitar `V` isolado**: alternância com
  `VI{1,3}` e sem `V` perde todos os incisos V sem nenhum erro visível.
- **`§` colado no meio da linha** (`...regulamentar. &£ 5º. Todos...`) precisa virar parágrafo novo, mas só
  quando vem depois de fim de frase (`[.;:!?]`); separar sempre quebra remissões do tipo "na forma do § 1º".
- **Sequência de incisos é prova de leitura.** Se o OCR der `I, II, II, IV` ou faltar numeral, reconte os itens:
  quando a quantidade casa com a sequência canônica, renumere `I..N`; quando não casa, confira na imagem.
  Numeral repetido **do original** não se corrige.
- **Numeral romano crítico se confere na imagem, não no OCR.** `vision_analyze` com `region` na faixa dos incisos,
  pedindo transcrição literal "sem corrigir a numeração", resolve em uma chamada.
- **Título vem na mesma linha do corpo** em PDF diagramado (`I - O Trabalhismo Democrático - O Trabalhismo…`).
  Separe no segundo ` - ` e jogue o resto como prosa; trate também a variante com ponto (`VIII. Título - corpo`).
- **Mobília de página não é conteúdo:** remova cabeçalho/rodapé repetido antes de contar palavras, senão a
  verificação de fidelidade mente nos dois sentidos.
- **Bloco partido por quebra de página:** a regra "fecha parágrafo no ponto final" resolve a maioria, mas lista
  com `;` continua acumulando — junte os blocos da lista antes de extrair itens (foi assim que uma lista de
  nomes saiu truncada).
- **Badge perdido na conversão:** ao passar HTML de cartões para EPUB, reescreva o item em
  `<p class="item"><span class="num">N</span> texto</p>` em vez de mutar o HTML de cartão — trocar `</div>`
  por `</p>` gera `<p>` aninhado e o Kindle renderiza errado.
- **Fonte remota em EPUB:** o Kindle ignora/atrasa webfont; use `serif`/`sans-serif` do sistema.
- **`pkill -f <binário>` derruba a própria sessão** quando o padrão casa com o wrapper que executou o comando.
  Encerre por PID.
- **Validar layout sem ver a imagem não conta.** Screenshot na largura do aparelho + `vision_analyze` antes de
  declarar pronto: "muralha de texto", cartão vazio, sobreposição e botão cobrindo linha só aparecem no pixel.
- **Declarar pronto sem abrir o arquivo:** EPUB válido = `mimetype` primeiro e sem compressão + XML válido +
  capa presente + capítulos no spine.

## Referências

- `references/ocr-pdf-sem-camada-de-texto.md` — OCR de PDF vetorial: instalação, dpi, `--psm`, traineddata,
  dicionário de correções e conferência por página.
- `references/segmentacao-de-texto-pdf.md` — linhas → parágrafos → estrutura; mobília de página e título na
  mesma linha do corpo.
- `references/epub-kindle-manual.md` — EPUB 3 + NCX sem dependências, capa com PIL, CSS seguro para Kindle,
  validação por XML.
- `references/verificacao-de-fidelidade.md` — os três gates de integridade (bloco a bloco, EPUB, visual).
- `templates/leitura-mobile.html` — HTML mobile pronto (CSS + sumário recolhível + modo escuro).
- `scripts/build_epub.py` — gerador de EPUB 3 + NCX a partir de `chapters.json`.
