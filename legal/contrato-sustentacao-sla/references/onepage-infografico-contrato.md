# One-page infográfico A4 (HTML → Chromium) — leitura facilitada de contrato/proposta

Receita da página que acompanha a minuta de sustentação: A4 claro, identidade ID, um gráfico por
número. Vale para qualquer "explique o contrato/proposta em uma página" — o conteúdo muda, a forma não.

## Estrutura de arquivos (reprodutível, sem montar HTML à mão a cada ajuste)

```
work/<peca>/fonts.css                 # @font-face Neulis Neue 700 (OTF) + Nunito Sans 400 (woff2)
work/<peca>/logo-id-cor-900.png       # logo colorido, recortado e reduzido
work/<peca>/page-icon.svg             # diamante teal do header
work/<peca>/onepage.template.html     # HTML com {{FONTS}} {{LOGO}} {{ICON}}
work/build_onepage.py                 # injeta os 3 placeholders + renderiza + confere
```

O script injeta `fonts.css` no `<style>`, o logo como `<img src="data:image/png;base64,...">` e o
ícone como SVG sem `width`/`height` fixos (remova os atributos com regex e aplique classe de
tamanho), grava o HTML final e roda o Chromium.

**Logo em fundo claro:** o SVG do template de proposta é **branco** (só serve em fundo escuro). Em
página clara, usar o PNG colorido da identidade (pacote de catálogo em
`profiles/<rama>/workspace/*/assets/png/logo-id-*-cor.png`), com `img.crop(img.getbbox())` e resize
para ~900 px de largura antes de converter para base64.

## Esqueleto CSS do desenho

```css
@page{size:A4;margin:0}
.page{width:210mm;height:297mm;padding:8mm 9mm 6mm;overflow:hidden;position:relative}
:root{--navy:#0a1929;--teal:#4AC6D3;--teal-deep:#0f8b99;--line:#dbe4ec;--bg2:#f6f9fb;
      --ink2:#41566b;--ink3:#7b8c9c;--green:#2f7d5e;--warn:#a8603f}
body{font-family:'Nunito Sans';font-size:7.5pt;line-height:1.3}
h1{font-family:'Neulis Neue';font-size:14.4pt}
h2{ /* rótulo de seção com ícone + fio até a direita: display:flex; gap; h2::after{flex:1;height:1px;background:var(--line)} */ }
```

Blocos que carregam o desenho (cada um com ícone): `.kpi` (valor 10–11 pt + uma linha), `.tl`
(linha do tempo da vigência, barra com gradiente teal e tick labels), `.chart/.bar` (barra
proporcional: label 33% + trilho `flex:1` + valor à direita), `.sev` (severidade: tag colorida S1–S4 +
definição curta + barra de prazo), `.box/.box.green/.box.warn` (destaque), `.decide` (rodapé de
decisão) e `.foot` absoluto a ~4 mm do pé.

## Ícones de linha (inline, sem biblioteca)

```html
<svg class="ic" viewBox="0 0 24 24"><use href="#i-check"/></svg>
...
<svg width="0" height="0"><defs><g id="i-check"><path d="M4 12.5l5 5L20 6.5"/></g>…</defs></svg>
```

- **Todo `<svg>` que só carrega `<use>` PRECISA de `viewBox="0 0 24 24"`.** Sem ele o elemento
  herda o sistema de coordenadas em px, mostra apenas o canto superior esquerdo do desenho 24×24 e o
  ícone sai cortado (o `vision_analyze` acusa "ícone cortado"). Aplique por regex no build, para não
  depender de lembrar em cada linha.
- CSS do ícone: `width/height` em mm, `fill:none; stroke:currentColor; stroke-width:1.7;
  stroke-linecap:round; stroke-linejoin:round` — a cor vem do contexto (`.kpi .icon{color:var(--teal-deep)}`,
  `li.ok svg{color:var(--green)}`, `li.no svg{color:var(--warn)}`).
- `<g id>` + `<use>` funciona; desenhe num grid 24×24 com `stroke`, nunca ícone preenchido e nunca emoji.

## Verificação (as duas que pegam de verdade)

1. **Teste do overflow com altura automática.** Renderize uma variante do HTML com `height:297mm`
   trocado por `height:auto`; se ela vira **2 páginas**, a versão normal está **cortando** conteúdo
   em silêncio (`overflow:hidden`). Corte por conteúdo (frases longas, um item de lista, um bloco)
   antes de encolher fonte. `pdfinfo | grep Pages` nas duas versões.
2. **`vision_analyze` na PNG** (`pdftoppm -png -r 110`): pedir explicitamente por texto invadindo a
   margem/coluna vizinha, ícone não desenhado e bloco desalinhado — a contagem de páginas não vê nada disso.
   Achado típico: **texto longo dentro de linha `flex` empurra o bloco vizinho** → `min-width:0` no
   filho de texto (`flex:1;min-width:0`) é o conserto.

## Conteúdo (o que o dono cobra)

- Um número por cartão, com o número **grande** e a explicação em uma linha.
- Explicar em concreto: "99% de disponibilidade" → "até ~7 h fora do ar no mês sem sair da meta,
  fora manutenção programada e falhas de terceiros".
- Comparativo sempre em barra com **o valor absoluto ao lado**; nunca pizza/donut.
- O que tem começo e fim vira linha do tempo (vigência, 12 parcelas, marcos).
- Item sem obrigação real se declara: "nada devido — nem a receber, nem a cobrar".
- Zero emoji, zero nome de ferramenta interna; rodapé com "documento interno" + link do doc editável.
