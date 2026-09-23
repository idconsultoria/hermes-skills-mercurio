#!/usr/bin/env python3
"""Extrai fontes embutidas (@font-face com data:...;base64) de um HTML aprovado para arquivos
locais, para reuso com url() relativo em qualquer HTML novo.

Uso: python3 extrair_fontes.py <template.html> <pasta_saida>
Gera: <pasta_saida>/<familia>-<peso>-<estilo>.<otf|ttf|woff2|woff>

Por que: o Chromium resolve caminho relativo igual ao file:// e o pacote sobrevive ao zip.
Procurar o arquivo de fonte no disco costuma falhar (a licenciada vive embutida no template).
"""
import re, sys, base64, pathlib

SRC = sys.argv[1]
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
html = pathlib.Path(SRC).read_text(encoding="utf-8", errors="ignore")

blocks = re.findall(r"@font-face\s*\{(.*?)\}", html, re.S)
print("blocos @font-face:", len(blocks))
ext = {"font/otf": "otf", "font/ttf": "ttf", "font/woff2": "woff2", "font/woff": "woff"}
for b in blocks:
    fam = re.search(r"font-family:\s*['\"]?([^;'\"]+)", b)
    wgt = re.search(r"font-weight:\s*([^;]+)", b)
    sty = re.search(r"font-style:\s*([^;]+)", b)
    m = re.search(r"url\(data:(font/[a-z0-9]+);base64,([A-Za-z0-9+/=]+)\)", b)
    if not (fam and m):
        continue
    name = re.sub(r"[^a-z0-9]+", "-", fam.group(1).lower()).strip("-")
    weight = wgt.group(1).strip() if wgt else "400"
    style = sty.group(1).strip() if sty else "normal"
    fn = f"{name}-{weight}-{style}.{ext.get(m.group(1), 'bin')}"
    data = base64.b64decode(m.group(2))
    (OUT / fn).write_bytes(data)
    print(f"  {fn:34s} {len(data)/1024:8.0f} KB   (family={fam.group(1).strip()})")
