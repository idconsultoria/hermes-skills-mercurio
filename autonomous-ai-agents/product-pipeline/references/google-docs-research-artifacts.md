# Google Docs for Research Artifacts

When F2 research produces .md files (interviews, reports), mirror them as Google Docs in the project's Drive folder for collaborative editing.

## Pattern

1. Create the doc with `docs create --title "..." --body "..."` (body limited to ~3500 chars)
2. Append remaining content with `docs append DOC_ID --text "..."` (15KB chunks)
3. Move docs to the correct Drive folder (since `docs create` doesn't support `--parent`):
   - Use the Drive API's `files.update` with `addParents` and `removeParents="root"`
   - Requires Python with google-api-python-client and google-auth-oauthlib

## Example

```bash
GAPI="/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"

# Step 1: Create doc
result=$($GAPI docs create --title "Interview — Profile A" --body "First 3500 chars...")
doc_id=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('documentId',''))")

# Step 2: Append remaining content
tail -c +3501 input.md | head -c 15000 | xargs -0 $GAPI docs append "$doc_id" --text

# Step 3: Move to folder (Python Drive API)
python3 -c "
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
creds = Credentials.from_authorized_user_file('/opt/data/google_token.json')
service = build('drive', 'v3', credentials=creds)
service.files().update(fileId='$doc_id', addParents='FOLDER_ID', removeParents='root').execute()
"
```

## Pitfalls

- `docs create` does NOT support `--parent` flag — movedocs must happen as a separate step
- The `google_api.py` CLI doesn't have a `drive update` command — use Python Drive API directly for folder moves
- Body is truncated at ~3500 chars — always append remaining content
- Token path: `/opt/data/google_token.json` (Hermes-specific)
- Venv: `/opt/data/venvs/google/bin/python3` (has googleapiclient installed)
