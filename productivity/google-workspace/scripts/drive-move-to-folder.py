#!/usr/bin/env python3
"""Move files matching a name pattern to a Drive folder, deduplicating.

Usage:
    python3 drive-move-to-folder.py FOLDER_ID "NamePattern"

    Moves all files containing NamePattern to FOLDER_ID.
    Deduplicates: if multiple files match, keeps the first, deletes extras.
    Already-in-folder files are skipped (not moved).

Examples:
    python3 drive-move-to-folder.py "1abc..." "Monster_Vol13_Q85"
    python3 drive-move-to-folder.py "1xyz..." "Berserk_v01_Kindle"
"""
import sys, os

TOKEN_PATH = "/opt/data/google_token.json"
TOKEN_PATH = "/opt/data/google_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = None
if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    else:
        raise RuntimeError("Need valid credentials — run google-workspace setup first")

service = build("drive", "v3", credentials=creds)
folder_id = sys.argv[1]
name_query = sys.argv[2]

results = service.files().list(
    q=f"name contains '{name_query}' and trashed=false",
    fields="files(id, name, parents)",
    pageSize=20
).execute()
files = results.get('files', [])

if not files:
    print(f"No files found matching '{name_query}'")
    sys.exit(0)

to_move = []
for f in files:
    parents = f.get('parents', [])
    if folder_id in parents:
        print(f"Already in folder: {f['name']} ({f['id']})")
    else:
        to_move.append(f)

for f in to_move:
    current_parents = ",".join(f.get('parents', []))
    service.files().update(
        fileId=f['id'],
        addParents=folder_id,
        removeParents=current_parents,
        fields='id, parents'
    ).execute()
    print(f"Moved: {f['name']} ({f['id']})")

# Deduplicate: keep one (prefer one already in folder), delete rest
if len(files) > 1:
    kept = False
    for f in files:
        parents = f.get('parents', [])
        if folder_id in parents:
            if kept:
                service.files().delete(fileId=f['id']).execute()
                print(f"Deleted duplicate (in folder): {f['name']} ({f['id']})")
            kept = True
    if not kept and len(files) > 1:
        for f in files[1:]:
            service.files().delete(fileId=f['id']).execute()
            print(f"Deleted duplicate: {f['name']} ({f['id']})")

print(f"Done: {name_query}")
