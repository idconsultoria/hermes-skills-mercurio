#!/usr/bin/env python3
"""Gera EPUB 3 (com NCX para Kindle antigo + capa JPEG) a partir de um JSON de capítulos.

Uso:
    python build_epub.py chapters.json saida.epub

Formato do JSON:
{
  "title": "Manifesto",
  "subtitle": "Partido ... · Diretório Nacional",
  "cover_line": "Documento de fundação",
  "kicker_top": "PDT · documento de fundação",
  "author": "Partido ...", "publisher": "...", "language": "pt-BR",
  "css": "opcional: css extra concatenado ao padrão",
  "chapters": [{"title": "I — Princípios", "kicker": "Princípio I", "html": "<p>...</p>"}],
  "notes": ["nota de edição"]
}

O HTML de cada capítulo é um fragmento XHTML do subconjunto seguro (p/ul/li/ol/h2/div simples).
Única dependência opcional: Pillow, para a capa tipográfica; sem ele a capa é só texto.
"""
import json, re, sys, uuid, zipfile, datetime, html
from pathlib import Path

CSS = """@charset "utf-8";
body{font-family:serif;line-height:1.55;margin:0;padding:0.6em 0.7em 1.2em;color:#16242f}
h1{font-family:sans-serif;font-size:1.5em;line-height:1.2;margin:0 0 .2em;color:#0a1929}
h2{font-family:sans-serif;font-size:1.18em;line-height:1.25;margin:1.4em 0 .5em;color:#0a1929;
   border-top:2px solid #14b8a6;padding-top:.55em;page-break-after:avoid}
p{margin:0 0 .85em;text-indent:0}
.kicker{font-family:sans-serif;font-size:.72em;letter-spacing:.14em;text-transform:uppercase;
        color:#14b8a6;font-weight:bold;margin:0 0 .3em}
.sub{font-family:sans-serif;font-size:.9em;color:#5c7182;margin:0 0 1.4em}
.lead{border-left:3px solid #14b8a6;padding-left:.7em;margin:.8em 0 1.2em}
.item{margin:0 0 .9em;padding:.55em .6em;background:#f2f7f8;border-left:3px solid #cfe6e2}
.num,.ref{font-family:sans-serif;font-weight:bold;color:#0f8c80}
.num{margin-right:.35em}
.lbl{font-weight:bold;margin-top:.9em}
ul.subs{margin:.3em 0 .6em 1em;padding:0}
ol{margin:.4em 0 .8em 1.2em;padding:0}
.note{font-size:.84em;color:#5c7182;border-top:1px solid #dbe6ec;margin-top:1.6em;padding-top:.8em}
.cover{text-align:center;padding-top:2.2em}
.cover img{max-width:100%}
"""

esc = lambda t: html.escape(str(t), quote=False)


def make_cover(path, title, subtitle, cover_line, accent="#14b8a6"):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    W, H = 1200, 1600
    img = Image.new("RGB", (W, H), (10, 25, 41))
    d = ImageDraw.Draw(img)
    acc = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5))

    def font(sz, bold=False):
        cands = [f"/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans{'-Bold' if bold else ''}.ttf",
                 f"/system/fonts/Roboto{'-Bold' if bold else '-Regular'}.ttf"]
        for c in cands:
            try:
                return ImageFont.truetype(c, sz)
            except Exception:
                continue
        return ImageFont.load_default()

    def wrap(text, f, maxw):
        words, lines, cur = str(text).split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                lines.append(cur); cur = w
        if cur:
            lines.append(cur)
        return lines

    d.rectangle([0, 0, W, 14], fill=acc)
    d.rectangle([0, H - 12, W, H], fill=acc)
    d.rectangle([90, 240, 104, 1120], fill=acc)
    y = 420
    for ln in wrap(title, font(120, True), W - 240):
        d.text((150, y), ln, font=font(120, True), fill=(255, 255, 255)); y += 140
    y += 10
    d.rectangle([150, y, 470, y + 5], fill=acc)
    y += 55
    for ln in wrap(subtitle, font(38), W - 240):
        d.text((150, y), ln, font=font(38), fill=(169, 193, 210)); y += 52
    y2 = H - 260
    for ln in wrap(cover_line, font(30), W - 240):
        d.text((150, y2), ln, font=font(30), fill=(127, 154, 173)); y2 += 44
    img.save(path, "JPEG", quality=88)
    return True


def build(data, out_path):
    out_path = Path(out_path)
    title = data.get("title", "Documento")
    subtitle = data.get("subtitle", "")
    cover_line = data.get("cover_line", "")
    lang = data.get("language", "pt-BR")
    chapters = data["chapters"]
    notes = data.get("notes") or []
    bid = "urn:uuid:" + str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    cover_jpg = out_path.with_suffix(".cover.jpg")
    has_cover = make_cover(cover_jpg, title, subtitle, cover_line)

    pages = []
    for i, ch in enumerate(chapters, start=1):
        front = ""
        if i == 1:
            front = (f'<p class="kicker">{esc(data.get("kicker_top", ""))}</p>'
                     f'<h1>{esc(title)}</h1><p class="sub">{esc(subtitle)}</p>')
        kick = f'<p class="kicker">{esc(ch["kicker"])}</p>' if ch.get("kicker") else ""
        body = ch.get("html", "")
        if notes and i == len(chapters):
            body += ('<div class="note"><p class="lbl">Nota sobre esta edição</p>'
                     + "".join(f"<p>{esc(n)}</p>" for n in notes) + "</div>")
        pages.append(f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">
<head><meta charset="utf-8"/><title>{esc(ch["title"])}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
{front}
{kick}
<h2>{esc(ch["title"])}</h2>
{body}
</body></html>''')

    cover_page = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}" lang="{lang}">
<head><meta charset="utf-8"/><title>{esc(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body class="cover">{'<img src="cover.jpg" alt="capa"/>' if has_cover else '<h1>' + esc(title) + '</h1>'}</body></html>'''

    nav = (f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}">
<head><meta charset="utf-8"/><title>Sumário</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><nav epub:type="toc" id="toc"><h1>Sumário</h1><ol>'''
           + "".join(f'<li><a href="ch{i:02d}.xhtml">{esc(c["title"])}</a></li>' for i, c in enumerate(chapters, 1))
           + "</ol></nav></body></html>")

    ncx = (f'''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="{lang}">
<head><meta name="dtb:uid" content="{bid}"/><meta name="dtb:depth" content="1"/>
<meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>
<docTitle><text>{esc(title)}</text></docTitle>
<navMap>'''
           + "".join(f'<navPoint id="np{i}" playOrder="{i}"><navLabel><text>{esc(c["title"])}</text></navLabel>'
                     f'<content src="ch{i:02d}.xhtml"/></navPoint>' for i, c in enumerate(chapters, 1))
           + "</navMap></ncx>")

    manifest = "\n".join(f'    <item id="ch{i:02d}" href="ch{i:02d}.xhtml" media-type="application/xhtml+xml"/>'
                          for i in range(1, len(chapters) + 1))
    spine = "\n".join(f'    <itemref idref="ch{i:02d}"/>' for i in range(1, len(chapters) + 1))
    cover_item = ('\n    <item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>'
                  if has_cover else "")
    cover_meta = '\n    <meta name="cover" content="cover-image"/>' if has_cover else ""
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{lang}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{bid}</dc:identifier>
    <dc:title>{esc(title)}</dc:title>
    <dc:creator>{esc(data.get("author", ""))}</dc:creator>
    <dc:publisher>{esc(data.get("publisher", ""))}</dc:publisher>
    <dc:language>{lang}</dc:language>
    <dc:date>{now}</dc:date>
    <meta property="dcterms:modified">{now}</meta>{cover_meta}
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
    <item id="coverpage" href="cover.xhtml" media-type="application/xhtml+xml"/>{cover_item}
{manifest}
  </manifest>
  <spine toc="ncx">
    <itemref idref="coverpage"/>
{spine}
  </spine>
  <guide><reference type="cover" title="Capa" href="cover.xhtml"/></guide>
</package>'''

    container = '''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>'''

    css = CSS + (data.get("css") or "")
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", css, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/cover.xhtml", cover_page, compress_type=zipfile.ZIP_DEFLATED)
        if has_cover:
            z.write(cover_jpg, "OEBPS/cover.jpg", compress_type=zipfile.ZIP_STORED)
        for i, pg in enumerate(pages, start=1):
            z.writestr(f"OEBPS/ch{i:02d}.xhtml", pg, compress_type=zipfile.ZIP_DEFLATED)
    if has_cover:
        cover_jpg.unlink(missing_ok=True)
    return out_path


def verify(path):
    import xml.dom.minidom as md
    path = Path(path)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert z.read("mimetype") == b"application/epub+zip", "mimetype errado ou comprimido"
        for n in names:
            if n.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                md.parseString(z.read(n))
        chs = [n for n in names if re.match(r"OEBPS/ch\d+\.xhtml$", n)]
        leftovers = []
        for n in chs:
            s = z.read(n).decode("utf-8")
            for bad in ('class="badge"', "</p></p>", '<div class="item"'):
                if bad in s:
                    leftovers.append((n, bad))
    print(f"{path} · {path.stat().st_size} bytes · {len(names)} arquivos · {len(chs)} capítulos")
    print("XML válido em todos os capítulos · mimetype OK")
    if leftovers:
        print("RESTOS DE MARCAÇÃO:", leftovers)
    return not leftovers


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("uso: python build_epub.py chapters.json saida.epub")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = build(data, sys.argv[2])
    sys.exit(0 if verify(out) else 1)
