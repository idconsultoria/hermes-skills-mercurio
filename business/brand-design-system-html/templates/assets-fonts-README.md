# Fontes do design system <Marca> (self-hosted)

Este diretório deve conter os arquivos de fonte licenciados por <Marca>.
Após colocar os arquivos aqui, o design system passa a renderizar com as
fontes oficiais (<Display> + <Body>) em vez dos proxies.

## <Body Font> (<Foundry> — licenciada)

Coloque os `.woff2` (ou `.ttf`/`.otf`) aqui com estes nomes exatos — o
`@font-face` no HTML já aponta para eles:

- `<nome>-400.woff2`  → Regular (corpo)
- `<nome>-500.woff2`  → Medium (ênfase leve)
- `<nome>-800.woff2`  → ExtraBold (negrito de texto)

> Regra do sistema: **em texto, negrito = ExtraBold (800)**.

## <Display Font> (gratuita — <CDN/source>)

Carregada via <Fontshare/Google> (CDN público, licença gratuita), nos pesos
**400 e 500** (pesos oficiais de título). Nenhum arquivo necessário aqui.

---

**Nota de licença:** <Body Font> é uma fonte comercial. NÃO retire uma cópia
de sites de "download de fontes grátis" — use somente os arquivos cobertos
pela licença de <Marca>.