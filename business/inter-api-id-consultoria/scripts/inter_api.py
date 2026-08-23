#!/usr/bin/env python3
"""
inter_api.py — Consultas e relatórios da conta PJ do Banco Inter da ID Consultoria.

Instru: python inter_api.py <saldo|extrato|relatorio> [--inicio YYYY-MM-DD] [--fim YYYY-MM-DD]
        [--resumo] [--o saida.html] [--repo /caminho/idata]

Atalho padrão (venv + repo clonados em /opt/data/work/idata):
    PY=/opt/data/work/idata/.venv/bin/python
    $PY inter_api.py saldo
    $PY inter_api.py extrato --inicio 2026-06-01 --fim 2026-06-30 --resumo
    $PY inter_api.py relatorio --inicio 2026-06-01 --fim 2026-06-30 --o rel_v1.html

README: sem credenciais no output. Só dados de negócio e status.
"""
import argparse, os, sys, json, datetime
from pathlib import Path

# Ambiente: repo e interpretador do motor podem ser sobrescritos por env var.
REPO = Path(os.environ.get("IDATA_REPO", "/opt/data/work/idata"))
PCA = Path(os.environ.get("IDATA_PY", "/opt/data/work/idata/.venv/bin/python"))

def load_motor():
    """Importa as funções já validadas do repo idconsultoria/iData."""
    repo = Path(os.environ.get("IDATA_REPO", "/opt/data/work/idata"))
    sys.path.insert(0, str(repo))
    try:
        from etl.extratores.api_inter import obter_token, obter_saldo, obter_extrato
    except Exception as e:
        sys.stderr.write(f"[erro] Não consegui importar o motor em {repo}: {e}\n"
                         "Clone/atualize o repo e crie o venv (ver skill).\n")
        sys.exit(2)
    return obter_token, obter_saldo, obter_extrato


# ----------------------------------------------------------------------------
# Consultas
# ----------------------------------------------------------------------------
def cmd_saldo(args):
    _token, obter_saldo, _extrato = load_motor()
    if args.inicio and args.fim:
        d0 = datetime.date.fromisoformat(args.inicio)
        d1 = datetime.date.fromisoformat(args.fim)
        print("data;disponivel;bloqueadoCheque;bloqueadoJudicialmente;bloqueadoAdministrativo;limite")
        d = d0
        while d <= d1:
            s = obter_saldo(d.strftime("%Y-%m-%d"))
            print(f"{d};{s['disponivel']};{s['bloqueadoCheque']};{s['bloqueadoJudicialmente']};"
                  f"{s['bloqueadoAdministrativo']};{s['limite']}")
            d += datetime.timedelta(days=1)
    else:
        s = obter_saldo(None)
        print("SALDO ATUAL da conta Inter da ID:")
        for k, v in s.items():
            print(f"  {k}: {v}")

def cmd_extrato(args):
    _token, _saldo, obter_extrato = load_motor()
    trans = obter_extrato(args.inicio, args.fim)
    if args.resumo:
        print("dataTransacao;tipoTransacao;titulo;valor")
        for t in sorted(trans, key=lambda x: x.get("dataTransacao", "")):
            val = t.get("valor")
            if isinstance(val, (int, float)):
                val = f"{val:.2f}"
            print(f"{t.get('dataTransacao')};{t.get('tipoTransacao')};{t.get('titulo')};{val}")
    else:
        print(json.dumps(trans, ensure_ascii=False, indent=2, default=str))


# ----------------------------------------------------------------------------
# Relatório HTML (identidade da ID — id-design-guide)
# ----------------------------------------------------------------------------
def cmd_relatorio(args):
    import pandas as pd
    _token, _saldo, obter_extrato = load_motor()
    trans = obter_extrato(args.inicio, args.fim)

    if not trans:
        html = _crash("Sem transações no período")
    else:
        df = pd.DataFrame([{k: v for k, v in t.items() if k != "detalhes"} for t in trans])
        df["valor"] = df.apply(
            lambda r: float(r["valor"]) if r.get("tipoOperacao") == "C" else -float(r["valor"]),
            axis=1)
        entrada = df[df["valor"] > 0]["valor"].sum()
        saida = -df[df["valor"] < 0]["valor"].sum()
        por_tipo = df.groupby("tipoTransacao")["valor"].sum().sort_values()
        linhas = ""
        for _, r in df.sort_values("dataTransacao").iterrows():
            cor = "#14b8a6" if r["valor"] >= 0 else "#f87171"
            linhas += (f"<tr><td>{r.get('dataTransacao')}</td><td>{r.get('tipoTransacao')}</td>"
                       f"<td>{r.get('titulo')}</td>"
                       f"<td style='color:{cor};text-align:right'>R$ {abs(r['valor']):,.2f}</td></tr>")
        barras = "".join(
            f"<div style='display:flex;align-items:center;gap:8px;margin:6px 0'>"
            f"<span style='width:150px'>{tipo}</span>"
            f"<div style='background:#233554;border-radius:4px;height:18px;width:100%'>"
            f"<div style='background:#14b8a6;height:18px;border-radius:4px;width:{max(1,min(100,abs(v)/max(abs(por_tipo.max()),1)*100)):.0f}%'></div>"
            f"</div><span style='width:110px;text-align:right'>R$ {abs(v):,.2f}</span></div>"
            for tipo, v in por_tipo.items())
        html = _template(entrada, saida, entrada - saida, barras, linhas,
                         args.inicio, args.fim)

    out = Path(args.o)
    out.write_text(html, encoding="utf-8")
    print(f"Relatório gerado: {out.resolve()}")

def _crash(msg):
    return (f"<html><body style='background:#0a1929;color:#14b8a6;font-family:sans-serif;"
            f"padding:40px'><h2>Sem dados</h2><p>{msg}</p></body></html>")

def _template(entrada, saida, fluxo, barras, linhas, d0, d1):
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório — Conta Inter ID</title>
<style>
  body{{margin:0;background:linear-gradient(135deg,#0a1929 0%,#112240 100%);color:#e6f1ff;
       font-family:'Nunito Sans',system-ui,sans-serif;}}
  .wrap{{max-width:1000px;margin:0 auto;padding:40px 24px;}}
  h1,h2{{font-family:'Neulis Neue','Nunito Sans',sans-serif;color:#14b8a6;}}
  .cards{{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0;}}
  .card{{background:#112240;border:1px solid #233554;border-radius:12px;padding:20px;flex:1;min-width:180px;}}
  .card b{{display:block;font-size:26px;}}
  table{{width:100%;border-collapse:collapse;margin-top:12px;background:#112240;border-radius:12px;overflow:hidden;}}
  th,td{{padding:10px 14px;text-align:left;border-bottom:1px solid #233554;}}
  th{{background:#0a1929;color:#14b8a6;}}
  .lbl{{color:#8892b0;font-size:13px;text-transform:uppercase;}}
</style></head><body><div class="wrap">
<h1>Conta Inter da ID Consultoria</h1>
<p style="color:#8892b0">Período: {d0} → {d1} · Escopo extrato.read</p>
<div class="cards">
  <div class="card"><span class="lbl">Entradas</span><b style="color:#14b8a6">R$ {entrada:,.2f}</b></div>
  <div class="card"><span class="lbl">Saídas</span><b style="color:#f87171">R$ {saida:,.2f}</b></div>
  <div class="card"><span class="lbl">Fluxo líquido</span><b style="color:#e6f1ff">R$ {fluxo:,.2f}</b></div>
</div>
<h2>Distribuição por tipo</h2>{barras}
<h2>Transações</h2>
<table><thead><tr><th>Data</th><th>Tipo</th><th>Título</th><th>Valor</th></tr></thead><tbody>{linhas}</tbody></table>
</div></body></html>"""


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Consultas da conta Inter da ID")
    ap.add_argument("comando", choices=["saldo", "extrato", "relatorio"])
    ap.add_argument("--inicio")
    ap.add_argument("--fim")
    ap.add_argument("--resumo", action="store_true")
    ap.add_argument("--o", default="/opt/data/work/id-inter-relatorio_v1.html")
    ap.add_argument("--repo", default=str(REPO))
    args = ap.parse_args()
    if args.repo:
        os.environ["IDATA_REPO"] = args.repo
    if args.comando == "saldo":
        cmd_saldo(args)
    elif args.comando == "extrato":
        cmd_extrato(args)
    elif args.comando == "relatorio":
        cmd_relatorio(args)

if __name__ == "__main__":
    main()
