#!/usr/bin/env python3
"""Aplica identidade de marca (cores/fontes) a um Google Doc já convertido de markdown.

Uso:  <venv-google>/python theme_doc.py <DOC_ID>

Copiar e ajustar PALETA/FONTES antes de rodar. Idempotente: re-rodar após qualquer correção de
conteúdo. Requer google_token.json do OAuth já configurado (skill google-workspace).
"""
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/data/data/com.termux/files/home/capitolium/google_token.json"
DOC_ID = sys.argv[1]

# ---- paleta / tipografia da marca -------------------------------------------------
COR_PRIMARIA = {"color": {"rgbColor": {"red": 0.780, "green": 0.098, "blue": 0.129}}}  # #C71921
COR_SECUNDARIA = {"color": {"rgbColor": {"red": 0.640, "green": 0.070, "blue": 0.086}}}
COR_TEXTO = {"color": {"rgbColor": {"red": 0.067, "green": 0.067, "blue": 0.067}}}
BRANCO = {"color": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}}
FONTE_CORPO = "Inter"
FONTE_TITULO = "Montserrat"
CORPO_PT = 10.5

creds = Credentials.from_authorized_user_file(TOKEN)
docs = build("docs", "v1", credentials=creds)
doc = docs.documents().get(documentId=DOC_ID).execute()

paras, tables = [], []
for el in doc["body"]["content"]:
    if "paragraph" in el:
        p = el["paragraph"]
        text = "".join(r.get("textRun", {}).get("content", "") for r in p.get("elements", []))
        paras.append((el["startIndex"], el["endIndex"],
                      p.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT"), text))
    elif "table" in el:
        tables.append(el)


def cell_text(cell):
    out = []
    for blk in cell["content"]:
        if "paragraph" in blk:
            out.append("".join(e.get("textRun", {}).get("content", "")
                               for e in blk["paragraph"].get("elements", [])))
    return "".join(out).strip()


reqs = []
end_doc = max(p[1] for p in paras)
reqs.append({"updateTextStyle": {
    "range": {"startIndex": 1, "endIndex": end_doc - 1},
    "textStyle": {"weightedFontFamily": {"fontFamily": FONTE_CORPO},
                  "fontSize": {"magnitude": CORPO_PT, "unit": "PT"},
                  "foregroundColor": COR_TEXTO},
    "fields": "weightedFontFamily,fontSize,foregroundColor"}})

title_done = False
for start, end, style, text in paras:
    if end - start <= 1:
        continue
    rng = {"startIndex": start, "endIndex": end - 1}
    if style == "TITLE" and not title_done:
        title_done = True
        reqs.append({"updateParagraphStyle": {"range": rng,
            "paragraphStyle": {"namedStyleType": "TITLE", "alignment": "START",
                               "spaceAbove": {"magnitude": 0, "unit": "PT"},
                               "spaceBelow": {"magnitude": 4, "unit": "PT"},
                               "lineSpacing": 100},
            "fields": "namedStyleType,alignment,spaceAbove,spaceBelow,lineSpacing"}})
        reqs.append({"updateTextStyle": {"range": rng,
            "textStyle": {"weightedFontFamily": {"fontFamily": FONTE_TITULO},
                          "fontSize": {"magnitude": 24, "unit": "PT"},
                          "bold": True, "foregroundColor": COR_TEXTO},
            "fields": "weightedFontFamily,fontSize,bold,foregroundColor"}})
    elif style == "HEADING_1":
        reqs.append({"updateParagraphStyle": {"range": rng,
            "paragraphStyle": {"spaceAbove": {"magnitude": 22, "unit": "PT"},
                               "spaceBelow": {"magnitude": 8, "unit": "PT"},
                               "keepWithNext": True, "lineSpacing": 100},
            "fields": "spaceAbove,spaceBelow,keepWithNext,lineSpacing"}})
        reqs.append({"updateTextStyle": {"range": rng,
            "textStyle": {"weightedFontFamily": {"fontFamily": FONTE_TITULO},
                          "fontSize": {"magnitude": 12.5, "unit": "PT"},
                          "bold": True, "foregroundColor": COR_PRIMARIA},
            "fields": "weightedFontFamily,fontSize,bold,foregroundColor"}})
    elif style == "HEADING_2":
        reqs.append({"updateParagraphStyle": {"range": rng,
            "paragraphStyle": {"spaceAbove": {"magnitude": 18, "unit": "PT"},
                               "spaceBelow": {"magnitude": 6, "unit": "PT"},
                               "keepWithNext": True},
            "fields": "spaceAbove,spaceBelow,keepWithNext"}})
        reqs.append({"updateTextStyle": {"range": rng,
            "textStyle": {"weightedFontFamily": {"fontFamily": FONTE_TITULO},
                          "fontSize": {"magnitude": 11.5, "unit": "PT"},
                          "bold": True, "foregroundColor": COR_SECUNDARIA},
            "fields": "weightedFontFamily,fontSize,bold,foregroundColor"}})
    elif style == "NORMAL_TEXT":
        reqs.append({"updateParagraphStyle": {"range": rng,
            "paragraphStyle": {"lineSpacing": 118,
                               "spaceBelow": {"magnitude": 8, "unit": "PT"},
                               "alignment": "JUSTIFIED"},   # JUSTIFIED, não JUSTIFY
            "fields": "lineSpacing,spaceBelow,alignment"}})

for el in tables:
    tb = el["table"]
    if not tb.get("rows"):
        continue
    is_sig = cell_text(tb["tableRows"][0]["tableCells"][0]) == ""
    if is_sig:
        # bloco de assinaturas: sem faixa, bordas invisíveis, espaço para assinar
        for ri, row in enumerate(tb["tableRows"]):
            for blk in row["tableCells"][0]["content"]:
                pass
        for ri, row in enumerate(tb["tableRows"]):
            for ci, cell in enumerate(row["tableCells"]):
                for blk in cell["content"]:
                    if "paragraph" in blk:
                        st, en = blk["startIndex"], blk["endIndex"]
                        reqs.append({"updateParagraphStyle": {
                            "range": {"startIndex": st, "endIndex": max(st, en - 1)},
                            "paragraphStyle": {"alignment": "START",
                                               "spaceAbove": {"magnitude": 0, "unit": "PT"},
                                               "spaceBelow": {"magnitude": 0, "unit": "PT"}},
                            "fields": "alignment,spaceAbove,spaceBelow"}})
                borda = {"color": {"color": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}},
                         "width": {"magnitude": 1, "unit": "PT"}, "dashStyle": "SOLID"}
                reqs.append({"updateTableCellStyle": {
                    "tableRange": {"tableCellLocation": {
                        "tableStartLocation": {"index": el["startIndex"]},
                        "rowIndex": ri, "columnIndex": ci},
                        "rowSpan": 1, "columnSpan": 1},
                    "tableCellStyle": {"borderTop": borda, "borderBottom": borda,
                                       "borderLeft": borda, "borderRight": borda},
                    "fields": "borderTop,borderBottom,borderLeft,borderRight"}})
        reqs.append({"updateTableRowStyle": {          # tableStartLocation + rowIndices
            "tableStartLocation": {"index": el["startIndex"]},
            "rowIndices": [0],
            "tableRowStyle": {"minRowHeight": {"magnitude": 46, "unit": "PT"}},
            "fields": "minRowHeight"}})
        continue
    for cell in tb["tableRows"][0]["tableCells"]:
        st, en = cell["content"][0]["startIndex"], cell["content"][0]["endIndex"]
        if en - st <= 1:
            continue
        reqs.append({"updateTextStyle": {
            "range": {"startIndex": st, "endIndex": en - 1},
            "textStyle": {"weightedFontFamily": {"fontFamily": FONTE_TITULO},
                          "fontSize": {"magnitude": 9.5, "unit": "PT"},
                          "bold": True, "foregroundColor": BRANCO},
            "fields": "weightedFontFamily,fontSize,bold,foregroundColor"}})
    reqs.append({"updateTableCellStyle": {
        "tableRange": {"tableCellLocation": {"tableStartLocation": {"index": el["startIndex"]},
                                             "rowIndex": 0, "columnIndex": 0},
                       "rowSpan": 1, "columnSpan": len(tb["tableRows"][0]["tableCells"])},
        "tableCellStyle": {"backgroundColor": COR_PRIMARIA},
        "fields": "backgroundColor"}})

for el in tables:                                    # nenhuma linha quebra no meio
    for row in el["table"]["tableRows"]:
        for cell in row["tableCells"]:
            for blk in cell["content"]:
                if "paragraph" in blk:
                    st, en = blk["startIndex"], blk["endIndex"]
                    reqs.append({"updateParagraphStyle": {
                        "range": {"startIndex": st, "endIndex": max(st, en - 1)},
                        "paragraphStyle": {"keepLinesTogether": True},
                        "fields": "keepLinesTogether"}})

reqs.append({"updateDocumentStyle": {
    "documentStyle": {
        "pageSize": {"width": {"magnitude": 595.3, "unit": "PT"},
                     "height": {"magnitude": 841.9, "unit": "PT"}},
        "marginTop": {"magnitude": 62, "unit": "PT"},
        "marginBottom": {"magnitude": 58, "unit": "PT"},
        "marginLeft": {"magnitude": 65, "unit": "PT"},
        "marginRight": {"magnitude": 65, "unit": "PT"}},
    "fields": "pageSize,marginTop,marginBottom,marginLeft,marginRight"}})

done = 0
for i in range(0, len(reqs), 60):
    docs.documents().batchUpdate(documentId=DOC_ID,
                                body={"requests": reqs[i:i + 60]}).execute()
    done += len(reqs[i:i + 60])
print("requisições aplicadas:", done, "| parágrafos:", len(paras), "| tabelas:", len(tables))
