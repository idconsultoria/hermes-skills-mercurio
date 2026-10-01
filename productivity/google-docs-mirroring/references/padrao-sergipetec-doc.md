# Exemplo trabalhado: DNA do documento institucional do SergipeTec

Modelo de como ler o DNA de um Doc de referência e o que resultou na prática. Serve
tanto para reescrever documentos do Parque quanto como roteiro de leitura para
outro cliente (troque os valores lidos).

## O que ler no Doc de referência

```
# por run
paragraph.elements[].textRun.textStyle.weightedFontFamily.fontFamily   -> fontes reais
paragraph.elements[].textRun.textStyle.fontSize.magnitude              -> quando explícito
paragraph.elements[].textRun.textStyle.foregroundColor.color.rgbColor  -> cores
# por estilo nomeado (herdado por run sem valor explícito)
namedStyles.styles[].textStyle.fontSize / weightedFontFamily
# por parágrafo
paragraphStyle.namedStyleType / lineSpacing / spaceAbove / spaceBelow
# documento
documentStyle.pageSize / marginTop / marginBottom / marginLeft / marginRight
# tabelas
tableRow.tableCells[].tableCellStyle.paddingTop/Bottom/Left/Right + backgroundColor
# capa
inlineObjects (imagens) + elementos de paragraph sem tipo conhecido (desenho)
```

`pdffonts` no PDF exportado confirma o que o leitor realmente vê (run sem fonte
explícita aparece com a fonte do estilo nomeado).

## DNA do documento do Parque (lido do Doc de referência)

| Elemento | Valor |
|---|---|
| Corpo do texto | **Nunito Sans 11pt**, entrelinha 115%, 8pt abaixo de cada parágrafo |
| Títulos | **Calibri** azul `#2E74B5` — H1 16pt, H2 13pt, H3 12pt |
| Texto de tabela | **Calibri 11pt**, cabeçalho em negrito, borda preta fina |
| Capa | página desenhada (fundo escuro + gráfico), logo do Parque, selo em **Montserrat 10pt verde**, título em **Montserrat 28pt** (branco + verde), bloco navy 1×1 com o resumo do programa em azul-claro |
| Página | A4, margens de 72pt em todos os lados |
| Cabeçalho | logo à esquerda + título do projeto à direita, com linha azul |
| Rodapé | identificação do documento + campo de página (“Página X de Y”) |

Como o corpo é Nunito Sans e as tabelas/títulos herdam Calibri, o resultado tem
duas famílias convivendo — é o padrão do documento, não um erro a corrigir.

## Calibração de páginas na prática

Mesma densidade de conteúdo, alavancas aplicadas em sequência e páginas obtidas:

| Configuração | Páginas |
|---|---|
| conversão crua (fonte 11pt, margens 72pt, espaçamento padrão) | 15 |
| + corpo 9pt e espaçamento reduzido | 11 |
| + padding de célula 1,5pt (só tabelas) | 10 |
| + corpo 8,6pt, títulos ajustados, padding 1pt | 9 |

Leitura: **padding de célula foi a maior alavanca isolada** (com 16 tabelas), e
fonte/espaçamento rendem ~30% de páginas. Com o padrão do Parque mantido (11pt), a
mesma proposta ocupa ~19 páginas — confira o teto contratual do cliente antes de
“otimizar” e informe o número real.

## Entrega

Cópia do Doc de referência na pasta de trabalho da proposta, conteúdo escrito na
cópia, capa/cabeçalho/rodapé preservados, logo temporária subida apenas para a
inserção da capa (permissão revogada e PNG na lixeira depois).
