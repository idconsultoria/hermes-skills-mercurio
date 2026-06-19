#!/usr/bin/env python3
"""
entity_frequency.py — Analisa frequência de entidades no manifesto
da IAF para aplicar Regra B (limite de 3 aparições por tópico).

Uso:
    python3 scripts/entity_frequency.py

Lê:  /opt/data/cron/history/iaf_manifest.json
Saída: relatório tabular com entidades, edições e status (✅/⛔)

Design: determinístico, zero dependências, ~5KB de output.
"""

import json
import os
import re
import sys
from collections import defaultdict

HISTORY_DIR = "/opt/data/cron/history"
MANIFEST_PATH = os.path.join(HISTORY_DIR, "iaf_manifest.json")

# ─── ENTIDADES CONHECIDAS ─────────────────────────────────────
ENTITIES = [
    "Anthropic", "OpenAI", "Meta", "Google", "Alphabet", "Microsoft",
    "xAI", "SpaceX", "Apple", "Amazon", "NVIDIA", "AMD", "Intel",
    "DeepMind", "Isomorphic", "Prometheus", "Bezos",
    "Fable", "Mythos", "Claude", "ChatGPT", "GPT", "Gemini",
    "Gemma", "DiffusionGemma", "Llama", "DeepSeek", "Kimi",
    "Qwen", "Grok", "MAI", "Copilot", "Siri", "Manus", "Perplexity",
    "Midjourney", "Stable Diffusion", "Flux", "Ideogram",
    "OpenRouter", "Fusion",
    "S&P 500", "S&P", "IPO", "S-1", "SEC", "FAANG", "MANGOS",
    "SWE-bench", "GSM8K", "DesignArena", "NeurIPS", "ACL",
    "Altman", "Amodei", "Zuckerberg", "Huang", "Yang", "Suleyman",
    "Bezos", "Trump",
    "jailbreak", "shutdown", "desligamento", "moratória",
    "hackathon", "deepfake", "protesto", "data center",
    "regulação", "regulatório", "testes humanos",
    "supercomputador", "RTX", "GPU", "cluster", "semicondutor",
    "jqwik", "R1", "prompt", "agente", "fronteira", "open-weight",
    "open-source", "código aberto", "robótica", "humanóide",
    "Unitree", "NEURA", "Mondo",
]

COMPOUND = {e for e in ENTITIES if " " in e}


def load_manifest() -> dict | None:
    if not os.path.exists(MANIFEST_PATH):
        print(f"Manifesto não encontrado: {MANIFEST_PATH}")
        return None
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def extract_entity_refs(title: str) -> set[str]:
    found = set()
    title_lower = title.lower()
    for entity in COMPOUND:
        if entity.lower() in title_lower:
            found.add(entity)
    for entity in ENTITIES:
        if entity in COMPOUND:
            continue
        pattern = r"\b" + re.escape(entity) + r"\b"
        if re.search(pattern, title, re.IGNORECASE):
            found.add(entity)
    return found


def cluster_key(entities: frozenset) -> str:
    if not entities:
        return "(sem entidades)"
    return " + ".join(sorted(entities)[:3])


def build_report(editions: dict) -> str:
    lines = []
    entity_by_edition = {}
    for date, titles in sorted(editions.items()):
        refs = set()
        for title in titles:
            refs |= extract_entity_refs(title)
        entity_by_edition[date] = refs

    entity_freq = defaultdict(int)
    for refs in entity_by_edition.values():
        for e in refs:
            entity_freq[e] += 1

    flagged = {e for e, c in entity_freq.items() if c >= 3}

    lines.append("=" * 60)
    lines.append("RELATÓRIO DE FREQUÊNCIA DE ENTIDADES")
    lines.append("=" * 60)
    lines.append(f"Total de edições: {len(editions)} | Entidades: {len(entity_freq)}")
    lines.append("")
    lines.append(f"{'Entidade':<25} {'Edições':>8} {'Status':>10}")
    lines.append("-" * 45)
    for entity in sorted(entity_freq, key=lambda e: entity_freq[e], reverse=True):
        count = entity_freq[entity]
        status = "⛔ EXAUSTO" if entity in flagged else "✅ OK"
        lines.append(f"{entity:<25} {count:>8} {status:>10}")

    lines.append("")
    lines.append("-" * 60)
    lines.append("CLUSTERS DE TÓPICOS (por entidade)")
    lines.append("-" * 60)
    cluster_titles = defaultdict(list)
    for date, titles in sorted(editions.items()):
        for title in titles:
            refs = extract_entity_refs(title)
            key = cluster_key(frozenset(refs))
            cluster_titles[key].append(f"[{date}] {title[:80]}")
    for cluster in sorted(cluster_titles, key=lambda k: len(cluster_titles[k]), reverse=True):
        items = cluster_titles[cluster]
        flag = " ⛔" if len(items) >= 3 else ""
        lines.append(f"\n  ▶ {cluster}{flag} ({len(items)} ocorr.)")
        for item in items:
            lines.append(f"      {item}")

    if flagged:
        lines.append(f"\n⚠️  EXAUSTOS (>3 edições): {', '.join(sorted(flagged))}")

    return "\n".join(lines)


def main() -> int:
    manifest = load_manifest()
    if not manifest:
        return 1
    editions = manifest.get("titles_by_edition", {})
    if not editions:
        print("Manifesto vazio.")
        return 1
    print(build_report(editions))

    entity_by_edition = {}
    for date, titles in editions.items():
        refs = set()
        for title in titles:
            refs |= extract_entity_refs(title)
        entity_by_edition[date] = refs
    entity_freq = defaultdict(int)
    for refs in entity_by_edition.values():
        for e in refs:
            entity_freq[e] += 1
    flagged = {e for e, c in entity_freq.items() if c >= 3}
    if flagged:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
