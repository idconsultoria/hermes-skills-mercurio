# Sheets Column Padding — DataFrame from Varied Column Counts

## Problem

Google Sheets API trims trailing empty cells from each row. When reading a range like `Processos!A3:AK`:

- The header row (row 3) returns 37 values — all columns populated
- Data rows with trailing empty cells return fewer values (e.g., 14 instead of 37)

Pandas `pd.DataFrame(data_rows, columns=headers)` raises:
```
ValueError: 37 columns passed, passed data had 14 columns
```

## Fix

Pad each data row to match the header length before creating the DataFrame:

```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd

# Read raw data
result = sheets_svc.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='SheetName!A1:AK',
    valueRenderOption='FORMATTED_VALUE'
).execute()
all_data = result.get('values', [])

headers = all_data[0]
data_rows = all_data[1:]

# Pad each row to header length
for i in range(len(data_rows)):
    if len(data_rows[i]) < len(headers):
        data_rows[i] = list(data_rows[i]) + [''] * (len(headers) - len(data_rows[i]))

df = pd.DataFrame(data_rows, columns=headers)
```

## Alternative: Write-back padding

To fix the sheet permanently (so future reads don't need padding), pad all rows via batch update:

```python
updates = []
for i, row in enumerate(data_rows):
    row_num = i + START_ROW
    if len(row) < len(headers):
        padded = list(row) + [''] * (len(headers) - len(row))
        updates.append({
            'range': f'SheetName!A{row_num}:{LAST_COL}{row_num}',
            'values': [padded]
        })

if updates:
    sheets_svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'data': updates, 'valueInputOption': 'USER_ENTERED'}
    ).execute()
```

## Root cause

`values().update()` with `valueInputOption='USER_ENTERED'` only writes explicitly provided values. Trailing empty strings from the update array may be trimmed by Sheets. Use `valueInputOption='RAW'` to preserve empty cells, or pad on read as shown above.
