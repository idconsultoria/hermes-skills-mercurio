# Gmail API — responder na thread e verificar o envio

Receita usada para responder a um interlocutor externo mantendo a conversa e provando o que saiu.
Tokens da ID vivem em `$HERMES_HOME/google_token.json` (por conta; ex.: `admin@idconsultoria.ai`,
`gustavo.idteal@gmail.com` — o segundo para assuntos fiscais). Escopos: Gmail + Drive.

## 1. Montar o serviço

```python
creds = Credentials(tok["token"], refresh_token=tok.get("refresh_token"),
                    token_uri=tok["token_uri"], client_id=tok["client_id"],
                    client_secret=tok["client_secret"], scopes=tok.get("scopes"))
gmail = build("gmail", "v1", credentials=creds)
```

Confirme a conta antes de enviar: `gmail.users().getProfile(userId="me").execute()` → `emailAddress`.

## 2. Achar a conversa e o Message-ID do interlocutor

```python
r = gmail.users().messages().list(userId="me", q="<assunto ou remetente>").execute()
msg = gmail.users().messages().get(userId="me", id=r["messages"][0]["id"], format="full").execute()
hd = {h["name"].lower(): h.get("value", "") for h in msg["payload"]["headers"]}
thread_id = msg["threadId"]          # use ESTE para responder
reply_to  = hd["message-id"]         # header, não o id interno da API
refs      = (hd.get("references", "") + " " + hd["message-id"]).strip()
```

Percorrer a thread inteira: `gmail.users().threads().get(userId="me", id=thread_id, format="full")`
→ `messages[]` com `payload.headers` (From/To/Cc/Subject/Date) e `internalDate` (epoch em ms).

## 3. Enviar como resposta

```python
import base64
from email.message import EmailMessage
m = EmailMessage()
m["From"] = "Nome Exibido <email@dominio>"     # identidade que o cliente já conhece
m["To"] = "interlocutor@dominio"
m["Subject"] = hd.get("subject", "")          # manter o Re: existente
m["In-Reply-To"] = reply_to
m["References"] = refs
m.set_content(texto_aprovado)                  # texto aprovado, sem edição
raw = base64.urlsafe_b64encode(m.as_bytes()).decode()
gmail.users().messages().send(userId="me", body={"threadId": thread_id, "raw": raw}).execute()
```

Sem `threadId`, a API cria conversa nova mesmo com `In-Reply-To` preenchido.

## 4. Verificar lendo de volta

```python
s = gmail.users().messages().get(userId="me", id=sent_id, format="full").execute()
hd2 = {h["name"].lower(): h.get("value", "") for h in s["payload"]["headers"]}
# s["threadId"] == thread_id ; hd2["from"], hd2["to"], hd2.get("cc"), hd2["subject"]
# hd2["in-reply-to"] == reply_to ; hd2.get("references") contém a cadeia
```

Extrair o corpo `text/plain` (decodifica `payload.body.data` em base64url; se vier em `parts[]`,
percorra a árvore) e comparar com o texto aprovado por **hash** (ex.: `sha256`), não visualmente.

## Notas de leitura

- `internalDate` é epoch em ms → converter para BRT (UTC-3) ao relatar horário ao principal.
- Duas causas cobrem a maioria dos "não chegou": `threadId` errado (virou conversa nova) ou `From`
  com display name que o cliente não reconhece.
- O corpo que a ID envia não carrega as cópias do lado do cliente: o relatório deve dizer
  explicitamente quem entrou em `Cc`.
