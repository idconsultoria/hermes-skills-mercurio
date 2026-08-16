#!/usr/bin/env python3
"""Teste empírico de engines SearXNG — robusto, mede resultados+latência+erros.

Roda do container Hermes contra http://searxng-core:8080 (acessível).
Para cada engine candidata: 5 queries variadas, 2 rodadas, mede:
  - nº de resultados
  - latência
  - erro/unresponsive
Suspensões do SearXNG são temporárias; entre chamadas esperamos 2s para não
disparar rate-limit. Engines que falharem em >1 rodada são descartadas.
"""
import json
import time
import urllib.request
import urllib.parse

BASE = "http://searxng-core:8080"
# Engines de busca web geral (sem API key) instaladas no container
ENGINES = [
    "bing", "google", "duckduckgo", "brave", "mojeek", "startpage",
    "yahoo", "dogpile", "fireball", "gmx", "iseek", "marginalia",
    "mwmbl", "presearch", "privacywall", "seznam", "swisscows",
    "tusksearch", "heexy", "vuhuv", "yacy", "chatnoir", "bpb",
    "boardreader", "annas_archive", "grokipedia", "wikidata", "wikipedia",
]
# Queries variadas: EN, PT, técnica, local, notícia
QUERIES = [
    "OpenAI GPT-5",
    "análise financeira consultoria empresas",
    "python async programming tutorial",
    "previsão do tempo Aracaju",
    "latest AI news",
]

def search(engine: str, query: str) -> dict:
    params = urllib.parse.urlencode({
        "q": query, "format": "json", "engines": engine, "pageno": 1,
    })
    url = f"{BASE}/search?{params}"
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        lat = time.time() - start
        return {
            "n": len(data.get("results", [])),
            "lat": lat,
            "unresponsive": data.get("unresponsive_engines", []),
            "error": None,
        }
    except Exception as e:
        return {"n": 0, "lat": time.time() - start,
                "unresponsive": [], "error": f"{type(e).__name__}: {str(e)[:120]}"}

def run_round(label: str) -> dict:
    results = {}
    for eng in ENGINES:
        per_eng = []
        for q in QUERIES:
            r = search(eng, q)
            per_eng.append(r)
            time.sleep(1.5)  # evitar rate-limit / suspensão em cadeia
        results[eng] = per_eng
    print(f"\n===== RODADA {label} =====", flush=True)
    print(f"{'engine':<14} {'ok_q':>4} {'avg_n':>6} {'avg_lat':>8} {'errs':>5}  detalhe")
    summary = {}
    for eng, rs in results.items():
        ok = sum(1 for r in rs if r["n"] > 0)
        avg_n = sum(r["n"] for r in rs) / len(rs)
        avg_lat = sum(r["lat"] for r in rs) / len(rs)
        errs = sum(1 for r in rs if r["error"])
        detail = []
        for r in rs:
            if r["error"]:
                detail.append("ERR")
            elif r["n"] == 0:
                detail.append("0")
            else:
                detail.append(str(r["n"]))
        print(f"{eng:<14} {ok:>4} {avg_n:>6.1f} {avg_lat:>7.1f}s {errs:>5}  {' '.join(detail)}", flush=True)
        summary[eng] = {"ok": ok, "avg_n": avg_n, "avg_lat": avg_lat, "errs": errs, "detail": detail}
    return summary

if __name__ == "__main__":
    r1 = run_round("1/2")
    time.sleep(10)
    r2 = run_round("2/2")
    print("\n===== RANKING (2 rodadas, ok>=4 nas 2) =====")
    ranked = []
    for eng in ENGINES:
        a, b = r1[eng], r2[eng]
        ok_total = a["ok"] + b["ok"]
        n_total = a["avg_n"] + b["avg_n"]
        lat_avg = (a["avg_lat"] + b["avg_lat"]) / 2
        stable = (a["errs"] == 0) and (b["errs"] == 0)
        if ok_total >= 8:  # pelo menos 4/5 em cada rodada
            ranked.append((eng, ok_total, n_total, lat_avg, stable, a["detail"], b["detail"]))
    ranked.sort(key=lambda x: (-x[1], -x[2], x[3]))
    for eng, ok, n, lat, stable, d1, d2 in ranked:
        print(f"  {eng:<14} ok={ok}/10 n={n:.1f} lat={lat:.1f}s stable={stable}")
        print(f"      r1: {' '.join(d1)}")
        print(f"      r2: {' '.join(d2)}")
    print("\n===== DESCARTADAS (instáveis ou sem resultados) =====")
    for eng in ENGINES:
        if eng not in [x[0] for x in ranked]:
            a, b = r1[eng], r2[eng]
            print(f"  {eng:<14} ok={a['ok']+b['ok']}/10 errs={a['errs']+b['errs']} r1={a['detail']} r2={b['detail']}")
