# Smart chips (rich links do Google) em células — criação via Sheets API

As planilhas da ID (especialmente `contratos` e `clientes` da Symplexis) usam **smart chips
do Google** nas células que referenciam arquivos do Drive/pessoas. Não são texto comum nem
hyperlink simples — são chips (`@`-like) renderizados na UI. **Para manter o padrão ao editar,
é preciso criá-los via API**, não por `values().update`.

## Colunas com chips (mapa da Symplexis, verificado 19/08/2026)

| Aba | Coluna | Tipo de chip |
|---|---|---|
| `contratos` | **H** (Contrato editável/minuta) | rich link → Google Doc (mime `application/vnd.google-apps.document`) |
| `contratos` | **I** (Contrato assinado) | rich link → arquivo Drive/PDF (mime `application/pdf`) |
| `contratos` | **J** (Backlog associada) | rich link → planilha/Drive |
| `clientes` | **D** (Email) | people chip (email) |
| `symplexis` | **E** (Consultor responsável) | people chip (email/nome) |
| `consultores` | **A** | people chip |

Detecção (read-only): `spreadsheets.get` com `includeGridData=True` → célula tem
`chipRuns` com `chip.richLinkProperties.uri` (+ `mimeType`) ou `chip.personProperties`.

## Criação — método validado

A API exige um **placeholder `@`** na `stringValue`; o `startIndex` do chip aponta para ele.
Depois que o Google processa, a célula passa a exibir o **nome do arquivo** automaticamente.

```python
requests = [
  {"updateCells": {
     "rows": [{"values": [
        # text = "@" → o Google substitui pelo nome do arquivo do link
        {"userEnteredValue": {"stringValue": "@"},
         "chipRuns": [{"startIndex": 0,
            "chip": {"richLinkProperties": {
               "uri": DOC_URI, "mimeType": "application/vnd.google-apps.document"}}}]}
     ]}],
     "range": {"sheetId": sheet_id,            # pegar via spreadsheets.get (fields sheets.properties.sheetId)
               "startRowIndex": row-1, "endRowIndex": row,
               "startColumnIndex": col0, "endColumnIndex": col0+1},   # 0-indexed
     "fields": "userEnteredValue,chipRuns"
  }}
]
sheets.batchUpdate(spreadsheetId=S, body={"requests": requests})
```

- `mimeType` do Google Doc vem de volta normalizado para `application/vnd.google-apps.kix`
  pelo Google (comportamento normal, igual às linhas existentes).
- PDF/Drive: `uri = https://drive.google.com/file/d/<ID>/view?usp=drive_link`, mime `application/pdf`.
- **Erro comum:** `"The chip run start index must be a placeholder character"` → a `stringValue`
  precisa conter `@` na posição do `startIndex` (0). Não usar o nome do arquivo como stringValue
  com um chip vazio — é isso que dispara o erro.

## Extrair o texto/links dos chips (para auditoria)

`spreadsheets.get` → `sheets.data[0].rowData[].values[].chipRuns[].chip`:
- `richLinkProperties.uri` (+`mimeType`) para arquivos
- `personProperties.email` para people chips

## Contexto

Google lançou suporte a smart chips direto na **Sheets API** (guia oficial "Smart chips /
sheets/api/guides/chips"). O padrão de criação com o placeholder `@` e `chipRuns` segue o que
o gist tanaikech/682d77c3e3fb4aade4e816801a26ca21 documenta para Apps Script — o mesmo request
`batchUpdate` funciona de qualquer linguagem (aqui via `googleapiclient` no venv do Google).
