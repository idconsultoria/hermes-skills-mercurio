# Extraindo Tabelas e Checkboxes de Google Docs

## O Problema

O comando `GAPI docs get DOC_ID` retorna o corpo do documento como **string de texto plana** — tabelas, listas e checkboxes são perdidos. O conteúdo de tabelas aparece como texto corrido, e checkboxes viram glifos Unicode PUA (`\ue907`) sem estado estrutural.

## Solução: REST API Direta

Para ler tabelas e checkboxes, use a Google Docs REST API diretamente via Python com o token de acesso:

```python
import json, urllib.request

DOC_ID = 'seu_documento_id'
with open('/opt/data/google_token.json') as f:
    token_data = json.load(f)

access_token = token_data.get('token')
headers = {'Authorization': f'Bearer {access_token}'}

url = f'https://docs.googleapis.com/v1/documents/{DOC_ID}'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
doc = json.loads(resp.read())

content = doc['body']['content']
```

## Estrutura dos Elementos

Cada elemento em `body.content` pode ser:

- **`paragraph`** — texto normal. Buscar `textRun.content` dentro de `paragraph.elements[]`
- **`table`** — contém `tableRows[] → tableCells[] → content[]` (cada cell tem paragraphs)
- **`sectionBreak`** — quebra de seção

## Extraindo Tabelas

```python
for elem in content:
    if 'table' in elem:
        table = elem['table']
        for row in table.get('tableRows', []):
            cells = row.get('tableCells', [])
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

## Checkboxes

Checklists no Google Docs usam glifos Unicode na **Private Use Area** (PUA). O caractere `\ue907` (U+E907) é renderizado como uma caixa de seleção por fontes específicas do Google.

**Limitação conhecida:** A API REST NÃO expõe o estado marcado/desmarcado como dado estruturado para checkboxes inseridos via interface de checklist do Google Docs. O texto retornado é idêntico (`\ue907`) para ambos os estados. Se o documento usa checkboxes com estados diferentes, a única forma de ler os estados é:

1. **Visão humana** — abrir o documento e verificar visualmente
2. **Screenshot + visão computacional** — capturar imagem e analisar com modelo de visão
3. **Solicitar ao autor** que exporte os estados manualmente

## Documentos com Listas

Listas (bullet points, numeração) aparecem em `doc.get('lists', {})`. Cada lista tem `listProperties.nestingLevels[]` com `glyphSymbol` e `glyphType`.

```python
lists = doc.get('lists', {})
for lid, ldata in lists.items():
    print(f'Lista {lid}: {json.dumps(ldata["listProperties"], ensure_ascii=False)[:300]}')
```

## Exemplo Completo

Ver `bridge.js` workflow ou executar:
```bash
/opt/data/venvs/google/bin/python3 /caminho/para/seu_script.py
```

Sempre use o venv do Google (`/opt/data/venvs/google/bin/python3`) — o system python não tem `googleapiclient`.
