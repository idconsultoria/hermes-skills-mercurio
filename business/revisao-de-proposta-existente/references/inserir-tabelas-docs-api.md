# Inserir tabelas nativas num Google Doc existente (Docs API)

Caso de uso: substituir um bloco de bullets por seções com tabelas (especificação de pacote,
cronograma, matriz de entregáveis) sem regenerar o documento. Continua a
`troca-pontual-docs-api.md`, que cobre substituição de texto/parágrafos.

## Sequência

1. Congelar a linha de base (export `text/plain`) e trabalhar numa **cópia** versionada.
2. **Apagar o bloco antigo:** `deleteContentRange` do range completo do bloco, começando
   sempre pelo range de MAIOR índice (o segundo não desloca se o primeiro for o mais alto).
3. **Esqueleto de texto:** um único `insertText` no índice inicial com todos os parágrafos
   (título, intro, subtítulos, parágrafo final), cada um terminando em `\n` — **sem** o
   conteúdo das tabelas.
4. **Inserir cada tabela** com `insertTable` no `startIndex` do parágrafo que vem DEPOIS do
   seu subtítulo (a tabela entra entre os dois). Inserir em **ordem inversa** (última tabela
   primeiro) e com GET fresco entre cada `insertTable`.
5. **Preencher células:** GET → `insertText` no `startIndex` do parágrafo da célula,
   percorrendo as células **de trás para frente**, e as tabelas também em ordem inversa.
6. **Estilo em batch separado:** larguras (`updateTableColumnProperties`, exige
   `fields: 'widthType,width'` — sem a máscara o request é rejeitado), padding/alinhamento
   (`updateTableCellStyle` com `tableRange` cobrindo a tabela inteira), negrito por segmento
   (`updateTextStyle` com máscara `bold,foregroundColor,fontSize,weightedFontFamily`).
7. **`updateTableRowStyle` com `preventOverflow: true`** em todas as linhas: sem isso o Docs
   deixa a linha quebrar no meio entre páginas.
8. Verificar com PDF renderizado (`pdftotext` por página para a ordem + `pdftoppm` +
   inspeção visual).

## Pitfalls

1. **Âncora por texto pode casar longe do alvo.** Ancorar "antes do parágrafo que começa com
   `Investimento:`" acertou o resumo executivo, ~9 mil caracteres antes do alvo, e criou uma
   tabela fantasma. Use prefixo longo/único, valide o índice contra a faixa esperada
   (ex.: dentro do bloco recém-criado) antes de enviar, e confira o resultado com um outline
   da região logo depois.
2. **`insertTable` no início de um parágrafo cria um parágrafo vazio ANTES da tabela** —
   vira linha em branco entre o subtítulo e a tabela.
3. **Esse parágrafo vazio não pode ser apagado:** o Docs recusa (`Invalid deletion range`)
   porque apagar a quebra fundiria o parágrafo com a tabela. Solução: apagar a quebra do
   parágrafo ANTERIOR (`deleteContentRange(start-1, start)`), o que funde o subtítulo com o
   vazio e deixa o subtítulo imediatamente antes da tabela. Fazer do maior índice para o menor.
4. **Célula nova herda o estilo do título onde foi inserida** (cor azul e tamanho do
   `HEADING_2`, por exemplo). Reaplique o estilo base das tabelas irmãs — leia o estilo de uma
   tabela que já existe no documento (no caso: Calibri 11 pt, `#1A1A1A`, regular) em vez de
   supor a identidade visual. O Docs normaliza e o GET volta sem override, igual às irmãs.
5. **`cell['content'][0]` é o invólucro `{startIndex, endIndex, paragraph}`, não o
   parágrafo.** O texto está em `content[0]['paragraph']` e o índice em `content[0]`. Ler o
   invólucro como parágrafo devolve string vazia e faz parecer que a célula não foi preenchida.
6. **Leitura do Docs pode vir atrasada** logo após um `batchUpdate`: uma releitura mostrou
   "células vazias" e 4 tabelas quando o documento já tinha 11 tabelas preenchidas. Releia
   depois de alguns segundos antes de concluir que o request falhou.
7. **Cabeçalho órfão no pé da página:** se a tabela nasce na última faixa da página, sobra só
   a linha de cabeçalho. `keepWithNext` no subtítulo não resolve; `insertPageBreak` antes do
   subtítulo resolve e não conflita com `preventOverflow`.
8. **Sumário (TOC) estático não se atualiza pela API.** Se o doc tiver um, avise na entrega;
   sem TOC, não há o que atualizar.
9. **Estilos de cabeçalho não são transferíveis entre documentos:** leia o nível
   (`HEADING_2` × `HEADING_3`) dos subtítulos irmãos do próprio doc antes de aplicar.
10. **Preenchimento duplicado quando um script estoura o tempo:** se o script que preenche
    células morre por timeout e você reexecuta, o texto pode entrar **duas vezes** na mesma
    célula — como dois runs no MESMO parágrafo (`'Diagnóstico...'` + `'Diagnóstico...\n'`).
    Sintoma no PDF: `EixoEixo`, `EntregaEntrega`. A leitura de `cell['content'][0]['paragraph']`
    mostra o texto duplicado, mas ler só `elements[0]` esconde o problema: **confira o texto
    completo do parágrafo** antes de declarar preenchido. Correção: apagar o range a partir do
    fim do texto esperado e reaplicar o estilo da célula.
11. **`insertTable` recria parágrafos vazios em OUTRAS tabelas:** a rotina que remove o
    parágrafo vazio criado pelas tabelas novas varre uma região e acaba apagando também os
    vazios que o documento **já tinha** antes de tabelas antigas — mexendo no layout de partes
    que não eram o alvo. Antes de rodar a limpeza, registre quais tabelas já tinham vazio antes
    (`elemento anterior é parágrafo com texto vazio?`) e restrinja a limpeza às tabelas novas;
    se já apagou, restaure inserindo `\n` em `tableStartIndex - 1` (do maior índice para o menor).
