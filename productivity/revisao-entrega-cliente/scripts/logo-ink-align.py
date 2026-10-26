#!/usr/bin/env python3
"""Iguala a ALTURA DE TINTA de marcas lado a lado (capa A4, timbrado, lockup).

Altura de caixa igual nao da altura visual igual: cada arquivo de logo tem padding interno
proprio. Este script mede a fracao de tinta de cada arquivo e devolve a altura de caixa (mm)
necessaria para que todas as tintas meçam o mesmo alvo.

Uso:
    python3 logo-ink-align.py marcaA.png marcaB.svg --alvo 18

Saida por arquivo: fracao de tinta (altura e largura), centro da tinta relativo ao centro da
caixa (compense com `margin` se nao for ~0) e a altura de caixa em mm.

Dependencias: Pillow (PNG). cairosvg so para SVG (se faltar, converta o SVG para PNG antes).
"""
from __future__ import annotations

import argparse
import io
import os
import sys


def _bbox_alpha(img):
    return img.convert("RGBA").split()[-1].getbbox()


def _bbox_vs_branco(img, tol=24):
    """Fallback para PNG sem alfa: tinta = pixel que nao e branco/quase branco."""
    rgb = img.convert("RGB")
    w, h = rgb.size
    if max(w, h) > 1200:  # varredura por pixel fica caro; reduz proporcionalmente
        f = 1200 / max(w, h)
        rgb = rgb.resize((max(1, int(w * f)), max(1, int(h * f))))
        w, h = rgb.size
    px = rgb.load()
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - 255) + abs(g - 255) + abs(b - 255) > tol:
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y
    if maxx < 0:
        return None
    return (minx, miny, maxx + 1, maxy + 1)


def measure_png(path):
    from PIL import Image

    img = Image.open(path)
    box = _bbox_alpha(img)
    if box is None or box == (0, 0) + img.size:
        box = _bbox_vs_branco(img)
    return img.size, box


def measure_svg(path):
    try:
        import cairosvg
    except ImportError:
        sys.exit(
            "cairosvg ausente para %s. Converta o SVG para PNG "
            "(rsvg-convert, inkscape ou Chromium) e passe o PNG." % path
        )
    from PIL import Image

    data = cairosvg.svg2png(url=path, output_width=1600)
    img = Image.open(io.BytesIO(data))
    box = _bbox_alpha(img) or _bbox_vs_branco(img)
    return img.size, box


def report(path, alvo_mm):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        size, box = measure_svg(path)
    elif ext in (".png", ".webp", ".jpg", ".jpeg"):
        size, box = measure_png(path)
    else:
        sys.exit("formato nao suportado: %s" % path)

    if box is None:
        sys.exit("nao consegui localizar tinta em %s (arquivo vazio?)" % path)

    w, h = size
    x0, y0, x1, y1 = box
    ink_h = (y1 - y0) / h
    ink_w = (x1 - x0) / w
    cx = (x0 + x1) / 2 / w - 0.5
    cy = (y0 + y1) / 2 / h - 0.5

    box_mm = alvo_mm / ink_h if ink_h else float("nan")
    largura_mm = box_mm * (w / h)

    print("\n%s" % path)
    print("  canvas %dx%d px" % (w, h))
    print("  tinta  altura %.1f%%  largura %.1f%%" % (ink_h * 100, ink_w * 100))
    print("  centro da tinta deslocado: x %+.1f%%  y %+.1f%% da caixa" % (cx * 100, cy * 100))
    print("  -> caixa para %.1f mm de tinta: height %.1fmm  (largura ~%.1fmm)" % (alvo_mm, box_mm, largura_mm))
    if abs(cy) > 0.01:
        print(
            "     tinta fora do centro vertical: compense com margin %+.1fmm"
            % (-cy * box_mm)
        )
    return box_mm, largura_mm


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivos", nargs="+", help="PNG/SVG das marcas, na ordem em que aparecem")
    ap.add_argument("--alvo", type=float, default=18.0, help="altura de tinta desejada em mm (padrao 18)")
    ap.add_argument("--largura-util", type=float, default=172.0, help="largura util da pagina em mm (padrao 172 = A4 com 19mm de margem)")
    ap.add_argument("--gap", type=float, default=9.0, help="espaco entre marcas em mm (padrao 9)")
    args = ap.parse_args()

    total = 0.0
    for p in args.arquivos:
        _, larg = report(p, args.alvo)
        total += larg
    total += args.gap * (len(args.arquivos) - 1)

    print("\nlargura total estimada: %.1f mm de %.1f mm uteis" % (total, args.largura_util))
    if total > args.largura_util:
        print("ATENCAO: nao cabe em uma linha; reduza --alvo ou empilhe as marcas")
    else:
        print("cabe; sobra %.1f mm" % (args.largura_util - total))


if __name__ == "__main__":
    main()
