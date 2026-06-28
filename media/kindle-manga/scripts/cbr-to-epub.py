#!/usr/bin/env python3
"""
Convert CBR (Comic Book RAR) to EPUB for Kindle.

Usage:
    python3 cbr-to-epub.py path/to/file.cbr

Tries extraction backends in order:
  1. unrar.cffi.rarfile (compiled CFFI, no system tool needed)
  2. rarfile (requires system 'unrar' binary)

Output:
    Creates file.epub in the same directory as the input.
"""

import os
import sys
from zipfile import ZipFile, ZIP_STORED


def extract_images(cbr_path):
    """Extract image filenames and data from CBR archive.
    Returns list of (filename, bytes) tuples, or None on failure."""
    images = None

    # Try 1: unrar.cffi.rarfile (no system binary needed)
    try:
        from unrar.cffi.rarfile import RarFile as CffiRarFile
        rf = CffiRarFile(cbr_path)
        all_names = rf.namelist()
        image_names = sorted(n for n in all_names
                             if n.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')))
        if image_names:
            images = []
            for name in image_names:
                data = rf.read(name)
                images.append((name, data))
            print(f"  Extracted via unrar.cffi: {len(images)} images")
        rf.close()
        return images
    except ImportError:
        pass
    except Exception as e:
        print(f"  unrar.cffi failed ({e}), trying rarfile...")

    # Try 2: rarfile (needs system unrar binary)
    try:
        import rarfile
        try:
            rarfile.tool_setup()
        except rarfile.RarCannotExec:
            print("  unrar binary not found via rarfile")
            return None

        rf = rarfile.RarFile(cbr_path)
        all_names = rf.namelist()
        image_names = sorted(n for n in all_names
                             if n.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')))
        if image_names:
            images = []
            for name in image_names:
                rf2 = rarfile.RarFile(cbr_path)
                try:
                    data = rf2.read(name)
                finally:
                    rf2.close()
                images.append((name, data))
            print(f"  Extracted via rarfile: {len(images)} images")
        rf.close()
        return images
    except ImportError:
        pass
    except Exception as e:
        print(f"  rarfile failed: {e}")

    return None


def create_epub(images, title, epub_path):
    """Create a simple image-based EPUB."""
    with ZipFile(epub_path, 'w', ZIP_STORED) as epub:
        epub.writestr('mimetype', 'application/epub+zip', compress_type=ZIP_STORED)

        epub.writestr('META-INF/container.xml', (
            '<?xml version="1.0"?>'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles>'
            '</container>'
        ))

        manifest = ''
        spine = ''
        for i, (name, data) in enumerate(images):
            mid = f'i{i}'
            ext = os.path.splitext(name)[1].lower()
            mt = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png'
            manifest += f'<item id="{mid}" href="{name}" media-type="{mt}"/>\n'
            spine += f'<itemref idref="{mid}"/>\n'
            epub.writestr(f'OEBPS/{name}', data)
            if i % 50 == 0 and i > 0:
                print(f"  {i}/{len(images)}")

        opf = (
            '<?xml version="1.0"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" '
            'unique-identifier="bookid">'
            '<metadata>'
            f'<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{title}</dc:title>'
            '<dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>'
            '</metadata>'
            f'<manifest>{manifest}</manifest>'
            f'<spine>{spine}</spine>'
            '</package>'
        )
        epub.writestr('OEBPS/content.opf', opf)


def convert_cbr_to_epub(cbr_path):
    if not os.path.exists(cbr_path):
        print(f"  File not found: {cbr_path}")
        return False

    base = os.path.splitext(cbr_path)[0]
    epub_path = base + ".epub"

    print(f"Processing: {cbr_path}")
    images = extract_images(cbr_path)

    if not images:
        print("  No images extracted. Install unrar via:")
        print("    uv pip install unrar-cffi  (pure Python, no system deps)")
        print("    OR apt install unrar && uv pip install rarfile")
        return False

    create_epub(images, os.path.basename(base), epub_path)

    size_mb = os.path.getsize(epub_path) / (1024 * 1024)
    print(f"  EPUB created: {epub_path} ({size_mb:.1f} MB)")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 cbr-to-epub.py <file.cbr> [file2.cbr ...]")
        sys.exit(1)

    all_ok = True
    for arg in sys.argv[1:]:
        if not convert_cbr_to_epub(arg):
            all_ok = False
        print()

    sys.exit(0 if all_ok else 1)
