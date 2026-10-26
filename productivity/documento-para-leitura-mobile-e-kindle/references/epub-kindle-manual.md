# EPUB 3 para Kindle sem dependências

`ebooklib` não é necessário: um EPUB é um ZIP com `mimetype` **sem compressão** na primeira posição.
Receita com `zipfile` + `xml.dom.minidom` (validação) + `PIL` (capa).

## Estrutura

```
mimetype                      (application/epub+zip, ZIP_STORED — 1º arquivo)
META-INF/container.xml
OEBPS/content.opf             (EPUB 3: dc:*, manifest, spine toc="ncx")
OEBPS/toc.ncx                 (NCX — Kindle antigo depende dele; mantenha junto do nav)
OEBPS/nav.xhtml               (properties="nav")
OEBPS/style.css
OEBPS/cover.xhtml + cover.jpg (item properties="cover-image"; <meta name="cover" content="cover-image"/>)
OEBPS/ch01..chNN.xhtml
```

- `content.opf`: `<item id="nav" ... properties="nav"/>`, `<item id="ncx" media-type="application/x-dtbncx+xml"/>`,
  `<spine toc="ncx">`, `<meta property="dcterms:modified">` em UTC `AAAA-MM-DDTHH:MM:SSZ`, `dc:language=pt-BR`.
- Um capítulo por unidade navegável (título/capítulo do documento), não um arquivo gigante.

## CSS seguro para Kindle

- Só `body/h1..h4/p/ul/li/span` com `font-family:serif`, `line-height`, `margin`, `border` e
  `page-break-after:avoid` nos títulos. **Sem flex, grid, `position:fixed`, `vh/vw`** — o conversor ignora e
  desmonta o layout.
- Numeração e rótulos como `<span class="num">` inline; nunca cartão circular.
- `page-break-after:avoid` no título evita cabeçalho órfão no fim da tela.

## Capa

`PIL` 1200×1600: fundo chapado, uma barra de acento, título grande, subtítulo e uma linha institucional no pé.
Fontes `DejaVuSerif/Sans` em `/data/data/com.termux/files/usr/share/fonts/TTF/` ou `/system/fonts/Roboto*`,
com fallback `ImageFont.load_default()`. **Não repita o nome da instituição** no topo e no pé, e não ponha
metadado de arquivo ("10 páginas no original") na capa: é capa, não ficha técnica.

## Validação mínima

```python
import zipfile, xml.dom.minidom as md
z = zipfile.ZipFile(path)
assert z.read('mimetype') == b'application/epub+zip'
for n in z.namelist():
    if n.endswith(('.xhtml', '.opf', '.ncx', '.xml')):
        md.parseString(z.read(n))     # XHTML malformado estoura aqui
```

HTML e EPUB saem do **mesmo modelo JSON**. Ao converter HTML de tela para EPUB, não reaproveite o markup:
`div`/`flex` não sobrevivem — rendereize os mesmos dados com `p` + `ul/li`.
