---
name: id-papel-timbrado
description: "Use ao criar doc da ID com timbrado no Google Docs."
type: Reference
timestamp: 2026-08-20T00:00:00Z
---

# Papel timbrado da ID no Google Docs

Como criar um documento da ID com timbrado (capa + masthead nas páginas de corpo)
a partir de um modelo gdoc, preenchendo **os lugares certos** e inserindo/formando o
corpo. Aprendido em 20/08/2026 ao criar a proposta "Contribuição da ID ao DESO Smart
Dosing".

## Modelos de timbrado (gdocs na conta pessoal)

| Modelo | Doc ID |
|---|---|
| **Modelo de Doc [Fundo Preto]** | `1dFY0Mb0X0OAS8TjnIW6rqAP3A-dhA1nTMS3HETht5To` |
| Modelo de Doc [Fundo Verde] | `1EU_pJrSc-k6LLE2Dm4oL4FI-7pb3blenNo4eLsIEfGw` |
| Modelo de Doc [Fundo Azul] | `155J24ZBD__X5sf7nhz6FwLaGyVGMgS66XqT0HjbjBEE` |

Estrutura do Fundo Preto (via Docs API): capa com logo/watermark topográfico, depois
placeholders de texto editável, depois páginas de corpo com masthead ID + cabeçalho
(2 campos) + rodapé numerado.

## Acesso (IMPORTANTE)

- `google_token.json` (primário) está **só-gmail** (parcial) desde 08/2026 → NÃO serve
  para Drive/Docs/Sheets.
- Tokens com escopo **full** (Drive+Docs+Sheets): `google_token.admin_idconsultoria.json`
  (conta admin) e `google_token.backup_gustavomelloenciv.json` (conta pessoal — dona da
  pasta FINEP/Sergipetec; use esta quando o alvo for arquivo da conta pessoal).
- Usar o wrapper: `export GAPI_TOKEN=/opt/data/google_token.<escolhido>.json` e
  `/opt/data/venvs/google/bin/python /opt/data/gapi_token.py <cmd>`.

## Procedimento (copiar modelo → editar lugares certos)

1. **Copiar o modelo** (preserva masthead, watermarks, headers/footers e tipografia):
   ```python
   drive.files().copy(fileId=SRC, body={'name': DOCNAME, 'parents':[FOLDER]}).execute()
   ```
   Nomear com **versão (v1...)** — nunca reutilizar nome.

2. **Editar placeholders da CAPA** (no corpo, replaceAllText matchCase):
   - `Tipo de Documento` → ex.: `PROPOSTA DE CONTRIBUIÇÃO TÉCNICA`
   - `Título Expandido do Documento` → título completo
   - `TÍTULO` → título resumido/hero da capa

3. **Editar placeholders do CABEÇALHO** (vivem nos page-headers, não no corpo; também
   via replaceAllText que alcança headers):
   - `Título Resumido do Documento` → título curto (ex.: `Proposta — DESO Smart Dosing (FINEP)`)
   - `CLIENTE` → cliente (ex.: `DESO + SergipeTec`)
   - Não mexer no glyph `\ue907` que os sucede (espaçador decorativo).

4. **Inserir o CORPO** logo após o parágrafo do título da capa (`TÍTULO`):
   - Achar `endIndex` do parágrafo que contém o texto do título (`el['endIndex'] - 1`).
   - `insertText` em `{index: <esse>}` com `"\n" + corpo + "\n"`.

5. **Estilizar** (batches por parágrafo, matcher por ordem de conteúdo; **não incluir o
   `\n` final no range** — usar `endIndex - 1`):
   - Seções → `updateParagraphStyle` `namedStyleType: HEADING_2`
   - Corpo → `NORMAL_TEXT` (já herdou Nunito Sans 12pt justificado 115% do template)
   - Bullets → `createParagraphBullets` com `bulletPreset: 'BULLET_DISC_CIRCLE_SQUARE'`
     ⚠️ **`BULLET_DISC` é INVÁLIDO** (erro 400) — use `BULLET_DISC_CIRCLE_SQUARE`.

## FLUXO RECOMENDADO — reusar o `DocBuilder` do md-to-gdoc (tabelas nativas + code blocks)

Para inserir o corpo com **tabelas NATIVAS e code blocks** (não texto plano), NÃO
reimplementar o parser manualmente. Reusar o builder do próprio script:

```python
import importlib.util, sys
spec=importlib.util.spec_from_file_location('mdg','/opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py')
mdg=importlib.util.module_from_spec(spec); sys.modules['mdg']=mdg; spec.loader.exec_module(mdg)

# após copiar o modelo + preencher placeholders (capa/cabeçalho) com a conta certa:
# achar o parágrafo do herói da capa (TITULO) e usar ins = el['endIndex']  (começo do 1º parág. de corpo)
b=mdg.DocBuilder(NEW); b.cur=ins
for tipo,dados in mdg.parse_md(body_markdown_sem_H1):
    if tipo=='heading': l,v=dados; b.add_heading(l,v)
    elif tipo=='para': b.add_para(dados)
    elif tipo=='callout': b.add_callout(dados)
    elif tipo=='bullets': b.add_bullets(dados, numbered=False)
    elif tipo=='checklist': b.add_checklist(dados)
    elif tipo=='numbered': b.add_bullets(dados, numbered=True)
    elif tipo=='table': h,r=dados; b.add_table(h,r)
    elif tipo=='code': b.add_code(dados)
    elif tipo=='hr': b.insert_text('\n')
b.finish()
```

Isso produz tabelas nativas (grade) e código JetBrains Mono 9pt — o `DocBuilder` já cuida de
u16len (emojis), bleeding e batches. Lembrar: remover a linha `# ` (H1) do markdown antes de
`parse_md` (senão duplica o título da capa). Às H1 visíveis no doc restante são da própria capa
(intencionais). Manter só a versão boa na pasta: apagar as intermediárias (permanent).

### Bold não renderiza (weight 400 fixado) — CORRIGIR weight p/ 700
Sintoma: termos **bold** aparecem com a MESMA espessura do texto normal. Causa: o
`_normalize_font` do script fixa `weightedFontFamily Arial weight 400` em cada parágrafo, e o
`bold:True` sozinho não sobe o peso → o renderizador usa 400 (regular). Fix pós-build: percorrer
o doc e aplicar `updateTextStyle` com `weightedFontFamily weight 700` (mantendo bold) em todos
os runs com `bold:True`. ⚠️ ler `startIndex`/`endIndex` do ELEMENTO (`e.get(...)`), NÃO do
`textRun` (que não os tem → 400 "must contain a start and end index"). Batch de 25.

### Bold perde a 1ª letra (drift pós-tabela) — estender 1 char à esquerda
Sintoma (com o `DocBuilder` embutido no timbrado): nas páginas APÓS a primeira tabela, cada
trecho em negrito perde a 1ª letra (ex.: `*P*roteção`, `*M*ínimo` — a 1ª letra fica no run
anterior, sem bold). É drift de índice do builder incremental após inserir tabelas. Fix
pós-build: para cada run com `bold:True`, estender 1 char à ESQUERDA quando o char em
`s-1` for alfanumérico e estiver sem bold, e aplicar `weightedFontFamily.weight=700`
(junto com bold). Merge ranges contíguos e batch 25.

### Parágrafo em branco antes de cada tabela
O Docs API **proíbe deletar** o parágrafo que antecede uma tabela (tabela exige parágrafo
anterior na estrutura) — `deleteContentRange` retorna 400. WORKAROUND: colapsar os parágrafos
vazios antes das tabelas com `updateTextStyle fontSize 1pt` + `updateParagraphStyle`
`spaceAbove=0,spaceBelow=0` (campos são `spaceAbove/spaceBelow`, NÃO `spaceBefore/After`).
A linha vazia vira ~1pt — o espaço visual some. Fonte: os 6 parágrafos antes das tabelas.

### CUIDADO: reaplicar bold a partir do MARKDOWN (não "estender run")
Se o negrito ficar "100%/errado" (ex.: tudo em negrito), a forma SEGURA de corrigir é:
1. **Reset**: `updateTextStyle` em todo o corpo com `bold:False` + `weightedFontFamily Arial 400`
   (range body a partir do 1º parágrafo do corpo, NÃO toca capa/masthead).
2. **Reaplicar** apenas nos trechos que o markdown marca com `**...**`: montar o texto
   concatenado dos runs (parágrafos + células de tabela) com `prefix` para mapear posição
   sequencial → índice do doc (`seq2doc` com bisect), achar cada frase bold com
   `re.finditer(re.escape(frase))` e aplicar `bold:True, weight:700` nos ranges mapeados.
   Dedupe (set de ranges) + batches de 25.
Sintoma a evitar: o truque anterior de "estender 1 char à esquerda de cada run bold + union de
contíguos" pode apagar o negrito OU acabar unindo tudo em bold. Usar a fonte da verdade
(markdown) para reaplicar é determinístico. Obs.: o Docs API só seta o campo `bold` quando o
`updateTextStyle` declara `fields:'bold,...'` — verificar visualmente (PDF) e não pelo campo
`textStyle.bold` (peso 700 pode renderizar bold sem setar o campo booleano).

## Cross-account (criar doc num Drive de cliente, conta admin)

O modelo mora na conta pessoal (gustavomelloenciv), mas se o destino for uma pasta de
cliente na conta admin (ex.: `4.2.x. <Cliente>` em *4.2. Symplexis*), fazer a cópia
COM o token admin não funciona direto (admin não enxerga o modelo). Receita:

1. Compartilhar o modelo com `admin@idconsultoria.ai` (role writer) usando o token pessoal:
   `drive.personal.permissions().create(fileId=MODEL, body={'role':'writer','type':'user','emailAddress':'admin@idconsultoria.ai'})`.
2. Copiar com o token ADMIN (google_token.json full-scope) e `parents=[FOLDER]` da pasta do
   cliente → o novo doc fica **owned pelo admin** e já na pasta certa.
3. Verificar com `drive get`: owners==['admin@idconsultoria.ai'] e parents==[FOLDER].

Pitfall de parser de md ao inserir o corpo:
- Linhas `---` (regua horizontal) viram artefato de texto — **pular** com `re.match(r'^---+\s*$', s)`.
- Tabelas md (`| a | b |`) → converter para texto normal (`' · '.join(cells)`), pular a linha `|---|` de separação.
- Localizar mês em inglês (ex.: `Data: August de 2026` → `Agosto de 2026`) antes de inserir.
- Para achar o ponto de inserção, casar por igualdade exata do texto do herói da capa (`ptext(el).strip()==TITULO`), não substring (senão colide com o título expandido).

## CAUSA-RAIZ do bug "1ª letra do negrito some" — glifo decorativo \ue907
O template (Fundo Preto) tem um parágrafo final com o caractere `\ue907` (área privada,
decorativo do modelo). O `DocBuilder` do md-to-gdoc usa `self.cur = content[-1].endIndex - 1`,
que cai NO MEIO desse elemento `\ue907\n`, corrompendo os offsets → a 1ª letra de cada trecho
em negrito fica sem bold (e piora depois de tabelas). 
- NÃO é bug do motor (em doc vazio, bold sai certo).
- Fix: ANTES de buildar, **deletar só o caractere `\ue907`** (`deleteContentRange [start, start+1]`
  do run que o contém) — NÃO a nova linha final (essa é protegida: "cannot include the newline
  at end of segment"). Manter a CAPA intacta (não esvaziar o body) para ter capa + negrito certo.
- `replaceAllText` NÃO remove `\ue907` (char de área privada não casa) — usar delete do char.
- Depois do body, adicionar a CONTACAPA (pageBreak + bloco final da ID) e remover linhas
  em branco finais para não sobrar página vazia.
Fluxo final validado: copiar → preencher capa+cabeçalho → deletar `\ue907` → build motor
(Nunito Sans sem weight) → adicionar contracapa → limpar linhas finais.
Ferramenta de referência: `/opt/data/work/md_to_timbrado_id.py`.

## Pitfall CRÍTICO — corpo vira "título 1" gigante (style bleeding por herança)
Ao inserir o corpo logo após o título da capa (que é um heading GRANDE), TODO parágrafo inserido
herda a fonte/estilo gigante do título — sintoma: documento inteiro com texto enorme (parece
"muitas linhas em título 1 / document inteiro em heading"). Correção (seguir o padrão do
`md-to-gdoc.py`): **aplicar `namedStyleType` explícito a CADA parágrafo do corpo** — não só a
headings. Regra de ouro:
- `normal` e `bullet` → `updateParagraphStyle` `NORMAL_TEXT` (reseta a fonte herdada p/ 12pt; não
  deixar sem estilo).
- `h2`/`h3` → `HEADING_2`/`HEADING_3`.
- bullet → NORMAL_TEXT + `createParagraphBullets` preset `BULLET_DISC_CIRCLE_SQUARE`.
- Flush em batches de 25 (evita 429). Nunca incluir o `\n` final no range (`endIndex-1`).

## Pitfalls / notas

- **Etiqueta "Empresa"** na capa: embutida na IMAGEM/SVG (não é text-run) → não edita
  por replaceAllText; deixar como está (artefato do modelo genérico) para não danificar
  o masthead.
- "Linhas cinzas cruzando o texto" nas páginas de corpo = watermark topográfico do
  próprio template (presente no original também) — NÃO é defeito.
- Tipografia padrão do corpo: NORMAL_TEXT Nunito Sans 12pt, JUSTIFIED, line 115;
  HEADING_2 18pt. Página A4, margens 72pt. Corpo justificado + margens largas ⇒
  documentos longos se estendem por várias páginas (normal).
- A ferramenta `docs get` mostra bullets como `#` e headings como `#`/`##` — usar p/ conferir.
- Scripts de referência desta sessão: `/opt/data/finep_trabalho/{copy_template.py,
  build_doc.py, style_doc.py, fill_headers.py, check_headers.py, inspect_doc.py}`.

## Verificação

Exportar a PDF e renderizar (pypdfium2 + Pillow no venv
`/opt/data/venvs/google/bin/python`) e conferir capa + páginas de corpo com
`vision_analyze`. Confirmar capa com logo/cores e corpo com masthead ID.
