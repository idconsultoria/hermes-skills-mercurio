#!/usr/bin/env python3
"""Le (e opcionalmente ajusta) um evento da agenda primaria da ID.

A CLI `google_api.py calendar` so expoe `list/create/delete`: este script cobre o
`events().get()` de verificacao e o `events().patch()` dos campos que ela nao aceita
(`location`, descricao com newline real, convidados com `sendUpdates`).

Rodar com o python do venv que tem googleapiclient:
  PY=$HERMES_HOME/id-nfse-motor/.venv/bin/python
  $PY scripts/event_get_patch.py --event-id <id>
  $PY scripts/event_get_patch.py --event-id <id> --location 'Presencial - Defesa Civil de Sergipe (SUPDEC)'
  $PY scripts/event_get_patch.py --event-id <id> --description 'l1
l2'
  $PY scripts/event_get_patch.py --event-id <id> --attendees 'a@x.com,b@y.com' --send-updates all

`--send-updates all` SÓ depois do ok explicito do dono para o convite.
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERMES = Path(os.environ.get("HERMES_HOME", "/data/data/com.termux/files/home/capitolium"))
SCRIPTS = HERMES / "skills" / "productivity" / "google-workspace" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from google_api import get_credentials  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event-id", required=True)
    ap.add_argument("--calendar", default="primary")
    ap.add_argument("--location")
    ap.add_argument("--description", help="newline real: passe entre aspas simples no shell")
    ap.add_argument("--attendees", help="lista separada por virgula")
    ap.add_argument(
        "--send-updates",
        choices=["all", "externalOnly", "none"],
        default=None,
        help="use 'all' apenas quando o convite ja foi aprovado pelo dono",
    )
    a = ap.parse_args()

    svc = build("calendar", "v3", credentials=get_credentials())

    body = {}
    if a.location is not None:
        body["location"] = a.location
    if a.description is not None:
        body["description"] = a.description
    if a.attendees:
        body["attendees"] = [{"email": e.strip()} for e in a.attendees.split(",") if e.strip()]

    if body:
        kwargs = {"calendarId": a.calendar, "eventId": a.event_id, "body": body}
        if a.send_updates:
            kwargs["sendUpdates"] = a.send_updates
        svc.events().patch(**kwargs).execute()

    ev = svc.events().get(calendarId=a.calendar, eventId=a.event_id).execute()
    print(json.dumps({
        "summary": ev.get("summary"),
        "start": ev["start"].get("dateTime") or ev["start"].get("date"),
        "end": ev["end"].get("dateTime") or ev["end"].get("date"),
        "location": ev.get("location"),
        "description": ev.get("description"),
        "attendees": [(x.get("email"), x.get("responseStatus")) for x in ev.get("attendees", [])],
        "status": ev.get("status"),
        "htmlLink": ev.get("htmlLink"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
