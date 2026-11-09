#!/usr/bin/env python3
"""Lista as mensagens de uma thread do Gmail (headers) e, opcionalmente, o corpo.

Por que existe: antes de cobrar um cliente de novo é preciso saber quem já respondeu e
quando — cobrar depois de resposta é erro de relacionamento, e escalada já feita consome
o nível da escalada.

Uso:
  PY=$HERMES_HOME/venvs/google/bin/python        # venv com googleapiclient
  $PY scripts/ler_thread_gmail.py <thread_id>
  $PY scripts/ler_thread_gmail.py <thread_id> --corpo
  $PY scripts/ler_thread_gmail.py <thread_id> --de elenaldo --corpo

Token: $HERMES_HOME/google_token.json (admin@idconsultoria.ai). Só lê — nunca envia.
"""
import argparse
import base64
import json
import os
import re
import sys

HH = os.environ.get("HERMES_HOME", "/data/data/com.termux/files/home/capitolium")
HEADERS = ["From", "To", "Cc", "Subject", "Date"]


def service(token):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    d = json.load(open(token))
    d.setdefault("type", "authorized_user")
    creds = Credentials.from_authorized_user_info(d, d.get("scopes"))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def corpo(part, out):
    if part.get("body", {}).get("data"):
        out.append(base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", "replace"))
    for p in part.get("parts") or []:
        corpo(p, out)


def texto(msg):
    out = []
    corpo(msg.get("payload", {}), out)
    txt = "\n".join(out)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return re.sub(r"[ \t]+", " ", txt).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thread_id")
    ap.add_argument("--corpo", action="store_true", help="imprime o corpo em texto")
    ap.add_argument("--de", default=None, help="filtra remetente (substring do From)")
    ap.add_argument("--token", default=os.path.join(HH, "google_token.json"))
    ap.add_argument("--limite", type=int, default=1500, help="caracteres do corpo por mensagem")
    a = ap.parse_args()

    svc = service(a.token)
    t = svc.users().threads().get(
        userId="me",
        id=a.thread_id,
        format="full" if a.corpo else "metadata",
        metadataHeaders=HEADERS,
    ).execute()

    n = 0
    for m in t.get("messages", []):
        h = {x["name"]: x["value"] for x in m.get("payload", {}).get("headers", [])}
        if a.de and a.de.lower() not in (h.get("From") or "").lower():
            continue
        n += 1
        print("---", h.get("Date"), "|", h.get("From"))
        print("    para:", h.get("To"), "| cc:", h.get("Cc"))
        print("    assunto:", h.get("Subject"))
        print("    labels:", [l for l in m.get("labelIds", []) if l in ("SENT", "INBOX", "DRAFT")])
        if a.corpo:
            print("    corpo:", texto(m)[: a.limite].replace("\n", "\n           "))
    print(f"total: {n} mensagem(ns) em {a.thread_id}")
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
