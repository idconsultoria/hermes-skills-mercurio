---
name: doc-brand-theming
description: "Use ao aplicar identidade de marca em Google Doc."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [google-docs, marca, identidade-visual, batchupdate, contrato, proposta]
    related_skills: [google-docs-formatting, google-workspace, contrato-prestacao-servicos-b2b]
type: ToolIntegration
timestamp: 2026-11-03T00:00:00Z
---

# Identidade de marca num Google Doc (pós-conversão)

Quando o documento tem de sair na identidade de um **cliente ou parceiro** — preto e vermelho de
uma agência, paleta de um cliente institucional — e não no padrão do conversor. O documento é
convertido primeiro (`md-to-gdoc.py`) e **temado depois** por um script de `batchUpdate`
idempotente, que pode ser re-rodado a cada correção de conteúdo sem duplicar efeito.

## Ordem de trabalho

1. `md-to-gdoc.py arquivo.md --title "..." --parent <PASTA>` — cria estrutura e conteúdo.
2. Script de tema (`templates/theme_doc.py`) — cores, fontes, tabelas, assinatura, margens.
3. Exportar PDF: `drive download <id> --export-mime application/pdf --output x.pdf`.
4. Verificar: `pdfinfo` (páginas, A4), `pdffonts` (fontes do tema embutidas), `pdftotext -f N
   -l N` por página (quebras, página órfã) e o JSON do doc para conferir tabela por tabela.
5. Criar a pasta do cliente no Drive antes de converter e passar `--parent` — documento de
   cliente não nasce na raiz.

## Regras de offsets

- Classifique cada parágrafo por `paragraph.paragraphStyle.namedStyleType` (TITLE / HEADING_1 /
  HEADING_2 / NORMAL_TEXT) a partir de um único GET.
- Pule parágrafos com `endIndex - startIndex <= 1`.
- Todo range de estilo de parágrafo termina em **`endIndex - 1`**: incluir o `\n` propaga o
  estilo ao parágrafo seguinte em cascata.
- Aplicar estilo **não insere nem apaga texto** — os índices do GET inicial continuam válidos e
  as requisições podem ir em lotes de ~60 sem recalcular.
- Lotes de `batchUpdate` são **tudo-ou-nada**: um enum inválido derruba o lote inteiro. Rode o
  script inteiro de novo após corrigir; nada fica pela metade justamente porque é idempotente.

## Gotchas da API (custam tempo)

1. **`table["rows"]` é `int`.** Itere `table["tableRows"]` (linhas) e `row["tableCells"]`.
   `table["rows"][0]` devolve `TypeError: 'int' object is not subscriptable`.
2. **`updateTableRowStyle` usa `tableStartLocation` + `rowIndices` (lista).** Mandar
   `tableRange` devolve `Invalid JSON payload ... Unknown name "tableRange"`. Já
   `updateTableCellStyle` **usa** `tableRange` com `tableCellLocation{tableStartLocation,
   rowIndex, columnIndex}` + `rowSpan`/`columnSpan`.
3. **Enum de alinhamento é `JUSTIFIED`**, não `JUSTIFY`. Válidos: `START`, `CENTER`, `END`,
   `JUSTIFIED`.
4. **`keepLinesTogether: true` nos parágrafos das células** impede a linha de tabela quebrar no
   meio da página — sem isso o PDF corta uma célula em duas páginas.
5. **Corrigir paginação sem regenerar o documento:** `updateParagraphStyle` com
   `pageBreakBefore: true` no parágrafo do título da seção.
6. **`docs get` inventa uma linha `| 1 | 2 | 3 |` antes do cabeçalho real** ao serializar
   tabelas. Não conclua que há linha-lixo: confira em `tableRows[0].tableCells[].content[].
   paragraph.elements[].textRun.content`.
7. **Texto branco sobre cor de marca:** ao pintar o cabeçalho de uma tabela, aplique
   `updateTableCellStyle` (backgroundColor) **e** `updateTextStyle` (branco, bold, ~9,5 pt) na
   mesma linha; preto sobre vermelho escuro é ilegível.

## Bloco de assinaturas em doc temado

- No markdown, a primeira linha da tabela é o cabeçalho: use-a **vazia** (`| | | |`) para
  reservar espaço de assinatura.
- Detecte essa tabela pelo primeiro caracter da primeira célula vazio e trate diferente: sem
  faixa colorida, `alignment: START`, `spaceAbove/spaceBelow = 0`.
- Bordas brancas 1pt nas quatro laterais de todas as células = grade invisível; cor de borda tem
  **duas camadas** (`borderTop: {color: {color: {rgbColor: {...}}}, width, dashStyle}`).
- `updateTableRowStyle` com `minRowHeight` ~42 pt na linha vazia superior dá espaço real para
  caneta.
- Feche a seção com heading próprio (`## ASSINATURAS`), com a data **antes** da tabela, e
  `<!-- pagebreak -->` antes do heading — sem isso a tabela de assinatura sozinha cai na página
  seguinte, separada do fecho do contrato.

## Fontes e página

- `Montserrat` (títulos, bold) + `Inter` (corpo 10,5 pt) existem no Google Docs e saem embutidas
  no PDF — confirme com `pdffonts`. Um `ArialMT` residual costuma ser só o glifo do bullet.
- `updateDocumentStyle` com `pageSize` A4 (595,3 × 841,9 pt) e margens em PT (2,2 cm ≈ 62 pt;
  2,3 cm ≈ 65 pt), com `fields` listando todas as propriedades alteradas.

## Pitfalls

1. **Declarar pronto sem conferir paginação no PDF.** Fonte e cor certas com o bloco de
   assinatura órfão na página seguinte é entrega errada. Rode `pdftotext -f/-l` página a página.
2. **Julgar tabela pelo `docs get`.** O extrator injeta a linha numerada fantasma; conferir no
   JSON evita "corrigir" uma tabela que estava certa.
3. **Temar antes de terminar o conteúdo.** Cada correção de texto exige re-temar; por isso o
   script precisa ser idempotente.

## Arquivos

- `templates/theme_doc.py` — script base de tema (classificação por estilo, fontes, faixa de
  cabeçalho de tabela, bloco de assinatura, A4, idempotente): copiar, trocar a paleta e os nomes
  de fonte, rodar com o `doc_id`.
