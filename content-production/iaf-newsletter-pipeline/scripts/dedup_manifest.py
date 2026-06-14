#!/usr/bin/env python3
"""
dedup_manifest.py — Extrai títulos dos HTMLs da IAF e mantém
manifesto rolante de 14 dias para dedup eficiente em termos de tokens.

Uso:
    python3 dedup_manifest.py

Lê:  /opt/data/cron/history/iaf_YYYY-MM-DD.html (últimos 14 dias)
Escreve: /opt/data/cron/history/iaf_manifest.json (~6KB)

O JSON resultante substitui a leitura de 14 HTMLs (~560KB) por
um único arquivo compacto. O agente lê só o manifest.

Design: determinístico, idempotente, zero dependências externas.
"""

import json
import glob
import os
import re
import sys
from datetime import datetime, timedelta


# ─── CONFIG ───────────────────────────────────────────────────
HISTORY_DIR = "/opt/data/cron/history"
MAX_DAYS = 14
# ───────────────────────────────────────────────────────────────


def clean(text: str) -> str:
    """Remove tags HTML, entidades, e normaliza whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&mdash;", "—")
    text = text.replace("&ndash;", "–")
    text = text.replace("&aacute;", "á")
    text = text.replace("&eacute;", "é")
    text = text.replace("&iacute;", "í")
    text = text.replace("&oacute;", "ó")
    text = text.replace("&uacute;", "ú")
    text = text.replace("&atilde;", "ã")
    text = text.replace("&otilde;", "õ")
    text = text.replace("&ccedil;", "ç")
    text = text.replace("&ocirc;", "ô")
    text = text.replace("&ecirc;", "ê")
    text = text.replace("&acirc;", "â")
    text = text.replace("&nbsp;", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Decode remaining &#NNNN; entities
    text = re.sub(
        r"&#(\d+);",
        lambda m: chr(int(m.group(1))),
        text,
    )
    return text


def extract_titles(html: str) -> list[str]:
    """
    Extrai títulos de notícias do HTML da IAF — Manhã Aumentada.

    Estratégia: busca padrões específicos do template v3.
    Ordem no HTML = ordem de aparição no documento, que reflete
    a seção (Editorial → Análise → Radar → Comunidade → Prática).
    """
    titles = []
    seen = set()

    def add(title: str):
        t = clean(title)
        if t and len(t) > 10 and t.lower() not in seen:
            seen.add(t.lower())
            titles.append(t)

    # 1. Deep-dive cards: <h3 class="deep-dive-title">...</h3>
    for m in re.finditer(
        r'<h3\s+class="deep-dive-title">(.*?)</h3>', html, re.DOTALL
    ):
        add(m.group(1))

    # 2. News grid items: <strong>...</strong> seguido por tag badge
    for m in re.finditer(
        r'<strong>(.*?)</strong>\s*[—–-]?\s*(?:<[^>]+>)*?\s*<span\s+class="news-tag',
        html,
        re.DOTALL,
    ):
        add(m.group(1))

    # 3. Community pulse: <strong>XXX:</strong> "TÍTULO..." — descrição
    for m in re.finditer(
        r'<strong>[A-Za-z0-9/]+:</strong>\s*["""](.*?)["""]\s*[—–-]',
        html,
        re.DOTALL,
    ):
        add(m.group(1))

    # 4. App card: <h3 class="app-title">...</h3>
    for m in re.finditer(
        r'<h3\s+class="app-title">(.*?)</h3>', html, re.DOTALL
    ):
        add(m.group(1))

    return titles


def extract_edition_date(path: str) -> str | None:
    """Extrai data YYYY-MM-DD do nome do arquivo."""
    m = re.search(r"iaf_(\d{4}-\d{2}-\d{2})\.html", path)
    return m.group(1) if m else None


def main() -> int:
    cutoff = (datetime.now() - timedelta(days=MAX_DAYS)).strftime("%Y-%m-%d")

    if not os.path.isdir(HISTORY_DIR):
        print(f"ERRO: diretório {HISTORY_DIR} não encontrado.", file=sys.stderr)
        return 1

    # Escaneia HTMLs ordenados por data (mais antigo primeiro)
    pattern = os.path.join(HISTORY_DIR, "iaf_2*.html")
    html_files = sorted(glob.glob(pattern))

    editions = {}

    for path in html_files:
        date = extract_edition_date(path)
        if date is None or date < cutoff:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            titles = extract_titles(content)
            if titles:
                editions[date] = titles
        except Exception as e:
            print(f"AVISO: erro ao processar {path}: {e}", file=sys.stderr)
            continue

    # Monta manifest
    sorted_dates = sorted(editions.keys(), reverse=True)
    titles_flat = []
    for d in sorted(editions):
        titles_flat.extend(editions[d])

    manifest = {
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "edition_count": len(editions),
        "max_days": MAX_DAYS,
        "editions": sorted_dates,
        "titles_flat": titles_flat,
        "titles_by_edition": editions,
    }

    output_path = os.path.join(HISTORY_DIR, "iaf_manifest.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(
        f"OK: manifest atualizado — {len(editions)} edições, "
        f"{len(titles_flat)} títulos em {os.path.getsize(output_path)} bytes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
