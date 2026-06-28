#!/usr/bin/env python3
"""
epub-builder.py — Create a Kindle-compatible image-based EPUB from JPEG files.

Input:  a directory of JPEG files named 0001.jpg, 0002.jpg, ... (or any sorted order)
Output: an .epub file with RTL manga metadata, grayscale conversion, contrast check,
        and device-specific resize.

Typical usage:

    # Just package existing JPEGs into EPUB (fastest)
    python3 epub-builder.py /tmp/mypages/ --title "My Manga" --author "Author" --output out.epub

    # Convert source images, apply grayscale + contrast + resize, then package
    python3 epub-builder.py /tmp/raw_jpgs/ --grayscale --contrast --resize 1236x1648 \\
        --title "The Gods Lie" --author=*** Arakawa" --output The_Gods_Lie.epub

    # CBR source (extract first, then package):
    # from unrar.cffi.rarfile import RarFile; [extract to /tmp/pages/]
    python3 epub-builder.py /tmp/pages/ --title "Manga" --author "Author" --output m.epub

The --grayscale flag converts to 'L' mode. --contrast applies ImageOps.autocontrast
if dark pixels are <5% of histogram. --resize thumbnails to the given dimensions.

If neither --grayscale nor --resize is specified, images are embedded as-is (fast).
--rtl is always on for manga — omit only for left-to-right books.
"""

import os
import sys
import argparse
from zipfile import ZipFile, ZIP_STORED


def build_epub(image_dir, output_path, title="Manga", author="Unknown",
               do_grayscale=False, do_contrast=False, resize=None, rtl=True):
    from PIL import Image, ImageOps
    import io

    exts = {'.jpg', '.jpeg', '.png', '.jp2', '.gif', '.webp'}
    files = sorted([
        f for f in os.listdir(image_dir)
        if os.path.splitext(f)[1].lower() in exts
    ])

    if not files:
        print("Error: No image files found in", image_dir)
        sys.exit(1)

    print("Building EPUB: {} pages".format(len(files)))

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

        manifest = []
        spine = []
        contrast_applied = False
        final_dims = None

        for i, fname in enumerate(files):
            mid = 'img{:04d}'.format(i)
            src = os.path.join(image_dir, fname)
            img = Image.open(src)

            if do_grayscale or do_contrast or resize:
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                gray = img.convert('L') if do_grayscale else img

                if do_contrast:
                    h = gray.histogram()
                    total = sum(h)
                    dark_pct = sum(h[:64]) / total * 100 if total > 0 else 0
                    if dark_pct < 5:
                        gray = ImageOps.autocontrast(gray, cutoff=1)
                        contrast_applied = True

                if resize:
                    gray.thumbnail(resize, Image.LANCZOS)

                buf = io.BytesIO()
                gray.save(buf, 'JPEG', quality=85, optimize=True)
                img_data = buf.getvalue()
                store_name = 'OEBPS/Images/{}.jpg'.format(mid)
                img_type = 'image/jpeg'
                if final_dims is None:
                    final_dims = gray.size
            else:
                with open(src, 'rb') as f:
                    img_data = f.read()
                ext = os.path.splitext(fname)[1].lower()
                store_name = 'OEBPS/Images/' + fname
                mime_map = {
                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.jp2': 'image/jp2',
                    '.gif': 'image/gif', '.webp': 'image/webp',
                }
                img_type = mime_map.get(ext, 'image/jpeg')
                if final_dims is None:
                    final_dims = img.size

            zf.writestr(store_name, img_data)
            manifest.append(
                '<item id="{}" href="{}" media-type="{}"/>'.format(
                    mid, store_name.split('/')[-1], img_type))
            spine.append('<itemref idref="{}"/>'.format(mid))

        dir_attr = ' page-progression-direction="rtl"' if rtl else ''
        opf = (
            '<?xml version="1.0"?>\n'
            '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" '
            'unique-identifier="bookid">\n'
            '  <metadata>\n'
            '    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">'
            + title + '</dc:title>\n'
            '    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">'
            + author + '</dc:creator>\n'
            '    <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">'
            'en</dc:language>\n'
            '  </metadata>\n'
            '  <manifest>\n    ' + '\n    '.join(manifest) + '\n'
            '  </manifest>\n'
            '  <spine toc="ncx"' + dir_attr + '>\n    '
            + '\n    '.join(spine) + '\n'
            '  </spine>\n'
            '</package>'
        )
        zf.writestr('OEBPS/content.opf', opf)

    mb = os.path.getsize(output_path) / (1024 * 1024)
    print("EPUB:", output_path)
    print("Size: {:.0f} MB".format(mb))
    print("Pages:", len(files))
    if final_dims:
        print("Dimensions: {}x{}".format(final_dims[0], final_dims[1]))
    print("RTL:", 'yes' if rtl else 'no')
    if contrast_applied:
        print("Contrast: autocontrast applied (source was washed out)")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Build a Kindle-compatible manga EPUB from images.')
    parser.add_argument('image_dir', help='Directory containing image files')
    parser.add_argument('--output', '-o', default=None,
                        help='Output EPUB path (default: ./output.epub)')
    parser.add_argument('--title', '-t', default='Manga',
                        help='Book title metadata')
    parser.add_argument('--author', '-a', default='Unknown',
                        help='Book author metadata')
    parser.add_argument('--grayscale', '-g', action='store_true',
                        help='Convert images to grayscale')
    parser.add_argument('--contrast', '-c', action='store_true',
                        help='Apply autocontrast fix if histogram is washed out')
    parser.add_argument('--resize', '-r', default=None,
                        help='Resize to WxH, e.g. 1236x1648')
    parser.add_argument('--ltr', action='store_true',
                        help='Left-to-right (default is RTL for manga)')

    args = parser.parse_args()

    if not os.path.isdir(args.image_dir):
        print("Error:", args.image_dir, "is not a directory")
        sys.exit(1)

    output = args.output or 'output.epub'

    resize_tuple = None
    if args.resize:
        try:
            parts = args.resize.lower().split('x')
            resize_tuple = (int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            print("Error: Invalid resize format. Use WxH, e.g. 1236x1648")
            sys.exit(1)

    build_epub(
        args.image_dir, output,
        title=args.title, author=args.author,
        do_grayscale=args.grayscale,
        do_contrast=args.contrast,
        resize=resize_tuple,
        rtl=not args.ltr,
    )
