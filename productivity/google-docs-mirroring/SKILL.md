---
name: google-docs-mirroring
description: "Use when reescrever um Google Doc no padrão do anterior."
version: 1.0.0
author: Hermes curator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [google-docs, espelhamento, formatacao, entrega, pdf, paginacao]
    related_skills: [google-workspace, google-docs-formatting, proposta-sergipetec-documento]
type: Orchestrator
timestamp: 2026-09-30T00:00:00Z
---

# Reescrever um Google Doc no padrão de outro

Classe de trabalho: **“faça uma vN a partir de uma cópia do documento anterior”, “deixe no exato mesmo
padrão do GDoc anterior”** — trocar o conteúdo de um documento mantendo integralmente a apresentação do
original (capa, timbrado, cabeçalho, rodapé numerado, fontes, tamanhos, tabelas) e fazendo o resultado
caber num orçamento de páginas.

## Procedimento

1. **Clonar, não recriar.** `drive.files().copy(fileId=REF, body={"name": ..., "parents": [PASTA]})`.
   A cópia leva capa, imagens embutidas, cabeçalho, rodapé (com o **campo** de número de página), A4 e
   margens. Recriar do zero perde tudo isso — e o campo de página não volta pela API.
2. **Achar a fronteira capa × corpo:** varrer `body.content` e pegar o `endIndex` do **segundo** elemento
   `sectionBreak` (o primeiro é a seção 0–1 do documento).
3. **Reescrever só o corpo.** `md-to-gdoc.py --doc-id` apaga de `[1, end-1]` e destrói a capa: copie o
   script para o diretório de trabalho e faça o início da deleção vir de um env (`KEEP_UNTIL`), deletando
   `[KEEP_UNTIL, end-1]`. Assim o fim do documento passa a ser a própria capa e o caminho normal do
   conversor (inserir no fim) escreve exatamente depois dela.
4. **Ler o DNA do original antes de aplicar estilo:** fontes dos runs
   (`textStyle.weightedFontFamily`), tamanhos efetivos (`namedStyles.styles[TIPO].textStyle.fontSize` — run
   sem size herda daqui), cores de título, `lineSpacing`/`spaceAbove`/`spaceBelow`, `documentStyle.margin*`
   e `tableCellStyle.padding*`. Reproduza os valores lidos; não invente a partir do HTML de origem.
5. **Negrito: conferir depois de converter.** Conte runs com `textStyle.bold is True`. Negrito inline que
   não sobreviveu à conversão não avisa — reaplique a partir do markdown de origem (item 7 dos pitfalls).
6. **Calibrar páginas** medindo pelo **PDF exportado do Doc** (`files.export` + `pdfinfo`), nunca pelo HTML:
   a paginação do Google Docs é própria. Ordem de eficácia: padding de célula → tamanho de fonte →
   espaçamento (spaceAbove/spaceBelow, lineSpacing) → margens. Um ajuste por vez, medindo entre eles.
7. **Conferir com visão** nas páginas-chave (capa, tabela grande, última) via `pdftoppm -png` +
   `vision_analyze`: corte, sobreposição, assinatura flutuando, página órfã.

## Pitfalls

- **Não existe `insertPageNumber` no schema do Docs** (`Request` tem `insertPageBreak`, não campo de
  página). Preserve o rodapé do Doc de referência ou peça ao usuário os dois cliques (Inserir → Números de
  página). Recriar com `createFooter` + texto entrega rodapé **sem** campo — pior que o original.
- **`insertInlineImage` exige imagem publicamente acessível:** suba o PNG ao Drive →
  `permissions.create` (`anyone`/`reader`) → espere ~5s → insira apontando para
  `https://drive.google.com/uc?export=download&id=<ID>` → revogue a permissão e mande o PNG temporário para
  a lixeira. Sem a permissão a API responde `There was a problem retrieving the image`.
- **Máscara de campo é o que preserva o resto:** em `updateTextStyle` de calibração use
  `fields: "fontSize,weightedFontFamily"` (e `foregroundColor` só em título). Como a máscara não inclui
  `bold`, o negrito já aplicado sobrevive.
- **Nunca inclua o `\n` final no range de estilo** (`end - 1`): o estilo vaza para o parágrafo seguinte em
  cascata (documento inteiro vira título/mono).
- **Página órfã:** última página com muito pouco texto significa que o bloco de fecho não coube — reduza o
  material anterior ou agrupe o fecho; não force quebra.
- **Excesso de tabelas domina o orçamento de páginas:** o padding de célula (1–2pt vertical, 3pt
  horizontal) é a alavanca mais forte antes de mexer em fonte.

## Reaplicar negrito a partir do markdown

1. Indexe cada bloco do markdown (parágrafo, célula de tabela, linha de callout) pelo texto **sem
   marcadores**, guardando as faixas `(ini, fim)` de cada `**...**`.
2. No Doc, normalize o texto do parágrafo (espaços colapsados) e case no índice.
3. `updateTextStyle` com `fields: "bold"`, somando o `startIndex` do parágrafo e o offset até o primeiro
   run de texto (elementos de imagem/objeto deslocam esse offset).

## Revisar um Doc que o usuário editou

Quando o usuário edita o documento por conta própria e pede para “pegar o texto de lá”:

- **O markdown autoral é a fonte, não o Doc.** O round trip Doc → markdown perde negrito (texto digitado
  por cima não herda o run em negrito). Faça o diff normalizado (sem marcadores, sem espaços repetidos)
  entre o markdown autoral e o texto atual do Doc e aplique só as diferenças sobre o markdown.
- **Varra o documento por contradições que a edição criou** e reporte cada uma com número: valor por
  unidade × quantidade de unidades, prazos repetidos em resumo/encerramento/próximos passos, numeração de
  marcos citada em anexos, contagem de páginas no rodapé, versão citada na capa. Entregar contradição em
  silêncio é o pior resultado.
- **Inconsistência que envolve dinheiro não se corrige sozinho:** mostre a conta (total ÷ nº de unidades) e
  deixe a decisão com o usuário.
- **Documento que cita anexos:** ao mudar versão, numeração ou prazo, varrer os anexos e reescrever as
  remissões.
- **Quando o usuário assume o restante, pare de editar** e entregue o estado: o que está pronto, links/IDs e
  o que ficou aberto.

## Verificação

- [ ] Doc novo está na pasta certa, com nome versionado, e o original permanece intacto.
- [ ] Capa, cabeçalho e rodapé preservados (rodapé ainda com campo de página, quando o original tinha).
- [ ] Contagem de runs em negrito > 0 e fontes conferidas por `pdffonts` no PDF exportado.
- [ ] Número de páginas medido pelo PDF do Doc e dentro do teto do cliente (sem página órfã).
- [ ] `vision_analyze` na capa, numa página de tabela e na última: sem corte/sobreposição.

## References

- `references/padrao-sergipetec-doc.md` — exemplo trabalhado: o DNA do documento institucional do Sergipe
  Parque Tecnológico (fontes, tamanhos, capa desenhada, margens) e os números reais de calibração de
  páginas, útil como modelo de leitura de DNA para qualquer cliente.
