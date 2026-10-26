# Segmentar texto extraído de PDF em blocos (parágrafos + estrutura)

Problema central: `pdftotext -layout` devolve linhas visuais, não parágrafos. Títulos podem vir
colados ao corpo e a quebra de página corta um parágrafo no meio. Regras que funcionaram em
documento institucional diagramado (manifesto, estatuto), reaproveitáveis em contrato,
relatório e capítulo.

## 1. Remover mobília de página

Antes de qualquer coisa, descarte as linhas que se repetem por página e os filetes:

```python
FURNITURE = re.compile(
    r'^(PARTIDO DEMOCRÁTICO TRABALHISTA|PDT – DIRETÓRIO NACIONAL|EXECUTIVA NACIONAL|_+|'
    r'Pág\.\s*\d+\s*-\s*(Manifesto|Programa) PDT)$')
```

Monte essa regex a partir do que realmente se repete no `.txt` — nunca de suposição. Troque
`\f` (form feed) por `\n` e descarte as linhas vazias: o parágrafo é reconstruído pela regra
seguinte, não pelo espaço em branco.

## 2. Linhas → parágrafos

Regra: **acumule até a linha terminar em pontuação final** (`. ! ? : ;`). Em texto justificado,
continuação de parágrafo termina no meio da frase; parágrafo de verdade termina em ponto. Isso
resolve sozinho o parágrafo cortado por quebra de página.

```python
for s in lines:
    buf.append(s)
    if s.endswith(('.', '!', '?', ':', ';')):
        blocks.append(' '.join(buf)); buf = []
```

Exceção: linha que é **título sozinho** fecha o bloco e vira bloco próprio —
`^\d{1,2}\.\s+[A-ZÁÉÍÓÚÂÊÔÃÕ]` com menos de ~50 caracteres (`3. No Plano Econômico`). Sem
isso o título engole o primeiro parágrafo da seção e o índice sai com texto no lugar do nome.

## 3. Padrões estruturais

```python
ROMAN_HEAD     = r'^(I|II|...|IX)\s*-\s*([^-]+?)\s*-\s*(.*)$'   # título + corpo na MESMA linha
ROMAN_DOT_BODY = r'^(I|II|...|IX)\.\s+([^-]+?)\s+-\s+(.*)$'     # VIII. Título - corpo
ROMAN_SOLO     = r'^(I|II|...|IX|X)\s*[-.]\s+(.+)$'             # IX. Só o título.
ITEM           = r'^(\d{1,2}\.\d{1,2})\.\s+(.*)$'               # 3.4.
LETTER         = r'^([a-l])\)\s*(.*)$'                         # a)
DASH           = r'^-\s+(.*)$'                                   # - item
HEAD_SCALAR    = r'^(\d{1,2})\.\s+([A-Z...].*)$'                # 2. Plano Político.
```

Ordene a checagem do mais específico para o mais genérico: `TÍTULO - corpo` (com travessão)
antes de `TÍTULO -`; `3.12.` antes de `3.`; senão um item numerado é promovido a título e a
seção se parte.

## 4. Contexto decide o tipo

O número `1.` é título de seção ("1. Compromissos prioritários") **ou** item de lista ("1. O
direito de viver..."). Decida pelo contexto: títulos escalares são curtos e acontecem antes do
primeiro item da seção; itens simples acontecem dentro de uma seção já aberta. Não resolva só
por tamanho — item curto ("2.7. Extinção dos órgãos de repressão política.") vira título falso.

Separe a **parte final/registral** (atos, assinaturas, cláusulas de fecho) num bloco próprio
antes de interpretar títulos: ela reusa a mesma numeração romana e confunde o parser.

## 5. Listas quebradas em vários blocos

Lista com `;` entre itens acumula até o ponto final e pode ser partida pela quebra de página.
Junte os blocos da lista (do cabeçalho da lista até o próximo irmão estrutural) **antes** de
extrair os itens com `\d+\)\s*([^;]+)` → foi assim que uma lista de nomes saiu com um único
item.

## 6. Prova de que não perdeu conteúdo

Imprima `len(blocks)` e os primeiros 90 caracteres de cada bloco durante o desenvolvimento: é a
forma mais rápida de ver título colado, lista partida ou seção ausente. Depois rode a
comparação de multiconjunto de palavras entre fonte e saída (ver SKILL.md). Seção faltando no
índice = bug de parser, sempre.
