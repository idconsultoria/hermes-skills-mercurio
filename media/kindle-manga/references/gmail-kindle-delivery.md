# Gmail API Kindle Delivery

Send manga EPUB directly to Kindle via Gmail API (Send-to-Kindle). Requires authenticated Google Workspace OAuth with Gmail send scope.

## Prerequisites

- Google Workspace skill authenticated (`setup.py --check` → AUTHENTICATED)
- EPUB file ready for delivery
- Recipient's Kindle email (format: `<username>@kindle.com`)

## Python script

```python
import base64, json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

TOKEN_PATH = "/opt/data/google_token.json"  # or ~/.hermes/google_token.json
KINDLE_EMAIL = "user@kindle.com"
FROM_EMAIL = "sender@gmail.com"
EPUB_PATH = "/path/to/file.epub"
SUBJECT = "Chapter Title - Convert"  # "Convert" triggers Kindle format conversion
BODY_TEXT = "Sent via Hermes Agent."

creds = Credentials.from_authorized_user_file(TOKEN_PATH, [
    'https://www.googleapis.com/auth/gmail.send',
])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('gmail', 'v1', credentials=creds)

msg = MIMEMultipart()
msg['To'] = KINDLE_EMAIL
msg['From'] = FROM_EMAIL
msg['Subject'] = SUBJECT
msg.attach(MIMEText(BODY_TEXT, 'plain'))

with open(EPUB_PATH, 'rb') as f:
    part = MIMEBase('application', 'epub+zip')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
        f'attachment; filename="manga.epub"')
    msg.attach(part)

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
result = service.users().messages().send(
    userId='me', body={'raw': raw}
).execute()

print(f'Sent! Message ID: {result["id"]}')
print(f'Thread ID: {result["threadId"]}')
```

## Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Gmail attachment limit | 25 MB | Total message (base64 overhead ~37% adds to effective size) |
| Kindle email size limit | 50 MB | Per Amazon's Send-to-Kindle docs |
| Android app limit | 200 MB | Separate channel from email |

Files over 25 MB cannot be sent via Gmail — use Google Drive upload + share instead.

## Subject line

The subject line is not critical for delivery, but adding "Convert" at the end triggers Kindle's format conversion if needed. EPUB is already accepted natively.

## Threading

Each Send-to-Kindle email creates a new thread. Use the same `Subject` for the same manga series to keep threads organized in Gmail.
