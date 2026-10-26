#!/usr/bin/env python3
# -*- coding: utf-8 -*-"""
Mede o excesso de altura de cada pagina de um documento A4 de altura fixa
(.page{height:297mm; overflow:hidden}) SEM browser, percorrendo a arvore geometrica
do WeasyPrint. Nesse tipo de documento o conteudo excedente nao cria pagina nova:
passa por cima do rodape. A contagem de paginas nao detecta.

Uso:
    python3 medir-overflow-weasyprint.py documento.html

Saida: uma linha por pagina, excesso em mm (positivo = passa da linha do rodape).
Exit code 1 se alguma pagina estourar.
"""
import sys

from weasyprint import HTML

PX_PER_MM = 96.0 / 25.4
TOLERANCIA_MM = 0.5


def _cls(box):
    el = getattr(box, 'element', None)
    return str(el.get('class') or '') if el is not None else ''


def walk(box, out, in_foot=False):
    """Coleta caixas pulando a subarvore inteira do rodape.

    Os filhos do rodape nao carregam a classe `.foot`; sem este flag eles viram o
    'ultimo elemento' de toda pagina e o resultado sai uniformemente errado.
    """
    if not in_foot:
        out.append(box)
    if 'foot' in _cls(box):
        in_foot = True
    for ch in getattr(box, 'children', ()) or ():
        walk(ch, out, in_foot)


def medir(path):
    doc = HTML(filename=path).render()
    print(f"paginas renderizadas: {len(doc.pages)}")
    pior_geral = -999.0
    for i, page in enumerate(doc.pages, 1):
        boxes = []
        walk(page._page_box, boxes)
        secs = [b for b in boxes if getattr(b, 'element_tag', None) == 'section']
        if not secs:
            print(f"pg {i}: secao .page nao encontrada")
            continue
        sec = secs[0]
        # Limite real = topo do rodape absoluto. Sem rodape, o fim da caixa de conteudo:
        # .page com box-sizing:border-box tem box.height = caixa de CONTEUDO
        # (~260 mm num A4 com padding 19/18 mm), nao a folha.
        foots = [b for b in boxes if 'foot' in _cls(b)]
        if foots:
            limite = foots[0].position_y - 1.0 * PX_PER_MM
        else:
            limite = sec.position_y + sec.height
        pior_bottom, pior_tag = 0.0, ''
        for b in boxes:
            tag = getattr(b, 'element_tag', None) or ''
            if tag in ('', 'html', 'body'):
                continue
            bottom = b.position_y + b.height
            if bottom > pior_bottom:
                pior_bottom, pior_tag = bottom, f"{tag}.{_cls(b)}".strip('.')
        excesso = (pior_bottom - limite) / PX_PER_MM
        pior_geral = max(pior_geral, excesso)
        estado = 'OVERFLOW' if excesso > TOLERANCIA_MM else 'ok'
        print(f"pg {i}: {estado}  excesso={excesso:+.1f} mm  (ultimo: {pior_tag})")
    return pior_geral


if __name__ == '__main__':
    alvo = sys.argv[1] if len(sys.argv) > 1 else 'documento.html'
    pior = medir(alvo)
    sys.exit(1 if pior > TOLERANCIA_MM else 0)
