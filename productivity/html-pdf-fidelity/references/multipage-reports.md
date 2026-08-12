# Relatórios Analíticos Multi-Página (HTML → PDF)

Fluxo validado em 12/08/2026 (relatório "Harness do Pi Agent", 30 KB de HTML,
PDF de 352 KB entregue como MEDIA). Complementa o corpo da skill, que foca em
cartas de 1 página — aqui o caso é relatório técnico com N páginas (hero, KPI
cards, tabelas, callouts, footer).

## Diferenças vs. carta de 1 página

| Aspecto | Carta (1 página) | Relatório multi-página |
|--------|------------------|------------------------|
| Paginação | 1 página exata, design para caber | Fluxo contínuo; Chromium quebra páginas |
| Margens | `@page { margin: 0 }` + padding no wrap | Igual — `@page { margin: 0 }` e padding lateral no `.wrap` |
| Fontes | EB Garamond/Playfair/Cinzel embutidas via `@font-face` file:// | Font stack de sistema (SF Mono/Consolas/monospace para code) — remover Google Fonts, NÃO remapear |
| Verificação | pymupdf: 1 página + fontes | Screenshot do HTML (não do PDF) via Chromium do host + `vision_analyze` |

## Fluxo completo (cat → host → chromium → cat back)

```bash
# 1. HTML → host (o snap do Chromium não lê /tmp; usar /home/ubuntu)
cat /opt/data/reports/pi-harness-report.html | ssh oracle-host 'cat > /home/ubuntu/pi-harness-report.html'

# 2. Converter — o `--no-pdf-header-footer` remove data/URL/nº de página
ssh oracle-host 'timeout 120 chromium-browser --headless --no-sandbox --disable-gpu \
  --disable-software-rasterizer --no-pdf-header-footer \
  --print-to-pdf=/home/ubuntu/pi-harness-report.pdf "file:///home/ubuntu/pi-harness-report.html" 2>&1 | tail -3; \
  ls -la /home/ubuntu/pi-harness-report.pdf'

# 3. Trazer de volta para /opt/data (write-safe root para MEDIA)
ssh oracle-host 'cat /home/ubuntu/pi-harness-report.pdf' > /opt/data/reports/pi-harness-report/pi-harness-report-v1.pdf

# 4. Limpar temporários do host
ssh oracle-host 'rm -f /home/ubuntu/pi-harness-report.html /home/ubuntu/pi-harness-report.pdf'
```

## Verificação sem pymupdf/pdftoppm no container

```bash
# Screenshot do HTML com o MESMO renderer do PDF (Chromium do host)
ssh oracle-host 'timeout 90 chromium-browser --headless --no-sandbox --disable-gpu \
  --screenshot=/home/ubuntu/preview.png --window-size=1240,1750 "file:///home/ubuntu/pi-harness-report.html" 2>&1 | tail -1'
ssh oracle-host 'cat /home/ubuntu/preview.png' > /opt/data/reports/pi-harness-report/preview-p1.png
# depois: vision_analyze no PNG local — conferir hero, alinhamento de KPI cards,
# headers de tabela azuis, ausência de texto cortado
```

- `--window-size=1240,1750` ≈ 1 página A4 em ~70 DPI.
- Para seções abaixo do fold, subir o height (ex.: `1240,3500`).
- Erros de DBus/UPower no stderr do snap são normais — ignorar.

## Pontos que o vision_analyze deve confirmar

Checklist usado na validação de 12/08/2026 (pergunte explicitamente ao modelo de
visão):
1. Hero com gradiente renderizou?
2. KPI cards alinhados em grid uniforme?
3. Headers de tabela azul royal com texto branco?
4. Algum texto cortado / layout quebrado / scroll horizontal?

## Pitfall de versionamento

Entregar SEMPRE com versão no nome (`-v1.pdf`) e limpar os temporários do host —
o host é infra compartilhada (IAF PDF usa o mesmo Chromium snap); não deixar
arquivos órfãos em /home/ubuntu.
