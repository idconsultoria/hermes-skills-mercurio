# Markdown → Google Docs (md-to-gdoc.py)

Converte um arquivo `.md` em um Google Doc **formatado corretamente** (não texto
plano): headings reais, negrito/itálico/código inline, bullets e listas numeradas,
tabelas nativas com largura inteligente, callouts, code blocks e espaçamento entre
parágrafos.

## Uso

```bash
PY=/path/to/venv/bin/python   # python com google-auth instalado
CONV="$PY /opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py"

# Criar documento novo em uma pasta do Drive
$CONV documento.md --title "Título do Doc" --parent FOLDER_ID

# Atualizar documento existente (preserva o ID — apaga e reconstrói o conteúdo)
$CONV documento.md --title "Título" --doc-id DOCUMENT_ID

# Exemplos reais do CFP IA
$CONV product/management/PRD.md --title "CFP IA — PRD" --doc-id 1fDSjh-j6Q52...
$CONV relatorio.md --title "Relatório" --parent 1sl-uFwjOnGQAsk-...
```

- `--parent` move o doc criado para a pasta (via Drive API)
- `--doc-id` atualiza um doc existente (apaga o conteúdo e reconstrói)
- Token OAuth: usa `$GOOGLE_TOKEN_PATH` se definido, senão
  `$HERMES_HOME/google_token.json`, senão `/opt/data/google_token.json`

## Formatos suportados (markdown)

| Markdown | Resultado no Google Docs |
|----------|--------------------------|
| `#` / `##` / `###` / `####` | HEADING_1..4 (estilos nativos) |
| `**negrito**` | Texto em negrito (runs separados — só o trecho marcado) |
| `*itálico*` | Texto em itálico |
| `` `código` `` | Fonte JetBrains Mono 9pt (só o trecho) |
| `- item` / `* item` | Bullet list (cada item vira parágrafo com bullet) |
| `- [ ] item` / `- [x] item` | **Checklist com checkbox clicável** (`BULLET_CHECKBOX`) |
| `1. item` | Lista numerada (o Google numera sozinho — NÃO inserir prefixo manual) |
| `\| a \| b \|` tabela markdown | Tabela nativa com largura proporcional ao conteúdo |
| `> texto` | Callout: fundo acinzentado + borda esquerda azul + recuo |
| ` ```code``` ` | Code block em JetBrains Mono 9pt |
| `[texto](url_google_doc)` | **Smart chip** (rich link) — mostra o TÍTULO do doc com ícone; ideal p/ docs que se referenciam |
| `[texto](url_externa)` | Hyperlink normal (texto azul clicável) |
| `---` | Quebra de seção (parágrafo vazio) |

Parágrafos normais recebem `spaceBelow: 8pt` para respiro de leitura.

**Sobre smart chips:** para qualquer URL de `docs.google.com/document|spreadsheets|presentation` ou `drive.google.com/file|open`, o conversor insere um **rich link** (chip) que exibe o título do documento referenciado com um ícone — muito mais usável no celular que uma URL crua. O texto do link markdown vira apenas o label (ignorado na renderização; o chip mostra o título real do doc).

## Como funciona (importante para debugging)

- **Modo batch:** acumula requests e faz flush a cada 25 (evita rate limit 429).
  O `BATCH_SIZE = 25` no topo do script controla isso. Ajuste se a quota do
  usuário for menor.
- **Índice rastreado localmente:** `self.cur` é o índice de inserção (início do
  parágrafo vazio final), não o endIndex. Cada `insertText` avança `cur` por
  `len(texto)` — o Google cria um parágrafo vazio extra após cada `\n`.
- **Tabelas:** criadas no índice atual, depois relê o doc para mapear as células
  (os índices de célula não são previsíveis localmente), e preenche **de trás
  para frente** — inserir texto numa célula desloca os índices das seguintes;
  ir do fim para o começo evita acumular tudo na primeira célula.

## Pitfalls (todos encontrados e corrigidos na prática)

1. **Style bleeding por `\n`:** aplicar `updateTextStyle`/`updateParagraphStyle`
   num range que INCLUI o `\n` final propaga o estilo ao parágrafo seguinte —
   e em cascata ao documento inteiro. SEMPRE usar `end - 1` para excluir o `\n`
   dos ranges de estilo. Sintoma clássico: documento todo em fonte mono ou todo
   com bullet.
2. **Herança de fonte ao inserir:** um parágrafo criado após um code block nasce
   com fonte mono herdada. O builder chama `_normalize_font()` (reseta para
   Arial) no range de CADA parágrafo antes de aplicar bold/code inline.
3. **Herança de bullet em cascata:** parágrafo criado após uma lista herda o
   bullet. `clear_bullet()` remove do parágrafo vazio atual `[cur, cur+1]` antes
   de inserir conteúdo normal. CUIDADO: o range correto é `[cur, cur+1]` (início
   do parágrafo vazio), não `[cur-1, cur]` — este último apaga o bullet do item
   anterior da lista (sintoma: só o último item da lista tem bullet).
4. **`endOfSegmentLocation` normaliza índices:** inserir texto com
   `endOfSegmentLocation` desloca o texto para um índice imprevisível. Usar
   `location.index = current_end() - 1` (dentro do parágrafo vazio final) e
   rastrear `cur` localmente. O texto inserido começa exatamente em `cur`.
5. **`tableCellLocation` não existe em `insertText`:** a API NÃO aceita
   `tableCellLocation` dentro de `insertText.location`. Para preencher célula,
   usar o `startIndex` do parágrafo dentro da célula
   (`cell["content"][0]["startIndex"]`).
6. **Célula vazia tem parágrafo:** o `startIndex` de uma célula aponta para um
   marcador; o texto deve ser inserido no `content[0]["startIndex"]` (o
   parágrafo vazio dentro da célula).
7. **`fontFamily` não existe em `updateTextStyle`:** o campo é
   `weightedFontFamily: {fontFamily: "..."}` — `fontFamily` direto retorna 400.
8. **Nunca inserir prefixo manual em listas numeradas:** `1. texto` + preset
   `NUMBERED_DECIMAL_ALPHA_ROMAN` duplica o número ("1. 1. texto"). O preset
   numera sozinho.
9. **Rate limit 429:** o script tem retry exponencial (15s × tentativa) no
   `api_request`. Com batches de 25, documentos grandes (~700 operações) rodam
   em ~2-4 minutos mesmo com alguns 429. NÃO rodar dois processos em paralelo
   no MESMO doc — o último a terminar sobrescreve (resultado indeterminado se
   terminarem juntos).
10. **Verificação visual é do usuário:** a estrutura de runs do Google Docs
    retornada pela API pode mostrar "células vazias" que na verdade estão
    preenchidas (depende de como se lê `tableRows`). Confiar na inspeção visual
    do usuário, não em leituras parciais da API.
11. **Células vazias em tabelas (400 "must specify text to insert"):** se uma
    célula de tabela estiver vazia no markdown (ex.: tabela de preenchimento
    `| 1 | | | |`), NÃO chamar `insertText` com `text: ""` — a API rejeita com
    400. Pular células vazias (`if not plain: continue`).
12. **Smart chips (insertRichLink) INSEREM, não substituem:** inserir um rich
    link no índice do caractere reservado `\uFFFC` deixa o `\uFFFC` residual em
    `idx+1` (deslocando o documento em +1 e colando o próximo bloco). SEMPRE
    deletar o residual: `insertRichLink` em `idx` + `deleteContentRange`
    `[idx+1, idx+2]`, processando os chips **de trás para frente**.
13. **`textStyle.link` usa `url`, não `uri`:** `updateTextStyle` com
    `textStyle.link` aceita o campo `url`; `uri` retorna 400
    ("Unknown name"). Já `insertRichLink.richLinkProperties` usa `uri`
    (não `url`) — são APIs diferentes com nomes invertidos.
14. **`emit_segs` precisa retornar o start:** os métodos que chamam
    `emit_segs` usam o retorno como `startIndex` dos ranges de estilo. Se o
    `return start` faltar, `start=None` → 400 "must contain a start and end index".
15. **Segmentos agora têm 3 valores `(tipo, texto, url)`:** após adicionar
    chips/links, TODO código que itera `segs` deve desempacotar 3 campos
    (`tipo, txt = seg[0], seg[1]`). Loop antigo `for tipo, txt in segs` →
    `ValueError: too many values to unpack`. Verificar `add_table` em
    particular (células com links).
16. **Emojis quebram offsets — usar `u16len()` SEMPRE:** o Google Docs API
    indexa por **code units UTF-16**, mas Python `len()` conta codepoints.
    Emojis como 🎯 (U+1F3AF) são surrogate pairs = **2 code units**, não 1.
    Um único emoji desloca todos os índices seguintes em 1 → sintomas:
    parágrafos grudados ("TÍTULOtexto"), estilos aplicados em ranges errados
    (documento inteiro vira heading/fonte grande). Usar `u16len(s) =
    len(s.encode("utf-16-le")) // 2` em TODO offset: avanço do `cur`,
    ranges de `updateTextStyle`, posição de chips, `_normalize_font`.
17. **Callout com heading interno:** `> ### Título` NÃO é parseado como
    heading (fica texto literal com `###`). Dentro de callouts, usar
    `> **Título em negrito**` — o callout já tem fundo destacado; negrito é
    suficiente e o parser entende.
18. **Chips dentro de TABELAS (emoji OBJ/￼ = `\uFFFC` residual):** o loop de
    células do `add_table` precisa processar `richlink` — senão o placeholder
    `\uFFFC` fica visível como caractere OBJ. Além do `insertRichLink`,
    deletar o `\uFFFC` residual (`deleteContentRange [idx+1, idx+2]`) e somar
    `offset += 1` (não `u16len(label)`) para richlink. Sintoma: coluna "Abrir"
    de uma tabela mostrando ￼ em vez do chip.
19. **Mermaid com MÚLTIPLOS nodes por linha (corrigido 2026-08-14):** a antiga
    lógica de limpeza de colchetes do `_fix_mermaid()` assumia UM par de
    colchetes por linha (um node). Em diagramas reais com `A[...] --> B[...]`
    (dois+ nodes na MESMA linha), ela apagava o `]` do primeiro node e o `[`
    do segundo → sintaxe mermaid corrompida. Duas formas de falhar:
    - **RIPD:** mmdc falhava de vez → NENHUMA imagem subia (diagrama some do doc)
    - **PRD/lgpd-onboarding/fluxo-solicitacoes:** mmdc renderizava a corrupção →
      a imagem SUBIA MUTILADA (labels fundidos, arestas perdidas) — pior, porque
      a contagem de imagens no Drive (`inlineObjects`) dizia "OK" (1 imagem existe)
    **Fix:** `_fix_mermaid()` agora usa scanner de profundidade — preserva o par
    mais externo de CADA label na linha e só remove colchetes/parênteses
    ANINHADOS de verdade (nível > 0). Verificar: `/opt/data/igor-docs-md/verificar_mermaid_drive.py`
    compara blocos mermaid no .md vs imagens inline no Drive, e avisa quando um
    doc tem múltiplos nodes/linha (padrão que merece checagem visual).
    Ao adicionar diagramas mermaid em markdown, NUNCA colocar mais de um node
    por linha se quiser compatibilidade total com o renderer antigo — com o fix
    atual, múltiplos nodes por linha são suportados.

## Tabelas com largura inteligente

A largura de cada coluna é proporcional ao conteúdo: mede o maior comprimento
de texto em cada coluna (header + células) e distribui o orçamento total
(560pt) proporcionalmente, com clamps de 60pt (mínimo) e 300pt (máximo).
Cada coluna recebe seu próprio `updateTableColumnProperties` num único batch.

## Requisitos

- Python com `google-auth` (o token OAuth precisa de refresh automático)
- Token em `google_token.json` com escopos de Drive + Docs (o setup do
  google-workspace cobre isso)
