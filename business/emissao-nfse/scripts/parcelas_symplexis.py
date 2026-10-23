#!/usr/bin/env python3
"""Parcelas de um cliente na planilha [ID] Gestao de Symplexis.

Uso:
  $HERMES_HOME/venvs/google/bin/python parcelas_symplexis.py SM
  $HERMES_HOME/venvs/google/bin/python parcelas_symplexis.py        # tudo

Le a aba `contratos` (valor total, datas, oferta) e a aba `recebimentos`
(iD.contrato, Discriminacao, Valor, Status, Data prevista) e imprime as linhas
que contem o filtro. Read-only, sem side effects.
Token: $HERMES_HOME/google_token.json (admin@idconsultoria.ai).
"""
import json
import os
import sys

HH = os.environ.get("HERMES_HOME", os.path.expanduser("~/capitolium"))
SID = "1qV_L-WMOMDKQwIgLj_l9frokFVO032nsVbM_Qbw8kR0"  # [ID] Gestao de Symplexis


def main():
    filtro = (sys.argv[1] if len(sys.argv) > 1 else "").upper()

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    d = json.loads(open(f"{HH}/google_token.json").read())
    if not d.get("type"):
        d["type"] = "authorized_user"
    c = Credentials.from_authorized_user_info(d, d.get("scopes"))
    if c.expired and c.refresh_token:
        c.refresh(Request())
    sh = build("sheets", "v4", credentials=c, cache_discovery=False)

    for tab in ("contratos", "recebimentos"):
        rows = sh.spreadsheets().values().get(
            spreadsheetId=SID, range=f"{tab}!A1:M200"
        ).execute().get("values", [])
        if not rows:
            continue
        print(f"\n===== {tab} | cabecalho: {' ~ '.join(rows[0])}")
        for i, row in enumerate(rows, 1):
            joined = " ~ ".join(str(x) for x in row)
            if not filtro or filtro in joined.upper():
                print(i, "|", joined)


if __name__ == "__main__":
    main()
