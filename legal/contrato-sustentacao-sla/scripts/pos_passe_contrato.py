#!/usr/bin/env python3
"""Pós-passe de contrato gerado no modelo timbrado da ID.

Faz as duas correções que o gerador não faz de forma confiável e que só se veem no PDF:
  1. quebra de página antes do primeiro anexo (o anexo costuma sair na página das assinaturas);
  2. alinhamento à esquerda dos títulos (justificado estica o espaço quando o título quebra).

Uso:
    python pos_passe_contrato.py <DOC_ID> --so-quebra
    python pos_passe_contrato.py <DOC_ID> --so-estilos
    python pos_passe_contrato.py <DOC_ID> --verificar

Rode as duas fases em chamadas separadas, nesta ordem: inserir a quebra desloca os índices
usados para aplicar estilo. Rode com o venv que tem googleapiclient e redirecione a saída
para arquivo (a saída de rede se perde no caminho).

Verificação que fecha o serviço: exporte o PDF e confira em que página cada ANEXO caiu —
`pdftotext -layout -f P -l P` página a página procurando 'ANEXO'. O log do gerador não prova nada.
"""
import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

H = Path(os.environ.get("HERMES_HOME", "/data/data/com.termux/files/home/capitolium"))
TOKEN = H / "google_token.json"  # admin@idconsultoria.ai

d = json.loads(TOKEN.read_text())
d.setdefault("type", "authorized_user")
creds = Credentials.from_authorized_user_info(d, d.get("scopes"))
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
docs = build("docs", "v1", credentials=creds, cache_discovery=False)

DOC = sys.argv[1]
modo = sys.argv[2] if len(sys.argv) > 2 else "--tudo"


def paragrafos(doc):
    out = []

    def walk(el):
        if "paragraph" in el:
            txt = "".join(e.get("textRun", {}).get("content", "")
                          for e in el["paragraph"].get("elements", []))
            style = el["paragraph"].get("paragraphStyle", {})
            out.append({"start": el.get("startIndex"), "end": el.get("endIndex"),
                        "texto": txt, "estilo": style.get("namedStyleType", ""),
                        "alinhamento": style.get("alignment", "")})
        elif "table" in el:
            for row in el["table"].get("tableRows", []):
                for cel in row.get("tableCells", []):
                    for el2 in cel.get("content", []):
                        walk(el2)

    for el in doc.get("body", {}).get("content", []):
        walk(el)
    return out


doc = docs.documents().get(documentId=DOC).execute()
ps = paragrafos(doc)

if modo in ("--tudo", "--so-quebra"):
    alvo = next((p for p in ps if p["texto"].strip().startswith("ANEXO I —")), None)
    if not alvo:
        print("ERRO: nao achei o paragrafo do ANEXO I")
    else:
        docs.documents().batchUpdate(documentId=DOC, body={"requests": [
            {"insertPageBreak": {"location": {"index": alvo["start"]}}}]}).execute()
        print(f"QUEBRA inserida em {alvo['start']} antes de '{alvo['texto'].strip()[:40]}'")
        doc = docs.documents().get(documentId=DOC).execute()
        ps = paragrafos(doc)

if modo in ("--tudo", "--so-estilos"):
    reqs = []
    for p in ps:
        t = p["texto"].strip()
        if p["estilo"].startswith("HEADING") or t.startswith(("CLÁUSULA", "ANEXO", "PARTES")):
            if p["alinhamento"] != "START":
                reqs.append({"updateParagraphStyle": {
                    "range": {"startIndex": p["start"],
                              "endIndex": max(p["start"] + 1, p["end"] - 1)},
                    "paragraphStyle": {"alignment": "START"},
                    "fields": "alignment"}})
    for i in range(0, len(reqs), 25):
        docs.documents().batchUpdate(documentId=DOC, body={"requests": reqs[i:i + 25]}).execute()
    print(f"ESTILOS: {len(reqs)} paragrafos de titulo alinhados a esquerda")

if modo == "--verificar":
    for p in ps:
        if p["estilo"].startswith("HEADING"):
            print(p["start"], p["estilo"], p["alinhamento"], p["texto"].strip()[:70])
