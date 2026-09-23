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

## Variante SergipeTec (timbrado do parceiro)

`scripts/md_to_timbrado_sergipetec.py` — gera o mesmo tipo de doc, mas no **modelo SergipeTec**
(`1R8PCezBW8QtjHA1g4Qi6fZulxJkIBQ62IesN3Uqx3bM`), cujo corpo é o do TJSE (parceria anterior).
O fluxo é outro: **copia o modelo**, troca capa/cabeçalho/rodapé por `replaceAllText`,
**deleta o corpo inteiro** (âncora: parágrafo "Introdução") e reinjeta o novo corpo no fim.

```bash
python3 md_to_timbrado_sergipetec.py corpo.md --folder <FOLDER_ID> \
  --doc-name "Proposta ... — vN" \
  --titulo-l1 "Proposta Comercial — Plataforma de" \
  --titulo-l2 "Mitigação do El Niño / Comitê SEMAC" \
  --metadata "Parceria estratégica entre ..." \
  --header-l1 "PLATAFORMA DE MITIGAÇÃO DO EL NIÑO" \
  --header-l2 "Comitê Intersetorial El Niño · SEMAC × SergipeTec"
```

O `corpo.md` deve conter **só o corpo** (começar em `# Resumo Executivo`): a capa vem do modelo.

### Pitfall do cabeçalho (SergipeTec)

- **`replaceAllText` alcança headers, mas NÃO footers.** O rodapé exige a rota dedicada
  (`edit_footer`), e o **cabeçalho herda o texto do TJSE** — sem `--header-l1/--header-l2`
  a proposta do cliente sai com **"MUTIRÃO DE CONCILIAÇÃO" / "Dívida Ativa · TJSE"** no topo
  de todas as páginas. Sempre passar as duas linhas e conferir na renderização.
- Números de referência do modelo: header `kix.hf0` (tabela r0c1, 2 parágrafos), footer `kix.hf1`.
- O `d` + glifo no 1º parágrafo da capa é âncora do modelo (invisível no render) — **não apagar**;
  ao extrair o texto do doc ele aparece como uma letra solta, e isso **não** é defeito do doc.
- Após gerar, **conferir por API**: links (`textRun.textStyle.link`), ocorrências de strings do
  modelo antigo ("Mutirão", "TJSE", "Dívida Ativa") e as 2 linhas do header/footer (que vivem
  DENTRO de uma tabela — um walk só de parágrafos do header devolve vazio e dá falso negativo).
- **Render de conferência:** `pdftoppm -png -r 70 -f <p> -l <p>` + inspeção visual; export PDF do
  modelo SergipeTec reproduz a capa corretamente (ao contrário do modelo ID de fundo preto).
- **Quebra de página: `<!-- pagebreak -->` (ou `\pagebreak`) numa linha isolada do markdown.**
  O Google Docs **não** mantém tabela junta sozinho: uma tabela de fechamento ("Valor total
  anual", "Total geral") parte entre duas páginas e a linha de TOTAL cai sozinha na página
  seguinte — feio e fácil de passar batido. Insira o marcador ANTES do título da seção e
  confira a página renderizada: a tabela tem de aparecer inteira. O marcador é reconhecido por
  `parse_md` e vira `insertPageBreak` (`DocBuilder.add_pagebreak`), sem sobrar texto no doc.
  Depois, confirme que os hyperlinks do corpo sobreviveram (contar `textStyle.link` via API:
  um doc El Niño saudável tem 7).
- **Largura de tabela = largura ÚTIL da seção (não 560pt).** O motor usava orçamento FIXO de
  560pt; o corpo do modelo SergipeTec tem margens de 55pt (útil **485pt**) e o do modelo ID 72pt
  (útil **451pt**) → toda tabela invadia a margem direita; quando a última coluna era estreita
  (ex. célula `R$ 153.753,25`), o texto **saía da página e o último dígito saía cortado** no PDF.
  Corrigido em `md-to-gdoc.py`: `DocBuilder.content_width_pt` (pageSize − margens da seção do
  corpo = a do `sectionBreak NEXT_PAGE`) + **piso por coluna** = maior token inquebrável da
  coluna ×7pt + 12pt de padding, com redistribuição do excedente. Checar sempre com
  `pdftotext -bbox`: em A4 (595pt) nenhuma palavra pode passar de **~540pt**.
- `occurrencesChanged` é **omitido** quando o `replaceAllText` dá 0 ocorrências → somar direto
  dá `KeyError`. E a troca da capa já reescreve a 2ª linha do header (replaceAllText alcança
  headers): `edit_header` por isso **lê o texto atual do header** e substitui o que encontrou,
  em vez de assumir as strings do modelo.

## Pitfalls operacionais

- **Tabela que quebra de página perde o cabeçalho.** O Docs API não repete a linha de cabeçalho
  por padrão: numa tabela longa (plano operacional, matriz de riscos), a continuação na página
  seguinte aparece sem os títulos das colunas. Fix pós-build: `pinTableHeaderRows`
  (`tableStartLocation: {index: <startIndex da tabela>}`, `pinnedHeaderRowsCount: 1`) para CADA
  tabela do documento, num único batch. Obs.: o campo `pinnedHeaderRowsCount` **não volta** na
  leitura do doc — confirme o efeito no PDF renderizado (a linha de cabeçalho reaparece no topo
  da página de continuação), não pela API.
- **Validar tabela grande é olhar a página renderizada**, não só o texto: `pdftotext -layout`
  mostra a paginação (útil para achar em que página cada tabela caiu) e `pdftoppm`+visão confirma
  se a tabela estourou a margem ou partiu em duas.
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
