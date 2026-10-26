#!/usr/bin/env python3
"""Lista faixas de tinta e vãos em branco de um print, para escolher uma linha
de corte limpa (fronteira de card/bloco) sem cortar texto ao meio.

Uso:
    python3 faixas_de_tinta.py print.png
    python3 faixas_de_tinta.py print.png --de 300 --ate 1800 --limiar 200
    python3 faixas_de_tinta.py print.png --zoom-base 120 --saida-zoom /tmp/base.png

Saída: faixas (início,fim) de linhas com tinta e os vãos entre elas. Corte
dentro de um vão.
"""
import argparse
import sys


def carrega(caminho):
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        sys.exit("precisa de Pillow e numpy")
    im = Image.open(caminho).convert("L")
    return np.asarray(im).astype(float), im


def faixas(a, limiar, y0, y1, vao_min):
    linhas = (a[y0:y1] < limiar).sum(axis=1)
    ys = [y0 + i for i, v in enumerate(linhas) if v > 0]
    if not ys:
        return [], []
    grupos = []
    ini = prev = ys[0]
    for y in ys[1:]:
        if y - prev > 4:
            grupos.append((ini, prev))
            ini = y
        prev = y
    grupos.append((ini, prev))
    vaos = [(grupos[i][1], grupos[i + 1][0]) for i in range(len(grupos) - 1)
            if grupos[i + 1][0] - grupos[i][1] >= vao_min]
    return grupos, vaos


def main():
    p = argparse.ArgumentParser()
    p.add_argument("imagem")
    p.add_argument("--de", type=int, default=0)
    p.add_argument("--ate", type=int, default=None)
    p.add_argument("--limiar", type=int, default=200,
                   help="abaixo disso é tinta (default 200; use 235 para ver sombras)")
    p.add_argument("--vao-min", type=int, default=8)
    p.add_argument("--zoom-base", type=int, default=0,
                   help="salva um zoom 3x da faixa final, para conferir o corte")
    p.add_argument("--saida-zoom", default="/tmp/base.png")
    a = p.parse_args()

    arr, im = carrega(a.imagem)
    h, w = arr.shape
    y1 = a.ate if a.ate is not None else h
    grupos, vaos = faixas(arr, a.limiar, a.de, y1, a.vao_min)

    print(f"{a.imagem}: {w}x{h} px · janela {a.de}..{y1} · limiar {a.limiar}")
    print("faixas com tinta:")
    for g in grupos:
        print(f"  {g[0]:5d} .. {g[1]:5d}  ({g[1] - g[0] + 1} px)")
    print("vãos para corte:")
    for v in vaos:
        print(f"  {v[0]:5d} .. {v[1]:5d}  ({v[1] - v[0]} px)")
    if grupos:
        print(f"última tinta em {grupos[-1][1]} px — corte seguro a partir de {grupos[-1][1] + 2}")

    if a.zoom_base:
        from PIL import Image
        topo = max(0, h - a.zoom_base)
        im.crop((0, topo, w, h)).resize((w, a.zoom_base * 3)).save(a.saida_zoom)
        print(f"zoom da base salvo em {a.saida_zoom}")


if __name__ == "__main__":
    main()
