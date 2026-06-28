#!/usr/bin/env python3
"""
kindlegen replacement: converts KCC-generated EPUB to MOBI format.
Drops in where KCC calls 'kindlegen' so MOBI output works on any arch.

Creates a PalmDB (PDB) file with:
  - PDB header (BOOK/MOBI type)
  - MOBI header with EXTH metadata (title, author, manga/right-to-left mode)
  - JPEG page images as sequential PalmDB records

Usage:
    python3 kindlegen-replacement.py /path/to/output.epub
    # Creates /path/to/output.mobi
"""
import sys, os, struct
from zipfile import ZipFile
from xml.etree import ElementTree as ET

PALMDOC_TYPE = b'BOOK'
PALMDOC_CREATOR = b'MOBI'

def make_pdb_header(records, title):
    title_bytes = title.encode('utf-8')[:31]
    title_padded = title_bytes + b'\x00' * (32 - len(title_bytes))
    num_records = len(records)
    header_size = 78 + (num_records * 8)
    h = struct.pack('>32s', title_padded)
    h += struct.pack('>H', 0)
    h += struct.pack('>H', 0)
    h += struct.pack('>I', 0)
    h += struct.pack('>I', 0)
    h += struct.pack('>I', 0)
    h += struct.pack('>I', 0)
    h += struct.pack('>I', header_size)
    h += struct.pack('>I', header_size)
    h += PALMDOC_TYPE
    h += PALMDOC_CREATOR
    h += struct.pack('>I', 0)
    h += struct.pack('>I', 0)
    h += struct.pack('>H', num_records)
    offset = header_size
    for i, (rec_data) in enumerate(records):
        h += struct.pack('>I', offset)
        h += struct.pack('>B', 0)
        uid_bytes = struct.pack('>I', i)
        h += uid_bytes[:3]
        offset += len(rec_data)
    return h

def make_mobi_header(html_content, images, title, author='KCC'):
    mobi_ident = b'MOBI'
    mobi_header_len = 232

    exth_records = []
    title_b = title.encode('utf-8') + b'\x00'
    author_b = author.encode('utf-8') + b'\x00'
    exth_records.append(struct.pack('>II', 100, len(title_b)) + title_b)
    exth_records.append(struct.pack('>II', 103, len(author_b)) + author_b)
    exth_records.append(struct.pack('>II', 501, 2) + b'\x00\x00')

    exth_data = b''.join(exth_records)
    exth_len = 12 + len(exth_data)
    exth_header = struct.pack('>II', 0x45585448, exth_len)
    exth_header += struct.pack('>H', 1)
    exth_header += struct.pack('>H', len(exth_records))
    exth_data = exth_header + exth_data
    mobi_header_len = 232 + len(exth_data)

    mobi = mobi_ident
    mobi += struct.pack('>I', mobi_header_len)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', len(html_content))
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += b'\x00' * 8
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += b'\x00' * 32
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += b'\x00' * 12
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>I', 0)
    mobi += struct.pack('>H', 0)
    mobi += struct.pack('>H', 0)
    mobi += struct.pack('>H', 0)
    mobi += b'\x00' * 30

    # Insert EXTH after the 232-byte base header
    mobi = mobi[:232] + exth_data
    return mobi

def convert(epub_path, output_path=None):
    with ZipFile(epub_path, 'r') as zf:
        image_data = {}
        html_content = None
        title = os.path.splitext(os.path.basename(epub_path))[0]
        author = 'KCC'
        for name in zf.namelist():
            if name.startswith('OEBPS/Images/') or '/img/' in name:
                image_data[name] = zf.read(name)
            elif name.endswith('.opf'):
                try:
                    root = ET.fromstring(zf.read(name))
                    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
                    te = root.find('.//dc:title', ns)
                    if te is not None and te.text:
                        title = te.text
                    ae = root.find('.//dc:creator', ns)
                    if ae is not None and ae.text:
                        author = ae.text
                except Exception:
                    pass
            elif name.endswith(('.html', '.xhtml')) and html_content is None:
                html_content = zf.read(name)

    sorted_names = sorted(image_data.keys())
    images = [image_data[n] for n in sorted_names]

    if not images:
        print("Error: No images found in EPUB")
        return False

    if not html_content:
        parts = ['<?xml version="1.0"?><html><head><meta charset="utf-8"/><title>'
                  + title + '</title></head><body>']
        for i in range(len(images)):
            parts.append(f'<p><img src="img_{i:04d}.jpg" alt="p{i+1}"/></p>')
        parts.append('</body></html>')
        html_content = '\n'.join(parts).encode('utf-8')

    mobi_header = make_mobi_header(html_content, images, title, author)
    records = [mobi_header + html_content] + images
    pdb_header = make_pdb_header(records, title)

    if output_path is None:
        output_path = os.path.splitext(epub_path)[0] + '.mobi'
    with open(output_path, 'wb') as f:
        f.write(pdb_header)
        for rec in records:
            f.write(rec)

    mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"MOBI created: {output_path} ({mb:.0f} MB)")
    return True

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    epub_path = next((a for a in args if a.endswith('.epub')), None)
    if not epub_path:
        print("Usage: kindlegen-replacement.py <epub> [output.mobi]")
        sys.exit(1)
    output = None
    if len(args) > 1:
        output = args[1] if args[1].endswith('.mobi') else None
    convert(epub_path, output)
