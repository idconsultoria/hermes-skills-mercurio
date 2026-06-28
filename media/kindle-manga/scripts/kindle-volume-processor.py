#!/usr/bin/env python3
"""
kindle_volume_processor.py — Process a single manga volume for Kindle PW11.
Downloads source from Archive.org, extracts images, filters out tiny overlays,
processes grayscale+upscale+contrast, builds fixed-layout EPUB, and uploads
to Google Drive (or sends email if under 25 MB).

Usage:
  python3 kindle_volume_processor.py MONSTER 1
  python3 kindle_volume_processor.py BERSERK 1

Available series:
  MONSTER - monster-manga collection, Monster vNN (CM).epub
  BERSERK - manga_Berserk collection, danke-Empire HD CBZ
"""
import sys, os, json, base64, subprocess, urllib.parse, shutil, re
from zipfile import ZipFile, ZIP_STORED
from PIL import Image, ImageOps
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from io import BytesIO

TARGET_W, TARGET_H = 1236, 1648
KINDLE_EMAIL = "gustavomelloenciv_0yDkTw@kindle.com"
FROM_EMAIL = "gustavomelloenciv@gmail.com"
TOKEN_PATH = "/opt/data/google_token.json"
GAPI = "/opt/data/venvs/google/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py"

SERIES = {
    "MONSTER": {
        "collection": "monster-manga",
        "pattern": re.compile(r"Monster v(\d+) \(CM\)\.epub$"),
        "author": "Naoki Urasawa",
        "quality": 85,
        "volumes": 18,
        "type": "epub",
    },
    "BERSERK": {
        "collection": "manga_Berserk",
        "pattern": re.compile(r"!Berserk \[danke-Empire\]\{HD\}/Berserk v(\d+) \(\d{4}\) \(Digital\) \(danke-Empire\)\.cbz$"),
        "author": "Kentaro Miura",
        "quality": 85,
        "volumes": 38,
        "type": "cbz",
    },
}

def find_source(series_key, vol_num):
    info = SERIES[series_key]
    r = subprocess.run(["curl", "-s", f"https://archive.org/metadata/{info['collection']}"],
                       capture_output=True, text=True, timeout=30)
    data = json.loads(r.stdout)
    for f in data.get('files', []):
        name = f.get('name', '')
        m = info['pattern'].search(name)
        if m and int(m.group(1)) == vol_num:
            return name, int(f.get('size', 0))
    return None, 0

def download(url, dest):
    r = subprocess.run(["curl", "-sL", "--connect-timeout", "60", "--max-time", "900",
                        "-H", "User-Agent: Mozilla/5.0", url],
                       capture_output=True, timeout=950)
    if r.returncode != 0 or len(r.stdout) < 50000:
        raise RuntimeError(f"Download failed: return={r.returncode}, size={len(r.stdout)}")
    with open(dest, 'wb') as f:
        f.write(r.stdout)

def extract_images(source_path, raw_dir):
    os.makedirs(raw_dir, exist_ok=True)
    count = 0
    with ZipFile(source_path) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith(('.jpg','.jpeg','.png')): continue
            if '__MACOSX' in name or '/.' in name: continue
            data = z.read(name)
            if len(data) < 2000: continue
            try:
                test = Image.open(BytesIO(data))
                if min(test.size) < 300: continue
            except: continue
            fname = f"{count+1:04d}.jpg"
            with open(os.path.join(raw_dir, fname), 'wb') as f:
                f.write(data)
            count += 1
    return count

def process_image(src, dst, quality):
    img = Image.open(src)
    if img.mode not in ('RGB', 'L'): img = img.convert('RGB')
    gray = img.convert('L')
    hist = gray.histogram()
    if sum(hist[:64]) / sum(hist) * 100 < 5:
        gray = ImageOps.autocontrast(gray, cutoff=1)
    ow, oh = gray.size
    ratio = TARGET_H / oh
    new_w = int(ow * ratio)
    if new_w > TARGET_W:
        ratio = TARGET_W / ow
        new_h = int(oh * ratio)
        resized = gray.resize((TARGET_W, new_h), Image.LANCZOS)
        canvas = Image.new('L', (TARGET_W, TARGET_H), 255)
        canvas.paste(resized, (0, (TARGET_H - new_h) // 2))
    else:
        resized = gray.resize((new_w, TARGET_H), Image.LANCZOS)
        canvas = Image.new('L', (TARGET_W, TARGET_H), 255)
        canvas.paste(resized, ((TARGET_W - new_w) // 2, 0))
    canvas.save(dst, 'JPEG', quality=quality, optimize=True)

def build_epub(proc_dir, output_path, title, author):
    files = sorted([f for f in os.listdir(proc_dir) if f.endswith('.jpg')])
    with ZipFile(output_path, 'w', ZIP_STORED) as zf:
        zf.writestr('mimetype', 'application/epub+zip', compress_type=ZIP_STORED)
        zf.writestr('META-INF/container.xml',
            '<?xml version="1.0"?><container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles></container>')
        css = ('@page{margin:0;padding:0}'
               'html,body{margin:0;padding:0;width:100%;height:100%;'
               'background-color:#fff;text-align:center}'
               'img{display:block;max-width:100%;max-height:100%;'
               'margin:0 auto;padding:0}')
        zf.writestr('OEBPS/css/base.css', css)
        manifest = ['<item id="css" href="css/base.css" media-type="text/css"/>']
        spine = []
        for i, fname in enumerate(files):
            pid = f'p{i:04d}'; iid = f'i{i:04d}'
            with open(os.path.join(proc_dir, fname), 'rb') as f:
                zf.writestr(f'OEBPS/Images/{fname}', f.read())
            xhtml = (f'<?xml version="1.0" encoding="utf-8"?>'
                     f'<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">'
                     f'<head><meta charset="utf-8"/>'
                     f'<link rel="stylesheet" type="text/css" href="../css/base.css"/>'
                     f'</head><body>'
                     f'<img src="../Images/{fname}" alt="Page {i+1}"/>'
                     f'</body></html>')
            zf.writestr(f'OEBPS/xhtml/{pid}.xhtml', xhtml.encode('utf-8'))
            manifest.append(f'<item id="{pid}" href="xhtml/{pid}.xhtml" '
                           f'media-type="application/xhtml+xml"/>')
            manifest.append(f'<item id="{iid}" href="Images/{fname}" '
                           f'media-type="image/jpeg"/>')
            spine.append(f'<itemref idref="{pid}"/>')
        opf = (f'<?xml version="1.0" encoding="utf-8"?>'
               f'<package xmlns="http://www.idpf.org/2007/opf" version="2.0" '
               f'unique-identifier="bookid" '
               f'xmlns:rendition="http://www.idpf.org/vocab/rendition/#">'
               f'<metadata>'
               f'<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">'
               f'{title}</dc:title>'
               f'<dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">'
               f'{author}</dc:creator>'
               f'<dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">'
               f'en</dc:language>'
               f'<meta property="rendition:layout">pre-paginated</meta>'
               f'<meta name="fixed-layout" content="true"/>'
               f'<meta name="zero-margin" content="true"/>'
               f'<meta property="rendition:orientation">auto</meta>'
               f'<meta property="rendition:spread">none</meta>'
               f'</metadata>'
               f'<manifest>\n    ' + '\n    '.join(manifest) + '\n</manifest>'
               f'<spine page-progression-direction="rtl">\n    '
               + '\n    '.join(spine) + '\n</spine></package>')
        zf.writestr('OEBPS/content.opf', opf.encode('utf-8'))

def upload_to_drive(path, name):
    r = subprocess.run(GAPI.split() + ["drive", "upload", path, "--name", name],
                       capture_output=True, text=True, timeout=120)
    result = json.loads(r.stdout)
    file_id = result.get('id', '')
    subprocess.run(GAPI.split() + ["drive", "share", file_id,
                                    "--type", "anyone", "--role", "reader"],
                   capture_output=True, text=True, timeout=30)
    return f"https://drive.google.com/file/d/{file_id}/view"

def main():
    if len(sys.argv) < 3:
        print("Usage: kindle_volume_processor.py SERIES VOLUME")
        sys.exit(1)

    series_key = sys.argv[1].upper()
    vol = int(sys.argv[2])
    info = SERIES[series_key]

    print(f"\n{'='*60}\n{series_key} Vol.{vol:02d}\n{'='*60}")

    workdir = f"/tmp/manga_q85/{series_key.lower()}/v{vol:02d}"
    os.makedirs(workdir, exist_ok=True)

    print("Locating source...", end=' ', flush=True)
    filename, size = find_source(series_key, vol)
    if not filename:
        print("NOT FOUND")
        return

    encoded = urllib.parse.quote(filename, safe='')
    url = f"https://archive.org/download/{info['collection']}/{encoded}"
    src_path = f"{workdir}/source.{info['type']}"

    print(f"Downloading {size/1024/1024:.0f} MB...", end=' ', flush=True)
    download(url, src_path)

    raw_dir = f"{workdir}/raw"
    print("Extracting...", end=' ', flush=True)
    count = extract_images(src_path, raw_dir)
    print(f"{count} pages")

    proc_dir = f"{workdir}/proc"
    os.makedirs(proc_dir, exist_ok=True)
    print(f"Processing Q{info['quality']}...", end=' ', flush=True)
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.endswith('.jpg'): continue
        process_image(os.path.join(raw_dir, fname),
                      os.path.join(proc_dir, fname), info['quality'])

    out_name = f"{series_key.title()}_Vol{vol:02d}_Q{info['quality']}.epub"
    out_path = f"{workdir}/{out_name}"
    print("Building EPUB...", end=' ', flush=True)
    build_epub(proc_dir, out_path, f"{series_key.title()} Vol.{vol:02d}", info['author'])

    link = upload_to_drive(out_path, out_name)
    print(f"Done: {link}")
    shutil.rmtree(workdir, ignore_errors=True)

if __name__ == '__main__':
    main()
