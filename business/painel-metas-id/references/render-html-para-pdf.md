# Render e verificação destes HTML (painel e slide)

Vale para os artefatos da ID gerados como HTML: painel de metas, slide da Phronesis, decks em
geral. Pipeline usado: **WeasyPrint** (via `PYTHONPATH=/opt/mercurio-data/work/pylibs python3`)
e **pymupdf** para rasterizar e conferir com visão.

## Regra de verificação

**Conte as páginas e olhe as páginas.** Deck de N slides tem de gerar PDF de N páginas. Se o PDF
tem mais, algum bloco estourou a altura e o resto daquele slide virou página órfã. Rasterize
(`pymupdf.open(pdf)[i].get_pixmap(dpi=72).save(png)`) e inspecione — layout "certo" no HTML sai
empilhado, cortado ou sem o elemento gráfico.

Confira os dois temas quando o artefato é lido no navegador e impresso: `media_type="screen"`
(tema escuro) e `media_type="print"` (tema claro). Print com variáveis CSS trocadas resolve
texto branco sobre fundo branco de uma vez — redefina os tokens em `@media print`.

## O que o motor de impressão não suporta

- **`grid-template-columns: repeat(auto-fit, minmax(Npx, 1fr))`** — colapsa para **uma coluna**,
  empilhando os cards e estourando a altura. Use `repeat(N, 1fr)` com N calculado no gerador a
  partir da contagem de itens.
- **SVG inline estilizado por classe/`var()`** — não pinta: as formas saem pretas ou invisíveis.
  Para linha decorativa/diagrama simples prefira **div + gradiente CSS** (diagonal:
  `linear-gradient(to bottom right, transparent 49.3%, rgba(...,.55) 49.85%, rgba(...,.55) 50.35%, transparent 50.9%)`);
  se o SVG for indispensável, ponha `fill`/`stroke` literais no próprio elemento.
- **`overflow:hidden` não segura paginação** — os filhos que passam da altura continuam na
  página seguinte mesmo com o container no tamanho certo. Reduza conteúdo, não confie no clip.
- `-webkit-background-clip: text` é ignorado. Gradientes comuns **funcionam**.

## Medir em vez de chutar

A árvore de caixas diz exatamente qual bloco estourou:

```python
import weasyprint
doc = weasyprint.HTML(filename=html, media_type="print").render()
slide = doc.pages[i]._page_box.children[0].children[0]   # html > body > section
for box in slide.children:
    print(box.element_tag, getattr(box.element, "get", lambda *_: None)("class"),
          box.position_y, box.height, box.position_y + box.height)
```

Atalho para isolar um slide suspeito: monte um HTML temporário só com o `<head>` (CSS) + aquela
`<section>` e renderize — 17 slides levam ~90 s, um slide leva segundos.

`@page{size:1920px 1080px}` vira **1440×810 pt** (1px = 0.75pt) — formato em pt não é defeito.
Imagem em base64 e `@font-face` com `data:font` funcionam offline.
