# Google Sheets Pitfalls — Produção (PT-BR)

## Default Sheet Name by Locale

Google Sheets API creates sheets with locale-dependent default names:

| Locale | Default Name |
|--------|-------------|
| `en-US` | `Sheet1` |
| `pt-BR` | `Página1` |
| `es` | `Hoja1` |
| `fr` | `Feuille1` |

**Pitfall:** Scripts that hardcode `"Sheet1"` for rename operations fail silently on PT-BR accounts. The `batchUpdate` to rename `Sheet1 → Clientes` succeeds with HTTP 200 but does nothing because `Sheet1` doesn't exist.

**Fix:** Always read the actual sheet name first via `spreadsheets().get()`, then use the real `sheetId`:

```python
info = sheets.spreadsheets().get(spreadsheetId=SID).execute()
first_sheet_id = info['sheets'][0]['properties']['sheetId']

sheets.spreadsheets().batchUpdate(spreadsheetId=SID, body={
    'requests': [{
        'updateSheetProperties': {
            'properties': {'sheetId': first_sheet_id, 'title': 'Clientes'},
            'fields': 'title'
        }
    }]
}).execute()
```

## PROCV Case Sensitivity

Python's `in` operator is case-sensitive:

```python
"MARIA" in "XPerformance_Maria_Oliveira.pdf"   # → False
"Maria" in "XPerformance_Maria_Oliveira.pdf"   # → True
```

When matching planilha IDs against filenames:
- Use consistent casing across planilha and filenames
- Or normalize both sides: `linha[0].lower() in identificador_relatorio.lower()`

## Service Account + User OAuth Cross-Access

Resources created by user OAuth are invisible to service account until explicitly shared. Always verify access from the automation's perspective, not just the user's.
