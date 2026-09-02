# BiotechSe — auditoria de PDF rasterizado e vetorização (2026-08-27)

Sessão: Gustavo pediu extração de assets do manual `doc_949ad65b4766_MArca_biotechse.pdf` usado para gerar o DS v1–v5.

## Diagnóstico

```python
import pymupdf
doc = pymupdf.open("doc_949ad65b4766_MArca_biotechse.pdf")
len(doc) # 8
for p in doc: print(p.get_fonts(), p.get_drawings(), len(p.get_text()), len(p.get_images()))
# 0 fonts, 0 drawings, 0 text, 1 JPEG 3125x2084 por página
# rect 1500x1000pt, 1 content stream com `Do` da imagem
```

**Conclusão:** 100% rasterizado — export de Figma/Canva como JPEG chapado. Não há vetores, fontes ou texto selecionável. `get_drawings()==0` é o teste decisivo.

## Assets extraíveis

- `embedded-p01-4.jpeg` … `embedded-p08-32.jpeg` (272–445KB) via `doc.extract_image(xref)` — JPEGs originais sem recompressão. Render em PNG 150dpi (3126×2084) em `/tmp/biotechse-assets/` para vision.
- Conteúdo por página (vision_analyze): P01 capa slogan, P02 manifesto, P03 conceito B+DNA+folha, P04 paleta oficial 5 cores, P05 sistema tipográfico, P06 lockup fachada 3D, P07 mockups, P08 divisória institucional. Ver `biotechse-brand.md` para paleta/tipografia.

## Tentativa de vetorização (vtracer 0.6.15)

- `vtracer` no crop flat P08 (`1469×917`) → `biotechse-trace-p08.svg` 495KB: traçou fundo desfocado/textura junto, inútil.
- `vtracer` binário no threshold branco → `biotechse-trace-bw.svg` 63KB: bordas denteadas por compressão JPEG.
- **Lição:** PDFs raster de foto (fachada 3D, mockup) não geram logo limpo via autotrace. Necessário redesenho manual.

## Reconstrução limpa

`biotechse-logo-reconstructed.svg` (2.7KB, 800×400) — SVG puro: B grotesk #029190 + fita DNA #00ffa3 + folha #00c77f, wordmark Clash Display 500 (`Biotech` teal / `se` mint), assinatura. Aproximação geométrica, requer validação do designer Tácio. Serve como prova de conceito para pacote `svg + png @1x/@2x`.

## Entrega da sessão

- DS v5 corrigido (v4 tinha `<title> v2` / tag `v2` / footer `v3` — checklist `grep -n "Design System|<title>|· v"` adicionado à skill).
- Relatório `biotechse-extracao-8p-v1.md` em deliverables + crops em `/tmp/biotechse-assets/`.

## Reuso

Para qualquer manual futuro: rode auditoria raster primeiro; se `get_drawings==0`, avise cliente e ofereça reconstrução vs. pedir `.ai/.eps` original.
