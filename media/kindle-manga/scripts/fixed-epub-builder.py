#!/usr/bin/env python3
"""Build a fixed-layout image-based EPUB for Kindle (edge-to-edge, no margins).

Each image gets its own XHTML page with margin:0 CSS and the OPF declares
rendition:layout=pre-paginated (with hyphen!), fixed-layout=true, and
zero-margin=true. This tells Kindle's EPUB renderer to display each page
full-screen without automatic margins.

Paths are relative: XHTML pages are in OEBPS/xhtml/, images in
OEBPS/Images/, so src uses ../Images/filename.jpg.

Usage:
    python3 fixed-epub-builder.py <images_dir> <output.epub> <title> <author>

Images must be JPEG files named with zero-padded sortable names (e.g. 0001.jpg).
"""
import os, sys
from zipfile import ZipFile, ZIP_STORED

def build(images_dir, output_path, title, author):
    ext = '.jpg'
    images = sorted([f for f in os.listdir(images_dir) if f.endswith(ext)])
    if not images:
        print("No JPEG images found.")
        return False

    print(f"Building {title}: {len(images)} pages")

    with ZipFile(output_path, 'w', ZIP_STORED) as zf:
        zf.writestr('mimetype', 'application/epub+zip', compress_type=ZIP_STORED)

        zf.writestr('META-INF/container.xml', (
            '<?xml version="1.0"?>\n'
            '<container version="1.0" '
            'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            '  <rootfiles>\n'
            '    <rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/>\n'
            '  </rootfiles>\n'
            '</container>'
        ))

        css = (
            '@page { margin: 0; padding: 0; }\n'
            'html, body { margin: 0; padding: 0; width: 100%; height: 100%; '
            'background-color: #fff; text-align: center; }\n'
            'img { display: block; max-width: 100%; max-height: 100%; '
            'margin: 0 auto; padding: 0; }\n'
        )
        zf.writestr('OEBPS/css/base.css', css)

        manifest = ['<item id="css" href="css/base.css" media-type="text/css"/>']
        spine = []

        for i, fname in enumerate(images):
            pid = f'p{i:04d}'
            if i == 0:
                iid = 'cover-image'
                is_cover = ' properties="cover-image"'
            else:
                iid = f'i{i:04d}'
                is_cover = ''

            with open(os.path.join(images_dir, fname), 'rb') as f:
                zf.writestr(f'OEBPS/Images/{fname}', f.read())

            xhtml = (
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<!DOCTYPE html>\n'
                '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                '<head>\n'
                '  <meta charset="utf-8"/>\n'
                '  <link rel="stylesheet" type="text/css" href="../css/base.css"/>\n'
                '</head>\n'
                '<body>\n'
                f'  <img src="../Images/{fname}" alt="Page {i+1}"/>\n'
                '</body>\n'
                '</html>'
            )
            zf.writestr(f'OEBPS/xhtml/{pid}.xhtml', xhtml.encode('utf-8'))

            manifest.append(
                f'<item id="{pid}" href="xhtml/{pid}.xhtml" '
                f'media-type="application/xhtml+xml"/>'
            )
            manifest.append(
                f'<item id="{iid}" href="Images/{fname}" '
                f'media-type="image/jpeg"{is_cover}/>'
            )
            spine.append(f'<itemref idref="{pid}"/>')

        man_xml = '\n    '.join(manifest)
        spi_xml = '\n    '.join(spine)

        opf = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" '
            'unique-identifier="bookid" '
            'xmlns:rendition="http://www.idpf.org/vocab/rendition/#">\n'
            '<metadata>\n'
            '  <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">'
            + title + '</dc:title>\n'
            '  <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">'
            + author + '</dc:creator>\n'
            '  <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">'
            'en</dc:language>\n'
            '  <meta name="cover" content="cover-image"/>\n'
            '  <meta property="rendition:layout">pre-paginated</meta>\n'
            '  <meta name="fixed-layout" content="true"/>\n'
            '  <meta name="zero-margin" content="true"/>\n'
            '  <meta property="rendition:orientation">auto</meta>\n'
            '  <meta property="rendition:spread">none</meta>\n'
            '</metadata>\n'
            '<manifest>\n    ' + man_xml + '\n</manifest>\n'
            '<spine page-progression-direction="rtl">\n    '
            + spi_xml + '\n</spine>\n'
            '</package>'
        )
        zf.writestr('OEBPS/content.opf', opf.encode('utf-8'))

    size_mb = os.path.getsize(output_path) / (1024*1024)
    print(f"EPUB: {size_mb:.0f} MB | Fixed-layout: YES | RTL: YES | Cover: YES")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: fixed-epub-builder.py <images_dir> <output.epub> <title> <author>")
        sys.exit(1)
    build(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
