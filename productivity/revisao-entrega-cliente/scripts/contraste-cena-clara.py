#!/usr/bin/env python3
"""Mede contraste de texto NO PIXEL com uma cena CLARA simulada atrás do conteúdo.

Por que existe: audit de contraste que compõe o fundo só a partir do DOM (ancestrais)
não enxerga o que está atrás de um canvas/WebGL. Texto sobre cena 3D clara passa no
audit e falha na tela do cliente. Aqui a cena real é substituída por um gradiente
claro fixo (z-index acima do canvas, abaixo do conteúdo) e o contraste é medido nos
pixels do screenshot: por caixa de elemento, percentis 2%/98% de luminância -> razão
WCAG. Percentil largo (5%/95%) dilui glifo fino e inventa falha; 2%/98% aproxima o
traço real.

Limites aplicados: 4,5:1 texto normal · 3:1 texto grande. A classificação de "grande"
é heurística pelo tamanho da CAIXA mediana (h>=48, ou caixa larga e alta) porque a
caixa inclui padding — se a precisão importar, leia `font-size` computado e ajuste.

Uso:
  CDP_DIR=/pasta/com/cdp.py python3 contraste-cena-clara.py \
      --url http://127.0.0.1:8099/index.html --config alvos.json \
      [--width 1440] [--height 900] [--port 9671] \
      [--cena "#A8F5FB,#66E8F1,#4AC6D3,#1A5266"] [--out pasta-de-screenshots]

alvos.json:
  [ {"nome": "cta", "nav": "cta", "selectors": [".s5-eyebrow", ".s5-cta"]},
    {"nome": "relatorio", "selectors": [".s3-title", ".s3-footer .copy"]} ]
  "nav" é opcional: id passado a `window.__app.nav.goTo(id, true)` quando o site expõe
  essa API; sem ele a tela é medida como está (páginas estáticas). Selector ausente é
  ignorado, o que permite medir telas diferentes no mesmo arquivo.

Saída: linha por elemento (OK/FALHA, razão, limite) + resumo das falhas.
Exit code 1 se houver falha — serve de gate em ciclo de polimento.

Pré-requisito: o helper `cdp.py` do harness local (Chromium do playwright + CDP por
websocket) acessível via CDP_DIR; ele expõe Chrome(port,width,height), connect_page(),
device(), goto(url, wait), js(), shot(path) e close().
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from PIL import Image

CENA_PADRAO = ["#A8F5FB", "#66E8F1", "#4AC6D3", "#1A5266"]


def carregar_cdp():
    pasta = os.environ.get("CDP_DIR")
    if pasta:
        sys.path.insert(0, pasta)
    sys.modules.pop("cdp", None)
    import cdp  # noqa: E402  (depende do CDP_DIR acima)

    return cdp


def injetar_cena(cores):
    """Camada clara entre o canvas (z-index baixo) e o conteúdo (z-index alto)."""
    c1, c2, c3, c4 = (cores + CENA_PADRAO)[:4]
    return (
        "(()=>{const antigo=document.getElementById('cena-clara-teste');"
        "if(antigo) antigo.remove();"
        "const l=document.createElement('div');l.id='cena-clara-teste';"
        "l.style.cssText='position:fixed;inset:0;z-index:1;pointer-events:none;background:'"
        f"+ 'radial-gradient(circle at 50% 42%, {c1} 0%, {c2} 34%, {c3} 62%, {c4} 100%)';
"
        "document.body.appendChild(l);return true})()"
    )


def luminancia(v):
    v = v / 255
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def razao(a, b):
    la, lb = luminancia(a), luminancia(b)
    alto, baixo = max(la, lb), min(la, lb)
    return (alto + 0.05) / (baixo + 0.05)


def caixas(c, seletores):
    bruto = c.js(
        "(()=>{const ids=%s;return JSON.stringify(ids.map(s=>{const e=document.querySelector(s);"
        "if(!e) return null;const r=e.getBoundingClientRect();"
        "return [s,Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height),"
        "getComputedStyle(e).fontSize];}).filter(Boolean))})()" % json.dumps(seletores)
    )
    return json.loads(bruto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--config", required=True, help="JSON com [{nome, nav?, selectors[]}]")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--port", type=int, default=9671)
    ap.add_argument("--cena", default=",".join(CENA_PADRAO))
    ap.add_argument("--out", default=".")
    ap.add_argument("--espera", type=float, default=1.7,
                    help="segundos após trocar de tela, antes de medir")
    args = ap.parse_args()

    alvos = json.load(open(args.config))
    cdp = carregar_cdp()
    os.makedirs(args.out, exist_ok=True)

    c = cdp.Chrome(port=args.port, width=args.width, height=args.height)
    try:
        c.connect_page()
        c.device(args.width, args.height)
        c.goto(args.url, wait=9)

        falhas = []
        for alvo in alvos:
            if alvo.get("nav"):
                c.js("window.__app.nav.goTo('%s', true)" % alvo["nav"])
                time.sleep(args.espera)
            c.js(injetar_cena([x.strip() for x in args.cena.split(",")]))
            time.sleep(0.6)
            shot = c.shot(os.path.join(args.out, "cc-%s.png" % alvo.get("nome", "tela")))
            caminho = shot[0] if isinstance(shot, (tuple, list)) else shot
            im = Image.open(caminho).convert("L")

            print("===", alvo.get("nome", "?"), "(cena clara simulada)")
            for nome, x, y, w, h, fonte in caixas(c, alvo.get("selectors", [])):
                if w < 2 or h < 2:
                    continue
                px = sorted(im.crop((max(0, x), max(0, y), max(1, x + w), max(1, y + h))).getdata())
                if not px:
                    continue
                p2 = px[int(len(px) * 0.02)]
                p98 = px[min(len(px) - 1, int(len(px) * 0.98))]
                r = razao(p98, p2)
                grande = float(str(fonte).replace("px", "") or 0) >= 24 or h >= 48
                limite = 3.0 if grande else 4.5
                ok = r >= limite
                if not ok:
                    falhas.append((alvo.get("nome"), nome, round(r, 2), limite))
                print("   %-5s %-24s %5.2f:1  (fonte %s · limite %.1f)"
                      % ("OK" if ok else "FALHA", nome, r, fonte, limite))
            c.js("document.getElementById('cena-clara-teste').remove()")

        print()
        if falhas:
            print("FALHAS:", falhas)
            return 1
        print("Nenhuma falha: todo elemento medido acima do limite, sobre cena clara.")
        return 0
    finally:
        try:
            c.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
