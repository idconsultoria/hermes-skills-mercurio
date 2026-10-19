#!/usr/bin/env python3
"""Mede o ORÇAMENTO VERTICAL de cada tela em várias resoluções 16:9.

Por que existe: tela que "cabe" (scrollHeight == innerHeight) pode estar sufocada —
título de 4-5 linhas ocupando 41% da altura, todos os blocos empilhados de ponta a
ponta, respiro zero. Isso passa em qualquer checagem de overflow e ainda assim é
reprovado pelo cliente. Aqui se mede, por tela e por resolução:

  * overflow real            -> scrollHeight da tela > innerHeight          (reprova)
  * fatia do bloco de conteúdo -> altura do bloco / altura da viewport       (alvo <= 0,60)
  * respiro topo/base         -> (innerHeight - bloco) / 2 / innerHeight     (alvo >= 0,15)
  * linhas do título          -> altura do título / lineHeight computado     (conte, não olhe)
  * ritmo vertical            -> gaps entre os blocos listados               (constância)

Uso:
  CDP_DIR=/pasta/com/cdp.py python3 orcamento-vertical-tela.py \
      --url http://127.0.0.1:8099/index.html --config telas.json \
      [--resolucoes 1280x720,1366x768,1440x900,1920x1080] [--out pasta-de-screenshots]

telas.json:
  [ {"nome": "cta", "nav": "cta", "bloco": ".s5-inner", "titulo": ".s5-headline",
     "elementos": [".s5-eyebrow", ".s5-headline", ".s5-sub", ".s5-cta", ".s5-links", ".s5-contact"]},
    {"nome": "relatorio", "nav": "relatorio", "bloco": ".s3-grid", "titulo": ".s3-title"} ]
  "nav" é opcional (id de `window.__app.nav.goTo(id, true)`); sem ele a tela é medida como está.
  "titulo"/"elementos" são opcionais; o container da tela é detectado pelo seletor `#screen-<nav>`
  ou `#screen-<nome>`, com fallback para `body`.

Saída: uma linha por resolução e tela, com a marca de cada critério; resumo das reprovações.
Exit code 1 se houver reprovação — serve de gate no ciclo de polimento.

Pré-requisito: o helper `cdp.py` do harness local (Chromium do playwright + CDP por
websocket) acessível via CDP_DIR; expõe Chrome(port,width,height), connect_page(), device(),
goto(url, wait), js(), shot(path) e close().
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

LIMITE_FATIA = 0.60
MIN_RESPIRO = 0.15
RAZAO_RITMO = 2.5  # maior gap / menor gap tolerado entre blocos consecutivos


MEDIDA = """(()=>{
  const sel = %s;
  const raiz = document.querySelector(sel.tela) || document.body;
  const out = {tela: sel.tela, vh: innerHeight, vw: innerWidth,
               scrollTela: raiz.scrollHeight, bloco: null, titulo: null, elementos: []};
  if (sel.bloco) {
    const b = document.querySelector(sel.bloco);
    if (b) { const r = b.getBoundingClientRect();
      out.bloco = {top: Math.round(r.top), bottom: Math.round(r.bottom),
                   h: Math.round(r.height), share: +(r.height / innerHeight).toFixed(3)}; }
  }
  if (sel.titulo) {
    const t = document.querySelector(sel.titulo);
    if (t) { const r = t.getBoundingClientRect(); const lh = parseFloat(getComputedStyle(t).lineHeight) || 1;
      out.titulo = {h: Math.round(r.height), fonte: getComputedStyle(t).fontSize,
                    linhas: Math.round(r.height / lh)}; }
  }
  out.elementos = (sel.elementos || []).map(s => {
    const e = document.querySelector(s); if (!e) return null;
    const r = e.getBoundingClientRect();
    return {sel: s, top: Math.round(r.top), bottom: Math.round(r.bottom), h: Math.round(r.height)};
  }).filter(Boolean);
  return JSON.stringify(out);
})()"""


ROCK = None


def carregar_cdp():
    pasta = os.environ.get("CDP_DIR")
    if pasta:
        sys.path.insert(0, pasta)
    sys.modules.pop("cdp", None)
    import cdp  # noqa: E402

    return cdp


def executar(url, alvos, resolucoes, out, espera):
    cdp = carregar_cdp()
    os.makedirs(out, exist_ok=True)
    reprovacoes = []
    for w, h in resolucoes:
        c = cdp.Chrome(port=9000 + (w + h) % 900, width=w, height=h)
        try:
            c.connect_page()
            c.device(w, h)
            c.goto(url, wait=9)
            print("=" * 72)
            print("RESOLUCAO %dx%d" % (w, h))
            for alvo in alvos:
                nome = alvo.get("nome", "tela")
                if alvo.get("nav"):
                    c.js("window.__app.nav.goTo('%s', true)" % alvo["nav"])
                    time.sleep(espera)
                sel = {
                    "tela": "#screen-%s" % (alvo.get("nav") or nome),
                    "bloco": alvo.get("bloco"),
                    "titulo": alvo.get("titulo"),
                    "elementos": alvo.get("elementos", []),
                }
                dado = json.loads(c.js(MEDIDA % json.dumps(sel)))
                shot = c.shot(os.path.join(out, "ov-%s-%dx%d.png" % (nome, w, h)))
                caminho = shot[0] if isinstance(shot, (tuple, list)) else shot

                overflow = dado["scrollTela"] > dado["vh"] + 1
                bloco = dado.get("bloco") or {}
                share = bloco.get("share")
                respiro = None
                if bloco:
                    respiro = round(min(bloco["top"], dado["vh"] - bloco["bottom"]) / dado["vh"], 3)

                marca_overflow = "OK" if not overflow else "REPROVA"
                marca_fatia = "OK" if (share is None or share <= LIMITE_FATIA) else "REPROVA"
                marca_respiro = "OK" if (respiro is None or respiro >= MIN_RESPIRO) else "ATENCAO"

                print("  %-14s overflow=%s (%d/%d) · fatia bloco=%s · respiro=%s · titulo=%s linhas (%s)"
                      % (nome, marca_overflow, dado["scrollTela"], dado["vh"],
                         "-" if share is None else "%s %.2f" % (marca_fatia, share),
                         "-" if respiro is None else "%s %.2f" % (marca_respiro, respiro),
                         (dado.get("titulo") or {}).get("linhas", "-"),
                         (dado.get("titulo") or {}).get("fonte", "-")))

                if overflow or (share is not None and share > LIMITE_FATIA) \
                        or (respiro is not None and respiro < MIN_RESPIRO):
                    reprovacoes.append((str(w) + "x" + str(h), nome, "overflow" if overflow
                                        else ("fatia %.2f" % share if share is not None
                                              else "respiro %.2f" % respiro)))

                els = dado.get("elementos") or []
                gaps = [els[i + 1]["top"] - els[i]["bottom"] for i in range(len(els) - 1)]
                if gaps and min(gaps) > 0 and max(gaps) / min(gaps) > RAZAO_RITMO:
                    print("     ritmo irregular (gaps %s) - uniformize o gap entre blocos" % gaps)
                    reprovacoes.append((str(w) + "x" + str(h), nome, "ritmo %s" % gaps))
                elif gaps:
                    print("     ritmo %s" % gaps)
                print("     screenshot: %s" % caminho)
        finally:
            try:
                c.close()
            except Exception:
                pass
    print()
    if reprovacoes:
        print("REPROVACOES:")
        for r in reprovacoes:
            print("  %s %s -> %s" % r)
        return 1
    print("Todas as telas dentro do orcamento vertical nas resolucoes medidas.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--config", required=True, help="JSON com [{nome, nav?, bloco?, titulo?, elementos[]}]")
    ap.add_argument("--resolucoes", default="1280x720,1366x768,1440x900,1920x1080")
    ap.add_argument("--out", default=".")
    ap.add_argument("--espera", type=float, default=1.7)
    args = ap.parse_args()

    alvos = json.load(open(args.config))
    resolucoes = []
    for par in args.resolucoes.split(","):
        w, h = par.strip().lower().split("x")
        resolucoes.append((int(w), int(h)))
    return executar(args.url, alvos, resolucoes, args.out, args.espera)


if __name__ == "__main__":
    sys.exit(main())
