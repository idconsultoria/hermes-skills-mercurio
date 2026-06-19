# Google Drive `trashed=false` Pitfall — Reproduction Recipe

## Setup

Any folder with files that were created, then deleted (moved to trash),
while the API query uses `supportsAllDrives=True` without `trashed=false`.

## Reproduction

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_service_account_file('sa.json', scopes=['.../drive'])
drive = build('drive', 'v3', credentials=creds)
FOLDER_ID = '<folder_with_deleted_files>'

# Buggy query (returns trashed items)
r = drive.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name, trashed, parents)",
    pageSize=1000,
    supportsAllDrives=True,
    includeItemsFromAllDrives=True
).execute()

for f in r.get('files', []):
    status = 'TRASH' if f.get('trashed') else 'ACTIVE'
    print(f"[{status}] {f['name']}  parents={f.get('parents', [])}")
```

## Expected output (buggy)

```
[TRASH] CVT - Gestao de eventos.m4a  parents=['<FOLDER_ID>']
[TRASH] CVT - Gestao de salas.m4a    parents=['<FOLDER_ID>']
...
[ACTIVE] CVT - Abertura de Turma.m4a  parents=['<FOLDER_ID>']
```

## Fix

Add `and trashed=false` to the query:

```python
q=f"'{FOLDER_ID}' in parents and trashed=false"
```

Now only the active file is returned.

## Root cause

Deleting a file via Drive API or UI moves it to Trash but preserves the
`parents` field. With `supportsAllDrives=True`, the API no longer excludes
trashed items by default — you must explicitly filter them.
