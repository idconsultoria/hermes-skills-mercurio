#!/usr/bin/env python3
"""Move Drive files matching a name pattern to a target folder, deduplicating.

Usage:
  /opt/data/venvs/google/bin/python3 scripts/drive-move-to-folder.py <folder_id> <name_query>

Searches Drive with "name contains '<name_query>'" and moves all matching files
into <folder_id>, removing them from other parent folders. If multiple files
match the same name, keeps one and deletes the rest.

Limitation: This uses the Drive API directly (not google_api.py) because the
search from google_api.py uses 'fullText contains' and does NOT return the
'parents' field needed to detect already-in-folder files.
"""
import sys, os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH="/opt/data/google_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = None
if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    else:
        raise RuntimeError("Need valid credentials: token not found or expired")

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
already_in = []
for f in files:
    parents = f.get('parents', [])
    if folder_id in parents:
        already_in.append(f)
    else:
        to_move.append(f)

for f in to_move:
    current_parents = ",".join(f.get('parents', ['root']))
    service.files().update(
        fileId=f['id'],
        addParents=folder_id,
        removeParents=current_parents,
        fields='id, parents'
    ).execute()
    print(f"Moved: {f['name']} ({f['id']})")

all_files = already_in + [f for f in to_move if f]
if len(all_files) > 1:
    kept = False
    for f in all_files:
        parents = f.get('parents', [])
        if folder_id in parents:
            if kept:
                service.files().delete(fileId=f['id']).execute()
                print(f"Deleted duplicate: {f['name']} ({f['id']})")
            kept = True
    if not kept:
        for f in all_files[1:]:
            service.files().delete(fileId=f['id']).execute()
            print(f"Deleted duplicate: {f['name']} ({f['id']})")

print(f"Done: {name_query} ({len(all_files)-len(already_in)} moved, {len(already_in)} already in folder)")
