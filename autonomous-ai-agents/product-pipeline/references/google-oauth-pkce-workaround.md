# Google OAuth PKCE Workaround

## Problema

O script `setup.py` do skill google-workspace gera URLs de autenticação OAuth sem
persistir o `code_verifier` PKCE. Quando o usuário autoriza e cola o redirect URL,
a troca falha com:

```
oauthlib.oauth2.rfc6749.errors.InvalidGrantError: (invalid_grant) Missing code verifier.
```

Isso acontece porque o Google OAuth 2.0 agora **exige PKCE** (Proof Key for Code Exchange)
para OAuth clients do tipo "Desktop app". O `code_verifier` gerado no passo 1 (auth URL)
precisa ser o mesmo usado no passo 2 (code exchange).

## Solução

Usar dois scripts Python que salvam o `code_verifier` entre os passos:

### google_oauth_gen.py

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/contacts.readonly",
]

flow = InstalledAppFlow.from_client_secrets_file(
    "/opt/data/google_client_secret.json", SCOPES, redirect_uri="http://localhost"
)

auth_url, _ = flow.authorization_url(
    access_type="offline",
    include_granted_scopes="true",
    prompt="consent",
)

# Save the PKCE verifier for later use
state_data = {
    "code_verifier": flow.code_verifier,
    "client_config": flow.client_config,
    "redirect_uri": flow.redirect_uri,
    "scopes": SCOPES,
}
with open("/opt/data/google_oauth_state.json", "w") as f:
    json.dump(state_data, f, indent=2)

print(auth_url)
```

### google_oauth_exchange.py

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import json, sys, urllib.parse

with open("/opt/data/google_oauth_state.json") as f:
    state = json.load(f)

flow = InstalledAppFlow.from_client_secrets_file(
    "/opt/data/google_client_secret.json",
    state["scopes"],
    redirect_uri=state["redirect_uri"],
)

# Critical: inject the saved code_verifier
flow.code_verifier = state["code_verifier"]
flow.oauth2session.code_verifier = state["code_verifier"]

# Extract code from URL
redirect_url = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
parsed = urllib.parse.urlparse(redirect_url)
code = urllib.parse.parse_qs(parsed.query)["code"][0]

# Exchange
flow.fetch_token(code=code)
creds = flow.credentials

with open("/opt/data/google_token.json", "w") as f:
    f.write(creds.to_json())

print("TOKEN_OK")
```

## Fluxo

1. Roda `google_oauth_gen.py` → gera URL e salva estado
2. Usuário abre URL, autoriza, cola redirect
3. Roda `google_oauth_exchange.py "redirect_url"` → troca código por token

## Token Expiry

- O token de acesso expira após ~1 hora (refresh automático)
- O refresh token expira após ~7 dias sem uso
- Quando `refresh` falha com `invalid_grant: Token has been expired or revoked`,
  o fluxo completo de re-autenticação é necessário
- Os scripts acima são reutilizáveis para re-auth
