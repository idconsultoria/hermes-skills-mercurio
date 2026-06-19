# Cloning and Resetting a Google Sheets Spreadsheet

Multi-step workflow for cloning an existing spreadsheet (with all its tabs, headers, and
structural rows), moving it to a target Drive folder, and clearing all data rows while
preserving template structure.

## Step 1: Copy the spreadsheet

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file('/path/to/token.json')
drive_service = build('drive', 'v3', credentials=creds)

orig_id = 'SOURCE_SPREADSHEET_ID'
copy_body = {'name': 'New Spreadsheet Name'}
copied = drive_service.files().copy(fileId=orig_id, body=copy_body, fields='id, name').execute()
new_id = copied['id']
```

## Step 2: Move to target folder

```python
target_folder = 'TARGET_FOLDER_ID'

# Get current parents
file_meta = drive_service.files().get(fileId=new_id, fields='parents').execute()
prev_parents = ','.join(file_meta.get('parents', []))

# Move
drive_service.files().update(
    fileId=new_id,
    addParents=target_folder,
    removeParents=prev_parents,
    fields='id, parents'
).execute()
```

## Step 3: Clear data per sheet

Each sheet (tab) may have a different number of structural rows to preserve.
Inspect first, then clear:

```python
sheets_service = build('sheets', 'v4', credentials=creds)

# Read first rows to understand structure
result = sheets_service.spreadsheets().values().get(
    spreadsheetId=new_id,
    range='SheetName!A1:H10'
).execute()

# Clear data rows while keeping headers
sheets_service.spreadsheets().values().clear(
    spreadsheetId=new_id,
    range='SheetName!A{start}:{end}'
).execute()
```

## Pitfalls

- **`drive.files().copy()` copies ALL sheets** — including hidden tabs. Review all tabs after cloning.
- **Merged cells and visual template rows** — Google Sheets often has 2-3 rows of visual scaffolding above the actual column headers. Inspect with `A1:H10` before clearing to avoid destroying layout.
- **`values().clear()` is a hard delete** — it removes values and formatting in the cleared range. If you need to keep formatting, use `values().update()` with empty strings instead.
- **The `Processos!A3` range notation** uses the sheet tab name + A1 notation. Include the `!` separator. If the sheet name contains spaces or special chars, wrap it in single quotes: `'My Sheet'!A1:Z10`.
