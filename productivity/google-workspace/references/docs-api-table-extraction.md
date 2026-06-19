# Extracting Tables from Google Docs via REST API

The `gws docs get` / `google_api.py docs get` command returns document body as **plain text only** — tables are silently stripped, losing both structure and cell content.

To extract tables (e.g., action-item tables from meeting minutes), use the Google Docs REST API directly:

```python
import json, urllib.request

DOC_ID = 'your-doc-id'

with open('/opt/data/google_token.json') as f:
    token_data = json.load(f)

access_token = token_data.get('token')
headers = {'Authorization': f'Bearer {access_token}'}

url = f'https://docs.googleapis.com/v1/documents/{DOC_ID}'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
doc = json.loads(resp.read())

content = doc['body']['content']
for elem in content:
    if 'table' in elem:
        rows = elem['table']['tableRows']
        for row in rows:
            cells = row['tableCells']
            row_data = []
            for cell in cells:
                cell_text = ''
                for ce in cell.get('content', []):
                    if 'paragraph' in ce:
                        for pe in ce['paragraph'].get('elements', []):
                            if 'textRun' in pe:
                                cell_text += pe['textRun'].get('content', '')
                row_data.append(cell_text.strip())
            print(' | '.join(row_data))
```

## Table Structure in the API

Each table element has:
- `tableRows[]` → each row has:
  - `tableCells[]` → each cell has:
    - `content[]` → paragraph elements with textRun content
    - `tableCellStyle` → cell formatting

## Checking for Lists (Bullets/Checkboxes)

The document has a top-level `lists` key containing list definitions with glyph types:

```python
if 'lists' in doc_json:
    for lid, ldata in doc_json['lists'].items():
        props = ldata['listProperties']
        # nestingLevels[].glyphSymbol = checkbox state
```

## Checkbox Limitations

Google Docs checklists use custom font glyphs (U+E907) for unchecked boxes. The API does not expose checked/unchecked state as structured data — only the raw character is returned. If you need checkbox state, use the visual rendering (screenshot + vision analysis) or ask the user to export to markdown.

## Usage Context

This technique was developed when the `Ata de Reunião de Operações` (15/06/2026) had all action items in a table invisible to the standard docs command. The table had columns: Atividade/Ação, Responsável, Prazo, Status (with checkboxes).
