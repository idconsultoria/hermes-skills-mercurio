---
name: pdf-deck-to-html
description: "Convert PDF/Figma decks to HTML slides — original art preserved, real text.

Load this skill when converting presentations/PDFs into HTML that opens in the browser, keeping the ORIGINAL art with real selectable text. Validated formula: semantic HTML + original PDF art as background + real text positioned over PDF regions + explicit colors. Never redraw brand assets manually — extract them (v3 approved by user, v2 rejected)."
metadata:
  hermes:
    tags: [pdf, html, pymupdf, svg, deck, slides, figma, reconstruction]
    related_skills: [html-pdf-fidelity, research-report-standards]
type: Media
timestamp: 2026-08-14T00:00:00Z
---

# PDF/Deck → HTML Reconstruction

Converte apresentações/PDFs em HTML que abre no navegador, mantendo a arte ORIGINAL e com texto real. Validado em 3 iterações com usuário (14/ago/2026): a fórmula que ele aprovou é **HTML semântico + arte original do PDF como fundo + texto real posicionado nas regiões do PDF + cores explícitas**.

## Regra de ouro (lição do usuário)

**NÃO recriar assets de marca manualmente.** A v2 (fundos desenhados à mão, logo recriada em HTML) foi rejeitada: "Ficou péssimo sem os fundos e a logo originais. Parece que errou o tom e as fontes também e removeu os ícones". A v3 (assets originais extraídos do PDF + HTML semântico) foi aprovada: "Parabéns, ficou perfeito". Sempre extrair e reutilizar fundos, logos, ícones e tons do PDF original.

## Pipeline (validado)

1. **Análise** — `pymupdf` (instalar via `uv pip install pymupdf`): tamanhos de página, `page.get_text("dict")` (linhas com bbox/font/tamanho), `page.get_drawings()` (formas/cores), `page.get_images()`.
2. **Detectar export Figma**: fontes Type3 + Form XObjects aninhados. Texto VISÍVEL = paths vetoriais dentro dos XObjects; a camada BT/ET no content stream é **acessibilidade invisível** (cor preta). Ver `references/figma-pdf-svg-structure.md`.
3. **Camada de arte**: `page.get_svg_image()` → SVG fiel (ordem, opacidade, máscaras preservadas). ~1MB/página com arte complexa.
4. **Camada de texto no SVG**:
   - `<use data-text="X" ...>` = glifos INVISÍVEIS com os caracteres reais (resolvem artefatos do texto extraído)
   - `<path d="..." fill="#ffffff">` = glifos VISÍVEIS (remover os que sobrepõem linhas de texto)
5. **Texto limpo**: reconstruir por linha a partir de `data-text` (ordenar por x, sem expandir verticalmente a caixa da linha — expansão mistura linhas adjacentes). Corrigir ligaduras com difflib contra a camada de acessibilidade (ver Pitfalls).
6. **Extrair assets** (logo, ícones, fundos) como componentes SVG por bbox — **sempre definir `fill` explícito** (default SVG = preto; logo extraído sem fill fica invisível sobre fundo preto).
7. **Montar HTML**: SVG limpo = `.bg` (camada de fundo); HTML semântico (h1/h2/h3/p/ul/li) = `.fg` posicionado com as coordenadas do PDF; **cores explícitas por elemento** (nunca inferir por overlap — deu errado na v1); bullets recriados via `li::before` (coluna fixa de x).
8. **Verificar no navegador** (browser tools): checagem programática (cores computadas, `getBoundingClientRect`, overflow) é a fonte de verdade; a vision model é imprecisa com zoom < 1 (zoom 1 para confirmação visual). O browser pode resetar para `about:blank` no meio da sessão — re-navegar para a URL `file://` antes de julgar que a página quebrou.

## Pitfalls

- **`apply_redactions()` não remove texto visível** em PDFs Figma: remove a camada BT/ET logicamente (`get_text` volta 0) mas o render fica IDÊNTICO — o texto visível são paths nos XObjects.
- **Span color reporta `#000000`** (camada de acessibilidade preta) enquanto o texto visível é branco. Não confie no color do span; amostre o render ou use os paths.
- **Ligaduras fi/fl**: o glifo único tem `data-text="f"` e o i/l some da reconstrução ("Artifcial", "ofcina"). Fix: `difflib.SequenceMatcher` entre texto limpo e acessibilidade; inserir deletes de 'i'/'l' únicos quando o char anterior é 'f'.
- **`€` no texto de acessibilidade = non-breaking space** (ex. "Duração:€Wor" → "Duração:\xa0Workshop"); "€Wor" = artefato de glifo duplicado na camada de acessibilidade.
- **Números de seção ("1.", "2.") são desenhados DENTRO do path do título** — aparecem ~32px à esquerda do bbox do texto extraído. Verifique crops; adicione manualmente ao texto.
- **Chips/cards atrás de texto** (ex. retângulo teal atrás de um preço) são removidos pela regra de remoção de texto (fill = cor de texto + overlap). Re-adicionar como elementos HTML no foreground.
- **Bullets são subpaths do path do texto** — remoção os remove; recriar com `li::before` (círculo branco ~10px, coluna de x fixa, ex. alinhada ao header da coluna).
- **Opacidade de camadas**: blobs decorativos frequentemente a 40% (`/E1 gs ca .4`). Confirmar amostrando pixels ao longo dos paths (não centros — arte esparsa).
- **`getBBox()` no SVG ignora transform** — aplicar CTM/transform manualmente (matrix y-flip `matrix(1,0,0,-1,X,Y)`).
- **Regra de remoção de texto**: path é texto se (interseção com linha/área do path > 0.15) OU (soma das interseções com todas as linhas / área > 0.35) — a segunda pega blocos multi-linha que são 1 path só.

## Templates de proposta comercial (marca ID — Gustavo/ID Consultoria)

Depois do deck, o usuário pediu um template HTML adaptável de proposta comercial com a marca ID, seguindo um guia de princípios (ver deep-research: propostas de consultoria). Iteração de validação: **"um slide de cada vez"**; quando ele pedir comparação, **listar diferenças sem editar**; validar cada slide antes de seguir.

### Estilo (seguir o deck aprovado, NÃO inventar)
- Hierarquia de fontes (style guide do usuário): **Neulis Neue Bold** = Title 96 · H1 60 · H2 48 · H3 36; **Nunito Sans Regular** = Body1 36 · Body2 30 · Body3 24 · Note 20. Capa/transições 96; títulos de seção 48; subtítulos 24; leads 30; listas 24.
- Paleta: fundo preto, texto branco, teal `#4AC6D3` (headers de seção/chips), teal escuro `#1AAEBD` (chip do preço, validade).
- **Bullets BRANCOS** (não teal); **leads BRANCOS** (não esmaecidos/muted); teal só em headers de seção e chips de preço.
- Capa: logo do cliente (`{{CLIENTE_LOGO_URL}}`, box tracejado "LOGO DO CLIENTE") + divisor + logo ID no topo; título (96) e subtítulo (36) abaixo; meta em grid por fim — tudo num **bloco centralizado na porção direita, NUNCA sobrepondo o diamante/escudo do fundo** (medir a extensão real do escudo no SVG de fundo antes de posicionar).
- Transições: título gigante alinhado à **ESQUERDA** (como o deck original), fundo teal claro (contornos `#679DA3`).
- Slides padrão: logo da marca no canto superior esquerdo, título (48) + subtítulo (24), conteúdo em fluxo.
- Slide final: logo + "Proposta válida até {{VALIDADE}}" (teal `#1AAEBD`) + disclaimer.

### Estrutura aprovada (do Guia de Princípios)
Capa → Resumo Executivo (com preço) → Entendimento do Desafio (com "custo de não agir") → Escopo & Entregáveis (com "fora do escopo") → Prova social → Metodologia & Cronograma → **ROI antes do preço** → transição teal → Investimento (3 opções Good-Better-Best, médio "Recomendado") → Garantia → Condições Comerciais → Responsabilidades → Sobre a empresa → Próximos Passos + assinatura → Final.

## Referências

- `references/figma-pdf-svg-structure.md` — anatomia de PDFs exportados de Figma (XObjects, Type3, camadas, opacidade, cores)
- `references/logo-and-asset-extraction.md` — extração de logo/ícones por bbox + remoção de assets específicos do SVG
