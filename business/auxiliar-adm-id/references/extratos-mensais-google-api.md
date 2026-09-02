# Google API — download de anexo do Gmail e upload no Drive (extratos mensais)

Técnica validada em 20/08/2026 ao arquivar extratos/faturas de julho/2026. Atualizada 01/09/2026 para HERMES_HOME=/opt/mercurio-data.
**Muitos anexos NÃO vêm embutidos no corpo da mensagem** — vêm como `attachmentId`
separado, exigindo uma 2ª chamada à API para baixar. Código mínimo que funciona:

## Download do anexo (Gmail API)

```python
import json, base64, os, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 01/09/2026 — HERMES_HOME correto é /opt/mercurio-data, não /opt/data
# NUNCA usar gustavomelloenciv@gmail.com — usar exclusivamente admin e gustavo.idteal
import os
HH = os.environ.get("HERMES_HOME", "/opt/mercurio-data")
TOKEN_GMAIL = f"{HH}/google_token.gustavo_idteal.json"   # caixa de origem do email (gustavo.idteal@gmail.com)
d=json.loads(open(TOKEN_GMAIL).read())
if not d.get("type"): d["type"]="authorized_user"
c=Credentials.from_authorized_user_info(d, d.get("scopes"))
if c.expired and c.refresh_token: c.refresh(Request())
svc=build('gmail','v1',credentials=c)

mid, outdir = 'MSG_ID', '/tmp'
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
            raw = base64.urlsafe_b64decode(data + '===') if data else None
            if not raw and attid:
                a=svc.users().messages().attachments().get(
                    userId='me', messageId=mid, id=attid).execute()
                raw=base64.urlsafe_b64decode(a['data'] + '===')
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
# Token de upload = $HERMES_HOME/google_token.json (admin@idconsultoria.ai) — NUNCA gustavomelloenciv
d2=json.loads(open(f"{HH}/google_token.json").read())
if not d2.get("type"): d2["type"]="authorized_user"
c_drive=Credentials.from_authorized_user_info(d2, d2.get("scopes"))
if c_drive.expired and c_drive.refresh_token: c_drive.refresh(Request())
svc_d=build('drive','v3',credentials=c_drive)
def upload(path, parent, mime):
    from googleapiclient.http import MediaFileUpload
    media=MediaFileUpload(path, mimetype=mime, resumable=True)
    return svc_d.files().create(
        body={'name':os.path.basename(path),'parents':[parent]},
        media_body=media, fields='id,name').execute()
```

- **Token de upload = `google_token.json` (admin@idconsultoria.ai)** em `$HERMES_HOME`, NÃO o fallback `gustavomelloenciv`.
- **Parâmetro de MIME:** a lib googleapiclient usa `media_mime_type` (snake_case), não
  `media_mimeType` (camelCase) — este último dá `TypeError: unexpected keyword argument` (usar `MediaFileUpload` com `mimetype=`).
- **MIMEs por extensão usados:**
  | Ext | MIME |
  |---|---|
  | `.pdf` | `application/pdf` |
  | `.csv` | `text/csv` |
  | `.txt` | `text/plain` |
  | `.ofx` | `application/octet-stream` |
  | `.xlsx`| `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |

## MIMEs dos anexos de email (ok para download)

- Inter: `application/octet-stream` (CSV/TXT/PDF/OFX) — o filename diz a extensão real.
- Nubank: `application/pdf`, `application/x-ofx`, `text/csv`.
- Mercado Pago: `application/pdf`, `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (xlsx).

## Verificação pós-upload (obrigatória)

Ler de volta a lista de arquivos da pasta-alvo (`files.list` com `'<id>' in parents`)
e conferir nome x quantidade, em vez de confiar no retorno do `create` (que confirma só
o upload, não a localização).

## Auditoria 01/09/2026

Tokens corretos não encontrados no disco — apenas fallback `gustavomelloenciv@gmail.com` em `$HERMES_HOME/google_token.json`. Procedimento vetado até recriar OAuth para `admin@idconsultoria.ai` e `gustavo.idteal@gmail.com`.
