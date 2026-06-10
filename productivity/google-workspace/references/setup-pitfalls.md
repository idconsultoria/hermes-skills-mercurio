## Setup Pitfalls

### PEP 668 (externally-managed environment)
Debian/Ubuntu 2023+, Nix, and some Docker images ship with `PEP 668` — pip refuses to install globally.

**Symptom:** `No module named pip` or `externally-managed-environment` error from setup.py.

**Fix:** Create a venv with uv, then run ALL google scripts with the venv Python:
```bash
uv venv ~/.hermes/venvs/google
uv pip install --python ~/.hermes/venvs/google/bin/python \
  google-api-python-client google-auth-oauthlib google-auth-httplib2
```
Then use:
```bash
GSETUP="~/.hermes/venvs/google/bin/python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/setup.py"
GAPI="~/.hermes/venvs/google/bin/python ${HERMES_HOME}/skills/productivity/google-workspace/scripts/google_api.py"
```

### 403 access_denied at auth step
The OAuth client was created in Testing mode but the user's Google account was not added as a test user.

**Fix:** User navigates to:
console.cloud.google.com → Search "Audience" (or "Público-alvo") → OAuth consent screen → Test users → Add users → enter their email → Save.

The direct link `https://console.cloud.google.com/auth/audience` may redirect to login first. After adding the user, retry with the SAME auth URL.

### Client ID/Secret as raw values (no JSON file)
If the user pastes `client_id` + `client_secret` as bare strings instead of a downloaded JSON file:

Write a valid Desktop OAuth JSON file yourself:
```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    "redirect_uris": ["http://localhost"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```
Save it, then run `--client-secret` against it.

### Sheets `get` requires full A1 range
Passing a bare sheet name like `"Sheet1"` fails with `"Unable to parse range: Sheet1"`.

**Fix:** Always use A1 notation: `"Sheet1!A1:Z100"` or `"A1:Z100"`.

### No `--services` flag in setup.py
The setup script has no `--services` or `--format` flags. It always requests ALL scopes (Gmail read/send/modify, Calendar, Drive, Contacts, Sheets, Docs). If the user wants minimal scopes, they must create a restricted OAuth client in Cloud Console instead.
