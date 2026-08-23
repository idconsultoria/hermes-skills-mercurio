# Google API — download de anexo do Gmail e upload no Drive (extratos mensais)

Técnica validada em 20/08/2026 ao arquivar extratos/faturas de julho/2026.
**Muitos anexos NÃO vêm embutidos no corpo da mensagem** — vêm como `attachmentId`
separado, exigindo uma 2ª chamada à API para baixar. Código mínimo que funciona:

## Download do anexo (Gmail API)

```python
import json, base64, os, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN='/opt/data/google_token.gustavo_idteal.json'   # caixa de origem do email
d=json.loads(open(TOKEN).read())
if not d.get("type"): d["type"]="authorized_user"
c=Credentials.from_authorized_user_info(d, d.get("scopes"))
if c.expired and c.refresh_token: c.refresh(Request())
svc=build('gmail','v1',credentials=c)

mid, outdir = 'MSG_ID', '/caminho/saida'
m=svc.users().messages().get(userId='me', id=mid).execute()

def walk(p):
    if 'parts' in p:
        for pt in p['parts']: walk(pt)
    else:
        fn=p.get('filename','')
        if fn:
            body=p.get('body',{})
            data=body.get('data')
            attid=body.get('attachmentId')      # <-- chave: anexo separado
            raw = base64.urlsafe_b64decode(data) if data else None
            if not raw and attid:
                a=svc.users().messages().attachments().get(
                    userId='me', messageId=mid, id=attid).execute()
                raw=base64.urlsafe_b64decode(a['data'])
            if raw:
                open(os.path.join(outdir,fn),'wb').write(raw)
walk(m['payload'])
```

**Pitfall importante:** com `format='metadata'` o corpo dos anexos NÃO é trazido (o campo
`filename` some / `att` conta como 0). Para listar/download usar `format='full'` (ou o
`.get(...)` sem format), e sempre tratar `attachmentId` — os anexos de Inter/Nubank vêm
separados.

## Upload no Drive (Drive API)

```python
svc_d=build('drive','v3',credentials=c_drive)   # c_drive = token admin_idconsultoria
def upload(path, parent, mime):
    return svc_d.files().create(
        body={'name':os.path.basename(path),'parents':[parent]},
        media_body=path, media_mime_type=mime, fields='id,name').execute()
```

- **Token de upload = `google_token.admin_idconsultoria.json`** (Drive), NÃO o de Gmail.
- **Parâmetro de MIME:** a lib googleapiclient usa `media_mime_type` (snake_case), não
  `media_mimeType` (camelCase) — este último dá `TypeError: unexpected keyword argument`.
- **MIMEs por extensão usados:**
  | Ext | MIME |
  |---|---|
  | `.pdf` | `application/pdf` |
  | `.csv` | `text/csv` |
  | `.txt` | `text/plain` |
  | `.ofx` | `application/octet-stream` |

## MIMEs dos anexos de email (ok para download)

- Inter: `application/octet-stream` (CSV/TXT/PDF/OFX) — o filename diz a extensão real.
- Nubank: `application/pdf`, `application/x-ofx`, `text/csv`.

## Verificação pós-upload (obrigatória)

Ler de volta a lista de arquivos da pasta-alvo (`files.list` com `'<id>' in parents`)
e conferir nome x quantidade, em vez de confiar no retorno do `create` (que confirma só
o upload, não a localização).
