# Layout de documento técnico A4 — fundo branco, marca ID

Receita para estudo, guia e relatório de cliente em A4 de leitura impressa (não deck, não one-pager).
O que decide se a peça parece sóbria é a hierarquia e o ritmo, não o enfeite.

## Tokens

```css
:root{
  --paper:#FFFFFF; --ink:#0A1929; --body:#22333C;
  --teal:#0E7C8A;  /* texto e filetes de acento sobre branco */
  --tealb:#14B8A6; /* acento gráfico, marcas de lista */
  --hair:#DFE7EA; --hair2:#EDF2F4; --wash:#F6FAFB; --quiet:#63767E;
  --head:'Neulis Neue','Nunito Sans',sans-serif; --text:'Nunito Sans',sans-serif;
}
@page{size:A4;margin:0}
.page{width:210mm;height:297mm;padding:19mm 19mm 18mm;overflow:hidden;page-break-after:always}
```

Corpo 9,5 pt / 1,6; `max-width` do parágrafo em ~164 mm (nem linha longa, nem coluna de blog).
Título de seção 17 pt; rótulo de seção 8,2 pt com 1,9 px de letter-spacing.

## Componentes

**Cabeçalho de seção** — número, nome do capítulo e filete de base, numa linha:

```html
<div class="sect"><span class="num">4</span><span class="name">Estrutura de acompanhamento</span></div>
```

O `<h2>` logo abaixo enuncia o conteúdo ("O Painel de Receita e suas cinco pastas"), nunca um slogan.

**Tabela de referência** — é o componente padrão para listas de indicadores, estágios, pastas e
responsáveis. Cabeçalho em maiúsculas pequenas sobre filete de 0,7 pt; linhas separadas por hairline
0,5 pt; sem zebra, sem borda externa, sem cartão.

```css
table.ref td{padding:2,8mm 3mm;border-bottom:.5pt solid var(--hair2);font-size:9pt}
table.ref .k{font-family:var(--head);color:var(--ink)}      /* nome do indicador */
table.ref .sig{color:var(--teal);white-space:nowrap}          /* sigla */
table.ref .who{color:var(--quiet);white-space:nowrap}         /* responsável */
table.ref .num{text-align:right;font-variant-numeric:tabular-nums}
```

**Diagrama de linha** (estágios com os intervalos anotados) — SVG inline de `viewBox="0 0 660 96"`,
altura 24–26 mm: linha hairline, trecho percorrido em `--tealb`, quatro nós, nome do estágio acima,
rótulo do intervalo abaixo em dois níveis (palavra em maiúsculas teal + explicação em `--quiet`).
Fonte do SVG por família, não por variável CSS — conversor que não é navegador ignora `var()`.

**Nota de escopo / fecho** — caixa única com `border-left:1,6pt solid var(--tealb)` e fundo `--wash`,
usada no máximo duas vezes por documento.

## Orçamento de páginas

- ~2,3 mil palavras em 7 páginas com um diagrama de meia página e tabelas — densidade confortável.
- Tabela de referência com 13 linhas + uma tabela de 5 linhas + título e introdução: uma página.
- 21 indicadores em tabela de 3 colunas não cabem em uma página junto da tabela de pastas: divida a
  lista em duas páginas por grupo (ex.: visão geral/comercial/operação · administrativo/financeiro)
  e use a folga da segunda para os critérios de construção do painel.
- Sempre fechar o ciclo: medir overflow → cortar texto (não encolher fonte) → medir de novo.
