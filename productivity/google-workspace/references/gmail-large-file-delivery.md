# Gmail Attachment Size Limits & Large File Delivery

Gmail (both API and SMTP) enforces a **25 MB total message size limit** for outgoing emails. Base64 encoding adds ~33% overhead, so the effective binary attachment limit is **~25 MB**.

This limit applies regardless of the sending method:

| Method | Max Message Size | Effective Binary Limit |
|--------|:-:|:-:|
| Gmail API (`users.messages.send`) | 35 MB (base64) | ~25 MB |
| Gmail SMTP (`smtp.gmail.com:587`) | 25 MB | ~25 MB |
| Google Workspace API (resumable upload) | 35 MB | ~25 MB |

## What to do when files exceed 25 MB

### Recommended: Google Drive + share link

When you need to deliver files that exceed the Gmail size limit:

1. **Upload** the file(s) to Google Drive using `$GAPI drive upload /path/to/file --parent FOLDER_ID`
2. **Share** the folder/file publicly: `$GAPI drive share FILE_ID --type anyone --role reader`
3. **Send** the shareable link via email or directly to the user

```bash
# Full pattern
FOLDER_ID=$($GAPI drive create-folder "Shared Files" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
$GAPI drive upload /path/to/large_file.zip --parent "$FOLDER_ID"
$GAPI drive share "$FOLDER_ID" --type anyone --role reader
$GAPI gmail send --to user@example.com --subject "Your files" --body "Download: https://drive.google.com/drive/folders/$FOLDER_ID"
```

### Edge cases

- **MOBI/media files:** ZIP compression doesn't help — MOBI, PDF, JPEG and most media formats are already compressed. Zipping yields <5% reduction. Gmail's 25 MB limit still applies.
- **Amazon Kindle email** (`@kindle.com`): accepts MOBI but has a 50 MB total per-email limit. Files >50 MB can be zipped, but Gmail blocks files >25 MB before they even reach Amazon. Always use Drive for Kindle manga delivery.
- **Splitting works for text** but corrupts structured binary formats (MOBI, AZW, CBZ). Don't split.
- **Send to Kindle desktop app** bypasses email limits entirely — use it when available (Windows/Mac).

## Quick reference

```bash
# Check file size before deciding delivery method
ls -lh /path/to/file
# If > 25 MB: use Drive upload + share link
# If ≤ 25 MB: attach directly if the script supports it
```
