#!/usr/bin/env python3
"""Verifica se os nomes da ID resolvem para o IP esperado do host Oracle.

Consulta dois provedores DoH independentes (Cloudflare e Google) e reporta o nome que
não devolve o IP esperado — inclusive NXDOMAIN (Status 3), que é o sintoma de registro
removido da zona.

Uso:
    python3 verificar-dns-id.py            # inventário padrão
    python3 verificar-dns-id.py --ip 1.2.3.4 nome1.dominio nome2.dominio
    python3 verificar-dns-id.py --quiet    # só o resumo

Saída: uma linha por nome e, no fim, o resumo. Exit 0 = tudo ok; 1 = algum nome fora do
IP esperado; 2 = erro de rede nos provedores (resultado inconclusivo, não é prova de falha).

Por que dois provedores: o NXDOMAIN fica em cache negativo (SOA minimum) e caches regionais
divergem por minutos. Um provedor só não é evidência suficiente — nem de existência, nem de
ausência.
"""

import argparse
import json
import sys
import urllib.request

IP_ESPERADO = "129.146.163.107"

INVENTARIO = [
    "artemis.idconsultoria.ai",
    "1.artemis.idconsultoria.ai",  # curinga dos previews por PR
    "treinamentos.idconsultoria.ai",  # Moodle da ID (mesmo host, atrás do NPM)
]

PROVEDORES = (
    ("cloudflare", "https://cloudflare-dns.com/dns-query"),
    ("google", "https://dns.google/resolve"),
)


def consultar(base: str, nome: str, tipo: str = "A", timeout: int = 15):
    """Devolve (status, [respostas]) no formato DoH JSON. Status 3 = NXDOMAIN."""
    url = f"{base}?name={nome}&type={tipo}"
    req = urllib.request.Request(url, headers={"accept": "application/dns-json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        dados = json.load(resp)
    return dados.get("Status"), [a.get("data") for a in dados.get("Answer", [])]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("nomes", nargs="*", default=None, help="nomes a checar (padrão: inventário)")
    ap.add_argument("--ip", default=IP_ESPERADO, help=f"IP esperado (padrão: {IP_ESPERADO})")
    ap.add_argument("--quiet", action="store_true", help="só o resumo final")
    args = ap.parse_args()

    nomes = args.nomes or INVENTARIO
    problemas, erro_rede = [], False

    for nome in nomes:
        linha = []
        for provedor, base in PROVEDORES:
            try:
                status, respostas = consultar(base, nome)
            except Exception as exc:  # rede/provedor fora — resultado inconclusivo
                erro_rede = True
                linha.append(f"{provedor}=ERRO({exc})")
                continue
            if status == 3:
                linha.append(f"{provedor}=NXDOMAIN")
            elif not respostas:
                linha.append(f"{provedor}=vazio(status={status})")
            else:
                linha.append(f"{provedor}={','.join(str(r) for r in respostas)}")
        ok = all(f"={args.ip}" in p or f",{args.ip}" in p for p in linha)
        if not ok:
            problemas.append(nome)
        if not args.quiet:
            print(f"{'OK  ' if ok else 'FALHA'} {nome}: " + " | ".join(linha))

    print()
    if problemas:
        print(f"RESUMO: {len(problemas)} nome(s) fora do esperado ({args.ip}): {', '.join(problemas)}")
        print("NXDOMAIN = registro ausente na zona; peça o registro A ao dono do DNS")
        print("e use `curl -sk --resolve <nome>:443:<ip> https://<nome>/` para separar DNS de serviço.")
        return 1
    if erro_rede:
        print("RESUMO: nenhum nome fora do esperado, mas houve erro de rede — repetir antes de concluir.")
        return 2
    print(f"RESUMO: todos os {len(nomes)} nomes resolvem para {args.ip}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
