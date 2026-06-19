# Scope Recovery — Partial Auth Fix

When `$GSETUP --check` prints `AUTHENTICATED (partial)`, the token exists but
is missing one or more required scopes. This happens when:
- An older token (e.g. calendar-only) was refreshed and overwrote a full-scope token
- The OAuth consent screen was updated after the token was created
- The user revoked individual scopes

## Detection

```bash
GSETUP="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --check
```

Look for `(partial)` in the output. The list of missing scopes follows.

## Recovery

**Do NOT just delete the token and start over.** The client secret is already
configured. Use the revoke-and-re-auth flow:

```bash
# 1. Revoke the current token
$GSETUP --revoke

# 2. Get a fresh auth URL (this generates a new PKCE challenge)
$GSETUP --auth-url
# → Returns JSON with auth_url. Send this URL to the user.

# 3. User visits URL, authorizes ALL requested scopes, gets redirected
#    to http://localhost:1/?code=...&scope=...

# 4. Exchange the code
$GSETUP --auth-code "THE_URL_OR_CODE"

# 5. Verify full auth
$GSETUP --check
# → Should print AUTHENTICATED (no "partial") with all 8 scopes
```

## Scopes Required

The consent screen requests these scopes (must ALL be granted during auth):

| Service | Scope |
|---------|-------|
| Calendar | `https://www.googleapis.com/auth/calendar` |
| Drive | `https://www.googleapis.com/auth/drive` |
| Docs | `https://www.googleapis.com/auth/documents` |
| Sheets | `https://www.googleapis.com/auth/spreadsheets` |
| Gmail read | `https://www.googleapis.com/auth/gmail.readonly` |
| Gmail send | `https://www.googleapis.com/auth/gmail.send` |
| Gmail modify | `https://www.googleapis.com/auth/gmail.modify` |
| Contacts | `https://www.googleapis.com/auth/contacts.readonly` |

## Prevention

After a successful re-auth, the token auto-refreshes. The scopes are
preserved across refreshes as long as the consent screen remains unchanged.
If you update the OAuth client in Google Cloud Console, re-auth is required.
