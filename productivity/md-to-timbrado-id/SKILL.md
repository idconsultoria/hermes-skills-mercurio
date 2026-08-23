---
name: md-to-timbrado-id
description: "Gerar Google Doc no timbrado da ID a partir de Markdown."
type: ToolIntegration
timestamp: 2026-08-23T00:00:00Z
---

# MD → Google Doc no papel timbrado da ID

Converte um arquivo `.md` em um Google Doc completo no **Modelo de Doc [Fundo Preto]** da ID
(`1dFY0Mb0X0OAS8TjnIW6rqAP3A-dhA1nTMS3HETht5To`): capa, corpo formatado (Nunito Sans, negrito,
tabelas, código JetBrains Mono, callouts) e a **contracapa nativa do modelo** na última página.

## Script

`scripts/md_to_timbrado_id.py` — uso:

```bash
/opt/data/venvs/google/bin/python md_to_timbrado_id.py arquivo.md \
  --folder <FOLDER_ID> --doc-name "Nome do Doc vN" \
  --tipo "DOCUMENTO DE REQUISITOS (PRD)" \
  --titulo-exp "Título expandido (capa)" \
  --titulo "TÍTULO HERO (na capa)" \
  --titulo-res "Running title (cabeçalho)" \
  --cliente "Cliente"
```

Motor: `/opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py`
(importado como `mdg` e **monkeypatchado**).

## Estrutura da receita

1. **Copiar o modelo** → herda capa + masthead + contracapa.
2. **Preencher** placeholders da capa e do cabeçalho via `replaceAllText`.
3. **Construir o corpo** com o motor, com 2 patches críticos (abaixo).
4. **Ajustes finais**: colapsar o gap da capa (hero/página-título), espaçamento de tabelas,
   quebra de página antes da contracapa.

## ⚠️ PITFALLS CRÍTICOS (custaram várias iterações — NÃO pular)

1. **NÃO limpar o glifo `\ue907` do parágrafo final.** Ele é o **âncora da contracapa**:
   o modelo renderiza a contracapa na página terminal por causa dele. Apagar esse glifo
   (via `deleteContentRange`) **faz a contracapa sumir**. O glifo NÃO é decorativo — é estrutural.

2. **Patch do `DocBuilder.__init__` — insira ANTES do parágrafo final.** O default do motor é
   `self.cur = doc["body"]["content"][-1]["endIndex"] - 1` (apenda NO fim, fundindo corpo com
   o glifo e corrompendo negritos). Patch para `self.cur = startIndex do último parágrafo`
   (inserir antes do âncora). Isso preserva a contracapa E mantém o negrito íntegro.

3. **Patch do `DocBuilder.add_table` — mesmo motivo.** O `add_table` original **re-reseta**
   `self.cur = endIndex - 1` (linha ~676) após CADA tabela, quebrando o invariante do patch.
   Consequência: tudo que vem depois da 1ª tabela é anexado no lugar errado → a **1ª letra de
   cada bloco de código vira um run separado em Nunito** (deveria ser JetBrains Mono) e os
   **negritos das seções seguintes voltam a quebrar**. Patch: depois do `_orig_add_table`,
   re-setar `self.cur = startIndex do último parágrafo`.

4. **`_normalize_font` (Nunito Sans) SEM `weight:400`** — peso 400 explícito suprime o negrito
   no motor. Monkeypatch de `DocBuilder._normalize_font` para só `weightedFontFamily: Nunito Sans`.

5. **Página-título (hero) entre capa e corpo.** O modelo tem um parágrafo hero (`TÍTULO`) que
   ocupa uma página só. Para eliminar: `remove_cover_gap` apaga o hero + parágrafos vazios +
   a imagem pós-título entre a capa e o corpo, e insere **quebra de página antes do 1º
   parágrafo do corpo** (senão o corpo cai na página da capa).

6. **Linha em branco antes de cada tabela = limitação do Docs API.** O `insertTable` cria
   obrigatoriamente um parágrafo antes da tabela, e o API **REJEITA apagá-lo**
   (`Cannot delete the requested range`). Workaround: **zerar a altura** desse parágrafo
   (`fontSize:1pt` + `spaceAbove/Below:0`) → gap invisível, tabela colada ao heading; e
   **inserir uma linha em branco DEPOIS** de cada tabela (`insertText "\n"` no endIndex, em
   ordem reversa num único batch).

## Pitfalls operacionais

- **Rate limit de escrita do Docs** (`WriteRequestsPerMinutePerUser` = 60/min). O build do
  PRD inteiro já chega perto; NÃO rodar o script em rajada (2+ builds seguidos estouram a
  cota e quebram no meio). Quando estourar: aguardar ~60-70s e refazer, e manter os
  pós-passes (tabela/contracapa) em **1 batch único** cada.
- **Validação via API (leitura), não só render:** para checar fonte/negrito, percorra os
  textRuns — um bloco de código correto tem o 1º run já em `JetBrains Mono`. Parágrafos
  normais com `code` inline têm 1º run em Nunito (isso é CORRETO, não confundir com bug).
- **Export PDF não reproduz elementos posicionados** (a capa sai "branca" no PDF export) —
  para julgar a capa, olhe o doc aberto no editor, não o PDF.
- Não há `.md` do conteúdo em arquivo separado no fluxo da Solution Master — o `.md` fonte é
  `sm-credenciais/PRD_Credenciais_Solution_Master.md`; para outros, gere o `.md` antes.

## Verificação final (PRD Solution Master, ~17 pág)

p1 capa · p2 corpo (título+metadados+Resumo Executivo) · blocos de código JetBrains ·
negritos íntegros · tabelas (sem gap antes, blank depois) · contracapa limpa na última página.
