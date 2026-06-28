"""Send EPUB to Kindle via Gmail using Google API."""
import os, sys, json, base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def send_kindle_epub(epub_path, title):
    """Send an EPUB file to Kindle via Gmail attachments."""
    TOKEN_PATH = "/opt/data/google_token.json"
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    KINDLE_EMAIL = "gustavomelloenciv_0yDkTw@kindle.com"
    FROM_EMAIL = "gustavomelloenciv@gmail.com"

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError("Need valid Gmail credentials")

    service = build("gmail", "v1", credentials=creds)

    msg = MIMEMultipart()
    msg["To"] = KINDLE_EMAIL
    msg["From"] = FROM_EMAIL
    msg["Subject"] = f"{title} - Convert"
    msg.attach(MIMEText("Kindle EPUB", "plain"))

    with open(epub_path, "rb") as f:
        part = MIMEBase("application", "epub+zip")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment",
                        filename=os.path.basename(epub_path))
        msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId="me",
                                              body={"raw": raw}).execute()
    print(f"  Email sent: {result.get('id', 'OK')}")
    return result

if __name__ == "__main__":
    epub_path = sys.argv[1]
    title = sys.argv[2]
    send_kindle_epub(epub_path, title)
