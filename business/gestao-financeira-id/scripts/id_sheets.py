#!/usr/bin/env python3
"""Leitura read-only de planilhas Google da ID (Gestão Financeira / Gestão de Symplexis).

Uso (venv com googleapiclient; token admin da ID):
    PY=$HERMES_HOME/id-nfse-motor/.venv/bin/python
    $PY id_sheets.py abas  <SPREADSHEET_ID>
    $PY id_sheets.py dump  <SPREADSHEET_ID> "<aba>" [render] [limite]
    $PY id_sheets.py find  <SPREADSHEET_ID> "<aba>" <termo> [...]

render: FORMATTED_VALUE (default) | FORMULA | UNFORMATTED_VALUE

Token: $HERMES_HOME/google_token.json (admin@idconsultoria.ai). Carregue sempre com os
scopes do próprio arquivo — refresh com escopo a menos dá invalid_scope.

Dump grande: redirecione para arquivo e analise em Python, não no chat.
"""
import json
import os
import sys
import unicodedata

HOME = os.environ.get("HERMES_HOME") or "/data/data/com.termux/files/home/capitolium"
TOKEN = os.path.join(HOME, "google_token.json")


def svc():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    with open(TOKEN) as fh:
        d = json.load(fh)
    creds = Credentials.from_authorized_user_info(d, d.get("scopes"))
    if not creds.valid:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def abas(spreadsheet_id):
    meta = svc().spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="sheets.properties"
    ).execute()
    return [sh["properties"]["title"] for sh in meta["sheets"]]


def ler(spreadsheet_id, aba, render="FORMATTED_VALUE"):
    """Linhas da aba como listas de strings (índices absolutos desde a coluna A)."""
    r = svc().spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=f"'{aba}'", valueRenderOption=render
    ).execute()
    return r.get("values", [])


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def dump(spreadsheet_id, aba, render="FORMATTED_VALUE", limite=None):
    rows = ler(spreadsheet_id, aba, render)
    print(f"=== {aba} ({len(rows)} linhas) ===")
    for i, row in enumerate(rows, 1):
        if limite and i > limite:
            print(f"... ({len(rows) - limite} linhas omitidas)")
            break
        print(i, "\t".join(str(c).replace("\n", " ⏎ ") for c in row))


def find(spreadsheet_id, aba, termos, render="FORMATTED_VALUE"):
    """Imprime as linhas que contêm TODOS os termos (sem acento/caixa) + o nº da linha."""
    rows = ler(spreadsheet_id, aba, render)
    alvos = [_norm(t) for t in termos]
    achou = 0
    for i, row in enumerate(rows, 1):
        linha = _norm("\t".join(str(c) for c in row))
        if all(t in linha for t in alvos):
            achou += 1
            print(i, "\t".join(str(c).replace("\n", " ⏎ ") for c in row))
    print(f"--- {achou} linha(s) com {termos} em '{aba}' ({len(rows)} linhas) ---", file=sys.stderr)
    return achou


def main(argv):
    cmd = argv[1]
    if cmd == "abas":
        for t in abas(argv[2]):
            print(t)
    elif cmd == "dump":
        render = argv[4] if len(argv) > 4 else "FORMATTED_VALUE"
        limite = int(argv[5]) if len(argv) > 5 else None
        dump(argv[2], argv[3], render, limite)
    elif cmd == "find":
        find(argv[2], argv[3], argv[4:])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
