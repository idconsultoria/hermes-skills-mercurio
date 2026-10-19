#!/usr/bin/env python3
"""Prepara markdown para o md-to-gdoc.py.

Correge tres defeitos que aparecem no PDF exportado quando o markdown foi
datilografado com quebra de linha suave:

1. parse_md do motor trata CADA LINHA como um paragrafo -> paragrafos
   fragmentados em linhas curtas. Aqui as linhas de continuacao viram uma so.
2. Uma linha recuada depois de bullet/numerada/heading continua a linha anterior
   (senao vira paragrafo novo e perde a indentacao).
3. Callout (>) em fonte monoespacada estoura a margem -> quebra por palavra
   em pedacos de MAX_CALLOUT caracteres, nunca no meio de um token.

E converte lista numerada nativa em bullet com numero explicito, porque
createParagraphBullets cria uma lista por paragrafo e "1. 2. 3." sairia
como "1. 1. 1." no PDF.

Uso:
    python3 prepara_md.py original.md=pronto.md [outro.md=outro_pronto.md]
"""
import re
import shutil
import sys

MAX_CALLOUT = 74


def quebra_por_palavra(texto, largura):
    palavras = texto.split()
    linhas, atual = [], ""
    for p in palavras:
        if atual and len(atual) + 1 + len(p) > largura:
            linhas.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}" if atual else p
    if atual:
        linhas.append(atual)
    return linhas


def e_quebra_pagina(line):
    return bool(re.match(r"^\s*(<!--\s*pagebreak\s*-->|\\pagebreak)\s*$", line, re.I))


def e_bloco(line):
    s = line.strip()
    return bool(
        s.startswith("|")
        or s.startswith("```")
        or s.startswith("#")
        or s.startswith(">")
        or re.match(r"^[-*]\s+", s)
        or re.match(r"^\d+\.\s+", s)
        or re.match(r"^={3,}$", s)
        or re.match(r"^-{3,}$", s)
    )


def normaliza(linhas):
    out = []
    buf = None

    def flush():
        nonlocal buf
        if buf is not None:
            out.append(buf)
            buf = None

    for raw in linhas:
        linha = raw.rstrip()
        s = linha.strip()

        if not s:
            flush()
            out.append("")
            continue

        if e_quebra_pagina(linha):
            flush()
            out.append(s)
            continue

        # bloco de codigo: preserva como veio
        if linha.startswith("```"):
            flush()
            out.append(linha)
            continue

        if s.startswith("|"):
            flush()
            out.append(linha)
            continue

        if s.startswith(">"):
            flush()
            texto = re.sub(r"^>\s?", "", s)
            if not texto:
                out.append(">")
                continue
            for pedaco in quebra_por_palavra(texto, MAX_CALLOUT):
                out.append("> " + pedaco)
            continue

        if e_bloco(linha):
            flush()
            out.append(linha)
            continue

        # recuo = continuacao da linha anterior
        if linha[:1].isspace() and out and out[-1].strip():
            sep = "" if out[-1].endswith(("|", "-")) else " "
            out[-1] = out[-1] + sep + s
            continue

        # texto corrido: junta no buffer
        if buf is None:
            buf = s
        else:
            buf = f"{buf} {s}"

    flush()
    return out


def converte_numeradas(linhas):
    """'1. texto' -> '- **1.** texto' (mantem o numero da fonte)."""
    out = []
    for linha in linhas:
        m = re.match(r"^(\d+)\.\s+(.*)$", linha.strip())
        if m and not linha.startswith(" "):
            out.append(f"- **{m.group(1)}.** {m.group(2)}")
        else:
            out.append(linha)
    return out


def prepara(origem, destino):
    shutil.copy(origem, destino)
    linhas = normaliza(open(origem, encoding="utf-8").read().split("\n"))
    linhas = converte_numeradas(linhas)

    saida = []
    for l in linhas:
        if not l.strip() and saida and not saida[-1].strip():
            continue
        saida.append(l)
    open(destino, "w", encoding="utf-8").write("\n".join(saida))

    n = sum(1 for l in saida if re.match(r"^- \*\*\d+\.\*\*", l))
    print(f"{destino}: {len(saida)} linhas | itens numerados: {n}")

    curtas = [l for l in saida
              if l.strip() and not e_bloco(l)
              and not l[:1].isspace() and len(l) < 45]
    if curtas:
        print("   paragrafos curtos (revisar se sobrou quebra de linha suave):")
        for l in curtas[:8]:
            print("     ", l)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        origem, destino = arg.split("=", 1)
        prepara(origem, destino)
