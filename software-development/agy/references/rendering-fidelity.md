# Fidelidade de Render — HTML do agy → PDF (estudo validado 11/08/2026)

Sintoma do usuário: "O HTML ficou ótimo no navegador, mas o PDF destoa." Diagnóstico
e solução completos, validados em sessão real (carta de apresentação com drop cap,
chips e ornamentos).

## Causa raiz nº 1 — FONTES

O design editorial do agy usa serifas que NÃO existem no host Ubuntu:
- Corpo: `Garamond / EB Garamond / Georgia / Baskerville / Hoefler Text / Times New Roman`
- Nome/drop cap: `Didot / Bodoni MT / Cinzel / Playfair Display / Garamond`
- Labels: `-apple-system / Segoe UI / Roboto / Helvetica / Arial` (sans — fallback ok)
- Chips/data: `Courier New / Courier / monospace` (mono — fallback ok)

O host tinha apenas 8 fontes DejaVu → o Chromium caía em serif genérica → visual
"diferente" do computador do usuário.

## O snap do Chromium tem fontconfig ISOLADO

Testes provaram:
- Instalar em `~/.local/share/fonts` + `fc-cache -f` → o snap NÃO enxerga.
- Instalar em `/usr/share/fonts/truetype/custom` + `fc-cache -f` → o snap NÃO enxerga.
- O snap lê `/home/ubuntu` (o HTML file:// funciona) → **`@font-face` com `src: file:///home/ubuntu/fonts/X.ttf` FUNCIONA**.

## Solução validada

1. Baixar as fontes do Google Fonts (repo `google/fonts`, arquivos variáveis TTF):
   - `ofl/ebgaramond/EBGaramond%5Bwght%5D.ttf` e `EBGaramond-Italic%5Bwght%5D.ttf`
   - `ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf` e `-Italic...`
   - `ofl/cinzel/Cinzel%5Bwght%5D.ttf`
   (variáveis `[wght]` cobrem todos os pesos; pegar regular + itálico)
2. Copiar para `/home/ubuntu/fonts/` no host.
3. Injetar no HTML (antes de `</style>`):
   ```css
   @font-face { font-family: "EB Garamond"; src: url("file:///home/ubuntu/fonts/EBGaramond.ttf"); font-weight: 100 900; font-style: normal; }
   @font-face { font-family: "EB Garamond"; src: url("file:///home/ubuntu/fonts/EBGaramond-Italic.ttf"); font-weight: 100 900; font-style: italic; }
   /* Playfair Display (+Italic) e Cinzel idem */
   ```
4. Renderizar: `chromium-browser --headless --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=out.pdf "file:///home/ubuntu/arquivo.html"`

## Verificação (não confiar no olho)

```python
import pymupdf
doc = pymupdf.open("out.pdf")
for page in doc:
    for f in page.get_fonts():
        print(f[3])  # embutidas via @font-face → 'Type3' ou nome vazio; DejaVu* = fallback
# por trecho:
for b in page.get_text("dict")["blocks"]:
    for line in b.get("lines", []):
        for span in line["spans"]:
            print(span["font"], span["text"][:40])
```
Resultado real: corpo/nome em Type3 (EB Garamond/Playfair embutidas); labels em
DejaVu Sans (equivalente sans do design — correto); data/chips em DejaVu Sans Mono
(equivalente Courier — correto). Único fallback residual: travessões decorativos
`───` (glifo ausente na EB Garamond) — irrelevante.

## Causa raiz nº 2 — fundos/chips sem cor no PDF

O Chromium NÃO imprime backgrounds por padrão. Se o HTML tem `@media print` que zera
fundo, OU usa `rgba()` em chips, o PDF sai branco/sem cor. Fix:
```css
@media print {
  body { background-color: #F5EFE6 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .metric-chip { background-color: rgba(...) !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
}
```

## Outros ajustes de fidelidade (validados)

- **Traços espessos**: `.header-divider { height: 1px !important; border-top-width: 1px !important; border-bottom-width: 1px !important; }` (borda dupla + height 3px = barra de 5px no PDF).
- **1 página**: `@page { size: A4; margin: 8mm 11mm; }` + compactação print (body 9pt, line-height 1.22, p margin 2pt, assinatura 12pt). O `.page` do agy tem `padding: 50px 60px` que duplica a margem no print — zerar.
- **Drop cap**: WeasyPrint 69 CRASHA com `::first-letter { float }` (AssertionError em float_layout) — para WeasyPrint usar `float: none` + font-size grande; para Chromium manter o float original.
- **Assinatura órfã na p2**: verificar se a classe real do footer foi coberta (o agy varia: `.letter-footer`, `.assinatura-secao`, `.signature-name`...). `margin-top: auto` no footer empurra — sobrescrever com `margin-top: 2pt !important`.

## WeasyPrint (fallback) — bugs conhecidos do agy HTML

- Grids com fração não-inteira (`1.85fr 1.15fr`) renderizam sobrepostos — trocar por `48% 48%` ou `62% 38%` + `justify-content: space-between`, ou empilhar (display:block).
- `sanitize_fonts` (mapear fontes → DejaVu) INFLAR o layout (DejaVu é mais largo que serifas) e quebra a paginação — para Chromium usar sanitização LEVE (só remover Google Fonts links), nunca mapear font-family.
- Containers `.page { min-height: 297mm }` + `page-break-after: always` geram 1 página por `.page` — injetar fix de fluxo natural.
- `.right-column { height: 100% }` de pai com altura automática colapsa o conteúdo — `height: auto !important`.
- Detectar carta pelo `<title>` contendo "carta/cover letter" — as classes variam a cada geração do agy (`.letter-card`, `.a4-page`, `.letter-body`, `.letter-sheet`...).
