#!/opt/data/venvs/google/bin/python
"""md_to_timbrado_id.py — MD -> Google Doc no papel timbrado da ID, formatado perfeito.

RECEITA PADRÃO (validada 2026-08-20 com o PRD da Solution Master):
  1. COPIA o MODELO ORIGINAL da ID ("Modelo de Doc [Fundo Preto]") -> herda capa + masthead.
  2. PREENCHE os placeholders da capa e o cabeçalho (running title + cliente).
  3. APLICA o conteúdo do .MD no CORPO com o motor md->gdoc.

  DUAS CHAVES CRÍTICAS (descobertas por busca de causa-raiz):
  * NÃO limpar o glifo '\\ue907' do parágrafo final — ele é o ÂNCORA que posiciona a
    CONTRACAPA na página final do modelo. Limpar = a contracapa some.
  * Motor inserido ANTES do parágrafo final: em vez de apendar no fim (que fundia o corpo
    com o glifo e corrompia os negritos), o DocBuilder é patcheado para apontar
    self.cur = startIndex do último parágrafo, mantendo o glifo/contracapa como último
    elemento. Isso preserva a contracapa E mantém o negrito íntegro (sem bug da 1ª letra).
  * O add_table original re-reseta self.cur = endIndex - 1 após cada tabela — mesmo patch
    necessário (senão 1ª letra dos blocos de código vira Nunito e negritos quebram depois).

Uso:
  md_to_timbrado_id.py <arquivo.md> --folder <FOLDER_ID> --doc-name "Nome v1" \
      [--tipo "TIPO"] [--titulo-exp "Título expandido"] [--titulo "Título curto"] \
      [--titulo-res "Running title"] [--cliente "Cliente"]
"""
import argparse, importlib.util, os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HERMES_HOME = os.environ.get("HERMES_HOME", "/opt/data")
TOKEN = Path(HERMES_HOME) / "google_token.json"
SCRIPT = "/opt/data/skills/productivity/google-workspace/scripts/md-to-gdoc.py"
# Modelo de Doc [Fundo Preto] — capa + masthead + contracapa da ID
MODEL_TIMBRADO = "1dFY0Mb0X0OAS8TjnIW6rqAP3A-dhA1nTMS3HETht5To"


def load_mdg():
    spec = importlib.util.spec_from_file_location("mdg", SCRIPT)
    mdg = importlib.util.module_from_spec(spec); sys.modules["mdg"] = mdg
    spec.loader.exec_module(mdg)

    # Nunito Sans SEM weight (peso 400 suprime o negrito no motor)
    def _normalize_nunito(self, start, length):
        self._add({"updateTextStyle": {"range": {"startIndex": start, "endIndex": start + length},
            "textStyle": {"weightedFontFamily": {"fontFamily": "Nunito Sans"}},
            "fields": "weightedFontFamily"}})
    mdg.DocBuilder._normalize_font = _normalize_nunito

    # CHAVE: inserir ANTES do parágrafo final (preserva o glifo/âncora da contracapa).
    def _patched_init(self, doc_id):
        self.doc_id = doc_id
        self.buffer = []
        doc = mdg.api_request(f"https://docs.googleapis.com/v1/documents/{doc_id}", "GET")
        last_start = None
        for el in doc["body"]["content"]:
            if "paragraph" in el:
                last_start = el["startIndex"]
        self.cur = last_start
        self.ops = 0
    mdg.DocBuilder.__init__ = _patched_init

    # CHAVE 2: add_table re-reseta self.cur = endIndex-1; corrigir p/ inserir antes do âncora.
    _orig_add_table = mdg.DocBuilder.add_table
    def _patched_add_table(self, header, rows):
        _orig_add_table(self, header, rows)
        doc = mdg.api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}", "GET")
        last_start = None
        for el in doc["body"]["content"]:
            if "paragraph" in el:
                last_start = el["startIndex"]
        if last_start is not None:
            self.cur = last_start
        self.ops = getattr(self, "ops", 0) + 1
    mdg.DocBuilder.add_table = _patched_add_table
    return mdg


def creds():
    return Credentials.from_authorized_user_file(str(TOKEN),
        ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"])


GLYPH = "\ue907"


def remove_cover_gap(docs, doc_id, titulo_exp, titulo):
    """Remove hero + parágrafos vazios/imagem entre o fim da capa (título expandido) e o
    início do corpo. Quebra página antes do 1º parágrafo do corpo p/ começar na p2."""
    r = docs.documents().get(documentId=doc_id, fields="body").execute()
    content = r["body"]["content"]
    start_idx = None
    end_idx = None
    first_body_idx = None
    marker = (titulo_exp or "").strip()
    hero = (titulo or "").strip()
    in_gap = False
    for el in content:
        p = el.get("paragraph")
        if not p:
            continue
        elems = p.get("elements", [])
        texte = "".join(e.get("textRun", {}).get("content", "") for e in elems if "textRun" in e)
        npos = sum("positionedObjectElement" in e for e in elems)
        probe = texte.strip()
        if not in_gap:
            if marker and probe == marker:
                in_gap = True
                start_idx = el.get("endIndex")
            continue
        is_gap_el = (probe == "" and npos == 0) or (hero and probe == hero) or probe == "TÍTULO"
        if is_gap_el:
            if start_idx is None:
                start_idx = el.get("startIndex")
            end_idx = el.get("endIndex")
        else:
            first_body_idx = el.get("startIndex")
            break
    pagebreak_idx = None
    if start_idx is not None and end_idx is not None and end_idx > start_idx:
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"deleteContentRange": {"range": {"startIndex": start_idx, "endIndex": end_idx}}}]}).execute()
        print("GAP_COLLAPSED", start_idx, end_idx)
        if first_body_idx is not None:
            pagebreak_idx = first_body_idx - (end_idx - start_idx)
    else:
        pagebreak_idx = first_body_idx
    if pagebreak_idx is not None:
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"insertPageBreak": {"location": {"index": pagebreak_idx}}}]}).execute()
        print("BODY_PAGEBREAK_OK", pagebreak_idx)
    return first_body_idx


def fix_table_spacing(docs, doc_id):
    """Garante UMA linha em branco DEPOIS de cada tabela; zera a altura do parágrafo
    ANTES (auto-criado pelo Docs e que não pode ser deletado)."""
    def _empty(p):
        if not p:
            return False
        t = "".join(e.get("textRun", {}).get("content", "") for e in (p["paragraph"].get("elements") or []) if "textRun" in e)
        return t.strip() == ""

    r = docs.documents().get(documentId=doc_id, fields="body").execute()
    content = r["body"]["content"]
    # Loop 1: zerar a altura do parágrafo que ANTECEDE cada tabela
    zero_reqs = []
    for i, el in enumerate(content):
        if "table" in el and i > 0 and "paragraph" in content[i-1]:
            prev = content[i-1]
            s, e = prev["startIndex"], prev["endIndex"]
            zero_reqs.append({"updateTextStyle": {"range": {"startIndex": s, "endIndex": e},
                "textStyle": {"fontSize": {"magnitude": 1, "unit": "PT"}}, "fields": "fontSize"}})
            zero_reqs.append({"updateParagraphStyle": {"range": {"startIndex": s, "endIndex": e},
                "paragraphStyle": {"spaceAbove": {"magnitude": 0, "unit": "PT"},
                                   "spaceBelow": {"magnitude": 0, "unit": "PT"}},
                "fields": "spaceAbove,spaceBelow"}})
    if zero_reqs:
        try:
            docs.documents().batchUpdate(documentId=doc_id, body={"requests": zero_reqs}).execute()
        except Exception as ex:
            print("ZERO_BEFORE_ERR", str(ex)[:100])
    # Loop 2: ordem REVERSA das tabelas: inserir após a última primeiro, índices válidos
    inserts = []
    for i, el in enumerate(content):
        if "table" in el:
            nxt = content[i+1] if i+1 < len(content) else None
            if nxt is None or not _empty(nxt):
                inserts.append({"insertText": {"location": {"index": content[i]["endIndex"]}, "text": "\n"}})
    if inserts:
        inserts.reverse()
        try:
            docs.documents().batchUpdate(documentId=doc_id, body={"requests": inserts}).execute()
            print("TABLE_SPACING_OK z", len(zero_reqs)//2, "ins", len(inserts))
        except Exception as e:
            print("TABLE_SPACING_ERR", str(e)[:120])
    else:
        print("TABLE_SPACING_OK z", len(zero_reqs)//2, "ins 0")


def add_pagebreak_before_anchor(docs, doc_id):
    """Insere quebra de página antes do parágrafo final (âncora da contracapa) p/ a
    contracapa abrir em página própria, sem texto do corpo sobreposto."""
    r = docs.documents().get(documentId=doc_id, fields="body").execute()
    k = None
    for el in r["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        for e in p.get("elements", []):
            tr = e.get("textRun")
            if tr and GLYPH in tr.get("content", ""):
                k = e["startIndex"] + tr["content"].index(GLYPH)
                break
        if k is not None:
            break
    if k is not None:
        docs.documents().batchUpdate(documentId=doc_id, body={"requests": [
            {"insertPageBreak": {"location": {"index": k}}}]}).execute()
        print("PAGEBREAK_OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_file")
    ap.add_argument("--folder", required=True)
    ap.add_argument("--doc-name", required=True)
    ap.add_argument("--tipo", default="DOCUMENTO DE REQUISITOS (PRD)")
    ap.add_argument("--titulo-exp", default="")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--titulo-res", default="")
    ap.add_argument("--cliente", default="")
    args = ap.parse_args()

    c = creds()
    drive = build("drive", "v3", credentials=c)
    docs = build("docs", "v1", credentials=c)
    mdg = load_mdg()

    # 1) copiar o modelo original (capa + masthead + contracapa)
    copy = drive.files().copy(fileId=MODEL_TIMBRADO, body={"name": args.doc_name, "parents": [args.folder]}).execute()
    NEW = copy["id"]
    print("NEW_ID", NEW)

    # 2) preencher capa-placeholders e cabeçalho
    repl = []
    for placeholder, val in [("Tipo de Documento", args.tipo),
                             ("Título Expandido do Documento", args.titulo_exp),
                             ("TÍTULO", args.titulo),
                             ("Título Resumido do Documento", args.titulo_res),
                             ("CLIENTE", args.cliente)]:
        if val:
            repl.append((placeholder, val))
    if repl:
        docs.documents().batchUpdate(documentId=NEW, body={"requests": [
            {"replaceAllText": {"containsText": {"text": a, "matchCase": True}, "replaceText": b}} for a, b in repl]}).execute()

    # 3) aplicar o .MD no corpo (motor insere ANTES do parágrafo final -> contracapa preservada)
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

    # Ajustes finais: colapsar hero/página-título, espaçamento de tabelas e contracapa em página própria
    remove_cover_gap(docs, NEW, args.titulo_exp, args.titulo)
    fix_table_spacing(docs, NEW)
    add_pagebreak_before_anchor(docs, NEW)

    print("BLOCO_OK", len(blocks))
    print("URL", f"https://docs.google.com/document/d/{NEW}/edit")


if __name__ == "__main__":
    main()
