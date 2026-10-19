# Preparar o markdown antes do md-to-gdoc (3 defeitos que saem no PDF)

O motor `md-to-gdoc.py` trata **cada linha do markdown como um paragrafo** (`parse_md`
faz `blocks.append(("para", ...))` por linha). Markdown escrito com quebra de linha
suave — o padrao quando o texto foi datilografado em ~80 colunas — vira no Doc um
paragrafo por linha. No PDF exportado isso aparece como **linhas curtas fragmentadas**
no meio da frase, e na revisao por visao parece "texto quebrado". Nao e defeito do
motor: e entrada nao normalizada.

Rode `scripts/prepara_md.py` antes de chamar o motor. Ele faz tres coisas.

## 1. Juntar linhas de continuacao

Cada paragrafo vira **uma** linha. Regra: uma linha recuada (indentada) continua a
linha anterior — inclusive depois de bullet, item numerado ou heading. Sem isso, a
segunda linha de um bullet vira paragrafo novo e perde a indentacao.

## 2. Nao usar lista numerada nativa

`createParagraphBullets` cria **uma lista por paragrafo**, entao `1. / 2. / 3. / 4.`
sai no PDF como **`1. 1. 1. 1.`** — cada item com seu proprio contador zerado.

Solucao: o numero vai **dentro do texto** e o vira bullet, preservando o numero que a
fonte ja tinha:

```markdown
- **1.** texto do primeiro item
- **2.** texto do segundo item
```

Guarde o numero da fonte, nao um contador proprio: uma lista que recomeca em "1." numa
secao nova precisa sair como "1.", nao "7.".

## 3. Callout (`>`) em linhas curtas

O callout sai em fonte monoespacada, que e bem mais larga que a proportional. Uma
linha de 130 caracteres estoura a largura util e o Docs **nao** quebra codigo inline —
o texto passa da margem. Quebre por **palavra** (nunca no meio de um token, nem de um
numero CNPJ) em pedacos de ~74 caracteres.

Antes de escrever:

```
> **Contratada:** ID Consultoria
> iD.teal Consultoria em Gestão Organizacional LTDA
> CNPJ 54.569.818/0001-59
```

## Script

```bash
python3 prepara_md.py original.md=pronto.md
python3 md-to-gdoc.py pronto.md --title "..." --parent PASTA
```

Ele imprime quantas linhas gerou, quantos itens numerados converter e **quais
paragrafos ficaram curtos demais** (sinal de que sobrou quebra de linha suave) — essa
ultima lista e o checklist antes de gerar o Doc.

## Checklist de conferencia depois de gerar

```bash
pdftotext -layout DOC.pdf - | grep -c '\*\*'   # 0 = negrito virou texto cru
pdfinfo DOC.pdf | grep Pages                   # numero de paginas
pdftoppm -png -r 70 -f 1 -l 1 DOC.pdf pag     # revisao por visao da pagina 1
```

- `**` no texto extraido = `split_inline` nao casou o paragrafo (numero impar de `**`
  na linha de origem). Junte a linha na origem.
- Paragrafos em blocos coesos, tabela completa, bloco de metadados **dentro** da
  margem, lista de 3 itens mostrando **1. 2. 3.**
