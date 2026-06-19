# Google Sheets Cell Limit (50K chars)

## Error transcript

```
googleapiclient.errors.HttpError: <HttpError 400 when requesting
https://sheets.googleapis.com/v4/spreadsheets/{ID}/values/Processos%21Q25%3AAK?valueInputOption=USER_ENTERED&alt=json
returned "Your input contains more than the maximum of 50000 characters in a single cell.".
Details: "Your input contains more than the maximum of 50000 characters in a single cell.">
```

## Reproduction

1. Generate a long transcription (>50K chars) via Gemini diarization
2. Attempt to write it to a Google Sheets cell via `values().update()`
3. Cell limit is per-cell, not per-request

## Fix location

`agemini/conectores/google_sheets.py:89-94` — truncation in `atualizar_planilha()`.

## Google Drive Trashed Items

### Error behavior

Query `q=f"'{folder_id}' in parents"` with `supportsAllDrives=True` and
`includeItemsFromAllDrives=True` returns files where `trashed: True`, as long
as the `trashed=false` filter is absent.

### Reproduction

```python
# Returns 8 files (7 trashed + 1 active)
drive.files().list(
    q=f"'{FOLDER_ID}' in parents",  # no trashed=false
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

# Returns 1 file (correct)
drive.files().list(
    q=f"'{FOLDER_ID}' in parents and trashed=false",
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()
```

Verified on: Google Drive API v3, 2026-06-18, service account.

### Fix location

`agemini/conectores/google_drive.py:230` — added `and trashed=false`.
