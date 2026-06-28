---
name: google-workspace
description: "Gmail, Calendar, Drive, Docs, Sheets via gws CLI — OAuth2 setup and automation.

Load this skill when you need to automate Google Workspace. Covers gws CLI installation and OAuth2 setup from Google Cloud Console credentials, then using it for Gmail operations, Calendar management, Drive file operations, Docs editing, and Sheets data manipulation."
version: 1.1.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials (downloaded from Google Cloud Console)
metadata:
  hermes:
    tags: [Google, Gmail, Calendar, Drive, Sheets, Docs, Contacts, Email, OAuth]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [himalaya, airtable, ocr-and-documents]
type: ToolIntegration
timestamp: 2026-06-28T05:11:55Z
---

# Google Workspace

Gmail, Calendar, Drive, Contacts, Sheets, and Docs — through Hermes-managed OAuth and a thin CLI wrapper.

## Hermes-specific paths

On this host (Oracle Linux, Hermes container), the scripts and credentials live at:

```bash
GSETUP="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/setup.py"
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"
```

Always verify auth before first use:
```bash
$GSETUP --check
# AUTHENTICATED (partial) → see references/scope-recovery.md
```

## References

- `references/gmail-search-syntax.md` — Gmail search operators (is:unread, from:, newer_than:, etc.)
- `references/setup-pitfalls.md` — PEP 668 workaround, 403 fix, range syntax, client JSON creation
- `references/docs-table-extraction.md` — Como extrair tabelas e checkboxes de Google Docs via REST API (o comando `docs get` perde tabelas e não expõe estado de checkboxes)
- `references/scope-recovery.md` — how to fix partial auth (missing scopes)
- `references/clone-spreadsheet.md` — Clonar planilha via Drive API, mover entre pastas, limpar dados por aba preservando headers
- `references/sheets-column-padding.md` — Fix for "N columns passed, passed data had M columns" when reading Sheets into pandas (API trims trailing empty cells per row)
- `references/service-account-sharing.md` — Cross-account Drive access: service account vs user OAuth visibility (404 on valid IDs, sharing patterns)
- `references/gmail-large-file-delivery.md` — Gmail 25 MB attachment limit and Drive sharing workaround for larger files
- `references/drive-file-organization.md` — Moving files to folders and deduplicating after batch uploads (uses `scripts/drive-move-to-folder.py`)

## Scripts

- `scripts/setup.py` — OAuth2 setup (run once to authorize)
- `scripts/google_api.py` — compatibility wrapper CLI
- `scripts/gws_bridge.py` — bridge for gws CLI backend
- `scripts/drive-move-to-folder.py` — batch-move Drive files to a folder, deduplicating (see `references/drive-file-organization.md`)

## First-Time Setup

The setup is fully non-interactive — you drive it step by step so it works
on CLI, Telegram, Discord, or any platform.

Define a shorthand first:

```bash
GSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"

# On PEP 668 / externally-managed systems (Debian/Ubuntu 2023+, Nix):
# Create a venv and use its Python instead:
#   uv venv ~/.hermes/venvs/google
#   uv pip install --python ~/.hermes/venvs/google/bin/python google-api-python-client google-auth-oauthlib google-auth-httplib2
#   GSETUP="~/.hermes/venvs/google/bin/python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py"
#   GAPI="~/.hermes/venvs/google/bin/python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

### Step 0: Check if already set up

```bash
$GSETUP --check
```

If it prints `AUTHENTICATED`, skip to Usage — setup is already done.

**PEP 668 environments** (Debian/Ubuntu systems where system pip is blocked):
The `setup.py` script calls `python3 -m pip install` which fails on PEP 668 systems.
If `--install-deps` or `--auth-url` fails with "No module named pip" or "externally managed",
create a venv and use it for all Google commands going forward:

```bash
uv venv /path/to/google-venv
/path/to/google-venv/bin/python "$GSETUP" --client-secret /path/to/client_secret.json
/path/to/google-venv/bin/python "$GSETUP" --auth-url
# ... then --auth-code the same way
```

Set a shorthand to avoid typing the venv path every time:

```bash
GAPI="/path/to/google-venv/bin/python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

### Step 1: Triage — ask the user what they need

Before starting OAuth setup, ask the user TWO questions:

**Question 1: "What Google services do you need? Just email, or also Calendar/Drive/Sheets/Docs?"**

- **Email only** → They don't need this skill at all. Use the `himalaya` skill instead — it works with a Gmail App Password (Settings → Security → App Passwords) and takes 2 minutes to set up. No Google Cloud project needed. Load the himalaya skill and follow its setup instructions.

- **Any other combination (Calendar, Drive, Sheets, Docs, etc.)** → Continue with this skill. The setup script uses a fixed full-scope consent screen covering Gmail, Calendar, Drive, Contacts, Sheets, and Docs. There is no `--services` flag — scope narrowing is not supported by the current script. Revoke and create a stripped-down OAuth client in Cloud Console if you need truly minimal scopes.

**Question 2: "Does your Google account use Advanced Protection (hardware security keys required to sign in)? If you're not sure, you probably don't — it's something you would have explicitly enrolled in."**

- **No / Not sure** → Normal setup. Continue below.
- **Yes** → Their Workspace admin must add the OAuth client ID to the org's allowed apps list before Step 4 will work. Let them know upfront.

### Step 2: Create OAuth credentials (one-time, ~5 minutes)

Tell the user:

> You need a Google Cloud OAuth client. This is a one-time setup:
>
> 1. Create or select a project:
>    https://console.cloud.google.com/projectselector2/home/dashboard
> 2. Enable the required APIs from the API Library:
>    https://console.cloud.google.com/apis/library
>    Enable: Gmail API, Google Calendar API, Google Drive API,
>    Google Sheets API, Google Docs API, People API
> 3. Create the OAuth client here:
>    https://console.cloud.google.com/apis/credentials
>    Credentials → Create Credentials → OAuth 2.0 Client ID
> 4. Application type: "Desktop app" → Create
> 5. If the app is still in Testing, add the user's Google account as a test user here:
>    https://console.cloud.google.com/auth/audience
>    Audience → Test users → Add users
> 6. Download the JSON file and tell me the file path
>
> Important Hermes CLI note: if the file path starts with `/`, do NOT send only the bare path as its own message in the CLI, because it can be mistaken for a slash command. Send it in a sentence instead, like:
> `The JSON file path is: /home/user/Downloads/client_secret_....json`

Once they provide the path:

```bash
$GSETUP --client-secret /path/to/client_secret.json
```

If they paste the raw client ID / client secret values instead of a file path,
write a valid Desktop OAuth JSON file for them yourself, save it somewhere
explicit (for example `~/Downloads/hermes-google-client-secret.json`), then run
`--client-secret` against that file.

### Step 3: Get authorization URL

```bash
$GSETUP --auth-url
```

This returns JSON with an `auth_url` field and also saves the exact URL to
`~/.hermes/google_oauth_last_url.txt`.

Agent rules for this step:
- Extract the `auth_url` field and send that exact URL to the user as a single line.
- Tell the user that the browser will likely fail on `http://localhost:1` after approval, and that this is expected.
- Tell them to copy the ENTIRE redirected URL from the browser address bar.
- If the user gets `Error 403: access_denied`, send them directly to `https://console.cloud.google.com/auth/audience` to add themselves as a test user.
  - If the direct URL redirects or fails, guide through the UI: console.cloud.google.com → Search bar → "Audience" → OAuth consent screen → Test users → Add users → enter email → Save.
  - After adding, have them retry the same auth URL (no need to regenerate).

### Step 4: Exchange the code

The user will paste back either a URL like `http://localhost:1/?code=4/0A...&scope=...`
or just the code string. Either works. The `--auth-url` step stores a temporary
pending OAuth session locally so `--auth-code` can complete the PKCE exchange
later, even on headless systems:

```bash
$GSETUP --auth-code "THE_URL_OR_CODE_THE_USER_PASTED"
```

If `--auth-code` fails because the code expired, was already used, or came from
an older browser tab, it now returns a fresh `fresh_auth_url`. In that case,
immediately send the new URL to the user and have them retry with the newest
browser redirect only.

### Step 5: Verify

```bash
$GSETUP --check
```

Should print `AUTHENTICATED`. Setup is complete — token refreshes automatically from now on.

### Notes

- Token is stored at `~/.hermes/google_token.json` and auto-refreshes.
- Pending OAuth session state/verifier are stored temporarily at `~/.hermes/google_oauth_pending.json` until exchange completes.
- If `gws` is installed, `google_api.py` points it at the same `~/.hermes/google_token.json` credentials file. Users do not need to run a separate `gws auth login` flow.
- To revoke: `$GSETUP --revoke`

## Usage

All commands go through the API script. Set `GAPI` as a shorthand:

```bash
GAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"

# On PEP 668 systems, use the venv Python (same venv as GSETUP):
#   GAPI="~/.hermes/venvs/google/bin/python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
```

**Critical — verify your Python binary before first use:**
The same Python used for GSETUP (the one with `googleapiclient` installed) MUST be used for GAPI. Mixing system python and venv python causes `ModuleNotFoundError`. Verify before running any GAPI command:

```bash
$GAPI gmail labels  # quick connectivity test
```

If that fails, check which Python GAPI resolves to:
```bash
echo "$GAPI" | awk '{print $1}' | xargs which
# On PEP 668: ensure GAPI points to your venv's Python, not system python
```

### Gmail

```bash
# Search (returns JSON array with id, from, subject, date, snippet)
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"

# Read full message (returns JSON with body text)
$GAPI gmail get MESSAGE_ID

# Send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"
$GAPI gmail send --to user@example.com --subject "Report" --body "<h1>Q4</h1><p>Details...</p>" --html
$GAPI gmail send --to user@example.com --subject "Hello" --from '"Research Agent" <user@example.com>' --body "Message text"

# Reply (automatically threads and sets In-Reply-To)
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
$GAPI gmail reply MESSAGE_ID --from '"Support Bot" <user@example.com>' --body "Thanks"

# Labels
$GAPI gmail labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

### Calendar

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (ISO 8601 with timezone required)
$GAPI calendar create --summary "Team Standup" --start 2026-03-01T10:00:00-06:00 --end 2026-03-01T10:30:00-06:00
$GAPI calendar create --summary "Lunch" --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z --location "Cafe"
$GAPI calendar create --summary "Review" --start 2026-03-01T14:00:00Z --end 2026-03-01T15:00:00Z --attendees "alice@co.com,bob@co.com"

# Delete event
$GAPI calendar delete EVENT_ID
```

### Drive

```bash
# Search existing files
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5

# Get metadata for a single file
$GAPI drive get FILE_ID

# Upload a local file (auto-detects MIME type)
$GAPI drive upload /path/to/report.pdf
$GAPI drive upload /path/to/image.png --name "Logo.png" --parent FOLDER_ID

# Download (binary files download as-is; Google-native files export to a
# sensible default — Docs→pdf, Sheets→csv, Slides→pdf, Drawings→png)
$GAPI drive download FILE_ID
$GAPI drive download DOC_ID --output ~/doc.pdf
$GAPI drive download DOC_ID --export-mime text/plain --output ~/doc.txt

# Create a folder
$GAPI drive create-folder "Reports"
$GAPI drive create-folder "Q4" --parent FOLDER_ID

# Share
$GAPI drive share FILE_ID --email alice@example.com --role reader
$GAPI drive share FILE_ID --email alice@example.com --role writer --notify
$GAPI drive share FILE_ID --type anyone --role reader        # anyone with link
$GAPI drive share FILE_ID --type domain --domain example.com --role reader

# Delete — defaults to trash (reversible). Use --permanent to skip the trash.
$GAPI drive delete FILE_ID
$GAPI drive delete FILE_ID --permanent

# Batch move to folder — see scripts/drive-move-to-folder.py
# Example: move all matching files to a folder, deduplicate
python3 scripts/drive-move-to-folder.py FOLDER_ID "Berserk_Vol16_Q85"
```

**Batch download pattern:** for structured folder trees (e.g., project folders with subfolders per process), see `references/drive-batch-download-pattern.md` — covers listing, mapping, per-type download, parallelism, and case-sensitivity pitfalls.

### Contacts

```bash
$GAPI contacts list --max 20
```

### Sheets

```bash
# Create a new spreadsheet
$GAPI sheets create --title "Q4 Budget"
$GAPI sheets create --title "Inventory" --sheet-name "Stock"

# Read (REQUIRES full A1 notation — bare sheet name like "Sheet1" errors with "Unable to parse range")
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"
# If you don't know the sheet name/structure, use a broad range and inspect:
$GAPI sheets get SHEET_ID "A1:Z100"

# Write
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[[\"Name\",\"Score\"],[\"Alice\",\"95\"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[[\"new\",\"row\",\"data\"]]'
```

### Docs

```bash
# Read
$GAPI docs get DOC_ID
# ⚠️ Returns plain text only — tables and checkboxes are stripped.
#    For table extraction, see references/docs-api-table-extraction.md

# Create a new Doc (optionally seeded with body text)
$GAPI docs create --title "Meeting Notes"
$GAPI docs create --title "Draft" --body "First paragraph..."

# Append text to the end of an existing Doc
$GAPI docs append DOC_ID --text "Additional content to append"

# Inline update/replace — NOT available via google_api.py.
# Use the Google Docs REST API batchUpdate endpoint directly.
# See references/docs-api-batch-update.md for the technique.
```

## Output Format

All commands return JSON. Parse with `jq` or read directly. Key fields:

- **Gmail search**: `[{id, threadId, from, to, subject, date, snippet, labels}]`
- **Gmail get**: `{id, threadId, from, to, subject, date, labels, body}`
- **Gmail send/reply**: `{status: "sent", id, threadId}`
- **Calendar list**: `[{id, summary, start, end, location, description, htmlLink}]`
- **Calendar create**: `{status: "created", id, summary, htmlLink}`
- **Drive search**: `[{id, name, mimeType, modifiedTime, webViewLink}]`
- **Drive get**: `{id, name, mimeType, modifiedTime, size, webViewLink, parents, owners}`
- **Drive upload**: `{status: "uploaded", id, name, mimeType, webViewLink}`
- **Drive download**: `{status: "downloaded", id, name, path, mimeType}`
- **Drive create-folder**: `{status: "created", id, name, webViewLink}`
- **Drive share**: `{status: "shared", permissionId, fileId, role, type}`
- **Drive delete**: `{status: "trashed" | "deleted", fileId, permanent}`
- **Contacts list**: `[{name, emails: [...], phones: [...]}]`
- **Sheets get**: `[[cell, cell, ...], ...]`
- **Sheets create**: `{status: "created", spreadsheetId, title, spreadsheetUrl}`
- **Docs create**: `{status: "created", documentId, title, url}`
- **Docs append**: `{status: "appended", documentId, inserted_at, characters}`

## Rules

1. **Never send email, create/delete calendar events, delete Drive files, share files, or modify Docs/Sheets without confirming with the user first.** Show what will be done (recipients, file IDs, content, share role) and ask for approval. For `drive delete`, prefer the default trash (reversible) over `--permanent`.
2. **Check auth before first use** — run `setup.py --check`. If it fails, guide the user through setup.
3. **Use the Gmail search syntax reference** for complex queries — load it with `skill_view("google-workspace", file_path="references/gmail-search-syntax.md")`.
4. **Calendar times must include timezone** — always use ISO 8601 with offset (e.g., `2026-03-01T10:00:00-06:00`) or UTC (`Z`).
5. **Respect rate limits** — avoid rapid-fire sequential API calls. Batch reads when possible.

## Programmatic Automation (Python API)

For programmatic Google Drive and Sheets patterns (folder trees, batch population, cross-account sharing, service account operations), see `references/workspace-automation-patterns.md` (absorbed from former `workspace-automation` skill). Also see `references/drive-trashed-files-pitfall.md` for the critical trashed-files filtering bug when using `supportsAllDrives=True`.

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run setup Steps 2-5 above |
| `REFRESH_FAILED` | Token revoked or expired — redo Steps 3-5 |
| `HttpError 403: Insufficient Permission` | Missing API scope — `$GSETUP --revoke` then redo Steps 3-5. Check scope list with `--check` first. |
| `AUTHENTICATED (partial)` or "Token missing scopes" | Token has fewer scopes than the consent screen requests. See `references/scope-recovery.md` for the revoke-and-re-auth procedure. |
| `HttpError 403: Access Not Configured` | API not enabled — user needs to enable it in Google Cloud Console |
| `ModuleNotFoundError` | Python mismatch. First check: `$GSETUP --check` — if it says AUTHENTICATED, the venv exists but GAPI is using the wrong Python. Use the **same** Python for both GSETUP and GAPI (see PEP 668 note above). Otherwise run `$GSETUP --install-deps`, or on PEP 668 systems use the `uv venv` workaround in the setup section |
| Advanced Protection blocks auth | Workspace admin must allowlist the OAuth client ID |
| `Ocorreu um erro: N columns passed, passed data had M columns` | Google Sheets trims trailing empty cells per row. Data rows end up with fewer columns than the header row. Fix: pad each row to match the header length before creating the DataFrame. See `references/sheets-column-padding.md`. |
| `File not found` when sharing a service-account-created folder via user OAuth | Service accounts and user OAuth have separate Drive scopes. Folders created by one are invisible to the other until explicitly shared. Share the folder to the other account's email FIRST, then operate. |
| Service account can't access a user-owned folder/spreadsheet | Use user OAuth (`GAPI` or `drive share`) to share the resource with the service account email (Editor role). Then retry with service account credentials. See `references/service-account-sharing.md`. |
| `HttpError 400: Invalid Value` on `drive search "'ID' in parents"` | Missing `--raw-query` flag. Without it, the CLI interprets the `'ID' in parents` string as a `fullText contains` search. Always use `--raw-query` for Drive parent-child queries. Also: Drive IDs are **case-sensitive** — verify with `drive get` before searching children. |
| Google Docs downloaded as `.pdf` instead of text | Add `--export-mime text/plain` to download Docs as readable text. Without it, the default export is PDF. |
| `Gmail send` fails for attachments >25 MB | Gmail API/SMTP has a ~25 MB total message limit (base64 overhead). Files >25 MB cannot be attached — upload to Drive instead and share the link. See `references/gmail-large-file-delivery.md`. |
| `$GAPI gmail send` has no `--attach` flag | The CLI wrapper `gmail send` does not support file attachments. For sending emails with attachments (e.g. EPUB manga files), use the Python Gmail API directly with MIMEBase — see kindle-manga's `references/gmail-kindle-delivery.md` for the complete script. |

## Revoking Access

```bash
$GSETUP --revoke
```

## Histórico de Atualizações

| Data | Mudança |
|------|---------|
| 2026-06-21 | Adicionado `references/gmail-large-file-delivery.md` — Gmail 25 MB attachment limit, Drive sharing workaround, and Kindle manga delivery edge case. Added pitfall and reference pointer in SKILL.md. |
| 2026-06-19 | Adicionados pitfalls: `drive search` parent queries exigem `--raw-query` (400 Invalid Value sem ele); Drive IDs case-sensitive; Docs precisam de `--export-mime text/plain` para download como texto. |
