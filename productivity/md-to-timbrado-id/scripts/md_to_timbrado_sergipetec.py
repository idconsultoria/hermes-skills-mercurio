#!/usr/local/lib/hermes-agent/venv/bin/python
"""md_to_timbrado_sergipetec.py — MD -> Google Doc no papel timbrado do SergipeTec.

Reaproveita a TÉCNICA da skill md-to-timbrado-id (copiar um modelo pronto, preencher
capa, injetar corpo com o motor md->gdoc), mas usando como MODELO o documento de
referência do SergipeTec (proposta TJSE), que já carrega logo, cores e footer.

Estrutura do modelo SergipeTec (doc 1R8PCezBW8QtjHA1g4Qi6fZulxJkIBQ62IesN3Uqx3bM):
  el0  sectionBreak CONTINUOUS          (margens da capa)
  el1  glifo \\ue907 + 'd'              (ancora interna da capa — PRESERVAR)
  el2  LOGO (inlineObject i.1)          (PRESERVAR)
  el3  eyebrow verde   'PROPOSTA ESTRATÉGICA · PLANO DE TRABALHO'
  el4  título (branco) 28pt
  el5  título (verde ) 28pt
  el6  TABLE metadata (Parceria estratégica ...)
  el7  parágrafo vazio
  el8  sectionBreak NEXT_PAGE           (início da página 2/corpo)
  el9+ corpo do TJSE                    (REMOVER e substituir)

DIFERENÇA CRÍTICA vs. modelo ID: o SergipeTec NÃO tem glifo/âncora de contracapa no
FINAL. Então NÃO se aplica o patch de "inserir antes do parágrafo final" — aqui o
corpo é simplesmente deletado e reinserido no fim (após o sectionBreak NEXT_PAGE).
"""
import argparse, importlib.util, os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HERMES_HOME = os.environ.get("HERMES_HOME", "/opt/mercurio-data")
TOKEN = Path(HERMES_HOME) / "google_token.json"
SCRIPT = f"{HERMES_HOME}/skills/productivity/google-workspace/scripts/md-to-gdoc.py"
MODEL_SERGIPETEC = "1R8PCezBW8QtjHA1g4Qi6fZulxJkIBQ62IesN3Uqx3bM"


def load_mdg():
    spec = importlib.util.spec_from_file_location("mdg", SCRIPT)
    mdg = importlib.util.module_from_spec(spec); sys.modules["mdg"] = mdg
    spec.loader.exec_module(mdg)
    # Nunito Sans SEM weight (peso 400 suprime negrito no motor)
    def _normalize_nunito(self, start, length):
        self._add({"updateTextStyle": {"range": {"startIndex": start, "endIndex": start + length},
            "textStyle": {"weightedFontFamily": {"fontFamily": "Nunito Sans"}},
            "fields": "weightedFontFamily"}})
    mdg.DocBuilder._normalize_font = _normalize_nunito
    # add_table re-reseta self.cur após cada tabela; re-ancorar no fim (append)
    _orig_add_table = mdg.DocBuilder.add_table
    def _patched_add_table(self, header, rows):
        _orig_add_table(self, header, rows)
        doc = mdg.api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}", "GET")
        last_start = None
        for el in doc["body"]["content"]:
            if el.get("hasContent") or "paragraph" in el and "textRun" in (el["paragraph"].get("elements") or [{}])[0]:
                last_start = el["startIndex"]
        # append no fim: endIndex do ultimo elemento
        last_end = None
        for el in doc["body"]["content"]:
            last_end = el["endIndex"]
        self.cur = (last_end - 1) if last_end else self.cur
        self.ops = getattr(self, "ops", 0) + 1
    mdg.DocBuilder.add_table = _patched_add_table
    return mdg


def creds():
    return Credentials.from_authorized_user_file(str(TOKEN),
        ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"])


def full_para(el):
    return "".join(e.get("textRun", {}).get("content", "") for e in el["paragraph"].get("elements", []) if "textRun" in e)


def delete_body(docs, doc_id, start_after_idx):
    """Deleta todo o corpo do doc a partir de start_after_idx (startIndex) até o fim,
    deixando o documento terminando na capa + sectionBreak. Retorna o endIndex final."""
    r = docs.documents().get(documentId=doc_id, fields="body").execute()
    content = r["body"]["content"]
    last_end = content[-1]["endIndex"]
    # acha o primeiro elemento de corpo (>= start_after_idx) para deletar de lá ao fim
    delete_from = None
    for el in content:
        if el.get("startIndex") is not None and el["startIndex"] >= start_after_idx:
            delete_from = el["startIndex"]
            break
    # preservar o ÚLTIMO parágrafo (contém o '\n' final que o API não aceita deletar).
    # Deletar de delete_from até o startIndex do último elemento, mantendo-o intacto.
    last_start = content[-1]["startIndex"]
    if delete_from is None or last_start <= delete_from:
        return last_end
    if delete_from < last_start:
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"deleteContentRange": {"range": {"startIndex": delete_from, "endIndex": last_start}}}]}).execute()
        print("BODY_DELETED", delete_from, last_start)
    return last_start


def edit_footer(docs, doc_id, old, new):
    """Edita o footer (seção kix.hf1) via rota dedicada (replaceAllText não alcança footers)."""
    r = docs.documents().get(documentId=doc_id, fields="footers").execute()
    for fid, fv in r.get("footers", {}).items():
        for el in fv.get("content", []):
            if "paragraph" in el:
                t = full_para(el)
                if old in t:
                    docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
                        {"replaceAllText": {"containsText": {"text": old, "matchCase": True},
                                            "replaceText": new}}]}).execute()
                    print("FOOTER_OK", repr(old), "->", repr(new))
                    return
    print("FOOTER_NOT_FOUND")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_file")
    ap.add_argument("--folder", required=True)
    ap.add_argument("--doc-name", required=True)
    ap.add_argument("--titulo-l1", default="")
    ap.add_argument("--titulo-l2", default="")
    ap.add_argument("--eyebrow", default="PROPOSTA COMERCIAL  \u00b7  PLANO DE TRABALHO")
    ap.add_argument("--metadata", default="")
    args = ap.parse_args()

    c = creds()
    drive = build("drive", "v3", credentials=c)
    docs = build("docs", "v1", credentials=c)
    mdg = load_mdg()

    # 1) copiar o modelo SergipeTec (capa + logo + footer)
    copy = drive.files().copy(fileId=MODEL_SERGIPETEC, body={"name": args.doc_name, "parents": [args.folder]}).execute()
    NEW = copy["id"]
    print("NEW_ID", NEW)

    # 2) preencher capa via replaceAllText (preserva estilo do run)
    repl = [
        ("PROPOSTA ESTRAT\u00c9GICA  \u00b7  PLANO DE TRABALHO", args.eyebrow),
        ("Mutir\u00e3o de Concilia\u00e7\u00e3o da", args.titulo_l1),
        ("D\u00edvida Ativa N\u00e3o Tribut\u00e1ria", args.titulo_l2),
    ]
    if args.metadata:
        repl.append(("Parceria estrat\u00e9gica entre o Tribunal de Justi\u00e7a de Sergipe"
                     "\ne o SergipeTec para a recupera\u00e7\u00e3o inteligente de cr\u00e9ditos p\u00fablicos", args.metadata))
    reqs = [{"replaceAllText": {"containsText": {"text": a, "matchCase": True}, "replaceText": b}} for a, b in repl if a]
    if reqs:
        docs.documents().batchUpdate(documentId=NEW, body={"requests": reqs}).execute()
        print("CAPA_OK")

    # 3) editar footer
    edit_footer(docs, NEW, "Proposta de Plano de Trabalho \u2014 SergipeTec", "Proposta Comercial \u2014 SergipeTec")

    # 4) remover o corpo do TJSE (começa no parágrafo 'Introdução', el9 startIndex ~236)
    #   localizar pelo texto 'Introdução' para robustez
    r = docs.documents().get(documentId=NEW, fields="body").execute()
    body_start = None
    for el in r["body"]["content"]:
        if "paragraph" in el:
            t = full_para(el).strip()
            if t and "Introdu" in t and "Introdu\u00e7\u00e3o" in t:
                body_start = el["startIndex"]
                break
    if body_start is None:
        # fallback: elemento 9
        body_start = r["body"]["content"][9]["startIndex"]
    delete_body(docs, NEW, body_start)

    # 5) injetar o corpo da proposta El Niño via motor md->gdoc (append no fim)
    md = Path(args.md_file).read_text(encoding="utf-8")
    blocks = mdg.parse_md(md)
    b = mdg.DocBuilder(NEW)
    for tipo, dados in blocks:
        if tipo == "heading":
            l, v = dados; b.add_heading(l, v)
        elif tipo == "para":
            b.add_para(dados)
        elif tipo == "callout":
            b.add_callout(dados)
        elif tipo == "bullets":
            b.add_bullets(dados, numbered=False)
        elif tipo == "checklist":
            b.add_checklist(dados)
        elif tipo == "numbered":
            b.add_bullets(dados, numbered=True)
        elif tipo == "table":
            h, r_ = dados; b.add_table(h, r_)
        elif tipo == "code":
            b.add_code(dados)
        elif tipo == "mermaid":
            b.add_mermaid(dados)
        elif tipo == "hr":
            b.insert_text("\n")
    b.finish()
    print("BLOCO_OK", len(blocks))
    print("URL", f"https://docs.google.com/document/d/{NEW}/edit")


if __name__ == "__main__":
    main()
