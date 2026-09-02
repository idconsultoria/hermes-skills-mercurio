# Geração de variantes de marca a partir de um PNG principal

Pipeline usado e validado na criação dos assets da BiotechSe (logo enviado em PNG 1280×720,
fundo preto). O script correspondente é `scripts/generate_logo_variants.py`.

## Heurísticas

### 1. Crop ao conteúdo
- Threshold nos 3 canais (default 20): pixel "vivo" se qualquer canal > thr.
- Calcula bbox do primeiro ao último pixel vivo; aplica padding (40px) p/ respiro.
- Sem bbox → usa a imagem inteira (não quebra).

### 2. Fundo → transparente
- Preto real (r,g,b < 25) vira `alpha=0`. Tudo o mais vira RGBA opaco.
- Funciona para fundos pretos e quase-pretos; para fundos coloridos usar chroma-key por cor
  dominante do canto (não coberto pelo script base — estender se precisar).

### 3. Recolorir para fundo claro (positivo)
O branco do PNG original tem DOIS significados visuais que o script separa pela **posição**:
- Zona do **ícone** (topo ~55% da altura do crop) → cor primária da marca (ex.: teal `#029190`).
- Zona do **wordmark** (restante) → charcoal `#2d2d2d`.
- Verdes originais → normalizados para mint `#00ffa3` (ou o verde da marca).
- Outros tons (cinzas) → mantidos.

Ajuste `--split` se o ícone ocupar proporção diferente. Para marcas sem divisão
ícone/texto, passe `--split 0` (tudo branco → `icon_white`) ou `1` (tudo → `text_white`).

### 4. Composição de fundo
- Positivo: compor o recolorido transparente sobre `cream #f7eadf` e `offwhite #f2f1f0`.
- Negativo: compor o original transparente sobre `charcoal #2d2d2d` (usa quando a página é escura).

### 5. Símbolo isolado
- Recorta só a zona do ícone (topo 58% da altura), re-aplica bbox, padding 20px.
- Exporta transparente + sobre charcoal/off-white. Uso: app icon, favicon, pin, badge.

### 6. Monocromáticas
- Tudo não-transparente → branco (sobre charcoal) ou charcoal (sobre off-white).
- Uso: marca d'água, estamparia, selo.

### 7. Vetor (SVG)
O raster não substitui o vetor para lockup. Reconstruir à mão com a geometria do manual:
- Forma do "B" em grotesk (path com `stroke-linecap:round`, espessura ~11 em viewBox 120×90).
- Dupla fita de DNA (dois paths senoidais) + folha (path fechado).
- Wordmark em `<text>` com Clash Display 500; sufixo "se" em mint; assinatura em Tomato/Hanken.
- Ver exemplo em `biotechse-assets/logos/biotechse-logo-positivo.svg`.

## Pitfalls
- Não usar o PNG original em fundo claro: o fundo preto vira uma mancha. Sempre gera positivo.
- Teal puro `#029190` como cor de texto corrido tem ~3.2:1 (falha AA) — use `teal-deep #01706f`.
- Se o cliente mandar logo já em fundo transparente, pule a etapa 2 (o script ainda recorta/recolore).
- Pillow em PRoot: `python3 -c "from PIL import Image"`; se faltar, `pip install pillow` (ou venv).
