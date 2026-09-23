# Emissor python-pptx — receitas

## Escala

Deck 1920x1080 px → slide 13,333x7,5 in (16:9): `1 px = 6350 EMU`; logo `1 pt = 2 px` (font-size em px ÷ 2). Slide: `prs.slide_width = Emu(1920*6350)`, `slide_height = Emu(1080*6350)`, layout em branco.

## XML que o python-pptx não expõe

- **Gradiente:** `a:gradFill` com `a:gsLst` (um `a:gs pos=pos*1000` por stop; `a:srgbClr` + `a:alpha` quando alpha < 1) e `a:lin ang=(graus_css + 90) * 60000`. Trate `transparent` como `rgba(0,0,0,0)`. Precisa entrar na ordem do schema (`a:prstGeom`/`a:xfrm` antes); remova fills anteriores (`a:noFill|a:solidFill|a:gradFill`) antes de inserir.
- **Alpha em fill sólido:** `a:solidFill/a:srgbClr/a:alpha val=alpha*100000` — vale para formas **e** para células de tabela.
- **Sombra:** `a:effectLst/a:outerShdw` com `blurRad ≈ 1,6 × blur_css × 6350`, `dist = hypot(dx,dy) * 6350`, `dir = atan2(dy,dx)` em 60000avos (270° quando deslocamento zero), `rotWithShape="0"`, `a:srgbClr` + alpha. Use `shape.shadow.inherit = False` quando não houver sombra.
- **Canto arredondado:** `MSO_SHAPE.ROUNDED_RECTANGLE` com `shape.adjustments[0] = min(0.5, raio / min(w,h))`.

## Bordas

4 lados → contorno normal (`line.color` + `line.width = max(1, w/2) * 12700`). 1–3 lados → `line.fill.background()` e desenhe um retângulo fino preenchido por lado (topo/base com altura = largura da borda; esquerda/direita com largura = borda). Contornar a caixa inteira cria moldura falsa em rodapé com `border-top`.

## Texto

- `tf.word_wrap = not single`, `tf.auto_size = None`, margens todas 0.
- `single = rect.h <= 1.75 * fs` → `vertical_anchor = MIDDLE`, caixa `y-5`/`h+10` e largura generosa (`max(w*1.3, w+60)`, expandindo conforme o alinhamento) para nunca quebrar linha.
- multi-linha → `vertical_anchor = TOP`, `y += max(0, (lineHeight - fs) / 2)` (half-leading do CSS vs. leading abaixo no PowerPoint), largura `+12` (se centralizado, `x-6`).
- `p.line_spacing = lineHeight / fs` (só se a razão ficar entre 0,7 e 3).
- Letter-spacing → `run.font._rPr.set('spc', str(int(px/2*100)))`.
- `text-transform` aplicado no texto do run (uppercase/lowercase).
- Runs: tamanho/peso/cor/família por run (o CSS inline muda cor e negrito no meio da frase).
- Fontes: família de display para títulos, família de corpo para o resto — mantendo os nomes reais do deck (o cliente precisa tê-las instaladas).

## Tabelas nativas

`add_table(len(rows), ncols, x, y, w, soma_alturas)`; `table.first_row = False`, `table.horz_banding = False` (senão o estilo padrão do Office pinta faixas que não existem no deck). Larguras de coluna pela linha de cabeçalho; altura de linha `max(row_h, fs_max * 1.9 + 10)` para o texto não ser cortado ao renderizar no Office. Células: margens 2 px/1 px, `vertical_anchor = MIDDLE`, fill sólido **com alpha** ou `fill.background()`.

## Ordem das formas

1) imagem do fundo cobrindo o slide; 2) caixas (+ retângulos de borda parcial); 3) selos de pseudo-elemento; 4) logos/imagens base64 decodificadas; 5) ícones SVG rasterizados; 6) tabelas; 7) textos. Texto por último garante que nada o cubra.

## Checagens antes de entregar

- `pdfinfo` no PDF gerado pelo LibreOffice: páginas == slides.
- Percurso visual de **todos** os slides na composição referência|conversão.
- Contagem de formas/imagens/tabelas por slide coerente com o JSON (uma imagem a menos = SVG sem PNG, silencioso).
- Tamanho do `.pptx` (~8 MB com fundos rasterizados) e menção das fontes na entrega.
