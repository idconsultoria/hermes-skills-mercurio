# Sheets API — Pitfalls, payloads exatos e erros 400 vistos (produção, 2026-08)

Sessão real: checklist pré-MVP + aba Progresso na planilha Roadmap do CFP IA.
Todos os erros abaixo foram encontrados e corrigidos ao vivo.

## 1. Locale pt-BR — separador de fórmula é `;`

Fórmulas escritas com `,` (locale en-US) resultam em `#ERROR!` ou texto literal:

```
=COUNTIF(rng,"CONCLUIDO")        → #ERROR! (ou vira texto)
=COUNTIF(rng;"CONCLUIDO")        → ✅ funciona
=COUNTIFS(B2:B500;"Engenharia";G2:G500;"CONCLUIDO")   → ✅
=SUMIFS(I2:I500;B2:B500;"Engenharia";G2:G500;"CONCLUIDO") → ✅
```

Mesmo `=SUM(1,2)` virou o literal "1,2" — o locale pt-BR interpreta `,` como separador decimal.

**Diagnóstico rápido:** testar `=1+1` (funciona) vs `=SUM(1,2)` (vira texto) numa célula da planilha.

## 2. Dropdown: ONE_OF_LIST vs ONE_OF_RANGE

```
Erro 400: "ConditionType 'ONE_OF_RANGE' requires exactly one ConditionValue, but 5 values were supplied."
```

`ONE_OF_RANGE` é para referenciar um range de células (1 condition value = range).
Para lista literal de valores usar **`ONE_OF_LIST`**:

```json
{"setDataValidation": {
  "range": {"sheetId": 0, "startRowIndex": 1, "endRowIndex": 90, "startColumnIndex": 6, "endColumnIndex": 7},
  "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
    {"userEnteredValue": "CONCLUIDO"}, {"userEnteredValue": "EM_ANDAMENTO"}]},
    "showCustomUi": true, "strict": true}}}
```

## 3. URL-encode do nome da aba na URL de values

```
values/Checklist pré-MVP!A1:O42   → HTTP 400 InvalidURL (espaço/acento)
values/{urllib.parse.quote('Checklist pré-MVP')}!A1:O42   → ✅
```

## 4. textFormatRuns — formato dos runs

```
Erro 400: "Unknown name \"textFormat\" at 'requests[0].update_cells.rows[0].values[0].text_format_runs[0].format'"
```

Dentro de `textFormatRuns[].format`, os campos de fonte vão **direto** (sem aninhar em `textFormat`):

```json
{"textFormatRuns": [
  {"startIndex": 0, "format": {"link": {"uri": "https://..."}, "foregroundColor": {"red": 0.1, "green": 0.35, "blue": 0.9}}}
]}
```

## 5. repeatCell — fields no nível do request

```
Erro 400: "Unknown name \"fields\" at 'requests[2].repeat_cell.cell'"
```

```json
{"repeatCell": {
  "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 8},
  "cell": {"userEnteredFormat": {...}},
  "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}}   ← AQUI, fora do cell
```

## 6. gradientRule / colorScale

```
Erro 400: "Invalid InterpolationPoint.value: 0.5"
```

`NUMBER` com valor decimal falha no locale pt-BR. Usar MIN/MAX/PERCENTILE:

```json
{"gradientRule": {
  "minpoint":  {"color": {"red": 0.86, "green": 0.13, "blue": 0.13}, "type": "MIN"},
  "midpoint":  {"color": {"red": 0.98, "green": 0.73, "blue": 0.10}, "type": "PERCENTILE", "value": "50"},
  "maxpoint":  {"color": {"red": 0.13, "green": 0.55, "blue": 0.13}, "type": "MAX"}}}
```

## 7. Números como string → SUM retorna 0

CSV entrega `esforco_pontos` como `"5"` (string). `SUM(I2:I500)` retorna 0 se tudo for texto.
Converter para `int()` antes do upload:

```python
if h == "esforco_pontos" and v.strip().isdigit():
    v = int(v.strip())
```

## 8. Idempotência — deletar e recriar abas

`addBanding` e `addConditionalFormatRule` duplicam a cada execução. Para scripts re-rodáveis:

```python
delete_reqs = [{"deleteSheet": {"sheetId": sid}} for nome, sid in abas.items() if nome in alvo]
api_request(f".../spreadsheets/{SHEET_ID}:batchUpdate", "POST", {"requests": delete_reqs})
time.sleep(2)   # aguardar propagação antes de addSheet
```

## 9. Smart-chips nativos não são criáveis via API

Sheets API não expõe criação de smart-chips (@mention de arquivos). Aproximação visual **pill**:

```json
{"updateCells": {
  "range": {...},
  "rows": [{"values": [{
    "userEnteredValue": {"stringValue": "[Doc] [Planilha]"},
    "textFormatRuns": [{"startIndex": 0, "format": {"link": {"uri": url}, "foregroundColor": {"red": 0.1, "green": 0.35, "blue": 0.9}}}],
    "userEnteredFormat": {
      "backgroundColor": {"red": 0.91, "green": 0.94, "blue": 0.99},
      "borders": {"top": {"style": "SOLID", "width": 1, "color": {"red": 0.55, "green": 0.65, "blue": 0.9}},
                  "bottom": {...}, "left": {...}, "right": {...}},
      "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
      "padding": {"top": 4, "bottom": 4}}}]}],
  "fields": "userEnteredValue,textFormatRuns,userEnteredFormat.backgroundColor,userEnteredFormat.borders,userEnteredFormat.horizontalAlignment,userEnteredFormat.verticalAlignment,userEnteredFormat.padding"}}
```

Atenção ao `padding` no JSON: não deixar vírgula trailing antes do fechamento (`"padding": {...}` seguido
de `}` — vírgula extra desbalanceia o dict e dá SyntaxError em Python).

## 10. Fórmulas exigem valueInputOption=USER_ENTERED

`values.update` com fórmula:
```
PUT .../values/Progresso!A1:H116?valueInputOption=USER_ENTERED
```
`RAW` grava `=COUNTIF(...)` como texto literal (sem calcular).

## 11. Abas OBJECT (painel visual) — values API não lê nem escreve

Planilha "Roadmap" do CFP IA tem 2 abas visuais (`Roadmap`, `Tarefas`) que são
`sheetType: OBJECT` — painel com desenhos/objetos, SEM grid de células. Sintoma:

```
GET /values/'Roadmap'!A1:G8        → 400 Unable to parse range
GET /values/Roadmap!A1:G8          → 400 Unable to parse range (mesmo sem aspas!)
GET /values/A1:Z50                 → 400 Invalid range (bare range usa 1ª aba = OBJECT)
POST batchGetByDataFilter (sheetId) → 400 No grid with id: <sheetId>
```

**Não é problema de escaping de nome.** O nome real NÃO tem aspas (verificar com
`[hex(ord(c)) for c in title]` — `repr()` mostra `'Roadmap'` mas os bytes são só `Roadmap`).

Diagnóstico decisivo — metadata mostra o tipo:
```python
GET /spreadsheets/{SID}?fields=sheets.properties(title,sheetType,gridProperties)
# OBJECT: sem gridProperties  → inacessível via values API
# GRID:   gridProperties.rowCount/columnCount → acessível
```

Solução: operar SÓ nas abas GRID, sempre com nome entre aspas na URL:
```
GET /values/'Tarefas em tabela'!A1:T88   → ✅
GET /values/'Roadmap em tabela'!A1:AB1000 → ✅
```

Padrão de leitura robusto: (1) listar abas com sheetType, (2) iterar só GRID,
(3) `urllib.parse.quote(rng, safe="'!:")` na URL.

## Verificação pós-escrita

1. `valueRenderOption=FORMATTED_VALUE` nas células de fórmula → número, não `#ERROR!`
2. `valueRenderOption=FORMULA` → fórmula armazenada correta (sem backslashes `\'`)
3. Coluna de pills com FORMATTED_VALUE → `[Doc] [Planilha]`
4. `?fields=sheets.properties.title` → sem abas duplicadas
