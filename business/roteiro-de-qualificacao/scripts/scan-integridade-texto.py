#!/usr/bin/env python3
"""Gate de integridade para texto longo gerado (roteiros, propostas, relatorios).

Detecta o que a leitura normal nao pega:
  - contaminacao de alfabeto (CJK, cirilico, hangul, fullwidth)
  - pontuacao CJK/estrangeira residual no meio de texto PT-BR
  - contagem por secao diferente do esperado
  - sequencia de numeracao com lacuna ou duplicata
  - termos ingleses concatenados sem espaco (sintoma de substituicao mal aplicada)

Uso:
  python3 scan-integridade-texto.py ROTEIRO.md --esperado-por-secao 10
  python3 scan-integridade-texto.py ROTEIRO.md --esperado-por-secao 10 --sequencia 1-80
  python3 scan-integridade-texto.py ROTEIRO.md --termos Committee,affects

Saida: 0 = limpo; 1 = violacao encontrada. Printa o NUMERO DA LINHA de cada achado,
que e o que permite corrigir a linha inteira em vez de a palavra.
"""
import argparse
import re
import sys

# Faixas de caracteres que nunca deveriam aparecer em documento PT-BR/EN gerado.
FAIXAS_SUSPEITAS = {
    "CJK": r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]",
    "Cirilico": r"[\u0400-\u04ff]",
    "Hangul": r"[\uac00-\ud7af]",
    "Fullwidth": r"[\uff01-\uff5e\uff65-\uff9f]",
    "PunctCJK": r"[\u3000-\u303f]",
}
# Terminos PT que normalmente aparecem deitados (sintoma de patch mal aplicado).
TERMOS_SUSPEITOS = [
    "Committee", "affects", "Safra", "airspace", "university", "management",
    "oComite", "doComite", "oSemac", "doSemac",
]


def varrer_alfabeto(caminho):
    linhas = open(caminho, encoding="utf-8").read().split("\n")
    achados = []
    for i, linha in enumerate(linhas, 1):
        for nome, padrao in FAIXAS_SUSPEITAS.items():
            if re.search(padrao, linha):
                achados.append((i, nome, linha.strip()[:160]))
    return achados


def varrer_termos(caminho, termos):
    linhas = open(caminho, encoding="utf-8").read().split("\n")
    achados = []
    alvo = termos or TERMOS_SUSPEITOS
    for i, linha in enumerate(linhas, 1):
        for t in alvo:
            if re.search(r"\b" + re.escape(t), linha):
                achados.append((i, "Termo", f"{t}: {linha.strip()[:140]}"))
    return achados


def contar_por_secao(caminho, padrao_secao, padrao_item):
    texto = open(caminho, encoding="utf-8").read()
    blocos = re.split(padrao_secao, texto, flags=re.M)
    resultado = []
    for b in blocos:
        if not b.strip():
            continue
        nome = b.split("\n", 1)[0].strip()
        n = len(re.findall(padrao_item, b, flags=re.M))
        resultado.append((nome, n))
    return resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--esperado-por-secao", type=int, default=None)
    ap.add_argument("--padrao-secao", default=r"^## ")
    ap.add_argument("--padrao-item", default=r"^\s*\d+\.\s")
    ap.add_argument("--padrao-item-bold", default=r"^\*\*(\d+)\.\s")
    ap.add_argument("--sequencia", default=None, help="ex: 1-80")
    ap.add_argument("--termos", default=None)
    args = ap.parse_args()

    violacoes = 0
    print(f"== varredura: {args.arquivo} ==")

    alfabeto = varrer_alfabeto(args.arquivo)
    if alfabeto:
        violacoes += len(alfabeto)
        print(f"\n[ALFABETO] {len(alfabeto)} linha(s) com caractere fora do PT-BR:")
        for i, nome, l in alfabeto:
            print(f"  {i}: [{nome}] {l}")
    else:
        print("\n[ALFABETO] ok — nenhuma contaminacao")

    termos = [t.strip() for t in args.termos.split(",")] if args.termos else None
    achados_termo = varrer_termos(args.arquivo, termos)
    if achados_termo:
        violacoes += len(achados_termo)
        print(f"\n[TERMOS] {len(achados_termo)} termo(s) suspeito(s):")
        for i, _, l in achados_termo:
            print(f"  {i}: {l}")
    else:
        print("[TERMOS] ok")

    if args.esperado_por_secao is not None:
        secoes = contar_por_secao(args.arquivo, args.padrao_secao, args.padrao_item)
        fora = [(n, c) for n, c in secoes if c != args.esperado_por_secao and c > 0]
        total = sum(c for _, c in secoes)
        print(f"\n[CONTAGEM] {len(secoes)} secao(oes), {total} item(ns)")
        for nome, c in secoes:
            marca = "ok" if c == args.esperado_por_secao else f"!= {args.esperado_por_secao}"
            print(f"  {marca:>6}  {c:>3}  {nome[:70]}")
        if fora:
            violacoes += len(fora)
            print(f"  ATENCAO: {len(fora)} secao(es) fora do esperado")

    if args.sequencia:
        m = re.match(r"^(\d+)-(\d+)$", args.sequencia.strip())
        if m:
            ini, fim = int(m.group(1)), int(m.group(2))
            texto = open(args.arquivo, encoding="utf-8").read()
            nums = [int(x) for x in re.findall(args.padrao_item_bold, texto, flags=re.M)]
            if not nums:
                nums = [int(x) for x in re.findall(r"^\s*(\d+)\.\s", texto, flags=re.M)]
            esperado = list(range(ini, fim + 1))
            faltando = sorted(set(esperado) - set(nums))
            extras = sorted(set(nums) - set(esperado))
            if nums == esperado:
                print(f"\n[SEQUENCIA] ok {ini}..{fim} ({len(nums)} itens)")
            else:
                violacoes += 1
                print(f"\n[SEQUENCIA] DIVERGENTE — esperado {ini}..{fim}, achado {len(nums)}")
                if faltando:
                    print(f"  faltando: {faltando}")
                if extras:
                    print(f"  extras:   {extras}")
        else:
            print(f"[SEQUENCIA] formato invalido: {args.sequencia} (use 1-80)")

    print(f"\nRESULTADO: {'VIOLACOES' if violacoes else 'limpo'} ({violacoes})")
    return 1 if violacoes else 0


if __name__ == "__main__":
    sys.exit(main())
