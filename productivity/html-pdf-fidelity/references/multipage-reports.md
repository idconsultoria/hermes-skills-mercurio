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
| Verificação | pymupdf: 1 página + fontes | Screenshot do HTML (não do PDF) via Chromium ARM64 compartilhado do proot + `vision_analyze` |

## Fluxo completo (local, sem host remoto)

Use o Chromium ARM64 compartilhado no próprio proot. Não copie para o Oracle, não use SSH e não use Chromium do Snap.

```bash
CHROMIUM=/opt/data/.playwright/chromium-1117/chrome-linux/chrome
INPUT=/caminho/absoluto/relatorio.html
OUTPUT=/caminho/absoluto/relatorio-v1.pdf

"$CHROMIUM" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --no-pdf-header-footer --print-to-pdf="$OUTPUT" "file://$INPUT"
```

Para gerar preview com o mesmo renderer:

```bash
"$CHROMIUM" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --hide-scrollbars --window-size=1240,1750 \
  --screenshot=/caminho/preview.png "file://$INPUT"
```

Validar com `pdfinfo`/`stat` e `vision_analyze`; limpar apenas os arquivos temporários criados pela tarefa. Para websites externos, usar `browser_exec`.

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
