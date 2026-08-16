---
name: hermes-style-charts
description: "Data-viz in Hermes style — matplotlib pipeline, fonts, design tokens, QA.

Load this skill when generating charts (bar, line, scatter) in the Hermes Agent design system with matplotlib. Covers the render pipeline and pitfalls: fonts, brand tokens, layout QA. Load style-guide-consultation for the catalog of other brands' guides (ID, IAF)."
version: 1.0.0
author: hermes
license: MIT
tags: [charts, matplotlib, data-viz, hermes-style, design-tokens]
type: Reference
timestamp: 2026-08-13T00:00:00Z
metadata:
  hermes:
    tags: [charts, matplotlib, data-viz, design-tokens]
    related_skills: [style-guide-consultation, html-report-hermes]
---

# Hermes-Style Charts (matplotlib)

Pipeline comprovado para gerar gráficos (barras, linhas, dispersão) no design system
Hermes Agent com matplotlib. Carregue `style-guide-consultation` para o catálogo de
guias e tokens das outras marcas (ID, IAF) — esta skill cobre o pipeline de RENDER
de data-viz e seus pitfalls.

## When to Use
- Usuário pede gráfico(s) — barra, linha, dispersão — sem marca explícita (padrão Hermes) ou em estilo Hermes
- Qualquer data-viz matplotlib que precise de fontes/marca consistentes e QA de layout
- Batch de gráficos comparativos (mesma série de modelos/entidades em vários charts)

## Tokens aplicados a charts
- Fundo branco `#FFFFFF`; grid tracejada `#E8E8E8`; texto `#171717` (charcoal); mute `#9A9AA6`
- Destaques: azul royal `#0000F2` (série principal/hero), amber `#FFBD38` (secundário), red `#FF0000` (só alerta)
- Fontes: **Syncopate** (títulos, uppercase, bold), **Space Mono** (labels/valores), **VT323** (rodapé/índices/legenda)
- Tema claro (azul-royal sobre branco) — coerente com o site Hermes. Dark mode: adaptar com charcoal bg + white fg + amber accent.

## Fontes locais e registro
- TTFs em `/opt/data/fonts/hermes/`: Syncopate-Regular/Bold, SpaceMono-Regular/Bold, VT323-Regular
- Registrar antes de plotar: `fm.fontManager.addfont('/opt/data/fonts/hermes/<fonte>.ttf')`
- Usar via `fontfamily="Space Mono"`, `fontfamily="Syncopate"`, `fontfamily="VT323"`

## Baixar TTF do Google Fonts (quando raw.githubusercontent 404)
O repo google/fonts reestrutura paths (variable fonts `[wght].ttf`, pastas movidas — Syncopate 404 em paths antigos). Técnica que funciona:

```bash
# UA não-browser → API devolve format('truetype') com URL .ttf direto do gstatic
curl -sL -A "curl" "https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&display=swap"
# UAs de browser → devolvem .woff2 (inútil p/ matplotlib); UA simples força .ttf
```
- `fonts.google.com/download?family=X` NÃO é zip (retorna HTML) — não usar.
- Validar TTF baixado: `addfont` + conferir nome em `fm.fontManager.ttflist`.

## Pitfall crítico: Space Mono é fonte LARGA (~1.25em advance)
`"DeepSeek V4 Flash Preview"` (25 chars) ≈ **500px** a 12pt — estoura figura de 2200px com margem de 7–15%.
- Margem esquerda para nomes de modelo: ~26% do width (`fig.add_axes([0.26, 0.115, 0.69, 0.66])`) + fonte 11.5pt.
- NÃO estimar largura de texto — medir (verificação abaixo).

## Verificação de layout: ground truth, não OCR de visão
Vision-model QA oscila/misread em texto cortado e overlap (relatou clipping inexistente e perdeu clipping real). Verificar programaticamente antes do savefig:

```python
fig.canvas.draw()
rend = fig.canvas.get_renderer()
W, H = fig.get_size_inches() * fig.dpi
for t in ax.get_yticklabels():
    b = t.get_window_extent(rend)
    if b.x0 < 0 or b.x1 > W:
        print("CLIP WARNING", t.get_text(), b.x0)  # x0 negativo = label cortado
```
Zero warnings = layout seguro. Aplicar em QUALQUER texto crítico, não só yticklabels.

## Outros pitfalls
- **Slug de arquivo**: substituir `/` — "HLE (wo/w tools)" virou path `wo/w-tools/` → FileNotFoundError. Sanitizar: `.replace("/", "-")` junto com espaços/parenteses.
- **Marcador de líder (★)**: inline após o label de valor (mesmo y). Star flutuante acima da barra (y+offset) parece órfã. Adicionar nota no rodapé: `* = melhor desempenho`.
- **Cores por série fixas entre gráficos de um batch**: família principal em escala de azul (#0000F2 → #4D4DF7 → #8A8AF8 → #C0C0FA), competidores charcoal/amber. Assim os gráficos são comparáveis entre si.
- **Label de valor em barra curta**: no fim da barra com offset pequeno (`val + xmax*0.015`), nunca dentro.
- **Dados ausentes**: sem barra + travessão `—` na posição, nunca barra zero.
- **Escala por gráfico**: `0 → teto de 20` (`max(40, -(-int(hi)//20)*20)`) mantém consistência interna sem barras minúsculas.
- **Entregar em lote**: usuário espera os arquivos — validar rápido (bbox script) e entregar; não ficar em loop longo de QA por imagem.

## Estrutura de gráfico (receita que funcionou)
1. `fig.add_axes([0.26, 0.115, 0.69, 0.66])`, dpi=200, figsize (11, 5.4), fundo branco
2. Título Syncopate bold uppercase azul royal à esquerda; índice `01/10` VT323 à direita
3. Barras horizontais (labels longos cabem na margem), ordenadas por valor desc
4. Labels de modelo via `set_yticks`/`set_yticklabels`, cor por modelo (bold no hero)
5. Grid X tracejada, spines top/right/left removidos, bottom `#D5D5DD`
6. Rodapé VT323: fonte dos dados à esquerda, marca à direita
7. Validação bbox → savefig → montar contact sheet com PIL (thumbnail + grid 2×N)

## Related
- `style-guide-consultation`: catálogo de guias (Hermes, ID, IAF) e tokens CSS para HTML/CSS
- `html-report-hermes`: relatórios HTML dark com SVG charts (outro caminho de render)
