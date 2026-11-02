# Edição cirúrgica e leitura de Doc via Docs API

Complemento de `references/api-docs-receitas.md` para os casos em que a edição precisa ser
cirúrgica (trocar uma cláusula, um valor, um bloco de assinatura) e para auditoria do documento
por API. Todos os itens abaixo falham **em silêncio** quando ignorados.

## `replaceAllText`: substituir a CAUDA, não o parágrafo

Para corrigir texto corrido (cláusula, item, valor), casar **só o trecho que muda** e deixar de
fora o rótulo inicial do parágrafo. Motivo mecânico: o texto novo herda o estilo do **primeiro run
casado**, então casar a partir do rótulo apaga o negrito do número ("6.2.", "a)", "3.1.").
Casando só a cauda, o run em negrito nem é tocado.

Duas armadilhas:

- **Comer conectores deixa a frase sem pontuação.** Trocar `"e as obrigações de sigilo
  perdurarão…"` por `"As obrigações de sigilo perdurarão…"` produz `"…na data de sua assinatura As
  obrigações…"`. Ao redigir o texto novo, abra com a pontuação que fecha a anterior (`". As
  obrigações…"`) ou inclua o conector na string antiga.
- **`occurrencesChanged` vem omitido quando o match dá 0** → `KeyError` ao somar os resultados.
  Leia com `.get("occurrencesChanged")` e **trate 0 como falha**: acento, pontuação ou espaço
  diferente e a troca simplesmente não aconteceu. Reconferir relendo o doc e casando o texto novo.

## Acrescentar subitem sem renumerar o documento

`insertText` no `endIndex - 1` do parágrafo âncora (antes do `\n` final), com `"\n3.2. texto"`: o
parágrafo novo herda o estilo do âncora. Depois, negrite o rótulo com `updateTextStyle` na faixa
`startIndex .. startIndex + len("3.2.")`, **relendo o doc antes** (índices antigos ficam stale).
Renumerar cláusulas de um documento que o cliente já leu é o que se evita — pendure subitem.

## Tabela nova (ex.: bloco de assinaturas)

1. `deleteContentRange` na faixa dos parágrafos antigos (faixa inteira, nunca caractere a caractere).
2. `insertTable(rows=R, columns=C, location={index: startIndex da faixa apagada})` — a API cria um
   parágrafo vazio antes da tabela, e isso é esperado.
3. Preencher células de trás para frente (maior `startIndex` primeiro). **Índice de célula vazia é
   `paragraph.startIndex`, não `+1`**: o parágrafo vazio tem extensão 1 (`startIndex+1 == endIndex`)
   e `insertText` em `endIndex` falha com *"The insertion index must be inside the bounds of an
   existing paragraph"*.
4. `updateTableColumnProperties` aceita `columnIndices: [n]` (lista) e **exige** `"fields": "*"`
   (sem isso: *"At least one field must be listed in 'fields'"*). `columnIndex` no singular dá
   400 `Unknown name`.
5. Cor de borda tem **duas camadas**: `borderLeft: {color: {color: {rgbColor: …}}, width, dashStyle}`.
   Uma camada só devolve *Unknown name "rgbColor"*.
6. Tipografia da tabela: um `updateTextStyle` na faixa `startIndex..endIndex` dela, com
   `weightedFontFamily` + `fontSize` e `fields` explícito.

## Ler o doc para auditoria

Um extrator ingênuo devolve string vazia e você conclui, errado, que o documento está sem texto.
Três detalhes:

- `table["rows"]` é um **inteiro** (contagem). As linhas estão em `table["tableRows"]`.
- Texto de célula vive em `tableCells[i]["content"][n]["paragraph"]`, e `n` **nem sempre é 0**
  (há um elemento estrutural antes). Itere todos os `content`.
- O texto está em `textRun["content"]` em qualquer profundidade: use um walker recursivo que, para
  dict, devolve `textRun.content` quando existir e senão concatena os filhos.

Ao auditar, registre também `namedStyleType` por parágrafo: é o que mostra se a hierarquia
(HEADING_1/2) sobreviveu à edição. E exporte o PDF para conferir que a tabela não partiu entre
páginas (`pdftotext -layout` página a página) — a API não mostra paginação.
