#!/usr/bin/env python3
"""Portao de poluicao — varre um pacote de skills e acusa residuo do doador ou de terceiros.

Uso:
    python3 portao_poluicao.py <pasta> --termos termos.txt [--max 25]

Formato de termos.txt (uma familia por bloco; '#' comenta):
    [outra empresa/cliente]
    Minuzzo
    Banco Inter
    [pessoa do doador]
    Fulano
    @handle-do-fulano
    [infra do doador]
    /opt/data
    context-kb

Saida: contagem por familia + `arquivo:linha [termo] trecho`.
Exit code: 0 = limpo, 1 = achou residuo (serve de portao em encadeamento), 2 = uso invalido.

Matcher (as tres regras que impedem o portao de mentir):
  - base64 mascarado antes da varredura: template com fonte/imagem embutida tem MB de
    `base64,...` e sigla em caixa alta casa dentro do payload;
  - sigla CAIXA ALTA e caminho absoluto casam case-sensitive e com fronteira de palavra
    (sigla curta sem fronteira acha texto no meio de palavra);
  - nome proprio casa com re.I.
"""
from __future__ import annotations

import pathlib
import re
import sys

TEXTOS = {'.md', '.html', '.htm', '.py', '.mjs', '.js', '.json', '.txt', '.css',
          '.yml', '.yaml', '.toml', '.sh', '.svg'}
B64 = re.compile(r'base64,[A-Za-z0-9+/=\s]{40,}')
ACRONIMO = re.compile(r'[A-Z]{2}')


def le_termos(caminho: str) -> dict[str, list[str]]:
    fam, fams = None, {}
    for linha in pathlib.Path(caminho).read_text(encoding='utf-8').splitlines():
        s = linha.strip()
        if not s or s.startswith('#'):
            continue
        if s.startswith('[') and s.endswith(']'):
            fam = s[1:-1].strip()
            fams.setdefault(fam, [])
            continue
        if fam is None:
            raise SystemExit(f'termo fora de familia (falta cabecalho [familia]): {s!r}')
        fams[fam].append(s)
    if not fams:
        raise SystemExit('arquivo de termos vazio')
    return fams


def pattern(termo: str) -> re.Pattern:
    if ACRONIMO.search(termo) or termo.startswith('/') or termo.startswith('~'):
        return re.compile(r'(?<![A-Za-z0-9])' + re.escape(termo) + r'(?![A-Za-z0-9])')
    return re.compile(re.escape(termo), re.I)


def main(argv: list[str]) -> int:
    if '--termos' not in argv or len(argv) < 2:
        print(__doc__)
        return 2
    raiz = pathlib.Path(argv[1])
    termos = pathlib.Path(argv[argv.index('--termos') + 1])
    maximo = int(argv[argv.index('--max') + 1]) if '--max' in argv else 25
    if not raiz.is_dir() or not termos.is_file():
        print('caminho invalido: informe uma pasta e um arquivo de termos')
        return 2

    fams = le_termos(str(termos))
    compilados = {f: [(t, pattern(t)) for t in termos_da_fam] for f, termos_da_fam in fams.items()}
    achados: dict[str, list[tuple[str, int, str, str]]] = {f: [] for f in fams}
    varridos = 0

    for p in sorted(raiz.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in TEXTOS:
            continue
        varridos += 1
        txt = B64.sub('base64,<IMG>', p.read_text(encoding='utf-8', errors='ignore'))
        linhas = txt.split('\n')
        for fam, pares in compilados.items():
            for termo, rx in pares:
                for m in rx.finditer(txt):
                    ln = txt[:m.start()].count('\n') + 1
                    achados[fam].append((str(p.relative_to(raiz)), ln, termo, linhas[ln - 1].strip()[:110]))

    print(f'Arquivos de texto varridos: {varridos}\n')
    total = 0
    for fam, itens in achados.items():
        print(f'{fam}: {len(itens)} ocorrencia(s)')
        total += len(itens)
        for arq, ln, termo, trecho in itens[:maximo]:
            print(f'   {arq}:{ln} [{termo}] {trecho}')
        if len(itens) > maximo:
            print(f'   ... +{len(itens) - maximo}')
    print(f'\nTOTAL: {total}')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
