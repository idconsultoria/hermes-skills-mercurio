#!/usr/bin/env python3
"""generate_logo_variants.py — recorte + recolor + export de variantes de marca.

Entrada: 1 PNG principal (tipicamente fundo preto / opaco).
Saída (em --out):
  <base>-principal.png                 crop do original (com fundo)
  <base>-principal-transparente.png
  <base>-positivo-transparente.png     recolorido p/ fundo claro
  <base>-positivo-<bg>.png             recolorido composto (bg: cream/offwhite)
  <base>-negativo-charcoal.png         sobre charcoal
  <base>-simbolo-transparente.png      só o ícone
  <base>-simbolo-<bg>.png              símbolo sobre fundo
  <base>-mono-branco-transparente.png / -mono-branco-charcoal.png
  <base>-mono-charcoal-transparente.png / -mono-charcoal-offwhite.png
  manifest.json

Uso:
  python3 generate_logo_variants.py --src logo.png --out outdir
  python3 generate_logo_variants.py --src logo.png --out outdir --palette pal.json --split 0.55

pal.json (opcional, exemplo BiotechSe):
  {"icon_white":[2,145,144], "text_white":[45,45,45], "green":[0,255,163],
   "cream":[247,234,223], "offwhite":[242,241,240], "charcoal":[45,45,45]}
"""
import argparse, json, os, sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("ERRO: Pillow ausente (pip install pillow).")

DEFAULT_PALETTE = {
    "icon_white": [2, 145, 144], "text_white": [45, 45, 45], "green": [0, 255, 163],
    "cream": [247, 234, 223], "offwhite": [242, 241, 240], "charcoal": [45, 45, 45],
}


def is_white(r, g, b, tol=60):
    return r > 180 and g > 180 and b > 180 and abs(r - g) < tol and abs(g - b) < tol


def is_green(r, g, b):
    return g > 150 and r < 90 and b < 130


def bbox_nonbg(im, thr=20):
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y][:3]
            if r > thr or g > thr or b > thr:
                found = True
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y
    if not found:
        return (0, 0, w - 1, h - 1)
    return (minx, miny, maxx, maxy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--palette", default=None)
    ap.add_argument("--split", type=float, default=0.55, help="fração da altura que é ícone")
    ap.add_argument("--thr", type=int, default=20)
    ap.add_argument("--pad", type=int, default=40)
    a = ap.parse_args()
    pal = DEFAULT_PALETTE.copy()
    if a.palette and os.path.exists(a.palette):
        pal.update(json.load(open(a.palette)))
    src = Image.open(a.src).convert("RGB")
    w, h = src.size
    os.makedirs(a.out, exist_ok=True)
    base = Path(a.src).stem

    # 1 crop
    minx, miny, maxx, maxy = bbox_nonbg(src, a.thr)
    p = a.pad
    minx = max(0, minx - p)
    miny = max(0, miny - p)
    maxx = min(w - 1, maxx + p)
    maxy = min(h - 1, maxy + p)
    crop = src.crop((minx, miny, maxx + 1, maxy + 1))
    crop.save(os.path.join(a.out, f"{base}-principal.png"))

    # 2 transparent
    rgba = crop.convert("RGBA")
    d = rgba.getdata()
    nd = []
    for r, g, b, al in d:
        if r < a.thr and g < a.thr and b < a.thr:
            nd.append((0, 0, 0, 0))
        else:
            nd.append((r, g, b, 255))
    rgba.putdata(nd)
    rgba.save(os.path.join(a.out, f"{base}-principal-transparente.png"))

    # 3 recolor positivo
    cw, ch = rgba.size
    split_y = int(ch * a.split)
    rec = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            r, g, b, al = rgba.getpixel((x, y))
            if al == 0:
                continue
            if is_white(r, g, b):
                tgt = pal["icon_white"] if y < split_y else pal["text_white"]
            elif is_green(r, g, b):
                tgt = pal["green"]
            else:
                tgt = (r, g, b)
            rec.putpixel((x, y), tuple(tgt) + (255,))
    rec.save(os.path.join(a.out, f"{base}-positivo-transparente.png"))
    for bgname, bgc in [("cream", pal["cream"]), ("offwhite", pal["offwhite"])]:
        bg = Image.new("RGBA", (cw, ch), tuple(bgc) + (255,))
        Image.alpha_composite(bg, rec).convert("RGB").save(os.path.join(a.out, f"{base}-positivo-{bgname}.png"))

    # negativo
    bgc = pal["charcoal"]
    bg = Image.new("RGBA", (cw, ch), tuple(bgc) + (255,))
    Image.alpha_composite(bg, rgba).convert("RGB").save(os.path.join(a.out, f"{base}-negativo-charcoal.png"))

    # simbolo
    icon_h = int(ch * 0.58)
    sym = rgba.crop((0, 0, cw, icon_h))
    bb = sym.getbbox()
    if bb:
        st = sym.crop(bb)
        pp = 20
        spad = Image.new("RGBA", (st.size[0] + pp * 2, st.size[1] + pp * 2), (0, 0, 0, 0))
        spad.paste(st, (pp, pp))
        spad.save(os.path.join(a.out, f"{base}-simbolo-transparente.png"))
        for bgname, bgc2 in [("negativo", pal["charcoal"]), ("positivo", pal["offwhite"])]:
            bg = Image.new("RGBA", spad.size, tuple(bgc2) + (255,))
            Image.alpha_composite(bg, spad).convert("RGB").save(os.path.join(a.out, f"{base}-simbolo-{bgname}.png"))

    # mono
    mono_w = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    mono_c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            r, g, b, al = rgba.getpixel((x, y))
            if al > 0:
                mono_w.putpixel((x, y), (255, 255, 255, 255))
                mono_c.putpixel((x, y), tuple(pal["charcoal"]) + (255,))
    mono_w.save(os.path.join(a.out, f"{base}-mono-branco-transparente.png"))
    mono_c.save(os.path.join(a.out, f"{base}-mono-charcoal-transparente.png"))
    Image.alpha_composite(Image.new("RGBA", (cw, ch), tuple(pal["charcoal"]) + (255,)), mono_w).convert("RGB").save(os.path.join(a.out, f"{base}-mono-branco-charcoal.png"))
    Image.alpha_composite(Image.new("RGBA", (cw, ch), tuple(pal["offwhite"]) + (255,)), mono_c).convert("RGB").save(os.path.join(a.out, f"{base}-mono-charcoal-offwhite.png"))

    manifest = {"source": a.src, "variants": sorted(os.listdir(a.out)), "palette": pal}
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"), indent=2)
    print(f"OK {len(manifest['variants'])} arquivos em {a.out}")


if __name__ == "__main__":
    main()
