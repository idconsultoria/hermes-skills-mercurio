#!/usr/bin/env python3
"""Inspect MOBI files for Kindle manga quality.
Usage: python3 inspect-mobi.py <path-to.mobi>

Checks:
- KCC processing (Kindle Comic Converter metadata)
- Manga mode (RTL reading direction)
- Image resolution distribution
- Page count estimate
- MOBI format validity
"""

import os
import struct
import sys


def inspect_mobi(path):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return False

    size_mb = os.path.getsize(path) / (1024 * 1024)

    with open(path, 'rb') as f:
        data = f.read(65536)  # Read headers + first EXTH records

    print(f"📁 {os.path.basename(path)}")
    print(f"📏 {size_mb:.1f} MB")

    # Check MOBI header
    mobi_start = data.find(b'MOBI')
    if mobi_start < 0:
        print("❌ Not a valid MOBI file (no MOBI header)")
        return False

    mobi_type = struct.unpack('>I', data[mobi_start + 0x4:mobi_start + 0x8])[0]
    print(f"📋 MOBI type: {'Book (2)' if mobi_type == 2 else f'Type {mobi_type}'}")

    # Check EXTH for KCC metadata
    exth_pos = data.find(b'EXTH')
    kcc = data.find(b'KCC') >= 0
    rtl = data.find(b'rtl') >= 0
    kcc_version = ''
    kcc_pos = data.find(b'KindleComicConverter')
    if kcc_pos >= 0:
        end = data.find(b'\x00', kcc_pos)
        kcc_version = data[kcc_pos:end].decode('latin-1', errors='replace')

    print(f"🔧 KCC: {'✅' if kcc else '❌'} {kcc_version}")
    print(f"↔️  Manga Mode (RTL): {'✅' if rtl else '❌'}")

    # Check device profile from EXTH
    res_pos = data.find(b'x1448')  # Paperwhite native height
    if res_pos >= 0:
        # Find the full resolution string
        start = max(0, res_pos - 8)
        end = min(len(data), res_pos + 10)
        chunk = data[start:end]
        for i in range(len(chunk)):
            if chunk[i] >= 48 and chunk[i] <= 57:
                res_end = chunk.find(b'\x00', i)
                resolution = chunk[i:res_end].decode('latin-1', errors='replace') if res_end > i else chunk[i:].decode('latin-1', errors='replace')
                print(f"📐 Device profile: {resolution}")
                break

    # Scan JPEG resolutions in the full file (re-read)
    with open(path, 'rb') as f:
        full_data = f.read()

    jpeg_count = 0
    resolutions = {}
    pos = 0
    while True:
        sofi = full_data.find(b'\xff\xc0', pos)
        if sofi < 0:
            break
        if sofi + 9 < len(full_data):
            h = struct.unpack('>H', full_data[sofi + 5:sofi + 7])[0]
            w = struct.unpack('>H', full_data[sofi + 7:sofi + 9])[0]
            res = f"{w}x{h}"
            resolutions[res] = resolutions.get(res, 0) + 1
            jpeg_count += 1
        pos = sofi + 2

    print(f"🖼️  Pages: {jpeg_count}")

    if resolutions:
        # Show top 3 resolutions
        top = sorted(resolutions.items(), key=lambda x: -x[1])[:3]
        print(f"📊 Top resolutions:")
        for res, count in top:
            pct = count / jpeg_count * 100
            print(f"    {res}: {count} ({pct:.0f}%)")

        # Quality assessment
        majority = max(resolutions, key=resolutions.get)
        w_str, h_str = majority.split('x')
        w, h = int(w_str), int(h_str)

        if w >= 1072 and h >= 1448:
            print(f"✅ Native Paperwhite resolution ({w}x{h})")
        elif w >= 964 and h >= 1448:
            print(f"✅ High resolution ({w}x{h}) — near-native")
        elif w >= 800 and h >= 1200:
            print(f"⚠️  Acceptable ({w}x{h}) — may letterbox")
        else:
            print(f"❌ Low resolution ({w}x{h})")

    print(f"✅ Format: MOBI (native Kindle)")

    # Size check
    if size_mb > 200:
        print(f"⚠️  Over 200 MB — may exceed Kindle per-file limit")
    elif size_mb > 50 and size_mb < 200:
        print(f"✅ Size OK for Kindle transfer")
    elif size_mb < 50:
        print(f"✅ Small enough for Gmail attachment (under 50 MB)")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 inspect-mobi.py <path-to.mobi> [path2.mobi ...]")
        sys.exit(1)

    all_ok = True
    for arg in sys.argv[1:]:
        if not inspect_mobi(arg):
            all_ok = False
        print()

    sys.exit(0 if all_ok else 1)
