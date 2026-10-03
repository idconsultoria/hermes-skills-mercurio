# Drive e Gmail — API na prática (receitas e erros reais)

## 0 · Carregamento do token (sempre o certo)

```python
import os, json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
HH = os.environ.get("HERMES_HOME", "/opt/mercurio-data")
d = json.loads(open(f"{HH}/google_token.json").read()); d.setdefault("type", "authorized_user")
c = Credentials.from_authorized_user_info(d, d.get("scopes"))   # usa os escopos que ele já tem
if not c.valid:
    c.refresh(Request())
dr = build("drive", "v3", credentials=c)
g  = build("gmail", "v1", credentials=c)
```

Venv com `googleapiclient` neste host: `$HERMES_HOME/id-nfse-motor/.venv/bin/python`.
Confirme antes: `g.users().getProfile(userId="me").execute()["emailAddress"]` tem que ser
`admin@idconsultoria.ai` para demanda da ID.

## 1 · Criar pasta e subpastas (idempotente)

```python
FOLDER = "application/vnd.google-apps.folder"
r = dr.files().list(q=f"name = '{nome}' and '{PAI}' in parents and trashed=false",
                    fields="files(id)", pageSize=1).execute()
pid = r["files"][0]["id"] if r.get("files") else dr.files().create(
    body={"name": nome, "mimeType": FOLDER, "parents": [PAI]}, fields="id,name").execute()["id"]
```

Sempre checar existência antes: rodar o `create` duas vezes cria duas pastas com o mesmo
nome, e o Drive **permite** duplicatas com mesmo nome.

## 2 · Mover (dois passos, nunca um)

```python
f = dr.files().get(fileId=fid, fields="name,parents").execute()
dr.files().update(fileId=fid, addParents=DEST, fields="id").execute()          # passo 1
for p in [x for x in dr.files().get(fileId=fid, fields="parents").execute().get("parents", [])
          if x != DEST]:
    dr.files().update(fileId=fid, removeParents=p, fields="id").execute()    # passo 2, 1 por vez
```

**Erro:** `HttpError 404 ... File not found: ['<pai>']` na chamada única com `addParents`
+ `removeParents`. Causa: pai compartilhado. Separe os passos.

**Armadilha:** se o passo 2 falhar e o passo 1 passou, o arquivo fica em **duas** pastas. E
se o `removeParents` rodar num pai e o arquivo passar a ter só o `Meu Drive`, ele some do
fluxo principal. **Sempre relistar a pasta depois.**

## 3 · Renomear (patch separado)

```python
dr.files().update(fileId=fid, body={"name": novo_nome}, fields="id,name").execute()
```

**Erro:** `TypeError: files.update() got an unexpected keyword argument 'name'` — `name` não
é parâmetro de `update`; vai no `body`.

## 4 · Mover arquivo de outro dono → 403 (copie)

**Erro:** `HttpError 403` ao mover. Diagnóstico: `files.get(fields="owners,capabilities")` —
a conta da ID tem `writer`, o dono é outra conta. **Writer não move arquivo alheio.**

```python
novo = dr.files().copy(fileId=fid, body={"name": nome, "parents": [DEST]},
                       fields="id,name").execute()
```

O original fica onde estava: preserva tudo e é reversível. Transferir posse de arquivo de
conta pessoal é decisão do principal, não nossa.

**403 ≠ "sem permissão para ler".** Se o `files.get` responde e devolve `owners`, você leu
sim; o 403 é só na escrita de *parenting*.

## 5 · Subir arquivo local

```python
from googleapiclient.http import MediaFileUpload
meta = dr.files().create(body={"name": nome_destino, "parents": [DEST],
                             "mimeType": mime}, fields="id").execute()
up = dr.files().update(fileId=meta["id"],
                       media_body=MediaFileUpload(caminho, mimetype=mime, resumable=True),
                       fields="id,name,size").execute()
```

**Erro:** `TypeError: media_filename must be str or MediaUpload` quando se passa o file
handle direto. Use `MediaFileUpload`.

**Verificação obrigatória:** `size` não-zero e `get_media` com o mesmo tamanho do disco.
Upload interrompido deixa item de 0 bytes, e ele aparece na listagem como se estivesse lá.

**Não confunda latência com arquivo perdido.** Logo após o `create`, o `files.list` da pasta
alvo pode **não devolver o item recém-criado** (indexação do Drive é eventual). O sintoma é
um arquivo que você acabou de subir, com tamanho correto no retorno, "sumindo" da
verificação. Antes de reenviar — reenviar cria duplicata, que é pior que a falsa falha —
confirme: `files.get(fileId, fields="id,name,size,parents,trashed")` e busca global
`name = '<nome>' and trashed=false`.

**Verificação forte: SHA-256 da origem contra o Drive.** Para lote que importa (comprovantes
fiscais, extratos), baixe o que está no Drive com `files.get_media(fileId).execute()` e
compare `hashlib.sha256` com os bytes da origem. Presença não é integridade — tamanho igual
com conteúdo diferente passa em qualquer conferência por tamanho.

**`drv.users()` não existe na Drive v3.** `AttributeError: 'Resource' object has no
attribute 'users'` é bug de script, não token ruim. O e-mail da conta sai de
`drv.about().get(fields="user").execute()["user"]["emailAddress"]`.

**`fields` com caminho de sub-objeto precisa existir de fato.** Um `fields` montado errado
(ao tentar ler fórmulas, p.ex. `sheets(data.rowData.values.formulaValue)`) volta
`400 Error expanding 'fields' parameter ... Cannot find matching fields for path`. Para ver
fórmulas de célula, use `values().get(..., valueRenderOption="FORMULA")` em vez de tentar
expandir `rowData` — o `GridData` expõe `userEnteredValue`, não `formulaValue`.

## 6 · Compartilhar

```python
dr.permissions().create(fileId=fid, sendNotificationEmail=True,
    body={"type": "user", "role": "commenter", "emailAddress": email}).execute()
```

`commenter` = lê e comenta (o que o cliente precisa para marcar o texto). `reader` só lê.

```python
ps = dr.permissions().list(fileId=fid, fields="permissions(emailAddress,role)", pageSize=50).execute()
```

**Erro 400 `invalidSharingRequest`** para e-mail sem conta Google: `sendNotificationEmail`
convida, mas **não garante** o acesso. Confira a lista um a um.

## 7 · Rascunho na thread certa (Gmail)

```python
from email.message import EmailMessage
import base64
orig = g.users().messages().get(userId="me", id=MSG_ANTERIOR, format="metadata",
                                metadataHeaders=["Message-ID", "References"]).execute()
oh = {x["name"]: x["value"] for x in orig["payload"]["headers"]}

m = EmailMessage()
m["From"] = "Principal ID Consultoria <admin@idconsultoria.ai>"
m["To"] = ", ".join(PARA)
m["Cc"] = ", ".join(CC)                      # tem que estar AQUI, na criação
m["Subject"] = "Re: " + assunto_da_thread    # idêntico ao da thread, com o Re:
m["In-Reply-To"] = oh["Message-ID"]
m["References"] = (oh.get("References", "") + " " + oh["Message-ID"]).strip()
m.set_content(corpo, subtype="plain", charset="utf-8")

raw = base64.urlsafe_b64encode(m.as_bytes()).decode()
g.users().drafts().create(userId="me",
    body={"message": {"raw": raw, "threadId": THREAD_ID}}).execute()
```

**Três condições para cair na thread original** (a API exige as três): `threadId` no corpo do
Draft + `References`/`In-Reply-To` em RFC 2822 + `Subject` idêntico ao da thread. Sem
`threadId`, o rascunho nasce em thread nova, sozinho.

**Erro:** `messages().modify(..., {"addHeaders": [...]})` → `400 No label or Classification
Label updates provided`. `modify` só mexe em `labelIds`/`classificationLabelValues`, **não**
em headers. Todo header vai no `raw` da criação.

**Erro:** `drafts.get(..., metadataHeaders=[...])` → `TypeError: unexpected keyword argument`.
`drafts.get` só aceita `format`, `id`, `userId`. Leia sem e filtre `payload.headers` à mão.
Já `messages.get` aceita `metadataHeaders`.

**Apague o rascunho anterior** se refez: duplicata na caixa é pior que rascunho faltando.

## 8 · Verificação do rascunho/enviado

```python
msg = g.users().drafts().get(userId="me", id=DRAFT_ID).execute()["message"]
h = {x["name"]: x["value"] for x in msg["payload"]["headers"]}
assert "DRAFT" in msg["labelIds"] and "SENT" not in msg["labelIds"]
assert msg["threadId"] == THREAD_ID
```

O corpo chega em base64url no `body.data` (recursivo pelos `parts` para mensagens
multipart) — decodifique e compare byte a byte com o texto aprovado, não "olhando".

## 9 · Localizar documentos espalhados

```python
for termo in ["credencial", "design system", "prototipo", "ementa"]:
    r = dr.files().list(q=f"fullText contains '{termo}' and trashed=false",
                        fields="files(id,name,mimeType,modifiedTime)", pageSize=30).execute()
```

`fullText contains` acha por **conteúdo**, não por nome — é o jeito de achar documento cujo
nome não tem relação com o assunto. Em pasta grande, sempre combinando com
`'{PAI}' in parents`.

**Desambiguar cópias:** com N arquivos de mesmo nome, compare `modifiedTime`, nº de blocos
do documento e presença dos marcadores de conteúdo (um PRD completo tem os requisitos
numerados; os rascunhos de teste, não).

## 10 · Ler Doc preservando tabela

Ao ler, `paragraph` e `table` são irmãos em `body.content` — iterar só `paragraph` devolve
documento "vazio" quando o miolo é tabela. Percorra os dois e monte as tabelas como
`linha | coluna`.

