# PDF → HTML: replicação com assets vetoriais originais

Técnica validada em 14/08/2026 (proposta Minuzzo → `Proposta_Minuzzo_slides_v3.html`). Converte um deck em PDF (export Figma) para HTML com a **arte vetorial original** como camada de fundo e **texto HTML semântico** sobreposto — sem redesenhar nada à mão.

## Anatomia de PDFs exportados do Figma (descoberta-chave)

PDFs do Figma têm DUAS representações do texto:
1. **Camada de acessibilidade invisível** — operadores `BT/ET` no content stream da página com fonte **Type3** e cor preta (invisível sobre fundo preto). É o que `page.get_text("dict")` retorna. Os glifos são códigos mapeados (ex.: `€` = nbsp real, `\r\n` = artefatos, duplicações tipo "Wor Wor").
2. **Texto VISÍVEL como paths vetoriais** — dentro de Form XObjects aninhados (`X1 → X1 → X1`), desenhado como fill branco/teal (ex.: grupos de ~190-5000 items por linha). É o que o olho vê.

Consequência: **redaction (`apply_redactions`) não remove o texto visível** — o texto é path, não texto. `get_text` após redaction volta 0, mas o render fica idêntico (texto ainda lá).

## Pipeline (PyMuPDF ≥ 1.24, `get_svg_image`)

```
pymupdf page.get_svg_image() → SVG da página inteira (paths, masks, opacity, imagens base64)
→ remover paths de TEXTO (filtro por fill + overlap com spans)
→ SVG limpo = camada .bg (arte original sem texto)
→ texto reconstruído (data-text dos <use>) vira HTML semântico no .fg
```

No SVG gerado:
- **Texto invisível**: `<use data-text="R" xlink:href="#font_8_12" transform="matrix(60,0,0,-60,X,Y)"/>` — data-text tem os CARACTERES CORRETOS (resolve os artefatos do layer de acessibilidade). Os defs `font_8_*` são grupos VAZIOS (o use não renderiza nada).
- **Texto visível**: `<path transform="matrix(1,0,0,-1,X,Y)" d="..."/>` com fill branco/teal, logo após os uses. bbox renderizado = aplicar matrix ao bbox local do `d`.

### Remover paths de texto (classificação)
- Path é TEXTO se fill ∈ {#ffffff, #4ac6d3, #1baebe} E bbox sobrepõe um span (bbox de linha do `get_text("dict")`).
- **Blocos multi-linha** (1 path = várias linhas, ex. 750×374 com 8 linhas): a razão inter/area por linha individual fica < 0.15. Usar **soma das interseções com todas as linhas / área do path > 0.35** (arte real tem ratio ~0.02-0.05).
- Logos vetoriais (ex.: logo ID branca) NÃO sobrepõem spans → ficam (e viram asset reutilizável).
- Ícones teal pequenos (diamond do header) podem ser removidos do fundo se você for recriá-los em HTML — remover por bbox.

### Reconstruir texto limpo (fix de ligaduras)
- Agrupar `<use data-text>` por linha (use.y dentro do bbox da linha, sem expandir vertical ±8px — bboxes adjacentes se sobrepõem e embaralham usos de linhas vizinhas). Ordenar por x, concatenar.
- **Ligaduras 'fi'/'fl'**: o glifo ligado tem data-text='f' e PERDE o 'i'/'l' → "Artifcial", "ofcina", "fexibilidade". Fix: `difflib.SequenceMatcher(access, clean)` — quando o texto de acessibilidade tem um 'i'/'l' deletado após 'f', reinserir. Trocar `€`→nbsp antes do alinhamento.
- Strip `\r\n` dos textos.

### Extrair assets de marca (logos) do SVG
- Selecionar paths por fill + bbox renderizado (parse `d` + transform matrix). Copiar para um componente `<svg viewBox="x0 y0 w h">` — **preservar o transform matrix(1,0,0,-1,X,Y) de cada path**.
- **Pitfall que deixou logo invisível**: esquecer de copiar `fill="#ffffff"` — default SVG é preto sobre fundo preto. Sempre setar fill no wrapper OU em cada path.
- Versões: logo completa (com tagline) para capa/final; **mark** (símbolo + letras) ou **diamond puro** para slides padrão — decidir olhando o deck de referência.

### Opacidade da arte
- A arte blob/contorno é desenhada com `gs /E1 (ca .4)` = 40% de opacidade. O `get_svg_image` já preserva (`<g opacity=".4">`). Ao medir no render: fill 0.227 (58,58,58) a 40% sobre preto = (23,23,23) exato. Não duplicar opacity manualmente.

## Pitfall Python: gerar HTML via f-strings
- `{fn(...)}` = executa a função; `{{fn(...)}}` = literal `{fn(...)}` no HTML. Com placeholders `{{CLIENTE}}` (escapados como `{{{{CLIENTE}}}}`), é fácil usar chave dupla na chamada de função e o HTML sai com a chamada como texto. Sintoma: `grep col_h3( arquivo.html` retorna ocorrências.
- Depois de um `replace_all` parcial, conferir o par completo (`{col_h3(...)}` e não `{col_h3(...)}` + sobras `)}}`). Rodar o builder e grepar o HTML por resíduos da chamada.

## Verificação (o usuário corrigiu este hábito)
- **Programática primeiro**: `browser_console` com `getBoundingClientRect` (left/top/size reais), computed styles (fontSize, color, backgroundColor, textAlign), contagem de ícones/elementos, checagem de overflow (`er.right > r.right + 1`).
- **vision model é não-confiável para posicionamento**: diz "centralizado" o que está à direita, "duplicado" slides irmãos, alucina ícones ("câmera/porquinho"), e zoom 0.66 distorce. Usar zoom 1 para detalhes finos.
- **Referência v3 (deck aprovado)**: coletar dele as posições reais (title left/top/size, bullet color, transição align, capa title pos) e comparar numericamente com o modelo — a diferença é a lista de ajustes.

## Processo iterativo com o usuário (ID Consultoria)
- **Um slide de cada vez**: capa → slides padrão → transições → final. Cada slide validado vira referência.
- "Compare com o v3" = extrair posições/cores/estilos do deck aprovado por inspeção programática.
- Entregas sempre versionadas e enviadas ao Telegram (Bot API `sendDocument` direto, `.html` funciona sem zipar).
