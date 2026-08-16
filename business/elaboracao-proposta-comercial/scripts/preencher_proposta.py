#!/usr/bin/env python3
"""Preenche os placeholders {{NOME}} do modelo de proposta com valores do cliente.

Uso:
    python preencher_proposta.py \
      --template templates/modelo_proposta.html \
      --valores /path/valores.json \
      --out /path/Proposta_<cliente>.html

valores.json: {"CLIENTE_NOME": "Construtora X", "TITULO_PROPOSTA": "...", ...}

O mapa completo dos placeholders está em references/placeholders.md.
Ao final, valida que NENHUM placeholder restou no HTML.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", required=True, help="Caminho do modelo HTML")
    ap.add_argument("--valores", required=True, help="JSON com placeholder -> valor")
    ap.add_argument("--out", required=True, help="Caminho de saída do HTML preenchido")
    args = ap.parse_args()

    template = Path(args.template)
    if not template.exists():
        print(f"ERRO: template não encontrado: {template}", file=sys.stderr)
        return 1

    valores = json.loads(Path(args.valores).read_text(encoding="utf-8"))
    html = template.read_text(encoding="utf-8")

    # substitui cada placeholder conhecido
    usados = set()
    def _sub(m):
        key = m.group(1)
        if key in valores:
            usados.add(key)
            return valores[key]
        return m.group(0)  # mantém intacto se não houver valor

    html = PLACEHOLDER_RE.sub(_sub, html)

    # placeholders não usados no JSON
    restantes = sorted(set(PLACEHOLDER_RE.findall(html)))
    nao_conhecidos = sorted(set(PLACEHOLDER_RE.findall(html)) - set(valores.keys()))
    nao_usados = sorted(set(valores.keys()) - usados)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(html, encoding="utf-8")

    print(f"OK: {args.out} ({len(html)} chars)")
    if restantes:
        print(f"  ⚠ placeholders restantes no HTML: {restantes}")
        print("  Confira o mapa em references/placeholders.md e o JSON de valores.")
    if nao_usados:
        print(f"  ℹ valores do JSON não usados no template: {nao_usados}")
    if restantes:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
