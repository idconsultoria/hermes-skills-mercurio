#!/usr/bin/env python3
"""Paridade entre o catálogo base (en) e um catálogo traduzido.

Uso: i18n-catalog-parity.py <locales-dir> [lang] [--base en]

Sai com código 1 quando falta chave ou quando os placeholders divergem — os dois defeitos que
só aparecem em produção como linha em inglês ou chave crua. Requer PyYAML (rode com o python do
ambiente onde o agente está instalado).
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - ambiente sem PyYAML
    sys.exit("PyYAML ausente: rode com o python do ambiente do Hermes (venv/bin/python)")

PLACEHOLDER = re.compile(r"{(\w+)")


def flatten(node, prefix=""):
    out = {}
    for key, value in (node or {}).items():
        full = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, full))
        else:
            out[full] = value
    return out


def placeholders(text):
    return set(PLACEHOLDER.findall(str(text)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("locales_dir")
    ap.add_argument("lang", nargs="?", default="pt")
    ap.add_argument("--base", default="en")
    args = ap.parse_args()

    base_path = Path(args.locales_dir) / f"{args.base}.yaml"
    lang_path = Path(args.locales_dir) / f"{args.lang}.yaml"
    for path in (base_path, lang_path):
        if not path.is_file():
            sys.exit(f"catálogo ausente: {path}")

    base = flatten(yaml.safe_load(base_path.read_text()))
    lang = flatten(yaml.safe_load(lang_path.read_text()))

    missing = sorted(set(base) - set(lang))
    extra = sorted(set(lang) - set(base))
    mismatch = [
        (key, sorted(placeholders(base[key])), sorted(placeholders(lang[key])))
        for key in base
        if key in lang and placeholders(base[key]) != placeholders(lang[key])
    ]
    identical = sum(1 for key in base if key in lang and lang[key] == base[key])

    print(f"chaves: {args.base}={len(base)} {args.lang}={len(lang)}")
    print(f"faltando em {args.lang}: {len(missing)}")
    print(f"sobrando em {args.lang}: {len(extra)}")
    print(f"placeholders divergentes: {len(mismatch)}")
    print(f"valores idênticos ao {args.base} (termos que não se traduzem): {identical}")

    for key in missing[:20]:
        print(f"  FALTA  {key}")
    for key, want, got in mismatch[:20]:
        print(f"  PLACEHOLDER  {key}: {args.base}={want} {args.lang}={got}")

    return 1 if (missing or mismatch) else 0


if __name__ == "__main__":
    sys.exit(main())
