#!/usr/bin/env python3
"""Converte markdown do CFP IA em Google Docs com formatação CORRETA (Docs API batchUpdate).

v3 — MODO BATCH (para lidar com rate limit):
- Acumula requests e faz flush a cada ~25 requests (em vez de 1 chamada por operação)
- Rastreia o índice corrente localmente (sem reler o doc a cada bloco)
- Tabelas: flush → insertTable → reler doc (índice da tabela) → preencher células em batch

Uso: md_to_gdoc.py <arquivo.md> --title "Título" [--doc-id <id>] [--parent <folder_id>]
"""
import argparse
import json
import os
import re
import struct
import sys
import time
import urllib.request
import urllib.error

# Token path: env override > Hermes home > /opt/data (fallback compat)
TOKEN_PATH = os.environ.get("GOOGLE_TOKEN_PATH") or os.path.join(
    os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), "google_token.json")
if not os.path.exists(TOKEN_PATH):
    alt = "/opt/data/google_token.json"
    if os.path.exists(alt):
        TOKEN_PATH = alt
HEADING_STYLES = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3", 4: "HEADING_4"}
BATCH_SIZE = 25


def u16len(s):
    """Comprimento em code units UTF-16 — como o Google Docs API indexa.
    Emojis (surrogate pairs) contam 2, não 1. Usar SEMPRE para offsets."""
    return len(s.encode("utf-16-le")) // 2


def get_token():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            json.dump({
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
                "expiry": creds.expiry.isoformat() if creds.expiry else None,
            }, f)
    return creds.token


# ── Parsing de markdown ────────────────────────────────────────────────

def split_inline(text):
    """Divide texto em segmentos (tipo, conteúdo) para estilos inline.
    Reconhece **bold**, *italic*, `code`, e [texto](url) → richlink (Google Doc/Drive)
    ou link (URL externa). Retorna lista de (tipo, texto, url=None)."""
    segs = []
    pattern = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*[^*]+?\*)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            segs.append(("normal", text[pos:m.start()], None))
        tok = m.group(0)
        if tok.startswith("**"):
            segs.append(("bold", tok[2:-2], None))
        elif tok.startswith("`"):
            segs.append(("code", tok[1:-1], None))
        elif tok.startswith("["):
            inner = tok[1:-1]  # remove [ ]
            # split na última ")" — o texto do link não pode conter ")"
            idx_close = inner.rfind("](")
            label = inner[:idx_close]
            url = inner[idx_close + 2:]
            if re.search(r"(docs\.google\.com/(document|spreadsheets|presentation)|drive\.google\.com/(file|open|drive/folders))", url):
                segs.append(("richlink", label, url))
            else:
                segs.append(("link", label, url))
        else:
            segs.append(("italic", tok[1:-1], None))
        pos = m.end()
    if pos < len(text):
        segs.append(("normal", text[pos:], None))
    return segs


def segs_to_plain(segs):
    """Concatena o texto visível. Rich links NÃO contribuem texto (chip é 1 char).
    Links normais contribuem o label."""
    out = []
    for seg in segs:
        tipo = seg[0]
        if tipo == "richlink":
            out.append("\uFFFC")  # caractere reservado que o chip substituirá
        elif tipo == "link":
            out.append(seg[1])
        else:
            out.append(seg[1])
    return "".join(out)


def parse_md(text):
    lines = text.split("\n")
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Tabela
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|?$", lines[i + 1]):
            header = [c.strip() for c in line.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            blocks.append(("table", (header, rows)))
            continue

        # Callout / blockquote (linhas começando com >)
        if line.startswith(">"):
            items = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                raw = re.sub(r"^>\s?", "", lines[i]).strip()
                if raw:
                    items.append(split_inline(raw))
                i += 1
            blocks.append(("callout", items))
            continue

        # Heading
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            blocks.append(("heading", (len(m.group(1)), split_inline(m.group(2)))))
            i += 1
            continue

        # Bullets (incluindo checkboxes "- [ ]")
        if re.match(r"^[-*]\s+", line):
            items = []
            is_checkbox = False
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                raw = re.sub(r"^[-*]\s+", "", lines[i])
                if re.match(r"^\[[ xX]\]\s+", raw):
                    is_checkbox = True
                    raw = re.sub(r"^\[[ xX]\]\s+", "", raw)
                items.append(split_inline(raw))
                i += 1
            blocks.append(("checklist" if is_checkbox else "bullets", items))
            continue

        # Numerada
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(split_inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            blocks.append(("numbered", items))
            continue

        # Mermaid / flowchart — bloco de código renderizado como IMAGEM no Docs
        if line.strip().startswith("```mermaid"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(("mermaid", "\n".join(code)))
            continue

        # Code block
        if line.strip().startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code)))
            continue

        # HR
        if re.match(r"^={3,}$", line.strip()) or re.match(r"^-{3,}$", line.strip()):
            blocks.append(("hr", None))
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        blocks.append(("para", split_inline(line)))
        i += 1
    return blocks


# ── Mermaid helpers ────────────────────────────────────────────────────

MMDC = "/opt/data/mmdc/node_modules/.bin/mmdc"
MMDC_CONFIG = "/opt/data/mmdc/puppeteer-config.json"


def _fix_mermaid(code):
    """Remove caracteres que quebram o parser mermaid:
    - aspas (' ") e parênteses () em QUALQUER linha de diagrama (labels de nodes, arestas, diamond)
    - colchetes ANINHADOS ([... dentro de [...]]) — o [ interno é interpretado como novo node;
      múltiplos pares de colchetes na MESMA linha (ex.: A[...] --> B[...]) são PRESERVADOS
    - em sequenceDiagram: ; e | em mensagens (quebram o parser)
    Mantém apenas o par de colchetes mais externo de CADA label na linha."""
    is_sequence = "sequenceDiagram" in code or "sequence" in code.lower()
    lines = []
    for line in code.split("\n"):
        if is_sequence and re.search(r"->>|->|-->>", line):
            # Linha de mensagem em sequence: remove ; e | (separadores do parser)
            line = line.replace(";", ",").replace("|", " e ")
        if re.search(r"\[.*\]|\{.*\}|-->|--", line):
            line = line.replace('"', "").replace("'", "")
            # Remove parênteses e colchetes ANINHADOS preservando o nível 0:
            # varre a linha com contagem de profundidade; só apaga caracteres que
            # estão em profundidade >= 1 (dentro de um par já aberto).
            # Parênteses: remove apenas os internos a um colchete/chave (label),
            # mas preserva parênteses no nível 0.
            out = []
            prof_col = 0   # profundidade de colchetes []
            prof_cha = 0   # profundidade de chaves {}
            prof_par = 0   # profundidade de parênteses ()
            for ch in line:
                if ch == "[":
                    prof_col += 1
                    if prof_col == 1:
                        out.append(ch)
                    continue
                if ch == "]":
                    if prof_col > 0:
                        prof_col -= 1
                    if prof_col == 0:
                        out.append(ch)
                    continue
                if ch == "{":
                    prof_cha += 1
                    if prof_cha == 1:
                        out.append(ch)
                    continue
                if ch == "}":
                    if prof_cha > 0:
                        prof_cha -= 1
                    if prof_cha == 0:
                        out.append(ch)
                    continue
                if ch == "(":
                    # remove se estiver DENTRO de um label ([ ou { aberto); preserva nível 0
                    if prof_col > 0 or prof_cha > 0:
                        prof_par += 1
                        continue
                    out.append(ch)
                    continue
                if ch == ")":
                    if prof_par > 0:
                        prof_par -= 1
                        continue
                    out.append(ch)
                    continue
                out.append(ch)
            line = "".join(out)
        lines.append(line)
    return "\n".join(lines)


def _render_mermaid_png(code, out_path):
    """Renderiza mermaid → PNG transparente 2x via mmdc + headless_shell do Hermes."""
    import subprocess
    tmp = out_path + ".mmd"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(_fix_mermaid(code))
    try:
        r = subprocess.run(
            [MMDC, "-i", tmp, "-o", out_path, "-b", "transparent", "-s", "2", "-p", MMDC_CONFIG],
            capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(out_path):
            print(f"  ⚠️ mmdc falhou: {(r.stderr or r.stdout)[-200:]}", file=sys.stderr)
            return False
        return True
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _png_size(path):
    """Lê dimensões (w, h) de um PNG pelo header IHDR (sem depender de PIL)."""
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("não é PNG")
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def _upload_image_drive(png_path, name):
    """Upload do PNG para o Drive e torna público (para insertInlineImage)."""
    import uuid
    boundary = uuid.uuid4().hex
    metadata = json.dumps({"name": name, "mimeType": "image/png"}).encode()
    content = open(png_path, "rb").read()
    parts = [f"--{boundary}\r\n".encode(), b"Content-Type: application/json; charset=UTF-8\r\n\r\n",
             metadata, b"\r\n",
             f"--{boundary}\r\n".encode(), b"Content-Type: image/png\r\n\r\n",
             content, b"\r\n", f"--{boundary}--\r\n".encode()]
    body = b"".join(parts)
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name"
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Authorization": f"Bearer {get_token()}", "Content-Type": f"multipart/related; boundary={boundary}"})
    with urllib.request.urlopen(req) as resp:
        file_id = json.loads(resp.read())["id"]
    # tornar público
    perm = json.dumps({"role": "reader", "type": "anyone"}).encode()
    preq = urllib.request.Request(f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
        data=perm, method="POST",
        headers={"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"})
    urllib.request.urlopen(preq)
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w3000"


# ── API helpers ────────────────────────────────────────────────────────

def api_request(url, method, payload=None):
    headers = {"Authorization": f"Bearer {get_token()}"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:1000]
            if e.code == 429:
                wait = 15 * (attempt + 1)
                print(f"  [429] aguardando {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"API ERROR {e.code} em {method} {url}\n{body}", file=sys.stderr)
            raise
    raise RuntimeError("Rate limit persistente")


def create_doc(title):
    return api_request("https://docs.googleapis.com/v1/documents", "POST", {"title": title})["documentId"]


def replace_doc_content(doc_id):
    doc = api_request(f"https://docs.googleapis.com/v1/documents/{doc_id}", "GET")
    end = doc["body"]["content"][-1]["endIndex"]
    if end <= 2:
        return
    api_request(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate", "POST",
                {"requests": [{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1}}}]})


def move_file(file_id, parent_id):
    info = api_request(f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=parents", "GET")
    current = info.get("parents", [])
    remove = ",".join(current) if current else ""
    api_request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?addParents={parent_id}&removeParents={remove}&fields=id",
        "PATCH")


# ── Construtor de documento em MODO BATCH ──────────────────────────────

class DocBuilder:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.buffer = []
        # Lê o índice final do doc UMA vez; rastreia localmente depois
        doc = api_request(f"https://docs.googleapis.com/v1/documents/{doc_id}", "GET")
        self.cur = doc["body"]["content"][-1]["endIndex"] - 1
        self.ops = 0

    def _add(self, request):
        self.buffer.append(request)
        self.ops += 1
        if len(self.buffer) >= BATCH_SIZE:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}:batchUpdate", "POST",
                    {"requests": self.buffer})
        self.buffer = []

    def insert_text(self, txt):
        """Insere no fim: o índice correto é current_end() - 1 (dentro do último parágrafo vazio).
        O texto inserido começa exatamente nesse índice (sem normalização do endOfSegmentLocation).
        Retorna o start (índice do início do texto)."""
        if not txt:
            return self.cur
        start = self.cur
        self._add({"insertText": {"location": {"index": self.cur}, "text": txt}})
        self.cur += u16len(txt)
        return start

    def apply_inline(self, segs, base_start):
        offset = 0
        for seg in segs:
            tipo, txt = seg[0], seg[1]
            if tipo == "bold":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": base_start + offset, "endIndex": base_start + offset + u16len(txt)},
                    "textStyle": {"bold": True}, "fields": "bold"}})
            elif tipo == "italic":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": base_start + offset, "endIndex": base_start + offset + u16len(txt)},
                    "textStyle": {"italic": True}, "fields": "italic"}})
            elif tipo == "code":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": base_start + offset, "endIndex": base_start + offset + u16len(txt)},
                    "textStyle": {"weightedFontFamily": {"fontFamily": "JetBrains Mono"},
                                 "fontSize": {"magnitude": 9, "unit": "PT"}},
                    "fields": "weightedFontFamily,fontSize"}})
            offset += u16len(txt)

    def clear_bullet(self):
        if self.cur <= 1:
            return  # doc ainda no início — não há parágrafo para limpar
        # cur é o índice de INSERÇÃO = início do parágrafo vazio atual [cur, cur+1]
        self._add({"deleteParagraphBullets": {"range": {"startIndex": self.cur, "endIndex": self.cur + 1}}})

    def _normalize_font(self, start, length):
        """Reseta a fonte para Arial no range [start, start+length) — remove qualquer
        herança de fonte (ex.: mono de um code block anterior)."""
        self._add({"updateTextStyle": {"range": {
            "startIndex": start, "endIndex": start + length},
            "textStyle": {"weightedFontFamily": {"fontFamily": "Arial"}},
            "fields": "weightedFontFamily"}})

    def emit_segs(self, segs, extra_after="\n"):
        """Insere texto + estilos inline + rich links (chips).
        Estratégia: insere o plain (com \uFFFC reservado por chip), aplica estilos,
        depois substitui cada \uFFFC por um insertRichLink — o chip ocupa exatamente
        1 posição, então os índices permanecem válidos.
        Retorna o start (índice do início do texto inserido)."""
        plain = segs_to_plain(segs)
        start = self.insert_text(plain + extra_after)
        self._normalize_font(start, u16len(plain))

        # Aplicar estilos inline (bold/italic/code/link) nos ranges corretos
        offset = 0
        chip_positions = []
        for seg in segs:
            tipo = seg[0]
            if tipo == "richlink":
                chip_positions.append((start + offset, seg[2]))
                offset += 1  # \uFFFC ocupa 1 posição
                continue
            txt = seg[1]
            if tipo == "bold":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": start + offset, "endIndex": start + offset + u16len(txt)},
                    "textStyle": {"bold": True}, "fields": "bold"}})
            elif tipo == "italic":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": start + offset, "endIndex": start + offset + u16len(txt)},
                    "textStyle": {"italic": True}, "fields": "italic"}})
            elif tipo == "code":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": start + offset, "endIndex": start + offset + u16len(txt)},
                    "textStyle": {"weightedFontFamily": {"fontFamily": "JetBrains Mono"},
                                 "fontSize": {"magnitude": 9, "unit": "PT"}},
                    "fields": "weightedFontFamily,fontSize"}})
            elif tipo == "link":
                self._add({"updateTextStyle": {"range": {
                    "startIndex": start + offset, "endIndex": start + offset + u16len(txt)},
                    "textStyle": {"link": {"url": seg[2]}}, "fields": "link"}})
            offset += u16len(txt)

        # Substituir \uFFFC por chips — o insertRichLink INSERE ao lado (não substitui),
        # deixando o \uFFFC em idx+1. Deletar o residual para manter deslocamento líquido 0.
        # Processar de trás para frente: deletes não invalidam índices de chips anteriores.
        for idx, uri in reversed(chip_positions):
            self._add({"insertRichLink": {
                "richLinkProperties": {"uri": uri},
                "location": {"index": idx}}})
            self._add({"deleteContentRange": {
                "range": {"startIndex": idx + 1, "endIndex": idx + 2}}})

        return start

    def add_heading(self, level, segs):
        self.clear_bullet()
        start = self.cur
        self.emit_segs(segs, extra_after="\n")
        style = HEADING_STYLES.get(level, "HEADING_3")
        self._add({"updateParagraphStyle": {"range": {"startIndex": start, "endIndex": self.cur - 1},
                 "paragraphStyle": {"namedStyleType": style}, "fields": "namedStyleType"}})

    def add_para(self, segs):
        self.clear_bullet()
        start = self.emit_segs(segs, extra_after="\n")
        # spaceBelow dá respiro entre parágrafos de texto corrido
        self._add({"updateParagraphStyle": {"range": {
            "startIndex": start, "endIndex": self.cur - 1},
            "paragraphStyle": {"spaceBelow": {"magnitude": 8, "unit": "PT"}},
            "fields": "spaceBelow"}})

    def add_bullets(self, items, numbered=False):
        preset = "NUMBERED_DECIMAL_ALPHA_ROMAN" if numbered else "BULLET_DISC_CIRCLE_SQUARE"
        for segs in items:
            self.clear_bullet()
            start = self.cur
            self.emit_segs(segs, extra_after="\n")
            self._add({"createParagraphBullets": {
                "range": {"startIndex": start, "endIndex": self.cur - 1},
                "bulletPreset": preset}})

    def add_checklist(self, items):
        """Checklist com checkboxes clicáveis (BULLET_CHECKBOX)."""
        for segs in items:
            self.clear_bullet()
            start = self.cur
            self.emit_segs(segs, extra_after="\n")
            self._add({"createParagraphBullets": {
                "range": {"startIndex": start, "endIndex": self.cur - 1},
                "bulletPreset": "BULLET_CHECKBOX"}})

    def add_callout(self, items):
        """Bloco destacado (callout): fundo acinzentado + borda esquerda azul + recuo."""
        for segs in items:
            self.clear_bullet()
            start = self.cur
            self.emit_segs(segs, extra_after="\n")
            self._add({"updateParagraphStyle": {"range": {
                "startIndex": start, "endIndex": self.cur - 1},
                "paragraphStyle": {
                    "shading": {"backgroundColor": {"color": {"rgbColor": {"red": 0.93, "green": 0.94, "blue": 0.96}}}},
                    "borderLeft": {"color": {"color": {"rgbColor": {"red": 0.16, "green": 0.36, "blue": 0.62}}},
                                   "width": {"magnitude": 4, "unit": "PT"}, "dashStyle": "SOLID",
                                   "padding": {"magnitude": 6, "unit": "PT"}},
                    "indentStart": {"magnitude": 18, "unit": "PT"},
                    "spaceBelow": {"magnitude": 8, "unit": "PT"},
                    "spaceAbove": {"magnitude": 8, "unit": "PT"},
                },
                "fields": "shading,borderLeft,indentStart,spaceBelow,spaceAbove"}})

    def add_table(self, header, rows):
        self.clear_bullet()
        self.flush()  # garantir que o buffer anterior foi aplicado antes de reler o doc
        n_rows = len(rows) + 1
        n_cols = max(len(header), max((len(r) for r in rows), default=1))
        # Inserir a tabela no índice atual (self.cur) — depois reler para achar a estrutura
        api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}:batchUpdate", "POST",
                    {"requests": [{"insertTable": {"rows": n_rows, "columns": n_cols,
                     "location": {"index": self.cur}}}]})
        doc = api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}", "GET")
        table_elem = None
        for e in doc["body"]["content"]:
            if "table" in e:
                table_elem = e
        if not table_elem:
            return
        table = table_elem["table"]
        table_start = table_elem["startIndex"]

        # Largura inteligente das colunas: proporcional ao conteúdo (header + células)
        cell_texts = [header] + rows
        max_lens = [0] * n_cols
        for row in cell_texts:
            for ci in range(n_cols):
                if ci < len(row):
                    max_lens[ci] = max(max_lens[ci], len(row[ci]))
        total_len = sum(max_lens) or 1
        total_width = 560  # orçamento total (mesmo da versão anterior — layout já validado)
        widths = []
        for ln in max_lens:
            w = int(total_width * ln / total_len)
            w = max(60, min(300, w))
            widths.append(w)
        # Um request por coluna (cada uma com largura própria), tudo num único batch
        col_reqs = [{"updateTableColumnProperties": {
            "tableStartLocation": {"index": table_start},
            "columnIndices": [ci],
            "tableColumnProperties": {"widthType": "FIXED_WIDTH",
                                      "width": {"magnitude": widths[ci], "unit": "PT"}},
            "fields": "widthType,width"}} for ci in range(n_cols)]
        api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}:batchUpdate", "POST",
                    {"requests": col_reqs})

        # Coletar células e preencher de trás para frente (em batch)
        cell_texts = [header] + rows
        cells = []
        for r_i, row in enumerate(table["tableRows"]):
            for c_i, cell in enumerate(row.get("tableCells", [])):
                if r_i < len(cell_texts) and c_i < len(cell_texts[r_i]):
                    segs = split_inline(cell_texts[r_i][c_i])
                    plain = segs_to_plain(segs)
                    cell_content = cell.get("content", [])
                    if cell_content:
                        cells.append((cell_content[0]["startIndex"], plain, segs, r_i == 0))

        cells.sort(key=lambda c: c[0], reverse=True)
        cell_buf = []
        for cell_para_start, plain, segs, is_header in cells:
            # Célula checkbox? formato "[ ] texto" ou "[x] texto"
            is_cell_checkbox = False
            if re.match(r"^\[[ xX]\]", plain):
                is_cell_checkbox = True
                # remover o "[ ] " do plain (pode sobrar vazio — checkbox vazio é válido)
                plain = re.sub(r"^\[[ xX]\]\s?", "", plain)
                # remover o "[ ] " do primeiro segmento dos segs
                first = segs[0]
                new_txt = re.sub(r"^\[[ xX]\]\s?", "", first[1])
                segs = [("normal", new_txt, None)] + segs[1:] if new_txt else segs[1:]
            if not plain and not is_cell_checkbox:
                continue  # célula vazia sem checkbox — insertText com "" é rejeitado (400)
            if plain:
                cell_buf.append({"insertText": {"location": {"index": cell_para_start}, "text": plain}})
            if is_cell_checkbox:
                cell_buf.append({"createParagraphBullets": {
                    "range": {"startIndex": cell_para_start, "endIndex": cell_para_start + max(u16len(plain), 1)},
                    "bulletPreset": "BULLET_CHECKBOX"}})
            if is_header:
                cell_buf.append({"updateTextStyle": {"range": {
                    "startIndex": cell_para_start, "endIndex": cell_para_start + u16len(plain)},
                    "textStyle": {"bold": True}, "fields": "bold"}})
            # inline formatting dentro da célula (formato: tipo, texto, url)
            offset = 0
            chip_positions = []  # (índice_absoluto, uri) — processar de trás p/ frente
            for seg in segs:
                tipo, txt = seg[0], seg[1]
                if tipo == "richlink":
                    chip_positions.append((cell_para_start + offset, seg[2]))
                    offset += 1  # \uFFFC ocupa 1 posição
                    continue
                if tipo == "bold":
                    cell_buf.append({"updateTextStyle": {"range": {
                        "startIndex": cell_para_start + offset, "endIndex": cell_para_start + offset + u16len(txt)},
                        "textStyle": {"bold": True}, "fields": "bold"}})
                elif tipo == "code":
                    cell_buf.append({"updateTextStyle": {"range": {
                        "startIndex": cell_para_start + offset, "endIndex": cell_para_start + offset + u16len(txt)},
                        "textStyle": {"weightedFontFamily": {"fontFamily": "JetBrains Mono"},
                                     "fontSize": {"magnitude": 9, "unit": "PT"}},
                        "fields": "weightedFontFamily,fontSize"}})
                elif tipo == "link":
                    cell_buf.append({"updateTextStyle": {"range": {
                        "startIndex": cell_para_start + offset, "endIndex": cell_para_start + offset + u16len(txt)},
                        "textStyle": {"link": {"url": seg[2]}}, "fields": "link"}})
                offset += u16len(txt)
            # Chips na célula: insertRichLink INSERE ao lado (não substitui) → \uFFFC
            # residual fica em idx+1. Deletar o residual; processar de trás p/ frente
            # para que deletes não invalidem índices de chips anteriores.
            for chip_idx, uri in reversed(chip_positions):
                cell_buf.append({"insertRichLink": {
                    "richLinkProperties": {"uri": uri},
                    "location": {"index": chip_idx}}})
                cell_buf.append({"deleteContentRange": {
                    "range": {"startIndex": chip_idx + 1, "endIndex": chip_idx + 2}}})
            if len(cell_buf) >= BATCH_SIZE:
                api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}:batchUpdate", "POST",
                            {"requests": cell_buf})
                cell_buf = []
        if cell_buf:
            api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}:batchUpdate", "POST",
                        {"requests": cell_buf})

        # Atualizar self.cur para o fim do doc (após a tabela + parágrafo vazio)
        doc = api_request(f"https://docs.googleapis.com/v1/documents/{self.doc_id}", "GET")
        self.cur = doc["body"]["content"][-1]["endIndex"] - 1

    def add_code(self, code):
        self.clear_bullet()
        start = self.insert_text(code + "\n")
        self._add({"updateTextStyle": {"range": {"startIndex": start, "endIndex": self.cur - 1},
                 "textStyle": {"weightedFontFamily": {"fontFamily": "JetBrains Mono"},
                               "fontSize": {"magnitude": 9, "unit": "PT"}},
                 "fields": "weightedFontFamily,fontSize"}})

    def add_mermaid(self, code):
        """Renderiza flowchart mermaid como imagem (transparente, 2x) e insere no doc.
        Dimensiona para CABER na página: max 550pt largura / 700pt altura (proporcional)."""
        self.clear_bullet()
        import tempfile
        import os as _os
        tmp_dir = tempfile.mkdtemp(prefix="mermaid-")
        png_path = _os.path.join(tmp_dir, "flow.png")
        try:
            if not _render_mermaid_png(code, png_path):
                # fallback: inserir o código como texto (não perde conteúdo)
                self.add_code(code)
                return
            uri = _upload_image_drive(png_path, "cfp-ia-flowchart.png")
            # Dimensões em PT: 2x de 96dpi → 72pt por 96px * 2 = 0.75pt/px
            px_w, px_h = _png_size(png_path)
            max_w, max_h = 550.0, 700.0
            scale = min(max_w / (px_w * 0.75), max_h / (px_h * 0.75), 1.0)
            w_pt = round(px_w * 0.75 * scale, 1)
            h_pt = round(px_h * 0.75 * scale, 1)
            self._add({"insertInlineImage": {
                "location": {"index": self.cur},
                "uri": uri,
                "objectSize": {"width": {"magnitude": w_pt, "unit": "PT"},
                               "height": {"magnitude": h_pt, "unit": "PT"}}}})
            # imagem ocupa 1 posição de índice
            self.cur += 1
            self._add({"insertText": {"location": {"index": self.cur}, "text": "\n"}})
            self.cur += 1
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def finish(self):
        self.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_file")
    ap.add_argument("--title", required=True)
    ap.add_argument("--doc-id", default=None)
    ap.add_argument("--parent", default=None)
    args = ap.parse_args()

    text = open(args.md_file, encoding="utf-8").read()
    blocks = parse_md(text)

    if args.doc_id:
        doc_id = args.doc_id
        print(f"Atualizando doc existente {doc_id}...")
        replace_doc_content(doc_id)
    else:
        doc_id = create_doc(args.title)
        print(f"Doc criado: {doc_id}")
        if args.parent:
            move_file(doc_id, args.parent)
            print(f"Movido para pasta {args.parent}")

    b = DocBuilder(doc_id)
    for tipo, dados in blocks:
        if tipo == "heading":
            level, segs = dados
            b.add_heading(level, segs)
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
            header, rows = dados
            b.add_table(header, rows)
        elif tipo == "code":
            b.add_code(dados)
        elif tipo == "mermaid":
            b.add_mermaid(dados)
        elif tipo == "hr":
            b.insert_text("\n")
    b.finish()

    print(f"Conteúdo aplicado: {len(blocks)} blocos ({b.ops} operações em batches)")
    print(f"URL: https://docs.google.com/document/d/{doc_id}/edit")


if __name__ == "__main__":
    main()
