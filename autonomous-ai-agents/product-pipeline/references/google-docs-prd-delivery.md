# Google Docs PRD Delivery

Quando o usuário pedir o PRD em formato Google Doc (compartilhável para comentários),
seguir este fluxo.

## Pré-requisitos

- Google Workspace OAuth configurado (token em `/opt/data/google_token.json`)
- Venv Google em `/opt/data/venvs/google/`
- API scripts em `/opt/data/skills/productivity/google-workspace/scripts/`
- Scripts auxiliares em `/opt/data/google_oauth_gen.py` + `/opt/data/google_oauth_exchange.py`

## Fluxo

### 1. Verificar token

```bash
SETUP_PY="/opt/data/skills/productivity/google-workspace/scripts/setup.py"
/opt/data/venvs/google/bin/python "$SETUP_PY" --check-live
```

Se retornar `LIVE_CHECK_OK`, pular para passo 3.
Se retornar `TOKEN_REVOKED` ou `NOT_AUTHENTICATED`, seguir passo 2.

### 2. Re-autenticação OAuth com PKCE

⚠️ **Problema conhecido:** O `setup.py --auth-url` gera URL sem salvar o PKCE `code_verifier`. 
A troca do código falha com `Missing code verifier`. Usar fluxo alternativo:

**Passo 2a — Gerar URL com PKCE salvo:**

```bash
/opt/data/venvs/google/bin/python /opt/data/google_oauth_gen.py
```

Isso gera a URL e salva o estado em `/opt/data/google_oauth_state.json`.

**Passo 2b — Usuário abre a URL, autoriza e cola o redirect.**

**Passo 2c — Trocar código por token:**

```bash
/opt/data/venvs/google/bin/python /opt/data/google_oauth_exchange.py "URL_DO_REDIRECT"
```

Isso salva o novo token e já cria um documento de teste.

**Se os scripts não existirem**, recriar com o conteúdo padrão em `references/code/google-oauth-scripts/`.

### 3. Criar o Google Doc

```bash
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI docs create --title "PRD NomeDoProjeto v1.x"
```

O comando retorna `documentId` e `url`.

### 4. Popular com conteúdo do PRD

**Opção direta — Python script com batchUpdate:**

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DOC_ID = "ID_DO_DOC"
creds = Credentials.from_authorized_user_file(
    "/opt/data/google_token.json",
    ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"],
)

with open("product/management/PRD.md") as f:
    prd = f.read()

docs = build("docs", "v1", credentials=creds)

# Clear existing content
doc = docs.documents().get(documentId=DOC_ID).execute()
end = doc["body"]["content"][-1]["endIndex"]
docs.documents().batchUpdate(documentId=DOC_ID, body={
    "requests": [{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1}}}]
}).execute()

# Insert new content
docs.documents().batchUpdate(documentId=DOC_ID, body={
    "requests": [{"insertText": {"location": {"index": 1}, "text": prd}}]
}).execute()
```

O conteúdo fica como markdown puro (legível). Se quiser formatação rica (headings, bold,
tabelas), é necessário parsear o markdown e aplicar estilos via requests adicionais.

### 5. Compartilhar para comentários

```bash
GAPI="/opt/data/venvs/google/bin/python .../google_api.py"
$GAPI drive share DOC_ID --type anyone --role commenter
```

**Sempre usar `--role commenter`** (não `reader` ou `writer`) para permitir que a equipe
adicione comentários sem editar o documento original.

### 6. Entregar link ao usuário

Enviar o link `https://docs.google.com/document/d/{DOC_ID}` via texto no chat.

---

## Fluxo Reverso: Sincronizar Edições do Google Docs para o PRD Local (Sync-Back)

> Quando o usuário disser "consulte o doc e atualize o PRD local" ou equivalente.

### 1. Extrair texto completo do Google Doc

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DOC_ID = "ID_DO_DOC"
creds = Credentials.from_authorized_user_file("/opt/data/google_token.json", ["https://www.googleapis.com/auth/documents"])
service = build("docs", "v1", credentials=creds)
doc = service.documents().get(documentId=DOC_ID).execute()

parts = []
for item in doc.get("body", {}).get("content", []):
    if "paragraph" in item:
        for elem in item["paragraph"].get("elements", []):
            if "textRun" in elem:
                parts.append(elem["textRun"].get("content", ""))
        if item["paragraph"].get("elements"):
            parts.append("\n")

with open("/tmp/prd-google.txt", "w") as f:
    f.write("".join(parts))
```

### 2. Comparar com o PRD local e mesclar mudanças

O conteúdo do Google Doc está em **texto puro** (sem markdown). Já o PRD local está
em **markdown formatado**. Para mesclar:

1. Ler o texto extraído do Google Doc e identificar **mudanças significativas**:
   - Seções novas (ex: "5.4 Roadmap: Alpha 0.0.2")
   - Renomeações (ex: "MVP" → "Alpha 0.0.1")
   - Features movidas entre versões (ex: LLM Wiki V3 → V2)
   - Decisões registradas pela equipe
2. Aplicar essas mudanças no PRD markdown local, preservando a formatação markdown
   existente (tabelas, negrito, listas).
3. Atualizar o histórico de atualizações no PRD.md com:
   ```markdown
   | DATA | Equipe ID (edição no Google Docs) | PRD vX.Y — descrição das mudanças |
   ```
4. Bump version no cabeçalho.

### 3. Padrões comuns de edição da equipe no Google Docs

| Mudança típica | Como refletir no PRD.md |
|----------------|------------------------|
| Renomeação de seção (ex: "MVP" → "Alpha 0.0.1") | Atualizar headings markdown |
| Nova seção adicionada | Criar seção markdown equivalente |
| Feature movida entre versões | Atualizar tabelas V2/V3 e "O que NÃO está no MVP" |
| Conteúdo truncado (tabelas vazias) | Preservar markdown local (a estrutura está no .md) |
| Decisão da equipe | Adicionar ao Anexo de Decisões |

### 4. Re-enviar para o Google Doc (se solicitado)

Após mesclar as edições, NÃO sobrescrever o Google Doc automaticamente — a equipe
pode estar usando o doc como fonte da verdade. Apenas atualizar se o usuário
explicitamente pedir.

---

## Notas

- **Publicação do app**: Se o app Google Cloud estiver em modo "Testing", o token
  expira em ~7 dias. Publicar o app em `console.cloud.google.com/apis/credentials/consent`
  → "Publish App" para que refresh tokens NÃO expirem mais.
- **Escopos necessários para Docs**: `https://www.googleapis.com/auth/documents`
  e `https://www.googleapis.com/auth/drive`. Se o token existente não incluir esses
  escopos, re-autenticar com escopos explícitos.
- O fluxo PKDE acima contorna o bug do `setup.py` que não persiste o `code_verifier`.
- Os scripts `google_oauth_gen.py` e `google_oauth_exchange.py` são reutilizáveis.
- **Não sobrescrever o Google Doc** com versão local sem autorização do usuário.
