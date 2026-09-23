# Troca pontual num Google Doc via Docs API

Receita para mudar um trecho de um documento que precisa continuar igual em todo o resto.
Complementa a técnica de conversão markdown → Doc (`google-docs-formatting`), que é o
caminho de CRIAÇÃO; aqui é edição de documento existente.

## Sequência

1. `docs.documents().get(documentId=ID)` → percorrer `body.content` e localizar **por
texto** o parágrafo/célula/bloco. Anotar `startIndex`/`endIndex` de cada parágrafo (o
`endIndex` inclui o `\n` final).
2. **Batch 1 — conteúdo:**
   - troca de texto curto, inclusive dentro de célula de tabela:
     `replaceAllText` com `replaceAllText: {containsText: {text: S}, replaceText: R}`;
   - troca de bloco inteiro: `deleteContentRange` do range do bloco e `insertText` no
     índice inicial com o texto novo terminando em `\n` (um `\n` por parágrafo — mantém a
     mesma estrutura de parágrafos).
3. **Novo GET** (os índices mudaram) e **batch 2 — estilo:** `updateParagraphStyle`
   (`namedStyleType`) e `createParagraphBullets` para os parágrafos novos.
4. Verificação: export `text/plain` + diff contra o congelado; dump de
   `namedStyleType`/bullet por parágrafo; export PDF + `pdfinfo` + `pdftoppm` da página
alterada.

## Pitfalls de índice e estilo

1. **`replaceAllText` retorna `occurrencesChanged: 0` com texto aparentemente idêntico:**
   a comparação é byte a byte — traço comum × en dash, aspas retas × curvas, espaço normal
   × não-quebrável, acento precomposto × decomposto. Monte a string de busca a partir do
   que o documento devolveu, nunca redigitando de memória ou de um print.
2. **Conteúdo e estilo no MESMO batch:** todo índice posterior ao primeiro insert/delete
   anda, e o estilo acaba no parágrafo vizinho. Separe em dois batches com GET novo no meio.
3. **Parágrafo inserido nasce plano** (sem estilo, sem bullet) e, se cai logo antes de um
   heading, **herda o estilo do heading seguinte**. Reafirme o `namedStyleType` de destino e
   reaplique o bullet no batch 2.
4. **Range de estilo que encosta no heading de cima rebaixa o heading** para
   `NORMAL_TEXT` (sintoma: o título da seção anterior "perde a fonte de título"). Cobrir o
   parágrafo novo inteiro e nada antes dele.
5. **Range de parágrafo nunca inclui o `\n` final** (use `end - 1`): incluí-lo propaga o
   estilo ao parágrafo seguinte em cascata (style bleeding).
6. **`namedStyleType` não é transferível entre documentos:** a mesma seção lógica pode ser
   `HEADING_2` num doc e `HEADING_3` no irmão. Leia o nível dos parágrafos vizinhos do
   próprio documento.
7. **Bullet "solto"** (marcador visível sem o texto dentro do item) = range de
   `createParagraphBullets` desalinhado dos parágrafos novos; recalcule pelo GET.
8. **`endOfSegmentLocation` não serve para posicionar:** o índice resultante é
   imprevisível; use índice explícito.

## Leitura

`docs get` (wrapper) devolve texto com estrutura; para tabelas/células e estado de
checkboxes use a leitura via REST percorrendo `table` → `tableRows` → `tableCells` →
`content` — a leitura rasa mostra o documento como se estivesse vazio.
